"""Parte II, Dinheiro e poder: receitas de campanha dos eleitos, 2002-2022 (análises D1-D5, D8-D10)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .comum import (ANOS_ELEICAO, C, F_IPCA, F_RTN, F_TSE_CONTAS, SIGLA, br, fator_real, fig, gini,
                    gravar_resultados, ler, nogridx, nogridy, partido_na_data, periodo_eleicao, salvar,
                    tabela, CUR)

TIPOS = {"pessoa_juridica": ("Empresas", C["blue"]), "partido": ("Repasses de partidos", C["orange"]),
         "fundo_publico": ("Fundo público", C["violet"]), "pessoa_fisica_agregado": ("Pessoas físicas", C["aqua"]),
         "recursos_proprios": ("Recursos próprios", C["yellow"]), "outro": ("Outros", C["gray"])}
ORDEM = list(TIPOS)
U_DEP = "Deputados federais eleitos ligados a um parlamentar da base (D-043)"


def cargo_eleito() -> pd.DataFrame:
    """Cargo para o qual cada ator foi eleito em cada eleição (deputado, senador ou outro)."""
    cg = ler("cargos")
    cg["ini"] = pd.to_datetime(cg.data_inicio, errors="coerce")
    rows = []
    for y in ANOS_ELEICAO:
        leg = 52 + (y - 2002) // 4
        dep = set(cg[cg.cargo == f"Deputado federal (titular), legislatura {leg}"].id_ator)
        sen = set(cg[(cg.cargo == "Senador (titular)") & (cg.ini.dt.year == y + 1)].id_ator)
        rows += [(y, a, "deputado") for a in dep] + [(y, a, "senador") for a in sen - dep]
    return pd.DataFrame(rows, columns=["ano_eleicao", "id_ator", "cat"])


def doacoes() -> pd.DataFrame:
    d = ler("doacoes_campanha")
    d = d[d.via == "direta"].copy()
    ce = cargo_eleito()
    d = d.merge(ce, on=["ano_eleicao", "id_ator"], how="left")
    d["cat"] = d.cat.fillna("outro")
    parts = []
    for y in ANOS_ELEICAO:
        pa = partido_na_data(f"{y}-10-01")
        x = d[d.ano_eleicao == y].copy()
        x["id_partido"] = x.id_ator.map(pa)
        x["sigla"] = x.id_partido.map(SIGLA)
        x["fator"] = fator_real(periodo_eleicao(y))
        parts.append(x)
    X = pd.concat(parts)
    X["real"] = X.valor * X.fator
    return X


def main() -> None:
    X = doacoes()
    R = {}
    dep = X[X.cat == "deputado"]
    R["p2_n_linhas"] = int(len(X))
    R["p2_n_dep_por_ano"] = {int(y): int(n) for y, n in dep.groupby("ano_eleicao").id_ator.nunique().items()}
    # --- mistura de fontes (D1)
    p = dep.pivot_table(index="ano_eleicao", columns="doador_tipo", values="valor", aggfunc="sum").reindex(ANOS_ELEICAO).fillna(0)
    p = p[[c for c in ORDEM if c in p.columns]]
    pp = p.div(p.sum(axis=1), axis=0) * 100
    for t in pp.columns:
        R[f"p2_mix_{t}"] = {int(y): round(float(v), 1) for y, v in pp[t].items()}
    f, a = fig(3.5)
    bot = np.zeros(len(pp))
    xs = [str(y) for y in pp.index]
    for c in pp.columns:
        a.bar(xs, pp[c], bottom=bot, color=TIPOS[c][1], label=TIPOS[c][0], width=0.62, edgecolor="white", linewidth=1.2)
        for i, v in enumerate(pp[c]):
            if v >= 6:
                a.text(i, bot[i] + v / 2, f"{br(v, 0)}%", ha="center", va="center", fontsize=7.5,
                       color="white" if c not in ("recursos_proprios", "outro") else C["ink"], fontweight="bold")
        bot += pp[c].values
    a.set_ylim(0, 100); a.set_ylabel("% do total arrecadado"); nogridx(a)
    a.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.1))
    a.set_title("Composição das receitas dos deputados federais eleitos")
    salvar(f, "c01", titulo="Composição das receitas de campanha dos deputados federais eleitos, por tipo de doador, 2002–2022",
           pergunta="De que fontes vinha o dinheiro dos deputados eleitos em cada eleição?",
           periodo="Eleições gerais de 2002 a 2022", unidade="% do total arrecadado no grupo (proporção; não depende de correção monetária)",
           universo=U_DEP, fonte_primaria=F_TSE_CONTAS,
           tratamento="Ligação candidato–parlamentar por nome e mandato (D-043); só receitas diretas (as linhas de doador originário de 2014 não são somadas de novo); em 2002 o tipo é deduzido do documento do doador; soma por tipo de doador",
           derivado="Parcela de cada tipo de doador no total do grupo, por eleição",
           limitacoes="Só eleitos; até 2010 os repasses de partido não mostram o doador original; 2002 com tipo deduzido",
           leitura=f"Empresas: {br(pp.get('pessoa_juridica', pd.Series({2002: 0}))[2002], 0)}% em 2002 e {br(pp['pessoa_juridica'][2014], 0)}% em 2014; fundo público: {br(pp['fundo_publico'][2018], 0)}% em 2018 e {br(pp['fundo_publico'][2022], 0)}% em 2022.",
           codigo="D1")
    # --- totais nominais e reais por origem (todos os eleitos e presidenciáveis)
    tn = X.pivot_table(index="ano_eleicao", columns="doador_tipo", values="valor", aggfunc="sum").reindex(ANOS_ELEICAO).fillna(0)
    tr = X.pivot_table(index="ano_eleicao", columns="doador_tipo", values="real", aggfunc="sum").reindex(ANOS_ELEICAO).fillna(0)
    R["p2_total_nominal_bi"] = {int(y): round(float(v) / 1e9, 2) for y, v in tn.sum(axis=1).items()}
    R["p2_total_real_bi"] = {int(y): round(float(v) / 1e9, 2) for y, v in tr.sum(axis=1).items()}
    f, axs = __import__("matplotlib.pyplot").pyplot.subplots(1, 2, figsize=(6.3, 3.2), sharey=False)
    for a, M, tit in ((axs[0], tn / 1e9, "Valores nominais"), (axs[1], tr / 1e9, "Reais de ago/2026 (IPCA)")):
        bot = np.zeros(len(M))
        for c in [c for c in ORDEM if c in M.columns]:
            a.bar([str(y)[2:] for y in M.index], M[c], bottom=bot, color=TIPOS[c][1], label=TIPOS[c][0], width=0.66, edgecolor="white", linewidth=0.8)
            bot += M[c].values
        for i, v in enumerate(bot):
            a.text(i, v + 0.03 * max(bot), br(v, 1), ha="center", fontsize=7)
        a.set_title(tit, fontsize=8.5); nogridx(a); a.set_ylim(0, max(bot) * 1.15); a.tick_params(labelsize=7.5)
    axs[0].set_ylabel("R$ bilhões"); axs[0].set_xlabel("eleição (20xx)"); axs[1].set_xlabel("eleição (20xx)")
    axs[1].legend(fontsize=6.5, loc="upper left")
    salvar(f, "c02", titulo="Receitas de campanha dos eleitos e dos presidenciáveis, por origem, em valores nominais e reais",
           pergunta="Quanto dinheiro entrou nas campanhas dos eleitos em cada eleição, e de onde?",
           periodo="Eleições gerais de 2002 a 2022", unidade="R$ bilhões; nominais (esquerda) e em reais de agosto de 2026 pelo IPCA de outubro do ano da eleição (direita)",
           universo="Presidenciáveis e governadores, senadores e deputados federais eleitos com receitas ligadas (D-043)",
           fonte_primaria=F_TSE_CONTAS + "; " + F_IPCA,
           tratamento="Soma das receitas diretas por origem; deflação pelo IPCA (D-070)",
           derivado="Total por origem, nominal e real",
           limitacoes="Não eleitos ficam fora; a série real depende do índice escolhido; valores do IPCA lidos na API do IBGE por ferramenta de leitura (D-070)",
           leitura=f"Em valores reais, o total passa de R$ {br(tr.sum(axis=1)[2002]/1e9,1)} bi (2002) a R$ {br(tr.sum(axis=1)[2014]/1e9,1)} bi (2014) e R$ {br(tr.sum(axis=1)[2022]/1e9,1)} bi (2022).",
           codigo="D1")
    t4 = pd.DataFrame({"eleicao": ANOS_ELEICAO})
    for c in [c for c in ORDEM if c in pp.columns]:
        t4[f"{TIPOS[c][0]} (%)"] = [round(float(pp[c][y]), 1) for y in ANOS_ELEICAO]
    t4["Total nominal (R$ mi)"] = [round(float(p.sum(axis=1)[y]) / 1e6, 1) for y in ANOS_ELEICAO]
    pr = dep.pivot_table(index="ano_eleicao", values="real", aggfunc="sum").reindex(ANOS_ELEICAO)
    t4["Total real (R$ mi de ago/2026)"] = [round(float(pr.real[y]) / 1e6, 1) for y in ANOS_ELEICAO]
    tabela(t4, "t_d1_mix", titulo="Composição das receitas dos deputados federais eleitos, por eleição",
           unidade="% do total; totais em R$ milhões nominais e reais (ago/2026)", periodo="2002–2022", universo=U_DEP,
           fonte=F_TSE_CONTAS + "; " + F_IPCA, notas="Receitas diretas; tipo de 2002 deduzido; deflação pelo IPCA de outubro do ano da eleição (D-070).", codigo="D1")
    # --- mediana do deputado eleito (D2) e distribuição
    pc = dep.groupby(["ano_eleicao", "id_ator"]).agg(valor=("valor", "sum"), real=("real", "sum")).reset_index()
    q = pc.groupby("ano_eleicao").agg(med=("valor", "median"), medr=("real", "median"),
                                      p10=("real", lambda s: s.quantile(.1)), p90=("real", lambda s: s.quantile(.9)), n=("real", "size"))
    R["p2_mediana_nominal_mil"] = {int(y): round(float(v) / 1e3, 0) for y, v in q.med.items()}
    R["p2_mediana_real_mil"] = {int(y): round(float(v) / 1e3, 0) for y, v in q.medr.items()}
    f, a = fig(3.0)
    xs = np.arange(len(q))
    a.fill_between(xs, q.p10 / 1e6, q.p90 / 1e6, color=C["blue"], alpha=0.12, lw=0, label="Entre os percentis 10 e 90 (real)")
    a.plot(xs, q.medr / 1e6, color=C["blue"], lw=2, marker="o", label="Mediana, reais de ago/2026")
    a.plot(xs, q.med / 1e6, color=C["gray"], lw=1.6, marker="o", ms=4, label="Mediana, nominal")
    for i, (v, w) in enumerate(zip(q.medr / 1e6, q.med / 1e6)):
        a.text(i, v + 0.12, br(v, 2), ha="center", fontsize=7.5, color=C["blue"], fontweight="bold")
    a.set_xticks(xs); a.set_xticklabels(q.index); a.set_ylabel("R$ milhões por deputado eleito"); nogridx(a)
    a.legend(fontsize=7, loc="upper left"); a.set_title("Arrecadação do deputado federal eleito")
    salvar(f, "c03", titulo="Mediana e faixa central da arrecadação dos deputados federais eleitos, nominal e real",
           pergunta="Quanto arrecadava um deputado eleito típico, descontada a inflação?", periodo="2002–2022",
           unidade="R$ milhões por deputado eleito; reais de agosto de 2026 (IPCA de outubro do ano da eleição) e nominais",
           universo=U_DEP, fonte_primaria=F_TSE_CONTAS + "; " + F_IPCA,
           tratamento="Soma das receitas diretas por deputado; mediana e percentis 10 e 90 por eleição; deflação (D-070)",
           derivado="Mediana, percentis 10 e 90", limitacoes="Só eleitos: não mede o custo de quem disputou e perdeu",
           leitura=f"A mediana real vai de R$ {br(q.medr[2002]/1e6,2)} mi (2002) a R$ {br(q.medr[2014]/1e6,2)} mi (2014) e R$ {br(q.medr[2022]/1e6,2)} mi (2022); a nominal, de R$ {br(q.med[2002]/1e3,0)} mil a R$ {br(q.med[2022]/1e6,2)} mi.",
           codigo="D2")
    # --- concentração (D3): parcela dos 10% e Gini entre deputados eleitos
    rows = []
    for y, g in pc.groupby("ano_eleicao"):
        s = g.valor.sort_values(ascending=False)
        k = max(1, int(round(len(s) * 0.1)))
        rows.append(dict(eleicao=int(y), deputados=len(s), parcela_10pct=round(float(s.head(k).sum() / s.sum() * 100), 1),
                         parcela_metade_inferior=round(float(s.tail(len(s) // 2).sum() / s.sum() * 100), 1), gini=round(gini(s), 3)))
    cc = pd.DataFrame(rows)
    R["p2_gini"] = dict(zip(cc.eleicao, cc.gini)); R["p2_top10pct"] = dict(zip(cc.eleicao, cc.parcela_10pct))
    f, (a1, a2) = __import__("matplotlib.pyplot").pyplot.subplots(1, 2, figsize=(6.3, 3.0))
    for y, col in zip(ANOS_ELEICAO, ["#cde2fb", "#9ec5f4", "#6da7ec", "#2a78d6", C["orange"], C["red"]]):
        s = np.sort(pc[pc.ano_eleicao == y].valor.values)
        cum = np.concatenate([[0], np.cumsum(s) / s.sum()])
        a1.plot(np.linspace(0, 1, len(cum)) * 100, cum * 100, color=col, lw=1.6, label=str(y))
    a1.plot([0, 100], [0, 100], color=C["gray"], lw=0.8, ls="--")
    a1.set_xlabel("% dos deputados (do que menos ao que mais arrecadou)", fontsize=7.5); a1.set_ylabel("% do dinheiro acumulado")
    a1.legend(fontsize=6.5, ncol=2); a1.set_title("Curvas de concentração", fontsize=8.5)
    a2.bar(cc.eleicao.astype(str), cc.gini, color=C["blue"], width=0.6)
    for i, v in enumerate(cc.gini):
        a2.text(i, v + 0.01, br(v, 2), ha="center", fontsize=7.5)
    a2.set_ylim(0, 0.8); nogridx(a2); a2.set_title("Índice de Gini", fontsize=8.5); a2.tick_params(labelsize=7.5)
    salvar(f, "c04", titulo="Concentração das receitas entre deputados federais eleitos: curvas de Lorenz e índice de Gini",
           pergunta="O dinheiro se concentrou em poucos eleitos ou se distribuiu mais igualmente?", periodo="2002–2022",
           unidade="% acumulado do dinheiro e dos deputados; Gini de 0 (igualdade) a 1", universo=U_DEP,
           fonte_primaria=F_TSE_CONTAS, tratamento="Soma por deputado; ordenação; curva de Lorenz e Gini por eleição",
           derivado="Curva de Lorenz, Gini, parcela dos 10% que mais arrecadaram",
           limitacoes="Mede desigualdade entre eleitos, não entre candidatos",
           leitura=f"Os 10% que mais arrecadaram ficaram com {br(cc.set_index('eleicao').parcela_10pct[2014],1)}% em 2014 e {br(cc.set_index('eleicao').parcela_10pct[2022],1)}% em 2022; o Gini vai de {br(cc.gini.iloc[0],2)} (2002) a {br(cc.set_index('eleicao').gini[2014],2)} (2014) e {br(cc.set_index('eleicao').gini[2022],2)} (2022).",
           codigo="D3")
    tabela(cc.rename(columns={"eleicao": "Eleição", "deputados": "Deputados", "parcela_10pct": "10% que mais arrecadaram (% do total)",
                              "parcela_metade_inferior": "Metade que menos arrecadou (% do total)", "gini": "Gini"}),
           "t_d3_conc", titulo="Concentração das receitas entre deputados federais eleitos", unidade="% e índice", periodo="2002–2022",
           universo=U_DEP, fonte=F_TSE_CONTAS, notas="Receitas diretas somadas por deputado.", codigo="D3")
    # --- escala das campanhas majoritárias (D4, como categoria)
    pres = ler("cargos")
    out = X[X.cat == "outro"].groupby(["ano_eleicao", "id_ator"]).real.sum().reset_index()
    top = out.sort_values("real", ascending=False).groupby("ano_eleicao").head(2).groupby("ano_eleicao").real.agg(["sum", "max"])
    R["p2_majoritaria_top2_real_mi"] = {int(y): round(float(v) / 1e6, 1) for y, v in top["sum"].items()}
    # --- recursos próprios (D10)
    rp = X[X.doador_tipo == "recursos_proprios"].groupby("ano_eleicao").agg(nom=("valor", "sum"), real=("real", "sum")).reindex(ANOS_ELEICAO)
    R["p2_recursos_proprios_nominal_mi"] = {int(y): round(float(v) / 1e6, 1) for y, v in rp.nom.items()}
    R["p2_recursos_proprios_real_mi"] = {int(y): round(float(v) / 1e6, 1) for y, v in rp.real.items()}
    f, a = fig(2.8)
    a.bar([str(y) for y in rp.index], rp.real / 1e6, color=C["yellow"], width=0.6, label="Reais de ago/2026")
    a.plot([str(y) for y in rp.index], rp.nom / 1e6, color=C["ink2"], marker="o", lw=1.2, label="Nominal")
    for i, v in enumerate(rp.real / 1e6):
        a.text(i, v + 3, br(v, 1), ha="center", fontsize=7.5)
    a.set_ylabel("R$ milhões"); nogridx(a); a.legend(fontsize=7); a.set_title("Recursos próprios dos candidatos nas próprias campanhas")
    salvar(f, "c11", titulo="Recursos próprios aplicados pelos eleitos e presidenciáveis nas próprias campanhas",
           pergunta="Quanto os candidatos eleitos pagaram da própria campanha?", periodo="2002–2022",
           unidade="R$ milhões, reais de ago/2026 (barras) e nominais (linha)",
           universo="Presidenciáveis e eleitos com receitas ligadas (D-043)", fonte_primaria=F_TSE_CONTAS + "; " + F_IPCA,
           tratamento="Soma das receitas do tipo recursos próprios; deflação (D-070)", derivado="Total por eleição",
           limitacoes="O limite ao autofinanciamento (Lei 13.878/2019) vale a partir de 2020; a base não registra a regra aplicada a cada candidato",
           leitura=f"Recursos próprios: R$ {br(rp.real[2018]/1e6,1)} mi em 2018 e R$ {br(rp.real[2022]/1e6,1)} mi em 2022, em reais de ago/2026.",
           codigo="D10")
    # --- partido como canal (D8, D9), por eleito
    pd_ = X[X.cat.isin(["deputado", "senador"]) & X.sigla.notna()]
    eleitos = pd_.groupby(["ano_eleicao", "sigla"]).id_ator.nunique()
    fu = pd_[pd_.doador_tipo == "fundo_publico"].groupby(["ano_eleicao", "sigla"]).real.sum()
    pj = pd_[pd_.doador_tipo == "pessoa_juridica"].groupby(["ano_eleicao", "sigla"]).real.sum()
    def tab_por(serie, anos, top=10):
        df = pd.DataFrame({"total": serie, "eleitos": eleitos}).dropna(subset=["total"]).reset_index()
        df = df[df.ano_eleicao.isin(anos)]
        tot = df.groupby("sigla").total.sum().sort_values(ascending=False).head(top).index
        df = df[df.sigla.isin(tot)]
        df["por_eleito"] = df.total / df.eleitos
        return df, list(tot)
    dff, siglas_f = tab_por(fu, [2018, 2022])
    dfp, siglas_p = tab_por(pj, [2002, 2006, 2010, 2014], top=8)
    for nome, df, sig_, anos, cor, tit, cod in (
            ("c09", dff, siglas_f, [2018, 2022], [C["violet"], "#9a8fe0"], "Fundo público recebido por eleito, por partido", "D8"),
            ("c10", dfp, siglas_p, [2002, 2006, 2010, 2014], ["#cde2fb", "#6da7ec", "#2a78d6", "#0d366b"], "Doações de empresas por eleito, por partido", "D9")):
        f, (a1, a2) = __import__("matplotlib.pyplot").pyplot.subplots(1, 2, figsize=(6.3, 3.4), sharey=True)
        y0 = np.arange(len(sig_))[::-1]
        h = 0.8 / len(anos)
        for j, (ano, c) in enumerate(zip(anos, cor)):
            g = df[df.ano_eleicao == ano].set_index("sigla").reindex(sig_)
            a1.barh(y0 + (len(anos) / 2 - j - 0.5) * h, g.total / 1e6, height=h, color=c, label=str(ano))
            a2.barh(y0 + (len(anos) / 2 - j - 0.5) * h, g.por_eleito / 1e6, height=h, color=c)
        a1.set_yticks(y0); a1.set_yticklabels(sig_); nogridy(a1); nogridy(a2)
        a1.set_xlabel("Total, R$ mi (ago/2026)", fontsize=7.5); a2.set_xlabel("Por eleito, R$ mi (ago/2026)", fontsize=7.5)
        a1.legend(fontsize=6.5, loc="lower right"); a1.set_title(tit, fontsize=9)
        lider = df.groupby("sigla").total.sum().sort_values(ascending=False)
        salvar(f, nome, titulo=tit + " (total e por eleito), reais de ago/2026",
               pergunta="Quanto cada partido recebeu, no total e por eleito?",
               periodo=", ".join(str(a) for a in anos), unidade="R$ milhões de ago/2026",
               universo="Deputados federais e senadores eleitos com partido identificado na data da eleição",
               fonte_primaria=F_TSE_CONTAS + "; " + F_IPCA,
               tratamento="Partido pela filiação em 1º de outubro do ano da eleição (D-016); soma e divisão pelo número de eleitos do partido com receita ligada",
               derivado="Total e média por eleito", limitacoes="Governadores e presidenciáveis ficam de fora; DEM inclui o PFL; o número de eleitos é o do universo ligado, não o oficial",
               leitura=f"Maiores totais no período: {', '.join(lider.index[:3])}.", codigo=cod)
        t = df.pivot_table(index="sigla", columns="ano_eleicao", values=["total", "por_eleito"]).reindex(sig_)
        t.columns = [f"{'Total' if a=='total' else 'Por eleito'} {b} (R$ mi)" for a, b in t.columns]
        t = (t / 1e6).round(2).reset_index().rename(columns={"sigla": "Partido"})
        tabela(t, "t_" + cod.lower() + "_partido", titulo=tit, unidade="R$ milhões de ago/2026", periodo=", ".join(map(str, anos)),
               universo="Deputados federais e senadores eleitos com partido identificado", fonte=F_TSE_CONTAS + "; " + F_IPCA,
               notas="Partido na data da eleição; média por eleito com receita ligada.", codigo=cod)
    # --- FEFC oficial (RTN) x recebido pelos eleitos do universo
    rtn = pd.read_csv(CUR / "tesouro_rtn_anual.csv")
    fefc = rtn[rtn.linha == "fefc"].set_index("ano").valor_rs_milhoes
    R["p2_fefc_rtn_mi"] = {int(a): round(float(v), 1) for a, v in fefc.items() if v and v > 0}
    rec = X[X.doador_tipo == "fundo_publico"].groupby("ano_eleicao").valor.sum() / 1e6
    R["p2_fundo_recebido_universo_mi"] = {int(a): round(float(v), 1) for a, v in rec.items()}
    # --- empresas nomeadas (para o Atlas; D5), sem proporções (D-071)
    e = ler("doacoes_campanha")
    e = e[e.id_doador.notna()]
    emp = e.pivot_table(index="id_doador", columns="via", values="valor", aggfunc="sum").fillna(0)
    emp["eleitos_ou_candidatos"] = e[e.via == "direta"].groupby("id_doador").id_ator.nunique()
    emp["nome"] = emp.index.map(lambda i: __import__("src.livro.comum", fromlist=["NOME_INS"]).NOME_INS.get(i, i))
    emp = emp.sort_values("direta", ascending=False)
    pj_total = X[X.doador_tipo == "pessoa_juridica"].valor.sum()
    R["p2_empresas_nomeadas_n"] = int(len(emp))
    R["p2_empresas_nomeadas_pct_valor_direto"] = round(float(emp.direta.sum() / pj_total * 100), 1)
    t = emp.reset_index()[["nome", "direta", "originario_via_partido", "eleitos_ou_candidatos"]].head(40)
    t.columns = ["Empresa", "Doação direta (R$, nominal)", "Doação via partido, doador originário (R$, nominal)", "Candidatos financiados"]
    tabela(t, "atlas_empresas", titulo="Empresas nomeadas na base de doações (as 40 de maior doação direta)",
           unidade="R$ nominais", periodo="2002–2014", universo=f"{len(emp)} empresas com linha própria por estarem no BNDES ou na CGU (D-043); cerca de {br(R['p2_empresas_nomeadas_pct_valor_direto'],0)}% do valor doado diretamente por empresas aos eleitos",
           fonte=F_TSE_CONTAS, notas="Seleção não aleatória: a lista não representa as maiores doadoras do período. Doações legais e declaradas à época. Doação via partido registrada só em 2014.", codigo="D5")
    gravar_resultados(R)
    print({k: R[k] for k in list(R)[:6]})


if __name__ == "__main__":
    main()
