"""Eixo 1 ampliado (D-060): registros formais em universos completos de candidatos, por partido e governo/oposição.

Universo: todos os candidatos das eleições gerais ordinárias de 2010 a 2022 (TSE, consulta_cand, arquivos por UF e do
Brasil), um por sequencial, com o partido do registro de candidatura.

Medidas (fixadas antes do cálculo):
- `tse_indeferimento`: candidatura indeferida ou cassada por motivo do eixo 1 (MOTIVOS_EIXO1); só 2018 e 2022, porque o
  TSE não publica o arquivo de motivos de 2010 e o de 2014 tem só 10 linhas. Ficha Limpa conta sempre; os demais motivos
  não contam quando o candidato tem, na mesma eleição, motivo que atinge a lista (MOTIVOS_LISTA; D-061). Sensibilidade:
  `tse_indeferimento_inclui_lista`, sem essa exclusão;
- `tcu_ate_eleicao`: CPF do candidato na lista pública do TCU de contas julgadas irregulares, com trânsito em julgado até
  o primeiro turno da eleição;
- `tcu_qualquer_data` (sensibilidade): a mesma lista, qualquer data de trânsito.

Taxa = candidatos com registro / candidatos do grupo, com intervalo de Wilson; grupos: partido (id da base, pela sigla
na data da eleição) e governo/oposição do partido na data da eleição (D-050). Teste de homogeneidade entre partidos com
pelo menos 30 candidatos no recorte: estatística qui-quadrado com p exato por simulação (hipergeométrica multivariada,
20.000 repetições, semente fixa), válido com contagens pequenas.

O CPF só é usado para ligar TSE e TCU; fica no intermediário data/staging/eixo1 (fora do Git) e não sai nas tabelas.

Saídas: relatorios/tabelas/eixo1_taxas.csv e eixo1_homogeneidade.csv; data/staging/eixo1/candidatos.csv.

Uso:
    python -m src.analise.eixo1
"""

import re
import zipfile

import numpy as np
import pandas as pd

from src.base import RAIZ, ler
from src.normalizacao.tse import arquivo, ler_zip, norm
from src.simetria.governo_oposicao import Siglas, grupo_na_data, ler_tabela as ler_tabela_governo
from src.simetria.taxa_bancada import wilson

ANOS = [2010, 2014, 2018, 2022]
ANOS_MOTIVO = [2018, 2022]
MOTIVOS_EIXO1 = {  # D-060: Ficha Limpa, abuso de poder, compra de votos ou captação ilícita, gasto ilícito
    "ficha limpa (lc 64/90)", "abuso de poder (lc 64/90)", "abuso de poder economico", "abuso de poder politico",
    "compra de voto (lei 9.504/97).", "captacao ilicita de sufragio", "gasto ilicito de recursos (lei 9.504/97).",
}
MOTIVOS_LISTA = ("cota de genero", "indeferimento de partido", "partido ou federacao invalidado")  # D-061: atingem a lista
STAGING = RAIZ / "data" / "staging" / "eixo1"
SAIDA = RAIZ / "relatorios" / "tabelas"


def digitos(x: str) -> str:
    return re.sub(r"\D", "", str(x or ""))


def data_iso(br: str) -> str:
    d, m, a = str(br).split("/")
    return f"{a}-{m}-{d}"


