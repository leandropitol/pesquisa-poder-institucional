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

from src.base import RegistroIds
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
    registrar_busca("Senado, dados abertos", "REP, DEN e PCE (Conselho de Ética) 2003 em diante", n_sen, SCRIPT, execucao.data[:10], {"siglas": SIGLAS_SENADO},
                    manifesto["senado_rep_por_ano.jsonl"], ids)
    registrar_busca("Câmara dos Deputados, dados abertos", "proposições tipo REP apresentadas desde 2003-01-01", len(props), SCRIPT,
                    execucao.data[:10], {"siglaTipo": "REP"}, manifesto["camara_rep_lista.jsonl"], ids)
    ids.salvar()
    print(contagem)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data")
    coletar(ap.parse_args().data)
