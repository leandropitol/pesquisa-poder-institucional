"""Eixo 2 (relações externas): métricas por governo com as regras de D-053, fixadas antes do cálculo.

- Baixa qualidade democrática (BQD): status "Não Livre" (NF) na Freedom House no ano; sensibilidade: V-Dem
  Regimes of the World 0 ou 1. Ano sem índice: sem classificação.
- Votos (AGNU, CDH, AG/OEA): cada resolução recebe um tipo e um país-alvo por regras de título (REGRAS, na ordem);
  a métrica principal usa as de escrutínio de país. Parcela de Sim do Brasil entre Sim, Não e Abstenção, por
  governo, comparada, resolução a resolução, com a média das democracias (FH "Livre", sem o Brasil) e da América
  Latina e Caribe (GRULAC). Embargo dos EUA a Cuba em bloco separado.
- BNDES: parcela do valor contratado com destino BQD, por governo.
- Acordos bilaterais: parcela de atos assinados com país BQD, por governo, e a parcela de países BQD no mundo.
- Redes partidárias: quadro descritivo.

Saídas (geradas): relatorios/tabelas/eixo2_*.csv.

Uso:
    python -m src.analise.eixo2
"""

import re

import pandas as pd

from src.base import RAIZ, ler
from src.normalizacao.conselho_dh import chave_nome, nomes_iso
from src.simetria.governo_oposicao import presidencias

SAIDA = RAIZ / "relatorios" / "tabelas"
GRULAC = set("ATG ARG BHS BRB BLZ BOL BRA CHL COL CRI CUB DMA DOM ECU SLV GRD GTM GUY HTI HND JAM MEX NIC PAN PRY PER KNA LCA VCT SUR "
             "TTO URY VEN".split())
# (tipo, expressão no título, alvo fixo ou None para extrair do título, nota); a primeira que casa vale
REGRAS = [
    ("embargo_cuba", r"embargo imposed by the unite[ds] states", "CUB", "resolução pelo fim do embargo dos EUA; não é escrutínio do regime"),
    ("cooperacao_tecnica", r"technical (cooperation|assistance)|capacity-building|mission by the office", None, "cooperação técnica ou missão"),
    ("escrutinio", r"occupied palestinian territory|israeli military operations", "ISR", "alvo = potência ocupante ou autora das operações"),
    ("escrutinio", r"crimea|occupied territories of ukraine|russian aggression", "RUS", "alvo = potência ocupante ou agressora"),
    ("escrutinio", r"situation of human rights|human rights situation|promotion and protection of human rights", None, ""),
    ("outro", r"emenda ao projeto|inclus[aã]o no tem[aá]rio|remessa ao conselho", None, "votação de procedimento"),
    ("escrutinio", r"nicaragua", "NIC", "resolução da OEA sobre a situação no país"),
    ("escrutinio", r"venezuela", "VEN", "resolução da OEA sobre a situação no país"),
]


def classificar(titulo: str, mapa: dict[str, str], padrao: re.Pattern) -> tuple[str, str, str]:
    t = titulo.lower()
    for tipo, expr, alvo, nota in REGRAS:
        if re.search(expr, t):
            if alvo is None and tipo != "outro":
                achados = padrao.findall(chave_nome(titulo))
                alvo = mapa[achados[0]] if achados else ""
            return tipo, alvo or "", nota
    return "outro", "", ""


def bqd(q: pd.DataFrame) -> tuple[dict, dict]:
    fh = q[q["indice"] == "fh_status"]
    vd = q[q["indice"] == "vdem_row"]
    return (dict(zip(zip(fh["pais_iso3"], fh["ano"]), fh["valor"])), dict(zip(zip(vd["pais_iso3"], vd["ano"]), vd["valor"])))


def rotulo_bqd(iso: str, ano: str, fh: dict, vd: dict) -> tuple[str, str]:
    f, v = fh.get((iso, ano)), vd.get((iso, ano))
    return ("sem_classificacao" if f is None else "BQD" if f == "NF" else "nao_BQD",
            "sem_classificacao" if v is None else "BQD" if v in ("0", "1") else "nao_BQD")


def governo(data: str, pres: pd.DataFrame) -> str:
    for _, p in pres.iterrows():
        if p["inicio"] <= data[:10] and (p["fim"] == "" or data[:10] <= p["fim"]):
            return f"{p['presidente']} ({p['inicio'][:4]}-{p['fim'][:4] or ''})"
    return "antes de 2003"


def resolucoes(v: pd.DataFrame, sigla: dict) -> pd.DataFrame:
    mapa = nomes_iso()
    # o apóstrofo curvo some na normalização ("PEOPLE’S" vira "PEOPLES"); sem o alias, a Coreia do Norte cairia em "REPUBLIC OF KOREA"
    mapa.update({"NICARAGUA": "NIC", "VENEZUELA": "VEN", "DEMOCRATIC PEOPLES REPUBLIC OF KOREA": "PRK"})
    padrao = re.compile("|".join(re.escape(k) for k in sorted(mapa, key=len, reverse=True)))
    r = v.drop_duplicates(["id_organismo", "resolucao"])[["id_organismo", "resolucao", "titulo", "data"]].copy()
    r["organismo"] = r["id_organismo"].map(sigla)
    r[["tipo", "alvo_iso3", "nota"]] = [classificar(t, mapa, padrao) for t in r["titulo"]]
    return r


