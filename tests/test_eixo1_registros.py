"""Testes dos registros individuais do TCU e do TSE (D-064)."""

import pandas as pd

from src.analise.eixo1_parlamentares import marcar
from src.normalizacao.eixo1_registros import cnj


def test_cnj_formata_20_digitos():
    assert cnj("06031901620226190000") == "0603190-16.2022.6.19.0000"
    assert cnj("SQ123") == ""
    assert cnj("") == ""


def test_medidas_no_periodo_e_acumulado():
    u = pd.DataFrame({"id_ator": ["A", "A", "B"]})
    datas = {"A": ["2010-05-01"]}
    ini = pd.Series(["2007-02-01", "2011-02-01", "2007-02-01"])
    fim = pd.Series(["2011-01-31", "2015-01-31", "2011-01-31"])
    r = marcar(u, datas, ini, fim)
    assert r["tcu_no_periodo"].tolist() == [True, False, False]
    assert r["tcu_acumulado"].tolist() == [True, True, False]
