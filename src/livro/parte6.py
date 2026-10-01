"""Parte VI, O Brasil no sistema internacional: réguas de democracia, votos, crédito, comércio e acordos (X1-X7)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from .comum import (C, F_BNDES, F_COMEX, F_FH, F_ITAMARATY, F_ONU, F_VDEM, NOME_INS, TAB, br, fig, gravar_resultados,
                    ler, nogridx, nogridy, salvar, tabela)

NP = {"IRN": "Irã", "RUS": "Rússia", "SYR": "Síria", "ISR": "Israel", "VEN": "Venezuela", "MMR": "Mianmar", "PRK": "Coreia do Norte",
      "BLR": "Belarus", "NIC": "Nicarágua", "AGO": "Angola", "ARG": "Argentina", "DOM": "Rep. Dominicana", "ECU": "Equador", "CUB": "Cuba",
      "MOZ": "Moçambique", "PER": "Peru", "GTM": "Guatemala", "GHA": "Gana", "HND": "Honduras", "MEX": "México", "USA": "Estados Unidos",
      "DEU": "Alemanha", "URY": "Uruguai", "BOL": "Bolívia", "PRY": "Paraguai", "FRA": "França", "PRT": "Portugal", "GBR": "Reino Unido", "CHN": "China"}
GOV = ["Lula 1", "Lula 2", "Dilma 1", "Dilma 2", "Temer", "Bolsonaro", "Lula 3"]
AMERICAS = set("ARG BOL BRA CHL COL ECU GUY PRY PER SUR URY VEN MEX GTM HND SLV NIC CRI PAN CUB DOM HTI JAM TTO BHS BRB BLZ USA CAN GRD LCA VCT DMA ATG KNA".split())
AFRICA = set("AGO MOZ GHA ZAF NGA SEN CPV GNB STP KEN TZA ETH ZMB ZWE CMR CIV GAB COG COD MAR DZA TUN EGY LBY SDN MRT MLI BFA NER TCD GIN SLE LBR TGO BEN NAM BWA MWI UGA RWA BDI MDG".split())


def main() -> None:
    R = {}
    # réguas
    q = ler("qualidade_democratica")
    b = q[q.pais_iso3 == "BRA"].pivot_table(index="ano", columns="indice", values="valor", aggfunc="first")
    ldi = pd.to_numeric(b.vdem_ldi, errors="coerce"); fht = pd.to_numeric(b.fh_total, errors="coerce")
    R["p6_ldi"] = {int(k): round(float(v), 2) for k, v in ldi.dropna().items()}; R["p6_fh_total"] = {int(k): int(v) for k, v in fht.dropna().items()}
    f, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 3.0))
    a1.plot(ldi.index, ldi.values, color=C["blue"], lw=2.2); a1.set_ylim(0.4, 0.9); a1.set_title("V-Dem: democracia liberal (0 a 1)", fontsize=8.5)
    for y in (2014, 2019, 2022, 2024):
        a1.scatter([y], [ldi[y]], color=C["blue"], s=22, zorder=3); a1.text(y, ldi[y] + 0.03, br(ldi[y], 2), ha="center", fontsize=7.5)
    a2.plot(fht.dropna().index, fht.dropna().values, color=C["orange"], lw=2.2, marker="o", ms=3); a2.set_ylim(60, 90); a2.set_title("Freedom House: pontuação (0 a 100)", fontsize=8.5)
    for y in (2012, 2016, 2019, 2024):
        a2.text(y, fht[y] + 1.3, str(int(fht[y])), ha="center", fontsize=7.5)
    for a in (a1, a2):
        nogridx(a); a.tick_params(labelsize=7.5)
    salvar(f, "c35", titulo="O Brasil em duas réguas de qualidade democrática: V-Dem (democracia liberal) e Freedom House (pontuação total)",
           pergunta="Como as duas réguas internacionais avaliam o Brasil ao longo do período?", periodo="V-Dem 2000–2025; Freedom House 2012–2024",
           unidade="índice de 0 a 1 (V-Dem LDI); pontos de 0 a 100 (Freedom House)", universo="Brasil", fonte_primaria=F_VDEM + "; " + F_FH,
           tratamento="Leitura das variáveis v2x_libdem e pontuação total; ano = ano avaliado (D-018)", derivado="Nenhum (valores da fonte)",
           limitacoes="Avaliações de especialistas com metodologias próprias; V-Dem com incerteza de modelo (intervalos não importados); Freedom House sem 2025",
           leitura=f"V-Dem: {br(ldi[2014],2)} (2014), {br(ldi[2019],2)} (2019), {br(ldi[2022],2)} (2022), {br(ldi[2024],2)} (2024); Freedom House: {int(fht[2012])} (2012) e {int(fht[2024])} (2024).",
           codigo="X6")
    fs = q[q.indice == "fh_status"].pivot_table(index="ano", columns="valor", values="pais_iso3", aggfunc="count").loc[2002:2024]
    R["p6_fh_nf"] = {int(k): int(v) for k, v in fs.NF.items()}; R["p6_fh_f"] = {int(k): int(v) for k, v in fs.F.items()}
    f, a = fig(3.0)
    bot = np.zeros(len(fs))
    for k, l, cl in [("F", "Livres", C["blue"]), ("PF", "Parcialmente livres", C["yellow"]), ("NF", "Não livres", C["red"])]:
        a.bar(fs.index, fs[k], bottom=bot, color=cl, label=l, width=0.78, edgecolor="white", linewidth=0.5); bot += fs[k].values
    a.set_ylabel("países"); nogridx(a); a.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12)); a.set_xticks(range(2002, 2025, 4))
    a.set_title("Países por status na Freedom House")
    salvar(f, "c36", titulo="Número de países por status na Freedom House, 2002–2024", pergunta="Em que contexto mundial se deu a trajetória brasileira?",
           periodo="2002–2024", unidade="número de países", universo="Países e territórios avaliados em cada ano", fonte_primaria=F_FH,
           tratamento="Contagem por status", derivado="Contagem", limitacoes="O número de avaliados varia por ano",
           leitura=f"Não livres: {int(fs.NF[2006])} (2006) e {int(fs.NF[2024])} (2024); livres: {int(fs.F[2006])} e {int(fs.F[2024])}.", codigo="X7")
    # divergência entre réguas (BQD)
    st = q[q.indice == "fh_status"][["pais_iso3", "ano", "valor"]].rename(columns={"valor": "fh"})
    rw = q[q.indice == "vdem_row"][["pais_iso3", "ano", "valor"]].rename(columns={"valor": "row"})
    m = st.merge(rw, on=["pais_iso3", "ano"])
    m["bqd_fh"] = m.fh == "NF"; m["bqd_v"] = pd.to_numeric(m.row, errors="coerce").isin([0, 1])
    agr = (m.bqd_fh == m.bqd_v).mean() * 100
    R["p6_concordancia_reguas_pct"] = round(float(agr), 1); R["p6_pares_reguas"] = int(len(m))
    so_v = m[~m.bqd_fh & m.bqd_v]
    R["p6_diverg_so_vdem"] = int(len(so_v)); R["p6_diverg_so_fh"] = int((m.bqd_fh & ~m.bqd_v).sum())
    R["p6_diverg_so_vdem_pf_pct"] = round(float((so_v.fh == "PF").mean() * 100), 1)
    dv = m.groupby("ano").apply(lambda d: pd.Series({"so_fh": int((d.bqd_fh & ~d.bqd_v).sum()), "so_vdem": int((~d.bqd_fh & d.bqd_v).sum())}), include_groups=False)
    f, a = fig(2.8)
    a.bar(dv.index, dv.so_vdem, color=C["blue"], width=0.75, label="Baixa qualidade só pelo V-Dem")
    a.bar(dv.index, dv.so_fh, bottom=dv.so_vdem, color=C["orange"], width=0.75, label="Baixa qualidade só pela Freedom House")
    a.set_ylabel("países"); nogridx(a); a.set_ylim(0, 55); a.legend(fontsize=7.5, loc="upper right"); a.set_title("Países em que as réguas discordam, por ano")
    salvar(f, "n17", titulo="Países classificados como de baixa qualidade democrática por uma régua e não pela outra, 2000–2024",
           pergunta="Em quantos casos a escolha da régua muda a classificação?", periodo="2000–2024", unidade="número de países",
           universo=f"{len(m)} pares país-ano com as duas réguas", fonte_primaria=F_VDEM + "; " + F_FH,
           tratamento="Baixa qualidade: Não Livre (FH) ou autocracia fechada ou eleitoral (V-Dem RoW 0 ou 1) (D-003, D-053)", derivado="Concordância e divergências",
           limitacoes="Limiares fixados pelo protocolo; outros cortes dariam outros números", leitura=f"As réguas concordam em {br(agr,1)}% dos pares; o V-Dem classifica mais países como de baixa qualidade do que a Freedom House.",
           codigo="X6, X7")
    # votos
    v = pd.read_csv(TAB / "eixo2_votos_por_resolucao.csv"); esc = v[v.tipo == "escrutinio"]
    cnt = esc[esc.alvo_iso3.isin(NP)].groupby(["alvo_iso3", "voto_brasil"]).size().unstack(fill_value=0)
    cnt["t"] = cnt.sum(axis=1); cnt = cnt.sort_values("t", ascending=False).head(8).iloc[::-1]
    allc = esc[esc.alvo_iso3.isin(["IRN", "RUS", "ISR"])].groupby(["alvo_iso3", "voto_brasil"]).size().unstack(fill_value=0)
    for iso in ["IRN", "RUS", "ISR"]:
        R[f"voto_{iso}"] = {k: int(allc.loc[iso].get(k, 0)) for k in ["sim", "abstencao", "nao", "consenso"]}
        R[f"voto_{iso}_total"] = int(allc.loc[iso].sum())
    R["p6_votos_pais"] = {NP[i]: {k: int(cnt.loc[i].get(k, 0)) for k in ["sim", "abstencao", "nao", "consenso"]} for i in cnt.index}
    f, a = fig(3.4)
    left = np.zeros(len(cnt))
    cl = {"sim": C["blue"], "abstencao": C["yellow"], "nao": C["red"], "consenso": C["gray"]}; lb = {"sim": "Sim", "abstencao": "Abstenção", "nao": "Não", "consenso": "Consenso"}
    for k in ["sim", "abstencao", "nao", "consenso"]:
        if k in cnt:
            a.barh([NP[i] for i in cnt.index], cnt[k], left=left, color=cl[k], label=lb[k], height=0.66, edgecolor="white", linewidth=1)
            for i, x in enumerate(cnt[k]):
                if x >= 2:
                    a.text(left[i] + x / 2, i, str(int(x)), ha="center", va="center", fontsize=8, color="white" if k in ("sim", "nao") else C["ink"], fontweight="bold")
            left += cnt[k].values
    a.set_xlim(0, left.max() * 1.08); a.set_xlabel("votações de escrutínio sobre o país, ONU e OEA, 2003–2025"); nogridy(a)
    a.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.2), fontsize=7.5); a.set_title("Voto do Brasil nas resoluções sobre cada país")
    salvar(f, "c30", titulo="Voto do Brasil em resoluções de escrutínio sobre países específicos, por país alvo, 2003–2025",
           pergunta="Como o Brasil votou nas resoluções que avaliam a situação de direitos humanos ou de democracia de um país?",
           periodo="2003–2025", unidade="número de votações", universo="Resoluções de escrutínio selecionadas na ONU (AG e CDH) e na OEA (D-031, D-044, D-053)",
           fonte_primaria=F_ONU, tratamento="País alvo pelo título; nas resoluções sobre território ocupado, a potência ocupante (D-053)", derivado="Contagem por voto",
           limitacoes="Amostra temática; o Brasil só vota no CDH quando é membro; resoluções sem votação não geram voto",
           leitura="Irã e Rússia concentram abstenções; Síria, Mianmar, Belarus e Coreia do Norte concentram votos favoráveis.", codigo="X1")

    # c30b matriz período × país
    esc2 = esc.copy()
    esc2["g"] = esc2.governo.str.replace("Luiz Inácio Lula da Silva", "Lula", regex=False).str.replace("Jair Messias Bolsonaro", "Bolsonaro", regex=False).str.replace("Michel Temer", "Temer", regex=False).str.replace("Dilma Rousseff", "Dilma", regex=False)
    gord = list(dict.fromkeys(esc2.sort_values("data").g)) if "data" in esc2 else sorted(esc2.g.unique())
    paises = ["IRN", "RUS", "SYR", "ISR", "VEN", "PRK"]
    f, a = fig(3.3)
    mp = {"sim": C["blue"], "abstencao": C["yellow"], "nao": C["red"]}
    for i, gg in enumerate(gord):
        for j, p_ in enumerate(paises):
            x_ = esc2[(esc2.g == gg) & (esc2.alvo_iso3 == p_)]
            if len(x_) == 0:
                a.add_patch(plt.Rectangle((j, i), 1, 1, color="#f2f1ee", ec="white", lw=2)); continue
            s_ = x_.voto_brasil.value_counts(); dom = s_.idxmax()
            a.add_patch(plt.Rectangle((j, i), 1, 1, color=mp.get(dom, C["gray"]), ec="white", lw=2))
            a.text(j + 0.5, i + 0.5, f"{s_.get('sim',0)}/{s_.get('abstencao',0)}/{s_.get('nao',0)}", ha="center", va="center", fontsize=7, color="white" if dom != "abstencao" else C["ink"])
    a.set_xlim(0, len(paises)); a.set_ylim(0, len(gord)); a.invert_yaxis(); a.set_xticks(np.arange(len(paises)) + 0.5); a.set_xticklabels([NP[p_] for p_ in paises], fontsize=7.5); a.xaxis.tick_top()
    a.set_yticks(np.arange(len(gord)) + 0.5); a.set_yticklabels(gord, fontsize=7.5); a.grid(False); [s_.set_visible(False) for s_ in a.spines.values()]
    a.legend(handles=[Patch(color=C["blue"], label="Sim predominante"), Patch(color=C["yellow"], label="Abstenção predominante"), Patch(color=C["red"], label="Não predominante"), Patch(color="#f2f1ee", label="Sem votação")],
             ncol=2, loc="upper center", bbox_to_anchor=(0.5, 0.0), fontsize=7)
    a.set_title("Voto predominante por período e país (sim/abstenção/não)", pad=24)
    salvar(f, "c30b", titulo="Voto predominante do Brasil por período presidencial e país alvo, com contagem de sim, abstenção e não",
           pergunta="A posição sobre cada país mudou entre períodos?", periodo="2003–2025", unidade="votações (sim/abstenção/não)",
           universo="Resoluções de escrutínio sobre seis países", fonte_primaria=F_ONU, tratamento="Contagem por período e país", derivado="Voto predominante",
           limitacoes="Poucas votações por célula; ausência de votação depende da agenda e da participação no CDH",
           leitura="A abstenção sobre o Irã aparece em todos os períodos; o voto sobre a Rússia passa a existir a partir de 2016; o único \"não\" predominante é sobre Israel em um período.", codigo="X1")
    tabela(cnt.reset_index().assign(alvo_iso3=lambda d: d.alvo_iso3.map(NP)).rename(columns={"alvo_iso3": "País alvo", "sim": "Sim", "abstencao": "Abstenção", "nao": "Não", "consenso": "Consenso", "t": "Total"}),
           "t_x1_pais", titulo="Voto do Brasil em resoluções de escrutínio, por país alvo", unidade="votações", periodo="2003–2025",
           universo="Resoluções de escrutínio (D-053)", fonte=F_ONU, notas="Amostra temática.", codigo="X1")
    vg = pd.read_csv(TAB / "eixo2_votos_por_governo.csv")
    fh = vg[vg.recorte.str.contains("FH")].reset_index(drop=True); vd = vg[vg.recorte.str.contains("V-Dem")].reset_index(drop=True)
    R["p6_sim_fh"] = dict(zip(GOV, (fh.parcela_sim_brasil * 100).round(1))); R["p6_sim_vdem"] = dict(zip(GOV, (vd.parcela_sim_brasil * 100).round(1)))
    f, a = fig(3.3)
    x = np.arange(7)
    a.plot(x, fh.parcela_sim_brasil * 100, color=C["blue"], lw=2.2, marker="o", label="Brasil, régua Freedom House")
    a.plot(x, vd.parcela_sim_brasil * 100, color=C["blue"], lw=1.4, ls="--", marker="s", ms=4, label="Brasil, régua V-Dem")
    a.plot(x, fh.media_sim_democracias * 100, color=C["gray"], lw=1.8, marker="o", ms=4, label="Média das democracias")
    a.plot(x, fh.media_sim_america_latina * 100, color=C["orange"], lw=1.8, marker="o", ms=4, label="Média da América Latina")
    for i, vv in enumerate(fh.parcela_sim_brasil):
        a.text(i, vv * 100 - 8, f"{br(vv*100,0)}%", ha="center", fontsize=7.5, color=C["blue"], fontweight="bold")
    a.set_xticks(x); a.set_xticklabels(GOV); a.set_ylim(0, 100); a.set_ylabel('% de votos "sim"'); nogridx(a); a.legend(fontsize=7, loc="lower left", ncol=2)
    a.set_title("Votos \"sim\" sobre países de baixa qualidade democrática")
    salvar(f, "c31", titulo="Parcela de votos favoráveis do Brasil em resoluções de escrutínio sobre países de baixa qualidade democrática, por período presidencial",
           pergunta="A posição do Brasil nessas resoluções variou entre períodos, e em relação a outros países?", periodo="2003–2025, por período presidencial",
           unidade='% de votos "sim"', universo="Resoluções de escrutínio sobre países classificados como de baixa qualidade democrática no ano (D-053)",
           fonte_primaria=F_ONU + "; " + F_VDEM + "; " + F_FH, tratamento="Classificação do alvo por cada régua; médias de democracias e da América Latina nas mesmas resoluções",
           derivado="Parcela de sim por período e régua", limitacoes="Número de resoluções varia por período e pela participação do Brasil no CDH; período não é causa",
           leitura=f"Pela Freedom House: {br(fh.parcela_sim_brasil.iloc[2]*100,1)}% em Dilma 1 e {br(fh.parcela_sim_brasil.iloc[6]*100,1)}% em Lula 3; pelo V-Dem, {br(vd.parcela_sim_brasil.iloc[6]*100,1)}% em Lula 3.",
           codigo="X2")
    tabela(pd.DataFrame({"Período": GOV, "Sim (FH)": (fh.parcela_sim_brasil * 100).round(1), "Sim (V-Dem)": (vd.parcela_sim_brasil * 100).round(1),
                         "Média das democracias (FH)": (fh.media_sim_democracias * 100).round(1), "Média da América Latina (FH)": (fh.media_sim_america_latina * 100).round(1)}),
           "t_x2_periodo", titulo="Votos favoráveis do Brasil por período e régua", unidade="%", periodo="2003–2025", universo="D-053",
           fonte=F_ONU + "; " + F_VDEM + "; " + F_FH, notas="As réguas divergem sobretudo no período iniciado em 2023.", codigo="X2")
    # BNDES
    bn = ler("operacoes_exportacao_bndes"); bn["data"] = pd.to_datetime(bn.data_contratacao, errors="coerce"); bn["ano"] = bn.data.dt.year
    bv = bn[bn.valor.notna()]
    R["p6_bndes_ops"] = int(len(bn)); R["p6_bndes_ops_valor"] = int(len(bv)); R["p6_bndes_valor_total_bi"] = round(float(bv.valor.sum() / 1e9), 2)
    pais = bv.groupby("pais_iso3").valor.sum().sort_values(ascending=False).head(8) / 1e9
    f, a = fig(2.9)
    a.barh([NP.get(k, k) for k in pais.index][::-1], pais.values[::-1], color=C["blue"], height=0.66)
    for i, vv in enumerate(pais.values[::-1]):
        a.text(vv + 0.05, i, f"{br(vv,2)}", va="center", fontsize=8)
    a.set_xlim(0, pais.max() * 1.25); a.set_xlabel("US$ bilhões contratados (só serviços de engenharia, 1998–2015)"); nogridy(a); a.set_title("Destinos do crédito do BNDES a serviços de engenharia")
    salvar(f, "c08", titulo="Valor contratado em operações de pós-embarque de serviços de engenharia do BNDES, por país de destino, 1998–2015",
           pergunta="Para onde foram as exportações de serviços de engenharia financiadas pelo BNDES?", periodo="1998–2015 (não há operação desse tipo depois de 2015)",
           unidade="US$ bilhões nominais", universo=f"{len(bv)} linhas com valor (de {len(bn)}); bens sem valor publicado", fonte_primaria=F_BNDES,
           tratamento="Soma do valor contratado por país", derivado="Total por destino", limitacoes="Valor contratado, não desembolsado; condições e garantias fora da base",
           leitura=f"Total com valor: US$ {br(bv.valor.sum()/1e9,1)} bi; maiores destinos: {', '.join(NP.get(k,k) for k in pais.index[:3])}.", codigo="X3")
    ex = bv.groupby("id_exportadora").valor.sum().sort_values(ascending=False) / 1e9
    R["p6_bndes_top5_pct"] = round(float(ex.head(5).sum() / ex.sum() * 100), 1)
    e6 = ex.head(6).iloc[::-1]
    f, a = fig(2.7)
    NM = {"INS-000108": "CNO (Construtora Norberto Odebrecht)", "INS-000107": "Andrade Gutierrez", "INS-000121": "Companhia de Obras e Infraestrutura",
          "INS-000118": "Queiroz Galvão", "INS-000115": "Camargo Corrêa", "INS-000119": "Coesa"}
    a.barh([NM.get(i, str(NOME_INS.get(i, i)).title()) for i in e6.index], e6.values, color=C["violet"], height=0.64)
    for i, vv in enumerate(e6.values):
        a.text(vv + 0.1, i, br(vv, 2), va="center", fontsize=8)
    a.set_xlim(0, e6.max() * 1.25); a.set_xlabel("US$ bilhões contratados (serviços de engenharia)"); nogridy(a); a.set_title("Exportadoras com maior valor financiado")
    salvar(f, "c32", titulo="Exportadoras de serviços de engenharia com maior valor contratado no BNDES, 1998–2015",
           pergunta="Quantas empresas concentram o crédito?", periodo="1998–2015", unidade="US$ bilhões nominais", universo="Operações de serviços de engenharia com valor",
           fonte_primaria=F_BNDES, tratamento="Soma por exportadora (CNPJ, D-030)", derivado="Total e concentração",
           limitacoes="Empresas, não pessoas; o BNDES não publica o mutuário (governo ou empresa estrangeira)",
           leitura=f"As cinco maiores exportadoras somam {br(R['p6_bndes_top5_pct'],1)}% do valor.", codigo="X3")
    def reg(i):
        return "América Latina e Caribe" if i in AMERICAS and i not in ("USA", "CAN") else ("África" if i in AFRICA else ("Sem país" if pd.isna(i) or i in ("", "DIV") else "Outros"))
    bn["reg"] = bn.pais_iso3.map(reg)
    by = bn.groupby(["ano", "reg"]).size().unstack(fill_value=0).reindex(range(1998, 2027), fill_value=0)
    R["p6_bndes_ops_ano"] = {int(k): int(v) for k, v in by.sum(axis=1).items()}
    f, a = fig(2.9)
    bot = np.zeros(len(by))
    for k, c in [("América Latina e Caribe", C["blue"]), ("África", C["orange"]), ("Outros", C["aqua"]), ("Sem país", C["gray"])]:
        if k in by:
            a.bar(by.index, by[k], bottom=bot, color=c, label=k, width=0.75); bot += by[k].values
    a.set_ylabel("operações contratadas"); nogridx(a); a.legend(fontsize=7, loc="upper left"); a.set_xticks(range(1998, 2027, 4)); a.set_title("Operações de exportação do BNDES por ano e região de destino")
    salvar(f, "n18", titulo="Número de operações de exportação pós-embarque do BNDES (bens e serviços) por ano de contratação e região de destino",
           pergunta="O ritmo do crédito à exportação mudou ao longo do período?", periodo="1998–2026", unidade="número de linhas (subcréditos)",
           universo=f"{len(bn)} linhas de pós-embarque", fonte_primaria=F_BNDES, tratamento="Contagem por ano; região pelo país de destino",
           derivado="Contagem", limitacoes="Contagem não mede valor (bens sem valor publicado); linhas são subcréditos de operações",
           leitura="A contagem mostra a distribuição no tempo e por região; para valor, ver o gráfico de destinos.", codigo="X3")
    bg = pd.read_csv(TAB / "eixo2_bndes_por_governo.csv")
    tabela(pd.DataFrame({"Período": bg.governo, "Operações": bg.n_operacoes, "% em países de baixa qualidade (FH)": (bg.parcela_operacoes_bqd_fh * 100).round(1),
                         "% (V-Dem)": (bg.parcela_operacoes_bqd_vdem * 100).round(1), "Principais destinos": bg.principais_destinos_por_operacoes}),
           "t_x3_periodo", titulo="Operações de exportação do BNDES por período presidencial", unidade="operações e %", periodo="1998–2026",
           universo="Pós-embarque (D-021)", fonte=F_BNDES, notas="Classificação do destino no ano da contratação (D-053).", codigo="X3")
    # comércio, com e sem China
    cm = pd.read_csv(TAB / "eixo2_comercio_por_governo.csv")
    china = cm.principais_destinos_bqd_fh.str.extract(r"CHN ([\d\.]+)%")[0].astype(float) / 100
    sem = (cm.parcela_exportacoes_bqd_fh - china) / (1 - china)
    R["p6_bqd_fh"] = dict(zip(GOV, (cm.parcela_exportacoes_bqd_fh * 100).round(1))); R["p6_china"] = dict(zip(GOV, (china * 100).round(1)))
    R["p6_bqd_sem_china"] = dict(zip(GOV, (sem * 100).round(1)))
    f, a = fig(3.2)
    x = np.arange(7)
    a.plot(x, cm.parcela_exportacoes_bqd_fh * 100, color=C["blue"], lw=2.2, marker="o", label="Todos os países de baixa qualidade (FH)")
    a.plot(x, china * 100, color=C["red"], lw=1.8, marker="o", ms=4, label="Só China")
    a.plot(x, sem * 100, color=C["ink2"], lw=1.8, ls="--", marker="s", ms=4, label="Sem a China (parcela do restante)")
    for i, (u, w) in enumerate(zip(cm.parcela_exportacoes_bqd_fh * 100, sem * 100)):
        a.text(i, u + 2.5, br(u, 0), ha="center", fontsize=7.5, color=C["blue"]); a.text(i, w - 4.5, br(w, 0), ha="center", fontsize=7.5, color=C["ink2"])
    a.set_xticks(x); a.set_xticklabels(GOV); a.set_ylim(0, 55); a.set_ylabel("% das exportações"); nogridx(a); a.legend(fontsize=7, loc="upper left")
    a.set_title("Exportações a países de baixa qualidade democrática")
    salvar(f, "c33", titulo="Parcela das exportações brasileiras destinada a países de baixa qualidade democrática (Freedom House), com e sem a China, por período",
           pergunta="A mudança na composição das exportações vem de muitos países ou de um só?", periodo="2003–2026, por período presidencial",
           unidade="% do valor FOB exportado", universo="Exportações brasileiras por país e mês (D-054)", fonte_primaria=F_COMEX + "; " + F_FH,
           tratamento="Classificação do destino no ano; parcela sem a China calculada como (parcela total − parcela China) ÷ (1 − parcela China)",
           derivado="Parcelas por período", limitacoes="47% do valor do período iniciado em 2023 sem classificação (FH até 2024); comércio responde a preços e demanda externa",
           leitura=f"Com a China: de {br(cm.parcela_exportacoes_bqd_fh.iloc[0]*100,1)}% a {br(cm.parcela_exportacoes_bqd_fh.iloc[6]*100,1)}%; sem a China: de {br(sem.iloc[0]*100,1)}% a {br(sem.iloc[6]*100,1)}%.",
           codigo="X4")
    # acordos
    ac = ler("acordos_bilaterais"); ac["d"] = pd.to_datetime(ac.data_assinatura, errors="coerce")
    ay = ac.groupby(ac.d.dt.year).size().reindex(range(1995, 2027)).fillna(0)
    R["p6_acordos_total"] = int(len(ac)); R["p6_acordos_ano"] = {int(k): int(v) for k, v in ay.items()}
    f, a = fig(2.8)
    a.bar(ay.index, ay.values, color=C["aqua"], width=0.75)
    for y in (2010, 2020, 2023):
        a.text(y, ay[y] + 6, str(int(ay[y])), ha="center", fontsize=8, fontweight="bold")
    a.set_ylabel("atos bilaterais assinados"); nogridx(a); a.set_xticks(range(1995, 2027, 5)); a.set_title("Atos bilaterais assinados pelo Brasil, por ano")
    salvar(f, "c34", titulo="Atos bilaterais assinados pelo Brasil com outros países, por ano, 1995–2026", pergunta="Como variou o ritmo da diplomacia bilateral formal?",
           periodo="1995–2026 (2026 parcial)", unidade="número de atos", universo=f"{len(ac)} atos bilaterais com um país como outra parte (D-041)", fonte_primaria=F_ITAMARATY,
           tratamento="Contagem pela data de assinatura", derivado="Contagem anual", limitacoes="Atos de naturezas diferentes; contagem não mede intensidade",
           leitura=f"{int(ay[2010])} atos em 2010, {int(ay[2020])} em 2020 e {int(ay[2023])} em 2023.", codigo="X5")
    pc = ac.pais_iso3.value_counts().head(10).iloc[::-1]
    f, a = fig(2.9)
    a.barh([NP.get(i, i) for i in pc.index], pc.values, color=C["aqua"], height=0.66)
    for i, x0 in enumerate(pc.values):
        a.text(x0 + 5, i, str(x0), va="center", fontsize=8)
    nogridy(a); a.set_xlabel("atos bilaterais, 1823–2026"); a.set_title("Países com mais atos bilaterais com o Brasil")
    salvar(f, "c34b", titulo="Países com mais atos bilaterais com o Brasil, 1823–2026", pergunta="Com quem o Brasil tem mais atos formais?",
           periodo="1823–2026", unidade="número de atos", universo="Atos bilaterais (D-041)", fonte_primaria=F_ITAMARATY, tratamento="Contagem por país",
           derivado="Contagem", limitacoes="Inclui atos antigos e de baixa relevância", leitura=f"{NP.get(pc.index[-1], pc.index[-1])}: {pc.iloc[-1]} atos.", codigo="X5")
    ag = pd.read_csv(TAB / "eixo2_acordos_por_governo.csv")
    tabela(pd.DataFrame({"Período": ag.governo, "Atos": ag.n_atos, "% com países de baixa qualidade (FH)": (ag.parcela_atos_bqd_fh * 100).round(1),
                         "% de países de baixa qualidade no mundo (FH)": (ag.parcela_paises_bqd_no_mundo_fh * 100).round(1), "% (V-Dem)": (ag.parcela_atos_bqd_vdem * 100).round(1)}),
           "t_x5_periodo", titulo="Atos bilaterais por período e qualidade democrática do parceiro", unidade="atos e %", periodo="2003–2026", universo="D-041, D-053",
           fonte=F_ITAMARATY + "; " + F_FH + "; " + F_VDEM, notas="Data de assinatura; comparação com a parcela de países de baixa qualidade no mundo.", codigo="X5")
    gravar_resultados(R)
    print(R["p6_concordancia_reguas_pct"], R["p6_bqd_sem_china"], R["p6_bndes_top5_pct"])


if __name__ == "__main__":
    main()
