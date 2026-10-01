"""Núcleo analítico (Parte VII): séries anuais do painel ampliado, 2002–2026 (D-074).

Cada série é lida das bases ou de resultados já publicados nas partes II a VI. Nada é interpolado: série eleitoral só existe
nos anos de eleição; anos fora da cobertura ficam vazios.
"""
from __future__ import annotations

import zipfile

import numpy as np
import pandas as pd

from .comum import (CUR, F_BNDES, F_CAMARA, F_CGU_EMENDAS, F_CGU_SANCOES, F_COMEX, F_ETICA, F_FH, F_IPCA, F_ITAMARATY, F_ONU, F_POP,
                    F_RTN, F_STF, F_TCU, F_TSE_CAND, F_TSE_CONTAS, F_VDEM, RAIZ, SIGLA, TAB, fator_real, ler, partido_na_data, periodo_ano,
                    resultados)
from .parte3 import TN
from .parte7 import nep_anual

ANOS = list(range(2002, 2027))
DIMENSOES = ["Financiamento eleitoral", "Recursos públicos", "Emendas parlamentares", "Execução orçamentária", "Partidos", "STF",
             "Controle administrativo", "Política externa", "Comércio exterior", "Indicadores democráticos"]
PERIODOS = [(2003, 2006), (2007, 2010), (2011, 2014), (2015, 2018), (2019, 2022), (2023, 2026)]
TROCAS_GOVERNO = [2003, 2011, 2016, 2019, 2023]  # D-075: primeiro ano com novo presidente na maior parte do ano
JANELAS = [(2003, 2005), (2008, 2010), (2013, 2015), (2016, 2018), (2019, 2020), (2021, 2022), (2023, 2026)]


def _s(d) -> pd.Series:
    return pd.Series({int(k): v for k, v in d.items() if str(k).isdigit()}, dtype=float)


def reeleicao() -> tuple[pd.DataFrame, pd.DataFrame]:
    """D-076: deputados titulares em 1º de julho do ano da eleição ligados à candidatura a deputado federal da mesma eleição.
    Devolve (painel por eleição, linhas por deputado)."""
    from src.normalizacao.tse import norm
    cg = ler("cargos"); at = ler("atores").set_index("id_ator")
    dep = cg[cg.cargo.str.startswith("Deputado federal (titular)")].copy()
    dep["ini"] = pd.to_datetime(dep.data_inicio, errors="coerce"); dep["fim"] = pd.to_datetime(dep.data_fim, errors="coerce").fillna(pd.Timestamp("2027-02-01"))
    linhas, painel = [], []
    for ano in (2006, 2010, 2014, 2018, 2022):
        d0 = pd.Timestamp(f"{ano}-07-01")
        ids = dep[(dep.ini <= d0) & (dep.fim >= d0)].id_ator.unique()
        z = zipfile.ZipFile(RAIZ / f"data/raw/tse/2026-09-25/consulta_cand_{ano}.zip")
        c = pd.concat([pd.read_csv(z.open(n), sep=";", encoding="latin1", dtype=str,
                                   usecols=lambda k: k in ("DS_CARGO", "DS_SIT_TOT_TURNO", "SG_UF", "NR_CANDIDATO", "NM_CANDIDATO", "NM_URNA_CANDIDATO",
                                                           "NM_TIPO_ELEICAO", "DS_SITUACAO_CANDIDATURA", "SG_PARTIDO"))
                       for n in z.namelist() if n.endswith(".csv") and "_BRASIL" not in n])
        c = c[(c.DS_CARGO.str.upper() == "DEPUTADO FEDERAL") & c.NM_TIPO_ELEICAO.map(norm).str.contains("ordinaria")]
        c = c.drop_duplicates(["SG_UF", "NR_CANDIDATO"])
        c["eleito"] = c.DS_SIT_TOT_TURNO.str.upper().isin(["ELEITO", "ELEITO POR QP", "ELEITO POR MÉDIA", "MÉDIA"])
        nomes = pd.concat([pd.DataFrame({"nm": c.NM_CANDIDATO.map(norm), "k": list(zip(c.SG_UF, c.NR_CANDIDATO))}),
                           pd.DataFrame({"nm": c.NM_URNA_CANDIDATO.map(norm), "k": list(zip(c.SG_UF, c.NR_CANDIDATO))})])
        idx = nomes.groupby("nm").k.agg(set).to_dict()
        chave = c.set_index(["SG_UF", "NR_CANDIDATO"])
        lig = 0
        for a in ids:
            nm = at.nome_normalizado.get(a, "")
            ach = idx.get(nm, set())
            if len(ach) == 1:
                k = next(iter(ach)); r = chave.loc[k]
                linhas.append(dict(ano=ano, id_ator=a, uf=k[0], eleito=bool(r.eleito), situacao=r.DS_SIT_TOT_TURNO, sigla_tse=r.SG_PARTIDO)); lig += 1
        sub = [l for l in linhas if l["ano"] == ano]
        painel.append(dict(ano=ano, deputados_em_exercicio=len(ids), ligados_a_candidatura=lig,
                           reeleitos=sum(l["eleito"] for l in sub), taxa_reeleicao=round(100 * sum(l["eleito"] for l in sub) / max(lig, 1), 1)))
    return pd.DataFrame(painel), pd.DataFrame(linhas)


