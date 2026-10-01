"""Parte VII, núcleo analítico: painel 2002–2026, janelas de inflexão, matriz sistêmica, quatro hipóteses e modelo provisório.

Regras fixadas antes do cálculo em D-074, D-075 e D-076. As explicações possíveis e as classes de evidência escritas neste
arquivo foram redigidas depois de ver os resultados e citam apenas o que o livro mede ou documenta.
"""
from __future__ import annotations

from itertools import combinations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch
from scipy import stats

from .comum import (C, F_CGU_EMENDAS, F_IPCA, F_POP, F_RTN, F_STF, F_TSE_CAND, F_TSE_CONTAS, F_CAMARA, TAB, br, fig, gravar_resultados,
                    ler, nogridx, nogridy, partido_na_data, resultados, salvar, tabela, fator_real, periodo_ano, periodo_eleicao)
from .nucleo_series import ANOS, DIMENSOES, JANELAS, PERIODOS, TROCAS_GOVERNO, painel

PRINCIPAL = {  # indicador de cada linha da matriz sistêmica (D-074)
    "Financiamento eleitoral": "Empresas no dinheiro dos eleitos (%)",
    "Recursos públicos": "Despesa total da União (R$ bi reais)",
    "Emendas parlamentares": "Emendas pagas (% da despesa total)",
    "Execução orçamentária": "Discricionárias do Executivo (% da despesa total)",
    "Partidos": "Número efetivo de partidos (Câmara)",
    "STF": "Ações penais com réu parlamentar em curso no STF",
    "Controle administrativo": "Contas irregulares no TCU, pessoas da base",
    "Política externa": "Votos a favor de resoluções de escrutínio (%)",
    "Comércio exterior": "Exportações para países Não Livres (%)",
    "Indicadores democráticos": "Democracia liberal do Brasil (V-Dem)",
}
ROT_JAN = {j: f"{j[0]}–{str(j[1])[2:]}" for j in JANELAS}
ROT_PER = {p: f"{p[0]}–{str(p[1])[2:]}" for p in PERIODOS}
SETA = {"alta": "↑", "queda": "↓", "estável": "→", "sem cobertura": "·", "primeiro período": "·"}


def _fmt(v, nome):
    if pd.isna(v):
        return "–"
    if "Gini" in nome or "V-Dem" in nome:
        return br(v, 2)
    if abs(v) >= 100:
        return br(v, 0)
    return br(v, 1)


