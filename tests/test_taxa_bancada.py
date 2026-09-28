"""Testes da taxa por bancada (D-049). Entidades fictícias."""

import math

import pandas as pd

from src.simetria.taxa_bancada import legislatura, pares, tabela, wilson


def test_wilson():
    a, b = wilson(0, 50)
    assert a == 0 and 0.05 < b < 0.08
    a, b = wilson(5, 100)
    assert a < 0.05 < b
    assert all(math.isnan(x) for x in wilson(0, 0))


def test_legislatura():
    assert legislatura("2007-01-31") == 52 and legislatura("2007-02-01") == 53 and legislatura("2002-12-31") is None


def test_pares_e_taxa():
    cargos = pd.DataFrame({"id_ator": ["A1", "A2", "A3", "A4"],
                           "cargo": ["Deputado federal (titular), legislatura 53", "Senador (titular)",
                                     "Senador (1º suplente)", "Deputado federal (titular), legislatura 53"],
                           "data_inicio": ["2007-02-01", "2003-02-01", "2003-02-01", "2007-02-01"],
                           "data_fim": ["2011-01-31", "2011-01-31", "2011-01-31", "2011-01-31"]})
    fil = pd.DataFrame({"id_ator": ["A1", "A1", "A2", "A4"], "id_partido": ["P1", "P2", "P2", "P1"],
                        "data_inicio": ["2003-01-01", "2009-01-01", "2003-02-01", "2007-02-01"], "data_fim": ["2008-12-31", "", "", ""]})
    p = pares(cargos, fil)
    # senador titular entra nas duas legislaturas; suplente de senador fica fora
    assert sorted(zip(p["id_ator"], p["legislatura"])) == [("A1", 53), ("A2", 52), ("A2", 53), ("A4", 53)]
    assert p.set_index(["id_ator", "legislatura"]).loc[("A1", 53), "id_partido"] == "P1"  # partido no início do mandato
    m = pd.DataFrame({"id_ator": ["A1", "A1"], "ap": ["AP 1", "AP 2"], "universo": ["sim", "revisar"], "a_conferir": [False, False],
                      "leg_reu": [53, 53], "leg_cond": [None, None]})
    t = tabela(p, m, {"P1": "UM", "P2": "DOIS"}).set_index(["sigla", "legislatura"])
    assert t.loc[("UM", "53"), "bancada"] == 2 and t.loc[("UM", "53"), "n_reu"] == 1 and t.loc[("UM", "53"), "taxa_reu"] == 0.5
    assert t.loc[("DOIS", "52-57"), "bancada"] == 2 and t.loc[("DOIS", "52-57"), "n_reu"] == 0
