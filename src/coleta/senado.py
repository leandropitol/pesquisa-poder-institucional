"""Coletor do Senado Federal (dados abertos), etapa E1.

Baixa, para as legislaturas de 52 (2003) até a atual:
  1. os senadores de cada legislatura, com os mandatos (`/senador/lista/legislatura/N`), que trazem
     titulares e suplentes;
  2. as filiações partidárias de cada senador, com data de filiação e de desfiliação
     (`/senador/{codigo}/filiacoes`).

Uso:
    python -m src.coleta.senado --planejar
    python -m src.coleta.senado
"""

import argparse

from src.base import RegistroIds
from src.coleta.comum import Cliente, Execucao, registrar_busca

API = "https://legis.senado.leg.br/dadosabertos"
SCRIPT = "src.coleta.senado"


def parlamentares(corpo: dict) -> list[dict]:
    lista = (corpo or {}).get("ListaParlamentarLegislatura", {}).get("Parlamentares", {}).get("Parlamentar", [])
    return lista if isinstance(lista, list) else [lista]


def planejar(legislaturas: range) -> dict:
    cliente, codigos = Cliente(), set()
    for n in legislaturas:
        codigos |= {p["IdentificacaoParlamentar"]["CodigoParlamentar"] for p in parlamentares(cliente.get(f"{API}/senador/lista/legislatura/{n}.json").json())}
    return {"legislaturas": list(legislaturas), "senadores_distintos": len(codigos), "requisicoes_estimadas": len(legislaturas) + len(codigos)}


def coletar(legislaturas: range, data: str | None = None) -> None:
    cliente, execucao, ids = Cliente(), Execucao("senado", data), RegistroIds()
    codigos: set[str] = set()
    contagens = {}
    for n in legislaturas:
        r = cliente.get(f"{API}/senador/lista/legislatura/{n}.json")
        corpo = execucao.gravar("senadores_por_legislatura.jsonl", f"{API}/senador/lista/legislatura/{{n}}.json", r, {"legislatura": n})
        r.raise_for_status()
        lista = parlamentares(corpo)
        contagens[n] = len(lista)
        codigos |= {p["IdentificacaoParlamentar"]["CodigoParlamentar"] for p in lista}
        print(f"legislatura {n}: {len(lista)} parlamentares")
    n_filiacoes = 0
    for i, cod in enumerate(sorted(codigos, key=int), 1):
        r = cliente.get(f"{API}/senador/{cod}/filiacoes.json")
        corpo = execucao.gravar("filiacoes.jsonl", f"{API}/senador/{{codigo}}/filiacoes.json", r)
        f = ((corpo or {}).get("FiliacaoParlamentar", {}).get("Parlamentar", {}).get("Filiacoes") or {}).get("Filiacao", [])
        n_filiacoes += len(f if isinstance(f, list) else [f])
        if i % 100 == 0:
            print(f"filiações: {i} de {len(codigos)}")

    arquivos = {a["arquivo"].rsplit("/", 1)[1]: a for a in execucao.fechar()}
    d = execucao.data
    for n, k in contagens.items():
        registrar_busca("Senado, dados abertos", f"senadores da legislatura {n}", k, SCRIPT, d, {"legislatura": n},
                        arquivos["senadores_por_legislatura.jsonl"], ids)
    registrar_busca("Senado, dados abertos", f"filiações de {len(codigos)} senadores", n_filiacoes, SCRIPT, d, None, arquivos["filiacoes.jsonl"], ids)
    ids.salvar()
    print(f"{cliente.n_requisicoes} requisições; {len(codigos)} senadores; {n_filiacoes} filiações")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--planejar", action="store_true")
    ap.add_argument("--ate", type=int, default=57, help="última legislatura")
    args = ap.parse_args()
    legs = range(52, args.ate + 1)
    print(planejar(legs)) if args.planejar else coletar(legs)
