"""Eixo 3, primeira parte (D-067): relator x presidente que indicou (E3-a) e uso do foro (E3-b), ações penais do STF com réu parlamentar.

E3-a: parlamentar x ação penal com desfecho de mérito na base (D-065). Ministro = "Nome Ministro(a)" da decisão do Corte Aberta na data do desfecho;
válido só se estava em exercício (composição do STF, D-058). A = indicado por presidente do PT (registro no TSE, D-059) ou por outro presidente;
D = réu filiado ao PT na data do desfecho (sensibilidade: partido de esquerda, centro-esquerda ou extrema-esquerda, D-062).
E3-b: ações penais com réu parlamentar de vínculo confirmado; medida = há decisão "Declinada a competência"; segunda medida = declínio com o réu ainda em mandato.

Saídas em relatorios/tabelas: eixo3_relator_ministros.csv, eixo3_relator_presidentes.csv, eixo3_relator_2x2.csv, eixo3_foro_taxas.csv,
eixo3_foro_testes.csv e eixo3_cobertura.csv.

Uso:
    python -m src.analise.eixo3
"""

import pandas as pd
from scipy.stats import fisher_exact

from src.analise.eixo1 import homogeneidade
from src.analise.etica import PERIODOS, linha, partido_em
from src.analise.ideologia import ORDEM, spearman_permutacao
from src.analise.stf_desfechos import julgados
from src.base import BASE, RAIZ, ler
from src.normalizacao.simetria_stf import carregar
from src.normalizacao.stf_desfechos import DECISOES, nomes_civis, vinculo
from src.normalizacao.tse import norm
from src.simetria.governo_oposicao import grupo_na_data, ler_tabela as ler_tabela_governo
from src.simetria.taxa_bancada import wilson

SAIDA = RAIZ / "relatorios" / "tabelas"
ESQUERDA = {"extrema_esquerda", "esquerda", "centro_esquerda"}
RESTRICAO_FORO = "2018-05-03"  # questão de ordem na AP 937
MIN_ACOES = 10


def decisoes_ap() -> pd.DataFrame:
    d = pd.read_excel(DECISOES, dtype=str)
    d = d[d["Processo"].str.startswith("AP ")].copy()
    d["data"] = d["Data da decisão"].str[:10]
    d["ministro"] = d["Nome Ministro (a)"].map(lambda x: norm(str(x).replace("MIN.", "")))
    return d


def composicao() -> pd.DataFrame:
    c = pd.read_csv(SAIDA / "stf_composicao.csv", dtype=str).fillna("")
    c["chave"] = c["nome_guerra"].map(norm)
    pres = pd.read_csv(SAIDA / "presidencias_partido.csv", dtype=str)
    pt = set(pres.loc[pres["sigla_tse"] == "PT", "presidente"])
    c["indicado_por_pt"] = c["presidente"].isin(pt)
    return c


def resolver_ministro(ap: str, data: str, dec: pd.DataFrame, comp: pd.DataFrame):
    """Ministro da decisão na data; sem decisão na data ou com vários ministros, o que mais aparece nas decisões da ação até a data (relator da ação)."""
    da_ap = dec[dec["Processo"] == ap]
    m = set(da_ap.loc[da_ap["data"] == data, "ministro"])
    if len(m) != 1:  # sem decisão na data (desfecho por notícia oficial) ou vários ministros (sessão plenária): relator da ação até a data
        ate = da_ap.loc[da_ap["data"] <= data, "ministro"]
        m = {ate.value_counts().index[0]} if len(ate) else set()
    if len(m) != 1:
        return None
    c = comp[comp["chave"] == next(iter(m))]
    if len(c) != 1:
        return None
    c = c.iloc[0]
    if c["data_posse"] <= data and (c["data_fim"] == "" or data <= c["data_fim"]):
        return c
    return None


