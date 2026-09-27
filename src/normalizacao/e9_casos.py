"""Casos-teste da etapa E9: Mensalão (AP 470) e Mensalão mineiro (AP 536), status formal das pessoas.

Entradas (curadoria revisável):
- data/curadoria/e9_ap470_reus.csv: réus da AP 470 como aparecem na aba Partes do portal do STF e a ligação
  a um ator da base (nome igual, palavras do nome da base contidas no nome civil com correspondência única,
  ou decisão manual com motivo); sem ligação, ator novo;
- data/curadoria/e9_status.csv: status formal por pessoa, data e tipificação, só quando há fonte judicial
  ou oficial que nomeia a pessoa e diz o resultado (nunca voto de um ministro, nunca dedução);
- data/curadoria/e9_fontes.csv: as fontes (página do processo, acórdão, notícia oficial), com o órgão (STF ou
  TJMG) e o relatório de navegação do bruto que registrou a leitura;
- data/curadoria/e9_processos.csv: processos fora do universo do STF (a parte da AP 536 enviada ao TJMG em 2014);
- data/curadoria/e9_fases.csv: fases desses processos, cada uma com fonte;
- data/curadoria/e9_pessoas.csv: pessoas que não estão na aba Partes da AP 470, com a ligação a um ator da base.

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
ORGAOS = {"STF": ("Supremo Tribunal Federal", "federal"), "TJMG": ("Tribunal de Justiça do Estado de Minas Gerais", "estadual")}
PORTAL = {"STF": "Página pública do STF", "TJMG": "Página pública do TJMG"}
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
    orgao = {o: ids.obter("instituicoes", f"orgao:{o}") for o in ORGAOS}
    inst = [{"id_instituicao": orgao[o], "nome": n, "sigla": o, "tipo_instituicao": "tribunal", "poder": "judiciario", "esfera": e, "pais_iso3": "BRA"}
            for o, (n, e) in ORGAOS.items() if o != "STF"]  # o STF vem da E5
    fontes, judiciais, oficiais, f_de = [], [], [], {}
    for f in ler_csv("e9_fontes.csv"):
        i = ids.obter("fontes", f"e9:{f['chave']}")
        f_de[f["chave"]] = i
        quem = "Claude Code no navegador embutido" if "verificacao" in f["relatorio"] else "Claude in Chrome no navegador do autor"
        fontes.append({"id_fonte": i, "tipo_fonte": f["tipo_fonte"], "titulo": f["titulo"], "data_publicacao": f["data_documento"], "url": f["url"],
                       "data_acesso": f["relatorio"].split("/")[3], "sha256": "", "caminho_raw": f["relatorio"],
                       "licenca": PORTAL[f["orgao"]], "observacao": f"Lida pelo {quem}; relatório de navegação no bruto"})
        if f["tipo_fonte"] == "judicial":
            judiciais.append({"id_fonte": i, "numero_processo": f["numero_processo"], "id_orgao": orgao[f["orgao"]], "data_documento": f["data_documento"],
                              "fase_processual": f["fase_processual"], "tipo_documento": f["tipo_documento"], "link_publico": f["url"]})
        else:
            oficiais.append({"id_fonte": i, "id_orgao": orgao[f["orgao"]], "tipo_documento": f"Notícia oficial do {f['orgao']}",
                             "data_documento": f["data_documento"], "link": f["url"]})
    processos, caso_de_processo = [], {}
    for p in ler_csv("e9_processos.csv"):
        i = ids.obter("processos", f"e9:{p['tribunal']}:{p['numero_cnj']}")
        id_proc[p["processo"]] = i
        caso_de_processo[i] = ids.obter("casos", f"e9:{p['caso']}")
        processos.append({"id_processo": i, "numero_cnj": p["numero_cnj"], "numero_originario": p["processo"], "classe": p["classe"],
                          "id_tribunal": orgao[p["tribunal"]], "data_autuacao": p["data_autuacao"], "id_caso": caso_de_processo[i],
                          "sigilo": p["sigilo"], "url": p["url"], "id_fonte": f_de[p["fonte"]]})
    fases = [{"id_fase": ids.obter("fases_processo", f"e9:{x['processo']}:{x['data']}:{x['fase']}"), "id_processo": id_proc[x["processo"]],
              "data": x["data"], "fase": x["fase"], "id_orgao_julgador": orgao[x["orgao"]], "resumo": x["resumo"], "id_fonte": f_de[x["fonte"]]}
             for x in ler_csv("e9_fases.csv")]
    casos = []
    for numero, (nome, inicio) in CASOS.items():
        casos.append({"id_caso": ids.obter("casos", f"e9:{numero}"), "nome": nome, "tipo_caso": "acao_penal", "eixo": "esquemas_ilicitos",
                      "data_inicio": inicio, "criterio_inclusao": "Caso-teste da etapa E9 (docs/plano_coleta.md); processo no universo do STF (E5)",
                      "id_fonte": f_de["portal_ap470"]})
    reus = ler_csv("e9_ap470_reus.csv")
    novos, ator_de = [], {r["nome_partes"]: r["id_ator"] for r in ler_csv("e9_pessoas.csv")}
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
    return {"instituicoes": inst, "fontes": fontes, "fonte_judicial": judiciais, "fonte_oficial": oficiais, "casos": casos, "atores": novos,
            "processos": processos, "fases_processo": fases, "status_pessoa_processo": status,
            "caso_de_processo": {**{id_proc[n]: ids.obter("casos", f"e9:{n}") for n in CASOS}, **caso_de_processo}}


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    atual = ler("instituicoes", base)
    novas = [l for l in r["instituicoes"] if l["id_instituicao"] not in set(atual["id_instituicao"])]
    gravar("instituicoes", pd.concat([atual, pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    for nome in ("fontes", "fonte_judicial", "fonte_oficial"):
        atual = ler(nome, base)
        novas = [l for l in r[nome] if l["id_fonte"] not in set(atual["id_fonte"])]
        gravar(nome, pd.concat([atual, pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    for nome, chave in (("casos", "id_caso"), ("atores", "id_ator"), ("processos", "id_processo")):
        atual = ler(nome, base)
        novos = pd.DataFrame(r[nome], dtype=str)
        gravar(nome, pd.concat([atual[~atual[chave].isin(novos[chave])] if len(novos) else atual, novos], ignore_index=True), base)
    proc = ler("processos", base)
    proc["id_caso"] = proc["id_processo"].map(r["caso_de_processo"]).fillna(proc["id_caso"])
    gravar("processos", proc, base)
    for nome, chave in (("fases_processo", "id_fase"), ("status_pessoa_processo", "id_status")):
        existentes = set(ler(nome, base)[chave])
        acrescentar(nome, [x for x in r[nome] if x[chave] not in existentes], base)  # histórico só cresce
    ids.salvar()


def run() -> None:
    ids = RegistroIds()
    r = montar(ids)
    gravar_resultado(r, ids)
    s = pd.DataFrame(r["status_pessoa_processo"])
    print(f"casos: {len(r['casos'])}; atores novos: {len(r['atores'])}; processos fora do STF: {len(r['processos'])}; "
          f"fases: {len(r['fases_processo'])}; status: {len(s)} {s['status'].value_counts().to_dict()}")


if __name__ == "__main__":
    run()
