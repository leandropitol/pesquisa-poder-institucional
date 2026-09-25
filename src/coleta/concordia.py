"""Coletor do Concórdia, sistema de atos internacionais do Itamaraty (etapa E8, bloco B).

O site https://concordia.itamaraty.gov.br consulta a interface pública
https://aplicacao.itamaraty.gov.br/ApiConcordia/Acordo/ (a mesma que o navegador usa, sem chave):

- `--lista`: pesquisa simples sem filtro, em páginas de 500, com todos os atos (bilaterais, trilaterais e
  multilaterais), gravada em JSONL;
- `--detalhes`: o detalhe de cada ato bilateral celebrado de 2003 em diante (signatários, vigência,
  mensagem ao Congresso, decreto legislativo, promulgação), um pedido por ato, com pausa de 1 segundo.

Uso:
    python -m src.coleta.concordia --lista
    python -m src.coleta.concordia --detalhes
    python -m src.coleta.concordia --paises
"""

import argparse
import csv
import json

from src.base import RAIZ, RegistroIds
from src.coleta.comum import Cliente, Execucao, registrar_busca

API = "https://aplicacao.itamaraty.gov.br/ApiConcordia/Acordo/"
CABECALHOS = {"Referer": "https://concordia.itamaraty.gov.br/", "Origin": "https://concordia.itamaraty.gov.br"}
SCRIPT = "src.coleta.concordia"
FONTE = "Itamaraty, Concórdia (atos internacionais), interface pública do site"
TAMANHO = 500


def coletar_lista(data: str | None = None) -> None:
    cliente, ids, ex = Cliente(pausa=1.0, tempo_limite=120), RegistroIds(), Execucao("concordia", data)
    pagina, total_paginas, n = 1, 1, 0
    while pagina <= total_paginas:
        corpo = {"Pagina": pagina, "TextoAcordo": "", "TamanhoPagina": TAMANHO, "TipoAcordo": ""}
        r = cliente.post(API + "pesquisar-acordos-simples", corpo, headers=CABECALHOS)
        r.raise_for_status()
        d = ex.gravar("lista_atos.jsonl", API + "pesquisar-acordos-simples", r, corpo)
        total_paginas, n = d["TotalPages"], n + len(d["Items"])
        print(f"página {pagina}/{total_paginas}: {n} de {d['TotalCount']}")
        pagina += 1
    for reg in ex.fechar():
        registrar_busca(FONTE, "todos os atos (pesquisa simples sem filtro)", n, SCRIPT, ex.data, {"tamanho_pagina": TAMANHO}, reg, ids)
    ids.salvar()


def coletar_paises(data: str | None = None) -> None:
    """Lista de países do Concórdia (nome em português e sigla ISO de três letras)."""
    cliente, ids, ex = Cliente(pausa=1.0), RegistroIds(), Execucao("concordia", data)
    r = cliente.get(API + "listar-paises", headers=CABECALHOS)
    r.raise_for_status()
    d = ex.gravar("paises.jsonl", API + "listar-paises", r)
    for reg in ex.fechar():
        registrar_busca(FONTE, "lista de países (nome e sigla)", len(d), SCRIPT, ex.data, {}, reg, ids)
    ids.salvar()
    print(f"{len(d)} países")


def ultima_lista() -> tuple[dict, list[dict]]:
    man = [m for m in csv.DictReader((RAIZ / "data" / "manifestos" / "concordia.csv").open(encoding="utf-8")) if m["arquivo"].endswith("lista_atos.jsonl")]
    reg = max(man, key=lambda m: m["data_acesso"])
    itens = []
    with (RAIZ / reg["arquivo"]).open(encoding="utf-8") as f:
        for linha in f:
            itens += json.loads(linha)["corpo"]["Items"]
    return reg, itens


def coletar_detalhes(data: str | None = None, ano_inicial: int = 2003) -> None:
    cliente, ids, ex = Cliente(pausa=1.0, tempo_limite=120), RegistroIds(), Execucao("concordia", data)
    _, itens = ultima_lista()
    alvo = [i for i in itens if i["TipoAcordo"] == "BL" and i.get("DataCelebracao") and int(i["DataCelebracao"][-4:]) >= ano_inicial]
    falhas = 0
    for k, i in enumerate(alvo, 1):
        url = f"{API}detalhar-acordo/{i['Id']}"
        try:
            r = cliente.get(url, headers=CABECALHOS)
            ex.gravar("detalhes_bilaterais.jsonl", API + "detalhar-acordo/{id}", r, {"id": i["Id"]})
        except Exception as e:  # noqa: BLE001 — falha de um ato não interrompe; fica contada na busca
            falhas += 1
            print(f"FALHA {i['Id']}: {e}")
        if k % 200 == 0:
            print(f"{k}/{len(alvo)}")
    for reg in ex.fechar():
        registrar_busca(FONTE, f"detalhe dos atos bilaterais celebrados de {ano_inicial} em diante", len(alvo) - falhas, SCRIPT, ex.data,
                        {"atos": len(alvo), "falhas": falhas}, reg, ids)
    ids.salvar()
    print(f"{len(alvo) - falhas} detalhes; {falhas} falhas")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lista", action="store_true")
    ap.add_argument("--detalhes", action="store_true")
    ap.add_argument("--paises", action="store_true")
    a = ap.parse_args()
    if a.paises:
        coletar_paises()
    if a.lista:
        coletar_lista()
    if a.detalhes:
        coletar_detalhes()
