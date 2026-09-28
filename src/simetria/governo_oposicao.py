"""Classificação de partidos em base do governo, oposição ou nenhum dos dois, por mandato presidencial e ano (D-050).

Fonte: orientações de bancada nas votações nominais do Plenário da Câmara (bruto de src.coleta.camara_orientacoes),
com a orientação do Governo ("GOV." ou "Governo"). Regra, fixada antes do cálculo:

- unidade: partido x mandato presidencial x ano civil (data_curadoria/presidencias.csv);
- concordância: votações em que o partido orientou igual ao Governo, sobre as votações em que os dois orientaram
  Sim ou Não;
- base do governo: concordância >= 2/3; oposição: < 1/2; entre as duas, nenhum; < 10 votações comparáveis, sem
  classificação;
- federação: orientação vale para cada partido membro; bloco parlamentar fica fora;
- sensibilidade: Obstrução contada como Não (coluna própria).

Sigla da Câmara -> partido da base: denominações com datas de vigência (tabela denominacoes_partido), mais as
formas abreviadas do arquivo (ALIAS). Sigla sem correspondência é contada e listada.

Saída (gerada): relatorios/tabelas/governo_oposicao_partidos.csv.

Uso:
    python -m src.simetria.governo_oposicao
"""

import csv
import re
import glob
import unicodedata

import pandas as pd

from src.base import RAIZ, ler

RAW = RAIZ / "data" / "raw" / "camara_orientacoes"
SAIDA = RAIZ / "relatorios" / "tabelas" / "governo_oposicao_partidos.csv"
GOVERNO = {"GOV.", "Governo"}
FEDERACOES = {"Fdr PT-PCdoB-PV": ["PT", "PCDOB", "PV"], "Fdr PSOL-REDE": ["PSOL", "REDE"], "Fdr PSDB-CIDADANIA": ["PSDB", "CIDADANIA"]}
ALIAS = {"SOLIDARIED": ["SOLIDARIEDADE", "SD"], "SDD": ["SD", "SOLIDARIEDADE"], "SOLIDARIEDADE": ["SOLIDARIEDADE", "SD"],
         "REPUBLICAN": ["REPUBLICANOS"], "PODEMOS": ["PODE"], "PATRIOTA": ["PATRIOTA", "PATRI"], "UNIAO": ["UNIÃO"], "UNIÃO": ["UNIÃO"],
         "MISSAO": ["MISSÃO"], "MISSÃO": ["MISSÃO"]}
BASE_MIN, OPOSICAO_MAX, MIN_VOTACOES = 2 / 3, 1 / 2, 10
# D-051: nome de bloco -> partidos listados (formas abreviadas do arquivo); "Fdr" antes de um partido traz a federação
ABREV = {"UNI": "UNIÃO", "CID": "CIDADANIA", "REP": "REPUBLICANOS", "AVAN": "AVANTE", "SOLID": "SOLIDARIEDADE", "SD": "SD"}
FDR = {"PT": ["PCDOB", "PV"], "PSDB": ["CIDADANIA"], "PSOL": ["REDE"]}
PRIORIDADE = {"proprio": 0, "federacao": 1, "bloco": 2}


def membros_bloco(nome: str) -> list[str]:
    """Partidos listados no nome do bloco ("PpMdbPtb", "Bl MdbPsdRepPode", "Bl UniPpFdrPsdbCid..."). Nome cortado com
    reticências: só os partidos listados."""
    s = re.sub(r"^Bl\s+", "", nome).rstrip(".").strip()
    s = re.sub(r"(?i)pcdob", "|PCDOB|", s)
    s = re.sub(r"(?i)ptdob", "|PTDOB|", s)
    partes = []
    for bloco in re.split(r"[|/]", s):
        # sigla toda em maiúsculas ("PT" em "FdrPTUni") ou palavra iniciada por maiúscula ("Pp", "Mdb")
        partes += [bloco] if bloco in ("PCDOB", "PTDOB") else re.findall(r"[A-Z]{2,}(?=[A-Z][a-z]|$)|[A-Z][a-z]*", bloco)
    saida, fdr = [], False
    for t in partes:
        t = t.upper()
        if t == "FDR":
            fdr = True
            continue
        t = ABREV.get(t, t)
        saida.append(t)
        if fdr:
            saida += FDR.get(t, [])
            fdr = False
    return list(dict.fromkeys(saida))