# ---------------- janelas de inflexão (D-074, item 2) ----------------
def janelas(P: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for c in P.columns:
        s = P[c].dropna(); sd = s.std()
        prev = None
        for k, (a, b) in enumerate(JANELAS):
            dentro = s[(s.index >= a) & (s.index <= b)]; antes = s[s.index < a]
            if len(dentro) == 0 or len(antes) == 0 or not sd:
                rows.append(dict(serie=c, janela=ROT_JAN[(a, b)], dz=np.nan, delta=np.nan, relevante=False, sentido="sem observação",
                                 aceleracao=False, reversao=False, duracao="sem observação", nivel_antes=np.nan, nivel_depois=np.nan))
                prev = None; continue
            v0, v1 = float(antes.iloc[-1]), float(dentro.iloc[-1]); d = v1 - v0; dz = d / sd
            rel = abs(dz) >= 1
            acel = prev is not None and not np.isnan(prev) and np.sign(prev) == np.sign(dz) and abs(dz) >= 2 * abs(prev) and abs(prev) > 0
            rev = prev is not None and not np.isnan(prev) and np.sign(prev) != np.sign(dz) and abs(prev) > 0.5 and abs(dz) > 0.5
            if k + 1 < len(JANELAS):
                a2, b2 = JANELAS[k + 1]; prox = s[(s.index >= a2) & (s.index <= b2)]
                dur = "sem observação posterior" if len(prox) == 0 else ("persistente" if np.sign(d) * (prox.mean() - v0) >= 0.5 * abs(d) else "revertida")
            else:
                dur = "sem observação posterior"
            rows.append(dict(serie=c, janela=ROT_JAN[(a, b)], dz=dz, delta=d, relevante=rel, sentido="alta" if d > 0 else ("queda" if d < 0 else "nula"),
                             aceleracao=acel, reversao=rev, duracao=dur if rel else "", nivel_antes=v0, nivel_depois=v1))
            prev = dz
    return pd.DataFrame(rows)


def logrank(t1, e1, t2, e2) -> float:
    """Teste log-rank de duas amostras (aproximação qui-quadrado com 1 grau de liberdade)."""
    t = np.concatenate([t1, t2]); e = np.concatenate([e1, e2]); g = np.concatenate([np.zeros(len(t1)), np.ones(len(t2))])
    O = E_ = V = 0.0
    for u in np.unique(t[e == 1]):
        risco = t >= u; n = risco.sum(); n1 = (risco & (g == 0)).sum(); d = ((t == u) & (e == 1)).sum(); d1 = ((t == u) & (e == 1) & (g == 0)).sum()
        O += d1; E_ += d * n1 / n
        if n > 1:
            V += d * (n1 / n) * (1 - n1 / n) * (n - d) / (n - 1)
    return float(stats.chi2.sf((O - E_) ** 2 / V, 1)) if V > 0 else float("nan")


def fora_das_janelas(P: pd.DataFrame) -> dict:
    """Séries cuja maior variação anual (entre observações consecutivas) cai fora das janelas do autor."""
    cob = {y for a, b in JANELAS for y in range(a, b + 1)}
    out = {}
    for c in P.columns:
        s = P[c].dropna()
        if len(s) < 3:
            continue
        d = (s.diff() / s.std()).dropna()
        y = int(d.abs().idxmax())
        if y not in cob:
            out[c] = y
    return out


# ---------------- matriz sistêmica (D-074, item 3) ----------------
def matriz(P: pd.DataFrame, comercio: pd.Series) -> pd.DataFrame:
    rows = []
    for c in list(P.columns) + ["Exportações para países Não Livres (%)"]:
        if c in P:
            s = P[c]; sd = s.dropna().std()
            vals = {p: s[(s.index >= p[0]) & (s.index <= p[1])].mean() for p in PERIODOS}
        else:
            vals = {p: comercio[p] for p in PERIODOS}; sd = comercio.std()
        ant = None
        for p in PERIODOS:
            v = vals[p]
            if pd.isna(v):
                sent = "sem cobertura"
            elif ant is None or pd.isna(ant):
                sent = "primeiro período"
            else:
                sent = "alta" if v - ant > 0.5 * sd else ("queda" if v - ant < -0.5 * sd else "estável")
            rows.append(dict(serie=c, periodo=ROT_PER[p], valor=v, sentido=sent))
            ant = v
    return pd.DataFrame(rows)


# ---------------- H4: trocas de governo (D-075) ----------------
def teste_trocas(P: pd.DataFrame, eleitorais: set) -> pd.DataFrame:
    rows = []
    for c in P.columns:
        if c in eleitorais:
            continue
        s = P[c].dropna(); s = s[s.index <= 2025]
        sd = s.std()
        d = (s.diff() / sd); d = d[s.index.to_series().diff() == 1].dropna().abs()  # só anos consecutivos
        T = [y for y in TROCAS_GOVERNO if y in d.index]
        if len(T) < 2 or len(d) - len(T) < 3:
            continue
        obs = d[T].mean() - d.drop(T).mean()
        vals = d.values; idx = list(range(len(vals))); k = len(T)
        tot = 0; ge = 0
        for comb in combinations(idx, k):
            m = vals[list(comb)].mean() - np.delete(vals, list(comb)).mean()
            tot += 1; ge += m >= obs - 1e-12
        rows.append(dict(serie=c, anos_troca=len(T), anos=len(d), media_troca=d[T].mean(), media_outros=d.drop(T).mean(), diferenca=obs, p=ge / tot))
    return pd.DataFrame(rows)


# ---------------- H1: emendas e reeleição (D-075, D-076) ----------------
def h1_reeleicao(lin: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    import statsmodels.api as sm
    em = ler("emendas_parlamentares", low_memory=False)
    em = em[em.tipo_emenda.str.contains("Individual", na=False) & em.id_ator.notna()].copy()
    em["real"] = em.valor_pago * em.ano.map(lambda y: fator_real(periodo_ano(int(y))))
    go = pd.read_csv(TAB / "governo_oposicao_partidos.csv"); go["ini"] = pd.to_datetime(go.inicio); go["fim"] = pd.to_datetime(go.fim)
    out, res = [], {}
    for ano, anos_em in ((2018, (2017, 2018)), (2022, (2019, 2022))):
        L = lin[lin.ano == ano].copy()
        e = em[em.ano.between(*anos_em)].groupby("id_ator").real.sum() / 1e6
        L["emendas_mi"] = L.id_ator.map(e).fillna(0)
        d = pd.Timestamp(f"{ano}-07-01"); part = partido_na_data(d); grp = go[(go.ini <= d) & (go.fim >= d)].set_index("id_partido").grupo
        L["base"] = (L.id_ator.map(part).map(grp) == "governo").astype(int)
        L["quartil"] = pd.qcut(L.emendas_mi.rank(method="first"), 4, labels=["1º (menor)", "2º", "3º", "4º (maior)"])
        for q, g in L.groupby("quartil", observed=True):
            out.append(dict(eleicao=ano, quartil=str(q), deputados=len(g), emendas_mediana_mi=g.emendas_mi.median(), reeleitos_pct=100 * g.eleito.mean()))
        rho, p = stats.spearmanr(L.emendas_mi, L.eleito.astype(int))
        mw = stats.mannwhitneyu(L[L.eleito].emendas_mi, L[~L.eleito].emendas_mi)
        X = L.copy(); X["log_em"] = np.log1p(X.emendas_mi)
        m = sm.Logit(X.eleito.astype(int), sm.add_constant(X[["log_em", "base"]])).fit(disp=0)
        ci = m.conf_int().loc["log_em"]
        res[ano] = dict(n=len(L), rho=float(rho), p_spearman=float(p), p_mw=float(mw.pvalue), or_em=float(np.exp(m.params["log_em"])),
                        or_em_ic=(float(np.exp(ci[0])), float(np.exp(ci[1]))), p_em=float(m.pvalues["log_em"]), or_base=float(np.exp(m.params["base"])), p_base=float(m.pvalues["base"]),
                        mediana_eleitos=float(L[L.eleito].emendas_mi.median()), mediana_nao=float(L[~L.eleito].emendas_mi.median()))
    return pd.DataFrame(out), res


# ---------------- figuras ----------------
def fig_painel(P, M):
    ordem = [c for d in DIMENSOES for c in P.columns if M.loc[c, "dimensao"] == d]
    Z = ((P - P.mean()) / P.std())[ordem]
    f, a = plt.subplots(figsize=(6.6, 7.4))
    cm = plt.get_cmap("RdBu_r")
    a.imshow(np.ma.masked_invalid(Z.T.values), cmap=cm, vmin=-2.5, vmax=2.5, aspect="auto")
    a.set_facecolor("#ecebe7")
    a.set_yticks(range(len(ordem))); a.set_yticklabels(ordem, fontsize=5.9)
    a.set_xticks(range(len(ANOS))); a.set_xticklabels([str(y)[2:] for y in ANOS], fontsize=6.5); a.grid(False)
    for s_ in a.spines.values():
        s_.set_visible(False)
    prev = None
    for i, c in enumerate(ordem):
        d = M.loc[c, "dimensao"]
        if d != prev:
            if i:
                a.axhline(i - 0.5, color="white", lw=2.2)
            prev = d
    for y in TROCAS_GOVERNO:
        a.axvline(ANOS.index(y) - 0.5, color=C["ink"], lw=0.5, ls=(0, (2, 2)))
    a.set_xlabel("ano (20xx); cinza: sem observação; tracejado: troca de governo", fontsize=7)
    a.set_title("Painel anual (escore z de cada série)", fontsize=9.5)
    sm_ = plt.cm.ScalarMappable(cmap=cm, norm=plt.Normalize(-2.5, 2.5)); cb = f.colorbar(sm_, ax=a, fraction=0.025, pad=0.01)
    cb.set_label("desvios-padrão da própria série", fontsize=6.5); cb.ax.tick_params(labelsize=6)
    return f, ordem


def fig_janelas(J, ordem):
    piv = J.pivot(index="serie", columns="janela", values="dz").reindex(index=ordem, columns=list(ROT_JAN.values()))
    rel = J.pivot(index="serie", columns="janela", values="relevante").reindex(index=ordem, columns=list(ROT_JAN.values()))
    f, a = plt.subplots(figsize=(6.6, 7.4))
    cm = plt.get_cmap("PuOr_r")
    a.imshow(np.ma.masked_invalid(np.clip(piv.values.astype(float), -3, 3)), cmap=cm, vmin=-3, vmax=3, aspect="auto")
    a.set_facecolor("#ecebe7")
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.values[i, j]
            if not pd.isna(v) and bool(rel.values[i, j]):
                a.text(j, i, ("▲" if v > 0 else "▼") + br(abs(v), 1), ha="center", va="center", fontsize=5.6, color="white" if abs(v) > 2 else C["ink"], fontweight="bold")
            elif not pd.isna(v):
                a.text(j, i, br(v, 1), ha="center", va="center", fontsize=5, color=C["ink2"])
    a.set_yticks(range(len(ordem))); a.set_yticklabels(ordem, fontsize=5.9)
    a.set_xticks(range(piv.shape[1])); a.set_xticklabels(piv.columns, fontsize=7); a.xaxis.tick_top(); a.grid(False)
    for s_ in a.spines.values():
        s_.set_visible(False)
    a.set_title("Variação em cada janela (desvios-padrão da série)\n▲▼ mudança relevante; cinza: sem observação", fontsize=8.5, pad=22)
    return f


def fig_sincronia(J):
    cols = list(ROT_JAN.values()); rows = []
    for j in cols:
        g = J[J.janela == j]
        rows.append(dict(janela=j, alta=int((g.relevante & (g.sentido == "alta")).sum()), queda=int((g.relevante & (g.sentido == "queda")).sum()),
                         estavel=int((~g.relevante & g.dz.notna()).sum()), naoobs=int(g.dz.isna().sum())))
    D = pd.DataFrame(rows).set_index("janela")
    f, a = fig(3.3)
    left = np.zeros(len(D))
    for k, cor, lab in (("alta", C["orange"], "alta relevante"), ("queda", C["blue"], "queda relevante"), ("estavel", "#d7d6d1", "sem mudança relevante"), ("naoobs", "#f2f1ee", "sem observação")):
        a.barh(D.index, D[k], left=left, color=cor, label=lab, edgecolor="white", linewidth=1.2, height=0.62)
        for i, (l, v) in enumerate(zip(left, D[k])):
            if v >= 2:
                a.text(l + v / 2, i, str(v), ha="center", va="center", fontsize=7, color="white" if k in ("alta", "queda") else C["ink2"])
        left += D[k].values
    a.invert_yaxis(); a.set_xlabel("número de séries"); nogridy(a); a.legend(ncol=4, fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.2))
    a.set_title("Quantas séries mudaram em cada janela, e em que sentido")
    return f, D


def fig_matriz(MX, comercio_nome):
    linhas = list(PRINCIPAL.items())
    f, a = plt.subplots(figsize=(6.6, 4.6))
    cores = {"alta": "#f6c6ae", "queda": "#bcd5f3", "estável": "#e9e8e4", "sem cobertura": "#ffffff", "primeiro período": "#f4f3f0"}
    for i, (dim, ser) in enumerate(linhas):
        g = MX[MX.serie == ser].set_index("periodo")
        for j, p in enumerate(ROT_PER.values()):
            r = g.loc[p]
            a.add_patch(plt.Rectangle((j, i), 0.96, 0.9, color=cores[r.sentido], ec=C["grid"]))
            txt = "sem\ncobertura" if r.sentido == "sem cobertura" else f"{SETA[r.sentido]} {_fmt(r.valor, ser)}"
            a.text(j + 0.48, i + 0.45, txt, ha="center", va="center", fontsize=6.6 if r.sentido != "sem cobertura" else 5.6,
                   color=C["ink"] if r.sentido != "sem cobertura" else C["mute"], fontweight="bold" if r.sentido in ("alta", "queda") else "normal")
        a.text(-0.08, i + 0.32, dim, ha="right", va="center", fontsize=6.8, fontweight="bold")
        a.text(-0.08, i + 0.66, ser, ha="right", va="center", fontsize=5.1, color=C["ink2"])
    a.set_xlim(-3.3, 6); a.set_ylim(len(linhas), -0.6)
    for j, p in enumerate(ROT_PER.values()):
        a.text(j + 0.48, -0.25, p, ha="center", fontsize=7, fontweight="bold")
    a.axis("off")
    a.set_title("Matriz sistêmica: média de cada período e sentido em relação ao anterior", fontsize=9)
    a.text(-3.3, len(linhas) + 0.35, "↑ alta e ↓ queda: diferença maior que meio desvio-padrão da série; → estável; períodos = mandatos presidenciais (2015–18 contém dois)",
           fontsize=5.6, color=C["ink2"])
    return f


def fig_h1(rp, tq, res):
    f, (a1, a2) = plt.subplots(1, 2, figsize=(6.4, 2.9), gridspec_kw=dict(width_ratios=[1, 1.15]))
    a1.plot(rp.ano, rp.taxa_reeleicao, color=C["blue"], marker="o", lw=1.6)
    for x, y in zip(rp.ano, rp.taxa_reeleicao):
        a1.text(x, y + 1.2, br(y, 1), ha="center", fontsize=7)
    a1.set_ylim(50, 85); a1.set_xticks(rp.ano); a1.set_ylabel("% reeleitos entre os que concorreram"); a1.set_title("Reeleição para a Câmara", fontsize=8.5); nogridx(a1)
    w = 0.38; qs = ["1º (menor)", "2º", "3º", "4º (maior)"]
    for k, (ano, cor) in enumerate(((2018, C["gray"]), (2022, C["blue"]))):
        g = tq[tq.eleicao == ano].set_index("quartil").reindex(qs)
        xs = np.arange(4) + (k - 0.5) * w
        a2.bar(xs, g.reeleitos_pct, width=w, color=cor, label=f"{ano} (emendas {'2017–18' if ano == 2018 else '2019–22'})", edgecolor="white")
        for x, v in zip(xs, g.reeleitos_pct):
            a2.text(x, v + 1, br(v, 0), ha="center", fontsize=6.5)
    a2.set_xticks(range(4)); a2.set_xticklabels(["1º\n(menor)", "2º", "3º", "4º\n(maior)"], fontsize=7); a2.set_ylim(0, 95)
    a2.set_xlabel("quartil de emendas individuais pagas ao deputado", fontsize=7); a2.legend(fontsize=6.3, loc="upper left"); nogridx(a2)
    a2.set_title("Reeleição por quartil de emendas", fontsize=8.5)
    return f


def fig_h2(E, PB):
    f, ax = plt.subplots(2, 3, figsize=(6.6, 4.4)); ax = ax.ravel()
    yrs = E.index
    ax[0].bar(yrs, E.pago_real_bi, color=C["blue"]); ax[0].set_title("Escala (R$ bi de ago/2026)", fontsize=7.5)
    mods = [("pct_Individual (finalidade definida)", "Ind. finalidade", C["blue"]), ("pct_Individual (transferência especial)", "Ind. transf. especial", C["aqua"]),
            ("pct_Bancada", "Bancada", C["orange"]), ("pct_Comissão", "Comissão", C["violet"]), ("pct_Relator", "Relator", C["red"])]
    bot = np.zeros(len(yrs))
    for k, lab, cor in mods:
        v = E[k].fillna(0).values; ax[1].bar(yrs, v, bottom=bot, color=cor, label=lab, width=0.8, edgecolor="white", linewidth=0.4); bot += v
    ax[1].set_title("Modalidades (% do pago)", fontsize=7.5); ax[1].legend(fontsize=4.6, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2)
    ax[2].plot(yrs, 100 - E.pct_autor_parlamentar, color=C["red"], marker="o", ms=2.5, label="sem autor parlamentar")
    ax[2].plot(yrs, E.pct_sem_uf, color=C["ink2"], marker="s", ms=2.5, ls="--", label="sem UF de destino")
    ax[2].set_title("Rastreabilidade (% do pago)", fontsize=7.5); ax[2].legend(fontsize=5.2)
    ax[3].plot(yrs, E.execucao, color=C["aqua"], marker="o", ms=2.5); ax[3].set_title("Execução (pago/empenhado, %)", fontsize=7.5); ax[3].set_ylim(0, 100)
    ax[4].plot(yrs, E.gini_pc_uf, color=C["violet"], marker="o", ms=2.5); ax[4].set_title("Gini per capita entre UF", fontsize=7.5); ax[4].set_ylim(0, 0.7)
    ax[5].plot(PB.index, PB.razao_base_fora, color=C["orange"], marker="o", ms=2.5); ax[5].axhline(1, color=C["gray"], lw=0.8)
    ax[5].set_title("Individuais: base / fora", fontsize=7.5); ax[5].set_ylim(0.6, 1.4)
    for a in ax:
        a.tick_params(labelsize=6); a.set_xticks([2017, 2019, 2021, 2023, 2025]); nogridx(a)
    return f


def fig_h3(ES):
    f, (a1, a2) = plt.subplots(1, 2, figsize=(6.4, 2.8))
    s = ES[ES.index <= 2025]
    a1.bar(s.index, s.estoque, color=C["blue"], width=0.75); a1.axvline(2018.33, color=C["orange"], lw=1)
    a1.text(2018.6, s.estoque.max() * 0.92, "AP 937 QO\n(03/05/2018)", fontsize=6.3, color=C["orange"])
    a1.set_title("Ações com réu parlamentar em curso (31/12)", fontsize=8); nogridx(a1); a1.tick_params(labelsize=6.5)
    t = s[s.estoque >= 5]
    a2.plot(t.index, t.pct_origem_stf, color=C["violet"], marker="o", ms=3, label="% autuadas no próprio STF")
    a2b = a2.twinx() if False else None
    a2.plot(t.index, 10 * t.idade_mediana, color=C["aqua"], marker="s", ms=3, ls="--", label="idade mediana (anos x 10)")
    a2.axvline(2018.33, color=C["orange"], lw=1); a2.set_ylim(0, 105); a2.legend(fontsize=6.2, loc="upper left")
    a2.set_title("Composição (anos com 5+ ações)", fontsize=8); nogridx(a2); a2.tick_params(labelsize=6.5)
    return f


def fig_h4(T, externas):
    T = T.copy(); T["grupo"] = np.where(T.serie.isin(externas), "externa", "doméstica")
    T = T.sort_values(["grupo", "diferenca"])
    f, a = plt.subplots(figsize=(6.4, 4.4))
    ys = np.arange(len(T))
    for y, r in zip(ys, T.itertuples()):
        cor = C["orange"] if r.grupo == "externa" else C["blue"]
        a.plot([r.media_outros, r.media_troca], [y, y], color=C["gray"], lw=1)
        a.scatter([r.media_outros], [y], color="white", edgecolor=cor, s=22, zorder=3)
        a.scatter([r.media_troca], [y], color=cor, s=22, zorder=3)
        a.text(max(r.media_outros, r.media_troca) + 0.06, y, f"p = {br(r.p, 2)}", va="center", fontsize=5.8, color=C["ink2"])
    a.set_yticks(ys); a.set_yticklabels([("[ext] " if g == "externa" else "") + s for s, g in zip(T.serie, T.grupo)], fontsize=5.8)
    a.set_xlabel("variação anual média (desvios-padrão); vazio: demais anos; cheio: trocas", fontsize=6.5)
    a.set_title("A variação é maior nos anos de troca de governo?", fontsize=9); nogridy(a)
    return f


REDE_NOS = {"Normas (Congresso e STF)": (0.0, 0.0), "Dinheiro eleitoral": (-2.3, 1.35), "Competição política": (0.0, 2.55), "Partidos": (2.3, 1.35),
            "Orçamento": (2.3, -1.25), "Distribuição de recursos": (0.3, -2.55), "Controle administrativo": (-2.1, -1.75), "Justiça (STF)": (-3.2, -0.05),
            "Política externa": (3.9, 2.55)}
# posição dos rótulos de cada relação (coordenadas do diagrama)
REDE_ROT = {("Normas (Congresso e STF)", "Dinheiro eleitoral"): (-0.75, 0.98), ("Normas (Congresso e STF)", "Orçamento"): (0.75, -0.95),
            ("Normas (Congresso e STF)", "Partidos"): (0.75, 0.98), ("Normas (Congresso e STF)", "Justiça (STF)"): (-1.75, -0.3),
            ("Dinheiro eleitoral", "Competição política"): (-1.55, 2.15), ("Orçamento", "Competição política"): (3.55, 0.2),
            ("Competição política", "Partidos"): (1.55, 2.15), ("Partidos", "Orçamento"): (1.65, 0.05),
            ("Orçamento", "Distribuição de recursos"): (1.75, -2.15), ("Controle administrativo", "Distribuição de recursos"): (-0.75, -1.85),
            ("Justiça (STF)", "Controle administrativo"): (-3.15, -1.05), ("Partidos", "Política externa"): (3.6, 1.75)}


def fig_modelo(REL):
    f, a = plt.subplots(figsize=(6.6, 5.4))
    estilo = {"Evidência direta": dict(ls="-", lw=2.0, color=C["ink"]), "Evidência associativa": dict(ls="--", lw=1.4, color=C["blue"]),
              "Hipótese": dict(ls=":", lw=1.4, color=C["orange"]), "Não determinável": dict(ls=(0, (1, 2.5)), lw=0.9, color=C["mute"])}
    for r in REL.itertuples():
        p0, p1 = REDE_NOS[r.origem], REDE_NOS[r.destino]
        st = estilo[r.evidencia]
        arr = FancyArrowPatch(p0, p1, arrowstyle="-|>" if r.sentido == "→" else "<|-|>", mutation_scale=10, shrinkA=30, shrinkB=30,
                              connectionstyle=f"arc3,rad={r.curva}", linestyle=st["ls"], lw=st["lw"], color=st["color"], zorder=3)
        a.add_patch(arr)
        lx, ly = REDE_ROT[(r.origem, r.destino)]
        a.text(lx, ly, r.rotulo, fontsize=5.6, color=st["color"] if r.evidencia != "Não determinável" else C["ink2"], ha="center", va="center", zorder=2, style="italic" if r.evidencia == "Não determinável" else "normal")
    for n, (x, y) in REDE_NOS.items():
        cor = "#fbe3d6" if n.startswith("Normas") else "#eaf1fb"
        a.text(x, y, n.replace(" (", "\n("), ha="center", va="center", fontsize=7, fontweight="bold", zorder=5,
               bbox=dict(boxstyle="round,pad=0.45", fc=cor, ec=C["navy"], lw=0.8))
    for i, (k, st) in enumerate(estilo.items()):
        y = -2.05 - 0.22 * i
        a.plot([2.75, 3.15], [y, y], ls=st["ls"], lw=st["lw"], color=st["color"])
        a.text(3.22, y, k, fontsize=6.3, va="center")
    a.set_xlim(-4.0, 4.7); a.set_ylim(-3.0, 3.0); a.axis("off")
    a.set_title("Modelo provisório: relações entre mecanismos, pela classe de evidência", fontsize=9)
    return f

CURTA = [("Tribunal Superior Eleitoral", "TSE"), ("Tesouro Nacional", "Tesouro (RTN)"), ("IBGE", "IBGE"), ("Controladoria-Geral", "CGU"),
         ("Câmara dos Deputados", "Câmara e Senado"), ("Supremo Tribunal", "STF"), ("Tribunal de Contas", "TCU"), ("Nações Unidas", "ONU e OEA"),
         ("Relações Exteriores", "Itamaraty"), ("BNDES", "BNDES"), ("V-Dem", "V-Dem"), ("Freedom House", "Freedom House")]

# Explicações possíveis por janela: redigidas depois de ver os resultados; cada uma traz a classe de evidência (D-075).
EXPLICA = {
    "2003–05": ("Aumento do número de atos bilaterais assinados por ano; o motivo não é medido no livro.", "Não determinável", "Só cinco séries têm observação; a janela começa no primeiro ano do painel."),
    "2008–10": ("Eleição de 2010: mais dinheiro por eleito e maior peso dos repasses de partidos; base do governo ampla no último ano do mandato; pico de atos bilaterais; primeira onda de ações penais que envelhecem no STF.",
                "Evidência associativa (mudanças do mesmo período, sem ligação medida entre elas)", "Repasses de partidos misturam fundo partidário e doações de empresas; o livro não separa a origem."),
    "2013–15": ("Início da legislatura de 2015: declínios de competência quando mandatos terminam (padrão de todos os inícios de legislatura); mais partidos na Câmara; queda das operações de exportação do BNDES.",
                "Evidência associativa para os declínios (calendário de mandatos, capítulo 18); hipótese para o BNDES", "O motivo da interrupção do crédito do BNDES não está nos dados do livro."),
    "2016–18": ("Mudança das regras de financiamento (revogação da norma sobre doações de empresas pela Lei 13.165/2015 e decisão do STF de 2015 [REFERÊNCIA A CONFIRMAR]; criação do fundo eleitoral pela Lei 13.487/2017) e restrição do foro no STF [REFERÊNCIA A CONFIRMAR]; queda dos indicadores externos de democracia; menor taxa de reeleição. Para a alta das contas irregulares no TCU, da base do governo e das operações do BNDES, o livro não examina explicação.",
                "Evidência direta para as regras de financiamento (leis verificadas); associativa para o foro, até a confirmação do acórdão, e para as séries que seguem as regras; não determinável para os indicadores de democracia e para a reeleição",
                "Passa no critério no limite (exatamente metade das séries observadas), com várias séries eleitorais entre as que mudam; várias normas no mesmo intervalo impedem atribuir cada mudança a uma delas."),
    "2019–20": ("Emendas de execução obrigatória ampliadas (bancada e transferência especial) e emendas de relator; salto da despesa total em 2020, depois revertido; menos declínios porque restam poucas ações com parlamentar no STF.",
                "Evidência direta para as modalidades criadas por emenda constitucional; hipótese para a despesa de 2020 (gastos extraordinários não separados no livro)", "Arquivo de emendas consistente só desde 2017; 2020 é ano atípico para a despesa."),
    "2021–22": ("Janela partidária de 2022; fundo eleitoral maior; execução das emendas mais alta; receitas dos eleitos menos concentradas; despesa total de volta ao nível anterior a 2020. Para as representações nos Conselhos de Ética, os votos na ONU e as operações do BNDES, o livro não examina explicação.",
                "Evidência direta para a janela partidária (Lei 13.165/2015) e para o valor do fundo (RTN); associativa para as demais", "Mudanças de partido contam só trocas individuais (D-072)."),
    "2023–26": ("Reconcentração partidária na Câmara no período em que passam a valer a cláusula de desempenho e as fusões; fim das emendas de relator, após decisão do STF de dez/2022 [REFERÊNCIA A CONFIRMAR], e crescimento das de comissão; mais sanções registradas pela CGU; recuperação do índice V-Dem.",
                "Evidência direta para a regra da cláusula (EC 97/2017); associativa para a reconcentração e para as demais séries", "Período em curso: 2025 e 2026 parciais ou ausentes em várias séries."),
}


def tabela_inflexoes(J: pd.DataFrame, M: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for j in ROT_JAN.values():
        g = J[(J.janela == j) & J.relevante]
        obs = int(J[(J.janela == j)].dz.notna().sum())
        al = [r.serie for r in g.itertuples() if r.sentido == "alta"]; qu = [r.serie for r in g.itertuples() if r.sentido == "queda"]
        mud = []
        if al:
            mud.append("Alta: " + "; ".join(al))
        if qu:
            mud.append("Queda: " + "; ".join(qu))
        fontes = sorted({c for s_ in g.serie for k, c in CURTA if k in M.loc[s_, "fonte"]})
        dims = sorted({M.loc[s_, "dimensao"] for s_ in g.serie}, key=DIMENSOES.index)
        mag = f"{len(g)} de {obs} séries observadas mudam ≥ 1 desvio-padrão; maior |variação| = {br(g.dz.abs().max(), 1)}" if len(g) else f"nenhuma das {obs} séries"
        dur = g.duracao.value_counts()
        durs = "; ".join(f"{k}: {v}" for k, v in dur.items()) if len(g) else "—"
        ex, ev, lim = EXPLICA[j]
        rows.append({"Período": j, "Mudança observada": " | ".join(mud) if mud else "Nenhuma mudança relevante", "Indicadores envolvidos": ", ".join(dims),
                     "Fontes": ", ".join(fontes), "Magnitude": mag, "Duração": durs, "Possíveis explicações": ex, "Evidência": ev, "Limitações": lim})
    return pd.DataFrame(rows)


def main() -> None:
    R0 = resultados(); R = {}
    P, M, X = painel()
    E, PB, rp, rl, ES, V, CM = X["emendas"], X["partidos_emendas"], X["reeleicao"], X["reeleicao_linhas"], X["estoque"], X["votos"], X["comercio"]
    eleitorais = {c for c in P.columns if P[c].dropna().index.isin([2002, 2006, 2010, 2014, 2018, 2022]).all()}
    externas = [c for c in P.columns if M.loc[c, "dimensao"] == "Política externa"]
    R["n7_series"] = len(P.columns); R["n7_dimensoes_painel"] = int(M.dimensao.nunique()); R["n7_dimensoes"] = int(M.dimensao.nunique()) + 1  # comércio exterior só por mandato

    # ---- painel
    f, ordem = fig_painel(P, M)
    salvar(f, "n30", titulo=f"Painel anual de {len(P.columns)} séries em {M.dimensao.nunique()} dimensões, padronizadas pela média e pelo desvio-padrão de cada série, 2002–2026",
           pergunta="As dimensões se movem nos mesmos anos?", periodo="2002–2026", unidade="desvios-padrão em relação à média da própria série (escore z)",
           universo="Séries anuais das partes II a VI e séries derivadas das mesmas bases (D-074)", fonte_primaria="As de cada série (tabela do painel)",
           tratamento="Padronização de cada série pelos anos observados; anos sem observação em cinza; linhas tracejadas nas trocas de governo",
           derivado="Escore z por série e ano", limitacoes="Séries de inícios diferentes e eleitorais a cada quatro anos; cor indica posição na própria série, não magnitude comparável",
           leitura="As cores mudam de lado em anos diferentes conforme a dimensão; não há um único ano de virada comum a todas.", codigo="Parte VII")
    t = P.round(3).T.reset_index().rename(columns={"index": "Série"})
    t.insert(1, "Dimensão", t["Série"].map(M.dimensao)); t.insert(2, "Unidade", t["Série"].map(M.unidade))
    t.columns = [str(c) for c in t.columns]
    fmt = lambda df: df.apply(lambda col: [("" if pd.isna(v) else _fmt(v, n)) for v, n in zip(col, t["Série"])] if col.name not in ("Série",) else col)
    for nome, anos_, rot in (("t_painel2", [y for y in ANOS if y <= 2014], "2002–2014"), ("t_painel2b", [y for y in ANOS if y >= 2015], "2015–2026")):
        tt = fmt(t[["Série"] + [str(y) for y in anos_]])
        tabela(tt, nome, titulo=f"Painel anual ampliado, {rot}", unidade="a de cada série (ver tabela de fontes do capítulo 35)", periodo=rot, universo="Séries anuais do núcleo analítico (D-074)",
               fonte="Ver a tabela de fontes das séries", notas="Vazio = sem observação. Séries eleitorais só em anos de eleição; emendas desde 2017; sanções desde 2015; discricionárias desde 2008; Freedom House 2012–2024; 2026 parcial ou excluído conforme a série.", codigo="Parte VII")
    import re
    curta = lambda f_: ", ".join(dict.fromkeys(c for k, c in sorted(CURTA, key=lambda kc: (kc[1] == "IBGE", f_.find(kc[0]))) if k in f_)) + "".join("; " + d for d in sorted(set(re.findall(r"D-0\d\d", f_))))
    tf = M.assign(fonte=M.fonte.map(curta)).reset_index().rename(columns={"index": "Série", "dimensao": "Dimensão", "unidade": "Unidade", "fonte": "Fonte primária", "nota": "Nota"})
    tf.insert(3, "Cobertura", [f"{int(P[s].dropna().index.min())}–{int(P[s].dropna().index.max())}" for s in tf["Série"]])
    tabela(tf, "t_painel2_fontes", titulo="Séries do painel ampliado: dimensão, unidade, cobertura e fonte", unidade="—", periodo="2002–2026",
           universo="Séries do núcleo analítico", fonte="Conforme cada linha; descrição completa de cada fonte (arquivo, código FNT e data de acesso) nas fichas e nas referências do Atlas", notas="Valores reais deflacionados pelo IPCA do IBGE (D-070); IPCA de junho de 2002 a 2013 acrescentado em 01/10/2026 (D-077).", codigo="Parte VII")
    R["n7_cobertura_min"] = int(min(P[c].dropna().index.min() for c in P)); R["n7_series_completas"] = int(sum(P[c].dropna().index.min() <= 2003 for c in P))

    # ---- janelas
    J = janelas(P)
    f = fig_janelas(J, ordem)
    salvar(f, "n31", titulo="Variação de cada série nas janelas de inflexão propostas pelo autor, em desvios-padrão da série",
           pergunta="Em quais janelas cada série mudou de modo relevante?", periodo="2003–2026 (sete janelas)", unidade="desvios-padrão da série",
           universo="Séries do painel ampliado", fonte_primaria="As de cada série", tratamento="Regra de D-074: última observação na janela menos a última antes dela, dividida pelo desvio-padrão da série; relevante se o valor absoluto é pelo menos 1",
           derivado="Variação padronizada por série e janela", limitacoes="Os anos 2006–07 e 2011–12 não pertencem a nenhuma janela; série eleitoral só muda em janela que contém eleição; o limiar é uma convenção",
           leitura="As mudanças relevantes se acumulam em 2016–18 e 2019–20, mas há mudanças relevantes em todas as janelas com observação.", codigo="Parte VII")
    f, SY = fig_sincronia(J)
    salvar(f, "n32", titulo="Número de séries com mudança relevante de alta ou de queda em cada janela de inflexão",
           pergunta="As mudanças acontecem juntas? Em que sentido?", periodo="2003–2026", unidade="número de séries",
           universo="Séries do painel ampliado", fonte_primaria="As de cada série", tratamento="Contagem pela regra de D-074", derivado="Contagem por janela e sentido",
           limitacoes="Alta e queda são numéricas; o significado depende da série (queda de empresas e alta de fundos públicos descrevem o mesmo movimento); séries de uma mesma dimensão não são independentes",
           leitura="; ".join(f"{j}: {int(r.alta + r.queda)} de {int(r.alta + r.queda + r.estavel)} séries observadas" for j, r in SY.iterrows()) + ".", codigo="Parte VII")
    SY["observadas"] = SY.alta + SY.queda + SY.estavel; SY["pct"] = 100 * (SY.alta + SY.queda) / SY.observadas
    SY["ambiente_comum"] = SY.pct >= 50
    R["n7_janelas"] = {j: dict(rel=int(r.alta + r.queda), obs=int(r.observadas), pct=round(float(r.pct), 0), alta=int(r.alta), queda=int(r.queda), comum=bool(r.ambiente_comum)) for j, r in SY.iterrows()}
    R["n7_janelas_comuns"] = [j for j, r in SY.iterrows() if r.ambiente_comum]
    R["n7_janela_max"] = SY.pct.idxmax(); R["n7_janela_max_pct"] = round(float(SY.pct.max()), 0)
    fj = fora_das_janelas(P); R["n7_fora_janelas"] = fj; R["n7_fora_janelas_n"] = len(fj)
    acc = J[J.aceleracao & J.relevante]; rev = J[J.reversao & J.relevante]
    R["n7_aceleracoes"] = [f"{r.serie} ({r.janela})" for r in acc.itertuples()]; R["n7_reversoes"] = [f"{r.serie} ({r.janela})" for r in rev.itertuples()]
    rel1618 = J[(J.janela == "2016–18") & J.relevante]
    R["n7_1618_eleitorais"] = int(rel1618.serie.isin(eleitorais).sum())
    jt = J[J.relevante].copy()
    jt = jt.assign(**{"Variação (dp)": jt.dz.round(2), "Antes": [_fmt(v, s) for v, s in zip(jt.nivel_antes, jt.serie)], "Depois": [_fmt(v, s) for v, s in zip(jt.nivel_depois, jt.serie)],
                      "Aceleração": np.where(jt.aceleracao, "sim", ""), "Reversão": np.where(jt.reversao, "sim", "")})
    tabela(jt[["janela", "serie", "sentido", "Antes", "Depois", "Variação (dp)", "Aceleração", "Reversão", "duracao"]].rename(
        columns={"janela": "Janela", "serie": "Série", "sentido": "Sentido", "duracao": "Duração"}), "t_janelas_relevantes",
        titulo="Mudanças relevantes por janela de inflexão", unidade="unidade de cada série; variação em desvios-padrão", periodo="2003–2026",
        universo="Pares série-janela com mudança relevante (D-074)", fonte="As de cada série", notas="Antes = última observação antes da janela; depois = última dentro dela. Duração pela média da janela seguinte.", codigo="Parte VII")

    TI = tabela_inflexoes(J, M)
    tabela(TI, "t_inflexoes", titulo="Pontos de inflexão: o que mudou em cada janela proposta", unidade="séries e desvios-padrão", periodo="2003–2026",
           universo="Séries do painel ampliado; janelas propostas pelo autor como hipótese de trabalho", fonte="As de cada série (tabela de fontes do painel)",
           notas="Mudança observada e magnitude calculadas pela regra de D-074; possíveis explicações e evidência redigidas pelo autor depois do cálculo, pela escala de D-075. Anos 2006–07 e 2011–12 fora das janelas.", codigo="Parte VII")

    # ---- matriz
    MX = matriz(P, CM)
    f = fig_matriz(MX, "Exportações para países Não Livres (%)")
    salvar(f, "n33", titulo="Matriz sistêmica: dez dimensões em seis períodos, com a média do período e o sentido em relação ao período anterior",
           pergunta="Em que períodos cada dimensão mudou de direção?", periodo="2003–2026", unidade="a de cada indicador",
           universo="Um indicador por dimensão (D-074); comércio exterior por mandato", fonte_primaria="As de cada série (tabela do painel); comércio: " + "ComexStat e Freedom House",
           tratamento="Média das observações do período; alta ou queda se a diferença para o período anterior passa de meio desvio-padrão da série",
           derivado="Valor médio e sentido por período", limitacoes="Um indicador resume cada dimensão; períodos coincidem com mandatos, então tempo e governo não se separam; 2023–26 parcial",
           leitura="As dimensões mudam em períodos diferentes: a parcela de empresas cai em 2007–10 e em 2015–18; o conjunto de ações no STF sobe até 2011–14 e cai em 2015–18 e 2019–22; as emendas sobem em 2019–22 e 2023–26; o número de partidos sobe de 2011 a 2022 e cai em 2023–26.", codigo="Parte VII")
    mt = MX.copy(); mt["célula"] = [("sem cobertura" if s_ == "sem cobertura" else f"{SETA[s_]} {_fmt(v, n)}".strip()) for v, s_, n in zip(mt.valor, mt.sentido, mt.serie)]
    full = mt.pivot(index="serie", columns="periodo", values="célula")[list(ROT_PER.values())]
    dimof = {**M.dimensao.to_dict(), "Exportações para países Não Livres (%)": "Comércio exterior"}
    full.insert(0, "Dimensão", full.index.map(dimof)); full = full.reset_index().rename(columns={"serie": "Série"})
    full["_o"] = full["Dimensão"].map({d: i for i, d in enumerate(DIMENSOES)}); full = full.sort_values(["_o", "Série"]).drop(columns="_o")
    tabela(full, "t_matriz_completa", titulo="Matriz sistêmica completa: todas as séries por período", unidade="média do período na unidade de cada série; seta = sentido",
           periodo="2003–2026", universo="Séries do painel ampliado e comércio por mandato", fonte="As de cada série",
           notas="↑ alta, ↓ queda (diferença maior que meio desvio-padrão), → estável; primeiro período observado sem seta.", codigo="Parte VII")
    mp = full[full["Série"].isin(PRINCIPAL.values())].copy()
    mp["_o"] = mp["Série"].map({v: i for i, v in enumerate(PRINCIPAL.values())}); mp = mp.sort_values("_o").drop(columns="_o")
    tabela(mp, "t_matriz", titulo="Matriz sistêmica: indicador de cada dimensão por período", unidade="média do período; seta = sentido em relação ao período anterior",
           periodo="2003–2026", universo="Um indicador por dimensão (D-074)", fonte="As de cada série; comércio: ComexStat e Freedom House por mandato",
           notas="Os períodos são mandatos presidenciais; 2015–18 contém dois governos e o comércio desse período é a média ponderada pelas exportações.", codigo="Parte VII")
    cnt = MX[MX.serie.isin(PRINCIPAL.values())].groupby("periodo").sentido.value_counts().unstack(fill_value=0)
    R["n7_matriz_mudancas"] = {p: int(cnt.loc[p].get("alta", 0) + cnt.loc[p].get("queda", 0)) for p in cnt.index}
    R["n7_matriz_sem_cobertura"] = int((MX[MX.serie.isin(PRINCIPAL.values())].sentido == "sem cobertura").sum())
    allc = MX.groupby("periodo").sentido.value_counts().unstack(fill_value=0)
    R["n7_matriz_completa_mudancas"] = {p: int(allc.loc[p].get("alta", 0) + allc.loc[p].get("queda", 0)) for p in allc.index}
    R["n7_matriz_completa_obs"] = {p: int(allc.loc[p].drop(["sem cobertura", "primeiro período"], errors="ignore").sum()) for p in allc.index}

    # ---- H4 trocas de governo (todas as séries anuais, para comparar)
    T = teste_trocas(P, eleitorais)
    f = fig_h4(T, externas)
    salvar(f, "n37", titulo="Variação anual média nos anos de troca de governo e nos demais anos, por série, com teste de permutação exato",
           pergunta="As séries externas e domésticas mudam mais quando muda o governo?", periodo="2003–2025", unidade="desvios-padrão da série (variação anual absoluta)",
           universo="Séries anuais do painel (as eleitorais ficam fora: eleição e posse caem em anos diferentes)", fonte_primaria="As de cada série",
           tratamento="Regra de D-075: média da variação absoluta padronizada em 2003, 2011, 2016, 2019 e 2023 (quando observados) contra os demais anos; p = parcela das combinações de anos com diferença igual ou maior",
           derivado="Diferença e p por série", limitacoes="Poucos anos de troca (2 a 5 por série); vários testes sem correção para comparações múltiplas; troca de governo coincide com outros eventos do mesmo ano",
           leitura="Poucas séries têm variação maior nos anos de troca com p < 0,05.", codigo="Parte VII")
    T["grupo"] = np.where(T.serie.isin(externas), "externa", "doméstica")
    R["h4_n"] = len(T); R["h4_sig"] = [f"{r.serie}" for r in T[T.p < 0.05].itertuples()]; R["h4_sig_n"] = int((T.p < 0.05).sum())
    R["h4_ext_sig"] = [r.serie for r in T[(T.p < 0.05) & (T.grupo == "externa")].itertuples()]
    R["h4_dom_sig"] = [r.serie for r in T[(T.p < 0.05) & (T.grupo == "doméstica")].itertuples()]
    R["h4_ext_n"] = int((T.grupo == "externa").sum()); R["h4_dom_n"] = int((T.grupo == "doméstica").sum())
    tabela(T.assign(media_troca=T.media_troca.round(2), media_outros=T.media_outros.round(2), diferenca=T.diferenca.round(2), p=T.p.round(3)).rename(columns={
        "serie": "Série", "grupo": "Grupo", "anos_troca": "Anos de troca", "anos": "Anos com variação observada", "media_troca": "Média nas trocas (dp)",
        "media_outros": "Média nos demais (dp)", "diferenca": "Diferença", "p": "p (permutação)"})[["Série", "Grupo", "Anos de troca", "Anos com variação observada", "Média nas trocas (dp)", "Média nos demais (dp)", "Diferença", "p (permutação)"]],
        "t_h4_trocas", titulo="Variação nos anos de troca de governo e nos demais anos, por série", unidade="desvios-padrão; p de permutação exata",
        periodo="2003–2025", universo="Séries anuais do painel", fonte="As de cada série", notas=f"{len(T)} testes, sem correção para comparações múltiplas; ao acaso, cerca de 1 em 20 teria p < 0,05.", codigo="H4")
    vg = R0["p6_sim_fh"]; R["h4_votos_gov"] = vg
    R["h4_comercio"] = {ROT_PER[p]: round(float(v), 1) for p, v in CM.items()}
    R["h4_china"] = R0["p6_china"]; R["h4_bqd_sem_china"] = R0["p6_bqd_sem_china"]

    # ---- H1
    tq, res = h1_reeleicao(rl)
    f = fig_h1(rp, tq, res)
    salvar(f, "n34", titulo="Taxa de reeleição dos deputados que concorreram de novo à Câmara, 2006–2022, e reeleição por quartil de emendas individuais pagas, 2018 e 2022",
           pergunta="Depois da mudança do financiamento, a reeleição aumentou? Quem recebeu mais emendas se reelegeu mais?", periodo="Eleições 2006–2022; emendas 2017–2022",
           unidade="% dos deputados que concorreram", universo=f"Deputados titulares em 1º de julho do ano da eleição ligados à candidatura a deputado federal (D-076): {', '.join(f'{a}: {n}' for a, n in zip(rp.ano, rp.ligados_a_candidatura))}",
           fonte_primaria=F_TSE_CAND + "; " + F_CAMARA + "; " + F_CGU_EMENDAS, tratamento="Ligação por nome único no país; quartis de emendas individuais pagas ao deputado (2017–18 para 2018; 2019–22 para 2022), em reais de ago/2026",
           derivado="Taxa de reeleição por eleição e por quartil", limitacoes="Só os deputados ligados à candidatura (cerca de dois terços); quem disputou outro cargo fica fora; emendas de 2018 cobrem só dois anos; o valor pago depende do tempo de mandato e da execução, não só do deputado",
           leitura=f"Reeleição: {', '.join(f'{a}: {br(v,1)}%' for a, v in zip(rp.ano, rp.taxa_reeleicao))}. Em 2022, do menor ao maior quartil de emendas: " +
                   ", ".join(f"{br(v,0)}%" for v in tq[tq.eleicao == 2022].reeleitos_pct) + ".", codigo="H1")
    R["h1_reeleicao"] = {int(a): float(v) for a, v in zip(rp.ano, rp.taxa_reeleicao)}
    R["h1_ligados"] = {int(a): int(n) for a, n in zip(rp.ano, rp.ligados_a_candidatura)}; R["h1_em_exercicio"] = {int(a): int(n) for a, n in zip(rp.ano, rp.deputados_em_exercicio)}
    R["h1_lig_pct"] = {a: round(100 * R["h1_ligados"][a] / R["h1_em_exercicio"][a], 0) for a in R["h1_ligados"]}
    R["h1_quartis"] = {int(a): [round(float(v), 1) for v in g.reeleitos_pct] for a, g in tq.groupby("eleicao")}
    R["h1_modelo"] = {int(k): {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in res.items()}
    tabela(tq.assign(emendas_mediana_mi=tq.emendas_mediana_mi.round(2), reeleitos_pct=tq.reeleitos_pct.round(1)).rename(columns={
        "eleicao": "Eleição", "quartil": "Quartil de emendas", "deputados": "Deputados", "emendas_mediana_mi": "Emendas pagas, mediana (R$ mi de ago/2026)", "reeleitos_pct": "Reeleitos (%)"}),
        "t_h1_quartis", titulo="Reeleição dos deputados por quartil de emendas individuais pagas", unidade="deputados, R$ milhões de ago/2026 e %", periodo="2018 e 2022",
        universo="Deputados em exercício ligados à candidatura a deputado federal (D-076)", fonte=F_TSE_CAND + "; " + F_CGU_EMENDAS + "; " + F_IPCA,
        notas="Emendas de 2017–2018 para a eleição de 2018 e de 2019–2022 para a de 2022.", codigo="H1")
    rows = []
    for a, v in res.items():
        rows.append({"Eleição": a, "Deputados": v["n"], "Spearman (emendas x reeleito)": round(v["rho"], 3), "p": round(v["p_spearman"], 4),
                     "Razão de chances por log(1+emendas)": round(v["or_em"], 2), "IC 95%": f"{br(v['or_em_ic'][0],2)} a {br(v['or_em_ic'][1],2)}", "p (emendas)": round(v["p_em"], 4),
                     "Razão de chances, base do governo": round(v["or_base"], 2),
                     "p (base)": round(v["p_base"], 4)})
    tabela(pd.DataFrame(rows), "t_h1_modelo", titulo="Associação entre emendas individuais pagas e reeleição, com controle de pertencer à base do governo",
           unidade="coeficientes e p", periodo="2018 e 2022", universo="Deputados ligados à candidatura (D-076)",
           fonte=F_TSE_CAND + "; " + F_CGU_EMENDAS + "; " + F_CAMARA,
           notas="Regressão logística (eleito = 1) com log(1+emendas em R$ mi de ago/2026) e base do governo em 1º de julho (D-078); sem controle de tempo de exercício nem de receita (indisponíveis). Associação, não efeito causal.", codigo="H1")
    # demais componentes de H1
    R["h1_pj"] = R0["p2_mix_pessoa_juridica"]; R["h1_fundo"] = R0["p2_mix_fundo_publico"]; R["h1_partido"] = R0["p2_mix_partido"]; R["h1_proprios"] = R0["p2_mix_recursos_proprios"]
    R["h1_gini"] = R0["p2_gini"]; R["h1_total_real"] = R0["p2_total_real_bi"]
    em_leg = float(E.loc[2019:2022, "pago_real_bi"].sum()); camp22 = float(R0["p2_total_real_bi"]["2022"])
    R["h1_emendas_leg56_bi"] = round(em_leg, 1); R["h1_campanha_2022_bi"] = camp22; R["h1_razao_emendas_campanha"] = round(em_leg / camp22, 0)
    ind = E[["pct_Individual (finalidade definida)", "pct_Individual (transferência especial)"]].fillna(0).sum(axis=1)
    R["h1_ind_pct_2019_2022"] = round(float((E.loc[2019:2022, "pago_real_bi"] * ind.loc[2019:2022] / 100).sum()), 1)
    m22 = res[2022]
    pj_cai = R0["p2_mix_pessoa_juridica"]["2022"] < R0["p2_mix_pessoa_juridica"]["2014"]; fp_sobe = R0["p2_mix_fundo_publico"]["2022"] > R0["p2_mix_fundo_publico"]["2014"]
    comp_ok = (m22["p_em"] < 0.05 and m22["or_em"] > 1); reel_ok = R["h1_reeleicao"][2022] > R["h1_reeleicao"][2014] and R["h1_reeleicao"][2018] > R["h1_reeleicao"][2014]
    R["h1_condicao_a"] = bool(pj_cai and fp_sobe); R["h1_teste_emendas"] = bool(comp_ok); R["h1_teste_reeleicao"] = bool(reel_ok)
    R["h1_veredito"] = ("não sustentada" if not (pj_cai and fp_sobe) else ("sustentada como associação" if (comp_ok and reel_ok) else "parcialmente sustentada"))
    h1 = pd.DataFrame([
        dict(Componente="Financiamento empresarial", Observação=f"{br(R0['p2_mix_pessoa_juridica']['2002'],1)}% do dinheiro dos eleitos em 2002, {br(R0['p2_mix_pessoa_juridica']['2014'],1)}% em 2014, zero em 2018 e 2022",
             Teste="Condição necessária (a)", Resultado="atendida", Evidência="Evidência direta (Lei 13.165/2015, art. 15, revoga o art. 81 da Lei 9.504/1997; decisão do STF de 2015 [REFERÊNCIA A CONFIRMAR: ADI 4650]; dado do TSE)"),
        dict(Componente="Fundo eleitoral", Observação=f"{br(R0['p2_mix_fundo_publico']['2018'],1)}% em 2018 e {br(R0['p2_mix_fundo_publico']['2022'],1)}% em 2022; inexistente antes de 2018",
             Teste="Condição necessária (a)", Resultado="atendida", Evidência="Evidência direta (Lei 13.487/2017; RTN)"),
        dict(Componente="Fundo partidário e transferências de partidos", Observação=f"Transferências de partidos: {br(R0['p2_mix_partido']['2010'],1)}% em 2010 e {br(R0['p2_mix_partido']['2014'],1)}% em 2014, quando misturavam fundo partidário e doações de empresas; {br(R0['p2_mix_partido']['2022'],1)}% em 2022",
             Teste="Origem pública antes de 2018", Resultado="não determinável", Evidência="Não determinável (a prestação de contas do candidato não separa a origem do dinheiro repassado pelo partido)"),
        dict(Componente="Recursos próprios", Observação=f"{br(R0['p2_mix_recursos_proprios']['2002'],1)}% em 2002, {br(R0['p2_mix_recursos_proprios']['2018'],1)}% em 2018, {br(R0['p2_mix_recursos_proprios']['2022'],1)}% em 2022",
             Teste="Descritivo", Resultado="queda em 2022", Evidência="Evidência direta para a regra (Lei 13.878/2019, limite de 10% do teto de gastos); associativa para a série"),
        dict(Componente="Concentração", Observação=f"Gini das receitas dos eleitos {br(R0['p2_gini']['2014'],3)} em 2014, {br(R0['p2_gini']['2022'],3)} em 2022",
             Teste="Descritivo", Resultado="desconcentração", Evidência="Evidência associativa (coincide com a troca de fonte; a regra de distribuição do fundo pelos partidos não foi medida)"),
        dict(Componente="Total real", Observação=f"R$ {br(R0['p2_total_real_bi']['2014'],2)} bi em 2014 e R$ {br(R0['p2_total_real_bi']['2022'],2)} bi em 2022, em reais de ago/2026",
             Teste="Descritivo", Resultado="queda", Evidência="Fato observado"),
        dict(Componente="Emendas", Observação=f"R$ {br(em_leg,1)} bi pagos em 2019–2022, cerca de {br(em_leg / camp22,0)} vezes o dinheiro de campanha de todos os eleitos de 2022",
             Teste="Escala", Resultado="emendas muito maiores que o financiamento de campanha", Evidência="Fato observado; a comparação de escala não mede uso na competição"),
        dict(Componente="Emendas e reeleição", Observação=f"2022: razão de chances {br(m22['or_em'],2)} (IC 95% {br(m22['or_em_ic'][0],2)} a {br(m22['or_em_ic'][1],2)}), p = {br(m22['p_em'],3)}",
             Teste="Associação (D-075)", Resultado="associação positiva" if comp_ok else "bivariada com sinais opostos em 2018 e 2022; sem significância com controle da base", Evidência="Evidência associativa" if comp_ok else "Não determinável com estes dados"),
        dict(Componente="Taxa de reeleição", Observação=", ".join(f"{a}: {br(v,1)}%" for a, v in R["h1_reeleicao"].items()),
             Teste="Alta em 2018 e 2022 frente a 2014 (critério do código, D-079)", Resultado="sem alta" if not reel_ok else "alta", Evidência="Fato observado"),
        dict(Componente="Distribuição partidária", Observação="Emendas individuais por autor: média da base sobre a de fora entre " + br(PB.razao_base_fora.min(), 2) + " e " + br(PB.razao_base_fora.max(), 2) + " (2017–2026)",
             Teste="Descritivo", Resultado="diferença pequena e estável", Evidência="Fato observado; emendas de relator e de comissão não têm autor individual"),
    ])
    tabela(h1, "t_h1", titulo="Hipótese 1: fontes privadas perdem espaço e mecanismos públicos ganham importância na competição política", unidade="—", periodo="2002–2026",
           universo="Deputados federais eleitos; deputados que concorreram à reeleição; emendas pagas", fonte=F_TSE_CONTAS + "; " + F_TSE_CAND + "; " + F_CGU_EMENDAS + "; " + F_RTN,
           notas=f"Veredito pela regra de D-075: {R['h1_veredito']}.", codigo="H1")

    # ---- H2
    f = fig_h2(E, PB)
    salvar(f, "n35", titulo="Emendas parlamentares, 2017–2026: escala, modalidades, rastreabilidade, execução, território e partido do autor",
           pergunta="Além de crescer, as emendas mudaram de natureza?", periodo="2017–2026 (2026 parcial)", unidade="ver cada painel",
           universo="Arquivo de emendas da CGU (D-029); população 2021, 2024 e 2025; autores com filiação na data", fonte_primaria=F_CGU_EMENDAS + "; " + F_POP + "; " + F_IPCA,
           tratamento="Somas anuais; percentuais do valor pago; Gini do valor pago por habitante entre UF; média de emendas individuais pagas por autor na base do governo e fora dela",
           derivado="Indicadores anuais", limitacoes="Pagamento inclui restos a pagar; sem UF e sem autor variam com a modalidade; base do governo pela concordância em votações (capítulo 24)",
           leitura="A escala muda em 2020 e em 2024; a composição muda três vezes (relator em 2020–2022, transferência especial desde 2020, comissão desde 2024); a execução sobe; a diferença entre base e fora da base é pequena.", codigo="H2")
    h2r = []
    def per(s, a, b):
        return float(s.loc[a:b].mean())
    for nome, s, und, ev in [
        ("Escala (R$ bi reais)", E.pago_real_bi, "R$ bi", "Fato observado"),
        ("Relator (% do pago)", E["pct_Relator"].fillna(0), "%", "Fato observado; decisão do STF de dez/2022 sobre emendas de relator [REFERÊNCIA A CONFIRMAR]"),
        ("Comissão (% do pago)", E["pct_Comissão"].fillna(0), "%", "Fato observado"),
        ("Transferência especial (% do pago)", E["pct_Individual (transferência especial)"].fillna(0), "%", "Evidência direta (EC 105/2019 cria a modalidade)"),
        ("Sem autor parlamentar (% do pago)", 100 - E.pct_autor_parlamentar, "%", "Fato observado"),
        ("Sem UF de destino (% do pago)", E.pct_sem_uf, "%", "Fato observado"),
        ("Execução (pago/empenhado, %)", E.execucao, "%", "Evidência direta para individuais e bancada (EC 86/2015 e EC 100/2019 tornam a execução obrigatória)"),
        ("Saúde (% do pago)", E.pct_saude, "%", "Fato observado"),
        ("Gini per capita entre UF", E.gini_pc_uf, "índice", "Fato observado"),
        ("Individuais: base / fora da base", PB.razao_base_fora, "razão", "Fato observado"),
    ]:
        sd = s.loc[2017:2025].std(); a_, b_, c_ = per(s, 2017, 2019), per(s, 2020, 2022), per(s, 2023, 2025)
        sent = lambda x, y: "alta" if y - x > 0.5 * sd else ("queda" if y - x < -0.5 * sd else "estável")
        h2r.append({"Dimensão": nome, "Unidade": und, "2017–19": round(a_, 2), "2020–22": round(b_, 2), "2023–25": round(c_, 2),
                    "Sentido 2020–22": sent(a_, b_), "Sentido 2023–25": sent(b_, c_), "Evidência": ev})
    H2 = pd.DataFrame(h2r)
    tabela(H2, "t_h2", titulo="Hipótese 2: dimensões das emendas em três triênios", unidade="médias dos triênios", periodo="2017–2025",
           universo="Arquivo de emendas da CGU", fonte=F_CGU_EMENDAS + "; " + F_POP + "; " + F_IPCA + "; legislação em planalto.gov.br",
           notas="Sentido pela regra de meio desvio-padrão (D-074) aplicada aos triênios; 2026 excluído por ser parcial.", codigo="H2")
    mud = H2[(H2["Sentido 2020–22"] != "estável") | (H2["Sentido 2023–25"] != "estável")]
    R["h2_dim_mudaram"] = [d for d in mud["Dimensão"] if not d.startswith("Escala")]; R["h2_dim_mudaram_n"] = len(R["h2_dim_mudaram"])
    R["h2_dim_estaveis"] = [d for d in H2["Dimensão"] if d not in list(mud["Dimensão"])]
    R["h2_veredito"] = "crescimento com mudança de natureza" if R["h2_dim_mudaram_n"] >= 2 else "crescimento sem mudança de natureza documentada"
    R["h2_te_max"] = round(float(E["pct_Individual (transferência especial)"].max()), 1); R["h2_te_max_ano"] = int(E["pct_Individual (transferência especial)"].idxmax())
    R["h2_comissao_2024"] = round(float(E.loc[2024, "pct_Comissão"]), 1); R["h2_relator_2020"] = round(float(E.loc[2020, "pct_Relator"]), 1)
    R["h2_exec_2017"] = round(float(E.loc[2017, "execucao"]), 1); R["h2_exec_2024"] = round(float(E.loc[2024, "execucao"]), 1)
    R["h2_semautor_2019"] = round(float(100 - E.loc[2019, "pct_autor_parlamentar"]), 1); R["h2_semautor_2022"] = round(float(100 - E.loc[2022, "pct_autor_parlamentar"]), 1); R["h2_semautor_2023"] = round(float(100 - E.loc[2023, "pct_autor_parlamentar"]), 1); R["h2_semautor_2025"] = round(float(100 - E.loc[2025, "pct_autor_parlamentar"]), 1)
    R["h2_semuf_2019"] = round(float(E.loc[2019, "pct_sem_uf"]), 1); R["h2_semuf_2022"] = round(float(E.loc[2022, "pct_sem_uf"]), 1); R["h2_semuf_2023"] = round(float(E.loc[2023, "pct_sem_uf"]), 1)
    R["h2_gini_2019"] = round(float(E.loc[2019, "gini_pc_uf"]), 2); R["h2_gini_2025"] = round(float(E.loc[2025, "gini_pc_uf"]), 2)
    R["h2_razao_min"] = round(float(PB.razao_base_fora.min()), 2); R["h2_razao_max"] = round(float(PB.razao_base_fora.max()), 2)
    R["h2_saude_min"] = round(float(E.pct_saude.min()), 1); R["h2_saude_max"] = round(float(E.pct_saude.max()), 1)

    # ---- H3
    f = fig_h3(ES)
    salvar(f, "n36", titulo="Ações penais com réu parlamentar em curso no STF ao fim de cada ano, e sua composição por origem e idade",
           pergunta="A mudança do foro alterou o tamanho, a composição e a idade do conjunto de ações que permanecem na Corte?", periodo="2003–2025",
           unidade="ações; % e anos", universo="Ações penais originárias com réu parlamentar (D-068), 365 ações", fonte_primaria=F_STF,
           tratamento="Ação em curso em 31/12: autuada até a data e com desfecho depois dela; composição só em anos com 5 ou mais ações",
           derivado="Estoque, parcela autuada no próprio STF e idade mediana", limitacoes="Universo da lista de D-048 e D-068: ações sem nenhuma decisão até a exportação não entram, o que pode reduzir os anos recentes; poucas ações depois de 2019",
           leitura=f"{int(ES.loc[2012,'estoque'])} ações em curso no fim de 2012, {int(ES.loc[2017,'estoque'])} em 2017 e {int(ES.loc[2018,'estoque'])} em 2018; a parcela autuada no próprio STF passa de {br(ES.loc[2017,'pct_origem_stf'],0)}% em 2017 para {br(ES.loc[2019,'pct_origem_stf'],0)}% em 2019.", codigo="H3")
    a = pd.read_csv(TAB / "foro_acoes.csv"); a = a[a.grupo == "com réu parlamentar"]
    a["ate2"] = a.anos <= 2; tab = pd.crosstab(a.coorte, a.ate2)
    fis = stats.fisher_exact(tab.values)
    tt = pd.read_csv(TAB / "foro_tempos.csv"); tc = tt[tt.recorte == "coorte"].set_index("coorte")
    R["h3_estoque"] = {int(k): int(v) for k, v in ES.estoque.items() if k <= 2025}
    R["h3_estoque_max"] = int(ES.estoque.max()); R["h3_estoque_max_ano"] = int(ES.estoque.idxmax())
    R["h3_pct_stf_2017"] = round(float(ES.loc[2017, "pct_origem_stf"]), 0); R["h3_pct_stf_2019"] = round(float(ES.loc[2019, "pct_origem_stf"]), 0)
    R["h3_idade_2017"] = round(float(ES.loc[2017, "idade_mediana"]), 1); R["h3_idade_2020"] = round(float(ES.loc[2020, "idade_mediana"]), 1)
    R["h3_med_pre"] = round(float(tc.loc["até 2018-05-02", "mediana_anos"]), 2); R["h3_med_pos"] = round(float(tc.loc["a partir de 2018-05-03", "mediana_anos"]), 2)
    R["h3_n_pre"] = int(tc.loc["até 2018-05-02", "acoes"]); R["h3_n_pos"] = int(tc.loc["a partir de 2018-05-03", "acoes"])
    R["h3_pct2_pre"] = round(float(100 * a[a.coorte == "até 2018-05-02"].ate2.mean()), 1); R["h3_pct2_pos"] = round(float(100 * a[a.coorte == "a partir de 2018-05-03"].ate2.mean()), 1)
    R["h3_fisher_p"] = round(float(fis.pvalue), 3)
    pre = a[a.coorte == "até 2018-05-02"]; pos = a[a.coorte == "a partir de 2018-05-03"]
    plr = logrank(pre.anos.values, pre.evento.values, pos.anos.values, pos.evento.values)
    R["h3_logrank_p"] = plr; R["h3_logrank_txt"] = "< 0,001" if plr < 0.001 else "= " + br(plr, 3)
    R["h3_autuadas_2011_2017"] = int(ES.loc[2011:2017, "autuadas"].sum()); R["h3_autuadas_2019_2025"] = int(ES.loc[2019:2025, "autuadas"].sum())
    H3 = pd.DataFrame([
        dict(Aspecto="Tamanho do conjunto em curso", Observação=f"Máximo de {R['h3_estoque_max']} ações em {R['h3_estoque_max_ano']}; {int(ES.loc[2017,'estoque'])} em 2017, {int(ES.loc[2018,'estoque'])} em 2018, {int(ES.loc[2020,'estoque'])} em 2020",
             Resultado="queda forte a partir de 2018", Evidência="Evidência associativa (coincide com a questão de ordem na AP 937 [REFERÊNCIA A CONFIRMAR]; os declínios de cada ação estão no capítulo 18)"),
        dict(Aspecto="Entrada de ações novas", Observação=f"{R['h3_autuadas_2011_2017']} autuadas em 2011–2017 e {R['h3_autuadas_2019_2025']} em 2019–2025",
             Resultado="queda", Evidência="Evidência associativa"),
        dict(Aspecto="Composição por origem", Observação=f"Autuadas no próprio STF: {br(R['h3_pct_stf_2017'],0)}% das ações em curso em 2017 e {br(R['h3_pct_stf_2019'],0)}% em 2019",
             Resultado="o conjunto que permanece passa a ser majoritariamente originário do STF", Evidência="Fato observado"),
        dict(Aspecto="Idade do conjunto", Observação=f"Idade mediana {br(R['h3_idade_2017'],1)} anos em 2017 e {br(R['h3_idade_2020'],1)} anos em 2020",
             Resultado="envelhece (ficam as ações antigas e entram poucas)", Evidência="Fato observado"),
        dict(Aspecto="Duração por coorte de autuação", Observação=f"Mediana {br(R['h3_med_pre'],2)} anos (até 02/05/2018, {R['h3_n_pre']} ações) e {br(R['h3_med_pos'],2)} anos (desde 03/05/2018, {R['h3_n_pos']} ações); log-rank p {R['h3_logrank_txt']}; encerradas em até 2 anos: {br(R['h3_pct2_pre'],1)}% e {br(R['h3_pct2_pos'],1)}% (Fisher p = {br(R['h3_fisher_p'],3)})",
             Resultado="log-rank aponta duração menor na coorte nova, mas o tempo de observação diferente encurta essa coorte por construção; proporção encerrada em dois anos sem diferença significativa", Evidência="Não determinável (coorte nova com " + str(R["h3_n_pos"]) + " ações e observação truncada)"),
    ])
    tabela(H3, "t_h3", titulo="Hipótese 3: o foro e o conjunto de ações que permanecem no STF", unidade="—", periodo="2003–2025",
           universo="Ações penais originárias com réu parlamentar (D-068)", fonte=F_STF, notas="Data de corte 03/05/2018 (D-068); referência do acórdão a confirmar.", codigo="H3")

    # ---- H4, quadro
    H4 = pd.DataFrame([
        dict(Comparação="Votos em resoluções de escrutínio", Observação="% de votos favoráveis por governo (régua Freedom House): " + "; ".join(f"{k} {br(v,0)}%" for k, v in vg.items()),
             Leitura="varia por governo, sem acompanhar a orientação partidária de modo regular (Dilma 1 e Bolsonaro altos; Lula 2 e Lula 3 baixos)", Evidência="Evidência associativa"),
        dict(Comparação="Exportações para países Não Livres", Observação="% por mandato: " + "; ".join(f"{k} {br(v,1)}%" for k, v in R["h4_comercio"].items()),
             Leitura="sobe de um mandato ao seguinte até 2019–22, sob governos de orientações diferentes, e fica estável em 2023–26; sem a China também sobe (capítulo 31)", Evidência="Fato observado"),
        dict(Comparação="BNDES, exportação de serviços", Observação="número de operações por ano sem salto nas trocas de governo; o valor das operações só é informado até 2015",
             Leitura="as maiores variações não caem nos anos de troca", Evidência="Não determinável quanto ao motivo"),
        dict(Comparação="Atos bilaterais", Observação="pico em 2010 e queda desde 2011, com mínimo em 2020",
             Leitura="a queda começa dentro de um mesmo partido no governo", Evidência="Fato observado"),
        dict(Comparação="Teste das trocas de governo", Observação=f"{R['h4_sig_n']} de {R['h4_n']} séries anuais com variação maior nas trocas (p < 0,05): {', '.join(R['h4_sig']) if R['h4_sig'] else 'nenhuma'}",
             Leitura="sem evidência de sincronia nas séries externas; com poucos anos de troca, ausência de evidência não prova autonomia", Evidência="Não determinável quanto à autonomia"),
    ])
    tabela(H4, "t_h4", titulo="Hipótese 4: política externa e ciclos domésticos", unidade="—", periodo="2003–2026", universo="Séries externas do livro",
           fonte="Ver capítulos 27 a 32 e a tabela do teste de trocas", notas="Governo é período de comparação, não causa medida.", codigo="H4")

    # ---- modelo provisório (relações e classes de evidência redigidas a partir dos resultados acima)
    REL = pd.DataFrame([
        dict(origem="Normas (Congresso e STF)", destino="Dinheiro eleitoral", sentido="→", evidencia="Evidência direta", rotulo="fim das doações de empresas (2015)\nfundo eleitoral (2017)", curva=0.0, dx=-0.15, dy=0.1,
             base="Lei 13.165/2015 (art. 15); Lei 13.487/2017; Lei 13.878/2019; decisão do STF de 2015 [REFERÊNCIA A CONFIRMAR]; dados do TSE mostram a troca de fonte na eleição seguinte", limite="A norma define a regra, não o comportamento dos candidatos"),
        dict(origem="Normas (Congresso e STF)", destino="Orçamento", sentido="→", evidencia="Evidência direta", rotulo="execução obrigatória\n(EC 86, 100, 105)", curva=0.0, dx=0.25, dy=0.05,
             base="EC 86/2015, EC 100/2019 e EC 105/2019; série de emendas da CGU", limite="O arquivo só é consistente desde 2017"),
        dict(origem="Normas (Congresso e STF)", destino="Partidos", sentido="→", evidencia="Evidência direta", rotulo="fim das coligações,\ncláusula, janela", curva=0.0, dx=0.1, dy=0.12,
             base="EC 97/2017; Lei 13.165/2015; NEP e mudanças de partido", limite="Fusões dependem também de decisões partidárias não medidas"),
        dict(origem="Normas (Congresso e STF)", destino="Justiça (STF)", sentido="→", evidencia="Evidência associativa", rotulo="restrição do foro (2018)\n[referência a confirmar]", curva=0.0, dx=0.0, dy=0.12,
             base="Questão de ordem na AP 937 [REFERÊNCIA A CONFIRMAR]; declínios e estoque de ações (capítulo 18 e H3)", limite="Passa a evidência direta quando o acórdão for confirmado; universo de ações da lista de D-048"),
        dict(origem="Dinheiro eleitoral", destino="Competição política", sentido="→", evidencia="Hipótese", rotulo="receitas menos concentradas;\nefeito na competição não medido", curva=0.0, dx=-0.15, dy=0.08,
             base="Gini e participação dos 10% maiores entre os eleitos (capítulo 7); testes de reeleição de H1 sem resultado", limite="As receitas medidas são só as dos eleitos; a regra interna de distribuição do fundo não foi medida"),
        dict(origem="Orçamento", destino="Competição política", sentido="→", evidencia="Evidência associativa" if comp_ok else "Não determinável", rotulo="emendas e reeleição\n(" + ("associação" if comp_ok else "sem associação estável") + ")", curva=0.55, dx=0.3, dy=0.0,
             base="Modelos de reeleição de 2018 e 2022 (H1)", limite="Valor pago depende da execução e de quem exerceu o mandato; " + f"{R['h1_lig_pct'][2018]:.0f}% e {R['h1_lig_pct'][2022]:.0f}% dos deputados em exercício ligados à candidatura"),
        dict(origem="Competição política", destino="Partidos", sentido="↔", evidencia="Hipótese", rotulo="dispersão e\nreconcentração", curva=0.0, dx=0.12, dy=0.1,
             base="NEP sobe até 2019 e cai em 2023 (capítulo 22)", limite="A reconcentração coincide com fusões e com a cláusula; o papel do dinheiro não foi medido"),
        dict(origem="Partidos", destino="Orçamento", sentido="↔", evidencia="Não determinável", rotulo="base e emendas\n(diferença pequena)", curva=0.0, dx=0.45, dy=0.0,
             base="Razão base/fora entre " + br(PB.razao_base_fora.min(), 2) + " e " + br(PB.razao_base_fora.max(), 2), limite="Emendas de relator e de comissão sem autor individual impedem o teste onde a distribuição seria mais discricionária"),
        dict(origem="Orçamento", destino="Distribuição de recursos", sentido="→", evidencia="Evidência associativa", rotulo="destino por UF\ne por função", curva=0.0, dx=0.35, dy=-0.05,
             base="Per capita por UF, saúde, sem UF (capítulo 15 e H2)", limite="Destino final do recurso não é observado"),
        dict(origem="Controle administrativo", destino="Distribuição de recursos", sentido="→", evidencia="Não determinável", rotulo="controle sobre\nemendas", curva=0.0, dx=-0.15, dy=-0.12,
             base="Sanções e contas irregulares não estão ligadas a emendas na base", limite="Faltam dados que liguem fiscalização a transferências"),
        dict(origem="Justiça (STF)", destino="Controle administrativo", sentido="↔", evidencia="Hipótese", rotulo="Lei 12.846/2013\ne leniências", curva=0.0, dx=-0.2, dy=0.0,
             base="Lei 12.846/2013; sanções crescem desde 2018 (capítulo 20)", limite="A série mede também a adesão ao cadastro"),
        dict(origem="Partidos", destino="Política externa", sentido="→", evidencia="Não determinável", rotulo="sincronia com\ngoverno: fraca", curva=0.0, dx=0.0, dy=0.12,
             base="Teste das trocas de governo e comparação por mandato (H4)", limite="Poucos governos; composição dos países-alvo muda a cada ano"),
    ])
    f = fig_modelo(REL)
    salvar(f, "n38", titulo="Modelo provisório da transformação institucional: relações entre mecanismos classificadas pela evidência disponível",
           pergunta="Como os mecanismos estudados se relacionam, segundo o que os dados permitem sustentar?", periodo="2003–2026", unidade="—",
           universo="Relações examinadas no livro", fonte_primaria="As dos capítulos e testes citados na tabela do modelo", tratamento="Classificação de cada relação pela escala de D-075",
           derivado="Diagrama em rede", limitacoes="Modelo interpretativo do autor; ausência de seta não significa ausência de relação, e sim falta de dado; não é um modelo causal estimado",
           leitura="As relações com evidência direta partem todas das normas; entre os mecanismos, as relações são associativas, hipotéticas ou não determináveis.", codigo="Parte VII")
    tabela(REL.assign(Relação=REL.origem + " " + REL.sentido + " " + REL.destino)[["Relação", "evidencia", "base", "limite"]].rename(columns={
        "evidencia": "Classe de evidência", "base": "Em que se apoia", "limite": "Limitação"}), "t_modelo",
        titulo="Relações do modelo provisório e classe de evidência", unidade="—", periodo="2003–2026", universo="Relações examinadas no livro",
        fonte="Capítulos e testes citados", notas="Escala de D-075. A cadeia linear proposta como ponto de partida (dinheiro, competição, partidos, orçamento, distribuição, controle, justiça, política externa) foi substituída por esta rede porque várias ligações da cadeia não têm sustentação e as relações com evidência direta partem das normas.", codigo="Parte VII")
    R["modelo_n"] = len(REL); R["modelo_classes"] = REL.evidencia.value_counts().to_dict()
    cadeia = [("Dinheiro", "Competição política", "Hipótese"), ("Competição política", "Partidos", "Hipótese"), ("Partidos", "Orçamento", "Não determinável"),
              ("Orçamento", "Distribuição de recursos", "Evidência associativa"), ("Distribuição de recursos", "Instituições de controle", "Não determinável"),
              ("Instituições de controle", "Justiça", "Hipótese"), ("Justiça", "Política externa", "Não determinável")]
    tabela(pd.DataFrame(cadeia, columns=["De", "Para", "Classe de evidência"]), "t_cadeia", titulo="A cadeia linear de partida, elo por elo",
           unidade="—", periodo="2003–2026", universo="Elos da cadeia proposta pelo autor", fonte="Testes e capítulos do livro",
           notas="Elos classificados pela escala de D-075 com os resultados deste livro; nenhum tem evidência direta.", codigo="Parte VII")
    R["cadeia_nd"] = sum(1 for *_, e in cadeia if e == "Não determinável")

    SK = dict(emp="Empresas no dinheiro dos eleitos (%)", fundo="Fundos eleitorais públicos no dinheiro dos eleitos (%)", part="Transferências de partidos no dinheiro dos eleitos (%)",
              prop="Recursos próprios no dinheiro dos eleitos (%)", gini="Gini das receitas dos eleitos", med="Receita mediana real por eleito (R$ mil)",
              desp="Despesa total da União (R$ bi reais)", fefc="Fundo eleitoral (FEFC) pago (R$ bi reais)", em_real="Emendas pagas (R$ bi reais)",
              em_pct="Emendas pagas (% da despesa total)", em_semautor="Emendas sem autor parlamentar identificado (% do pago)", em_te="Transferências especiais (% do pago)",
              em_giniuf="Desigualdade per capita entre UF (Gini)", disc_real="Discricionárias do Executivo (R$ bi reais)", disc_pct="Discricionárias do Executivo (% da despesa total)",
              exec="Execução das emendas (pago/empenhado, %)", nep="Número efetivo de partidos (Câmara)", trocas="Mudanças individuais de partido",
              base="Cadeiras da base do governo (%)", reel="Reeleição dos deputados que concorreram (%)", estoque="Ações penais com réu parlamentar em curso no STF",
              idade="Idade mediana das ações em curso (anos)", decl="Declínios de competência (réu parlamentar)", merito="Julgamentos de mérito (réu parlamentar)",
              sanc="Sanções a empresas registradas (CGU)", tcu="Contas irregulares no TCU, pessoas da base", etica="Representações nos Conselhos de Ética",
              votos="Votos a favor de resoluções de escrutínio (%)", coinc="Coincidência com a maioria das democracias (%)", atos="Atos bilaterais assinados",
              bndes="Operações de exportação de serviços (BNDES)", vdem="Democracia liberal do Brasil (V-Dem)", fh="Pontuação do Brasil (Freedom House)")
    R["pv"] = {k: {str(int(y)): float(v) for y, v in P[n].dropna().items()} for k, n in SK.items()}
    for k, n in SK.items():
        ss = P[n].dropna(); R["pv"][k]["max"] = float(ss.max()); R["pv"][k]["anomax"] = str(int(ss.idxmax())); R["pv"][k]["min"] = float(ss.min()); R["pv"][k]["anomin"] = str(int(ss.idxmin()))
    lst = lambda xs: (", ".join(xs[:-1]) + " e " + xs[-1]) if len(xs) > 1 else (xs[0] if xs else "nenhuma")
    low = lambda x: x[0].lower() + x[1:] if x and not x.startswith(("V-Dem", "STF", "TCU", "CGU", "BNDES", "Freedom")) else x
    R["t_janelas_comuns"] = lst(R["n7_janelas_comuns"])
    R["t_aceleracoes"] = lst([low(x) for x in R["n7_aceleracoes"]]); R["t_reversoes"] = lst([low(x) for x in R["n7_reversoes"]])
    R["n7_aceleracoes_n"] = len(R["n7_aceleracoes"]); R["n7_reversoes_n"] = len(R["n7_reversoes"])
    R["t_fora_janelas"] = lst([f"{low(k)} ({v})" for k, v in R["n7_fora_janelas"].items()])
    R["t_h4_sig"] = lst([low(x) for x in R["h4_sig"]]); R["t_h2_mudaram"] = lst([low(x) for x in R["h2_dim_mudaram"]]); R["t_h2_estaveis"] = lst([low(x) for x in R["h2_dim_estaveis"]])
    R["n7_rel_total"] = int(J.relevante.sum()); R["n7_rel_alta"] = int((J.relevante & (J.sentido == "alta")).sum()); R["n7_rel_queda"] = int((J.relevante & (J.sentido == "queda")).sum())
    R["n7_dur"] = {k: int(v) for k, v in J[J.relevante].duracao.value_counts().items()}
    R["n7_matriz_pct"] = {p: round(100 * R["n7_matriz_completa_mudancas"][p] / R["n7_matriz_completa_obs"][p], 0) for p in R["n7_matriz_completa_obs"] if R["n7_matriz_completa_obs"][p]}
    gravar_resultados(R)
    return dict(P=P, M=M, J=J, SY=SY, MX=MX, T=T, res=res, tq=tq, H2=H2, H3=H3, rp=rp, ES=ES, E=E, PB=PB)


if __name__ == "__main__":
    o = main()
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30); pd.set_option("display.max_colwidth", 60)
    print(o["SY"]); print(o["J"][o["J"].relevante][["serie", "janela", "dz", "sentido", "aceleracao", "reversao", "duracao"]].to_string())
    print(o["T"].round(3).to_string()); print(o["res"]); print(o["tq"]); print(o["H2"].to_string()); print(o["H3"].to_string())
    print(resultados()["n7_fora_janelas"], resultados()["n7_matriz_mudancas"], resultados()["n7_matriz_completa_mudancas"], resultados()["n7_matriz_completa_obs"])
