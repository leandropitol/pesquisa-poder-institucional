"""Estudo do foro por prerrogativa de função (D-068): desfecho e tempo das ações penais contra parlamentares no STF.

Universo: ações penais da lista de D-048 autuadas no STF de 2003 em diante. Grupo principal: com réu parlamentar de vínculo confirmado (D-065);
contraste descritivo: as demais. Desfecho por hierarquia (mérito > declínio > em tramitação > extinção da punibilidade > acordo > outro encerramento).
Tempo: autuação no STF até o desfecho; Kaplan-Meier (mediana com bootstrap) e incidência acumulada com riscos competitivos (Aalen-Johansen).

Saídas em relatorios/tabelas: foro_acoes.csv, foro_desfechos.csv, foro_tempos.csv, foro_serie_anual.csv, foro_pessoas.csv, foro_simetria.csv,
foro_simetria_testes.csv e foro_cobertura.csv.

Uso:
    python -m src.analise.foro
"""

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

from src.analise.eixo1 import homogeneidade
from src.analise.etica import linha, partido_em
from src.analise.ideologia import spearman_permutacao
from src.base import BASE, RAIZ, ler
from src.normalizacao.simetria_stf import carregar
from src.normalizacao.stf_desfechos import DECISOES, nomes_civis, vinculo
from src.simetria.governo_oposicao import grupo_na_data, ler_tabela as ler_tabela_governo

SAIDA = RAIZ / "relatorios" / "tabelas"
CORTE = "2026-09-23"
RESTRICAO = "2018-05-03"
INICIO = "2003-01-01"
MERITO = {"Procedente", "Procedente em parte", "Improcedente", "JULGAMENTO DO PLENO - IMPROCEDENTE"}
DECLINIO = {"Declinada a competência", "DECISÃO DO(A) RELATOR(A) - DECLINANDO DA COMPETÊNCIA"}
EXTINCAO = {"Declarada a extinção da punibilidade"}
ACORDO = {"Homologação de acordo de não persecução penal - art.28-A do CPP", "Homologado acordo de não persecução penal", "Homologação de transação penal"}
ORDEM = ["merito", "declinio", "em_tramitacao", "extincao", "acordo", "outro"]
ROTULO = {"merito": "julgamento de mérito", "declinio": "declínio de competência", "em_tramitacao": "em tramitação", "extincao": "extinção da punibilidade sem mérito",
          "acordo": "acordo homologado", "outro": "outro encerramento"}
HORIZONTES = (2, 4, 8)
DETALHE = [("declínio ou remessa (texto)", r"declin|incompet[eê]ncia|remet|remessa|encaminh\w* .{0,40}(ju[ií]zo|justi[çc]a|tribunal|vara)"),
           ("extinção ou prescrição (texto)", r"extin\w* .{0,30}punibilidade|prescri"), ("rejeição da denúncia (texto)", r"rejeit\w* .{0,20}den[úu]ncia"),
           ("arquivamento (texto)", r"arquiv"), ("trancamento ou anulação (texto)", r"tranc|anul|ordem de of[ií]cio"), ("acordo (texto)", r"acordo|transa[çc][ãa]o")]
BOOT, SEMENTE = 2000, 20260930


def iso_br(x: str) -> str:
    x = str(x)
    return f"{x[6:10]}-{x[3:5]}-{x[0:2]}" if len(x) >= 10 and x[2] == "/" else ""


def classificar(dec: pd.DataFrame) -> tuple[str, str]:
    """(categoria, data) de uma ação pelas decisões do Corte Aberta, pela hierarquia de D-068."""
    a = dec.sort_values("data")
    for cat, conj in (("merito", MERITO), ("declinio", DECLINIO)):
        x = a[a["Andamento decisão"].isin(conj)]
        if len(x):
            return cat, x["data"].iloc[0]
    if (a["Indicador de tramitação"] == "Sim").any():
        return "em_tramitacao", CORTE
    for cat, conj in (("extincao", EXTINCAO), ("acordo", ACORDO)):
        x = a[a["Andamento decisão"].isin(conj)]
        if len(x):
            return cat, x["data"].iloc[0]
    baixa = iso_br(a["Data baixa"].iloc[0])
    return "outro", baixa or a["data"].iloc[-1]


