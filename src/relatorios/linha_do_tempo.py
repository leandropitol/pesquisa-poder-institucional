"""Linha do tempo dos status formais de pessoas em processos (fechamento do estudo).

Cada linha vem de `status_pessoa_processo` e usa o modelo de frase do vocabulário `status_processual`; a fonte de cada status (id, título e URL) fica ao lado.
Regras de pessoas (CLAUDE.md, seção 5): só status formal, com absolvições, arquivamentos, prescrições e anulações ao lado das condenações; agente privado
só aparece por nome com status de réu ou acima; `representado` (abertura de representação por quebra de decoro) fica fora do texto e dentro do CSV.
Partido e grupo (governo ou oposição, D-050) são os da data do status, iguais para todos os atores.

Saídas: relatorios/linha_do_tempo.md, linha_do_tempo_status.csv e linha_do_tempo_fases_eventos.csv (fases de processo e eventos, sem pessoas).

Uso:
    python -m src.relatorios.linha_do_tempo
"""

import csv

import pandas as pd

from src.analise.etica import partido_em
from src.base import RAIZ, ler
from src.relatorios.util import commit, milhar
from src.simetria.governo_oposicao import grupo_na_data, ler_tabela as ler_tabela_governo

SAIDA = RAIZ / "relatorios"
ACIMA_DE_REU = {"reu", "condenado_1a_instancia", "condenado_2a_instancia", "condenado_tribunal_superior", "condenado_transito_em_julgado",
                "absolvido", "prescrito", "punibilidade_extinta", "condenacao_anulada", "processo_anulado"}
FORA_DO_TEXTO = {"representado"}
ROTULO_GRUPO = {"governo": "base do governo", "oposicao": "oposição", "nenhum": "sem orientação dominante", "sem_classificacao": "sem classificação", "sem_partido": "sem partido"}


def modelos() -> dict:
    return {r["codigo"]: r["modelo_frase"] for r in csv.DictReader((RAIZ / "data" / "vocabularios" / "status_processual.csv").open(encoding="utf-8"))}


def montar() -> pd.DataFrame:
    st, at, pr = ler("status_pessoa_processo"), ler("atores"), ler("processos")
    inst, fo = ler("instituicoes"), ler("fontes").fillna("")
    sigla = dict(zip(inst["id_instituicao"], inst["sigla"]))
    fo = fo[~fo["licenca"].str.contains("DataJud", case=False)]
    m = st.merge(at[["id_ator", "nome", "tipo_ator"]], on="id_ator").merge(pr[["id_processo", "numero_originario", "classe", "id_tribunal"]], on="id_processo")
    m = m.merge(fo[["id_fonte", "titulo", "url"]].rename(columns={"titulo": "fonte_titulo", "url": "fonte_url"}), on="id_fonte", how="inner")
    fil, gov = ler("filiacoes").sort_values("data_inicio"), ler_tabela_governo()
    m["id_partido"] = [partido_em(fil, a, d) for a, d in zip(m["id_ator"], m["data"])]
    m["partido"] = m["id_partido"].map(sigla).fillna("")
    m["grupo"] = [ROTULO_GRUPO.get(grupo_na_data(gov, p, d), "") if p else "" for p, d in zip(m["id_partido"], m["data"])]
    modelo = modelos()
    frases, visivel = [], []
    for r in m.itertuples():
        nome_ok = r.tipo_ator == "agente_publico" or r.status in ACIMA_DE_REU
        ator = r.nome if nome_ok else f"pessoa não identificada ({r.id_ator})"
        tip = f" ({str(r.tipificacao)[:170]})" if isinstance(r.tipificacao, str) and r.tipificacao else ""
        frases.append(modelo[r.status].format(data=r.data, ator=ator, processo=f"{r.numero_originario} ({sigla.get(r.id_tribunal, '')})", tipificacao=tip))
        visivel.append(nome_ok)
    m["frase"], m["nome_no_texto"] = frases, visivel
    m.loc[~m["nome_no_texto"], "nome"] = ""
    return m.sort_values(["data", "id_status"])


def run() -> None:
    m = montar()
    cols = ["data", "id_ator", "nome", "tipo_ator", "status", "frase", "numero_originario", "partido", "grupo", "id_fonte", "fonte_titulo", "fonte_url"]
    m[cols].to_csv(SAIDA / "linha_do_tempo_status.csv", index=False, encoding="utf-8")
    texto = m[~m["status"].isin(FORA_DO_TEXTO) & (m["nome_no_texto"] | m["tipo_ator"].eq("agente_publico"))]
    linhas = ["# Linha do tempo dos status formais de pessoas em processos, 2003 a 2026", "",
              f"Gerada por `python -m src.relatorios.linha_do_tempo` a partir de `status_pessoa_processo` (commit {commit()}). Cada linha traz o status formal, nunca a responsabilidade: "
              "condenações, absolvições, arquivamentos, prescrições, extinções de punibilidade e anulações entram com o mesmo formato, para atores de qualquer partido. "
              "`representado` (abertura de representação por quebra de decoro) aparece só no CSV. Agente privado só é citado por nome com status de réu ou acima. "
              "Partido e grupo (base do governo ou oposição, D-050) são os da data do status. Recomenda-se revisão jurídica antes de qualquer publicação.", "",
              f"Total no texto: {milhar(len(texto))} status de {milhar(texto['id_ator'].nunique())} pessoas; no CSV, {milhar(len(m))}. A linha do tempo de fases de processo e de eventos (sem pessoas) está em `linha_do_tempo_fases_eventos.csv`.", ""]
    for ano, x in texto.groupby(texto["data"].str[:4]):
        linhas += [f"## {ano}", ""]
        for r in x.itertuples():
            ctx = f" [{r.partido}; {r.grupo}]" if r.partido else ""
            linhas.append(f"- {r.frase}{ctx} *(Fonte: {r.id_fonte}, {r.fonte_titulo[:110]})*")
        linhas.append("")
    (SAIDA / "linha_do_tempo.md").write_text("\n".join(linhas), encoding="utf-8")
    fa, ev, pr, inst = ler("fases_processo"), ler("eventos"), ler("processos"), ler("instituicoes")
    sigla = dict(zip(inst["id_instituicao"], inst["sigla"]))
    num = dict(zip(pr["id_processo"], pr["numero_originario"]))
    f1 = pd.DataFrame({"data": fa["data"], "tipo": "fase", "rotulo": fa["fase"], "processo": fa["id_processo"].map(num), "orgao": fa["id_orgao_julgador"].map(sigla).fillna(""),
                       "descricao": fa["resumo"].fillna("").str[:200], "id_fonte": fa["id_fonte"]})
    e1 = ev.merge(ler("evento_fonte")[["id_evento", "id_fonte"]], on="id_evento", how="left")
    f2 = pd.DataFrame({"data": e1["data"], "tipo": "evento", "rotulo": e1["tipo_evento"], "processo": e1["id_processo"].map(num).fillna(""), "orgao": "",
                       "descricao": e1["descricao"].str[:200], "id_fonte": e1["id_fonte"]})
    pd.concat([f1, f2]).sort_values(["data", "tipo"]).to_csv(SAIDA / "linha_do_tempo_fases_eventos.csv", index=False, encoding="utf-8")
    print(f"status no CSV: {len(m)}; no texto: {len(texto)}; fases+eventos: {len(f1) + len(f2)}")


if __name__ == "__main__":
    run()
