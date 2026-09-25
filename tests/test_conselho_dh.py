"""Leitura das listas de votos do Conselho de Direitos Humanos (bloco A2). Trechos fictícios no formato da ONU."""

import re

from src.normalizacao.conselho_dh import RE_VOTO, data_iso, paises

MAPA = {"BRAZIL": "BRA", "CHILE": "CHL", "IRELAND": "IRL", "UNITED KINGDOM OF GREAT BRITAIN AND NORTHERN IRELAND": "GBR",
        "UNITED ARAB EMIRATES": "ARE", "BOSNIA AND HERZEGOVINA": "BIH", "CUBA": "CUB"}
PADRAO = re.compile(r"(?<![A-Z])(" + "|".join(re.escape(n) for n in sorted(MAPA, key=len, reverse=True)) + r")(?![A-Z])")


def test_nome_mais_longo_tem_prioridade_e_cabecalho_de_pagina_sai():
    lista = "Brazil, Bosnia and Herzegovina, United Arab A/HRC/RES/37/35 7 Emirates and United Kingdom of Great Britain and Northern Ireland"
    achados, sobra = paises(lista, MAPA, PADRAO)
    assert sorted(achados) == ["ARE", "BIH", "BRA", "GBR"]
    assert sobra == ""


def test_voto_com_variacoes_de_redacao():
    atual = ("[Adopted by a recorded vote of 2 to 1, with no abstentions.* The voting was as follows:3 In favour: Brazil and Chile "
             "Against: Cuba]")
    antigo = "[Resolution adopted by a recorded vote of 2 votes to 1, with 0 abstentions. The voting was as follows: In favour: Brazil, Chile. Against: Cuba.]"
    for texto in (atual, antigo):
        m = RE_VOTO.search(texto)
        assert m and m.group(1) == "2" and m.group(2) == "1"
        assert sorted(paises(m.group(4), MAPA, PADRAO)[0]) == ["BRA", "CHL"]


def test_data_de_adocao_ou_da_reuniao():
    assert data_iso("Resolution adopted by the Human Rights Council on 3 April 2023 52/2.") == "2023-04-03"
    assert data_iso("... 40th meeting 27 March 2008 [Adopted by ...]") == "2008-03-27"
    assert data_iso("sem data") == ""
