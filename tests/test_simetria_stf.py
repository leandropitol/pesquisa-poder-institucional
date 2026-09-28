"""Testes da ligação réu -> parlamentar e do partido na data (D-048). Entidades fictícias."""

import pandas as pd

from src.normalizacao.simetria_stf import partido_na_data, propor


def _base():
    atores = pd.DataFrame({"id_ator": ["A1", "A2", "A3"], "nome_normalizado": ["joao silveira", "marco antonio", "marco tebaldo"]})
    cargos = pd.DataFrame({"id_ator": ["A1", "A2", "A3"], "cargo": ["Deputado federal (titular), legislatura 54"] * 3,
                           "data_inicio": ["2011-02-01"] * 3, "data_fim": ["2015-01-31"] * 3})
    lista = pd.DataFrame({"data_autuacao": ["2012-01-01", "2020-01-01"], "data_ultimo_julgamento": ["2014-01-01", "2021-01-01"]},
                         index=["AP 1", "AP 2"])
    return atores, cargos, lista


def test_ligacao_forte_exige_prenome_e_sobrenome():
    atores, cargos, lista = _base()
    r = propor([{"ap": "AP 1", "incidente": "1", "nome": "JOÃO PEDRO SILVEIRA"}], lista, atores, cargos)
    assert [(x["id_ator"], x["forte"]) for x in r] == [("A1", True)]


def test_dois_candidatos_ficam_fracos():
    atores, cargos, lista = _base()
    r = propor([{"ap": "AP 1", "incidente": "1", "nome": "MARCO ANTÔNIO TEBALDO"}], lista, atores, cargos)
    assert {x["id_ator"] for x in r} == {"A2", "A3"} and not any(x["forte"] for x in r)


def test_sem_mandato_no_periodo_nao_liga():
    atores, cargos, lista = _base()
    assert propor([{"ap": "AP 2", "incidente": "2", "nome": "JOÃO PEDRO SILVEIRA"}], lista, atores, cargos) == []


def test_partido_na_data():
    f = pd.DataFrame({"id_ator": ["A1", "A1"], "id_partido": ["P1", "P2"], "data_inicio": ["2003-02-01", "2011-02-01"],
                      "data_fim": ["2007-01-31", "2015-01-31"]})
    assert partido_na_data(f, "A1", "2012-05-01") == {"P2"}
    assert partido_na_data(f, "A1", "2009-05-01") == {"P1"}  # sem filiação vigente: a última iniciada antes
    assert partido_na_data(f, "A1", "2001-01-01") == set()


def test_linhas_que_nao_sao_pessoa():
    from src.normalizacao.simetria_stf import NAO_PESSOA, so_iniciais
    assert NAO_PESSOA.match("MINISTÉRIO PÚBLICO FEDERAL") and NAO_PESSOA.match("OS MESMOS")
    assert not NAO_PESSOA.match("OSMAR MESMOS SILVA")
    assert so_iniciais("J. A. G. C.") and so_iniciais("S A S") and not so_iniciais("JOÃO A. SILVA")
