"""Caminhos, paleta, formatação e funções comuns aos scripts do livro.

Tudo é lido de `data/base/`, `relatorios/tabelas/` e `data/curadoria/`. Nada é digitado à mão:
os números do texto saem de `relatorios/livro/resultados.json`, gerado por `src.livro.calculos`.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
BASE = RAIZ / "data" / "base"
TAB = RAIZ / "relatorios" / "tabelas"
CUR = RAIZ / "data" / "curadoria"
SAIDA = RAIZ / "relatorios" / "livro"
FIG = SAIDA / "figuras"
TABS = SAIDA / "tabelas"
for _p in (SAIDA, FIG, TABS):
    _p.mkdir(parents=True, exist_ok=True)

# Paleta categórica de ordem fixa e rampa sequencial (azul).
C = dict(blue="#2a78d6", orange="#eb6834", aqua="#1baf7a", yellow="#eda100", magenta="#e87ba4",
         green="#008300", violet="#4a3aa7", red="#e34948", ink="#0b0b0b", ink2="#52514e",
         mute="#8a8983", grid="#e7e6e2", gray="#b9b8b2", navy="#0d366b")
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281", "#0d366b"]

DATA_CORTE = pd.Timestamp("2026-09-30")
ANOS_ELEICAO = [2002, 2006, 2010, 2014, 2018, 2022]


def br(x: float, d: int = 1) -> str:
    """Número no formato brasileiro (1.234,5)."""
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def ler(nome: str, pasta: Path = BASE, **kw) -> pd.DataFrame:
    return pd.read_csv(pasta / f"{nome}.csv", **kw)


# ---------- partidos ----------
_den = ler("denominacoes_partido")
_ins = ler("instituicoes")
SIGLA = _den.sort_values("data_inicio").groupby("id_partido").sigla.last().to_dict()
for _, _r in _ins[_ins.tipo_instituicao == "partido"].iterrows():
    SIGLA.setdefault(_r.id_instituicao, _r.sigla)
SIGLA["INS-000070"] = "DEM"  # linhagem PFL/DEM (D-016)
SUCESSORA = _ins.set_index("id_instituicao").id_sucessora.dropna().to_dict()
NOME_INS = _ins.set_index("id_instituicao").nome.to_dict()

_at = ler("atores")
NOME_ATOR = _at.set_index("id_ator").nome.to_dict()

_fil = ler("filiacoes")
for _c in ("data_inicio", "data_fim"):
    _fil[_c] = pd.to_datetime(_fil[_c], errors="coerce")
FILIACOES = _fil


def partido_na_data(data) -> pd.Series:
    """id_partido de cada ator na data (filiação vigente; D-016)."""
    d = pd.Timestamp(data)
    f = FILIACOES[(FILIACOES.data_inicio <= d) & (FILIACOES.data_fim.isna() | (FILIACOES.data_fim >= d))]
    return f.sort_values("data_inicio").drop_duplicates("id_ator", keep="last").set_index("id_ator").id_partido


# ---------- séries externas (D-070) ----------
def ipca() -> pd.Series:
    s = pd.read_csv(CUR / "ibge_ipca_numero_indice.csv", dtype={"periodo": str})
    return s.set_index("periodo").valor


IPCA_BASE_PERIODO = "202608"


def fator_real(periodo: str) -> float:
    """Multiplicador para levar um valor nominal do período ao poder de compra de IPCA_BASE_PERIODO."""
    s = ipca()
    return float(s[IPCA_BASE_PERIODO] / s[periodo])


def periodo_eleicao(ano: int) -> str:
    return f"{ano}10"  # índice de outubro do ano da eleição


def periodo_ano(ano: int) -> str:
    return f"{ano}06"  # índice de junho como meio do ano (fluxos anuais)


# ---------- resultados ----------
RES_PATH = SAIDA / "resultados.json"


def gravar_resultados(r: dict) -> None:
    antigo = json.loads(RES_PATH.read_text(encoding="utf-8")) if RES_PATH.exists() else {}
    antigo.update(r)
    RES_PATH.write_text(json.dumps(antigo, ensure_ascii=False, indent=1, default=float), encoding="utf-8")


def resultados() -> dict:
    return json.loads(RES_PATH.read_text(encoding="utf-8"))


def gini(x) -> float:
    x = np.sort(np.asarray(x, dtype=float))
    x = x[x >= 0]
    n = len(x)
    if n == 0 or x.sum() == 0:
        return float("nan")
    cum = np.cumsum(x)
    return float((n + 1 - 2 * (cum / cum[-1]).sum()) / n)


# ---------- gráficos e fichas ----------
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": C["gray"], "axes.labelcolor": C["ink2"],
    "xtick.color": C["ink2"], "ytick.color": C["ink2"], "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": C["grid"], "grid.linewidth": 0.6, "axes.axisbelow": True,
    "figure.facecolor": "white", "axes.facecolor": "white", "legend.frameon": False, "legend.fontsize": 8,
    "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlelocation": "left",
})

FICHAS_PATH = SAIDA / "fichas.json"


def fig(h: float = 3.4, w: float = 6.3):
    return plt.subplots(figsize=(w, h))


def nogridx(a):
    a.grid(axis="x", visible=False)


def nogridy(a):
    a.grid(axis="y", visible=False)


def _fichas() -> dict:
    return json.loads(FICHAS_PATH.read_text(encoding="utf-8")) if FICHAS_PATH.exists() else {}


def registrar(chave: str, **campos) -> None:
    """Registra a ficha de um gráfico ou tabela (campos do padrão do livro)."""
    f = _fichas()
    f[chave] = campos
    FICHAS_PATH.write_text(json.dumps(f, ensure_ascii=False, indent=1), encoding="utf-8")


def salvar(f, nome: str, **ficha) -> None:
    """Salva o gráfico (PNG, 220 dpi) e registra a ficha. Campos esperados na ficha: titulo, pergunta,
    periodo, unidade, universo, fonte_primaria, fonte_secundaria, tratamento, derivado, limitacoes,
    leitura, codigo."""
    f.tight_layout()
    f.savefig(FIG / f"{nome}.png", dpi=220, facecolor="white")
    plt.close(f)
    ficha.setdefault("fonte_secundaria", "Não há")
    ficha["tipo"] = "grafico"
    ficha["arquivo"] = f"relatorios/livro/figuras/{nome}.png"
    registrar(nome, **ficha)


def tabela(df: pd.DataFrame, nome: str, **ficha) -> None:
    """Grava a tabela em CSV e registra a ficha (titulo, unidade, periodo, universo, fonte, notas)."""
    df.to_csv(TABS / f"{nome}.csv", index=False)
    ficha["tipo"] = "tabela"
    ficha["arquivo"] = f"relatorios/livro/tabelas/{nome}.csv"
    registrar(nome, **ficha)


# Fontes primárias descritas uma vez (código FNT de data/base/fontes.csv)
F_TSE_CONTAS = ("Tribunal Superior Eleitoral, Portal de Dados Abertos, prestação de contas eleitorais de "
                "candidatos, eleições 2002 a 2022 (FNT-000077 a FNT-000082; arquivos e sha256 em "
                "data/manifestos/tse.csv), acesso em 25/09/2026")
F_TSE_CAND = ("Tribunal Superior Eleitoral, Portal de Dados Abertos, consulta de candidatos 2002 a 2022 "
              "(FNT-000071 a FNT-000076), acesso em 25/09/2026")
F_CGU_EMENDAS = ("Controladoria-Geral da União, Portal da Transparência, download de dados: emendas "
                 "parlamentares (FNT-000017; data/manifestos/transparencia.csv), acesso em 24/09/2026")
F_CGU_SANCOES = ("Controladoria-Geral da União, Portal da Transparência: CEIS, CNEP e acordos de leniência "
                 "(FNT-000014 a FNT-000016), arquivos de 23/09/2026, acesso em 24/09/2026")
F_STF = ("Supremo Tribunal Federal, Corte Aberta: decisões em ações penais e inquéritos de 08/01/2003 a "
         "23/09/2026 e acervo em tramitação (FNT-000046, FNT-000047, FNT-000232), exportação feita pelo "
         "autor (D-037); decisões publicadas no portal (FNT-000233 a FNT-000342)")
F_STF_MIN = ("Supremo Tribunal Federal, Biblioteca, páginas \"Dados e Datas\" dos ministros e notícias "
             "oficiais (FNT-000261 e seguintes), lidas no navegador em 29/09/2026 (D-058)")
F_TCU = ("Tribunal de Contas da União, Plataforma de Certidões: responsáveis com contas julgadas "
         "irregulares (FNT-000309), acesso em 29/09/2026")
F_CAMARA = ("Câmara dos Deputados, API de dados abertos v2 (FNT-000001 a FNT-000004) e Senado Federal, "
            "dados abertos (FNT-000005, FNT-000006), acesso em 24/09/2026")
F_ORIENT = ("Câmara dos Deputados, dados abertos, arquivos anuais de votações e orientações de bancada "
            "(data/manifestos/camara_orientacoes.csv; fonte ainda não registrada em fontes.csv), acesso "
            "em 28/09/2026")
F_ETICA = ("Câmara dos Deputados, tramitações das representações (FNT-000306); Senado Federal, processos "
           "do Conselho de Ética e projetos de resolução (FNT-000307, FNT-000308), acesso em 29/09/2026")
F_TSE_PART = ("Tribunal Superior Eleitoral, partidos registrados; fusões, incorporações e mudanças de nome "
              "(FNT-000007), lida no navegador em 24/09/2026 (D-015)")
F_BNDES = ("BNDES, dados abertos: operações de exportação pós-embarque, serviços de engenharia e bens "
           "(FNT-000011, FNT-000012), acesso em 24/09/2026")
F_ONU = ("Nações Unidas, UN Digital Library, dados de votação da Assembleia Geral, versão 5 (FNT-000018), e "
         "resoluções do Conselho de Direitos Humanos (FNT-000083 a FNT-000230); OEA, volumes e atas da "
         "Assembleia Geral (FNT-000019 a FNT-000045), acessos em 24 e 25/09/2026")
F_COMEX = ("Ministério do Desenvolvimento, Indústria, Comércio e Serviços, ComexStat, API pública "
           "(data/manifestos/comexstat.csv; fonte ainda não registrada em fontes.csv), acesso em 28/09/2026")
F_ITAMARATY = "Ministério das Relações Exteriores, Concórdia (FNT-000069, FNT-000070), acesso em 25/09/2026"
F_VDEM = ("V-Dem Institute, Country-Year Full+Others v16, pacote vdemdata (FNT-000008), acesso em "
          "24/09/2026")
F_FH = ("Freedom House, Freedom in the World: Ratings and Statuses 1973-2024 e Raw Data 2013-2024 "
        "(FNT-000009, FNT-000010), acesso em 24/09/2026")
F_IPCA = ("IBGE, SIDRA, tabela 1737, IPCA número-índice (dez/1993 = 100), acesso em 30/09/2026 "
          "(data/curadoria/ibge_ipca_numero_indice.csv; D-070)")
F_POP = ("IBGE, SIDRA, tabela 6579, população residente estimada por UF, 2025, acesso em 30/09/2026 "
         "(data/curadoria/ibge_populacao_uf.csv; D-070)")
F_RTN = ("Tesouro Nacional, Resultado do Tesouro Nacional, dez/2025, série histórica, Tabela 2.1 "
         "(data/manifestos/tesouro.csv; D-070), baixado pelo autor em 30/09/2026")
F_IDEOL = ("Bolognesi, Ribeiro e Codato (2023), Dados 66(2), doi 10.1590/dados.2023.66.2.303 "
           "(FNT-000305)")
REPO = "https://github.com/leandropitol/pesquisa-poder-institucional"
