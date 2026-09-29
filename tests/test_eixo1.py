"""Testes do eixo 1 ampliado (D-060, D-061). Dados fictícios."""

import numpy as np

from src.analise.eixo1 import MOTIVOS_EIXO1, MOTIVOS_LISTA, digitos, homogeneidade, qui2


def test_digitos():
    assert digitos("599.981.481-20") == "59998148120" and digitos(None) == ""


def test_qui2_zero_quando_taxas_iguais():
    assert abs(float(qui2(np.array([5.0, 10.0]), np.array([100.0, 200.0])))) < 1e-9


def test_homogeneidade():
    _, p_igual = homogeneidade(np.array([5, 10, 15]), np.array([100, 200, 300]))
    _, p_diferente = homogeneidade(np.array([30, 2, 1]), np.array([100, 100, 100]))
    assert p_igual > 0.5 and p_diferente < 0.001


def test_motivos():
    assert "ficha limpa (lc 64/90)" in MOTIVOS_EIXO1 and "ausencia de requisito de registro" not in MOTIVOS_EIXO1
    assert any(m in "fraude a cota de genero no drap" for m in MOTIVOS_LISTA)
