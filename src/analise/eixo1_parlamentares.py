"""Contas julgadas irregulares (TCU) em parlamentares da base (D-064): taxa por partido, governo/oposição e faixa ideológica.

Universo: deputados federais e senadores titulares da base cuja candidatura, a partir de 2002, foi ligada por CPF (eixo1_atores_ligados.csv);
quem não tem ligação não entra no denominador nem no numerador, e a cobertura por partido acompanha as tabelas.
Unidades: parlamentar x legislatura (partido e faixa ideológica) e parlamentar x trecho de mandato presidencial e ano (governo/oposição),
como em D-063.

Medidas (fixadas antes do cálculo):
- `tcu_no_periodo`: há status `contas_julgadas_irregulares` com data (trânsito em julgado) dentro da unidade;
- `tcu_acumulado`: há status com data até o fim da unidade (a pessoa já tinha contas julgadas irregulares, em qualquer função anterior).
A lista pública do TCU cobre todo responsável por recursos públicos, não só o mandato: a medida inclui contas de outras funções (prefeito, gestor).

Testes e recortes como em D-063: homogeneidade entre partidos (30+ unidades) por simulação exata, Spearman com escore ideológico por
permutação e governo x oposição por período presidencial (Fisher).

Saídas em relatorios/tabelas: eixo1_parlamentares_taxas.csv, _homogeneidade.csv, _correlacao.csv, _governo_periodo.csv e _cobertura.csv.

Uso:
    python -m src.analise.eixo1_parlamentares
"""

import pandas as pd

from src.analise.eixo1 import homogeneidade
from src.analise.etica import MIN_N, governo_por_periodo, linha, unidades_trecho
from src.analise.ideologia import ORDEM, spearman_permutacao
from src.base import RAIZ, ler
from src.simetria.governo_oposicao import ler_tabela as ler_tabela_governo
from src.simetria.taxa_bancada import LEGISLATURAS, pares

SAIDA = RAIZ / "relatorios" / "tabelas"
MEDIDAS = ("tcu_no_periodo", "tcu_acumulado")


def datas_tcu() -> dict[str, list[str]]:
    st = ler("status_pessoa_processo")
    st = st[st["status"] == "contas_julgadas_irregulares"]
    saida: dict[str, list[str]] = {}
    for a, d in zip(st["id_ator"], st["data"]):
        saida.setdefault(a, []).append(d)
    return saida


def marcar(u: pd.DataFrame, datas: dict, ini: pd.Series, fim: pd.Series) -> pd.DataFrame:
    u = u.copy()
    u["tcu_no_periodo"] = [any(i <= d <= f for d in datas.get(a, ())) for a, i, f in zip(u["id_ator"], ini, fim)]
    u["tcu_acumulado"] = [any(d <= f for d in datas.get(a, ())) for a, f in zip(u["id_ator"], fim)]
    return u


def run() -> None:
    ligados = set(pd.read_csv(SAIDA / "eixo1_atores_ligados.csv", dtype=str)["id_ator"])
    datas, gov = datas_tcu(), ler_tabela_governo()
    sigla = dict(zip(ler("instituicoes")["id_instituicao"], ler("instituicoes")["sigla"]))
    esc = ler("posicao_ideologica")
    esc = esc[esc["escala"] == "brc_2018"]
    media, faixa = dict(zip(esc["id_partido"], esc["media"].astype(float))), dict(zip(esc["id_partido"], esc["faixa"]))
    todas = pares(ler("cargos"), ler("filiacoes"))
    todas["ligado"] = todas["id_ator"].isin(ligados)
    lig = todas[todas["ligado"]]
    ul = marcar(lig, datas, lig["legislatura"].map(lambda l: LEGISLATURAS[l][0]), lig["legislatura"].map(lambda l: LEGISLATURAS[l][1]))
    ul["faixa"] = ul["id_partido"].map(faixa).fillna("sem_escore")
    ut = unidades_trecho({}, gov)
    ut = ut[ut["id_ator"].isin(ligados)]
    ut = marcar(ut, datas, ut["inicio"], ut["fim"])

    cobertura = todas.groupby("id_partido")["ligado"].agg(["sum", "count"]).reset_index()
    cobertura["sigla"] = cobertura["id_partido"].map(sigla).fillna("sem partido na base")
    cobertura["cobertura"] = cobertura["sum"] / cobertura["count"]
    cobertura.rename(columns={"sum": "ligados", "count": "parlamentar_legislatura"}).to_csv(SAIDA / "eixo1_parlamentares_cobertura.csv", index=False, encoding="utf-8")

    linhas, homog, corr = [], [], []
    for medida in MEDIDAS:
        for recorte, sub_l, sub_t in (("2003-2026", ul, ut), ("2007-2026 (sem a 52ª legislatura)", ul[ul["legislatura"] >= 53], ut[ut["inicio"] >= "2007-02-01"])):
            g = sub_l.groupby("id_partido")[medida].agg(["sum", "count"]).reset_index()
            for r in g.itertuples():
                linhas.append(linha(medida, recorte, "partido", r.id_partido or "sem_partido", r.sum, r.count, sigla.get(r.id_partido, "sem partido na base")))
            for gr, x in sub_t.groupby("grupo"):
                linhas.append(linha(medida, recorte, "governo_oposicao", gr, x[medida].sum(), len(x)))
            for fx, x in sub_l.groupby("faixa"):
                linhas.append(linha(medida, recorte, "faixa_ideologica", fx, x[medida].sum(), len(x)))
            h = g[(g["count"] >= MIN_N) & (g["id_partido"] != "")]
            if len(h) >= 2 and h["sum"].sum() > 0:
                est, p = homogeneidade(h["sum"].to_numpy(), h["count"].to_numpy())
                homog.append({"medida": medida, "recorte": recorte, "partidos": len(h), "qui2": est, "p_valor": p})
            c = h[h["id_partido"].isin(media)]
            if len(c) >= 5 and c["sum"].sum() > 0:
                r_, p_ = spearman_permutacao(c["id_partido"].map(media).to_numpy(), (c["sum"] / c["count"]).to_numpy())
                corr.append({"medida": medida, "recorte": recorte, "partidos": len(c), "spearman": r_, "p_permutacao": p_})
    t = pd.DataFrame(linhas)
    t["ordem"] = t["grupo"].map({f: i for i, f in enumerate(ORDEM)}).fillna(99)
    t.sort_values(["medida", "recorte", "grupo_tipo", "ordem", "grupo"]).drop(columns="ordem").to_csv(SAIDA / "eixo1_parlamentares_taxas.csv", index=False, encoding="utf-8")
    pd.DataFrame(homog).to_csv(SAIDA / "eixo1_parlamentares_homogeneidade.csv", index=False, encoding="utf-8")
    pd.DataFrame(corr).to_csv(SAIDA / "eixo1_parlamentares_correlacao.csv", index=False, encoding="utf-8")
    gp = governo_por_periodo(ut, MEDIDAS)
    gp.to_csv(SAIDA / "eixo1_parlamentares_governo_periodo.csv", index=False, encoding="utf-8")
    print(f"unidades legislatura: {len(ul)} de {len(todas)}; trecho: {len(ut)}")
    print(pd.DataFrame(homog).round(4).to_string(index=False))
    print(pd.DataFrame(corr).round(3).to_string(index=False))
    print(gp.round(4).to_string(index=False))


if __name__ == "__main__":
    run()
