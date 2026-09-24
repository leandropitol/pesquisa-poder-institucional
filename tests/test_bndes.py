"""Normalização do BNDES: números no formato publicado e chave estável por linha."""

import pytest

from src.normalizacao.bndes import chave_linha, numero_br


def test_numero_no_formato_publicado():
    assert numero_br("64400000,0") == "64400000.0"
    assert numero_br("63847527,21999999") == "63847527.21999999"
    assert numero_br("1.234,5") == "1234.5"
    assert numero_br(" ") == ""
    with pytest.raises(ValueError):
        numero_br("abc")


def test_chave_da_linha_nao_depende_da_ordem_das_colunas():
    a = {"numero": "1", "valor": "10,0", "pais": "PAIS TESTE"}
    b = {"pais": "PAIS TESTE", "valor": "10,0", "numero": "1"}
    assert chave_linha(a, 1) == chave_linha(b, 1)
    assert chave_linha(a, 1) != chave_linha(a, 2)
    assert chave_linha(a, 1) != chave_linha({**a, "valor": "11,0"}, 1)