def detalhe_outro(dec: pd.DataFrame) -> str:
    """Sensibilidade (não muda a categoria de D-068): tipo de encerramento lido no texto da última decisão final da ação."""
    import re
    f = dec[dec["Tipo decisão"] == "Decisão Final"].sort_values("data")
    if not len(f):
        return "sem decisão final na exportação"
    t = str(f["Observação do andamento"].iloc[-1])
    if "segredo de justiça" in t.lower() or f["Andamento decisão"].iloc[-1].startswith("Decisão (s"):
        return "decisão em segredo de justiça ou sigilosa"
    for rot, rx in DETALHE:
        if re.search(rx, t, re.I):
            return rot
    return "não identificado no texto"


def kaplan_meier(t: np.ndarray, e: np.ndarray):
    """Tempos únicos de evento e sobrevivência logo após cada um."""
    ordem = np.argsort(t)
    t, e = t[ordem], e[ordem]
    tempos = np.unique(t[e == 1])
    s, surv, risco = 1.0, [], []
    for u in tempos:
        n = int((t >= u).sum())
        d = int(((t == u) & (e == 1)).sum())
        s *= 1 - d / n
        surv.append(s)
        risco.append(n)
    return tempos, np.array(surv)


def mediana_km(t: np.ndarray, e: np.ndarray) -> float:
    tempos, s = kaplan_meier(t, e)
    abaixo = np.where(s <= 0.5)[0]
    return float(tempos[abaixo[0]]) if len(abaixo) else float("nan")


def incidencia(t: np.ndarray, causa: np.ndarray, k: str, h: float) -> float:
    """Aalen-Johansen: incidência acumulada da causa k até h anos (causa '' = censura)."""
    ordem = np.argsort(t)
    t, causa = t[ordem], causa[ordem]
    s, cif = 1.0, 0.0
    for u in np.unique(t[(causa != "") & (t <= h)]):
        n = (t >= u).sum()
        d_todos = ((t == u) & (causa != "")).sum()
        d_k = ((t == u) & (causa == k)).sum()
        cif += s * d_k / n
        s *= 1 - d_todos / n
    return float(cif)


def bootstrap_mediana(t: np.ndarray, e: np.ndarray) -> tuple[float, float]:
    rng = np.random.default_rng(SEMENTE)
    meds = []
    for _ in range(BOOT):
        i = rng.integers(0, len(t), len(t))
        meds.append(mediana_km(t[i], e[i]))
    meds = np.array(meds)
    meds = meds[~np.isnan(meds)]
    return (float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5))) if len(meds) > BOOT * 0.5 else (float("nan"), float("nan"))


def acoes() -> tuple[pd.DataFrame, set, dict]:
    c = carregar()
    lig, lista = c["lig"], c["lista"]
    atores, cargos = ler("atores"), ler("cargos")
    nome_ator = dict(zip(atores["id_ator"], atores["nome_normalizado"]))
    civ = nomes_civis(atores, cargos, ler("filiacoes"), BASE)
    pares = set()
    for (ap, nome), vs in lig.items():
        for ator, decisao in vs:
            if vinculo(nome, ator, decisao, nome_ator[ator], civ):
                pares.add((ap, ator))
    com_parl = {ap for ap, _ in pares}
    d = pd.read_excel(DECISOES, dtype=str)
    d = d[d["Processo"].isin(lista.index)].copy()
    d["data"] = d["Data da decisão"].str[:10]
    linhas, fora = [], 0
    for ap, x in d.groupby("Processo"):
        aut = lista.loc[ap, "data_autuacao"]
        if aut < INICIO:
            fora += 1
            continue
        cat, dt = classificar(x)
        det = detalhe_outro(x) if cat == "outro" else ""
        origem = str(x["Descrição Órgão Origem"].iloc[0]).strip().upper()
        linhas.append({"ap": ap, "grupo": "com réu parlamentar" if ap in com_parl else "sem réu parlamentar ligado", "autuacao": aut,
                       "coorte": "até 2018-05-02" if aut < RESTRICAO else "a partir de 2018-05-03", "origem": "autuada no STF" if origem == "SUPREMO TRIBUNAL FEDERAL" else "vinda de outra instância",
                       "categoria": cat, "detalhe_outro": det, "data_desfecho": dt, "anos": max((pd.Timestamp(dt) - pd.Timestamp(aut)).days, 0) / 365.25, "evento": int(cat != "em_tramitacao")})
    sem_decisao = len(set(lista.index) - set(d["Processo"]))
    return pd.DataFrame(linhas), pares, {"autuadas_antes_de_2003": fora, "sem_decisao_na_exportacao": sem_decisao}


