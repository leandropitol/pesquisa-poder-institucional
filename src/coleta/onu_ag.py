"""Registro do conjunto de votos da Assembleia Geral da ONU (etapa E8, bloco A1).

O servidor da UN Digital Library não entrega o arquivo a cliente automatizado (D-009) e o arquivo tem
364 MB; o autor baixou manualmente (D-032) de https://digitallibrary.un.org/record/4060887:
`2026_02_06_ga_voting.csv` (dados, versão 5) e `2026_02_06_ga_voting_md.md` (dicionário e termos de uso).
Este módulo move os arquivos para data/raw/onu_ag/<data>/, calcula o sha256, grava o manifesto e a busca.
Não acessa a rede.

Uso:
    python -m src.coleta.onu_ag --data 2026-09-24
"""

import argparse
import csv
import shutil

from src.base import RAIZ, RegistroIds
from src.coleta.comum import MANIFESTOS, RAW, registrar_busca, sha256

FONTE = "onu_ag"
URL = "https://digitallibrary.un.org/record/4060887"
ARQUIVOS = ["2026_02_06_ga_voting.csv", "2026_02_06_ga_voting_md.md"]
SCRIPT = "src.coleta.onu_ag"


def registrar(data: str) -> None:
    pasta = RAW / FONTE / data
    pasta.mkdir(parents=True, exist_ok=True)
    regs = []
    for nome in ARQUIVOS:
        origem, destino = RAW / FONTE / nome, pasta / nome
        if origem.exists() and not destino.exists():
            shutil.move(origem, destino)
        regs.append({"data_acesso": data, "arquivo": destino.relative_to(RAIZ).as_posix(), "url_base": f"{URL}/files/{nome}",
                     "n_requisicoes": 1, "bytes": destino.stat().st_size, "sha256": sha256(destino)})
    manifesto = MANIFESTOS / f"{FONTE}.csv"
    novo = not manifesto.exists()
    with manifesto.open("a", encoding="utf-8", newline="") as m:
        w = csv.DictWriter(m, fieldnames=list(regs[0]), lineterminator="\n")
        if novo:
            w.writeheader()
        w.writerows(regs)
    with (pasta / ARQUIVOS[0]).open(encoding="utf-8") as f:
        n = sum(1 for _ in f) - 1
    ids = RegistroIds()
    registrar_busca("ONU, UN Digital Library (download manual do autor, D-032)", "votos nominais da Assembleia Geral, resoluções 1 a 80/246",
                    n, SCRIPT, data, {"url": URL, "versao": "5 (fevereiro de 2026)"}, regs[0], ids)
    ids.salvar()
    print(f"registrado: {n} votos; sha256 {regs[0]['sha256']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    registrar(ap.parse_args().data)