def eh_bloco(sigla: str) -> bool:
    return sigla.startswith("Bl ") or "/" in sigla or bool(re.match(r"^[A-Z][a-z]+[A-Z]", sigla))


def sem_acento(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


class Siglas:
    """Sigla da Câmara e data -> id do partido, pela vigência das denominações."""

    def __init__(self, denominacoes: pd.DataFrame):
        self.d = denominacoes.fillna("")
        self.sem = {}

    def __call__(self, sigla: str, data: str) -> str | None:
        s = sigla.strip().upper()
        formas = ALIAS.get(s) or ALIAS.get(sem_acento(s)) or [s]
        c = self.d[self.d["sigla"].isin(formas)]
        if not len(c):
            self.sem[sigla] = self.sem.get(sigla, 0) + 1
            return None
        vig = c[((c["data_inicio"] == "") | (c["data_inicio"] <= data)) & ((c["data_fim"] == "") | (c["data_fim"] >= data))]
        if len(vig["id_partido"].unique()) == 1:
            return vig["id_partido"].iloc[0]
        if len(c["id_partido"].unique()) == 1:
            return c["id_partido"].iloc[0]  # sigla de um só partido fora da vigência registrada (registro da Câmara atrasado)
        self.sem[sigla] = self.sem.get(sigla, 0) + 1
        return None


def presidencias() -> pd.DataFrame:
    return pd.read_csv(RAIZ / "data" / "curadoria" / "presidencias.csv", dtype=str).fillna("")


def segmento(data: str, pres: pd.DataFrame) -> tuple[str, str, str] | None:
    """(presidente, início, fim) do trecho mandato x ano civil que contém a data."""
    for _, p in pres.iterrows():
        if p["inicio"] <= data and (p["fim"] == "" or data <= p["fim"]):
            ano = data[:4]
            ini = max(p["inicio"], f"{ano}-01-01")
            fim = min(p["fim"] or "9999-12-31", f"{ano}-12-31")
            return (p["presidente"], ini, fim)
    return None


def ler_bruto() -> tuple[pd.DataFrame, pd.DataFrame]:
    arqs = sorted(glob.glob(str(RAW / "*" / "votacoesOrientacoes-*.csv")))
    o = pd.concat([pd.read_csv(f, sep=";", dtype=str, encoding="utf-8-sig") for f in arqs])
    v = pd.concat([pd.read_csv(f, sep=";", dtype=str, encoding="utf-8-sig", usecols=["id", "data"])
                   for f in sorted(glob.glob(str(RAW / "*" / "votacoes-*.csv")))])
    return o, v


def orientacoes_por_partido(o: pd.DataFrame, v: pd.DataFrame, siglas: Siglas) -> pd.DataFrame:
    """Uma linha por votação do Plenário x partido, com a orientação do partido e a do Governo."""
    o = o[o["siglaOrgao"] == "PLEN"].merge(v.rename(columns={"id": "idVotacao"}), on="idVotacao", how="left")
    gov = o[o["siglaBancada"].isin(GOVERNO)].drop_duplicates("idVotacao").set_index("idVotacao")["orientacao"]
    o = o[o["idVotacao"].isin(gov.index) & ~o["siglaBancada"].isin(GOVERNO)]
    linhas = []
    for r in o.itertuples(index=False):
        if r.siglaBancada.upper().startswith(("MINORIA", "MAIORIA", "OPOSIÇÃO", "BLOCO PARLAMENTAR")):
            continue
        if r.siglaBancada in FEDERACOES:
            membros, via = FEDERACOES[r.siglaBancada], "federacao"
        elif eh_bloco(r.siglaBancada):
            membros, via = membros_bloco(r.siglaBancada), "bloco"
        else:
            membros, via = [r.siglaBancada], "proprio"
        for m in membros:
            p = siglas(m, r.data)
            if p:
                linhas.append({"idVotacao": r.idVotacao, "data": r.data, "id_partido": p, "orientacao": r.orientacao,
                               "gov": gov[r.idVotacao], "via": via})
    x = pd.DataFrame(linhas)
    # mesma votação e partido por mais de uma via: vale a orientação própria, depois a da federação, depois a do bloco
    return x.assign(_o=x["via"].map(PRIORIDADE)).sort_values("_o").drop_duplicates(["idVotacao", "id_partido"]).drop(columns="_o")


def grupo_de(c: float, n: int) -> str:
    return "sem_classificacao" if n < MIN_VOTACOES else "governo" if c >= BASE_MIN else "oposicao" if c < OPOSICAO_MAX else "nenhum"


def concordancia(g: pd.DataFrame, obstrucao_como_nao: bool = False) -> tuple[int, int, float]:
    o, gv = g["orientacao"], g["gov"]
    if obstrucao_como_nao:
        o, gv = o.where(o != "Obstrução", "Não"), gv.where(gv != "Obstrução", "Não")
    ok = o.isin(["Sim", "Não"]) & gv.isin(["Sim", "Não"])
    n, k = int(ok.sum()), int((o[ok] == gv[ok]).sum())
    return n, k, (k / n if n else float("nan"))


def classificar(x: pd.DataFrame, pres: pd.DataFrame, sigla: dict) -> pd.DataFrame:
    seg = {d: segmento(d, pres) for d in x["data"].unique()}
    x = x.assign(seg=x["data"].map(seg)).dropna(subset=["seg"])
    linhas = []
    for (p, s), g in x.groupby(["id_partido", "seg"]):
        n, k, c = concordancia(g)
        n2, _k2, c2 = concordancia(g, obstrucao_como_nao=True)
        n3, _k3, c3 = concordancia(g[g["via"] != "bloco"])  # regra original de D-050, sem blocos
        linhas.append({"id_partido": p, "sigla": sigla.get(p, p), "presidente": s[0], "inicio": s[1], "fim": s[2], "n_votacoes": n,
                       "n_concorda": k, "n_via_bloco": int((g["via"] == "bloco").sum()), "concordancia": round(c, 4), "grupo": grupo_de(c, n),
                       "concordancia_obstrucao_como_nao": round(c2, 4), "grupo_obstrucao_como_nao": grupo_de(c2, n2),
                       "concordancia_sem_blocos": round(c3, 4), "grupo_sem_blocos": grupo_de(c3, n3)})
    return pd.DataFrame(linhas).sort_values(["inicio", "concordancia"], ascending=[True, False])


def ler_tabela() -> pd.DataFrame:
    return pd.read_csv(SAIDA, dtype=str).fillna("")


def grupo_na_data(tabela: pd.DataFrame, partido: str, data: str) -> str:
    t = tabela[(tabela["id_partido"] == partido) & (tabela["inicio"] <= data) & (tabela["fim"] >= data)]
    return t["grupo"].iloc[0] if len(t) else "sem_classificacao"


def run() -> None:
    inst = ler("instituicoes")
    sigla = dict(zip(inst["id_instituicao"], inst["sigla"]))
    siglas = Siglas(ler("denominacoes_partido"))
    o, v = ler_bruto()
    x = orientacoes_por_partido(o, v, siglas)
    t = classificar(x, presidencias(), sigla)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(SAIDA, index=False, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    print(f"linhas partido x votação: {len(x)}; siglas sem correspondência: {siglas.sem}")
    print(t.groupby(["presidente", "grupo"]).size().unstack(fill_value=0).to_string())
    print(f"-> {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    run()