def universo(ano: int) -> pd.DataFrame:
    d = ler_zip(arquivo(f"consulta_cand_{ano}.zip"), lambda n: n.endswith(".csv") and not n.endswith("_BR.csv"))
    d = d[d["NM_TIPO_ELEICAO"].map(norm).str.contains("ordinaria")].copy()
    d["NR_TURNO"] = d["NR_TURNO"].astype(int)
    primeira = d.groupby("SQ_CANDIDATO")["DT_ELEICAO"].min()  # dd/mm/aaaa do 1º turno (menor data do sequencial)
    d = d.sort_values("NR_TURNO").drop_duplicates("SQ_CANDIDATO", keep="last")
    sit = d["DS_SIT_TOT_TURNO"].map(norm)
    return pd.DataFrame({"ano": ano, "uf": d["SG_UF"], "sq": d["SQ_CANDIDATO"], "cpf": d["NR_CPF_CANDIDATO"].map(digitos).str.zfill(11),
                         "nome": d["NM_CANDIDATO"], "cargo": d["DS_CARGO"].str.upper(), "sigla": d["SG_PARTIDO"],
                         "eleito": sit.str.startswith("eleito") | (sit == "media"),
                         "data_eleicao": d["SQ_CANDIDATO"].map(primeira).map(lambda x: min(data_iso(v) for v in [x]))})


def motivos() -> pd.DataFrame:
    partes = []
    for ano in ANOS_MOTIVO:
        z = zipfile.ZipFile(next((RAIZ / "data" / "raw" / "tse").glob(f"*/motivo_cassacao_{ano}.zip")))
        d = pd.concat([pd.read_csv(z.open(f), sep=";", encoding="latin-1", dtype=str) for f in z.namelist() if f.endswith(".csv")])
        col = next(c for c in d.columns if c in ("DS_MOTIVO", "DS_MOTIVO_CASSACAO"))
        partes.append(pd.DataFrame({"ano": ano, "sq": d["SQ_CANDIDATO"], "motivo": d[col].map(norm)}))
    m = pd.concat(partes)
    m["eixo1"] = m["motivo"].isin(MOTIVOS_EIXO1)
    m["lista"] = m["motivo"].str.contains("|".join(MOTIVOS_LISTA))
    m["ficha_limpa"] = m["motivo"].str.startswith("ficha limpa")
    return m


def tcu() -> pd.DataFrame:
    arq = next((RAIZ / "data" / "raw" / "tcu").glob("*/tcu_contas_julgadas_irregulares.csv"))
    d = pd.read_csv(arq, sep="|", encoding="latin-1", dtype=str, skiprows=1)
    d.columns = [norm(c) for c in d.columns]
    doc = d[next(c for c in d.columns if c.startswith("cpf"))].map(digitos)
    t = pd.DataFrame({"cpf": doc, "processo": d[next(c for c in d.columns if c == "processo")],
                      "transito": d[next(c for c in d.columns if c.startswith("transito"))].map(lambda x: data_iso(x) if isinstance(x, str) and x.count("/") == 2 else "")})
    return t[t["cpf"].str.len() == 11]


def montar() -> pd.DataFrame:
    siglas = Siglas(ler("denominacoes_partido"))
    gov = ler_tabela_governo()
    u = pd.concat([universo(a) for a in ANOS], ignore_index=True)
    m = motivos()
    chave = list(zip(m["ano"], m["sq"]))
    m["chave"] = chave
    lista = set(m.loc[m["lista"], "chave"])
    bruto = set(m.loc[m["eixo1"], "chave"])
    pessoal = set(m.loc[m["ficha_limpa"], "chave"]) | {k for k in bruto if k not in lista}  # D-061
    par = list(zip(u["ano"], u["sq"]))
    u["tse_indeferimento"] = [k in pessoal for k in par]
    u["tse_indeferimento_inclui_lista"] = [k in bruto for k in par]
    t = tcu()
    por_cpf = t.groupby("cpf")["transito"].apply(list).to_dict()
    u["tcu_qualquer_data"] = u["cpf"].map(lambda c: c in por_cpf)
    u["tcu_ate_eleicao"] = [any(x and x <= d for x in por_cpf.get(c, [])) for c, d in zip(u["cpf"], u["data_eleicao"])]
    u["id_partido"] = [siglas(s, d) or "" for s, d in zip(u["sigla"], u["data_eleicao"])]
    u["grupo"] = [grupo_na_data(gov, p, d) if p else "sem_classificacao" for p, d in zip(u["id_partido"], u["data_eleicao"])]
    return u


