"""Coletor das representações por quebra de decoro parlamentar (D-060), de 2003 em diante.

- Senado (dados abertos, serviço `processo`, substituto do antigo `materia`): por ano, as siglas usadas pelo Conselho de
  Ética: REP (representação), DEN (denúncia) e PCE (processo do Conselho de Ética, a partir de 2019), e o detalhe de
  cada processo.
- Câmara (API v2): proposições do tipo REP apresentadas desde 2003, o detalhe e as tramitações de cada uma. O tipo REP
  da Câmara inclui representações a outras comissões; o filtro do Conselho de Ética fica na normalização, com o
  bruto completo guardado.

Uso:
    python -m src.coleta.etica --data AAAA-MM-DD
"""

import argparse
import datetime as dt
import json
import re
from pathlib import Path

from src.base import RAIZ, RegistroIds
from src.coleta.comum import Cliente, Execucao, registrar_busca

SENADO = "https://legis.senado.leg.br/dadosabertos"
CAMARA = "https://dadosabertos.camara.leg.br/api/v2"
SCRIPT = "src.coleta.etica"
SIGLAS_SENADO = ["REP", "DEN", "PCE"]


def coletar(data: str | None = None) -> None:
    cliente, execucao, ids = Cliente(), Execucao("etica", data), RegistroIds()
    contagem = {}
    # Senado
    n_sen, ids_sen = 0, []
    for sigla in SIGLAS_SENADO:
        for ano in range(2003, dt.date.today().year + 1):
            r = cliente.get(f"{SENADO}/processo", params={"sigla": sigla, "ano": ano})
            corpo = execucao.gravar("senado_rep_por_ano.jsonl", f"{SENADO}/processo?sigla={{sigla}}&ano={{ano}}", r, {"sigla": sigla, "ano": ano})
            r.raise_for_status()
            lista = corpo if isinstance(corpo, list) else []
            n_sen += len(lista)
            ids_sen += [p["id"] for p in lista]
    for i in ids_sen:
        r = cliente.get(f"{SENADO}/processo/{i}")
        execucao.gravar("senado_rep_detalhe.jsonl", f"{SENADO}/processo/{{id}}", r, {"id": i})
    contagem["senado"] = n_sen
    # Câmara
    props, pagina = [], 1
    while True:
        r = cliente.get(f"{CAMARA}/proposicoes", params={"siglaTipo": "REP", "dataApresentacaoInicio": "2003-01-01", "ordem": "ASC",
                                                          "ordenarPor": "id", "itens": 100, "pagina": pagina})
        corpo = execucao.gravar("camara_rep_lista.jsonl", f"{CAMARA}/proposicoes?siglaTipo=REP&dataApresentacaoInicio=2003-01-01", r, {"pagina": pagina})
        r.raise_for_status()
        props += corpo["dados"]
        if not any(l["rel"] == "next" for l in corpo["links"]):
            break
        pagina += 1
    for p in props:
        for arquivo, url in (("camara_rep_detalhe.jsonl", f"{CAMARA}/proposicoes/{p['id']}"),
                             ("camara_rep_tramitacoes.jsonl", f"{CAMARA}/proposicoes/{p['id']}/tramitacoes")):
            r = cliente.get(url)
            execucao.gravar(arquivo, url.replace(str(p["id"]), "{id}"), r, {"id": p["id"]})
    contagem["camara"] = len(props)
    manifesto = {m["arquivo"].rsplit("/", 1)[1]: m for m in execucao.fechar()}
    registrar_busca("Senado, dados abertos", f"REP, DEN e PCE (Conselho de Ética) 2003 em diante (coleta {execucao.data})", n_sen, SCRIPT, execucao.data[:10], {"siglas": SIGLAS_SENADO},
                    manifesto["senado_rep_por_ano.jsonl"], ids)
    registrar_busca("Câmara dos Deputados, dados abertos", f"proposições tipo REP apresentadas desde 2003-01-01 (coleta {execucao.data})", len(props), SCRIPT,
                    execucao.data[:10], {"siglaTipo": "REP"}, manifesto["camara_rep_lista.jsonl"], ids)
    ids.salvar()
    print(contagem)


def referencias_prs(pasta: Path) -> list[tuple[str, str, str]]:
    """(identificação do processo de ética, número, ano) dos Projetos de Resolução do Senado (PRS) gerados por representações.

    Só entram os processos que o próprio Senado marca como transformados em PRS (deliberação TRANSF_PROJ_RES_SEN); o
    número vem do texto do parecer, e o PRS é o de ano igual ou posterior ao da representação."""
    saida = []
    for linha in (pasta / "senado_rep_detalhe.jsonl").open(encoding="utf-8"):
        d = json.loads(linha)["corpo"]
        if (d.get("deliberacao") or {}).get("siglaTipo") != "TRANSF_PROJ_RES_SEN":
            continue
        texto = " ".join((i.get("descricao") or i.get("texto") or "") for i in d["autuacoes"][0].get("informesLegislativos") or [])
        achados = {(n, a) for n, a in re.findall(r"Projeto de Resolu[çc][ãa]o(?: do Senado)?(?: n[º°o.]*)?\s*(\d+)[, ]+de\s+(\d{4})", texto, re.I)
                   if int(a) >= int(d["ano"])}
        saida += [(d["identificacao"], n, a) for n, a in sorted(achados)]
    return saida


def coletar_prs(pasta_origem: str, data: str | None = None) -> None:
    """Projetos de Resolução do Senado gerados por representações (resultado no plenário), da coleta em `pasta_origem`."""
    cliente, execucao, ids = Cliente(), Execucao("etica", data), RegistroIds()
    refs = referencias_prs(RAIZ / "data" / "raw" / "etica" / pasta_origem)
    for origem, numero, ano in refs:
        r = cliente.get(f"{SENADO}/processo", params={"sigla": "PRS", "numero": numero, "ano": ano})
        corpo = execucao.gravar("senado_prs_lista.jsonl", f"{SENADO}/processo?sigla=PRS&numero={{numero}}&ano={{ano}}", r,
                                {"origem": origem, "numero": numero, "ano": ano})
        r.raise_for_status()
        for p in corpo or []:
            r2 = cliente.get(f"{SENADO}/processo/{p['id']}")
            execucao.gravar("senado_prs_detalhe.jsonl", f"{SENADO}/processo/{{id}}", r2, {"origem": origem, "id": p["id"]})
    manifesto = {m["arquivo"].rsplit("/", 1)[1]: m for m in execucao.fechar()}
    registrar_busca("Senado, dados abertos", f"PRS gerados por representações do Conselho de Ética (coleta {execucao.data})", len(refs), SCRIPT,
                    execucao.data[:10], {"origem": pasta_origem}, manifesto["senado_prs_lista.jsonl"], ids)
    ids.salvar()
    print(refs)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data")
    ap.add_argument("--prs-de", help="pasta da coleta de representações de onde tirar os PRS")
    a = ap.parse_args()
    coletar_prs(a.prs_de, a.data) if a.prs_de else coletar(a.data)
