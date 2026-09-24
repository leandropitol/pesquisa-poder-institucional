"""Coletor do BNDES, operações de apoio à exportação (etapa E3).

Usa a API do catálogo de dados abertos do BNDES (CKAN) para listar os recursos do conjunto
`operacoes-exportacao` (pós-embarque de serviços de engenharia, pós-embarque de bens,
pré-embarque) e baixa cada arquivo sem alteração, com os dicionários de dados em PDF.

Uso:
    python -m src.coleta.bndes --planejar
    python -m src.coleta.bndes
"""

import argparse
import re

from src.base import RegistroIds
from src.coleta.comum import Cliente, Execucao, registrar_busca

CKAN = "https://dadosabertos.bndes.gov.br/api/3/action/package_show"
CONJUNTO = "operacoes-exportacao"
SCRIPT = "src.coleta.bndes"


def recursos(cliente: Cliente) -> tuple[dict, list[dict]]:
    r = cliente.get(CKAN, params={"id": CONJUNTO})
    r.raise_for_status()
    pacote = r.json()["result"]
    return pacote, pacote["resources"]


def nome_arquivo(url: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", url.rsplit("/", 1)[1])


def planejar() -> list[tuple[str, str, int | None]]:
    cliente = Cliente()
    _, recs = recursos(cliente)
    return [(r["name"], r["format"], r.get("size")) for r in recs]


def coletar(data: str | None = None) -> None:
    cliente, ids, execucao = Cliente(), RegistroIds(), Execucao("bndes", data)
    r = cliente.get(CKAN, params={"id": CONJUNTO})
    execucao.gravar("catalogo_operacoes_exportacao.jsonl", CKAN, r, {"id": CONJUNTO})
    pacote = r.json()["result"]
    print(f"conjunto atualizado em {pacote.get('metadata_modified')}")
    for rec in pacote["resources"]:
        destino = execucao.baixar(cliente, rec["url"], nome_arquivo(rec["url"]))
        print(f"{rec['name']}: {destino.stat().st_size / 1e6:.2f} MB")
    for reg in execucao.fechar():
        arquivo = reg["arquivo"].rsplit("/", 1)[1]
        n = 1
        if arquivo.endswith(".csv"):
            with open(reg["arquivo"], "rb") as f:
                n = max(sum(1 for _ in f) - 1, 0)
        registrar_busca("BNDES, dados abertos (CKAN)", f"conjunto {CONJUNTO}: {arquivo}", n, SCRIPT, execucao.data,
                        {"url": reg["url_base"]}, reg, ids)
    ids.salvar()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--planejar", action="store_true")
    a = ap.parse_args()
    print(planejar()) if a.planejar else coletar()
