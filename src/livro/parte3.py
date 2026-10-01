"""Parte III, O Estado como distribuidor de recursos: emendas parlamentares 2017-2026 (análises M1-M8)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .comum import (C, CUR, F_CGU_EMENDAS, F_IPCA, F_POP, F_RTN, NOME_ATOR, SIGLA, br, fator_real, fig, gini,
                    gravar_resultados, ler, nogridx, nogridy, partido_na_data, periodo_ano, salvar, tabela)

TN = {"Emenda Individual - Transferências com Finalidade Definida": "Individual (finalidade definida)",
      "Emenda Individual - Transferências Especiais": "Individual (transferência especial)",
      "Emenda de Bancada": "Bancada", "Emenda de Comissão": "Comissão", "Emenda de Relator": "Relator"}
TC = {"Individual (finalidade definida)": C["blue"], "Individual (transferência especial)": C["aqua"],
      "Bancada": C["orange"], "Comissão": C["violet"], "Relator": C["red"]}
ORD = list(TC)
ANOS = list(range(2017, 2027))
U = "Linhas do arquivo de emendas da CGU agregadas por emenda, localidade e função (D-029); 2017–2026 (2014–2016 com inconsistências, fora)"
UF = {"ACRE": "AC", "ALAGOAS": "AL", "AMAPÁ": "AP", "AMAZONAS": "AM", "BAHIA": "BA", "CEARÁ": "CE", "DISTRITO FEDERAL": "DF",
      "ESPÍRITO SANTO": "ES", "GOIÁS": "GO", "MARANHÃO": "MA", "MATO GROSSO": "MT", "MATO GROSSO DO SUL": "MS",
      "MINAS GERAIS": "MG", "PARÁ": "PA", "PARAÍBA": "PB", "PARANÁ": "PR", "PERNAMBUCO": "PE", "PIAUÍ": "PI",
      "RIO DE JANEIRO": "RJ", "RIO GRANDE DO NORTE": "RN", "RIO GRANDE DO SUL": "RS", "RONDÔNIA": "RO", "RORAIMA": "RR",
      "SANTA CATARINA": "SC", "SÃO PAULO": "SP", "SERGIPE": "SE", "TOCANTINS": "TO"}


def main() -> None:
    R = {}
    em = ler("emendas_parlamentares", low_memory=False)
    em["t"] = em.tipo_emenda.map(TN).fillna(em.tipo_emenda)
    em["fator"] = em.ano.map(lambda y: fator_real(periodo_ano(int(y))))
    em["pago_real"] = em.valor_pago * em.fator
    E = em[em.ano.between(2017, 2026)].copy()
    pv = E.pivot_table(index="ano", columns="t", values="valor_pago", aggfunc="sum").reindex(ANOS).fillna(0)[ORD] / 1e9
    pr = E.pivot_table(index="ano", columns="t", values="pago_real", aggfunc="sum").reindex(ANOS).fillna(0)[ORD] / 1e9
    R["p3_pago_nominal_bi"] = {int(y): round(float(v), 2) for y, v in pv.sum(axis=1).items()}
    R["p3_pago_real_bi"] = {int(y): round(float(v), 2) for y, v in pr.sum(axis=1).items()}
    for t in ORD:
        R[f"p3_pago_nominal_{t}"] = {int(y): round(float(v), 2) for y, v in pv[t].items()}
    R["p3_pago_nominal_Individual_te"] = R["p3_pago_nominal_Individual (transferência especial)"]
    R["p3_pago_nominal_Comissao"] = R["p3_pago_nominal_Comissão"]
    R["p3_mult_nominal_2017_2025"] = round(float(pv.sum(axis=1)[2025] / pv.sum(axis=1)[2017]), 1)
    R["p3_mult_real_2017_2025"] = round(float(pr.sum(axis=1)[2025] / pr.sum(axis=1)[2017]), 1)
    R["p3_pago_2014_2016_nominal_bi"] = {int(y): round(float(v) / 1e9, 2) for y, v in em[em.ano < 2017].groupby("ano").valor_pago.sum().items()}
    # c22: barras empilhadas nominais + linha real do total
    f, a = fig(3.8)
    bot = np.zeros(len(ANOS))
    for c in ORD:
        a.bar([str(y) for y in ANOS], pv[c], bottom=bot, color=TC[c], label=c, width=0.68, edgecolor="white", linewidth=0.8)
        bot += pv[c].values
    a.plot([str(y) for y in ANOS], pr.sum(axis=1), color=C["ink"], lw=1.4, marker="o", ms=3.5, label="Total em reais de ago/2026")
    for i, (v, w) in enumerate(zip(bot, pr.sum(axis=1))):
        a.text(i, v + 0.5, br(v, 1), ha="center", va="bottom", fontsize=7.5, fontweight="bold") if v + 2 < w or v > w + 0.5 else a.text(i, max(v, w) + 1.0, br(v, 1), ha="center", fontsize=7.5, fontweight="bold")
    a.set_ylabel("R$ bilhões pagos"); nogridx(a); a.legend(ncol=2, loc="upper left", fontsize=7); a.set_ylim(0, 46)
    a.set_title("Emendas parlamentares pagas, por modalidade")
    salvar(f, "c22", titulo="Emendas parlamentares pagas por modalidade, 2017–2026 (nominal) e total em valores reais",
           pergunta="Quanto o orçamento federal pagou por meio de emendas parlamentares, e em que modalidades?",
           periodo="2017–2026 (2026 até a data do arquivo, 23/09/2026)", unidade="R$ bilhões; barras nominais, linha em reais de ago/2026 (IPCA de junho de cada ano)",
           universo=U, fonte_primaria=F_CGU_EMENDAS + "; " + F_IPCA,
           tratamento="Soma do valor pago por ano e modalidade; deflação pelo IPCA de junho (D-070)",
           derivado="Total pago por ano e modalidade, nominal e real",
           limitacoes="Pagamento inclui restos a pagar de anos anteriores; 2026 parcial; 2014–2016 fora por inconsistência",
           leitura=f"Total pago: R$ {br(pv.sum(axis=1)[2017],1)} bi em 2017, R$ {br(pv.sum(axis=1)[2020],1)} bi em 2020 e R$ {br(pv.sum(axis=1)[2025],1)} bi em 2025, nominais; em reais de ago/2026, R$ {br(pr.sum(axis=1)[2017],1)} bi e R$ {br(pr.sum(axis=1)[2025],1)} bi.",
           codigo="M1")
    t = pv.round(2).copy(); t["Total nominal"] = t.sum(axis=1).round(2); t["Total real (ago/2026)"] = pr.sum(axis=1).round(2)
    tabela(t.reset_index().rename(columns={"ano": "Ano"}), "t_m1_tipo", titulo="Emendas pagas por modalidade e ano",
           unidade="R$ bilhões nominais; total também em reais de ago/2026", periodo="2017–2026", universo=U,
           fonte=F_CGU_EMENDAS + "; " + F_IPCA, notas="2026 parcial; pagamento inclui restos a pagar.", codigo="M1")
    # proporção da despesa (RTN)
    rtn = pd.read_csv(CUR / "tesouro_rtn_anual.csv").pivot_table(index="ano", columns="linha", values="valor_rs_milhoes")
    pct_tot = (pv.sum(axis=1) * 1e3 / rtn.despesa_total.reindex(ANOS) * 100).dropna()
    pct_dis = (pv.sum(axis=1) * 1e3 / rtn.despesas_discricionarias_executivo.reindex(ANOS) * 100).dropna()
    R["p3_pct_despesa_total"] = {int(y): round(float(v), 2) for y, v in pct_tot.items()}
    R["p3_razao_discricionarias"] = {int(y): round(float(v), 1) for y, v in pct_dis.items()}
    f, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 2.9))
    a1.plot(pct_tot.index, pct_tot.values, color=C["blue"], lw=2, marker="o", ms=4)
    for x0, v in pct_tot.items():
        a1.text(x0, v + 0.04, br(v, 2), ha="center", fontsize=7)
    a1.set_ylim(0, max(pct_tot) * 1.35); a1.set_title("% da despesa total (Gov. Central)", fontsize=8.5); nogridx(a1)
    a2.plot(pct_dis.index, pct_dis.values, color=C["orange"], lw=2, marker="o", ms=4)
    for x0, v in pct_dis.items():
        a2.text(x0, v + 0.6, br(v, 0), ha="center", fontsize=7)
    a2.set_ylim(0, max(pct_dis) * 1.3); a2.set_title("Sobre discricionárias do Executivo (%)", fontsize=8.5); nogridx(a2)
    for a in (a1, a2):
        a.set_xticks(list(pct_tot.index)); a.tick_params(labelsize=7); a.set_xticklabels([str(y)[2:] for y in pct_tot.index])
    salvar(f, "n07", titulo="Emendas pagas em proporção da despesa do Governo Central, 2017–2025",
           pergunta="Que peso as emendas têm no gasto federal?", periodo="2017–2025",
           unidade="% (valores nominais divididos por valores nominais do mesmo ano)",
           universo=U + "; despesa do Governo Central (RTN)", fonte_primaria=F_CGU_EMENDAS + "; " + F_RTN,
           tratamento="Divisão do total pago no ano pela despesa total e pelas despesas discricionárias do Poder Executivo do mesmo ano (Tabela 2.1 do RTN)",
           derivado="Razão emendas/despesa",
           limitacoes="Critérios diferentes: a CGU registra o pago no ano (inclusive restos a pagar), o RTN o pago pelo critério de caixa; a razão sobre as discricionárias não é uma parcela, porque as emendas não estão necessariamente contidas nessa linha do RTN",
           leitura=f"As emendas pagas equivalem a {br(pct_tot[2017],2)}% da despesa total em 2017 e {br(pct_tot[2025],2)}% em 2025; sobre as discricionárias do Executivo, a razão vai de {br(pct_dis[2017],0)}% a {br(pct_dis[2025],0)}%.",
           codigo="M1")
    # c23 linhas por modalidade (sem relator)
    f, a = fig(3.0)
    for c in ORD[:4]:
        a.plot(ANOS, pv[c], color=TC[c], lw=2, marker="o", ms=4, label=c)
    a.set_xticks(ANOS); a.set_ylabel("R$ bilhões pagos (nominais)"); nogridx(a); a.legend(fontsize=7, loc="upper left")
    a.set_title("Emendas pagas por modalidade, exceto relator")
    salvar(f, "c23", titulo="Emendas pagas por modalidade (exceto relator), 2017–2026", pergunta="Como cada modalidade evoluiu?",
           periodo="2017–2026", unidade="R$ bilhões nominais", universo=U, fonte_primaria=F_CGU_EMENDAS,
           tratamento="Soma do valor pago por ano e modalidade", derivado="Série por modalidade", limitacoes="2026 parcial",
           leitura=f"Transferências especiais: R$ {br(pv['Individual (transferência especial)'][2020],1)} bi em 2020 e R$ {br(pv['Individual (transferência especial)'][2024],1)} bi em 2024; comissão: R$ {br(pv['Comissão'][2023],1)} bi em 2023 e R$ {br(pv['Comissão'][2024],1)} bi em 2024.",
           codigo="M2")
    # c24 relator
    r = em[em.t == "Relator"].groupby("ano")[["valor_empenhado", "valor_pago"]].sum().reindex([2019, 2020, 2021, 2022, 2023]).fillna(0) / 1e9
    R["p3_relator_empenhado_bi"] = {int(y): round(float(v), 2) for y, v in r.valor_empenhado.items()}
    R["p3_relator_pago_bi"] = {int(y): round(float(v), 2) for y, v in r.valor_pago.items()}
    rel = em[em.t == "Relator"]
    R["p3_relator_linhas"] = int(len(rel)); R["p3_relator_sem_autor"] = int(rel.id_ator.isna().sum())
    R["p3_relator_relator_geral"] = int(rel.autor_fonte.astype(str).str.upper().str.contains("RELATOR").sum())
    f, a = fig(2.8)
    x = np.arange(len(r))
    a.bar(x - 0.2, r.valor_empenhado, 0.38, color=C["red"], label="Empenhado")
    a.bar(x + 0.2, r.valor_pago, 0.38, color=C["gray"], label="Pago")
    for i, (u, v) in enumerate(zip(r.valor_empenhado, r.valor_pago)):
        a.text(i - 0.2, u + 0.4, br(u, 1), ha="center", fontsize=7.5); a.text(i + 0.2, v + 0.4, br(v, 1), ha="center", fontsize=7.5)
    a.set_xticks(x); a.set_xticklabels(r.index); a.set_ylabel("R$ bilhões (nominais)"); nogridx(a); a.legend()
    a.set_title("Emendas de relator: empenhado e pago")
    salvar(f, "c24", titulo="Emendas de relator, empenhado e pago, 2019–2023", pergunta="Qual foi a escala das emendas de relator e quando deixam de aparecer?",
           periodo="2019–2023", unidade="R$ bilhões nominais", universo="Linhas do tipo Emenda de Relator no arquivo da CGU",
           fonte_primaria=F_CGU_EMENDAS, tratamento="Soma por ano", derivado="Empenhado e pago por ano",
           limitacoes="O arquivo registra o autor como \"relator geral\" ou sem informação; não identifica quem indicou os recursos; 2016–2017 com inconsistências",
           leitura=f"Empenhado: R$ {br(r.valor_empenhado[2020],1)} bi (2020), R$ {br(r.valor_empenhado[2021],1)} bi (2021), R$ {br(r.valor_empenhado[2022],1)} bi (2022); pago em 2023: R$ {br(r.valor_pago[2023],1)} bi.",
           codigo="M3")
    # c27 autor identificado
    g = em.groupby("t").apply(lambda d: pd.Series({"id": d[d.id_ator.notna()].valor_empenhado.sum(), "sem": d[d.id_ator.isna()].valor_empenhado.sum()}), include_groups=False).reindex(ORD) / 1e9
    R["p3_pct_empenhado_sem_parlamentar"] = round(float(em[em.id_ator.isna()].valor_empenhado.sum() / em.valor_empenhado.sum() * 100), 1)
    f, a = fig(2.9)
    y = np.arange(5)
    a.barh(y, g["id"], color=C["blue"], height=0.6, label="Parlamentar identificado")
    a.barh(y, g["sem"], left=g["id"], color=C["orange"], height=0.6, label="Sem parlamentar identificado")
    for i, (u, v) in enumerate(zip(g["id"], g["sem"])):
        a.text(u + v + 1, i, f"{br(u+v,0)} bi", va="center", fontsize=7.5)
    a.set_yticks(y); a.set_yticklabels(ORD, fontsize=7.5); a.invert_yaxis(); a.set_xlabel("R$ bilhões empenhados, 2014–2026 (nominais)")
    nogridy(a); a.legend(loc="lower right", fontsize=7.5); a.set_xlim(0, 150); a.set_title("Identificação do parlamentar no arquivo da CGU")
    salvar(f, "c27", titulo="Valor empenhado com e sem parlamentar identificado, por modalidade, 2014–2026",
           pergunta="Em que modalidades o arquivo público identifica o parlamentar autor?", periodo="2014–2026",
           unidade="R$ bilhões nominais empenhados", universo="Todas as linhas do arquivo de emendas da CGU",
           fonte_primaria=F_CGU_EMENDAS, tratamento="Ligação do autor publicado a parlamentar da base por nome e mandato no ano (D-029; 97,5% das linhas individuais com autor ligadas)",
           derivado="Valor com e sem ligação a parlamentar", limitacoes="Bancada e comissão não têm autor individual por desenho; a falta é da fonte, não da ligação",
           leitura=f"{br(R['p3_pct_empenhado_sem_parlamentar'],1)}% do valor empenhado no período não tem parlamentar identificado.", codigo="M6")
    tg = g.copy(); tg["% sem parlamentar"] = (tg["sem"] / (tg["id"] + tg["sem"]) * 100).round(1)
    tabela(tg.round(2).reset_index().rename(columns={"t": "Modalidade", "id": "Com parlamentar (R$ bi)", "sem": "Sem parlamentar (R$ bi)"}),
           "t_m6_autor", titulo="Valor empenhado com e sem parlamentar identificado, por modalidade", unidade="R$ bilhões nominais",
           periodo="2014–2026", universo="Arquivo de emendas da CGU", fonte=F_CGU_EMENDAS, notas="Ligação por nome e mandato (D-029).", codigo="M6")
    # c25 função
    fn = E.groupby("funcao").valor_pago.sum().sort_values(ascending=False) / 1e9
    tot = E.valor_pago.sum() / 1e9
    R["p3_saude_pct"] = round(float(fn.get("Saúde", 0) / tot * 100), 1)
    top = fn[fn.index != "Sem informação"].head(8).iloc[::-1]
    f, a = fig(3.2)
    a.barh(top.index, top.values, color=C["blue"], height=0.66)
    for i, v in enumerate(top.values):
        a.text(v + 1, i, f"{br(v,1)} ({br(v/tot*100,1)}%)", va="center", fontsize=7.5)
    a.set_xlim(0, top.max() * 1.35); a.set_xlabel("R$ bilhões pagos, 2017–2026 (nominais)"); nogridy(a); a.set_title("Emendas pagas por função orçamentária")
    salvar(f, "c25", titulo="Emendas pagas por função orçamentária, 2017–2026", pergunta="Para que áreas os recursos foram destinados?",
           periodo="2017–2026", unidade="R$ bilhões nominais e % do total pago", universo=U, fonte_primaria=F_CGU_EMENDAS,
           tratamento="Soma do pago por função", derivado="Total e parcela por função",
           limitacoes="Função declarada no orçamento, não uso efetivo; \"encargos especiais\" reúne transferências sem área definida",
           leitura=f"Saúde reúne {br(R['p3_saude_pct'],1)}% do valor pago.", codigo="M4")
    tf = (fn.head(12)).round(2).reset_index(); tf.columns = ["Função", "Pago (R$ bi)"]; tf["% do total"] = (tf["Pago (R$ bi)"] / tot * 100).round(1)
    tabela(tf, "t_m4_funcao", titulo="Emendas pagas por função", unidade="R$ bilhões nominais", periodo="2017–2026", universo=U,
           fonte=F_CGU_EMENDAS, notas="Função declarada.", codigo="M4")
    # per capita por UF
    pop = pd.read_csv(CUR / "ibge_populacao_uf.csv"); pop = pop[pop.ano == 2025].set_index("uf").populacao
    u = E.groupby("uf").valor_pago.sum()
    R["p3_pct_pago_sem_uf"] = round(float(u.reindex(["Múltiplo", "Sem informação"]).fillna(0).sum() / u.sum() * 100), 1)
    uu = u[u.index.isin(UF)]; uu.index = uu.index.map(UF)
    pc = (uu / pop).dropna().sort_values()
    R["p3_pc_max"] = (pc.index[-1], round(float(pc.iloc[-1]), 0)); R["p3_pc_min"] = (pc.index[0], round(float(pc.iloc[0]), 0))
    R["p3_pc_mediana"] = round(float(pc.median()), 0)
    f, a = fig(4.4)
    cores = [C["aqua"]] * len(pc)
    a.barh(pc.index, pc.values, color=cores, height=0.7)
    for i, v in enumerate(pc.values):
        a.text(v + 10, i, br(v, 0), va="center", fontsize=7)
    a.axvline(pc.median(), color=C["ink2"], lw=0.8, ls="--"); a.text(pc.median(), len(pc) - 0.2, " mediana", fontsize=7, color=C["ink2"])
    a.set_xlabel("R$ pagos por habitante, 2017–2026 (nominais acumulados; população de 2025)"); nogridy(a); a.tick_params(axis="y", labelsize=7)
    a.set_title("Emendas pagas por habitante, por UF")
    salvar(f, "n09", titulo="Emendas pagas por habitante, por unidade da federação, 2017–2026",
           pergunta="Como os recursos se distribuem entre os estados, considerando a população?",
           periodo="2017–2026 (acumulado)", unidade="R$ nominais acumulados por habitante (população estimada de 2025)",
           universo=U + f"; excluídos os {br(R['p3_pct_pago_sem_uf'],1)}% do valor pago sem UF definida (\"Múltiplo\" e \"Sem informação\")",
           fonte_primaria=F_CGU_EMENDAS + "; " + F_POP, tratamento="Soma do pago por UF de destino; divisão pela população de 2025 (D-070)",
           derivado="Valor por habitante", limitacoes="Valor nominal acumulado de anos diferentes; população de um só ano; UF de destino declarada na emenda",
           leitura=f"O valor por habitante vai de R$ {br(pc.iloc[0],0)} ({pc.index[0]}) a R$ {br(pc.iloc[-1],0)} ({pc.index[-1]}); mediana de R$ {br(pc.median(),0)}.",
           codigo="M4")
    tabela(pd.DataFrame({"UF": pc.index[::-1], "Pago 2017–2026 (R$ mi)": (uu.reindex(pc.index[::-1]) / 1e6).round(1).values,
                         "População 2025": pop.reindex(pc.index[::-1]).values, "R$ por habitante": pc.values[::-1].round(0)}),
           "t_m4_uf", titulo="Emendas pagas por UF, total e por habitante", unidade="R$ nominais", periodo="2017–2026",
           universo=U, fonte=F_CGU_EMENDAS + "; " + F_POP, notas="Excluído o valor sem UF definida.", codigo="M4")
    # concentração por autor (Lorenz) — emendas individuais com parlamentar
    ind = E[E.t.str.startswith("Individual") & E.id_ator.notna()]
    au = ind.groupby("id_ator").valor_pago.sum().sort_values(ascending=False)
    k = max(1, int(round(len(au) * 0.1)))
    R["p3_autores_n"] = int(len(au)); R["p3_autores_top10pct"] = round(float(au.head(k).sum() / au.sum() * 100), 1)
    R["p3_autores_gini"] = round(gini(au.values), 3)
    # concentração por mandato: autores com mandato no ano; normaliza por ano
    f, a = fig(3.0)
    s = np.sort(au.values); cum = np.concatenate([[0], np.cumsum(s) / s.sum()])
    a.plot(np.linspace(0, 100, len(cum)), cum * 100, color=C["violet"], lw=2)
    a.plot([0, 100], [0, 100], color=C["gray"], lw=0.8, ls="--")
    a.set_xlabel("% dos parlamentares autores (do menor ao maior valor pago)"); a.set_ylabel("% do valor pago acumulado")
    a.set_title("Concentração do valor pago entre autores de emendas individuais")
    salvar(f, "n10", titulo="Curva de concentração do valor pago entre parlamentares autores de emendas individuais, 2017–2026",
           pergunta="O valor das emendas individuais se concentra em poucos autores?", periodo="2017–2026 (acumulado)",
           unidade="% acumulado", universo=f"{len(au)} parlamentares com emenda individual paga e ligada (D-029)",
           fonte_primaria=F_CGU_EMENDAS, tratamento="Soma do pago por parlamentar; curva de Lorenz",
           derivado="Gini e parcela dos 10% maiores", limitacoes="Acumulado de anos diferentes: parlamentares com mais anos de mandato no período acumulam mais; a cota individual é igual por mandato",
           leitura=f"Os 10% de autores com maior valor pago somam {br(R['p3_autores_top10pct'],1)}% do total; Gini de {br(R['p3_autores_gini'],2)}.",
           codigo="M5")
    # Atlas: 30 maiores autores, com cargo e partido no último ano de emenda
    ult = ind.groupby("id_ator").ano.max()
    rows = []
    for i, v in au.head(30).items():
        y = int(ult[i]); pa = partido_na_data(f"{y}-07-01")
        rows.append(dict(Parlamentar=str(NOME_ATOR.get(i, i)).title(), **{"Partido (último ano com emenda)": SIGLA.get(pa.get(i), ""), "Último ano": y, "Pago 2017–2026 (R$ mi)": round(v / 1e6, 1)}))
    tabela(pd.DataFrame(rows), "atlas_autores_emendas", titulo="Parlamentares com maior valor pago em emendas individuais",
           unidade="R$ milhões nominais", periodo="2017–2026", universo="Emendas individuais com autor ligado a parlamentar da base",
           fonte=F_CGU_EMENDAS, notas="Valor pago acumulado; reflete tempo de mandato no período e regras de cota iguais por mandato; não mede influência nem uso dos recursos.", codigo="M5")
    # c28 por partido no ano da emenda, por parlamentar-ano
    ef = E[E.id_ator.notna()].copy()
    parts = []
    for y in ANOS:
        pa = partido_na_data(f"{y}-07-01"); x = ef[ef.ano == y].copy(); x["p"] = x.id_ator.map(pa).map(SIGLA); parts.append(x)
    ef = pd.concat(parts)
    gp = ef.groupby("p").agg(pago=("valor_pago", "sum"), parl_ano=("id_ator", lambda s: 0)).drop(columns="parl_ano")
    pa_n = ef.groupby(["p", "ano"]).id_ator.nunique().groupby("p").sum()
    gp["parl_ano"] = pa_n; gp["por_parl_ano"] = gp.pago / gp.parl_ano
    gp = gp.sort_values("pago", ascending=False).head(12)
    f, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 3.4), sharey=True)
    yy = np.arange(len(gp))[::-1]
    a1.barh(yy, gp.pago / 1e9, color=C["blue"], height=0.65); a2.barh(yy, gp.por_parl_ano / 1e6, color=C["aqua"], height=0.65)
    a1.set_yticks(yy); a1.set_yticklabels(gp.index); nogridy(a1); nogridy(a2)
    a1.set_xlabel("Total, R$ bi (nominal)", fontsize=7.5); a2.set_xlabel("Por parlamentar-ano, R$ mi", fontsize=7.5)
    a1.set_title("Emendas pagas por partido do autor no ano", fontsize=9)
    salvar(f, "c28", titulo="Emendas pagas por partido do autor no ano da emenda: total e por parlamentar-ano, 2017–2026",
           pergunta="Como o valor se distribui entre partidos, considerando o tamanho de cada bancada?", periodo="2017–2026",
           unidade="R$ nominais", universo="Linhas com autor ligado a parlamentar (individuais, sobretudo)",
           fonte_primaria=F_CGU_EMENDAS + "; " + F_CAMARA_REF, tratamento="Partido do autor em 1º de julho do ano da emenda (D-016); divisão pelo número de parlamentares-ano com emenda",
           derivado="Total e média por parlamentar-ano", limitacoes="Bancada, comissão e relator ficam fora (sem autor individual); diferenças por parlamentar refletem mais tipo de mandato (senador tem cota igual) que partido",
           leitura=f"Maiores totais: {', '.join(gp.index[:3])}; a média por parlamentar-ano varia pouco entre os partidos maiores.", codigo="M7")
    # c29 execução
    ex = (em.groupby("ano").valor_pago.sum() / em.groupby("ano").valor_empenhado.sum() * 100).reindex(ANOS)
    R["p3_execucao_pct"] = {int(y): round(float(v), 0) for y, v in ex.items()}
    f, a = fig(2.7)
    a.plot(ANOS, ex.values, color=C["blue"], lw=2, marker="o")
    for x0, v in ex.items():
        a.text(x0, v + 3, br(v, 0), ha="center", fontsize=7.5)
    a.set_ylim(0, 100); a.set_xticks(ANOS); a.set_ylabel("pago ÷ empenhado no ano (%)"); nogridx(a); a.set_title("Execução das emendas")
    salvar(f, "c29", titulo="Valor pago sobre valor empenhado no ano, 2017–2026", pergunta="Quanto do valor empenhado no ano foi pago?",
           periodo="2017–2026", unidade="%", universo="Arquivo de emendas da CGU", fonte_primaria=F_CGU_EMENDAS,
           tratamento="Divisão do pago pelo empenhado do ano", derivado="Razão de execução",
           limitacoes="O pago inclui restos a pagar de empenhos anteriores; anos recentes seguem em execução",
           leitura=f"A razão vai de {br(ex[2017],0)}% (2017) a {br(ex[2024],0)}% (2024).", codigo="M8")
    gravar_resultados(R)
    print({k: R[k] for k in ["p3_pct_despesa_total", "p3_autores_top10pct", "p3_pc_max", "p3_pc_min", "p3_pct_pago_sem_uf"]})


F_CAMARA_REF = "filiações da Câmara e do Senado (FNT-000001 a FNT-000006)"

if __name__ == "__main__":
    main()