def distribuicao(a: pd.DataFrame, por: list) -> pd.DataFrame:
    linhas = []
    for chave, x in a.groupby(por):
        chave = chave if isinstance(chave, tuple) else (chave,)
        base = dict(zip(por, chave))
        for cat in ORDEM:
            k = int((x["categoria"] == cat).sum())
            linhas.append({**base, "desfecho": ROTULO[cat], "acoes": k, "total": len(x), "parcela": k / len(x)})
    return pd.DataFrame(linhas)


def tempos(a: pd.DataFrame, por: list) -> pd.DataFrame:
    linhas = []
    for chave, x in a.groupby(por):
        chave = chave if isinstance(chave, tuple) else (chave,)
        t, e = x["anos"].to_numpy(float), x["evento"].to_numpy(int)
        causa = np.where(e == 1, x["categoria"].to_numpy(str), "")
        lo, hi = bootstrap_mediana(t, e)
        l = {**dict(zip(por, chave)), "acoes": len(x), "encerradas": int(e.sum()), "mediana_anos": mediana_km(t, e), "mediana_ic95_inf": lo, "mediana_ic95_sup": hi}
        for h in HORIZONTES:
            for cat in ORDEM:
                if cat != "em_tramitacao":
                    l[f"{cat}_ate_{h}_anos"] = incidencia(t, causa, cat, h)
        linhas.append(l)
    return pd.DataFrame(linhas)


