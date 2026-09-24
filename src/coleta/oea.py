"""Coletor dos volumes oficiais de resoluções da Assembleia Geral da OEA (etapa E8, bloco A3).

A lista de volumes (sessões ordinárias de 2003 em diante e as extraordinárias com conteúdo político)
está em data/curadoria/oea_volumes.csv, extraída do índice oficial https://www.oas.org/es/council/AG/resdec/.
Cada volume ("Actas y Documentos, Volumen I") traz o texto certificado das declarações e resoluções
aprovadas na sessão, com as notas de rodapé dos Estados.

Uso:
    python -m src.coleta.oea --planejar
    python -m src.coleta.oea
"""

import argparse
import csv
import re

from src.base import RAIZ, RegistroIds
from src.coleta.comum import LIMITE_ARQUIVO, Cliente, Execucao, registrar_busca

LISTA = RAIZ / "data" / "curadoria" / "oea_volumes.csv"
SCRIPT = "src.coleta.oea"


def volumes() -> list[dict]:
    return list(csv.DictReader(LISTA.open(encoding="utf-8")))


def nome_local(v: dict) -> str:
    return f"{v['ano']}_{v['sessao']}_{re.sub(r'[^A-Za-z0-9._-]', '_', v['url'].rsplit('/', 1)[1])}"


def planejar() -> list[tuple[str, int, int | None]]:
    cliente, saida = Cliente(), []
    for v in volumes():
        try:
            r = cliente.sessao.get(v["url"], stream=True, allow_redirects=True, timeout=60, headers={"Accept": "*/*"})
            saida.append((nome_local(v), r.status_code, int(r.headers.get("Content-Length", 0)) or None))
            r.close()
        except Exception as e:  # noqa: BLE001
            saida.append((nome_local(v), type(e).__name__, None))
    return saida


def coletar(data: str | None = None) -> None:
    cliente, ids, ex = Cliente(pausa=1.0), RegistroIds(), Execucao("oea", data)
    falhas = []
    for v in volumes():
        try:
            destino = ex.baixar(cliente, v["url"], nome_local(v))
            if destino.stat().st_size > LIMITE_ARQUIVO:
                print(f"AVISO: {destino.name} passa de 50 MB")
            print(f"{v['ano']} {v['sessao']}: {destino.stat().st_size / 1e6:.1f} MB")
        except Exception as e:  # noqa: BLE001 — falha de um volume não interrompe os demais; fica registrada
            falhas.append((v["sessao"], v["url"], f"{type(e).__name__}: {e}"[:200]))
            print(f"FALHA {v['ano']} {v['sessao']}: {e}")
    for reg in ex.fechar():
        registrar_busca("OEA, volumes de resoluções da Assembleia Geral", f"volume {reg['arquivo'].rsplit('/', 1)[1]}", 1, SCRIPT, ex.data,
                        {"url": reg["url_base"]}, reg, ids)
    for sessao, url, erro in falhas:
        registrar_busca("OEA, volumes de resoluções da Assembleia Geral", f"volume da sessão {sessao} (falha no download)", 0, SCRIPT, ex.data,
                        {"url": url, "erro": erro}, None, ids)
    ids.salvar()
    print(f"{len(volumes()) - len(falhas)} volumes baixados; {len(falhas)} falhas")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--planejar", action="store_true")
    a = ap.parse_args()
    print(planejar()) if a.planejar else coletar()