def votos(v: pd.DataFrame, r: pd.DataFrame, fh: dict, vd: dict, pres: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    x = v.merge(r[["id_organismo", "resolucao", "tipo", "alvo_iso3", "organismo"]], on=["id_organismo", "resolucao"])
    x["ano"] = x["data"].str[:4]
    x["valido"] = x["voto"].isin(["sim", "nao", "abstencao"])
    x["sim"] = (x["voto"] == "sim").astype(int)
    x["fh_votante"] = [fh.get((p, a)) for p, a in zip(x["pais_iso3"], x["ano"])]
    por_res = []
    for (org, res), g in x.groupby(["organismo", "resolucao"]):
        br = g[g["pais_iso3"] == "BRA"]
        if not len(br):
            continue
        val = g[g["valido"]]
        dem = val[(val["fh_votante"] == "F") & (val["pais_iso3"] != "BRA")]
        lac = val[val["pais_iso3"].isin(GRULAC - {"BRA"})]
        a, ano = g["alvo_iso3"].iloc[0], g["ano"].iloc[0]
        b_fh, b_vd = rotulo_bqd(a, ano, fh, vd) if a else ("", "")
        por_res.append({"organismo": org, "resolucao": res, "data": g["data"].iloc[0], "governo": governo(g["data"].iloc[0], pres),
                        "tipo": g["tipo"].iloc[0], "alvo_iso3": a, "alvo_bqd_fh": b_fh, "alvo_bqd_vdem": b_vd, "voto_brasil": br["voto"].iloc[0],
                        "sim_democracias": round(dem["sim"].mean(), 4) if len(dem) else None, "n_democracias": len(dem),
                        "sim_america_latina": round(lac["sim"].mean(), 4) if len(lac) else None, "n_america_latina": len(lac)})
    pr = pd.DataFrame(por_res).sort_values("data")

    def resumo(sub: pd.DataFrame) -> dict:
        val = sub[sub["voto_brasil"].isin(["sim", "nao", "abstencao"])]
        return {"n_resolucoes": len(sub), "n_votos_validos_brasil": len(val),
                "brasil_sim": int((val["voto_brasil"] == "sim").sum()), "brasil_nao": int((val["voto_brasil"] == "nao").sum()),
                "brasil_abstencao": int((val["voto_brasil"] == "abstencao").sum()),
                "brasil_outros": int((~sub["voto_brasil"].isin(["sim", "nao", "abstencao"])).sum()),
                "parcela_sim_brasil": round((val["voto_brasil"] == "sim").mean(), 4) if len(val) else None,
                "media_sim_democracias": round(val["sim_democracias"].mean(), 4) if len(val) else None,
                "media_sim_america_latina": round(val["sim_america_latina"].mean(), 4) if len(val) else None}

    linhas = []
    esc = pr[pr["tipo"] == "escrutinio"]
    recortes = [("escrutínio, alvo BQD (FH)", esc[esc["alvo_bqd_fh"] == "BQD"]), ("escrutínio, alvo BQD (V-Dem)", esc[esc["alvo_bqd_vdem"] == "BQD"]),
                ("escrutínio, todos os alvos", esc), ("embargo dos EUA a Cuba", pr[pr["tipo"] == "embargo_cuba"]),
                ("cooperação técnica", pr[pr["tipo"] == "cooperacao_tecnica"])]
    for nome, sub in recortes:
        for gov, g in sub.groupby("governo", sort=False):
            linhas.append({"recorte": nome, "governo": gov, **resumo(g)})
    return pr, pd.DataFrame(linhas)


def bndes(b: pd.DataFrame, fh: dict, vd: dict, pres: pd.DataFrame) -> pd.DataFrame:
    b = b.copy()
    b["valor"] = pd.to_numeric(b["valor"], errors="coerce").fillna(0)
    b["ano"] = b["data_contratacao"].str[:4]
    b["governo"] = [governo(d, pres) for d in b["data_contratacao"]]
    b[["bqd_fh", "bqd_vdem"]] = [rotulo_bqd(p, a, fh, vd) for p, a in zip(b["pais_iso3"], b["ano"])]
    # o arquivo aberto só publica valor nas operações de serviços de engenharia (todas em dólar, até 2015); nas de bens
    # não há valor, e a comparação entre todos os governos usa a contagem de operações
    linhas = []
    for gov, g in b.groupby("governo", sort=False):
        s = g[g["linha_de_apoio"].str.contains("engenharia")]
        tot = s["valor"].sum()
        top = s.groupby("pais_iso3")["valor"].sum().sort_values(ascending=False).head(5)
        cl = g[g["bqd_fh"] != "sem_classificacao"]
        topn = g["pais_iso3"].value_counts().head(5)
        linhas.append({"governo": gov, "n_operacoes": len(g), "n_com_indice_fh": len(cl),
                       "parcela_operacoes_bqd_fh": round((cl["bqd_fh"] == "BQD").mean(), 4) if len(cl) else None,
                       "parcela_operacoes_bqd_vdem": round((g.loc[g["bqd_vdem"] != "sem_classificacao", "bqd_vdem"] == "BQD").mean(), 4),
                       "principais_destinos_por_operacoes": "; ".join(f"{p} {n / len(g):.0%}" for p, n in topn.items()),
                       "n_servicos_engenharia": len(s), "valor_servicos_engenharia_usd": round(tot, 2),
                       "parcela_valor_servicos_bqd_fh": round(s.loc[s["bqd_fh"] == "BQD", "valor"].sum() / tot, 4) if tot else None,
                       "parcela_valor_servicos_bqd_vdem": round(s.loc[s["bqd_vdem"] == "BQD", "valor"].sum() / tot, 4) if tot else None,
                       "principais_destinos_servicos_por_valor": "; ".join(f"{p} {v / tot:.0%}" for p, v in top.items()) if tot else ""})
    ordem = {g: i for i, g in enumerate(sorted(b["governo"].unique(), key=lambda s: s[-10:]))}
    return pd.DataFrame(linhas).sort_values("governo", key=lambda s: s.map(ordem))


def acordos(a: pd.DataFrame, fh: dict, vd: dict, pres: pd.DataFrame) -> pd.DataFrame:
    a = a[a["data_assinatura"] >= "2003"].copy()
    a["ano"] = a["data_assinatura"].str[:4]
    a["governo"] = [governo(d, pres) for d in a["data_assinatura"]]
    a[["bqd_fh", "bqd_vdem"]] = [rotulo_bqd(p, y, fh, vd) for p, y in zip(a["pais_iso3"], a["ano"])]
    mundo = pd.Series({ano: sum(1 for (p, y), s in fh.items() if y == ano and s == "NF") / max(1, sum(1 for (p, y) in fh if y == ano))
                       for ano in a["ano"].unique()})
    linhas = []
    for gov, g in a.groupby("governo", sort=False):
        cl = g[g["bqd_fh"] != "sem_classificacao"]
        linhas.append({"governo": gov, "n_atos": len(g), "n_com_indice_fh": len(cl),
                       "parcela_atos_bqd_fh": round((cl["bqd_fh"] == "BQD").mean(), 4) if len(cl) else None,
                       "parcela_paises_bqd_no_mundo_fh": round(g["ano"].map(mundo).mean(), 4),
                       "parcela_atos_bqd_vdem": round((g.loc[g["bqd_vdem"] != "sem_classificacao", "bqd_vdem"] == "BQD").mean(), 4)})
    return pd.DataFrame(linhas)


def redes(rel: pd.DataFrame, sigla: dict, nome: dict) -> pd.DataFrame:
    x = rel[rel["tipo_relacao"].isin(["membro_de", "observador_de"])]
    return pd.DataFrame({"partido": x["origem_id"].map(sigla), "rede": x["destino_id"].map(nome), "tipo": x["tipo_relacao"],
                         "inicio_observado": x["data_inicio"], "fim_observado": x["data_fim"]}).sort_values(["rede", "partido"])


def run() -> None:
    inst = ler("instituicoes")
    sigla = dict(zip(inst["id_instituicao"], inst["sigla"]))
    nome = dict(zip(inst["id_instituicao"], inst["nome"]))
    fh, vd = bqd(ler("qualidade_democratica"))
    pres = presidencias()
    SAIDA.mkdir(parents=True, exist_ok=True)
    v = ler("votos_multilaterais")
    r = resolucoes(v, sigla)
    r.to_csv(SAIDA / "eixo2_resolucoes_classificadas.csv", index=False, lineterminator="\n")
    pr, rv = votos(v, r, fh, vd, pres)
    pr.to_csv(SAIDA / "eixo2_votos_por_resolucao.csv", index=False, lineterminator="\n")
    rv.to_csv(SAIDA / "eixo2_votos_por_governo.csv", index=False, lineterminator="\n")
    bn = bndes(ler("operacoes_exportacao_bndes"), fh, vd, pres)
    bn.to_csv(SAIDA / "eixo2_bndes_por_governo.csv", index=False, lineterminator="\n")
    ac = acordos(ler("acordos_bilaterais"), fh, vd, pres)
    ac.to_csv(SAIDA / "eixo2_acordos_por_governo.csv", index=False, lineterminator="\n")
    rd = redes(ler("relacoes"), sigla, nome)
    rd.to_csv(SAIDA / "eixo2_redes_partidarias.csv", index=False, lineterminator="\n")
    print(r.groupby(["organismo", "tipo"]).size().to_string())
    print("escrutínio sem alvo:", r[(r["tipo"] == "escrutinio") & (r["alvo_iso3"] == "")]["titulo"].str[:80].tolist())
    print("tabelas em relatorios/tabelas/eixo2_*.csv")


if __name__ == "__main__":
    run()
