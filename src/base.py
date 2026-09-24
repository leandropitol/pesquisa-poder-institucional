"""Leitura e gravação das tabelas de data/base e registro estável de identificadores.

`RegistroIds` guarda em data/ids_externos.csv a correspondência entre uma chave externa
(por exemplo "camara:74646" ou "raw:camara/2026-09-24/historicos.jsonl") e o identificador
interno (ATR-000123, FNT-000004). Assim, rodar a normalização de novo mantém os mesmos ids.
"""

import csv
from pathlib import Path

import pandas as pd

from src.esquema import POR_NOME

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ / "data" / "base"
IDS = RAIZ / "data" / "ids_externos.csv"


def ler(nome: str, base: Path = BASE) -> pd.DataFrame:
    caminho = base / f"{nome}.csv"
    if not caminho.exists():
        return pd.DataFrame(columns=POR_NOME[nome].nomes, dtype=str)
    return pd.read_csv(caminho, dtype=str, keep_default_na=False, encoding="utf-8")


def gravar(nome: str, df: pd.DataFrame, base: Path = BASE) -> None:
    t = POR_NOME[nome]
    saida = df.reindex(columns=t.nomes).fillna("").astype(str)
    saida = saida.sort_values(list(t.chave), kind="stable").reset_index(drop=True)
    saida.to_csv(base / f"{nome}.csv", index=False, encoding="utf-8", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)


def acrescentar(nome: str, linhas: list[dict], base: Path = BASE) -> None:
    """Acrescenta linhas sem reescrever as existentes (tabelas que só crescem)."""
    if not linhas:
        return
    cols = POR_NOME[nome].nomes
    caminho = base / f"{nome}.csv"
    with caminho.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writerows([{c: l.get(c, "") for c in cols} for l in linhas])


class RegistroIds:
    def __init__(self, caminho: Path = IDS, base: Path = BASE):
        self.caminho, self.base = caminho, base
        self.mapa: dict[tuple[str, str], str] = {}
        if caminho.exists():
            for l in csv.DictReader(caminho.open(encoding="utf-8")):
                self.mapa[(l["tabela"], l["chave_externa"])] = l["id"]
        self._ultimo: dict[str, int] = {}

    def _proximo(self, tabela: str) -> str:
        prefixo = POR_NOME[tabela].prefixo
        if tabela not in self._ultimo:
            usados = [v for (t, _), v in self.mapa.items() if t == tabela]
            usados += list(ler(tabela, self.base)[POR_NOME[tabela].chave[0]])
            self._ultimo[tabela] = max([int(u.split("-")[1]) for u in usados if u.startswith(prefixo + "-")] or [0])
        self._ultimo[tabela] += 1
        return f"{prefixo}-{self._ultimo[tabela]:06d}"

    def obter(self, tabela: str, chave: str) -> str:
        if (tabela, chave) not in self.mapa:
            self.mapa[(tabela, chave)] = self._proximo(tabela)
        return self.mapa[(tabela, chave)]

    def vincular(self, tabela: str, chave: str, ident: str) -> None:
        self.mapa[(tabela, chave)] = ident

    def existe(self, tabela: str, chave: str) -> bool:
        return (tabela, chave) in self.mapa

    def salvar(self) -> None:
        linhas = sorted(({"tabela": t, "chave_externa": c, "id": i} for (t, c), i in self.mapa.items()), key=lambda l: (l["tabela"], l["id"], l["chave_externa"]))
        with self.caminho.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["tabela", "chave_externa", "id"], lineterminator="\n")
            w.writeheader()
            w.writerows(linhas)


def cnpj_digitos(cnpj: str) -> str:
    return "".join(c for c in (cnpj or "") if c.isdigit())


def id_empresa(ids: "RegistroIds", cnpj: str) -> str:
    """Identificador da empresa pelo CNPJ só com dígitos; reaproveita chaves antigas com CNPJ formatado."""
    d = cnpj_digitos(cnpj)
    chave = f"cnpj14:{d}" if len(d) == 14 else f"cnpj_fonte:{cnpj.strip()}"
    if not ids.existe("instituicoes", chave) and len(d) == 14:
        for (tab, ch), ident in list(ids.mapa.items()):
            if tab == "instituicoes" and ch.startswith("cnpj:") and cnpj_digitos(ch[5:]) == d:
                ids.vincular("instituicoes", chave, ident)
                break
    return ids.obter("instituicoes", chave)
