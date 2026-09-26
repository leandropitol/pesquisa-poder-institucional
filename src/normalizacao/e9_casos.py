"""Casos-teste da etapa E9: Mensalão (AP 470) e Mensalão mineiro (AP 536), status formal das pessoas.

Entradas (curadoria revisável):
- data/curadoria/e9_ap470_reus.csv: réus da AP 470 como aparecem na aba Partes do portal do STF e a ligação
  a um ator da base (nome igual, palavras do nome da base contidas no nome civil com correspondência única,
  ou decisão manual com motivo); sem ligação, ator novo;
- data/curadoria/e9_status.csv: status formal por pessoa, data e tipificação, só quando há fonte judicial
  ou oficial que nomeia a pessoa e diz o resultado (nunca voto de um ministro, nunca dedução);
- data/curadoria/e9_fontes.csv: as fontes (página do processo, acórdão, notícia oficial do STF), com o
  relatório de navegação do bruto que registrou a leitura.

O que não está nas fontes lidas fica de fora e vai para as limitações (condenações por quadrilha de Marcos
Valério e José Roberto Salgado sem data documentada; embargos sobre lavagem de 13/03/2014 sem o nome do
embargante; resultados de 2012 dos demais réus, cujo texto no portal vem cortado).

Uso:
    python -m src.normalizacao.e9_casos
"""

import csv
import unicodedata
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, acrescentar, gravar, ler

CUR = RAIZ / "data" / "curadoria"
CASOS = {
    "AP 470": ("Ação Penal 470 (caso conhecido como Mensalão)", "2007-11-12"),
    "AP 536": ("Ação Penal 536 (caso conhecido como Mensalão mineiro)", "2010-05-13"),
}


def norm(s: str) -> str:
    return " ".join(unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii").lower().replace("(", " ").replace(")", " ").split())


def ler_csv(nome: str) -> list[dict]:
    return list(csv.DictReader((CUR / nome).open(encoding="utf-8")))


def montar(ids: RegistroIds) -> dict:
    proc = ler("processos")
    id_proc = dict(zip(proc["numero_originario"], proc["id_processo"]))
    stf = ids.obter("instituicoes", "orgao:STF")
    fontes, judiciais, oficiais, f_de = [], [], [], {}
    for f in ler_csv("e9_fontes.csv"):
        i = ids.obter("fontes", f"e9:{f['chave']}")
        f_de[f["chave"]] = i
        fontes.append({"id_fonte": i, "tipo_fonte": f["tipo_fonte"], "titulo": f["titulo"], "data_publicacao": f["data_documento"], "url": f["url"],
                       "data_acesso": f["relatorio"].split("/")[3], "sha256": "", "caminho_raw": f["relatorio"],
                       "licenca": "Página pública do STF", "observacao": "Lida pelo Claude in Chrome no navegador do autor; relatório de navegação no bruto"})
        if f["tipo_fonte"] == "judicial":
            judiciais.append({"id_fonte": i, "numero_processo": f["numero_processo"], "id_orgao": stf, "data_documento": f["data_documento"],
                              "fase_processual": f["fase_processual"], "tipo_documento": f["tipo_documento"], "link_publico": f["url"]})
        else:
            oficiais.append({"id_fonte": i, "id_orgao": stf, "tipo_documento": "Notícia oficial do STF", "data_documento": f["data_documento"], "link": f["url"]})
    casos = []
    for numero, (nome, inicio) in CASOS.items():
        casos.append({"id_caso": ids.obter("casos", f"e9:{numero}"), "nome": nome, "tipo_caso": "acao_penal", "eixo": "esquemas_ilicitos",
                      "data_inicio": inicio, "criterio_inclusao": "Caso-teste da etapa E9 (docs/plano_coleta.md); processo no universo do STF (E5)",
                      "id_fonte": f_de["portal_ap470"]})
    reus = ler_csv("e9_ap470_reus.csv")
    novos, ator_de = [], {}
    for r in reus:
        if r["id_ator"]:
            ator_de[r["nome_partes"]] = r["id_ator"]
            continue
        a = ids.obter("atores", f"stf_parte:AP 470:{norm(r['nome_partes'])}")
        ator_de[r["nome_partes"]] = a
        novos.append({"id_ator": a, "nome": r["nome_partes"], "nome_normalizado": norm(r["nome_partes"]), "tipo_ator": "agente_privado",
                      "observacao": "Réu na AP 470 (aba Partes do portal do STF); tipo provisório: sem cargo público registrado na base"})
    status = []
    for s in ler_csv("e9_status.csv"):
        nomes = [r["nome_partes"] for r in reus] if s["nome_partes"] == "*" else [s["nome_partes"]]
        for n in nomes:
            status.append({"id_status": ids.obter("status_pessoa_processo", f"e9:{s['processo']}:{norm(n)}:{s['data']}:{s['status']}:{norm(s['tipificacao'])[:60]}"),
                           "id_ator": ator_de[n], "id_processo": id_proc[s["processo"]], "data": s["data"], "status": s["status"],
                           "tipificacao": s["tipificacao"], "id_fonte": f_de[s["fonte"]]})
    return {"fontes": fontes, "fonte_judicial": judiciais, "fonte_oficial": oficiais, "casos": casos, "atores": novos, "status_pessoa_processo": status,
            "caso_de_processo": {id_proc[n]: ids.obter("casos", f"e9:{n}") for n in CASOS}}


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    for nome in ("fontes", "fonte_judicial", "fonte_oficial"):
        atual = ler(nome, base)
        novas = [l for l in r[nome] if l["id_fonte"] not in set(atual["id_fonte"])]
        gravar(nome, pd.concat([atual, pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    for nome, chave in (("casos", "id_caso"), ("atores", "id_ator")):
        atual = ler(nome, base)
        novos = pd.DataFrame(r[nome], dtype=str)
        gravar(nome, pd.concat([atual[~atual[chave].isin(novos[chave])] if len(novos) else atual, novos], ignore_index=True), base)
    proc = ler("processos", base)
    proc["id_caso"] = proc["id_processo"].map(r["caso_de_processo"]).fillna(proc["id_caso"])
    gravar("processos", proc, base)
    existentes = set(ler("status_pessoa_processo", base)["id_status"])
    acrescentar("status_pessoa_processo", [x for x in r["status_pessoa_processo"] if x["id_status"] not in existentes], base)  # histórico só cresce
    ids.salvar()


def run() -> None:
    ids = RegistroIds()
    r = montar(ids)
    gravar_resultado(r, ids)
    s = pd.DataFrame(r["status_pessoa_processo"])
    print(f"casos: {len(r['casos'])}; atores novos: {len(r['atores'])}; status: {len(s)} {s['status'].value_counts().to_dict()}")


if __name__ == "__main__":
    run()
