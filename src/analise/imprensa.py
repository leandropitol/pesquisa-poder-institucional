"""Contraste com a imprensa (D-047, D-055, D-056): tabela de classificação e resumos.

Junta a classificação curada (data/curadoria/imprensa_contraste.csv) com o bruto das buscas
(data/raw/imprensa/*/buscas.jsonl) e confere, linha a linha, que o título escolhido é o título devolvido
pela busca na posição indicada. Veículo em uso: principal com acesso e reserva com acesso (D-055, D-056).
Veículo principal sem acesso aparece com a situação de acesso no lugar do resultado.

Saídas (geradas): relatorios/tabelas/imprensa_contraste*.csv.

Uso:
    python -m src.analise.imprensa
"""

import json
import re
import unicodedata

import pandas as pd

from src.base import RAIZ

CUR = RAIZ / "data" / "curadoria"
RAW = RAIZ / "data" / "raw" / "imprensa"
SAIDA = RAIZ / "relatorios" / "tabelas"
RESULTADOS = ["concorda", "diverge", "mencao_sem_resultado", "sem_resultado"]


def normalizar(t: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(t))).strip().casefold()


def titulo_confere(curado: str, bruto: str) -> bool:
    """O título curado é trecho literal do título devolvido (sufixo do site e reticências ficam de fora)."""
    return normalizar(curado.rstrip(" .…")) in normalizar(bruto)


def buscas() -> pd.DataFrame:
    linhas = [json.loads(l) for arq in sorted(RAW.glob("*/buscas.jsonl")) for l in arq.open(encoding="utf-8")]
    return pd.DataFrame(linhas, columns=["fato", "veiculo", "dominio", "consulta", "acesso", "links", "registrado_em"])


def veiculos_em_uso(veic: pd.DataFrame) -> pd.DataFrame:
    return veic[veic["situacao_acesso"] == "ok"]


def conferir(fatos: pd.DataFrame, veic: pd.DataFrame, cont: pd.DataFrame, bus: pd.DataFrame) -> list[str]:
    """Lista de problemas; vazia se a classificação está completa e bate com o bruto."""
    erros = []
    uso = set(veiculos_em_uso(veic)["veiculo"])
    ok = bus[bus["acesso"] == "ok"]
    for (f, v), g in ok.groupby(["fato", "veiculo"]):
        if len(g) > 1:
            erros.append(f"{f} | {v}: mais de uma busca com acesso")
    links = {(r.fato, r.veiculo): r.links for r in ok.itertuples()}
    chaves = cont.groupby(["id_fato", "veiculo"]).size()
    for f in fatos["id_fato"]:
        for v in sorted(uso):
            n = chaves.get((f, v), 0)
            if n != 1:
                erros.append(f"{f} | {v}: {n} linhas de classificação")
            if (f, v) not in links:
                erros.append(f"{f} | {v}: busca com acesso não registrada no bruto")
    for r in cont.itertuples():
        if r.veiculo not in uso:
            erros.append(f"{r.id_fato} | {r.veiculo}: veículo fora de uso")
        if r.resultado not in RESULTADOS:
            erros.append(f"{r.id_fato} | {r.veiculo}: resultado inválido {r.resultado!r}")
        tem_pos = pd.notna(r.posicao) and str(r.posicao).strip() != ""
        if (r.resultado == "sem_resultado") == tem_pos:
            erros.append(f"{r.id_fato} | {r.veiculo}: posição {'indevida' if tem_pos else 'faltando'} para {r.resultado}")
        if tem_pos:
            ls = links.get((r.id_fato, r.veiculo), [])
            p = int(r.posicao)
            if not 1 <= p <= len(ls) or not titulo_confere(r.titulo, ls[p - 1]["title"]):
                erros.append(f"{r.id_fato} | {r.veiculo}: título não confere com a posição {p} do bruto")
    return erros


def montar() -> dict[str, pd.DataFrame]:
    fatos = pd.read_csv(CUR / "imprensa_fatos.csv", dtype=str)
    veic = pd.read_csv(CUR / "imprensa_veiculos.csv", dtype=str)
    cont = pd.read_csv(CUR / "imprensa_contraste.csv", dtype=str, keep_default_na=False)
    bus = buscas()
    erros = conferir(fatos, veic, cont, bus)
    if erros:
        raise ValueError("classificação da imprensa inconsistente:\n" + "\n".join(erros))
    links = {(r.fato, r.veiculo): r.links for r in bus[bus["acesso"] == "ok"].itertuples()}
    listados = veic[(veic["papel"] == "principal") | (veic["situacao_acesso"] == "ok")]
    det = []
    for f in fatos.itertuples():
        for v in listados.itertuples():
            base = {"id_fato": f.id_fato, "data_fato": f.data, "caso": f.caso, "fato_oficial": f.fato_oficial,
                    "veiculo": v.veiculo, "papel": v.papel}
            if v.situacao_acesso != "ok":
                det.append({**base, "resultado": v.situacao_acesso})
                continue
            c = cont[(cont["id_fato"] == f.id_fato) & (cont["veiculo"] == v.veiculo)].iloc[0]
            lk = links[(f.id_fato, v.veiculo)][int(c["posicao"]) - 1] if c["posicao"] else {}
            det.append({**base, "resultado": c["resultado"], "posicao": c["posicao"], "titulo": lk.get("title", ""),
                        "url": lk.get("url", ""), "verificacao": c["verificacao"], "observacao": c["observacao"]})
    det = pd.DataFrame(det)
    uso = det[det["resultado"].isin(RESULTADOS)]
    por_fato = (pd.crosstab([uso["id_fato"], uso["caso"], uso["fato_oficial"]], uso["resultado"])
                .reindex(columns=RESULTADOS, fill_value=0).reset_index())
    por_fato["veiculos_em_uso"] = por_fato[RESULTADOS].sum(axis=1)
    por_fato["com_materia"] = por_fato[["concorda", "diverge", "mencao_sem_resultado"]].sum(axis=1)
    por_veiculo = pd.crosstab(uso["veiculo"], uso["resultado"]).reindex(columns=RESULTADOS, fill_value=0).reset_index()
    por_veiculo["fatos"] = por_veiculo[RESULTADOS].sum(axis=1)
    return {"imprensa_contraste": det, "imprensa_contraste_por_fato": por_fato, "imprensa_contraste_por_veiculo": por_veiculo}


def run() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome, df in montar().items():
        df.to_csv(SAIDA / f"{nome}.csv", index=False, encoding="utf-8")
        print(f"{nome}: {len(df)} linhas")


if __name__ == "__main__":
    run()
