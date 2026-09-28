"""Taxa por partido e legislatura: parlamentares réus em ação penal do eixo 1 no STF sobre o total da bancada (D-049).

A contagem bruta de ações por partido (verificações de simetria, D-048) cresce com o tamanho da bancada. Aqui a
unidade é o par parlamentar x legislatura:

- denominador: quem exerceu mandato na legislatura (deputado titular ou suplente com período de exercício na base;
  senador titular, contado em cada legislatura que o mandato cobre). Suplentes de senador ficam fora: a base só os
  lista, sem período de exercício. Partido = filiação na data de início do mandato naquela legislatura (a mais
  recente iniciada até essa data);
- numerador: os pares cujo parlamentar é réu (ligação aceita, aceita a conferir ou automática) em ação penal do
  STF com assunto do eixo 1 pela regra da E5, autuada dentro da legislatura (padrão de réu) ou com primeiro
  julgamento de mérito com condenação dentro da legislatura (padrão de condenação). O partido do par é o do
  denominador, então a taxa fica entre 0 e 1 mesmo quando o parlamentar troca de partido.

Saídas (geradas, nunca editadas à mão):
- relatorios/tabelas/simetria_taxa_bancada.csv: partido x legislatura, o período todo (legislatura "52-57") e o
  período anterior à restrição do foro por prerrogativa de função no STF (legislatura "52-55"; AP 937 QO, maio de
  2018): depois dela, poucas ações penais contra parlamentares ficam no STF, e a taxa das legislaturas 56 e 57 cai a
  quase zero para todos os partidos. Comparação entre partidos usa o agregado 52-55;
- a sensibilidade sem as ligações "a conferir" e com as ações de assunto "revisar" vai em colunas próprias.

Intervalo de confiança de 95% pelo método de Wilson (proporção binomial; pares não são independentes quando o
mesmo parlamentar aparece em várias legislaturas, então o intervalo é indicativo).

Uso:
    python -m src.simetria.taxa_bancada
"""

import math
import re

import pandas as pd

from src.base import RAIZ, ler
from src.normalizacao.simetria_stf import CONDENACAO, carregar
from src.simetria.governo_oposicao import SAIDA as TABELA_GOVERNO, grupo_na_data, ler_tabela as ler_tabela_governo

LEGISLATURAS = {52: ("2003-02-01", "2007-01-31"), 53: ("2007-02-01", "2011-01-31"), 54: ("2011-02-01", "2015-01-31"),
                55: ("2015-02-01", "2019-01-31"), 56: ("2019-02-01", "2023-01-31"), 57: ("2023-02-01", "2027-01-31")}
SAIDA = RAIZ / "relatorios" / "tabelas" / "simetria_taxa_bancada.csv"
SAIDA_GRUPOS = RAIZ / "relatorios" / "tabelas" / "simetria_taxa_governo_oposicao.csv"


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - m), min(1.0, c + m))


def legislatura(data: str) -> int | None:
    return next((l for l, (i, f) in LEGISLATURAS.items() if i <= data[:10] <= f), None)


def pares(cargos: pd.DataFrame, filiacoes: pd.DataFrame) -> pd.DataFrame:
    """Um registro por parlamentar x legislatura com mandato exercido, com o partido no início do mandato nela."""
    c = cargos[cargos["cargo"].str.startswith("Deputado") | cargos["cargo"].str.startswith("Senador (titular)")]
    linhas = []
    for _, r in c.iterrows():
        fim = r["data_fim"] or "9999-12-31"
        for l, (i, f) in LEGISLATURAS.items():
            if r["data_inicio"] <= f and fim >= i:
                linhas.append({"id_ator": r["id_ator"], "legislatura": l, "inicio": max(r["data_inicio"], i)})
    p = pd.DataFrame(linhas).sort_values("inicio").drop_duplicates(["id_ator", "legislatura"])
    fil = filiacoes.sort_values("data_inicio")

    def partido(ator: str, data: str) -> str:
        f = fil[(fil["id_ator"] == ator) & (fil["data_inicio"] <= data)]
        vig = f[(f["data_fim"] == "") | (f["data_fim"] >= data)]
        f = vig if len(vig) else f
        return f["id_partido"].iloc[-1] if len(f) else ""

    p["id_partido"] = [partido(a, d) for a, d in zip(p["id_ator"], p["inicio"])]
    return p


