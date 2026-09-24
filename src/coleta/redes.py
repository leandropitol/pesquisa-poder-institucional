"""Coletor das listas de membros de redes partidárias e fóruns transnacionais (etapa E8, bloco D).

As páginas estão em data/curadoria/redes_fontes.csv (uma linha por endereço; busca `exata` ou por
`prefixo`). Para cada endereço, o índice do Internet Archive (CDX) dá as cópias guardadas; o coletor
baixa uma por ano, a mais próxima de 1º de julho, desde 2003, no formato original (`id_`), e grava
em data/raw/redes/<data>/<rede>/. Páginas com cópia no arquivo servem de fonte datada; o site atual
de cada rede entra pela cópia mais recente do arquivo, que é estável e citável.

Uso:
    python -m src.coleta.redes --planejar
    python -m src.coleta.redes
"""

import argparse
import csv
import re

from src.base import RAIZ, RegistroIds
from src.coleta.comum import Cliente, Execucao, registrar_busca

FONTES = RAIZ / "data" / "curadoria" / "redes_fontes.csv"
CDX = "https://web.archive.org/cdx/search/cdx"
SCRIPT = "src.coleta.redes"
ANO_INICIAL = 2003


def fontes() -> list[dict]:
    return list(csv.DictReader(FONTES.open(encoding="utf-8")))


def copias(cliente: Cliente, url: str, busca: str) -> list[tuple[str, str]]:
    """(timestamp, endereço original) das cópias com status 200 no arquivo."""
    r = cliente.get(CDX, params={"url": url, "matchType": "prefix" if busca == "prefixo" else "exact", "output": "json",
                                 "fl": "timestamp,original", "filter": ["statuscode:200"], "limit": "5000"})
    linhas = r.json()[1:] if r.text.strip() else []
    return [(t, o) for t, o in linhas]


def uma_por_ano(lista: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Para cada (ano, endereço original), a cópia mais próxima de 1º de julho."""
    melhor: dict[tuple[str, str], tuple[str, str]] = {}
    for t, o in lista:
        if int(t[:4]) < ANO_INICIAL:
            continue
        chave = (t[:4], re.sub(r":80(?=/)", "", o.split("?")[0].lower().rstrip("/")))
        alvo = f"{t[:4]}0701000000"
        if chave not in melhor or abs(int(t) - int(alvo)) < abs(int(melhor[chave][0]) - int(alvo)):
            melhor[chave] = (t, o)
    return sorted(melhor.values())


def nome_local(t: str, original: str) -> str:
    return f"{t}_{re.sub(r'[^A-Za-z0-9._-]+', '_', original.split('://', 1)[-1])[:120]}.html"


def planejar() -> None:
    cliente = Cliente(pausa=1.5)
    for f in fontes():
        sel = uma_por_ano(copias(cliente, f["url"], f["busca"]))
        print(f"{f['id_rede']:8s} {len(sel):3d} cópias {sorted({t[:4] for t, _ in sel})} {f['url']}")


def coletar(data: str | None = None) -> None:
    cliente, ids, ex = Cliente(pausa=1.5), RegistroIds(), Execucao("redes", data)
    buscas = []
    for f in fontes():
        sel = uma_por_ano(copias(cliente, f["url"], f["busca"]))
        baixadas = 0
        for t, o in sel:
            try:
                ex.baixar(cliente, f"https://web.archive.org/web/{t}id_/{o}", f"{f['id_rede']}/{nome_local(t, o)}")
                baixadas += 1
            except Exception as e:  # noqa: BLE001 — uma cópia com erro não interrompe as demais; fica no log da busca
                print(f"FALHA {f['id_rede']} {t} {o}: {e}")
        buscas.append((f, len(sel), baixadas))
        print(f"{f['id_rede']}: {baixadas}/{len(sel)} cópias de {f['url']}")
    regs = ex.fechar()
    for f, n, baixadas in buscas:
        registrar_busca(f"Internet Archive (Wayback Machine): {f['nome']}", f"cópias anuais de {f['url']}", baixadas, SCRIPT, ex.data,
                        {"url": f["url"], "busca": f["busca"], "copias_no_indice": n, "ano_inicial": ANO_INICIAL}, None, ids)
    ids.salvar()
    print(f"{len(regs)} arquivos gravados")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--planejar", action="store_true")
    a = ap.parse_args()
    planejar() if a.planejar else coletar()