def eh_turma(ap: str, data: str, dec: pd.DataFrame) -> bool:
    """Julgamento de Turma: a origem colegiada mais frequente nas decisões da ação até a data é uma Turma (e não o Plenário)."""
    o = dec[(dec["Processo"] == ap) & (dec["data"] <= data)]["Origem decisão"]
    o = o[o.isin(["1ª TURMA", "2ª TURMA", "TRIBUNAL PLENO"])]
    return bool(len(o)) and o.value_counts().index[0] != "TRIBUNAL PLENO"


def tabela_2x2(nome: str, x: pd.DataFrame) -> dict:
    a, b = x[x["indicado_por_pt"]], x[~x["indicado_por_pt"]]
    ka, kb = int(a["condenado"].sum()), int(b["condenado"].sum())
    p = fisher_exact([[ka, len(a) - ka], [kb, len(b) - kb]])
    return {"recorte": nome, "julgados_indicados_pt": len(a), "condenados_indicados_pt": ka, "taxa_indicados_pt": ka / len(a) if len(a) else float("nan"),
            "julgados_outros": len(b), "condenados_outros": kb, "taxa_outros": kb / len(b) if len(b) else float("nan"), "razao_de_chances": p[0], "p_fisher": p[1]}


def relator_x_indicacao() -> dict:
    s = julgados()
    dec, comp = decisoes_ap(), composicao()
    inst = ler("instituicoes")
    pt = inst[(inst["sigla"] == "PT") & (inst["tipo_instituicao"] == "partido")]["id_instituicao"].iloc[0]
    esc = ler("posicao_ideologica")
    esc = esc[esc["escala"] == "brc_2018"]
    faixa = dict(zip(esc["id_partido"], esc["faixa"]))
    linhas = [resolver_ministro(ap, d, dec, comp) for ap, d in zip(s["numero_originario"], s["data"])]
    s["resolvido"] = [m is not None for m in linhas]
    nao = s[~s["resolvido"]]
    s = s[s["resolvido"]].copy()
    ok = [m for m in linhas if m is not None]
    s["ministro"] = [m["nome_guerra"] for m in ok]
    s["indicou"] = [m["presidente"] for m in ok]
    s["indicado_por_pt"] = [bool(m["indicado_por_pt"]) for m in ok]
    s["reu_pt"] = s["id_partido"] == pt
    s["reu_esquerda"] = s["id_partido"].map(faixa).isin(ESQUERDA)
    s["turma"] = [eh_turma(ap, d, dec) for ap, d in zip(s["numero_originario"], s["data"])]
    por_min = []
    for (m, pres), x in s.groupby(["ministro", "indicou"]):
        por_min.append(linha("condenacao_entre_julgados", "2003-2026", "ministro", m, x["condenado"].sum(), len(x), pres))
    pd.DataFrame(por_min).rename(columns={"sigla": "indicado_por", "n_unidades": "n_julgados", "com_registro": "condenados"}).drop(columns=["medida", "recorte"]).to_csv(
        SAIDA / "eixo3_relator_ministros.csv", index=False, encoding="utf-8")
    por_pres = [linha("condenacao_entre_julgados", "2003-2026", "presidente_que_indicou", p, x["condenado"].sum(), len(x)) for p, x in s.groupby("indicou")]
    pd.DataFrame(por_pres).rename(columns={"n_unidades": "n_julgados", "com_registro": "condenados"}).drop(columns=["medida", "recorte", "sigla"]).to_csv(
        SAIDA / "eixo3_relator_presidentes.csv", index=False, encoding="utf-8")
    sem470 = s[s["numero_originario"] != "AP 470"]
    recortes = [("total", s), ("réu do PT", s[s["reu_pt"]]), ("réu de outro partido", s[~s["reu_pt"]]),
                ("réu de partido de esquerda", s[s["reu_esquerda"]]), ("réu de partido fora da esquerda", s[~s["reu_esquerda"]]),
                ("total, sem a AP 470", sem470), ("réu do PT, sem a AP 470", sem470[sem470["reu_pt"]]), ("réu de outro partido, sem a AP 470", sem470[~sem470["reu_pt"]]),
                ("total, só Turma", s[s["turma"]]), ("réu do PT, só Turma", s[s["turma"] & s["reu_pt"]]), ("réu de outro partido, só Turma", s[s["turma"] & ~s["reu_pt"]])]
    t2 = pd.DataFrame([tabela_2x2(n, x) for n, x in recortes])
    t2.to_csv(SAIDA / "eixo3_relator_2x2.csv", index=False, encoding="utf-8")
    return {"julgados": len(s), "nao_resolvidos": len(nao), "nao_resolvidos_lista": nao[["numero_originario", "data"]], "t2": t2, "ministros": pd.DataFrame(por_min)}


