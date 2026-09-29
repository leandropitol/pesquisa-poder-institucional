"""Contraste com a imprensa (D-047, D-055, D-056): tabela de classificação e resumos.

Junta a classificação curada (data/curadoria/imprensa_contraste.csv) com o bruto das buscas
(data/raw/imprensa/*/buscas.jsonl) e confere, linha a linha, que o título escolhido é o título devolvido
pela busca na posição indicada. Veículo em uso: principal com acesso e reserva com acesso (D-055, D-056).
Veículo principal sem acesso aparece com a situação de acesso no lugar do resultado.

Os principais sem acesso têm tabela própria (D-057), montada dos relatórios de navegação usados
(src.coleta.imprensa.relatorios_usados) e de data/curadoria/imprensa_contraste_navegador.csv, com a mesma
conferência de título por posição. Não é somada ao painel principal: o buscador é outro.

Saídas (geradas): relatorios/tabelas/imprensa_contraste*.csv e imprensa_navegador*.csv.

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


def conferir_navegador(cont: pd.DataFrame, regs: list[dict]) -> list[str]:
    """Cada busca com acesso de cada coleta tem uma linha; linhas só para buscas com acesso; título confere com a posição."""
    erros = []
    links = {(r["coleta"], r["fato"], r["veiculo"]): r["links"] for r in regs if r["acesso"] == "ok"}
    chaves = cont.groupby(["coleta", "id_fato", "veiculo"]).size()
    for k in links:
        if chaves.get(k, 0) != 1:
            erros.append(f"{' | '.join(k)}: {chaves.get(k, 0)} linhas de classificação")
    for r in cont.itertuples():
        k = (r.coleta, r.id_fato, r.veiculo)
        if k not in links:
            erros.append(f"{' | '.join(k)}: sem busca com acesso no relatório")
            continue
        for campo in ("resultado", "resultado_incluindo_blogs"):
            valor = getattr(r, campo)
            if valor and valor not in RESULTADOS:
                erros.append(f"{' | '.join(k)}: {campo} inválido {valor!r}")
        if (r.resultado == "sem_resultado") == bool(r.posicao):
            erros.append(f"{' | '.join(k)}: posição {'indevida' if r.posicao else 'faltando'} para {r.resultado}")
        if r.posicao:
            ls, p = links[k], int(r.posicao)
            if not 1 <= p <= len(ls) or not titulo_confere(r.titulo, ls[p - 1]["title"]):
                erros.append(f"{' | '.join(k)}: título não confere com a posição {p} do relatório")
    return erros


def montar_navegador(regs: list[dict] | None = None) -> dict[str, pd.DataFrame]:
    from src.coleta.imprensa import relatorios_usados

    regs = relatorios_usados() if regs is None else regs
    fatos = pd.read_csv(CUR / "imprensa_fatos.csv", dtype=str)
    cont = pd.read_csv(CUR / "imprensa_contraste_navegador.csv", dtype=str, keep_default_na=False)
    erros = conferir_navegador(cont, regs)
    if erros:
        raise ValueError("classificação dos relatórios de navegação inconsistente:\n" + "\n".join(erros))
    info = fatos.set_index("id_fato")
    idx = cont.set_index(["coleta", "id_fato", "veiculo"])
    det = []
    for r in regs:
        base = {"coleta": r["coleta"], "id_fato": r["fato"], "data_fato": info.at[r["fato"], "data"], "caso": info.at[r["fato"], "caso"],
                "veiculo": r["veiculo"]}
        if r["acesso"] != "ok":
            det.append({**base, "resultado": r["acesso"], "resultado_incluindo_blogs": r["acesso"]})
            continue
        c = idx.loc[(r["coleta"], r["fato"], r["veiculo"])]
        lk = r["links"][int(c["posicao"]) - 1] if c["posicao"] else {}
        det.append({**base, "resultado": c["resultado"], "resultado_incluindo_blogs": c["resultado_incluindo_blogs"] or c["resultado"],
                    "posicao": c["posicao"], "titulo": lk.get("title", ""), "url": lk.get("url", ""),
                    "data_exibida": lk.get("data_exibida", ""), "verificacao": c["verificacao"], "observacao": c["observacao"]})
    det = pd.DataFrame(det).sort_values(["coleta", "veiculo", "id_fato"])
    uso = det[det["resultado"].isin(RESULTADOS)]
    por_veiculo = (pd.crosstab([uso["coleta"], uso["veiculo"]], uso["resultado"]).reindex(columns=RESULTADOS, fill_value=0).reset_index())
    por_veiculo["buscas_com_acesso"] = por_veiculo[RESULTADOS].sum(axis=1)
    com_blog = uso.assign(m=uso["resultado_incluindo_blogs"] != "sem_resultado").groupby(["coleta", "veiculo"])["m"].sum()
    por_veiculo["com_materia"] = por_veiculo["buscas_com_acesso"] - por_veiculo["sem_resultado"]
    por_veiculo["com_materia_incluindo_blogs"] = [int(com_blog[(a, b)]) for a, b in zip(por_veiculo["coleta"], por_veiculo["veiculo"])]
    folha = (det[det["veiculo"] == "Folha de S.Paulo"].pivot(index="id_fato", columns="coleta", values="resultado").reset_index())
    return {"imprensa_navegador": det, "imprensa_navegador_por_veiculo": por_veiculo, "imprensa_navegador_folha_por_coleta": folha}


def run() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome, df in {**montar(), **montar_navegador()}.items():
        df.to_csv(SAIDA / f"{nome}.csv", index=False, encoding="utf-8")
        print(f"{nome}: {len(df)} linhas")


if __name__ == "__main__":
    run()
