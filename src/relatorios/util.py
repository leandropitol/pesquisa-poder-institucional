"""Auxiliares dos relatórios finais (fechamento do estudo): formatação em português, citação de fontes e leitura das tabelas de saída."""

import subprocess

import pandas as pd

from src.base import BASE, RAIZ, ler

TAB = RAIZ / "relatorios" / "tabelas"


def tabela(nome: str) -> pd.DataFrame:
    return pd.read_csv(TAB / f"{nome}.csv")


def milhar(x) -> str:
    return f"{int(round(float(x))):,}".replace(",", ".")


def dec(x, casas: int = 2) -> str:
    return f"{float(x):.{casas}f}".replace(".", ",")


def pct(x, casas: int = 1) -> str:
    return f"{float(x) * 100:.{casas}f}".replace(".", ",") + "%"


def pv(p) -> str:
    p = float(p)
    return "p < 0,001" if p < 0.001 else f"p = {p:.3f}".replace(".", ",")


def commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""


class Fontes:
    """Registra as fontes citadas nas frases do relatório; o apêndice lista cada uma. Fontes do DataJud nunca são citadas (CLAUDE.md, seção 6)."""

    def __init__(self, base=BASE):
        f = ler("fontes", base).fillna("")
        self.f = f[~f["licenca"].str.contains("DataJud", case=False) & ~f["titulo"].str.contains("DataJud", case=False)].set_index("id_fonte")
        self.citadas: set[str] = set()
        self.tabelas: set[str] = set()

    def ids(self, *padroes: str) -> list[str]:
        if not padroes:
            return []
        achados = [i for i, r in self.f.iterrows() if any(p.lower() in (r["titulo"] + " " + r["caminho_raw"]).lower() for p in padroes)]
        return sorted(achados)

    def cit(self, tabelas: tuple = (), decisoes: tuple = (), padroes: tuple = (), ids: list | None = None) -> str:
        partes = []
        for t in tabelas:
            self.tabelas.add(t)
            partes.append(f"`{t}`")
        achados = list(ids) if ids is not None else self.ids(*padroes)
        self.citadas.update(achados)
        if achados:
            mostrar = ", ".join(achados[:3]) + (f" e mais {len(achados) - 3}" if len(achados) > 3 else "")
            partes.append(f"fontes {mostrar}")
        if decisoes:
            partes.append(", ".join(decisoes))
        return "*(Fonte: " + "; ".join(partes) + ")*" if partes else ""

    def apendice(self) -> list:
        linhas = ["| Id | Tipo | Título | Data de acesso | URL | sha256 (início) |", "|---|---|---|---|---|---|"]
        for i in sorted(self.citadas):
            r = self.f.loc[i]
            linhas.append(f"| {i} | {r['tipo_fonte']} | {r['titulo'].replace('|', '/')[:150]} | {r['data_acesso']} | {r['url'][:110]} | {r['sha256'][:12]} |")
        return linhas