def run() -> None:
    a, pares, cont = acoes()
    a.to_csv(SAIDA / "foro_acoes.csv", index=False, encoding="utf-8")
    parl = a[a["grupo"] == "com réu parlamentar"]
    distribuicao(a, ["grupo"]).to_csv(SAIDA / "foro_desfechos.csv", index=False, encoding="utf-8")
    parl[parl["categoria"] == "outro"].groupby("detalhe_outro").size().rename("acoes").reset_index().sort_values("acoes", ascending=False).to_csv(
        SAIDA / "foro_outro_detalhe.csv", index=False, encoding="utf-8")
    pd.concat([distribuicao(parl, ["coorte"]).assign(recorte="coorte"), distribuicao(parl, ["origem"]).assign(recorte="origem")]).to_csv(
        SAIDA / "foro_desfechos_recortes.csv", index=False, encoding="utf-8")
    pd.concat([tempos(a, ["grupo"]).assign(recorte="grupo"), tempos(parl, ["coorte"]).assign(recorte="coorte"), tempos(parl, ["origem"]).assign(recorte="origem")]).to_csv(
        SAIDA / "foro_tempos.csv", index=False, encoding="utf-8")
    # série anual das decisões terminais das ações com réu parlamentar
    s = parl[parl["categoria"] != "em_tramitacao"].assign(ano=lambda x: x["data_desfecho"].str[:4])
    s.pivot_table(index="ano", columns="categoria", values="ap", aggfunc="count", fill_value=0).rename(columns=ROTULO).reset_index().to_csv(
        SAIDA / "foro_serie_anual.csv", index=False, encoding="utf-8")
    # pessoas: último status registrado de cada parlamentar x ação
    st, pr = ler("status_pessoa_processo"), ler("processos")
    idp = dict(zip(pr["numero_originario"], pr["id_processo"]))
    pp = pd.DataFrame([{"ap": ap, "id_ator": ator, "id_processo": idp.get(ap, "")} for ap, ator in pares if ap in set(parl["ap"])])
    ult = st.sort_values("data").drop_duplicates(["id_ator", "id_processo"], keep="last")
    pp = pp.merge(ult[["id_ator", "id_processo", "status", "data"]], on=["id_ator", "id_processo"], how="left")
    cat_ap = dict(zip(parl["ap"], parl["categoria"]))
    pp["status"] = [s if isinstance(s, str) else f"sem status de pessoa; a ação terminou em {ROTULO[cat_ap[ap]]}" for s, ap in zip(pp["status"], pp["ap"])]
    pp.groupby("status").size().rename("parlamentar_x_acao").reset_index().sort_values("parlamentar_x_acao", ascending=False).to_csv(
        SAIDA / "foro_pessoas.csv", index=False, encoding="utf-8")
    # simetria: mérito entre encerradas, por partido e grupo do réu na autuação
    fil, gov = ler("filiacoes").sort_values("data_inicio"), ler_tabela_governo()
    sigla = dict(zip(ler("instituicoes")["id_instituicao"], ler("instituicoes")["sigla"]))
    esc = ler("posicao_ideologica")
    esc = esc[esc["escala"] == "brc_2018"]
    media = dict(zip(esc["id_partido"], esc["media"].astype(float)))
    cat = dict(zip(parl["ap"], parl["categoria"]))
    aut = dict(zip(parl["ap"], parl["autuacao"]))
    u = pd.DataFrame([{"ap": ap, "id_ator": ator} for ap, ator in pares if ap in cat])
    u["id_partido"] = [partido_em(fil, x, aut[ap]) for ap, x in zip(u["ap"], u["id_ator"])]
    u["grupo"] = [grupo_na_data(gov, p, aut[ap]) if p else "sem_partido" for ap, p in zip(u["ap"], u["id_partido"])]
    u = u[[cat[ap] != "em_tramitacao" for ap in u["ap"]]].copy()
    u["merito"] = [cat[ap] == "merito" for ap in u["ap"]]
    linhas = [linha("merito_entre_encerradas", "2003-2026", "partido", p or "sem_partido", x["merito"].sum(), len(x), sigla.get(p, "sem partido na base")) for p, x in u.groupby("id_partido")]
    linhas += [linha("merito_entre_encerradas", "2003-2026", "governo_oposicao", g, x["merito"].sum(), len(x)) for g, x in u.groupby("grupo")]
    pd.DataFrame(linhas).to_csv(SAIDA / "foro_simetria.csv", index=False, encoding="utf-8")
    g = u.groupby("id_partido")["merito"].agg(["sum", "count"])
    g = g[(g["count"] >= 10) & (g.index != "")]
    testes = []
    est, p = homogeneidade(g["sum"].to_numpy(), g["count"].to_numpy())
    testes.append({"teste": "homogeneidade entre partidos", "grupos": len(g), "n": int(g["count"].sum()), "estatistica": est, "p_valor": p})
    go, op = u[u["grupo"] == "governo"], u[u["grupo"] == "oposicao"]
    testes.append({"teste": "governo x oposição (Fisher)", "grupos": 2, "n": len(go) + len(op), "estatistica": float("nan"),
                   "p_valor": fisher_exact([[int(go["merito"].sum()), len(go) - int(go["merito"].sum())], [int(op["merito"].sum()), len(op) - int(op["merito"].sum())]])[1]})
    cc = g[g.index.isin(media)]
    r, p = spearman_permutacao(pd.Series(cc.index).map(media).to_numpy(), (cc["sum"] / cc["count"]).to_numpy())
    testes.append({"teste": "Spearman com escore ideológico", "grupos": len(cc), "n": int(cc["count"].sum()), "estatistica": r, "p_valor": p})
    pd.DataFrame(testes).to_csv(SAIDA / "foro_simetria_testes.csv", index=False, encoding="utf-8")
    acervo = pd.read_excel(RAIZ / "data" / "raw" / "stf" / "2026-09-24" / "stf_corte_aberta_acervo_AP_Inq.xlsx", dtype=str)
    cont["com_reu_parlamentar_ainda_no_acervo_apos_desfecho"] = int(parl["ap"].isin(set(acervo.loc[acervo["Classe"] == "AP", "Processo"])).sum())
    pd.DataFrame([{**cont, "acoes_no_universo": len(a), "com_reu_parlamentar": len(parl), "pares_parlamentar_acao": len(pp), "pares_encerrados_para_simetria": len(u)}]).to_csv(
        SAIDA / "foro_cobertura.csv", index=False, encoding="utf-8")
    print(pd.read_csv(SAIDA / "foro_cobertura.csv").to_string(index=False))
    print(distribuicao(a, ["grupo"]).pivot(index="desfecho", columns="grupo", values="acoes").to_string())
    print(pd.read_csv(SAIDA / "foro_tempos.csv").round(2).T.to_string())
    print(pd.read_csv(SAIDA / "foro_outro_detalhe.csv").to_string(index=False))
    print(pd.read_csv(SAIDA / "foro_pessoas.csv").to_string(index=False))
    print(pd.DataFrame(testes).round(4).to_string(index=False))


if __name__ == "__main__":
    run()
