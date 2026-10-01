"""Extrai do Resultado do Tesouro Nacional (série histórica, dez/2025) as linhas anuais usadas no livro.

Fonte: Tesouro Nacional, Boletim Resultado do Tesouro Nacional, dezembro de 2025, anexo
"serie_historica_dez25.xlsx" (https://thot-arquivos.tesouro.gov.br/publicacao-anexo/27550), baixado pelo
autor em 2026-09-30 (D-009, D-070); sha256 em data/manifestos/tesouro.csv. Tabela 2.1 (anual, R$ milhões
correntes). Grava data/curadoria/tesouro_rtn_anual.csv.
"""
from __future__ import annotations

import hashlib

import openpyxl
import pandas as pd

from .comum import CUR, RAIZ

ARQ = RAIZ / "data/raw/tesouro/2026-09-30/serie_historica_dez25.xlsx"
LINHAS = {
    "4. DESPESA TOTAL": "despesa_total",
    "4.4.2 Despesas Discricionárias": "despesas_discricionarias_executivo",
    "4.3.19 Financiamento de Campanha Eleitoral": "fefc",
    "3. RECEITA LÍQUIDA  (1-2)": "receita_liquida",
}


def main() -> None:
    man = pd.read_csv(RAIZ / "data/manifestos/tesouro.csv")
    sha = hashlib.sha256(ARQ.read_bytes()).hexdigest()
    assert sha == man.sha256.iloc[0], "sha256 não confere com o manifesto"
    ws = openpyxl.load_workbook(ARQ, read_only=True, data_only=True)["2.1"]
    rows = list(ws.iter_rows(values_only=True))
    anos = rows[4][1:]
    out = []
    for r in rows:
        rot = str(r[0]).strip() if r[0] else ""
        for chave, nome in LINHAS.items():
            if rot.startswith(chave):
                for ano, v in zip(anos, r[1:]):
                    if isinstance(ano, int):
                        out.append(dict(ano=ano, linha=nome, rotulo_original=rot, valor_rs_milhoes=v))
    df = pd.DataFrame(out)
    df["fonte"] = "Tesouro Nacional, RTN dez/2025, série histórica, Tabela 2.1 (R$ milhões correntes)"
    df["url"] = "https://thot-arquivos.tesouro.gov.br/publicacao-anexo/27550"
    df["data_acesso"] = "2026-09-30"
    df.to_csv(CUR / "tesouro_rtn_anual.csv", index=False)
    print(df.pivot_table(index="ano", columns="linha", values="valor_rs_milhoes").tail(10).round(0))


if __name__ == "__main__":
    main()
