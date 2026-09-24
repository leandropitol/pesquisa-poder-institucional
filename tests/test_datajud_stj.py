"""Normalização do STJ via DataJud: datas da fonte e pertença ao universo do eixo 1. Dados fictícios."""

from src.normalizacao.datajud_stj import data_valida, no_universo

HOJE = "2026-09-24"


def test_formatos_de_data_da_fonte():
    assert data_valida("20150301000000", HOJE) == "2015-03-01"
    assert data_valida("2017-12-22T00:00:00.000Z", HOJE) == "2017-12-22"
    assert data_valida("26090101000000", HOJE) == ""  # ano impossível na fonte
    assert data_valida("19800101000000", HOJE) == ""  # antes da instalação do STJ
    assert data_valida("20151340000000", HOJE) == ""  # mês inválido
    assert data_valida(None, HOJE) == ""


def test_pertenca_ao_universo_pelos_assuntos():
    regras = {"1": "inclui", "2": "conexo", "3": "exclui", "4": "indeterminado", "5": "qualificador"}
    assert no_universo(["1", "3"], regras) == "sim"
    assert no_universo(["2"], regras) == "nao"          # conexo sozinho não entra
    assert no_universo(["3", "5"], regras) == "nao"
    assert no_universo(["4"], regras) == "revisar"      # assunto genérico
    assert no_universo(["99"], regras) == "revisar"     # assunto sem regra na curadoria
