"""Normalização dos votos da Assembleia Geral da ONU (etapa E8, bloco A1) para `votos_multilaterais`.

Critério aprovado (docs/lista_e8_para_revisao.md, D-031), aplicado aos títulos e itens de agenda das
resoluções adotadas por voto nominal de 2003 em diante:

1. `direitos_humanos_pais`: título com "situation of human rights" ou "human rights situation"
   (situação de direitos humanos em um país específico, de qualquer região; dá o denominador);
2. `cita_america_latina`: título ou item de agenda que cita nominalmente um país da América Latina e
   do Caribe, a região ou a questão das Malvinas.

Entra o voto de todos os países em cada resolução selecionada (Y sim, N não, A abstenção, X ausente).

Uso:
    python -m src.normalizacao.onu_ag
"""

import csv
import re
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, gravar, ler

MANIFESTO = RAIZ / "data" / "manifestos" / "onu_ag.csv"
INICIO = "2003-01-01"
VOTOS = {"Y": "sim", "N": "nao", "A": "abstencao", "X": "ausente"}
AMERICA_LATINA = [
    "Antigua and Barbuda", "Argentina", "Bahamas", "Barbados", "Belize", "Bolivia", "Brazil", "Chile", "Colombia", "Costa Rica",
    "Cuba", "Dominica", "Dominican Republic", "Ecuador", "El Salvador", "Grenada", "Guatemala", "Guyana", "Haiti", "Honduras",
    "Jamaica", "Mexico", "Nicaragua", "Panama", "Paraguay", "Peru", "Saint Kitts and Nevis", "Saint Lucia",
    "Saint Vincent and the Grenadines", "Suriname", "Trinidad and Tobago", "Uruguay", "Venezuela",
    "Latin America", "Caribbean", "Central America", "Malvinas", "Falkland",
]
RE_DH = re.compile(r"situation of human rights|human rights situation", re.I)
RE_AL = re.compile(r"\b(?:" + "|".join(re.escape(x) for x in AMERICA_LATINA) + r")\b", re.I)


def criterio(titulo: str, agenda: str) -> str:
    """Regra de seleção que inclui a resolução, ou '' se nenhuma se aplica."""
    if RE_DH.search(titulo or ""):
        return "direitos_humanos_pais"
    if RE_AL.search(titulo or "") or RE_AL.search(agenda or ""):
        return "cita_america_latina"
    return ""


def titulo_curto(titulo: str) -> str:
    return re.sub(r"\s*:\s*resolution\s*/\s*adopted by the General Assembly\s*$", "", titulo or "", flags=re.I).strip()


def montar(ids: RegistroIds) -> dict:
    man = list(csv.DictReader(MANIFESTO.open(encoding="utf-8")))
    reg = max((m for m in man if m["arquivo"].endswith(".csv")), key=lambda m: m["data_acesso"])
    ag = ids.obter("instituicoes", "organismo:ONU_AG")
    inst = [{"id_instituicao": ag, "nome": "Assembleia Geral das Nações Unidas", "sigla": "AGNU", "tipo_instituicao": "organismo_multilateral",
             "poder": "nao_se_aplica", "esfera": "internacional", "pais_iso3": ""}]
    f = ids.obter("fontes", f"raw:{reg['arquivo']}")
    fontes = [{"id_fonte": f, "tipo_fonte": "oficial", "titulo": "UN Dag Hammarskjöld Library: General Assembly voting data, resoluções 1 a 80/246 (versão 5)",
               "data_publicacao": "2026-02-06", "url": "https://digitallibrary.un.org/record/4060887", "data_acesso": reg["data_acesso"], "sha256": reg["sha256"],
               "caminho_raw": reg["arquivo"], "licenca": "Copyright United Nations; uso não comercial, com atribuição",
               "observacao": "Download manual do autor (D-032); só resoluções adotadas por voto nominal"}]
    oficiais = [{"id_fonte": f, "id_orgao": ag, "tipo_documento": "Conjunto de dados de votação (CSV)", "data_documento": "2026-02-06",
                 "link": "https://digitallibrary.un.org/record/4060887"}]
    d = pd.read_csv(RAIZ / reg["arquivo"], dtype=str, keep_default_na=False,
                    usecols=["undl_id", "ms_code", "ms_vote", "date", "resolution", "title", "agenda_title", "undl_link"])
    d = d[d["date"] >= INICIO]
    res = d.drop_duplicates("undl_id").copy()
    res["criterio"] = [criterio(t, a) for t, a in zip(res["title"], res["agenda_title"])]
    sel = res[res["criterio"] != ""].set_index("undl_id")
    v = d[d["undl_id"].isin(sel.index)]
    votos = []
    for _, r in v.iterrows():
        s = sel.loc[r["undl_id"]]
        votos.append({"id_voto": ids.obter("votos_multilaterais", f"undl:{r['undl_id']}:{r['ms_code']}"), "id_organismo": ag,
                      "resolucao": r["resolution"], "titulo": titulo_curto(r["title"]), "tema": s["agenda_title"], "criterio_inclusao": s["criterio"],
                      "data": r["date"], "pais_iso3": r["ms_code"], "voto": VOTOS.get(r["ms_vote"], "ausente"), "link": r["undl_link"], "id_fonte": f})
    return {"instituicoes": inst, "fontes": fontes, "fonte_oficial": oficiais, "votos_multilaterais": votos,
            "n_resolucoes": len(res), "selecionadas": sel["criterio"].value_counts().to_dict()}


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    for nome in ("fontes", "fonte_oficial"):
        atual = ler(nome, base)
        novas = [l for l in r[nome] if l["id_fonte"] not in set(atual["id_fonte"])]
        gravar(nome, pd.concat([atual, pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    atual = ler("instituicoes", base)
    novas = pd.DataFrame(r["instituicoes"], dtype=str)
    gravar("instituicoes", pd.concat([atual[~atual["id_instituicao"].isin(novas["id_instituicao"])], novas], ignore_index=True), base)
    atual = ler("votos_multilaterais", base)
    novos = pd.DataFrame(r["votos_multilaterais"], dtype=str)
    org = novas["id_instituicao"].iloc[0]
    gravar("votos_multilaterais", pd.concat([atual[atual["id_organismo"] != org], novos], ignore_index=True), base)
    ids.salvar()


def run() -> None:
    ids = RegistroIds()
    r = montar(ids)
    gravar_resultado(r, ids)
    print(f"resoluções com voto nominal desde 2003: {r['n_resolucoes']}; selecionadas: {r['selecionadas']}; votos gravados: {len(r['votos_multilaterais'])}")


if __name__ == "__main__":
    run()