def uso_do_foro() -> dict:
    c = carregar()
    lig, lista = c["lig"], c["lista"]
    atores, cargos = ler("atores"), ler("cargos")
    nome_ator = dict(zip(atores["id_ator"], atores["nome_normalizado"]))
    civ = nomes_civis(atores, cargos, ler("filiacoes"), BASE)
    dec = decisoes_ap()
    dec = dec[dec["Andamento decisão"] == "Declinada a competência"]
    primeiro = dec.groupby("Processo")["data"].min().to_dict()
    fil, gov = ler("filiacoes").sort_values("data_inicio"), ler_tabela_governo()
    esc = ler("posicao_ideologica")
    esc = esc[esc["escala"] == "brc_2018"]
    faixa, media = dict(zip(esc["id_partido"], esc["faixa"])), dict(zip(esc["id_partido"], esc["media"].astype(float)))
    sigla = dict(zip(ler("instituicoes")["id_instituicao"], ler("instituicoes")["sigla"]))
    mandatos = cargos[cargos["cargo"].str.startswith(("Deputado federal (titular)", "Deputado federal", "Senador (titular)"))]
    unidades = {}
    for (ap, nome), vs in lig.items():
        if ap not in lista.index:
            continue
        for ator, decisao in vs:
            if vinculo(nome, ator, decisao, nome_ator[ator], civ):
                unidades[(ap, ator)] = lista.loc[ap, "data_autuacao"]
    linhas = []
    for (ap, ator), aut in unidades.items():
        p = partido_em(fil, ator, aut)
        d = primeiro.get(ap, "")
        m = mandatos[mandatos["id_ator"] == ator]
        em_mandato = bool(d) and bool(((m["data_inicio"] <= d) & ((m["data_fim"] == "") | (m["data_fim"] >= d))).any())
        linhas.append({"ap": ap, "id_ator": ator, "autuacao": aut, "id_partido": p, "grupo": grupo_na_data(gov, p, aut) if p else "sem_partido",
                       "faixa": faixa.get(p, "sem_escore") if p else "sem_partido", "declinio": bool(d), "declinio_em_mandato": em_mandato,
                       "periodo": "antes da restrição do foro (até 2018-05-02)" if aut < RESTRICAO_FORO else "depois da restrição do foro"})
    u = pd.DataFrame(linhas)
    saidas, testes = [], []
    for recorte, x in (("todas as ações", u), ("antes da restrição do foro", u[u["periodo"].str.startswith("antes")])):
        for medida in ("declinio", "declinio_em_mandato"):
            for tipo, col in (("partido", "id_partido"), ("governo_oposicao", "grupo"), ("faixa_ideologica", "faixa")):
                for g, y in x.groupby(col):
                    saidas.append(linha(medida, recorte, tipo, g or "sem_partido", y[medida].sum(), len(y), sigla.get(g, g) if tipo == "partido" else ""))
            gp = x.groupby("id_partido")[medida].agg(["sum", "count"])
            gp = gp[(gp["count"] >= MIN_ACOES) & (gp.index != "")]
            if len(gp) >= 2 and gp["sum"].sum() > 0:
                est, p = homogeneidade(gp["sum"].to_numpy(), gp["count"].to_numpy())
                testes.append({"medida": medida, "recorte": recorte, "teste": "homogeneidade entre partidos", "grupos": len(gp), "n": int(gp["count"].sum()), "estatistica": est, "p_valor": p})
            go, op = x[x["grupo"] == "governo"], x[x["grupo"] == "oposicao"]
            ka, kb = int(go[medida].sum()), int(op[medida].sum())
            if len(go) and len(op):
                testes.append({"medida": medida, "recorte": recorte, "teste": "governo x oposição (Fisher)", "grupos": 2, "n": len(go) + len(op), "estatistica": float("nan"),
                               "p_valor": fisher_exact([[ka, len(go) - ka], [kb, len(op) - kb]])[1]})
            cc = gp[gp.index.isin(media)]
            if len(cc) >= 5 and cc["sum"].sum() > 0:
                r, p = spearman_permutacao(pd.Series(cc.index).map(media).to_numpy(), (cc["sum"] / cc["count"]).to_numpy())
                testes.append({"medida": medida, "recorte": recorte, "teste": "Spearman com escore ideológico", "grupos": len(cc), "n": int(cc["count"].sum()), "estatistica": r, "p_valor": p})
    # checagem de confusão por época, acrescentada depois de ver o resultado agregado (D-067): governo x oposição dentro de cada período presidencial da autuação
    por_periodo = []
    for nome, ini, fim in PERIODOS:
        x = u[(u["autuacao"] >= ini) & (u["autuacao"] <= fim)]
        go, op = x[x["grupo"] == "governo"], x[x["grupo"] == "oposicao"]
        for medida in ("declinio", "declinio_em_mandato"):
            ka, kb = int(go[medida].sum()), int(op[medida].sum())
            por_periodo.append({"medida": medida, "periodo": nome, "n_governo": len(go), "com_governo": ka, "taxa_governo": ka / len(go) if len(go) else float("nan"),
                                "n_oposicao": len(op), "com_oposicao": kb, "taxa_oposicao": kb / len(op) if len(op) else float("nan"),
                                "p_fisher": fisher_exact([[ka, len(go) - ka], [kb, len(op) - kb]])[1] if len(go) and len(op) and ka + kb else float("nan")})
    pd.DataFrame(por_periodo).to_csv(SAIDA / "eixo3_foro_governo_periodo.csv", index=False, encoding="utf-8")
    t = pd.DataFrame(saidas)
    t["ordem"] = t["grupo"].map({f: i for i, f in enumerate(ORDEM)}).fillna(99)
    t.sort_values(["medida", "recorte", "grupo_tipo", "ordem", "grupo"]).drop(columns="ordem").rename(columns={"n_unidades": "n_acoes", "com_registro": "com_declinio"}).to_csv(
        SAIDA / "eixo3_foro_taxas.csv", index=False, encoding="utf-8")
    pd.DataFrame(testes).to_csv(SAIDA / "eixo3_foro_testes.csv", index=False, encoding="utf-8")
    return {"unidades": len(u), "com_declinio": int(u["declinio"].sum()), "em_mandato": int(u["declinio_em_mandato"].sum()), "testes": pd.DataFrame(testes)}


def run() -> None:
    a = relator_x_indicacao()
    b = uso_do_foro()
    pd.DataFrame([{"julgados_resolvidos": a["julgados"], "julgados_sem_ministro_resolvido": a["nao_resolvidos"], "acoes_x_reu_no_foro": b["unidades"],
                   "com_declinio": b["com_declinio"], "declinio_com_reu_em_mandato": b["em_mandato"]}]).to_csv(SAIDA / "eixo3_cobertura.csv", index=False, encoding="utf-8")
    print(f"E3-a: resolvidos {a['julgados']}, sem ministro {a['nao_resolvidos']}")
    print(a["t2"].round(3).to_string(index=False))
    print(a["ministros"].round(3).to_string(index=False))
    print(f"E3-b: {b['unidades']} ação x réu; declínio {b['com_declinio']}; com réu em mandato {b['em_mandato']}")
    print(b["testes"].round(4).to_string(index=False))


if __name__ == "__main__":
    run()
