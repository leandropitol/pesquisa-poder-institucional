"""Parte IV, Justiça, competência e poder: ações penais no STF, TCU, TSE e CGU (análises J1-J10)."""
from __future__ import annotations

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from .comum import (C, F_CGU_SANCOES, F_STF, F_STF_MIN, F_TCU, F_TSE_CAND, NOME_ATOR, RAIZ, TAB, br, fig,
                    gravar_resultados, ler, nogridx, nogridy, salvar, tabela, F_ORIENT, F_IDEOL)

CATN = {"merito": "Julgamento de mérito", "declinio": "Declínio de competência", "extincao": "Extinção da punibilidade",
        "outro": "Outro encerramento", "em_tramitacao": "Em tramitação", "acordo": "Acordo"}
COL = {"merito": C["blue"], "declinio": C["orange"], "extincao": C["yellow"], "outro": C["gray"], "em_tramitacao": C["aqua"], "acordo": C["green"]}
U_AP = "Ações penais originárias do STF autuadas de 2003 em diante, da lista de D-048 (fora 8 de janeiro); grupo principal: ao menos um réu parlamentar federal com vínculo confirmado (D-065, D-068)"
TR_AP = "Classificação de um desfecho por ação pela hierarquia de D-068 (mérito > declínio > em tramitação > extinção > acordo > outro); tempo da autuação no STF ao desfecho"


