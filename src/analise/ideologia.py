"""Simetria por posição ideológica (D-062): taxas por faixa e correlação entre escore e taxa do partido.

Escore: posicao_ideologica, escala brc_2018 (Bolognesi, Ribeiro e Codato, 2023). Partido sem escore (fusão posterior a
2018 ou fora da tabela) fica em `sem_escore`.

Medidas já calculadas pelas regras próprias de cada uma:
- STF (D-048, D-049): réu e condenação em ação penal do eixo 1, por parlamentar x legislatura; recortes 52-57 e 52-55
  (antes da restrição do foro), de relatorios/tabelas/simetria_taxa_bancada.csv;
- TSE e TCU (D-060, D-061): por candidatura, de data/staging/eixo1/candidatos.csv, em todos os candidatos e só nos eleitos.

Correlação: Spearman entre escore e taxa, só partidos com pelo menos 30 no denominador; p bilateral por permutação dos
escores (20.000 repetições, semente fixa).

Saídas: relatorios/tabelas/ideologia_taxas_faixa.csv e ideologia_correlacao.csv.

Uso:
    python -m src.analise.ideologia
"""

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from src.base import RAIZ, ler
from src.simetria.taxa_bancada import wilson

SAIDA = RAIZ / "relatorios" / "tabelas"
ORDEM = ["extrema_esquerda", "esquerda", "centro_esquerda", "centro", "centro_direita", "direita", "extrema_direita", "sem_escore"]
MIN_N, PERMUTACOES, SEMENTE = 30, 20000, 20260929


def spearman_permutacao(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    rx, ry = rankdata(x), rankdata(y)
    r = float(np.corrcoef(rx, ry)[0, 1])
    rng = np.random.default_rng(SEMENTE)
    sim = np.array([np.corrcoef(rng.permutation(rx), ry)[0, 1] for _ in range(PERMUTACOES)])
    return r, float((1 + (np.abs(sim) >= abs(r) - 1e-12).sum()) / (1 + PERMUTACOES))


def por_partido() -> pd.DataFrame:
    """Uma linha por fonte x medida x recorte x partido, com k e n."""
    partes = []
    stf = pd.read_csv(SAIDA / "simetria_taxa_bancada.csv", dtype={"id_partido": str})
    stf = stf[stf["legislatura"].isin(["52-57", "52-55"])]
    for medida in ("reu", "condenacao"):
        partes.append(pd.DataFrame({"fonte": "STF", "medida": medida, "recorte": "legislaturas " + stf["legislatura"], "universo": "parlamentares",
                                    "id_partido": stf["id_partido"].fillna(""), "k": stf[f"n_{medida}"], "n": stf["bancada"]}))
    u = pd.read_csv(RAIZ / "data" / "staging" / "eixo1" / "candidatos.csv", dtype={"id_partido": str}, keep_default_na=False)
    for medida, anos in (("tse_indeferimento", [2018, 2022]), ("tcu_ate_eleicao", [2010, 2014, 2018, 2022]), ("tcu_qualquer_data", [2010, 2014, 2018, 2022])):
        for universo, x in (("candidatos", u), ("eleitos", u[u["eleito"].astype(str) == "True"])):
            x = x[x["ano"].isin(anos)]
            g = x.groupby("id_partido")[medida].agg(lambda s: int((s.astype(str) == "True").sum())).rename("k").to_frame().join(x.groupby("id_partido").size().rename("n")).reset_index()
            partes.append(g.assign(fonte="TSE" if medida.startswith("tse") else "TCU", medida=medida, recorte=f"{anos[0]}-{anos[-1]}", universo=universo))
    return pd.concat(partes, ignore_index=True)


def run() -> None:
    esc = ler("posicao_ideologica")
    esc = esc[esc["escala"] == "brc_2018"]
    media, faixa = dict(zip(esc["id_partido"], esc["media"].astype(float))), dict(zip(esc["id_partido"], esc["faixa"]))
    sigla = dict(zip(ler("instituicoes")["id_instituicao"], ler("instituicoes")["sigla"]))
    p = por_partido()
    p["faixa"] = p["id_partido"].map(faixa).fillna("sem_escore")
    chaves = ["fonte", "medida", "recorte", "universo"]
    f = p.groupby(chaves + ["faixa"])[["k", "n"]].sum().reset_index()
    f["taxa"] = f["k"] / f["n"]
    ic = [wilson(int(k), int(n)) for k, n in zip(f["k"], f["n"])]
    f["ic95_inf"], f["ic95_sup"] = [a for a, _ in ic], [b for _, b in ic]
    f["ordem"] = f["faixa"].map(ORDEM.index)
    f = f.sort_values(chaves + ["ordem"]).drop(columns="ordem")
    corr = []
    for chave, g in p[p["id_partido"].isin(media) & (p["n"] >= MIN_N)].groupby(chaves):
        if len(g) < 5 or g["k"].sum() == 0:
            continue
        r, pv = spearman_permutacao(g["id_partido"].map(media).to_numpy(), (g["k"] / g["n"]).to_numpy())
        corr.append(dict(zip(chaves, chave)) | {"partidos": len(g), "spearman": r, "p_permutacao": pv,
                                                "partidos_lista": ";".join(sorted(g["id_partido"].map(sigla)))})
    f.to_csv(SAIDA / "ideologia_taxas_faixa.csv", index=False, encoding="utf-8")
    pd.DataFrame(corr).to_csv(SAIDA / "ideologia_correlacao.csv", index=False, encoding="utf-8")
    print(pd.DataFrame(corr)[chaves + ["partidos", "spearman", "p_permutacao"]].round(3).to_string(index=False))


if __name__ == "__main__":
    run()
