"""Linhagem de partidos e resolução de siglas. Tabelas fictícias no formato da página do TSE."""

from src.normalizacao.partidos import Resolvedor, apelidos_por_nome, data_iso, linhagem, partidos_da_celula, sigla_e_nome

CAB = ["", "A", "B", "PROCESSO", "DATA"]


def tabelas(fusoes=(), incorporacoes=(), mudancas=(), registrados=()):
    reg = [["0001", "SIGLA", "NOME", "DEFERIMENTO", "PRES", "Nº"]] + [[str(i), *r] for i, r in enumerate(registrados, 1)]
    return [
        {"i": 0, "linhas": reg},
        {"i": 1, "linhas": [CAB] + [[str(i), *f] for i, f in enumerate(fusoes, 1)]},
        {"i": 2, "linhas": [CAB] + [[str(i), *f] for i, f in enumerate(incorporacoes, 1)]},
        {"i": 3, "linhas": [CAB] + [[str(i), *f] for i, f in enumerate(mudancas, 1)]},
        {"i": 4, "linhas": [["x"]]},
    ]


def test_textos_da_pagina():
    assert sigla_e_nome("Partido Teste Um (PTU)*") == ("PTU", "Partido Teste Um")
    assert sigla_e_nome("Patriota Teste (PAT).") == ("PAT", "Patriota Teste")
    assert sigla_e_nome("NOVONOME") == ("NOVONOME", "NOVONOME")
    assert partidos_da_celula("Partido A (PA) e Partido B (P do B)") == [("PA", "Partido A"), ("PDOB", "Partido B")]
    assert data_iso("1°.7.1988") == "1988-07-01" and data_iso("08/02/2022") == "2022-02-08"


def base_ficticia():
    return tabelas(
        fusoes=[["Partido Um (PU) e Partido Dois (PD)", "Partido Tres (PT3)", "RPP 1", "10/05/2010"]],
        incorporacoes=[["Partido Quatro (PQ)", "Partido Tres (PT3)", "PET 2", "01/03/2015"]],
        mudancas=[["Partido Tres (PT3)", "Novo Tres (N3)", "PET 3", "20/06/2018"],
                  ["Partido Seis (PU)", "Sexto (SX)", "PET 4", "01/01/2020"]],
        registrados=[["N3", "NOVO TRES", "10.5.2010", "X", "33"], ["SX", "SEXTO", "5.5.2012", "Y", "66"]],
    )


def test_linhagem_fusao_incorporacao_e_mudanca():
    ps = {p.chave: p for p in linhagem(base_ficticia())}
    assert set(ps) == {"partido_tse:PU|ate:2010-05-10", "partido_tse:PD|ate:2010-05-10", "partido_tse:PT3|N3",
                       "partido_tse:PQ|ate:2015-03-01", "partido_tse:PU|SX"}
    novo = ps["partido_tse:PT3|N3"]
    assert [(d.sigla, d.inicio, d.fim) for d in novo.denominacoes] == [("PT3", "2010-05-10", "2018-06-20"), ("N3", "2018-06-20", "")]
    assert ps["partido_tse:PU|ate:2010-05-10"].destino[0] == "fundiu_se_em" and ps["partido_tse:PU|ate:2010-05-10"].destino[1] is novo
    assert ps["partido_tse:PQ|ate:2015-03-01"].destino[:2] == ("incorporado_por", novo)
    # a mesma sigla "PU" em dois partidos diferentes: o fundido em 2010 e o registrado em 2012
    assert ps["partido_tse:PU|SX"].denominacoes[0].inicio == "2012-05-05"


def test_resolvedor_por_data_e_sigla_reutilizada():
    partidos = linhagem(base_ficticia())
    r = Resolvedor(partidos)
    chave = lambda s, d: (r(s, d)[0].chave, r(s, d)[1])
    assert chave("PU", "2008-01-01") == ("partido_tse:PU|ate:2010-05-10", "vigencia")
    assert chave("PU", "2013-01-01") == ("partido_tse:PU|SX", "vigencia")
    assert chave("PT3", "2016-01-01") == ("partido_tse:PT3|N3", "vigencia")
    # a fonte grava a sigla nova em registro antigo: só um partido que usou N3 existia na data
    assert chave("N3", "2012-01-01") == ("partido_tse:PT3|N3", "partido_existente")
    assert r("ZZ", "2012-01-01") == (None, "sem_correspondencia")


def test_apelido_pelo_nome_publicado_pela_fonte():
    partidos = linhagem(base_ficticia())
    apelidos = apelidos_por_nome(partidos, {"NTR": "Novo Três", "XX": "Nome Inexistente", "N3": "NOVO TRES"})
    assert apelidos == {"NTR": ["N3", "PT3"]}
    assert Resolvedor(partidos, apelidos)("NTR", "2019-01-01")[0].chave == "partido_tse:PT3|N3"
