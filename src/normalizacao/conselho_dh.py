"""Votos do Conselho de Direitos Humanos da ONU (etapa E8, bloco A2) para `votos_multilaterais`.

Fonte: resoluções baixadas do repositório de documentos da ONU (src/coleta/conselho_dh.py). Cada
resolução adotada por votação registrada traz no fim a lista de votos ("[Adopted by a recorded vote of
21 to 5, with 21 abstentions. The voting was as follows: In favour: ... Against: ... Abstaining: ...]").
Das sessões 1 a 11 (2006 a 2009), as resoluções vêm dos relatórios anuais do Conselho (A/62/53, A/63/53
e adendo, A/64/53).

Critério de seleção: o mesmo da Assembleia Geral (src/normalizacao/onu_ag.py, D-031): título sobre
situação de direitos humanos num país, ou título que cita país ou região da América Latina e do Caribe.
Os nomes dos países viram código ISO pela tabela nome-código do conjunto de votos da Assembleia Geral.
A contagem lida é conferida com o placar escrito na própria resolução; se não bate, a resolução fica fora
e é contada. Resoluções adotadas sem votação não geram voto por país (mesma regra da Assembleia Geral).

Uso:
    python -m src.normalizacao.conselho_dh
"""

import csv
import re
import unicodedata
from pathlib import Path

import fitz
import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, gravar, ler
from src.normalizacao.onu_ag import criterio

MANIFESTO = RAIZ / "data" / "manifestos" / "conselho_dh.csv"
MANIFESTO_AG = RAIZ / "data" / "manifestos" / "onu_ag.csv"
SAIDA = RAIZ / "data" / "staging" / "conselho_dh"
MESES = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
                                     "november", "december"], 1)}
# variações: "with no abstentions", nota de rodapé colada ("abstentions.*", "follows:3"), listas omitidas quando vazias
# e a redação dos relatórios de 2006 a 2009 ("[Resolution adopted by a recorded vote of 30 votes to 15, ...")
RE_VOTO = re.compile(r"\[\s*(?:Resolution )?adopted by (?:a )?recorded vote of (\d+|no|none)(?: votes)? to (\d+|no|none),?\s*with (\d+|no|none) "
                     r"abstentions?\.?\*?\s*The voting was as follows:\s*\d*\s*In favour:\s*(.*?)(?:\s*Against:\s*(.*?))?(?:\s*Abstaining:\s*(.*?))?\s*\]",
                     re.S | re.I)
RE_SEM_VOTO = re.compile(r"\[\s*(?:Resolution )?adopted without a vote\.?\s*\]", re.I)
RE_DATA = re.compile(r"adopted by the Human Rights Council on (\d{1,2}) (\w+) (\d{4})", re.I)
VOTOS = {"sim": 4, "nao": 5, "abstencao": 6}  # grupos da expressão RE_VOTO com as listas de países


