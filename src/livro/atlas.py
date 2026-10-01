"""Parte VIII, Atlas documental: registros nominais com contexto e casos de referência (contagens)."""
from __future__ import annotations

import pandas as pd

from .comum import F_STF, F_TCU, NOME_ATOR, SIGLA, TAB, gravar_resultados, ler, partido_na_data, tabela


def cargo_na_data(cargos: pd.DataFrame, id_ator: str, data: pd.Timestamp) -> str:
    c = cargos[cargos.id_ator == id_ator]
    viv = c[(c.ini <= data) & (c.fim.isna() | (c.fim >= data))]
    if len(viv):
        return "; ".join(sorted(set(viv.cargo)))
    ant = c[c.ini <= data].sort_values("ini")
    return ("último mandato anterior: " + ant.cargo.iloc[-1] + f" ({ant.ini.iloc[-1].year}–{'' if pd.isna(ant.fim.iloc[-1]) else ant.fim.iloc[-1].year})") if len(ant) else "sem mandato federal na base"


def main() -> None:
    R = {}
    cg = ler("cargos"); cg["ini"] = pd.to_datetime(cg.data_inicio, errors="coerce"); cg["fim"] = pd.to_datetime(cg.data_fim, errors="coerce")
    fo = ler("fontes").set_index("id_fonte")
    st = ler("status_pessoa_processo")
    sd = pd.read_csv(TAB / "stf_desfechos.csv"); sd["data"] = pd.to_datetime(sd["data"], errors="coerce")
    cd = sd[sd.status == "condenado_tribunal_superior"].sort_values("data")
    rows = []
    for r in cd.itertuples():
        m = st[(st.id_ator == r.id_ator) & (st.status == r.status) & (st.data == r.data.strftime("%Y-%m-%d"))]
        fid = m.id_fonte.iloc[0] if len(m) else ""
        fonte = f"{fo.titulo.get(fid, '')} ({fid}); {fo.url.get(fid, '')}" if fid else "Corte Aberta (FNT-000046)"
        rows.append({"Ação": r.ap, "Data da decisão": r.data.strftime("%Y-%m-%d"), "Nome parlamentar": str(NOME_ATOR.get(r.id_ator, r.nome_no_portal)).title(), "Nome no processo": str(r.nome_no_portal).title() if pd.notna(r.nome_no_portal) else "",
                     "Cargo na data (base)": cargo_na_data(cg, r.id_ator, r.data), "Partido na data": SIGLA.get(partido_na_data(r.data).get(r.id_ator), "sem filiação na data"),
                     "Natureza do registro": "Condenação em ação penal originária no STF (procedente ou procedente em parte)",
                     "Tipificação registrada": str(r.tipificacao) if pd.notna(r.tipificacao) else "não registrada",
                     "Situação processual na data de corte": "Último status registrado na base para a pessoa na ação; recursos, trânsito em julgado e revisões posteriores não foram lidos (D-065)",
                     "Fonte": fonte})
    tabela(pd.DataFrame(rows), "atlas_condenacoes", titulo="Condenações de parlamentares ou ex-parlamentares em ações penais originárias no STF registradas na base",
           unidade="registros", periodo="2003–2026 (data de corte 23/09/2026)", universo=f"{len(rows)} status \"condenado em tribunal superior\" por pessoa e ação (D-065)",
           fonte=F_STF, notas="Status formal, não juízo sobre os fatos. A contagem difere da nota técnica do foro (24), que conta por ação e com outra regra; aqui, por pessoa e ação. Revisão jurídica recomendada antes de qualquer publicação.",
           codigo="J3")
    R["p8_condenacoes"] = len(rows)
    # TCU (pessoas com mais decisões), com cargo
    tc = st[st.status == "contas_julgadas_irregulares"].copy(); tc["data"] = pd.to_datetime(tc.data, errors="coerce")
    g = tc.groupby("id_ator").agg(n=("id_status", "count"), primeira=("data", "min"), ultima=("data", "max")).sort_values("n", ascending=False).head(15)
    rows = []
    for i, r in g.iterrows():
        rows.append({"Nome": str(NOME_ATOR.get(i, i)).title(), "Decisões (trânsito em julgado)": int(r.n), "Período das decisões": f"{r.primeira.year}–{r.ultima.year}",
                     "Cargo na data da última decisão (base)": cargo_na_data(cg, i, r.ultima), "Partido na data da última decisão": SIGLA.get(partido_na_data(r.ultima).get(i), "sem filiação na data"),
                     "Natureza do registro": "Contas julgadas irregulares pelo TCU (processo de contas; não é condenação penal)"})
    tabela(pd.DataFrame(rows), "atlas_tcu", titulo="Pessoas da base com mais decisões de contas julgadas irregulares no TCU", unidade="decisões",
           periodo="2003–2026", universo="262 decisões sobre 84 pessoas ligadas pela candidatura (D-064)", fonte=F_TCU,
           notas="A decisão pode se referir a função de gestor (por exemplo, prefeito), não ao mandato parlamentar; a lista pública não traz revisões.", codigo="J9")
    # casos de referência: contagens por caso e status
    p = ler("processos", low_memory=False); cs = ler("casos")
    x = st.merge(p[["id_processo", "id_caso"]], on="id_processo"); x = x[x.id_caso.notna()]
    t = x.groupby(["id_caso", "status"]).agg(registros=("id_status", "count"), pessoas=("id_ator", "nunique"), primeira=("data", "min"), ultima=("data", "max")).reset_index()
    t["Caso"] = t.id_caso.map(cs.set_index("id_caso").nome)
    tabela(t[["Caso", "status", "registros", "pessoas", "primeira", "ultima"]].rename(columns={"status": "Status formal", "registros": "Registros", "pessoas": "Pessoas", "primeira": "Primeira data", "ultima": "Última data"}),
           "atlas_casos", titulo="Casos de referência: status formais registrados por caso", unidade="registros e pessoas", periodo="2007–2026",
           universo="Quatro casos-teste da etapa E9 (D-046, D-052)", fonte="STF, TRF4, JFPR, STJ, TJMG (fontes oficiais listadas em fontes.csv para cada status)",
           notas="Contagens, sem nomes: os casos servem para verificar se o universo captura episódios conhecidos. Condenações anuladas continuam registradas como fato histórico, seguidas do status de anulação.", codigo="Atlas D")
    gravar_resultados(R)
    print(len(rows), R)


if __name__ == "__main__":
    main()
