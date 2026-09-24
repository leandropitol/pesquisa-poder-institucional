"""Coletor da Câmara dos Deputados (API de dados abertos v2), etapa E1.

Baixa, para as legislaturas de 52 (2003) até a atual:
  1. as legislaturas e suas datas (`/legislaturas`);
  2. os deputados de cada legislatura (`/deputados?idLegislatura=N`), com paginação;
  3. o histórico de cada deputado (`/deputados/{id}/historico`): partido, situação e condição
     eleitoral com data e hora, em todas as legislaturas;
  4. os partidos citados (`/partidos/{id}`).

Não chama `/deputados/{id}` (detalhe), que devolve CPF: o dado bruto não pode ser editado, e o
projeto não guarda CPF (D-011).

Uso:
    python -m src.coleta.camara --planejar     # só conta o que seria baixado
    python -m src.coleta.camara                # coleta e registra
"""

import argparse
import datetime as dt
import re

from src.base import RegistroIds
from src.coleta.comum import Cliente, Execucao, registrar_busca

API = "https://dadosabertos.camara.leg.br/api/v2"
LEGISLATURA_INICIAL = 52
SCRIPT = "src.coleta.camara"


def _paginas(cliente: Cliente, execucao: Execucao | None, arquivo: str, url: str, params: dict) -> list[dict]:
    dados, proxima, p = [], url, dict(params)
    while proxima:
        r = cliente.get(proxima, params=p)
        corpo = execucao.gravar(arquivo, url, r, p) if execucao else r.json()
        r.raise_for_status()
        dados += corpo["dados"]
        proxima = next((l["href"] for l in corpo.get("links", []) if l["rel"] == "next"), None)
        p = None  # o link "next" já traz os parâmetros
    return dados


def legislaturas_no_periodo(legislaturas: list[dict], hoje: str) -> list[dict]:
    return sorted((l for l in legislaturas if l["id"] >= LEGISLATURA_INICIAL and l["dataInicio"] <= hoje), key=lambda l: l["id"])


def id_partido(uri: str | None) -> str | None:
    m = re.search(r"/partidos/(\d+)$", uri or "")
    return m.group(1) if m else None


def planejar(cliente: Cliente | None = None) -> dict:
    cliente = cliente or Cliente()
    hoje = dt.date.today().isoformat()
    legs = legislaturas_no_periodo(_paginas(cliente, None, "", f"{API}/legislaturas", {"itens": 100}), hoje)
    ids = set()
    for l in legs:
        ids |= {d["id"] for d in _paginas(cliente, None, "", f"{API}/deputados", {"idLegislatura": l["id"], "itens": 100})}
    return {"legislaturas": [l["id"] for l in legs], "deputados_distintos": len(ids),
            "requisicoes_estimadas": 1 + len(legs) * 6 + len(ids) + 80}


def coletar(data: str | None = None) -> None:
    cliente, execucao, ids = Cliente(), Execucao("camara", data), RegistroIds()
    hoje = dt.date.today().isoformat()
    legs = legislaturas_no_periodo(_paginas(cliente, execucao, "legislaturas.jsonl", f"{API}/legislaturas", {"itens": 100}), hoje)
    contagens = {}
    deputados: set[int] = set()
    partidos: set[str] = set()
    for l in legs:
        lista = _paginas(cliente, execucao, "deputados_por_legislatura.jsonl", f"{API}/deputados",
                         {"idLegislatura": l["id"], "itens": 100, "ordem": "ASC", "ordenarPor": "nome"})
        contagens[l["id"]] = len(lista)
        deputados |= {d["id"] for d in lista}
        partidos |= {p for p in (id_partido(d.get("uriPartido")) for d in lista) if p}
        print(f"legislatura {l['id']}: {len(lista)} deputados")

    n_registros = 0
    for i, dep in enumerate(sorted(deputados), 1):
        r = cliente.get(f"{API}/deputados/{dep}/historico")
        corpo = execucao.gravar("historicos.jsonl", f"{API}/deputados/{{id}}/historico", r)
        if r.ok and corpo:
            n_registros += len(corpo["dados"])
            partidos |= {p for p in (id_partido(h.get("uriPartido")) for h in corpo["dados"]) if p}
        if i % 250 == 0:
            print(f"históricos: {i} de {len(deputados)}")

    for p in sorted(partidos, key=int):
        execucao.gravar("partidos.jsonl", f"{API}/partidos/{{id}}", cliente.get(f"{API}/partidos/{p}"))

    arquivos = {a["arquivo"].rsplit("/", 1)[1]: a for a in execucao.fechar()}
    d = execucao.data
    registrar_busca("Câmara, API v2", "legislaturas", len(legs), SCRIPT, d, {"itens": 100}, arquivos["legislaturas.jsonl"], ids)
    for leg, n in contagens.items():
        registrar_busca("Câmara, API v2", f"deputados da legislatura {leg}", n, SCRIPT, d, {"idLegislatura": leg},
                        arquivos["deputados_por_legislatura.jsonl"], ids)
    registrar_busca("Câmara, API v2", f"histórico de {len(deputados)} deputados das legislaturas {legs[0]['id']} a {legs[-1]['id']}",
                    n_registros, SCRIPT, d, None, arquivos["historicos.jsonl"], ids)
    registrar_busca("Câmara, API v2", f"{len(partidos)} partidos citados", len(partidos), SCRIPT, d, None, arquivos["partidos.jsonl"], ids)
    ids.salvar()
    print(f"{cliente.n_requisicoes} requisições; {len(deputados)} deputados; {n_registros} registros de histórico; {len(partidos)} partidos")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--planejar", action="store_true")
    args = ap.parse_args()
    print(planejar()) if args.planejar else coletar()
