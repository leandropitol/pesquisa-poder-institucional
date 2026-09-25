"""Registro dos arquivos do portal de dados abertos do TSE baixados pelo autor (etapa E7).

O portal (https://dadosabertos.tse.jus.br) não entrega a cliente automatizado (D-009); o autor baixou os
ZIP no navegador. Este módulo registra só os conjuntos que a pesquisa usa (USADOS): move para
data/raw/tse/<data>/, calcula o sha256 e grava manifesto e busca. Não acessa a rede.

Ficam de fora, onde estão: cópias repetidas ("(1)" no nome), arquivos vazios e conjuntos com dados
pessoais que a pesquisa não usa (bens declarados e extratos bancários de candidatos), por minimização.

Uso:
    python -m src.coleta.tse --data 2026-09-25
"""

import argparse
import csv
import re
import shutil

from src.base import RAIZ, RegistroIds
from src.coleta.comum import MANIFESTOS, RAW, registrar_busca, sha256

SCRIPT = "src.coleta.tse"
FONTE = "TSE, portal de dados abertos (download feito pelo autor no navegador, D-042)"
PORTAL = "https://dadosabertos.tse.jus.br/"
USADOS = re.compile(r"^(consulta_cand(_complementar)?|consulta_coligacao|consulta_vagas|motivo_cassacao|prestacao_contas|prestacao_final|"
                    r"prestacao_contas_final_sup|prestacao_de_contas_eleitorais_(candidatos|orgaos_partidarios)|prestacao_contas_anual_partidaria|"
                    r"fefc_fp|CNPJ_campanha)_\d{4}\.zip$")


def registrar_manuais(data: str) -> None:
    raiz = RAW / "tse"
    pasta = raiz / data
    pasta.mkdir(parents=True, exist_ok=True)
    ids, regs, fora = RegistroIds(), [], []
    for f in sorted(p for p in raiz.iterdir() if p.is_file()):
        if not USADOS.match(f.name) or f.stat().st_size == 0:
            fora.append(f.name)
            continue
        destino = pasta / f.name
        if destino.exists():
            fora.append(f.name)
            continue
        shutil.move(f, destino)
        reg = {"data_acesso": data, "arquivo": destino.relative_to(RAIZ).as_posix(), "url_base": PORTAL, "n_requisicoes": 1,
               "bytes": destino.stat().st_size, "sha256": sha256(destino)}
        regs.append(reg)
        registrar_busca(FONTE, f"conjunto {f.name}", 1, SCRIPT, data, {"url": PORTAL, "arquivo": f.name}, reg, ids)
    caminho = MANIFESTOS / "tse.csv"
    novo = not caminho.exists()
    with caminho.open("a", encoding="utf-8", newline="") as m:
        w = csv.DictWriter(m, fieldnames=["data_acesso", "arquivo", "url_base", "n_requisicoes", "bytes", "sha256"], lineterminator="\n")
        if novo:
            w.writeheader()
        w.writerows(regs)
    ids.salvar()
    print(f"{len(regs)} registrados; fora do registro (ficam onde estão): {fora}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    registrar_manuais(ap.parse_args().data)
