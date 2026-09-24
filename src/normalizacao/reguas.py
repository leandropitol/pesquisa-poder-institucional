"""Normalização das réguas externas (etapa E2) para `qualidade_democratica`.

- V-Dem v16: `v2x_regime` (Regimes of the World, 0 a 3) e `v2x_libdem` (índice de democracia
  liberal, 0 a 1), extraídos por src/normalizacao/vdem_extrair.R; código do país = `country_text_id`.
- Freedom House: status por "ano sob avaliação" (planilha de ratings e status) e pontuação total por
  edição (planilha de dados brutos; ano = edição menos um). Nomes de país ligados ao código do V-Dem
  pelo nome normalizado; os demais, por data/curadoria/paises_freedom_house.csv.

A base guarda só os valores brutos. A classificação do protocolo (seção 4) é calculada por
`classificar`, nunca gravada.

Uso:
    python -m src.normalizacao.reguas
"""

import csv
import re
import subprocess
import unicodedata
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, gravar, ler

ANO_INICIAL = 2000
RSCRIPT = Path(r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe")
MANIFESTOS = RAIZ / "data" / "manifestos"
STAGING = RAIZ / "data" / "staging"
CURADORIA = RAIZ / "data" / "curadoria"

# Protocolo, seção 4: categorias publicadas pelas próprias réguas.
BAIXA = {"vdem_row": {"0", "1"}, "fh_status": {"NF"}}
INTERMEDIARIA = {"vdem_row": {"2"}, "fh_status": {"PF"}}


def classificar(indice: str, valor: str) -> str | None:
    """'baixa', 'intermediaria' ou 'alta' para as réguas categóricas; None para as contínuas."""
    if indice not in BAIXA:
        return None
    if valor in BAIXA[indice]:
        return "baixa"
    return "intermediaria" if valor in INTERMEDIARIA[indice] else "alta"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii")
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s.lower()).split())


def _manifesto(fonte: str) -> list[dict]:
    man = list(csv.DictReader((MANIFESTOS / f"{fonte}.csv").open(encoding="utf-8")))
    data = max(m["data_acesso"] for m in man)
    return [m for m in man if m["data_acesso"] == data]


def ler_vdem(reg: dict) -> pd.DataFrame:
    saida = STAGING / "vdem" / f"{Path(reg['arquivo']).stem}_row_ldi.csv"
    subprocess.run([str(RSCRIPT), str(RAIZ / "src/normalizacao/vdem_extrair.R"), str(RAIZ / reg["arquivo"]), str(saida), str(ANO_INICIAL)],
                   check=True, capture_output=True)
    return pd.read_csv(saida, dtype=str, keep_default_na=False)


def status_fh(caminho: Path) -> pd.DataFrame:
    """Planilha de ratings: linha 2 = ano sob avaliação; blocos de 3 colunas (PR, CL, Status)."""
    bruto = pd.read_excel(caminho, sheet_name="Country Ratings, Statuses ", header=None, dtype=object)
    anos = bruto.iloc[1]
    linhas = []
    for _, r in bruto.iloc[3:].iterrows():
        pais = r.iloc[0]
        if not isinstance(pais, str) or not pais.strip():
            continue
        for col in range(1, len(r), 3):
            ano = anos.iloc[col]
            status = r.iloc[col + 2] if col + 2 < len(r) else None
            if isinstance(ano, (int, float)) and not pd.isna(ano) and int(ano) >= ANO_INICIAL and isinstance(status, str) and status.strip() in {"F", "PF", "NF"}:
                linhas.append({"nome": pais.strip(), "ano": str(int(ano)), "valor": status.strip()})
    return pd.DataFrame(linhas)


def total_fh(caminho: Path) -> pd.DataFrame:
    d = pd.read_excel(caminho, sheet_name="FIW13-25", header=1, dtype=object)
    d = d[d["C/T"] == "c"]
    return pd.DataFrame({"nome": d["Country/Territory"].str.strip(), "ano": (d["Edition"].astype(int) - 1).astype(str),
                         "valor": d["Total"].astype(int).astype(str)})


def codigos_fh(nomes: set[str], vdem: pd.DataFrame) -> tuple[dict[str, str], list[str]]:
    por_nome = {norm(n): c for n, c in zip(vdem["country_name"], vdem["country_text_id"])}
    cur = {l["nome_freedom_house"]: l["pais_iso3"] for l in csv.DictReader((CURADORIA / "paises_freedom_house.csv").open(encoding="utf-8"))}
    mapa, faltam = {}, []
    for n in sorted(nomes):
        if n in cur:
            if cur[n]:
                mapa[n] = cur[n]
        elif norm(n) in por_nome:
            mapa[n] = por_nome[norm(n)]
        else:
            faltam.append(n)
    return mapa, faltam


