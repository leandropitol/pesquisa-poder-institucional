"""Datas, temas e nomes dos atos do Concórdia (bloco B). Registros fictícios."""

from src.normalizacao.concordia import data_iso, norm, tema


def test_data_iso():
    assert data_iso("24/12/2025") == "2025-12-24"
    assert data_iso("") == ""
    assert data_iso(None) == ""
    assert data_iso("2025-12-24") == ""


def test_norm_tira_acento_e_espaco():
    assert norm("  Bahrein ") == "bahrein"
    assert norm("República do Congo") == "republica do congo"


def test_tema_prefere_assunto_principal():
    assuntos = [{"Nome": "Saúde", "IsPrincipal": False}, {"Nome": "Educação e Cultura", "IsPrincipal": True}]
    assert tema(assuntos) == "Educação e Cultura"
    assert tema([{"Nome": "Saúde", "IsPrincipal": False}]) == "Saúde"
    assert tema(None) == ""