def main() -> None:
    R = {}
    ac = pd.read_csv(TAB / "foro_acoes.csv")
    for c in ("autuacao", "data_desfecho"):
        ac[c] = pd.to_datetime(ac[c], errors="coerce")
    par = ac[ac.grupo == "com réu parlamentar"]
    R["p4_acoes_parl"] = int(len(par)); R["p4_acoes_demais"] = int((ac.grupo == "sem réu parlamentar ligado").sum())
    dist = par.categoria.value_counts(normalize=True) * 100
    for k, v in dist.items():
        R[f"p4_pct_{k}"] = round(float(v), 1)
    R["p4_origem_outra_instancia"] = int((par.origem == "vinda de outra instância").sum())
    R["p4_origem_stf"] = int((par.origem == "autuada no STF").sum())
    R["p4_coorte_pos2018"] = int((par.coorte != "até 2018-05-02").sum())
    tempos = pd.read_csv(TAB / "foro_tempos.csv")
    tp = tempos.set_index("grupo")
    R["p4_mediana_anos_parl"] = round(float(tp.loc["com réu parlamentar", "mediana_anos"]), 2)
    R["p4_mediana_anos_demais"] = round(float(tp.loc["sem réu parlamentar ligado", "mediana_anos"]), 2)
    R["p4_mais_5_anos"] = int((par.anos > 5).sum()); R["p4_mais_10_anos"] = int((par.anos > 10).sum())
    # c13 desfechos
    grp = [("com réu parlamentar", f"Com réu parlamentar ({len(par)})"), ("sem réu parlamentar ligado", f"Demais ações ({R['p4_acoes_demais']})")]
    f, a = fig(2.6)
    for k, (g, lab) in enumerate(grp):
        s = ac[ac.grupo == g].categoria.value_counts(normalize=True) * 100
        left = 0
        for c in ["merito", "declinio", "extincao", "acordo", "outro", "em_tramitacao"]:
            v = s.get(c, 0)
            if v == 0:
                continue
            a.barh(k, v, left=left, color=COL[c], height=0.55, edgecolor="white", linewidth=1.2, label=CATN[c])
            if v >= 5:
                a.text(left + v / 2, k, f"{br(v, 0)}%", ha="center", va="center", fontsize=8, color="white" if c in ("merito", "declinio") else C["ink"], fontweight="bold")
            left += v
    h, l = a.get_legend_handles_labels(); seen = {}
    for hh, ll in zip(h, l):
        seen.setdefault(ll, hh)
    a.legend(seen.values(), seen.keys(), ncol=3, loc="upper center", bbox_to_anchor=(0.45, -0.3), fontsize=7.5)
    a.set_yticks([0, 1]); a.set_yticklabels([g[1] for g in grp]); a.invert_yaxis(); a.set_xlim(0, 100); a.set_xlabel("% das ações"); nogridy(a)
    a.set_title("Desfecho das ações penais originárias no STF")
    salvar(f, "c13", titulo="Desfecho das ações penais originárias no STF, com e sem réu parlamentar, 2003–2026",
           pergunta="Como terminam, no STF, as ações penais contra parlamentares, comparadas às demais?",
           periodo="Ações autuadas de 2003 a 2026; situação em 23/09/2026", unidade="% das ações do grupo",
           universo=U_AP, fonte_primaria=F_STF, tratamento=TR_AP, derivado="Parcela por desfecho",
           limitacoes="O que acontece após o declínio (em outra instância) não é observado; categorias pela decisão registrada, não pela leitura da íntegra",
           leitura=f"Com réu parlamentar: {br(dist.get('merito',0),0)}% com julgamento de mérito, {br(dist.get('declinio',0),0)}% com declínio de competência, {br(dist.get('extincao',0),0)}% com extinção da punibilidade.",
           codigo="J1, J5")
    fd = pd.read_csv(TAB / "foro_desfechos.csv"); fd = fd[(fd.grupo == "com réu parlamentar") & (fd.acoes > 0)]
    tabela(pd.DataFrame({"Desfecho": fd.desfecho, "Ações": fd.acoes, "% do grupo": (fd.parcela * 100).round(1)}), "t_j1_desfechos",
           titulo="Desfechos das ações penais originárias com réu parlamentar", unidade="número de ações e %", periodo="2003–2026",
           universo=U_AP, fonte=F_STF, notas="Hierarquia de desfechos de D-068; situação em 23/09/2026.", codigo="J1")
    # c14 tempo (curva)
    f, a = fig(3.2)
    for g, lab, cl in [("com réu parlamentar", "Com réu parlamentar", C["blue"]), ("sem réu parlamentar ligado", "Demais ações", C["orange"])]:
        x = ac[(ac.grupo == g) & (ac.evento == 1)].anos.sort_values().values
        n = (ac.grupo == g).sum()
        a.step(x, np.arange(1, len(x) + 1) / n * 100, where="post", color=cl, lw=2, label=lab)
    a.axhline(50, color=C["gray"], ls="--", lw=1); a.set_xlim(0, 14); a.set_ylim(0, 101)
    a.set_xlabel("anos desde a autuação no STF"); a.set_ylabel("% das ações que já saíram do STF"); a.legend(loc="lower right"); nogridx(a)
    a.set_title("Tempo até a saída do STF, por qualquer desfecho")
    salvar(f, "c14", titulo="Proporção acumulada de ações que já tiveram desfecho no STF, por tempo desde a autuação",
           pergunta="Quanto tempo as ações penais permanecem no STF?", periodo="2003–2026", unidade="% acumulado das ações; anos",
           universo=U_AP, fonte_primaria=F_STF, tratamento=TR_AP + "; curva acumulada simples (as ações em tramitação ficam no denominador)",
           derivado="Mediana de tempo (Kaplan-Meier em D-068)", limitacoes="Ações ainda em tramitação são censuradas; a autuação no STF não é a data da denúncia",
           leitura=f"Mediana de {br(R['p4_mediana_anos_parl'],1)} anos para ações com réu parlamentar e {br(R['p4_mediana_anos_demais'],2)} ano para as demais; {R['p4_mais_5_anos']} ações com réu parlamentar passaram de 5 anos.",
           codigo="J1")
    lg = par.sort_values("anos", ascending=False).head(10)
    tabela(pd.DataFrame({"Ação": lg.ap, "Autuação no STF": lg.autuacao.dt.strftime("%Y-%m-%d"), "Desfecho": lg.categoria.map(CATN),
                         "Anos até o desfecho": lg.anos.round(1)}), "t_j1_longas", titulo="As dez ações penais com réu parlamentar de maior duração no STF",
           unidade="anos", periodo="2003–2026", universo=U_AP, fonte=F_STF, notas="Identificadas pelo número da ação; réus no Atlas apenas quando houve condenação.", codigo="J1")
    # c16 série anual + marcos
    sa = pd.read_csv(TAB / "foro_serie_anual.csv").set_index("ano")
    R["p4_declinios_ano"] = {int(y): int(v) for y, v in sa["declínio de competência"].items()}
    f, a = fig(3.4)
    bot = np.zeros(len(sa))
    m = {"julgamento de mérito": "merito", "declínio de competência": "declinio", "extinção da punibilidade sem mérito": "extincao", "outro encerramento": "outro"}
    for c, k in m.items():
        a.bar(sa.index, sa[c], bottom=bot, color=COL[k], label=CATN[k], width=0.72, edgecolor="white", linewidth=0.6)
        bot += sa[c].values
    a.scatter([2007, 2011, 2015, 2019, 2023], [-2.5] * 5, marker="^", color=C["ink2"], s=22, clip_on=False, zorder=4, label="Início de legislatura")
    a.axvline(2018, color=C["red"], lw=0.9, ls=":"); a.text(2018.15, bot.max() * 0.95, "restrição do foro\n(AP 937, mai/2018)", fontsize=6.5, color=C["red"])
    a.set_ylabel("ações com réu parlamentar (ano do desfecho)"); nogridx(a); a.legend(ncol=2, loc="upper left", fontsize=7); a.set_xticks(range(2003, 2027, 3))
    a.set_ylim(0, bot.max() * 1.25); a.set_title("Desfechos por ano")
    salvar(f, "c16", titulo="Ações penais com réu parlamentar por ano e tipo de desfecho, com marcos institucionais",
           pergunta="Em que anos as ações saem do STF, e por qual via?", periodo="2003–2026", unidade="número de ações",
           universo=U_AP, fonte_primaria=F_STF, tratamento=TR_AP, derivado="Contagem anual por desfecho",
           limitacoes="Os marcos são contexto temporal, não causa medida; o motivo de cada declínio (fim de mandato, restrição do foro, desmembramento) não é registrado",
           leitura=f"Declínios: {R['p4_declinios_ano'].get(2011)} em 2011, {R['p4_declinios_ano'].get(2015)} em 2015 e {R['p4_declinios_ano'].get(2018)} em 2018.",
           codigo="J4")
    # c15 status por pessoa por ano
    sd = pd.read_csv(TAB / "stf_desfechos.csv"); sd["data"] = pd.to_datetime(sd["data"], errors="coerce")
    R["p4_status_pessoa"] = {k: int(v) for k, v in sd.status.value_counts().items()}
    R["p4_status_pessoa_total"] = int(len(sd))
    mer = sd[sd.status.isin(["absolvido", "condenado_tribunal_superior"])]
    R["p4_pct_condenados_merito"] = round(float((mer.status == "condenado_tribunal_superior").mean() * 100), 1)
    pv = sd.pivot_table(index=sd.data.dt.year, columns="status", values="ap", aggfunc="count").fillna(0)
    pv = pv.reindex(range(int(pv.index.min()), int(pv.index.max()) + 1)).fillna(0)
    ST = {"absolvido": ("Absolvição", C["blue"]), "condenado_tribunal_superior": ("Condenação", C["red"]), "prescrito": ("Prescrição", C["yellow"]),
          "punibilidade_extinta": ("Outra extinção da punibilidade", C["gray"]), "denuncia_rejeitada": ("Denúncia rejeitada", C["aqua"])}
    f, a = fig(3.3)
    bot = np.zeros(len(pv))
    for c in ST:
        if c in pv:
            a.bar(pv.index, pv[c], bottom=bot, color=ST[c][1], label=ST[c][0], width=0.7, edgecolor="white", linewidth=0.8); bot += pv[c].values
    a.set_ylabel("parlamentares com desfecho registrado"); nogridx(a); a.legend(ncol=2, loc="upper right", fontsize=7); a.set_title("Desfecho por pessoa, por ano da decisão")
    salvar(f, "c15", titulo="Desfechos por pessoa nas ações penais com réu parlamentar, por ano da decisão",
           pergunta="Quando o STF decide sobre o réu parlamentar, qual é o resultado formal?", periodo=f"{int(pv.index.min())}–{int(pv.index.max())}",
           unidade="número de pares parlamentar x ação", universo=f"{len(sd)} status por pessoa e ação lidos no texto oficial das decisões (D-065, D-066)",
           fonte_primaria=F_STF, tratamento="Status formal do último registro por pessoa e ação; prescrição separada de outras extinções",
           derivado="Contagem anual por status", limitacoes="\"Condenação\" inclui procedência em parte; recursos posteriores e trânsito em julgado não foram lidos; 27 eventos pendentes",
           leitura=f"Entre os julgados no mérito, {br(R['p4_pct_condenados_merito'],1)}% tiveram condenação; prescrições somam {R['p4_status_pessoa'].get('prescrito',0)} registros.",
           codigo="J2, J5")
    tabela(pv.astype(int).rename(columns={k: v[0] for k, v in ST.items()}).reset_index().rename(columns={"data": "Ano"}), "t_j5_status_ano",
           titulo="Status por pessoa por ano da decisão", unidade="número de registros", periodo="2008–2023", universo="Status por pessoa e ação (D-065)",
           fonte=F_STF, notas="Prescrição não é absolvição; extinção da punibilidade não julga o mérito.", codigo="J5")
    # c17 distribuição política dos declínios
    g = pd.read_csv(TAB / "eixo3_foro_governo_periodo.csv"); g = g[(g.medida == "declinio") & (g.n_governo > 0)]
    teste = pd.read_csv(TAB / "eixo3_foro_testes.csv")
    pfis = float(teste[(teste.medida == "declinio") & (teste.recorte == "todas as ações") & teste.teste.str.contains("Fisher")].p_valor.iloc[0])
    R["p4_declinio_p_fisher"] = round(pfis, 3)
    f, a = fig(3.0)
    xx = np.arange(len(g))
    a.bar(xx - 0.2, g.taxa_governo * 100, 0.38, color=C["blue"], label="Réus de partidos alinhados ao governo")
    a.bar(xx + 0.2, g.taxa_oposicao * 100, 0.38, color=C["orange"], label="Réus de partidos de oposição")
    for i, (u, v, nu, no) in enumerate(zip(g.taxa_governo, g.taxa_oposicao, g.n_governo, g.n_oposicao)):
        a.text(i - 0.2, u * 100 + 1.5, f"{br(u*100,0)}%\nn={nu}", ha="center", fontsize=6.5); a.text(i + 0.2, v * 100 + 1.5, f"{br(v*100,0)}%\nn={no}", ha="center", fontsize=6.5)
    a.set_xticks(xx); a.set_xticklabels([p.replace(" e início do 2º mandato", "").replace(" (e Dilma até 11/05/2016)", "") for p in g.periodo], fontsize=7)
    a.set_ylim(0, 125); a.set_ylabel("% das ações com declínio"); nogridx(a); a.legend(loc="upper left", fontsize=7)
    a.set_title("Declínio de competência por alinhamento do partido do réu")
    salvar(f, "c17", titulo="Parcela de ações com declínio de competência, por alinhamento do partido do réu e período presidencial",
           pergunta="O declínio de competência se distribui de modo diferente entre réus de partidos alinhados e não alinhados ao governo?",
           periodo="Períodos presidenciais de 2003 a 2022", unidade="% das ações do grupo; n = ações",
           universo="Pares ação x réu parlamentar com vínculo confirmado e partido classificado (D-067)",
           fonte_primaria=F_STF + "; " + F_ORIENT,
           tratamento="Partido do réu na data da ação; grupo pela concordância com a orientação do governo em votações nominais da Câmara (D-050, D-051)",
           derivado=f"Taxa por grupo; teste exato de Fisher no período inteiro (p = {br(pfis,3)})",
           limitacoes="Nenhum período isolado tem diferença significativa; sem correção para comparações múltiplas; grupos de oposição pequenos; o motivo do declínio não é medido; alinhamento em votação não é participação na coalizão",
           leitura="A parcela é maior entre réus de oposição nos quatro períodos com os dois grupos, com amostras pequenas e intervalos sobrepostos.",
           codigo="J6")
    tabela(pd.DataFrame({"Período": g.periodo, "Ações (alinhados)": g.n_governo, "Com declínio (alinhados)": g.com_governo,
                         "% (alinhados)": (g.taxa_governo * 100).round(1), "Ações (oposição)": g.n_oposicao, "Com declínio (oposição)": g.com_oposicao,
                         "% (oposição)": (g.taxa_oposicao * 100).round(1), "p (Fisher)": g.p_fisher.round(3)}), "t_j6_declinio_grupo",
           titulo="Declínio de competência por alinhamento do partido do réu e período", unidade="ações, % e p-valor", periodo="2003–2022",
           universo="Pares ação x réu parlamentar (D-067)", fonte=F_STF + "; " + F_ORIENT,
           notas="Teste exato de Fisher bicaudal por período; sem correção para múltiplas comparações.", codigo="J6")
    # c18 STF
    sc = pd.read_csv(TAB / "stf_composicao.csv"); sc["ini"] = pd.to_datetime(sc.data_posse, errors="coerce")
    sc["fim"] = pd.to_datetime(sc.data_fim, errors="coerce").fillna(pd.Timestamp("2026-09-30")); sc = sc.sort_values("ini")
    R["p4_stf_ministros"] = int(len(sc)); R["p4_stf_por_presidente"] = {k: int(v) for k, v in sc.presidente.value_counts().items()}
    def pc(p):
        return {"Luiz Inácio Lula da Silva": C["blue"], "Dilma Rousseff": C["orange"], "Michel Temer": C["aqua"], "Jair Messias Bolsonaro": C["yellow"]}.get(p, C["gray"])
    f, a = fig(5.6)
    for i, (_, r) in enumerate(sc.iterrows()):
        a.barh(i, (r.fim - r.ini).days, left=mdates.date2num(r.ini), height=0.7, color=pc(r.presidente))
        a.text(mdates.date2num(r.fim) + 90, i, r.nome_guerra, va="center", fontsize=6.8)
    a.xaxis_date(); a.set_xlim(mdates.date2num(pd.Timestamp("1974-01-01")), mdates.date2num(pd.Timestamp("2033-01-01"))); a.invert_yaxis(); a.set_yticks([])
    a.xaxis.set_major_locator(mdates.YearLocator(10)); a.xaxis.set_major_formatter(mdates.DateFormatter("%Y")); nogridy(a)
    a.legend(handles=[Patch(color=C["blue"], label="Indicação de Lula"), Patch(color=C["orange"], label="Dilma Rousseff"), Patch(color=C["aqua"], label="Michel Temer"),
                      Patch(color=C["yellow"], label="Jair Bolsonaro"), Patch(color=C["gray"], label="Presidentes anteriores a 2003")], loc="lower left", fontsize=7.5)
    a.set_title("Composição do STF: posse, saída e presidente que indicou")
    salvar(f, "c18", titulo="Ministros do STF em exercício em algum dia desde 2003: posse, saída e presidente que indicou",
           pergunta="Como a composição do STF mudou ao longo do período?", periodo="1975–2026", unidade="datas de posse e de saída",
           universo=f"{len(sc)} ministros em exercício em algum dia desde 2003 (D-058)", fonte_primaria=F_STF_MIN,
           tratamento="Datas corrigidas onde as páginas tinham erro, com fonte (D-058); indicação pela mensagem presidencial",
           derivado="Tempo de permanência", limitacoes="Indicação não mede orientação do ministro; a cor identifica quem indicou, não comportamento",
           leitura=f"{len(sc)} ministros; indicações de Lula: {R['p4_stf_por_presidente'].get('Luiz Inácio Lula da Silva',0)}; Dilma Rousseff: {R['p4_stf_por_presidente'].get('Dilma Rousseff',0)}.",
           codigo="J7")
    sc["anos"] = ((sc.fim - sc.ini).dt.days / 365.25).round(1)
    nome_pres = lambda p: str(p).replace("Luiz Inácio Lula da Silva", "Lula").replace("Jair Messias Bolsonaro", "Jair Bolsonaro")
    tabela(pd.DataFrame({"Ministro": sc.nome_guerra, "Indicado por": sc.presidente.map(nome_pres), "Posse": sc.data_posse.astype(str).str[:10],
                         "Saída": sc.data_fim.fillna("em exercício").astype(str).str[:12], "Motivo da saída": sc.motivo_fim.fillna("—"), "Anos (até 30/09/2026)": sc.anos}),
           "t_j7_stf", titulo="Composição do STF desde 2003", unidade="datas e anos", periodo="1975–2026", universo="Ministros em exercício em algum dia desde 2003",
           fonte=F_STF_MIN, notas="Correções de datas documentadas em D-058; vagas divergentes entre mensagem e decreto registradas em limitacoes.md.", codigo="J7")
    # c19 relator (nota estatística)
    mrel = pd.read_csv(TAB / "eixo3_relator_ministros.csv"); mrel = mrel[mrel.grupo_tipo == "ministro"].sort_values("grupo")
    f, a = fig(4.0)
    yy = np.arange(len(mrel))
    a.hlines(yy, mrel.ic95_inf * 100, mrel.ic95_sup * 100, color=C["gray"], lw=2); a.scatter(mrel.taxa * 100, yy, color=C["ink2"], s=36, zorder=3, edgecolor="white")
    a.set_yticks(yy); a.set_yticklabels([f"n = {int(r.n_julgados)}" for _, r in mrel.iterrows()], fontsize=7.5); a.invert_yaxis()
    a.set_xlabel("% de condenação entre julgados no mérito, com intervalo de 95%"); nogridy(a); a.set_xlim(-2, 102)
    a.set_title("Amostras pequenas: intervalos de 95% por relator (sem nomes)")
    r2 = pd.read_csv(TAB / "eixo3_relator_2x2.csv").set_index("recorte")
    R["p4_relator_p"] = round(float(r2.loc["total", "p_fisher"]), 2)
    salvar(f, "c19", titulo="Exemplo de falsa precisão: taxa de condenação por relator com intervalos de 95%",
           pergunta="Por que comparações entre relatores não sustentam conclusões?", periodo="2003–2026",
           unidade="% e intervalo de Wilson", universo="93 julgamentos de mérito de parlamentares com ministro resolvido (D-067)",
           fonte_primaria=F_STF, tratamento="Taxa por ministro da decisão; intervalo de Wilson", derivado="Taxas e intervalos",
           limitacoes="Entre 2 e 12 casos por ministro; o relator vem de sorteio e o julgamento é colegiado",
           leitura=f"Os intervalos vão de quase 0% a mais de 80% para vários ministros; a comparação agregada entre indicados por presidentes do PT e por outros tem p = {br(R['p4_relator_p'],2)}.",
           codigo="J8")
    # TCU c20
    st = ler("status_pessoa_processo"); st["data"] = pd.to_datetime(st["data"], errors="coerce")
    tc = st[st.status == "contas_julgadas_irregulares"]
    R["p4_tcu_decisoes"] = int(len(tc)); R["p4_tcu_pessoas"] = int(tc.id_ator.nunique())
    by = tc.groupby(tc.data.dt.year).size()
    f, a = fig(2.8)
    a.bar(by.index, by.values, color=C["blue"], width=0.7); a.set_ylabel("decisões"); nogridx(a); a.set_xticks(range(int(by.index.min()), 2027, 3))
    a.set_title("Contas julgadas irregulares pelo TCU, por ano do trânsito em julgado")
    salvar(f, "c20", titulo="Decisões de contas julgadas irregulares pelo TCU envolvendo parlamentares e eleitos da base, por ano",
           pergunta="Com que frequência agentes políticos da base aparecem na lista de contas irregulares?", periodo=f"{int(by.index.min())}–2026",
           unidade="número de decisões", universo=f"{len(tc)} decisões sobre {tc.id_ator.nunique()} pessoas da base (D-064)", fonte_primaria=F_TCU,
           tratamento="Ligação pela candidatura no TSE (CPF usado só como chave e não guardado; D-064)", derivado="Contagem anual",
           limitacoes="A lista cobre a pessoa em qualquer função (sobretudo ex-prefeitos e gestores), não o mandato; o TCU pode rever decisões; conta irregular não é condenação penal",
           leitura=f"{len(tc)} decisões sobre {tc.id_ator.nunique()} pessoas.", codigo="J9")
    # candidaturas (eixo 1 ampliado, D-060/D-061)
    et = pd.read_csv(TAB / "eixo1_taxas.csv"); et = et[et.grupo_tipo == "governo_oposicao"]
    s = et.groupby(["medida", "anos", "universo"])[["n", "com_registro"]].sum().reset_index()
    s = s[s.medida.isin(["tse_indeferimento", "tcu_ate_eleicao"])]
    s["taxa_%"] = (s.com_registro / s.n * 100).round(2)
    s["medida"] = s.medida.map({"tse_indeferimento": "Candidatura indeferida ou cassada por motivo do eixo 1 (TSE)", "tcu_ate_eleicao": "Conta julgada irregular no TCU até o 1º turno"})
    R["p4_tse_indef_todos"] = s[(s.anos == "todos") & s.medida.str.startswith("Candidatura") & (s.universo == "candidatos")][["n", "com_registro"]].iloc[0].astype(int).tolist()
    R["p4_tcu_cand_todos"] = s[(s.anos == "todos") & s.medida.str.startswith("Conta") & (s.universo == "candidatos")][["n", "com_registro"]].iloc[0].astype(int).tolist()
    tabela(s.rename(columns={"medida": "Medida", "anos": "Eleição", "universo": "Universo", "n": "Candidaturas", "com_registro": "Com registro", "taxa_%": "%"}),
           "t_j9_candidaturas", titulo="Candidaturas com indeferimento por motivo do eixo 1 e com contas irregulares no TCU",
           unidade="candidaturas e %", periodo="Eleições gerais de 2010 a 2022 (TSE: 2018 e 2022)", universo="Candidaturas a presidente, governador, senador e deputado federal (D-060)",
           fonte=F_TSE_CAND + "; " + F_TCU, notas="O TSE não publica motivos de 2010, e 2014 tem 10 linhas; casos de lista (cota de gênero) excluídos (D-061); CPF só como chave.", codigo="J9")
    # c21 sanções
    ev = ler("eventos"); ev["data"] = pd.to_datetime(ev["data"], errors="coerce")
    san = ev[ev.tipo_evento == "sancao_administrativa"]; le = ev[ev.tipo_evento == "acordo_leniencia"]
    sy = san.groupby(san.data.dt.year).size().reindex(range(2015, 2027)).fillna(0); ly = le.groupby(le.data.dt.year).size().reindex(range(2015, 2027)).fillna(0)
    R["p4_sancoes_total"] = int(len(san)); R["p4_leniencias_total"] = int(len(le)); R["p4_sancoes_ano"] = {int(k): int(v) for k, v in sy.items()}
    f, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 2.9))
    a1.bar(sy.index, sy.values, color=C["blue"], width=0.7); a1.set_title("Sanções a empresas no cadastro (registro)", fontsize=8.5)
    a2.bar(ly.index, ly.values, color=C["orange"], width=0.7); a2.set_title("Acordos de leniência (data de registro)", fontsize=8.5)
    for a in (a1, a2):
        nogridx(a); a.set_xticks(range(2015, 2027, 2)); a.tick_params(labelsize=7.5)
    salvar(f, "c21", titulo="Sanções administrativas a empresas e acordos de leniência registrados pela CGU, por ano",
           pergunta="Como evoluiu o registro de sanções e acordos com empresas?", periodo="2015–2026", unidade="número de registros",
           universo="CNEP inteiro (pessoas jurídicas); CEIS só de empresas já na base; 57 acordos de leniência (D-027)",
           fonte_primaria=F_CGU_SANCOES, tratamento="Contagem anual pela data de registro", derivado="Série anual",
           limitacoes="A série mede também a adesão de órgãos ao cadastro e a aplicação da Lei 12.846/2013; não mede quantidade de infrações",
           leitura=f"{len(san)} sanções e {len(le)} acordos de leniência; {int(sy.get(2015,0))} sanção em 2015 e {int(sy.get(2025,0))} em 2025.", codigo="J10")
    gravar_resultados(R)
    print({k: R[k] for k in ["p4_pct_merito", "p4_pct_declinio", "p4_mediana_anos_parl", "p4_tcu_decisoes", "p4_tse_indef_todos"]})


if __name__ == "__main__":
    main()
