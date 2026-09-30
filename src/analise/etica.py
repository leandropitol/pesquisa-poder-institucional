"""Conselhos de Ética (D-063): taxa de parlamentares representados e de decisões adversas, por partido, governo/oposição e faixa ideológica.

Unidade: parlamentar x trecho (mandato presidencial x ano civil), como em D-050, para o grupo governo/oposição; parlamentar x legislatura
para partido e faixa (partido no início do mandato na legislatura, como em D-049).

Medidas (a partir de status_pessoa_processo dos processos de classe `representacao_etica`):
- `representado`: parlamentar que passou a representado (apresentação da representação) no período da unidade;
- `adverso`: mandato cassado ou sanção disciplinar aprovada no período da unidade (13 casos ao todo);
- `improcedente_ou_arquivado` não entra como numerador.
Denominador: quem exerceu mandato de deputado federal ou senador titular na unidade.

Testes: homogeneidade entre partidos com pelo menos 30 unidades (qui-quadrado, p exato por simulação) e Spearman entre escore ideológico e taxa
(p por permutação), como no eixo 1 (D-060, D-062).

Saídas: relatorios/tabelas/etica_taxas.csv, etica_homogeneidade.csv, etica_correlacao.csv e etica_governo_periodo.csv.

Uso:
    python -m src.analise.etica
"""

import pandas as pd
from scipy.stats import fisher_exact

from src.analise.eixo1 import homogeneidade
from src.analise.ideologia import ORDEM, spearman_permutacao
from src.base import RAIZ, ler
from src.simetria.governo_oposicao import grupo_na_data, ler_tabela as ler_tabela_governo
from src.simetria.taxa_bancada import LEGISLATURAS, pares, wilson

SAIDA = RAIZ / "relatorios" / "tabelas"
ADVERSOS = {"mandato_cassado", "sancao_disciplinar"}
MIN_N = 30


def eventos_por_ator() -> dict[str, dict[str, list[str]]]:
    proc = ler("processos")
    ids = set(proc.loc[proc["classe"] == "representacao_etica", "id_processo"])
    st = ler("status_pessoa_processo")
    st = st[st["id_processo"].isin(ids)]
    saida: dict[str, dict[str, list[str]]] = {}
    for r in st.itertuples():
        medida = "representado" if r.status == "representado" else "adverso" if r.status in ADVERSOS else None
        if medida:
            saida.setdefault(medida, {}).setdefault(r.id_ator, []).append(r.data)
    return saida


def partido_em(fil: pd.DataFrame, ator: str, data: str) -> str:
    f = fil[(fil["id_ator"] == ator) & (fil["data_inicio"] <= data)]
    vig = f[(f["data_fim"] == "") | (f["data_fim"] >= data)]
    f = vig if len(vig) else f
    return f["id_partido"].iloc[-1] if len(f) else ""


def unidades_legislatura(ev: dict) -> pd.DataFrame:
    p = pares(ler("cargos"), ler("filiacoes"))
    for medida, por_ator in ev.items():
        p[medida] = [any(LEGISLATURAS[l][0] <= d <= LEGISLATURAS[l][1] for d in por_ator.get(a, [])) for a, l in zip(p["id_ator"], p["legislatura"])]
    return p


def unidades_trecho(ev: dict, gov: pd.DataFrame) -> pd.DataFrame:
    cargos, fil = ler("cargos"), ler("filiacoes").sort_values("data_inicio")
    c = cargos[cargos["cargo"].str.startswith("Deputado") | cargos["cargo"].str.startswith("Senador (titular)")]
    segs = gov[["inicio", "fim"]].drop_duplicates().sort_values("inicio").values.tolist()
    linhas = []
    for r in c.itertuples():
        fim_c = r.data_fim or "9999-12-31"
        for ini, fim in segs:
            if r.data_inicio <= fim and fim_c >= ini:
                d = max(r.data_inicio, ini)
                p = partido_em(fil, r.id_ator, d)
                linha = {"id_ator": r.id_ator, "inicio": ini, "grupo": grupo_na_data(gov, p, d) if p else "sem_partido"}
                for medida, por_ator in ev.items():
                    linha[medida] = any(ini <= x <= fim for x in por_ator.get(r.id_ator, []))
                linhas.append(linha)
    return pd.DataFrame(linhas).drop_duplicates(["id_ator", "inicio"])


