"""Parte VII, Transformações e ciclos: painel anual das séries das partes II a VI e marcos normativos."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .comum import (C, CUR, F_CAMARA, F_CGU_EMENDAS, F_CGU_SANCOES, F_ETICA, F_FH, F_ITAMARATY, F_RTN, F_STF, F_TSE_CONTAS,
                    F_VDEM, F_BNDES, F_IPCA, SIGLA, TAB, TABS, br, fig, gravar_resultados, ler, nogridx, partido_na_data, resultados,
                    salvar, tabela)

ANOS = list(range(2002, 2027))
# Marcos normativos e decisões, com a referência conferida (texto oficial lido em 30/09/2026) ou a decisão do projeto que já a usa.
MARCOS = [
    ("2013-08-01", "Lei 12.846 (responsabilização de pessoas jurídicas; acordo de leniência, art. 16)", "planalto.gov.br/ccivil_03/_ato2011-2014/2013/lei/l12846.htm", "Justiça e controle"),
    ("2015-03-17", "EC 86 (execução obrigatória das emendas individuais, 1,2% da RCL)", "planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc86.htm", "Orçamento"),
    ("2015-09-17", "STF, ADI 4650 (doações de pessoas jurídicas a campanhas)", "[REFERÊNCIA A CONFIRMAR: acórdão no portal do STF]; usada em docs/limitacoes.md", "Financiamento"),
    ("2015-09-29", "Lei 13.165 (minirreforma eleitoral; janela de mudança de partido, art. 22-A da Lei 9.096)", "planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13165.htm", "Partidos"),
    ("2017-10-04", "EC 97 (fim das coligações proporcionais a partir de 2020; cláusula de desempenho)", "planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc97.htm", "Partidos"),
    ("2017-10-06", "Lei 13.487 (Fundo Especial de Financiamento de Campanha)", "planalto.gov.br/ccivil_03/_ato2015-2018/2017/lei/l13487.htm", "Financiamento"),
    ("2018-05-03", "STF, AP 937, questão de ordem (restrição do foro por prerrogativa)", "data de corte usada em D-068; [REFERÊNCIA A CONFIRMAR: acórdão]", "Justiça e controle"),
    ("2019-06-26", "EC 100 (execução obrigatória das emendas de bancada)", "planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc100.htm", "Orçamento"),
    ("2019-12-12", "EC 105 (transferência especial e com finalidade definida)", "planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc105.htm", "Orçamento"),
    ("2022-02-08", "TSE registra a fusão de DEM e PSL (União)", "FNT-000007 (data em data/base/instituicoes.csv)", "Partidos"),
    ("2022-12-19", "STF julga as emendas de relator (ADPF 850, 851, 854, 1014)", "[REFERÊNCIA A CONFIRMAR: data e acórdão; notícia oficial do STF não pôde ser lida]", "Orçamento"),
]


def nep_anual() -> pd.Series:
    cg = ler("cargos"); dep = cg[cg.cargo.str.startswith("Deputado federal (titular)")].copy()
    dep["ini"] = pd.to_datetime(dep.data_inicio, errors="coerce"); dep["fim"] = pd.to_datetime(dep.data_fim, errors="coerce").fillna(pd.Timestamp("2027-02-01"))
    out = {}
    for y in ANOS:
        d = pd.Timestamp(f"{max(y, 2003)}-02-15")
        ids = dep[(dep.ini <= d) & (dep.fim >= d)].id_ator.unique()
        s = pd.Series(ids).map(partido_na_data(d)).map(SIGLA).dropna().value_counts()
        sh = s / s.sum(); out[y] = float(1 / (sh ** 2).sum())
    return pd.Series(out)


def main() -> None:
    R0 = resultados(); R = {}
    P = pd.DataFrame(index=ANOS)
    P["Empresas no dinheiro dos deputados eleitos (%)"] = pd.Series(R0["p2_mix_pessoa_juridica"]).rename(int)
    P["Fundo público no dinheiro dos deputados eleitos (%)"] = pd.Series(R0["p2_mix_fundo_publico"]).rename(int)
    P["Gini das receitas dos deputados eleitos"] = pd.Series(R0["p2_gini"]).rename(int)
    P["Emendas pagas, R$ bi reais"] = pd.Series(R0["p3_pago_real_bi"]).rename(int)
    P["Emendas pagas, % da despesa total"] = pd.Series(R0["p3_pct_despesa_total"]).rename(int)
    P["Número efetivo de partidos (Câmara)"] = nep_anual()
    P["Mudanças individuais de partido"] = pd.Series(R0["p5_trocas_individuais_ano"]).rename(int)
    P["Declínios de competência no STF (réu parlamentar)"] = pd.Series(R0["p4_declinios_ano"]).rename(int)
    sa = pd.read_csv(TAB / "foro_serie_anual.csv").set_index("ano")
    P["Julgamentos de mérito no STF (réu parlamentar)"] = sa["julgamento de mérito"]
    P["Representações nos Conselhos de Ética"] = pd.Series(R0["p5_etica_ano"]).rename(int)
    P["Sanções a empresas registradas (CGU)"] = pd.Series(R0["p4_sancoes_ano"]).rename(int)
    P["V-Dem, democracia liberal do Brasil"] = pd.Series(R0["p6_ldi"]).rename(int)
    P["Freedom House, pontuação do Brasil"] = pd.Series(R0["p6_fh_total"]).rename(int)
    P["Atos bilaterais assinados"] = pd.Series(R0["p6_acordos_ano"]).rename(int)
    P["Operações de exportação do BNDES"] = pd.Series(R0["p6_bndes_ops_ano"]).rename(int)
    P = P.loc[ANOS]
    # zeros estruturais antes do início de cada série viram ausência
    P.loc[:2014, "Sanções a empresas registradas (CGU)"] = np.where(P.loc[:2014, "Sanções a empresas registradas (CGU)"].fillna(0) == 0, np.nan, P.loc[:2014, "Sanções a empresas registradas (CGU)"])
    P.loc[2026, ["Declínios de competência no STF (réu parlamentar)", "Julgamentos de mérito no STF (réu parlamentar)"]] = np.nan
    t = P.round(3).reset_index().rename(columns={"index": "Ano"})
    tabela(t, "t_painel", titulo="Painel anual das séries usadas na Parte VII", unidade="unidades de cada série (ver nome da coluna)", periodo="2003–2026",
           universo="Séries das partes II a VI", fonte="As das fichas de cada série (TSE, CGU, Tesouro, IBGE, Câmara, Senado, STF, V-Dem, Freedom House, Itamaraty, BNDES)",
           notas="Células vazias: série não observada no ano (eleições a cada quatro anos; emendas desde 2017; sanções desde 2015; Freedom House sem 2025); 2026 parcial.", codigo="Parte VII")
    Z = (P - P.mean()) / P.std()
    f, a = fig(5.4)
    cm = plt.get_cmap("RdBu_r")
    Zm = np.ma.masked_invalid(Z.T.values)
    a.imshow(Zm, cmap=cm, vmin=-2.5, vmax=2.5, aspect="auto")
    a.set_facecolor("#f2f1ee")
    a.set_yticks(range(len(P.columns))); a.set_yticklabels(P.columns, fontsize=6.6)
    a.set_xticks(range(len(ANOS))); a.set_xticklabels([str(y)[2:] for y in ANOS], fontsize=7); a.grid(False)
    for s_ in a.spines.values():
        s_.set_visible(False)
    a.set_xlabel("ano (20xx); cinza: série não observada"); a.set_title("Painel anual (escore z de cada série)")
    sm = plt.cm.ScalarMappable(cmap=cm, norm=plt.Normalize(-2.5, 2.5)); cb = f.colorbar(sm, ax=a, fraction=0.03, pad=0.01); cb.set_label("desvios-padrão da própria série", fontsize=7); cb.ax.tick_params(labelsize=6.5)
    salvar(f, "n20", titulo="Painel anual de 15 séries das partes II a VI, padronizadas pela média e desvio-padrão de cada série, 2002–2026",
           pergunta="As mudanças das diferentes dimensões acontecem nos mesmos anos?", periodo="2002–2026", unidade="desvios-padrão em relação à média da própria série (escore z)",
           universo="Séries anuais descritas nas partes II a VI", fonte_primaria="As de cada série (fichas das partes II a VI)",
           tratamento="Padronização de cada série por sua média e desvio-padrão nos anos observados; anos sem observação em cinza",
           derivado="Escore z por série e ano", limitacoes="Séries com poucos pontos (eleições) e inícios diferentes; a padronização não torna as séries comparáveis em magnitude; cor por posição, não por causa",
           leitura="Os tons mudam de lado em vários anos entre 2015 e 2023, mas não todos no mesmo ano.", codigo="Parte VII")
    # anos de maior mudança
    mx = {}
    for c in P.columns:
        s = Z[c].dropna().diff().dropna()
        if len(s) >= 2:
            mx[c] = int(s.abs().idxmax())
    R["p7_ano_maior_mudanca"] = mx
    R["p7_marcos_n"] = len(MARCOS); R["p7_marcos_2015_2019"] = sum(1 for d, *_ in MARCOS if "2015" <= d[:4] <= "2019")
    cont = pd.Series(mx).value_counts().sort_index()
    R["p7_anos_contagem"] = {int(k): int(v) for k, v in cont.items()}
    R["p7_n_2016_2023"] = int(sum(v for k, v in cont.items() if 2016 <= k <= 2023))
    fora = sorted(int(k) for k in cont.index if not 2016 <= k <= 2023)
    R["p7_fora_lista"] = ", ".join(str(k) for k in fora[:-1]) + (" e " if len(fora) > 1 else "") + (str(fora[-1]) if fora else "")
    R["p7_anos_texto"] = "; ".join(f"{int(k)}, {int(v)} {'série' if v == 1 else 'séries'}" for k, v in cont.items())
    f, a = fig(3.6)
    items = sorted(mx.items(), key=lambda kv: kv[1])
    for i, (c, y) in enumerate(items):
        a.scatter([y], [i], color=C["blue"], s=30, zorder=3)
        a.text(y + 0.3, i, c, va="center", fontsize=6.6)
    for d, txt, _, area in MARCOS:
        yr = int(d[:4]) + (int(d[5:7]) - 1) / 12
        a.axvline(yr, color=C["orange"], lw=0.6, alpha=0.6)
    a.set_yticks([]); a.set_xlim(2003, 2034); a.set_xticks(range(2004, 2027, 2)); a.tick_params(labelsize=7)
    a.set_xlabel("ano da maior variação de cada série (pontos); marcos normativos (linhas laranja)")
    a.set_title("Em que ano cada série mais mudou"); nogridx(a)
    salvar(f, "n22", titulo="Ano da maior variação anual de cada série do painel, com os marcos normativos",
           pergunta="As maiores mudanças se concentram em algum período?", periodo="2003–2026", unidade="ano",
           universo="15 séries do painel", fonte_primaria="As de cada série", tratamento="Maior variação absoluta do escore z entre anos consecutivos observados; para séries eleitorais, entre eleições",
           derivado="Ano da maior mudança", limitacoes="Um só ano por série; variações próximas em tamanho não aparecem; marcos são contexto, não causa medida",
           leitura="Distribuição dos anos: " + ", ".join(f"{k}: {v}" for k, v in R["p7_anos_contagem"].items()) + ".", codigo="Parte VII")
    # linha do tempo normativa (diagrama)
    f, a = plt.subplots(figsize=(6.3, 3.6))
    areas = ["Financiamento", "Orçamento", "Partidos", "Justiça e controle"]; col = {"Financiamento": C["blue"], "Orçamento": C["aqua"], "Partidos": C["violet"], "Justiça e controle": C["orange"]}
    for i, ar in enumerate(areas):
        a.hlines(i, 2012.5, 2023.5, color=C["grid"], lw=6)
        a.text(2012.4, i, ar, ha="right", va="center", fontsize=8, fontweight="bold", color=col[ar])
    lado = {}
    for d, txt, ref, ar in MARCOS:
        yr = int(d[:4]) + (int(d[5:7]) - 1) / 12 + int(d[8:10]) / 365
        i = areas.index(ar); k = lado.get(ar, 0); lado[ar] = k + 1
        a.scatter([yr], [i], color=col[ar], s=36, zorder=3)
        a.annotate(f"{d[8:10]}/{d[5:7]}/{d[:4]}\n" + txt.split(" (")[0], (yr, i), xytext=(0, 13 if k % 2 == 0 else -22), textcoords="offset points", ha="center", fontsize=5.7, color=C["ink"])
    a.set_ylim(-0.8, 3.8); a.set_xlim(2009.3, 2024); a.set_yticks([]); a.set_xticks(range(2013, 2024)); a.tick_params(labelsize=7)
    [s.set_visible(False) for k_, s in a.spines.items() if k_ != "bottom"]; a.grid(False)
    a.set_title("Marcos normativos e decisões, 2013–2022")
    salvar(f, "n21", titulo="Linha do tempo dos marcos normativos e decisões usados como contexto no livro, 2013–2022",
           pergunta="Que regras formais mudaram no período em que as séries mudam?", periodo="2013–2022", unidade="datas",
           universo="Normas e decisões citadas no livro", fonte_primaria="Textos oficiais no portal da Presidência da República (leis e emendas constitucionais), lidos em 30/09/2026; decisões do STF e registro do TSE conforme a tabela de marcos",
           tratamento="Seleção das normas que tratam de financiamento, orçamento, partidos e controle", derivado="Nenhum",
           limitacoes="Seleção do autor; duas decisões do STF com referência a confirmar", leitura=f"{len(MARCOS)} marcos entre 2013 e 2022, {sum(1 for d, *_ in MARCOS if '2015' <= d[:4] <= '2019')} deles entre 2015 e 2019.", codigo="Parte VII")
    tabela(pd.DataFrame([dict(Data=d, Marco=t_, Referência=r_, Área=ar) for d, t_, r_, ar in MARCOS]), "t_marcos",
           titulo="Marcos normativos e decisões citados no livro", unidade="datas", periodo="2013–2022", universo="Seleção do autor",
           fonte="Presidência da República (legislação), STF, TSE", notas="Endereços de planalto.gov.br lidos em 30/09/2026; itens marcados exigem confirmação.", codigo="Parte VII")
    gravar_resultados(R)
    print(R["p7_ano_maior_mudanca"]); print(P.round(2).to_string())


if __name__ == "__main__":
    main()
