"""Registro da captura da página de partidos do TSE (etapa E1, sucessão partidária).

O portal do TSE recusa cliente automatizado (HTTP 403, D-009). A página pública
https://www.tse.jus.br/partidos/partidos-registrados-no-tse foi lida no navegador do
aplicativo, uma vez, à vista do autor (D-015). As tabelas foram extraídas do DOM com o
trecho JavaScript abaixo e gravadas em data/raw/tse_partidos/<data>/tabelas_partidos_registrados.json.
A integridade da cópia foi conferida comparando o sha256 do JSON das tabelas calculado no
navegador com o calculado sobre o arquivo gravado (`hash_tabelas`).

    const limpa = s => s.replace(/\\s+/g, ' ').trim();
    const tabs = [...document.querySelectorAll('table')].map((t, i) => ({i,
      linhas: [...t.querySelectorAll('tr')].map(tr => [...tr.querySelectorAll('td,th')].map(c => limpa(c.innerText)))}));

Este módulo não acessa a rede: só registra o arquivo no manifesto e em `buscas`.

Uso:
    python -m src.coleta.tse_partidos --data 2026-09-24 --hash-navegador <sha256>
"""

import argparse
import csv
import hashlib
import json

from src.base import RAIZ, RegistroIds
from src.coleta.comum import MANIFESTOS, RAW, registrar_busca, sha256

FONTE = "tse_partidos"
ARQUIVO = "tabelas_partidos_registrados.json"
URL = "https://www.tse.jus.br/partidos/partidos-registrados-no-tse"
SCRIPT = "src.coleta.tse_partidos"


def hash_tabelas(caminho) -> str:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    return hashlib.sha256(json.dumps(dados["tabelas"], ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def registrar(data: str, hash_navegador: str) -> None:
    caminho = RAW / FONTE / data / ARQUIVO
    if hash_tabelas(caminho) != hash_navegador:
        raise ValueError("o arquivo gravado não confere com o hash calculado no navegador")
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    n = sum(max(len(t["linhas"]) - 1, 0) for t in dados["tabelas"])
    reg = {"data_acesso": data, "arquivo": caminho.relative_to(RAIZ).as_posix(), "url_base": URL, "n_requisicoes": 1,
           "bytes": caminho.stat().st_size, "sha256": sha256(caminho)}
    manifesto = MANIFESTOS / f"{FONTE}.csv"
    novo = not manifesto.exists()
    with manifesto.open("a", encoding="utf-8", newline="") as m:
        w = csv.DictWriter(m, fieldnames=list(reg), lineterminator="\n")
        if novo:
            w.writeheader()
        w.writerow(reg)
    ids = RegistroIds()
    registrar_busca("TSE, página de partidos registrados (leitura no navegador, D-015)",
                    "partidos registrados; fusões, incorporações e mudanças de nome ou sigla desde a Lei 9.096/1995; números de legenda reutilizados",
                    n, SCRIPT, data, {"hash_tabelas_navegador": hash_navegador}, reg, ids)
    ids.salvar()
    print(f"registrado: {reg['arquivo']} ({n} linhas de tabela)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--hash-navegador", required=True)
    a = ap.parse_args()
    registrar(a.data, a.hash_navegador)