def marcas(lig: dict, lista: pd.DataFrame) -> pd.DataFrame:
    """Um registro por (parlamentar, ação), com o universo da ação, a legislatura de autuação e a da condenação."""
    linhas = []
    for (ap, _n), atores in lig.items():
        l = lista.loc[ap]
        cond = any(r in CONDENACAO for r in l["resultados"].split("; "))
        for a, dec in atores:
            linhas.append({"id_ator": a, "ap": ap, "universo": l["universo"], "a_conferir": dec == "aceita_a_conferir",
                           "leg_reu": legislatura(l["data_autuacao"]),
                           "leg_cond": legislatura(l["data_primeiro_julgamento"]) if cond and l["data_primeiro_julgamento"] else None})
    return pd.DataFrame(linhas)


def tabela(p: pd.DataFrame, m: pd.DataFrame, sigla: dict) -> pd.DataFrame:
    def conj(col: str, universos: tuple, sem_conferir: bool = False) -> set:
        x = m[m["universo"].isin(universos) & m[col].notna()]
        if sem_conferir:
            x = x[~x["a_conferir"]]
        return set(zip(x["id_ator"], x[col].astype(int)))

    reu, reu_sc, reu_rev = conj("leg_reu", ("sim",)), conj("leg_reu", ("sim",), True), conj("leg_reu", ("sim", "revisar"))
    cond, cond_rev = conj("leg_cond", ("sim",)), conj("leg_cond", ("sim", "revisar"))
    p = p.copy()
    chave = list(zip(p["id_ator"], p["legislatura"]))
    for nome, s in (("reu", reu), ("reu_sem_a_conferir", reu_sc), ("reu_com_revisar", reu_rev), ("condenacao", cond), ("condenacao_com_revisar", cond_rev)):
        p[nome] = [k in s for k in chave]
    todas = p.assign(legislatura="52-57")
    antes = p[p["legislatura"] <= 55].assign(legislatura="52-55")  # antes da restrição do foro (STF, AP 937 QO, maio de 2018)
    g = pd.concat([p.assign(legislatura=p["legislatura"].astype(str)), todas, antes]).groupby(["id_partido", "legislatura"])
    t = g.agg(bancada=("id_ator", "size"), **{f"n_{c}": (c, "sum") for c in ("reu", "reu_sem_a_conferir", "reu_com_revisar", "condenacao", "condenacao_com_revisar")}).reset_index()
    t.insert(1, "sigla", t["id_partido"].map(sigla).fillna("sem partido na base"))
    for c in ("reu", "condenacao"):
        t[f"taxa_{c}"] = (t[f"n_{c}"] / t["bancada"]).round(4)
        ic = [wilson(k, n) for k, n in zip(t[f"n_{c}"], t["bancada"])]
        t[f"ic95_{c}_inf"] = [round(a, 4) for a, _ in ic]
        t[f"ic95_{c}_sup"] = [round(b, 4) for _, b in ic]
    for c in ("reu_sem_a_conferir", "reu_com_revisar", "condenacao_com_revisar"):
        t[f"taxa_{c}"] = (t[f"n_{c}"] / t["bancada"]).round(4)
    return t.sort_values(["legislatura", "bancada"], ascending=[True, False])


