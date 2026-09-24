"""Detecção de partidos em listas de membros e períodos de observação (bloco D). Listas fictícias."""

import re

from src.normalizacao.redes import deteccoes
from src.normalizacao.redes_base import periodos

NOMES = [(re.compile(r"\bPartido\s+dos\s+Trabalhadores\b", re.I), "PT", False),
         (re.compile(r"\bDemocratas\b", re.I), "DEM", True)]
SIGLAS = {"PT": "PT", "PDT": "PDT", "DEM": "DEM"}


def siglas(texto):
    return {a["sigla"] for a in deteccoes(texto, NOMES, SIGLAS)}


def test_nome_ambiguo_so_perto_do_pais():
    assert siglas("Bolivia Movimiento Democratas Chile Partido X") == set()
    assert siglas("Brazil Democratas Member category: Full") == {"DEM"}


def test_sigla_so_depois_do_pais():
    assert siglas("Argentina PDT Chile PS") == set()
    assert siglas("Brasil Partido Democrático Trabalhista (PDT) Chile PS") == {"PDT"}
    assert siglas("Partido dos Trabalhadores") == {"PT"}


def test_periodos_so_interrompem_em_ano_informativo():
    obs = {"2014": ["20140801"], "2015": ["20150701"], "2018": ["20180701"]}
    # 2016 sem cópia informativa não interrompe; 2017 com cópia sem o partido interrompe
    blocos = periodos(obs, {"2014", "2015", "2017", "2018"})
    assert blocos == [(["20140801", "20150701"], False), (["20180701"], True)]
