"""Partido de cada mandato presidencial (D-059), do registro de candidatura no TSE.

Regra: o partido do presidente num mandato é o partido do registro de candidatura, no TSE, na eleição que deu esse
mandato (consulta_cand, cargo Presidente); para o vice que assumiu a Presidência, o do seu registro como vice.
A mudança de filiação durante o mandato é outra variável (filiação na data) e só entra com fonte própria.

Entradas: data/curadoria/presidencias.csv (mandatos) e data/raw/tse/*/consulta_cand_AAAA.zip (já no bruto, E7).
Saída (gerada): relatorios/tabelas/presidencias_partido.csv.

Uso:
    python -m src.normalizacao.presidencias_partido
"""

import unicodedata
import zipfile

import pandas as pd

from src.base import RAIZ, ler
from src.simetria.governo_oposicao import Siglas, presidencias

SAIDA = RAIZ / "relatorios" / "tabelas" / "presidencias_partido.csv"
# mandato que começa em -> (ano da eleição, cargo no registro); o vice que assumiu usa o registro de vice
ELEICAO = {"2003-01-01": (2002, "PRESIDENTE"), "2007-01-01": (2006, "PRESIDENTE"), "2011-01-01": (2010, "PRESIDENTE"),
           "2015-01-01": (2014, "PRESIDENTE"), "2016-05-12": (2014, "VICE-PRESIDENTE"), "2019-01-01": (2018, "PRESIDENTE"),
           "2023-01-01": (2022, "PRESIDENTE")}


def norm(s: str) -> str:
    return " ".join(unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii").upper().split())


def candidaturas(ano: int) -> tuple[pd.DataFrame, str]:
    arq = next((RAIZ / "data" / "raw" / "tse").glob(f"*/consulta_cand_{ano}.zip"))
    zf = zipfile.ZipFile(arq)
    nome = next(n for n in zf.namelist() if n.endswith(("_BR.csv", "_BRASIL.csv")))
    d = pd.read_csv(zf.open(nome), sep=";", encoding="latin-1", dtype=str)
    d = d[d["DS_CARGO"].str.upper().isin(["PRESIDENTE", "VICE-PRESIDENTE"])].drop_duplicates(["DS_CARGO", "NM_CANDIDATO", "SG_PARTIDO"])
    return d, f"{arq.relative_to(RAIZ).as_posix()}:{nome}"


def montar() -> pd.DataFrame:
    fontes = ler("fontes")
    siglas = Siglas(ler("denominacoes_partido"))
    linhas = []
    for p in presidencias().itertuples():
        ano, cargo = ELEICAO[p.inicio]
        d, origem = candidaturas(ano)
        palavras = set(norm(p.presidente).split()) - {"DA", "DE", "DO", "DOS", "DAS"}
        c = d[(d["DS_CARGO"].str.upper() == cargo) & d["NM_CANDIDATO"].map(lambda n: palavras <= set(norm(n).split()) or
                                                                               len(palavras & set(norm(n).split())) >= 2)]
        if len(c) != 1:
            raise ValueError(f"{p.presidente} {ano}: {len(c)} registros de {cargo} no TSE")
        r = c.iloc[0]
        f = fontes[fontes["titulo"] == f"TSE, dados abertos: consulta_cand_{ano}.zip"]
        linhas.append({"presidente": p.presidente, "inicio": p.inicio, "fim": p.fim, "ano_eleicao": str(ano), "cargo_no_registro": cargo,
                       "nome_tse": r["NM_CANDIDATO"], "sigla_tse": r["SG_PARTIDO"], "id_partido": siglas(r["SG_PARTIDO"], p.inicio) or "",
                       "situacao_tse": r.get("DS_SIT_TOT_TURNO", ""), "arquivo_raw": origem, "id_fonte": f["id_fonte"].iloc[0] if len(f) else ""})
    return pd.DataFrame(linhas)


def partido_na_data(tabela: pd.DataFrame, presidente: str, data: str) -> str:
    """id do partido do mandato em curso na data (regra de D-059); vazio se a data está fora dos mandatos da tabela."""
    t = tabela[(tabela["presidente"] == presidente) & (tabela["inicio"] <= data) & ((tabela["fim"] == "") | (tabela["fim"] >= data))]
    return t["id_partido"].iloc[0] if len(t) else ""


def run() -> None:
    t = montar()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(SAIDA, index=False, encoding="utf-8")
    print(t[["presidente", "inicio", "ano_eleicao", "cargo_no_registro", "sigla_tse", "id_partido", "id_fonte"]].to_string(index=False))


if __name__ == "__main__":
    run()
