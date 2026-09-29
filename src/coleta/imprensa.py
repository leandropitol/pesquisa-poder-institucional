"""Registro das buscas do contraste com a imprensa (D-047, D-055, D-056).

As buscas são feitas pela ferramenta de busca na web do assistente, restritas ao domínio de cada veículo, com a
consulta fixa de cada fato (data/curadoria/imprensa_fatos.csv). Este módulo grava no bruto, sem alteração, o que a
ferramenta devolveu (título e URL de cada link; o resumo automático não é guardado nem usado) e registra cada busca
em `buscas`, inclusive as sem resultado e as sem acesso.

Uso (a partir de um arquivo JSON com os registros de um lote):
    python -m src.coleta.imprensa <arquivo.json> --data AAAA-MM-DD
"""

import argparse
import datetime as dt
import json
from pathlib import Path

from src.base import RAIZ, RegistroIds
from src.coleta.comum import registrar_busca, sha256

RAW = RAIZ / "data" / "raw" / "imprensa"
SCRIPT = "src.coleta.imprensa"
FONTE = "Ferramenta de busca na web do assistente (restrita ao domínio do veículo)"


def registrar(registros: list[dict], data: str) -> None:
    """Cada registro: {fato, veiculo, dominio, consulta, acesso ('ok' | 'sem_acesso' | 'bloqueado'), links: [{title, url}]}."""
    pasta = RAW / data
    pasta.mkdir(parents=True, exist_ok=True)
    arq = pasta / "buscas.jsonl"
    with arq.open("a", encoding="utf-8", newline="\n") as f:
        for r in registros:
            f.write(json.dumps({**r, "registrado_em": dt.datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False) + "\n")
    ids = RegistroIds()
    reg = {"arquivo": arq.relative_to(RAIZ).as_posix(), "sha256": ""}  # arquivo cresce ao longo do dia; sha256 fica no manifesto ao fechar
    for r in registros:
        consulta = f"{r['fato']} | {r['veiculo']} ({r['dominio']}): {r['consulta']}"
        registrar_busca(FONTE, consulta, len(r["links"]) if r["acesso"] == "ok" else 0, SCRIPT, data,
                        {"fato": r["fato"], "dominio": r["dominio"], "acesso": r["acesso"]}, reg, ids)
    ids.salvar()


def fechar_manifesto(data: str) -> None:
    arq = RAW / data / "buscas.jsonl"
    man = RAIZ / "data" / "manifestos" / "imprensa.csv"
    novo = not man.exists()
    with man.open("a", encoding="utf-8", newline="") as m:
        if novo:
            m.write("data_acesso,arquivo,url_base,n_requisicoes,bytes,sha256\n")
        n = sum(1 for _ in arq.open(encoding="utf-8"))
        m.write(f"{data},{arq.relative_to(RAIZ).as_posix()},ferramenta de busca na web,{n},{arq.stat().st_size},{sha256(arq)}\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo", nargs="?")
    ap.add_argument("--data", required=True)
    ap.add_argument("--fechar", action="store_true")
    a = ap.parse_args()
    if a.fechar:
        fechar_manifesto(a.data)
    else:
        registrar(json.loads(Path(a.arquivo).read_text(encoding="utf-8")), a.data)
