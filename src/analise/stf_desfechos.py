"""Desfechos de mérito das ações penais do STF para parlamentares da base (D-065): condenação x absolvição por partido, governo/oposição e faixa.

Unidade: parlamentar (pessoa com filiação na base) x ação penal, com o primeiro desfecho de mérito registrado (`condenado_tribunal_superior` ou `absolvido`) na base, nas ações penais do STF
(inclui a AP 470 da E9). Partido = filiação do parlamentar na data do desfecho; governo/oposição = classificação do partido na data (D-050);
faixa = posição ideológica do partido (D-062).

Medida: proporção de condenados entre os julgados no mérito (IC de Wilson). Testes: homogeneidade entre partidos com 5 ou mais julgados (simulação exata,
como em D-060) e Fisher entre governo e oposição. O número de julgados é pequeno: os testes têm pouco poder e servem para dizer o que não se distingue.

Cobertura: das ações julgadas no mérito com réu ligado a parlamentar, quantas têm desfecho registrado na pessoa; o restante está em
relatorios/tabelas/stf_desfechos_pendentes.csv. A seleção do que foi possível registrar (ação de um réu ou curada) não é aleatória: ver limitações.

Saídas: relatorios/tabelas/stf_desfechos_taxas.csv, stf_desfechos_homogeneidade.csv e stf_desfechos_cobertura.csv.

Uso:
    python -m src.analise.stf_desfechos
"""

import pandas as pd
from scipy.stats import fisher_exact

from src.analise.eixo1 import homogeneidade
from src.analise.etica import linha, partido_em
from src.analise.ideologia import ORDEM
from src.base import RAIZ, ler
from src.simetria.governo_oposicao import grupo_na_data, ler_tabela as ler_tabela_governo

SAIDA = RAIZ / "relatorios" / "tabelas"
MERITO = ("condenado_tribunal_superior", "absolvido")
MIN_JULGADOS = 5


def julgados() -> pd.DataFrame:
    proc, st = ler("processos"), ler("status_pessoa_processo")
    stf = ler("instituicoes").query("sigla == 'STF'")["id_instituicao"].iloc[0]
    ap = proc[(proc["classe"] == "acao_penal") & (proc["id_tribunal"] == stf)][["id_processo", "numero_originario"]]
    s = st[st["status"].isin(MERITO)].merge(ap, on="id_processo").sort_values("data")
    s = s.drop_duplicates(["id_ator", "id_processo"], keep="first")
    fil, gov = ler("filiacoes").sort_values("data_inicio"), ler_tabela_governo()
    s["id_partido"] = [partido_em(fil, a, d) for a, d in zip(s["id_ator"], s["data"])]
    s = s[s["id_partido"] != ""].copy()  # sem filiação na base: não é parlamentar (réus da AP 470 de fora do Congresso)
    s["grupo"] = [grupo_na_data(gov, p, d) for p, d in zip(s["id_partido"], s["data"])]
    s["condenado"] = s["status"] == "condenado_tribunal_superior"
    return s


def run() -> None:
    s = julgados()
    sigla = dict(zip(ler("instituicoes")["id_instituicao"], ler("instituicoes")["sigla"]))
    esc = ler("posicao_ideologica")
    faixa = dict(zip(esc[esc["escala"] == "brc_2018"]["id_partido"], esc[esc["escala"] == "brc_2018"]["faixa"]))
    s["faixa"] = s["id_partido"].map(faixa).fillna("sem_escore")
    linhas = []
    for tipo, col in (("partido", "id_partido"), ("governo_oposicao", "grupo"), ("faixa_ideologica", "faixa")):
        for g, x in s.groupby(col):
            linhas.append(linha("condenacao_entre_julgados", "2003-2026", tipo, g or "sem_partido", x["condenado"].sum(), len(x), sigla.get(g, g) if tipo == "partido" else ""))
    t = pd.DataFrame(linhas)
    t["ordem"] = t["grupo"].map({f: i for i, f in enumerate(ORDEM)}).fillna(99)
    t.sort_values(["grupo_tipo", "ordem", "grupo"]).drop(columns="ordem").rename(columns={"n_unidades": "n_julgados", "com_registro": "condenados"}).to_csv(
        SAIDA / "stf_desfechos_taxas.csv", index=False, encoding="utf-8")
    g = s.groupby("id_partido")["condenado"].agg(["sum", "count"])
    g = g[(g["count"] >= MIN_JULGADOS) & (g.index != "")]
    est, p = homogeneidade(g["sum"].to_numpy(), g["count"].to_numpy())
    gov, opo = s[s["grupo"] == "governo"], s[s["grupo"] == "oposicao"]
    tab = [[int(gov["condenado"].sum()), len(gov) - int(gov["condenado"].sum())], [int(opo["condenado"].sum()), len(opo) - int(opo["condenado"].sum())]]
    pd.DataFrame([{"teste": "homogeneidade entre partidos", "grupos": len(g), "julgados": int(g["count"].sum()), "estatistica": est, "p_valor": p},
                  {"teste": "governo x oposicao (Fisher)", "grupos": 2, "julgados": len(gov) + len(opo), "estatistica": float("nan"), "p_valor": fisher_exact(tab)[1]}]
                 ).to_csv(SAIDA / "stf_desfechos_homogeneidade.csv", index=False, encoding="utf-8")
    # cobertura: ações julgadas no mérito com réu ligado a parlamentar
    from src.normalizacao.simetria_stf import carregar
    c = carregar()
    aps = {ap for (ap, _n) in c["lig"]}
    lista = c["lista"]
    merito = {ap for ap in aps if ap in lista.index and lista.loc[ap, "julgada_no_merito"] == "True"}
    com = set(s["numero_originario"])
    pd.DataFrame([{"acoes_julgadas_no_merito_com_reu_parlamentar": len(merito), "com_desfecho_na_pessoa": len(merito & com), "sem_desfecho_na_pessoa": len(merito - com),
                   "julgados_pessoa_acao": len(s)}]).to_csv(SAIDA / "stf_desfechos_cobertura.csv", index=False, encoding="utf-8")
    print(f"julgados (pessoa x ação): {len(s)}; condenados: {int(s['condenado'].sum())}")
    print(t.sort_values(["grupo_tipo", "grupo"])[["grupo_tipo", "sigla", "n_julgados" if "n_julgados" in t else "n_unidades", "com_registro", "taxa"]].round(3).to_string(index=False))
    print(pd.read_csv(SAIDA / "stf_desfechos_homogeneidade.csv").round(4).to_string(index=False))
    print(pd.read_csv(SAIDA / "stf_desfechos_cobertura.csv").to_string(index=False))


if __name__ == "__main__":
    run()
