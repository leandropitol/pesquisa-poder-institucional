"""Normalização dos processos do STJ vindos do DataJud (etapa E4) para `processos` e `fases_processo`.

Uso restrito (D-022): a base guarda os metadados para descobrir o universo; a fonte ligada tem a
licença do termo de uso do DataJud, e os relatórios não a citam.

- `processos`: todas as ações penais e inquéritos do STJ na API pública (nível de sigilo público),
  com os assuntos da TPU. A pertença ao universo do eixo 1 é calculada por `no_universo`, a partir de
  data/curadoria/assuntos_tpu_eixo1.csv (tipos penais do protocolo), não gravada.
- Data de autuação: `dataAjuizamento`; quando o ano é impossível (erro de formatação na fonte), usa-se
  o movimento mais antigo, e o caso é contado nas limitações.
- `fases_processo`: só movimentos da TPU com correspondência inequívoca no vocabulário (declínio por
  incompetência; determinação de arquivamento de procedimento investigatório). O trânsito em julgado
  fica de fora porque aparece a cada recurso interno encerrado. Os demais movimentos ficam no bruto.

Uso:
    python -m src.normalizacao.datajud_stj
"""

import csv
import datetime as dt
import html
import json
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, acrescentar, gravar, ler

MANIFESTO = RAIZ / "data" / "manifestos" / "datajud_stj.csv"
CURADORIA = RAIZ / "data" / "curadoria"
ARQUIVO = "processos_originarios_penais.jsonl"
URL_STJ = "https://processo.stj.jus.br/processo/pesquisa/?tipoPesquisa=tipoPesquisaNumeroUnico&termo={numero}"
LICENCA = "Termo de uso da API pública do DataJud (CNJ), v1.2: uso restrito, sem redistribuição (D-022)"
CLASSES = {"Ação Penal": "acao_penal", "Inquérito": "inquerito"}
# 848 (trânsito em julgado) fica de fora: no STJ ele aparece a cada recurso interno encerrado, não só no fim do processo.
MOVIMENTOS_FASE = {941: "declinio_competencia", 1063: "arquivamento_inquerito"}
ANO_MIN = 1989  # instalação do STJ


def data_valida(valor: str | None, hoje: str) -> str:
    """'20260227000000' ou '2017-12-22T00:00:00.000Z' -> 'AAAA-MM-DD'; '' se ausente ou impossível."""
    v = (valor or "").strip()
    if not v:
        return ""
    d = v[:10] if "-" in v[:10] else f"{v[:4]}-{v[4:6]}-{v[6:8]}"
    try:
        dt.date.fromisoformat(d)
    except ValueError:
        return ""
    return d if f"{ANO_MIN}-01-01" <= d <= hoje else ""


def assuntos(doc: dict) -> list[tuple[str, str]]:
    return [(str(a.get("codigo", "")), html.unescape(a.get("nome") or "").strip()) for a in (doc.get("assuntos") or [])]


def regras_assuntos(caminho: Path = CURADORIA / "assuntos_tpu_eixo1.csv") -> dict[str, str]:
    return {l["codigo_tpu"]: l["decisao"] for l in csv.DictReader(caminho.open(encoding="utf-8"))}


def no_universo(codigos: list[str], regras: dict[str, str]) -> str:
    """'sim' (ao menos um tipo do protocolo), 'revisar' (só assuntos genéricos ou sem regra), 'nao'."""
    decisoes = [regras.get(c, "sem_regra") for c in codigos]
    if "inclui" in decisoes:
        return "sim"
    if any(d in ("indeterminado", "sem_regra") for d in decisoes):
        return "revisar"
    return "nao"


def ler_documentos() -> tuple[dict, list[dict]]:
    man = [m for m in csv.DictReader(MANIFESTO.open(encoding="utf-8")) if m["arquivo"].endswith("/" + ARQUIVO)]
    reg = max(man, key=lambda m: m["data_acesso"])
    docs = []
    with (RAIZ / reg["arquivo"]).open(encoding="utf-8") as f:
        for linha in f:
            docs += [h["_source"] for h in json.loads(linha)["corpo"]["hits"]["hits"]]
    return reg, docs