SIMULACOES, SEMENTE = 20000, 20260929


def qui2(k: np.ndarray, n: np.ndarray) -> np.ndarray:
    """Estatística qui-quadrado de homogeneidade (grupos x {com, sem} registro); k pode ter várias linhas (simulações)."""
    e = n * k.sum(axis=-1, keepdims=True) / n.sum()
    f = n - e
    return (((k - e) ** 2) / e + (((n - k) - f) ** 2) / f).sum(axis=-1)


def homogeneidade(k: np.ndarray, n: np.ndarray) -> tuple[float, float]:
    """p exato por simulação: sob taxas iguais, os K casos se distribuem entre os grupos pela hipergeométrica multivariada."""
    obs = float(qui2(k.astype(float), n.astype(float)))
    rng = np.random.default_rng(SEMENTE)
    sim = rng.multivariate_hypergeometric(n.astype(np.int64), int(k.sum()), size=SIMULACOES).astype(float)
    return obs, float((1 + (qui2(sim, n.astype(float)) >= obs - 1e-9).sum()) / (1 + SIMULACOES))


def taxas(u: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sigla = dict(zip(ler("instituicoes")["id_instituicao"], ler("instituicoes")["sigla"]))
    linhas, homog = [], []
    recortes = [("tse_indeferimento", ANOS_MOTIVO), ("tse_indeferimento_inclui_lista", ANOS_MOTIVO), ("tcu_ate_eleicao", ANOS),
                ("tcu_qualquer_data", ANOS)]
    for medida, anos in recortes:
        for rotulo, anos_r in [(str(a), [a]) for a in anos] + [("todos", anos)]:
            for universo_r, filtro in (("candidatos", slice(None)), ("eleitos", "eleito")):
                x = u[u["ano"].isin(anos_r)]
                if filtro == "eleito":
                    x = x[x["eleito"]]
                for tipo, col in (("partido", "id_partido"), ("governo_oposicao", "grupo")):
                    g = x.groupby(col)[medida].agg(["sum", "count"]).reset_index()
                    for r in g.itertuples():
                        k, n = int(r.sum), int(r.count)
                        lo, hi = wilson(k, n)
                        linhas.append({"medida": medida, "anos": rotulo, "universo": universo_r, "grupo_tipo": tipo, "grupo": getattr(r, col) or "sem_partido",
                                       "sigla": sigla.get(getattr(r, col), getattr(r, col)), "n": n, "com_registro": k,
                                       "taxa": k / n if n else float("nan"), "ic95_inf": lo, "ic95_sup": hi})
                    if tipo == "partido":
                        h = g[(g["count"] >= 30) & (g[col] != "")]
                        if len(h) >= 2 and h["sum"].sum() > 0:
                            est, p = homogeneidade(h["sum"].to_numpy(), h["count"].to_numpy())
                            homog.append({"medida": medida, "anos": rotulo, "universo": universo_r, "partidos": len(h), "qui2": est,
                                          "p_valor": p, "metodo": f"Monte Carlo exato, {SIMULACOES} simulações, semente {SEMENTE}"})
    return pd.DataFrame(linhas), pd.DataFrame(homog)


def run() -> None:
    u = montar()
    STAGING.mkdir(parents=True, exist_ok=True)
    u.to_csv(STAGING / "candidatos.csv", index=False, encoding="utf-8")
    t, h = taxas(u)
    t.to_csv(SAIDA / "eixo1_taxas.csv", index=False, encoding="utf-8")
    h.to_csv(SAIDA / "eixo1_homogeneidade.csv", index=False, encoding="utf-8")
    print(u.groupby("ano")[["tse_indeferimento", "tse_indeferimento_inclui_lista", "tcu_ate_eleicao", "tcu_qualquer_data", "eleito"]].sum().assign(n=u.groupby("ano").size()).to_string())
    print(h.to_string(index=False))


if __name__ == "__main__":
    run()
