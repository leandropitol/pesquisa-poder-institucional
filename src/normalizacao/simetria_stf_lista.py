"""Lista das ações penais do STF cujas partes são lidas no portal, universo da verificação de simetria (D-048).

A exportação de decisões do Corte Aberta (E5) não traz as partes. Para verificar, partido por partido, se um
status registrado na E9 (réu, condenado, absolvido) tem equivalente em outros partidos, é preciso saber quem são
os réus de cada ação penal. O portal do STF recusa cliente automatizado (HTTP 403), então os nomes vêm da aba
Partes lida no navegador, em lotes, e entram depois em data/curadoria/simetria_stf_ap_reus.csv.

Universo: toda ação penal (AP) com alguma decisão na exportação, menos as dos atos de 8 de janeiro de 2023
(autuadas a partir de 2023 com o assunto genérico "DIREITO PROCESSUAL PENAL | AÇÃO PENAL"), que são do eixo de
concentração ou abuso de poder e pedem outro padrão de verificação.

Lotes: o lote 1 reúne as ações julgadas no mérito por órgão colegiado (andamento "Procedente", "Procedente em
parte" ou "Improcedente"); as demais seguem em lotes de 100 pela ordem de autuação.

Uso:
    python -m src.normalizacao.simetria_stf_lista
"""

import pandas as pd

from src.base import RAIZ

EXPORTACAO = RAIZ / "data" / "raw" / "stf" / "2026-09-24" / "stf_corte_aberta_decisoes_AP_Inq_2003-01-08_a_2026-09-23.xlsx"
SAIDA = RAIZ / "data" / "curadoria" / "simetria_stf_ap_lista.csv"
MERITO = ["Procedente", "Procedente em parte", "Improcedente"]
ASSUNTO_8JAN = "DIREITO PROCESSUAL PENAL | AÇÃO PENAL"
TAMANHO_LOTE = 100


def lista(d: pd.DataFrame) -> pd.DataFrame:
    ap = d[d["Processo"].str.startswith("AP ")].copy()
    ap["merito"] = ap["Andamento decisão"].isin(MERITO) & ap["Indicador colegiado"].eq("COLEGIADA")
    for c in ("Data de autuação", "Data da decisão"):
        ap[c] = ap[c].str[:10]  # a exportação traz "AAAA-MM-DD 00:00:00"
    m = ap[ap["merito"]]
    g = ap.groupby("Processo").agg(data_autuacao=("Data de autuação", "first"), assunto=("Assuntos do processo", "first")).reset_index()
    j = m.groupby("Processo").agg(
        data_primeiro_julgamento=("Data da decisão", "min"), data_ultimo_julgamento=("Data da decisão", "max"),
        resultados=("Andamento decisão", lambda s: "; ".join(sorted(set(s)))),
        orgao_julgador=("Órgão julgador", lambda s: "; ".join(sorted(set(s.dropna()))))).reset_index()
    g = g.merge(j, on="Processo", how="left")
    fora = g["assunto"].str.strip().eq(ASSUNTO_8JAN) & (g["data_autuacao"] >= "2023")
    g = g[~fora].copy()
    g["numero"] = g["Processo"].str.split().str[1].astype(int)
    g["julgada_no_merito"] = g["resultados"].notna()
    g = g.sort_values(["julgada_no_merito", "data_autuacao", "numero"], ascending=[False, True, True]).reset_index(drop=True)
    n_merito = int(g["julgada_no_merito"].sum())
    g["lote"] = [1 if i < n_merito else 2 + (i - n_merito) // TAMANHO_LOTE for i in range(len(g))]
    g["url_busca"] = "https://portal.stf.jus.br/processos/listarProcessos.asp?classe=AP&numeroProcesso=" + g["numero"].astype(str)
    return g.drop(columns="numero").rename(columns={"Processo": "processo"})


def run() -> None:
    d = pd.read_excel(EXPORTACAO, dtype=str)
    g = lista(d)
    g.to_csv(SAIDA, index=False, lineterminator="\n")
    print(f"{len(g)} ações penais (fora 8 de janeiro), {int(g['julgada_no_merito'].sum())} julgadas no mérito; "
          f"lotes: {g['lote'].value_counts().sort_index().to_dict()} -> {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    run()