def montar(ids: RegistroIds, hoje: str | None = None) -> dict:
    hoje = hoje or dt.date.today().isoformat()
    reg, docs = ler_documentos()
    stj = ids.obter("instituicoes", "orgao:STJ")
    cnj = ids.obter("instituicoes", "orgao:CNJ")
    instituicoes = [
        {"id_instituicao": stj, "nome": "Superior Tribunal de Justiça", "sigla": "STJ", "tipo_instituicao": "tribunal", "poder": "judiciario", "esfera": "federal", "pais_iso3": "BRA"},
        {"id_instituicao": cnj, "nome": "Conselho Nacional de Justiça", "sigla": "CNJ", "tipo_instituicao": "orgao_publico", "poder": "judiciario", "esfera": "federal", "pais_iso3": "BRA"},
    ]
    f = ids.obter("fontes", f"raw:{reg['arquivo']}")
    fontes = [{"id_fonte": f, "tipo_fonte": "oficial", "titulo": "DataJud (CNJ), API pública: ações penais e inquéritos do STJ, metadados e movimentos",
               "data_publicacao": reg["data_acesso"], "url": reg["url_base"], "data_acesso": reg["data_acesso"], "sha256": reg["sha256"],
               "caminho_raw": reg["arquivo"], "licenca": LICENCA, "observacao": "Uso restrito: descoberta do universo; não citar em relatório"}]
    oficiais = [{"id_fonte": f, "id_orgao": cnj, "tipo_documento": "Resposta da API pública do DataJud (JSONL)", "data_documento": reg["data_acesso"], "link": reg["url_base"]}]
    processos, fases, data_por_movimento = [], [], 0
    for d in docs:
        numero = d["numeroProcesso"]
        p = ids.obter("processos", f"cnj:{numero}")
        movs = sorted((m for m in (d.get("movimentos") or []) if data_valida(m.get("dataHora"), hoje)), key=lambda m: m["dataHora"])
        autuacao = data_valida(d.get("dataAjuizamento"), hoje)
        if not autuacao and movs:
            autuacao, data_por_movimento = data_valida(movs[0]["dataHora"], hoje), data_por_movimento + 1
        processos.append({"id_processo": p, "numero_cnj": numero, "classe": CLASSES[d["classe"]["nome"]], "id_tribunal": stj,
                          "data_autuacao": autuacao, "assuntos_tpu": "; ".join(f"{c}:{n}" for c, n in assuntos(d)),
                          "sigilo": "false", "url": URL_STJ.format(numero=numero), "id_fonte": f})
        for m in movs:
            fase = MOVIMENTOS_FASE.get(m.get("codigo"))
            if fase:
                data = data_valida(m["dataHora"], hoje)
                fases.append({"id_fase": ids.obter("fases_processo", f"cnj:{numero}:{m['codigo']}:{m['dataHora']}"), "id_processo": p,
                              "data": data, "fase": fase, "id_orgao_julgador": stj, "resumo": m.get("nome", ""), "id_fonte": f})
    return {"instituicoes": instituicoes, "fontes": fontes, "fonte_oficial": oficiais, "processos": processos, "fases_processo": fases,
            "data_por_movimento": data_por_movimento, "sem_data": sum(1 for p in processos if not p["data_autuacao"])}


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    for nome in ("fontes", "fonte_oficial"):
        atual = ler(nome, base)
        novas = [l for l in r[nome] if l["id_fonte"] not in set(atual["id_fonte"])]
        gravar(nome, pd.concat([atual, pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    atual = ler("instituicoes", base)
    novas = pd.DataFrame(r["instituicoes"], dtype=str)
    gravar("instituicoes", pd.concat([atual[~atual["id_instituicao"].isin(novas["id_instituicao"])], novas], ignore_index=True), base)
    atual = ler("processos", base)
    novos = pd.DataFrame(r["processos"], dtype=str)
    gravar("processos", pd.concat([atual[~atual["id_processo"].isin(novos["id_processo"])], novos], ignore_index=True), base)
    existentes = set(ler("fases_processo", base)["id_fase"])
    acrescentar("fases_processo", [x for x in r["fases_processo"] if x["id_fase"] not in existentes], base)  # histórico só cresce
    ids.salvar()


def run() -> None:
    ids = RegistroIds()
    r = montar(ids)
    gravar_resultado(r, ids)
    regras = regras_assuntos()
    p = pd.DataFrame(r["processos"])
    p["universo"] = [no_universo([a.split(":")[0] for a in s.split("; ") if a], regras) for s in p["assuntos_tpu"]]
    p["ano"] = p["data_autuacao"].str[:4]
    p.loc[p["ano"] < "2003", "universo"] = p.loc[p["ano"] < "2003", "universo"].replace({"sim": "antes_de_2003"})
    print(p.groupby(["classe", "universo"]).size().to_string())
    print(f"autuação pelo primeiro movimento: {r['data_por_movimento']}; sem data: {r['sem_data']}; fases registradas: {len(r['fases_processo'])}")
    print("no universo, por ano:", p[p["universo"] == "sim"].groupby("ano").size().to_dict())


if __name__ == "__main__":
    run()