def emendas_anuais() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Séries anuais das emendas (2017–2026): escala, modalidades, autoria, rastreabilidade, execução, destino e território."""
    em = ler("emendas_parlamentares", low_memory=False)
    em = em[em.ano.between(2017, 2026)].copy()
    em["t"] = em.tipo_emenda.map(TN).fillna(em.tipo_emenda)
    em["real"] = em.valor_pago * em.ano.map(lambda y: fator_real(periodo_ano(int(y))))
    pop = pd.read_csv(CUR / "ibge_populacao_uf.csv")
    from .parte3 import UF
    em["sg"] = em.uf.map(UF)
    out = {}
    for y, g in em.groupby("ano"):
        p = g.valor_pago.sum()
        r = dict(pago_real_bi=g.real.sum() / 1e9)
        for t in g.t.unique():
            r[f"pct_{t}"] = 100 * g.loc[g.t == t, "valor_pago"].sum() / p
        r["pct_autor_parlamentar"] = 100 * g.loc[g.id_ator.notna(), "valor_pago"].sum() / p
        r["pct_sem_uf"] = 100 * g.loc[g.sg.isna(), "valor_pago"].sum() / p
        r["pct_saude"] = 100 * g.loc[g.funcao == "Saúde", "valor_pago"].sum() / p
        r["execucao"] = 100 * p / g.valor_empenhado.sum()
        ap = 2021 if y <= 2022 else (2024 if y <= 2024 else 2025)
        pp = pop[pop.ano == ap].set_index("uf").populacao
        pc = (g.dropna(subset=["sg"]).groupby("sg").valor_pago.sum() / pp).dropna()
        from .comum import gini
        r["gini_pc_uf"] = gini(pc.values)
        r["razao_max_min_pc_uf"] = pc.max() / pc.min()
        out[int(y)] = r
    E = pd.DataFrame(out).T.sort_index()
    # partidos: emendas individuais pagas por autor e ano, autor na base do governo ou fora (filiação em 1º de julho)
    go = pd.read_csv(TAB / "governo_oposicao_partidos.csv"); go["ini"] = pd.to_datetime(go.inicio); go["fim"] = pd.to_datetime(go.fim)
    ind = em[em.t.str.startswith("Individual") & em.id_ator.notna()]
    rows = []
    for y, g in ind.groupby("ano"):
        d = pd.Timestamp(f"{int(y)}-07-01")
        part = partido_na_data(d)
        grp = go[(go.ini <= d) & (go.fim >= d)].set_index("id_partido").grupo
        s = g.groupby("id_ator").real.sum()
        gg = s.index.map(part).map(grp)
        df = pd.DataFrame({"v": s.values, "g": gg})
        rows.append(dict(ano=int(y), autores=len(s), media_base=df[df.g == "governo"].v.mean() / 1e6, media_fora=df[df.g != "governo"].v.mean() / 1e6,
                         n_base=int((df.g == "governo").sum()), n_fora=int((df.g != "governo").sum())))
    P = pd.DataFrame(rows).set_index("ano")
    P["razao_base_fora"] = P.media_base / P.media_fora
    return E, P


def estoque_stf() -> pd.DataFrame:
    a = pd.read_csv(TAB / "foro_acoes.csv")
    a = a[a.grupo == "com réu parlamentar"].copy()
    a["aut"] = pd.to_datetime(a.autuacao); a["des"] = pd.to_datetime(a.data_desfecho)
    rows = []
    for y in range(2003, 2027):
        d = pd.Timestamp(f"{y}-12-31") if y < 2026 else pd.Timestamp("2026-09-23")
        st = a[(a.aut <= d) & ((a.des > d) | a.des.isna())]
        rows.append(dict(ano=y, estoque=len(st), idade_mediana=float(((d - st.aut).dt.days / 365.25).median()) if len(st) else np.nan,
                         pct_origem_stf=100 * (st.origem == "autuada no STF").mean() if len(st) else np.nan,
                         autuadas=int((a.aut.dt.year == y).sum())))
    return pd.DataFrame(rows).set_index("ano")


def votos_anuais() -> pd.DataFrame:
    v = pd.read_csv(TAB / "eixo2_votos_por_resolucao.csv"); v["ano"] = v.data.str[:4].astype(int)
    e = v[(v.tipo == "escrutinio") & v.voto_brasil.isin(["sim", "abstencao", "nao"])].copy()
    e["sim"] = e.voto_brasil == "sim"
    e["coincide"] = np.where(e.sim_democracias.isna(), np.nan, ((e.sim & (e.sim_democracias > 0.5)) | (~e.sim & (e.sim_democracias <= 0.5))).astype(float))
    g = e.groupby("ano")
    return pd.DataFrame({"n": g.size(), "pct_sim": 100 * g.sim.mean(), "pct_coincide_democracias": 100 * g.coincide.mean()})


def comercio_periodos() -> pd.Series:
    """Parcela das exportações para países Não Livres (Freedom House), por período da matriz (2015–18 combina dois governos, ponderado pelas exportações)."""
    c = pd.read_csv(TAB / "eixo2_comercio_por_governo.csv")
    c["ini"] = c.governo.str.extract(r"\((\d{4})")[0].astype(int)
    out = {}
    for a, b in PERIODOS:
        g = c[c.ini.between(a, b)]
        out[(a, b)] = 100 * float((g.parcela_exportacoes_bqd_fh * g.exportacoes_fob_usd).sum() / g.exportacoes_fob_usd.sum())
    return pd.Series(out)


def tcu_anual() -> pd.Series:
    st = ler("status_pessoa_processo"); st["data"] = pd.to_datetime(st["data"], errors="coerce")
    tc = st[st.status == "contas_julgadas_irregulares"]
    return tc.groupby(tc.data.dt.year).size().reindex(range(2003, 2027)).fillna(0)


def painel() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Painel anual ampliado e metadados (dimensão, unidade, fonte, nota) de cada série."""
    R0 = resultados()
    P = pd.DataFrame(index=ANOS, dtype=float); M = {}

    def add(nome, serie, dim, unidade, fonte, nota=""):
        P[nome] = pd.Series(serie, dtype=float).reindex(ANOS); M[nome] = dict(dimensao=dim, unidade=unidade, fonte=fonte, nota=nota)

    add("Empresas no dinheiro dos eleitos (%)", _s(R0["p2_mix_pessoa_juridica"]), DIMENSOES[0], "% das receitas", F_TSE_CONTAS, "deputados federais eleitos na eleição")
    add("Fundos eleitorais públicos no dinheiro dos eleitos (%)", _s(R0["p2_mix_fundo_publico"]), DIMENSOES[0], "% das receitas", F_TSE_CONTAS)
    add("Transferências de partidos no dinheiro dos eleitos (%)", _s(R0["p2_mix_partido"]), DIMENSOES[0], "% das receitas", F_TSE_CONTAS, "origem mista até 2014 (fundo partidário e doações de empresas aos partidos)")
    add("Recursos próprios no dinheiro dos eleitos (%)", _s(R0["p2_mix_recursos_proprios"]), DIMENSOES[0], "% das receitas", F_TSE_CONTAS)
    add("Gini das receitas dos eleitos", _s(R0["p2_gini"]), DIMENSOES[0], "índice de 0 a 1", F_TSE_CONTAS)
    add("Receita mediana real por eleito (R$ mil)", _s(R0["p2_mediana_real_mil"]), DIMENSOES[0], "R$ mil de ago/2026", F_TSE_CONTAS + "; " + F_IPCA)
    rtn = pd.read_csv(CUR / "tesouro_rtn_anual.csv").pivot_table(index="ano", columns="linha", values="valor_rs_milhoes")
    fr = pd.Series({y: fator_real(periodo_ano(y)) for y in range(2002, 2026)})
    add("Despesa total da União (R$ bi reais)", (rtn.despesa_total.reindex(fr.index) * fr / 1e3), DIMENSOES[1], "R$ bilhões de ago/2026", F_RTN + "; " + F_IPCA)
    fefc = rtn.fefc.reindex(fr.index) * fr
    add("Fundo eleitoral (FEFC) pago (R$ bi reais)", (fefc[fefc > 0] / 1e3), DIMENSOES[1], "R$ bilhões de ago/2026", F_RTN + "; " + F_IPCA, "existe desde 2018")
    E, PB = emendas_anuais()
    add("Emendas pagas (R$ bi reais)", E.pago_real_bi, DIMENSOES[2], "R$ bilhões de ago/2026", F_CGU_EMENDAS + "; " + F_IPCA, "2014–2016 fora por inconsistência; 2026 parcial")
    add("Emendas pagas (% da despesa total)", _s(R0["p3_pct_despesa_total"]), DIMENSOES[2], "%", F_CGU_EMENDAS + "; " + F_RTN)
    add("Emendas sem autor parlamentar identificado (% do pago)", 100 - E.pct_autor_parlamentar, DIMENSOES[2], "% do valor pago", F_CGU_EMENDAS, "relator, comissão e bancada não têm autor individual")
    add("Transferências especiais (% do pago)", E["pct_Individual (transferência especial)"].fillna(0), DIMENSOES[2], "% do valor pago", F_CGU_EMENDAS)
    add("Desigualdade per capita entre UF (Gini)", E.gini_pc_uf, DIMENSOES[2], "índice de 0 a 1", F_CGU_EMENDAS + "; " + F_POP)
    disc = rtn.despesas_discricionarias_executivo.reindex(fr.index).replace(0, np.nan)  # série começa em 2008
    add("Discricionárias do Executivo (R$ bi reais)", disc * fr / 1e3, DIMENSOES[3], "R$ bilhões de ago/2026", F_RTN + "; " + F_IPCA)
    add("Discricionárias do Executivo (% da despesa total)", 100 * disc / rtn.despesa_total.reindex(fr.index), DIMENSOES[3], "%", F_RTN)
    add("Execução das emendas (pago/empenhado, %)", E.execucao, DIMENSOES[3], "%", F_CGU_EMENDAS, "pago inclui restos a pagar")
    add("Número efetivo de partidos (Câmara)", nep_anual(), DIMENSOES[4], "número", F_CAMARA, "titulares em 15 de fevereiro de cada ano")
    add("Mudanças individuais de partido", _s(R0["p5_trocas_individuais_ano"]), DIMENSOES[4], "mudanças por ano", F_CAMARA + "; D-072")
    add("Cadeiras da base do governo (%)", _s(R0["p5_pct_cadeiras_base"]), DIMENSOES[4], "% das cadeiras", F_CAMARA, "base pela concordância com o governo nas votações nominais")
    rp, rl = reeleicao()
    add("Reeleição dos deputados que concorreram (%)", rp.set_index("ano").taxa_reeleicao, DIMENSOES[4], "% dos ligados à candidatura", F_TSE_CAND + "; " + F_CAMARA + "; D-076")
    ES = estoque_stf()
    add("Ações penais com réu parlamentar em curso no STF", ES.estoque, DIMENSOES[5], "ações em 31/12", F_STF, "universo de D-068; 2026 em 23/09")
    add("Idade mediana das ações em curso (anos)", ES.idade_mediana, DIMENSOES[5], "anos", F_STF)
    sa = pd.read_csv(TAB / "foro_serie_anual.csv").set_index("ano")
    dec = _s(R0["p4_declinios_ano"]); dec.loc[2026] = np.nan
    add("Declínios de competência (réu parlamentar)", dec, DIMENSOES[5], "ações por ano", F_STF, "2026 parcial excluído")
    mer = sa["julgamento de mérito"].astype(float); mer.loc[2026] = np.nan
    add("Julgamentos de mérito (réu parlamentar)", mer, DIMENSOES[5], "ações por ano", F_STF, "2026 parcial excluído")
    san = _s(R0["p4_sancoes_ano"]); san = san[san.index <= 2025]
    add("Sanções a empresas registradas (CGU)", san, DIMENSOES[6], "registros por ano", F_CGU_SANCOES, "cadastro começa em 2015; 2026 parcial excluído")
    tc = tcu_anual(); tc.loc[2026] = np.nan
    add("Contas irregulares no TCU, pessoas da base", tc, DIMENSOES[6], "decisões por ano", F_TCU, "trânsito em julgado; 2026 parcial excluído")
    et = _s(R0["p5_etica_ano"]).reindex(range(2003, 2026)).fillna(0)
    add("Representações nos Conselhos de Ética", et, DIMENSOES[6], "representações por ano", F_ETICA, "2026 parcial excluído")
    V = votos_anuais()
    add("Votos a favor de resoluções de escrutínio (%)", V.pct_sim, DIMENSOES[7], "% dos votos do Brasil", F_ONU, "ONU (AGNU e CDH) e OEA; países-alvo mudam a cada ano")
    add("Coincidência com a maioria das democracias (%)", V.pct_coincide_democracias, DIMENSOES[7], "% das resoluções", F_ONU + "; " + F_VDEM)
    ac = _s(R0["p6_acordos_ano"]); ac = ac[(ac.index >= 2002) & (ac.index <= 2025)]
    add("Atos bilaterais assinados", ac, DIMENSOES[7], "atos por ano", F_ITAMARATY, "2026 parcial excluído")
    bn = _s(R0["p6_bndes_ops_ano"]).reindex(range(2002, 2026)).fillna(0)
    add("Operações de exportação de serviços (BNDES)", bn, DIMENSOES[7], "operações por ano", F_BNDES)
    add("Democracia liberal do Brasil (V-Dem)", _s(R0["p6_ldi"]), DIMENSOES[9], "índice de 0 a 1", F_VDEM)
    add("Pontuação do Brasil (Freedom House)", _s(R0["p6_fh_total"]), DIMENSOES[9], "0 a 100", F_FH, "pontuação agregada publicada desde a edição de 2013 na base")
    P = P.loc[ANOS]
    extras = dict(emendas=E, partidos_emendas=PB, reeleicao=rp, reeleicao_linhas=rl, estoque=ES, votos=V, comercio=comercio_periodos())
    return P, pd.DataFrame(M).T, extras


if __name__ == "__main__":
    P, M, X = painel()
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
    print(P.round(2).T.to_string())
    for k, v in X.items():
        print("==", k); print(v.round(2) if hasattr(v, "round") else v)