PERIODOS = [("Lula 1 e 2", "2003-01-01", "2010-12-31"), ("Dilma 1 e início do 2º mandato", "2011-01-01", "2016-05-11"), ("Temer (e Dilma até 11/05/2016)", "2016-05-12", "2018-12-31"),
            ("Bolsonaro", "2019-01-01", "2022-12-31"), ("Lula 3", "2023-01-01", "2026-12-31")]


def governo_por_periodo(ut: pd.DataFrame) -> pd.DataFrame:
    """Governo x oposição por período presidencial, com o teste exato de Fisher (bicaudal) em cada um. Períodos definidos pelo início do trecho."""
    linhas = []
    for nome, ini, fim in PERIODOS + [("Todo o período", "2003-01-01", "2026-12-31")]:
        x = ut[(ut["inicio"] >= ini) & (ut["inicio"] <= fim)]
        g, o = x[x["grupo"] == "governo"], x[x["grupo"] == "oposicao"]
        for medida in ("representado", "adverso"):
            kg, ko = int(g[medida].sum()), int(o[medida].sum())
            p = fisher_exact([[kg, len(g) - kg], [ko, len(o) - ko]])[1] if len(g) and len(o) and kg + ko else float("nan")
            linhas.append({"medida": medida, "periodo": nome, "n_governo": len(g), "registro_governo": kg, "taxa_governo": kg / len(g) if len(g) else float("nan"),
                           "n_oposicao": len(o), "registro_oposicao": ko, "taxa_oposicao": ko / len(o) if len(o) else float("nan"), "p_fisher": p})
    return pd.DataFrame(linhas)


def linha(medida, recorte, tipo, grupo, k, n, sigla="") -> dict:
    lo, hi = wilson(int(k), int(n))
    return {"medida": medida, "recorte": recorte, "grupo_tipo": tipo, "grupo": grupo, "sigla": sigla or grupo, "n_unidades": int(n), "com_registro": int(k),
            "taxa": k / n if n else float("nan"), "ic95_inf": lo, "ic95_sup": hi}


def run() -> None:
    ev = eventos_por_ator()
    gov = ler_tabela_governo()
    sigla = dict(zip(ler("instituicoes")["id_instituicao"], ler("instituicoes")["sigla"]))
    esc = ler("posicao_ideologica")
    esc = esc[esc["escala"] == "brc_2018"]
    media, faixa = dict(zip(esc["id_partido"], esc["media"].astype(float))), dict(zip(esc["id_partido"], esc["faixa"]))
    ul, ut = unidades_legislatura(ev), unidades_trecho(ev, gov)
    ul["faixa"] = ul["id_partido"].map(faixa).fillna("sem_escore")
    linhas, homog, corr = [], [], []
    for medida in ("representado", "adverso"):
        for recorte, sub_l, sub_t in (("2003-2026", ul, ut), ("2003-2019 (antes da restrição do foro)", ul[ul["legislatura"] <= 55], ut[ut["inicio"] < "2019-02-01"]),
                                      ("2007-2026 (sem a 52ª legislatura)", ul[ul["legislatura"] >= 53], ut[ut["inicio"] >= "2007-02-01"])):
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
    t = t.sort_values(["medida", "recorte", "grupo_tipo", "ordem", "grupo"]).drop(columns="ordem")
    t.to_csv(SAIDA / "etica_taxas.csv", index=False, encoding="utf-8")
    pd.DataFrame(homog).to_csv(SAIDA / "etica_homogeneidade.csv", index=False, encoding="utf-8")
    pd.DataFrame(corr).to_csv(SAIDA / "etica_correlacao.csv", index=False, encoding="utf-8")
    gp = governo_por_periodo(ut)
    gp.to_csv(SAIDA / "etica_governo_periodo.csv", index=False, encoding="utf-8")
    print(gp.round(4).to_string(index=False))
    print(pd.DataFrame(homog).round(4).to_string(index=False)); print(pd.DataFrame(corr).round(3).to_string(index=False))


if __name__ == "__main__":
    run()
