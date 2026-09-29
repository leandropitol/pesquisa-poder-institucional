"""Testes da posição ideológica (D-062)."""

import numpy as np

from src.analise.ideologia import spearman_permutacao
from src.normalizacao.ideologia import faixa, tabela_1


def test_faixa_cortes_do_artigo():
    assert faixa(1.5) == "extrema_esquerda" and faixa(1.51) == "esquerda" and faixa(3.0) == "esquerda"
    assert faixa(4.49) == "centro_esquerda" and faixa(4.5) == "centro" and faixa(5.51) == "centro_direita"
    assert faixa(7.01) == "direita" and faixa(8.5) == "direita" and faixa(8.51) == "extrema_direita"


def test_tabela_1():
    h = ("<table><tr><th>Partido</th><th>Média</th><th>Mediana</th><th>Moda</th><th>Desvio Padrão</th><th>N</th><th>Coeficiente</th></tr>"
         "<tr><td>XX</td><td>2,5</td><td>3</td><td>3</td><td>1,2</td><td>400</td><td>40</td></tr></table>").encode("utf-8")
    t = tabela_1(h)
    assert t.iloc[0].tolist()[:6] == ["XX", "2,5", "3", "3", "1,2", "400"]


def test_spearman_permutacao():
    r, p = spearman_permutacao(np.arange(10.0), np.arange(10.0) * 2)
    assert abs(r - 1) < 1e-9 and p < 0.001