def tabela_grupos(cargos: pd.DataFrame, filiacoes: pd.DataFrame, lig: dict, lista: pd.DataFrame, gov: pd.DataFrame) -> pd.DataFrame:
    """Taxa por grupo (governo, oposição, nenhum, sem classificação), D-050/D-051. Unidade: parlamentar x trecho (mandato
    presidencial x ano civil), porque o grupo de um partido muda de um trecho para outro. Denominador: quem exerceu mandato
    no trecho, com o grupo do seu partido no início do trecho; numerador: quem é réu em ação do eixo 1 autuada no trecho."""
    segs = gov[["inicio", "fim"]].drop_duplicates().sort_values("inicio").values.tolist()
    c = cargos[cargos["cargo"].str.startswith("Deputado") | cargos["cargo"].str.startswith("Senador (titular)")]
    fil = filiacoes.sort_values("data_inicio")
    reus = {}
    for (ap, _n), atores in lig.items():
        l = lista.loc[ap]
        if l["universo"] != "sim":
            continue
        for a, _d in atores:
            reus.setdefault(a, []).append(l["data_autuacao"])
    linhas = []
    for _, r in c.iterrows():
        fim_c = r["data_fim"] or "9999-12-31"
        for ini, fim in segs:
            if r["data_inicio"] <= fim and fim_c >= ini:
                d = max(r["data_inicio"], ini)
                f = fil[(fil["id_ator"] == r["id_ator"]) & (fil["data_inicio"] <= d)]
                vig = f[(f["data_fim"] == "") | (f["data_fim"] >= d)]
                f = vig if len(vig) else f
                p = f["id_partido"].iloc[-1] if len(f) else ""
                linhas.append({"id_ator": r["id_ator"], "inicio": ini, "fim": fim, "grupo": grupo_na_data(gov, p, d) if p else "sem_partido",
                               "reu": any(ini <= x <= fim for x in reus.get(r["id_ator"], []))})
    u = pd.DataFrame(linhas).drop_duplicates(["id_ator", "inicio"])
    saida = []
    for rotulo, sub in (("2003-2019 (antes da restrição do foro)", u[u["inicio"] < "2019-02-01"]), ("2003-2026", u)):
        for g, x in sub.groupby("grupo"):
            k, n = int(x["reu"].sum()), len(x)
            a, b = wilson(k, n)
            saida.append({"periodo": rotulo, "grupo": g, "parlamentar_ano": n, "n_reu": k, "taxa_reu": round(k / n, 4),
                          "ic95_inf": round(a, 4), "ic95_sup": round(b, 4)})
    return pd.DataFrame(saida)


def run() -> None:
    c = carregar()
    if not c["todos_lotes"]:
        raise SystemExit("faltam lotes da aba Partes (D-048): a taxa de réu exige todas as ações lidas")
    inst = ler("instituicoes")
    sigla = dict(zip(inst["id_instituicao"], inst["sigla"]))
    p = pares(c["cargos"], c["filiacoes"])
    m = marcas(c["lig"], c["lista"])
    fora = sorted(set(m["id_ator"]) - set(p["id_ator"]))  # ligados a quem não entra no denominador (suplente de senador)
    t = tabela(p, m, sigla)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(SAIDA, index=False, lineterminator="\n")
    tot = t[t["legislatura"] == "52-55"]
    print(f"pares parlamentar x legislatura: {len(p)}; sem partido na base: {(p['id_partido'] == '').sum()}; ligados fora do denominador: {fora}")
    print(tot[tot["bancada"] >= 30][["sigla", "bancada", "n_reu", "taxa_reu", "ic95_reu_inf", "ic95_reu_sup", "n_condenacao", "taxa_reu_sem_a_conferir",
                                    "taxa_reu_com_revisar"]].sort_values("taxa_reu", ascending=False).to_string(index=False))
    print(f"-> {SAIDA.relative_to(RAIZ)}")
    if TABELA_GOVERNO.exists():
        g = tabela_grupos(c["cargos"], c["filiacoes"], c["lig"], c["lista"], ler_tabela_governo())
        g.to_csv(SAIDA_GRUPOS, index=False, lineterminator="\n")
        print(g.to_string(index=False))
        print(f"-> {SAIDA_GRUPOS.relative_to(RAIZ)}")


if __name__ == "__main__":
    run()