def montar(ids: RegistroIds) -> dict:
    (vd,) = _manifesto("vdem")
    fh = {Path(m["arquivo"]).name: m for m in _manifesto("freedom_house")}
    fh_status_reg = fh["Country_and_Territory_Ratings_and_Statuses_FIW_1973-2024.xlsx"]
    fh_total_reg = fh["All_data_FIW_2013-2024.xlsx"]

    fontes, bases = [], []

    def fonte(reg: dict, titulo: str, org: str, conjunto: str, versao: str, variavel: str, link: str, licenca: str) -> str:
        f = ids.obter("fontes", f"raw:{reg['arquivo']}")
        fontes.append({"id_fonte": f, "tipo_fonte": "base_de_dados", "titulo": titulo, "data_publicacao": reg["data_acesso"], "url": reg["url_base"],
                       "data_acesso": reg["data_acesso"], "sha256": reg["sha256"], "caminho_raw": reg["arquivo"], "licenca": licenca})
        bases.append({"id_fonte": f, "organizacao": org, "conjunto": conjunto, "versao": versao, "variavel": variavel, "link": link})
        return f

    f_vdem = fonte(vd, "V-Dem Country-Year Full+Others, versão 16 (pacote vdemdata)", "V-Dem Institute", "Country-Year: V-Dem Full+Others",
                   "v16 (março de 2026)", "v2x_regime; v2x_libdem", "https://github.com/vdeminstitute/vdemdata/tree/V16", "CC BY-SA 4.0")
    f_fhs = fonte(fh_status_reg, "Freedom in the World: Country and Territory Ratings and Statuses, 1973-2024", "Freedom House",
                  "Country and Territory Ratings and Statuses", "edições 1973 a 2025 (anos sob avaliação 1972 a 2024)", "Status",
                  fh_status_reg["url_base"], "Uso livre para fins pessoais, acadêmicos e sem fins lucrativos (Freedom House)")
    f_fht = fonte(fh_total_reg, "Freedom in the World 2013-2025 Raw Data", "Freedom House", "All data FIW 2013-2025",
                  "edições 2013 a 2025 (anos sob avaliação 2012 a 2024)", "Total", fh_total_reg["url_base"],
                  "Uso livre para fins pessoais, acadêmicos e sem fins lucrativos (Freedom House)")

    vdem = ler_vdem(vd)
    linhas = []
    for _, r in vdem.iterrows():
        if r["v2x_regime"] != "":
            linhas.append({"pais_iso3": r["country_text_id"], "ano": r["year"], "indice": "vdem_row", "valor": r["v2x_regime"], "id_fonte": f_vdem})
        if r["v2x_libdem"] != "":
            linhas.append({"pais_iso3": r["country_text_id"], "ano": r["year"], "indice": "vdem_ldi", "valor": r["v2x_libdem"], "id_fonte": f_vdem})

    st = status_fh(RAIZ / fh_status_reg["arquivo"])
    tt = total_fh(RAIZ / fh_total_reg["arquivo"])
    mapa, faltam = codigos_fh(set(st["nome"]) | set(tt["nome"]), vdem)
    for df, indice, f in ((st, "fh_status", f_fhs), (tt, "fh_total", f_fht)):
        for _, r in df.iterrows():
            if r["nome"] in mapa:
                linhas.append({"pais_iso3": mapa[r["nome"]], "ano": r["ano"], "indice": indice, "valor": r["valor"], "id_fonte": f})
    return {"qualidade_democratica": linhas, "fontes": fontes, "fonte_base_dados": bases, "faltam": faltam,
            "n_paises": {"vdem": vdem["country_text_id"].nunique(), "fh": len(mapa)}}


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    for nome in ("fontes", "fonte_base_dados"):
        atual = ler(nome, base)
        novas = [l for l in r[nome] if l["id_fonte"] not in set(atual["id_fonte"])]
        gravar(nome, pd.concat([atual, pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    gravar("qualidade_democratica", pd.DataFrame(r["qualidade_democratica"], dtype=str), base)
    ids.salvar()


def run() -> None:
    ids = RegistroIds()
    r = montar(ids)
    if r["faltam"]:
        raise SystemExit(f"países da Freedom House sem código: {r['faltam']} (acrescentar em data/curadoria/paises_freedom_house.csv)")
    gravar_resultado(r, ids)
    q = pd.DataFrame(r["qualidade_democratica"])
    print(q.groupby("indice").agg(linhas=("valor", "size"), paises=("pais_iso3", "nunique"), ano_min=("ano", "min"), ano_max=("ano", "max")).to_string())
    print(f"países: V-Dem {r['n_paises']['vdem']}, Freedom House {r['n_paises']['fh']}")


if __name__ == "__main__":
    run()
