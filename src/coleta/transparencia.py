"""Coletor do Portal da Transparência (CGU), área de download em lote, etapa E6.

Não usa a API (que exige cadastro de chave): baixa os arquivos completos publicados em
https://portaldatransparencia.gov.br/download-de-dados/<conjunto>. A página de cada conjunto indica a
data do arquivo mais recente (`arquivos.push({...})`); o endereço de download redireciona para
dadosabertos-download.cgu.gov.br.

Conjuntos: acordos de leniência, CNEP (Cadastro Nacional de Empresas Punidas, Lei 12.846/2013), CEIS
(Cadastro de Empresas Inidôneas e Suspensas) e emendas parlamentares (arquivo único, todos os anos).

Uso:
    python -m src.coleta.transparencia --planejar
    python -m src.coleta.transparencia
"""

import argparse
import re

from src.base import RegistroIds
from src.coleta.comum import LIMITE_ARQUIVO, Cliente, Execucao, registrar_busca

PORTAL = "https://portaldatransparencia.gov.br/download-de-dados/{conjunto}"
CONJUNTOS = {"acordos-leniencia": "diario", "cnep": "diario", "ceis": "diario", "emendas-parlamentares": "unico"}
SCRIPT = "src.coleta.transparencia"


def url_do_arquivo(cliente: Cliente, conjunto: str) -> str:
    if CONJUNTOS[conjunto] == "unico":
        return PORTAL.format(conjunto=conjunto) + "/UNICO"
    r = cliente.get(PORTAL.format(conjunto=conjunto), headers={"Accept": "text/html"})
    r.raise_for_status()
    datas = re.findall(r'arquivos\.push\(\{"ano" : "(\d{4})", "mes" : "(\d{2})", "dia" : "(\d{2})"', r.text)
    if not datas:
        raise RuntimeError(f"data do arquivo não encontrada na página de {conjunto}")
    a, m, d = max(datas)
    return PORTAL.format(conjunto=conjunto) + f"/{a}{m}{d}"


def planejar() -> list[tuple[str, str, int | None]]:
    cliente, saida = Cliente(), []
    for c in CONJUNTOS:
        url = url_do_arquivo(cliente, c)
        h = cliente.sessao.head(url, allow_redirects=True, timeout=60)
        saida.append((c, h.url, int(h.headers["Content-Length"]) if "Content-Length" in h.headers else None))
    return saida


def coletar(data: str | None = None) -> None:
    cliente, ids, ex = Cliente(), RegistroIds(), Execucao("transparencia", data)
    for c in CONJUNTOS:
        url = url_do_arquivo(cliente, c)
        h = cliente.sessao.head(url, allow_redirects=True, timeout=60)
        tamanho = int(h.headers.get("Content-Length", 0))
        if tamanho > LIMITE_ARQUIVO:
            raise SystemExit(f"{c}: {tamanho / 1e6:.0f} MB passa de 50 MB; pedir autorização do autor (CLAUDE.md, seção 6)")
        destino = ex.baixar(cliente, h.url, f"{c}_{h.url.rsplit('/', 1)[1]}")
        print(f"{c}: {destino.name} ({destino.stat().st_size / 1e6:.1f} MB)")
    for reg in ex.fechar():
        registrar_busca("Portal da Transparência (CGU), download de dados", f"arquivo {reg['arquivo'].rsplit('/', 1)[1]}", 1, SCRIPT, ex.data,
                        {"url": reg["url_base"]}, reg, ids)
    ids.salvar()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--planejar", action="store_true")
    a = ap.parse_args()
    print(planejar()) if a.planejar else coletar()