def chave_nome(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").upper()
    s = s.replace("’", "'").replace("`", "'")
    return " ".join(re.sub(r"[^A-Z0-9()' -]", " ", s).split())


def nomes_iso() -> dict[str, str]:
    """Nome oficial da ONU (normalizado) -> ISO3, a partir do conjunto de votos da Assembleia Geral."""
    reg = max((m for m in csv.DictReader(MANIFESTO_AG.open(encoding="utf-8")) if m["arquivo"].endswith(".csv")), key=lambda m: m["data_acesso"])
    mapa = {}
    with (RAIZ / reg["arquivo"]).open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["ms_name"] and r["ms_code"]:
                mapa.setdefault(chave_nome(r["ms_name"]), r["ms_code"])
    # grafias do Conselho que não aparecem no conjunto da Assembleia Geral
    mapa.update({"CZECHIA": "CZE", "TURKIYE": "TUR", "TURKEY": "TUR", "NORTH MACEDONIA": "MKD", "ESWATINI": "SWZ",
                 "COTE D'IVOIRE": "CIV", "COTE D IVOIRE": "CIV", "COTE DIVOIRE": "CIV", "STATE OF PALESTINE": "PSE",
                 # nomes oficiais completos: o mais longo tem prioridade ("... AND NORTHERN IRELAND" não conta a Irlanda)
                 "UNITED KINGDOM OF GREAT BRITAIN AND NORTHERN IRELAND": "GBR", "UNITED STATES OF AMERICA": "USA",
                 "UNITES STATES OF AMERICA": "USA", "CAMERON": "CMR", "NETHERLANDS (KINGDOM OF THE)": "NLD"})
    return mapa


def paises(lista: str, mapa: dict[str, str], padrao: re.Pattern) -> tuple[list[str], str]:
    """ISO3 dos países da lista (nomes mais longos primeiro) e o que sobrou sem correspondência."""
    t = chave_nome(lista)
    t = re.sub(r"\bA HRC RES (?:S )?\d+ \d+ \d+\b", " ", t)  # cabeçalho de página no meio da lista ("A/HRC/RES/37/35 7")
    t = " ".join(t.split())
    achados = []

    def troca(m):
        achados.append(mapa[m.group(0)])
        return " "

    resto = padrao.sub(troca, t)
    resto = " ".join(re.sub(r"\bAND\b", " ", resto).split())
    return achados, resto


RE_REUNIAO = re.compile(r"\d+(?:st|nd|rd|th) meeting,?\s+(\d{1,2}) (\w+) (\d{4})", re.I)


def data_iso(texto: str) -> str:
    """Data de adoção: a linha "Resolution adopted by the Human Rights Council on <data>" ou, na falta dela, a
    data da reunião que fecha o texto ("40th meeting 27 March 2008"). Sem nenhuma das duas, vazio."""
    for m in (RE_DATA.search(texto), *list(RE_REUNIAO.finditer(texto))[-1:]):
        if m and m.group(2).lower() in MESES:
            return f"{m.group(3)}-{MESES[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    return ""


def resolucoes_do_arquivo(caminho: Path) -> list[dict]:
    """Resoluções de um PDF: uma (resolução avulsa) ou várias (relatório anual)."""
    texto = " ".join("".join(p.get_text() for p in fitz.open(caminho)).split())
    if caminho.name.startswith("A_HRC_RES_"):
        sessao, n = re.match(r"A_HRC_RES_(S-\d+|\d+)_(\d+)\.pdf", caminho.name).groups()
        m = re.search(rf"\b{re.escape(sessao)}/{n}\.?\s+(.+?)\s+The Human Rights Council\b", texto)  # com ou sem ponto após o número
        titulo = m.group(1) if m else ""
        return [{"simbolo": f"A/HRC/RES/{sessao}/{n}", "titulo": titulo, "texto": texto, "data": data_iso(texto)}]
    # relatório anual: cada resolução começa com "<sessão>/<n>. Título" seguido de "The Human Rights Council,"
    marcas = list(re.finditer(r"(?<![\w/.])((?:S-)?\d{1,2})/(\d{1,3})\.\s+(.{5,300}?)\s+The Human Rights Council,", texto))
    saida = []
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        trecho = texto[m.start():fim]
        saida.append({"simbolo": f"A/HRC/RES/{m.group(1)}/{m.group(2)}", "titulo": m.group(3), "texto": trecho, "data": data_iso(trecho)})
    return saida


def montar(ids: RegistroIds) -> dict:
    man = list(csv.DictReader(MANIFESTO.open(encoding="utf-8")))
    mapa = nomes_iso()
    padrao = re.compile(r"(?<![A-Z])(" + "|".join(re.escape(n) for n in sorted(mapa, key=len, reverse=True)) + r")(?![A-Z])")
    cdh = ids.obter("instituicoes", "organismo:ONU_CDH")
    inst = [{"id_instituicao": cdh, "nome": "Conselho de Direitos Humanos das Nações Unidas", "sigla": "CDH", "tipo_instituicao": "organismo_multilateral",
             "poder": "nao_se_aplica", "esfera": "internacional", "pais_iso3": ""}]
    fontes, oficiais, votos, resumo, vistas = [], [], [], [], set()
    for reg in man:
        caminho = RAIZ / reg["arquivo"]
        for r in resolucoes_do_arquivo(caminho):
            if r["simbolo"] in vistas:
                continue  # a mesma resolução no relatório e no adendo
            vistas.add(r["simbolo"])
            crit = criterio(r["titulo"], "")
            m = RE_VOTO.search(r["texto"])
            estado = "votacao" if m else ("sem_votacao" if RE_SEM_VOTO.search(r["texto"]) else "sem_registro_de_adocao")
            linha = {"simbolo": r["simbolo"], "titulo": r["titulo"][:200], "data": r["data"], "criterio": crit, "estado": estado, "confere": "", "sobra": ""}
            if m and crit and not r["data"]:
                linha["estado"] = "votacao_sem_data"  # nunca usar a data da coleta como data da resolução
            elif m and crit:
                listas = {v: paises(m.group(g) or "", mapa, padrao) for v, g in VOTOS.items()}
                placar = {v: int(m.group(k)) if m.group(k).isdigit() else 0 for v, k in (("sim", 1), ("nao", 2), ("abstencao", 3))}
                confere = all(len(listas[v][0]) == placar[v] for v in placar)
                linha["confere"], linha["sobra"] = confere, " | ".join(x[1] for x in listas.values() if x[1])
                if confere:
                    f = ids.obter("fontes", f"raw:{reg['arquivo']}")
                    if f not in {x["id_fonte"] for x in fontes}:
                        fontes.append({"id_fonte": f, "tipo_fonte": "oficial", "titulo": f"Nações Unidas, {caminho.stem.replace('_', '/')}",
                                       "data_publicacao": r["data"], "url": reg["url_base"], "data_acesso": reg["data_acesso"],
                                       "sha256": reg["sha256"], "caminho_raw": reg["arquivo"], "licenca": "Documento oficial das Nações Unidas",
                                       "observacao": "Repositório oficial de documentos da ONU (documents.un.org)"})
                        oficiais.append({"id_fonte": f, "id_orgao": cdh, "tipo_documento": "Resolução ou relatório do Conselho de Direitos Humanos",
                                         "data_documento": r["data"], "link": reg["url_base"]})
                    trecho = m.group(0)[:600]
                    for voto, (lista, _) in listas.items():
                        for iso in lista:
                            votos.append({"id_voto": ids.obter("votos_multilaterais", f"cdh:{r['simbolo']}:{iso}"), "id_organismo": cdh,
                                          "resolucao": r["simbolo"], "titulo": r["titulo"][:300], "tema": "", "criterio_inclusao": crit,
                                          "data": r["data"], "pais_iso3": iso, "voto": voto, "link": reg["url_base"],
                                          "modalidade": "votacao_registrada", "trecho": "" if iso != "BRA" else trecho, "id_fonte": f})
            resumo.append(linha)
    return {"instituicoes": inst, "fontes": fontes, "fonte_oficial": oficiais, "votos_multilaterais": votos, "resumo": resumo}


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    for nome in ("fontes", "fonte_oficial"):
        atual = ler(nome, base)
        novas = [l for l in r[nome] if l["id_fonte"] not in set(atual["id_fonte"])]
        gravar(nome, pd.concat([atual, pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    atual = ler("instituicoes", base)
    novas = pd.DataFrame(r["instituicoes"], dtype=str)
    gravar("instituicoes", pd.concat([atual[~atual["id_instituicao"].isin(novas["id_instituicao"])], novas], ignore_index=True), base)
    atual = ler("votos_multilaterais", base)
    org = novas["id_instituicao"].iloc[0]
    gravar("votos_multilaterais", pd.concat([atual[atual["id_organismo"] != org], pd.DataFrame(r["votos_multilaterais"], dtype=str)], ignore_index=True), base)
    ids.salvar()
    SAIDA.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(r["resumo"]).to_csv(SAIDA / "resolucoes.csv", index=False, encoding="utf-8")


def run() -> None:
    ids = RegistroIds()
    r = montar(ids)
    gravar_resultado(r, ids)
    res = pd.DataFrame(r["resumo"])
    print(f"resoluções lidas: {len(res)}; por estado: {res['estado'].value_counts().to_dict()}")
    sel = res[res["criterio"] != ""]
    print(f"selecionadas: {len(sel)} {sel['criterio'].value_counts().to_dict()}; votadas: {int((sel['estado'] == 'votacao').sum())}; "
          f"placar confere: {int((sel['confere'] == True).sum())}; votos gravados: {len(r['votos_multilaterais'])}")
    print(sel[(sel["estado"] == "votacao") & (sel["confere"] != True)][["simbolo", "sobra"]].head(15).to_string())


if __name__ == "__main__":
    run()
