"""Testes do eixo 3, primeira parte (D-067)."""

import pandas as pd

from src.analise.eixo3 import eh_turma, resolver_ministro, tabela_2x2


def comp():
    return pd.DataFrame({"chave": ["ana silva", "bruno costa"], "nome_guerra": ["Ana Silva", "Bruno Costa"], "presidente": ["P1", "P2"],
                         "data_posse": ["2000-01-01", "2010-01-01"], "data_fim": ["2009-12-31", ""], "indicado_por_pt": [True, False]})


def dec():
    return pd.DataFrame({"Processo": ["AP 1", "AP 1", "AP 1", "AP 2"], "data": ["2005-01-01", "2005-06-01", "2005-06-01", "2012-01-01"],
                         "ministro": ["ana silva", "ana silva", "bruno costa", "bruno costa"],
                         "Origem decisão": ["1ª TURMA", "1ª TURMA", "1ª TURMA", "TRIBUNAL PLENO"]})


def test_ministro_unico_na_data_e_em_exercicio():
    assert resolver_ministro("AP 1", "2005-01-01", dec(), comp())["nome_guerra"] == "Ana Silva"
    assert resolver_ministro("AP 2", "2012-01-01", dec(), comp())["nome_guerra"] == "Bruno Costa"


def test_ministro_fora_de_exercicio_nao_resolve():
    d = dec().assign(data=["2001-01-01", "2001-01-01", "2001-01-01", "2001-01-01"])
    assert resolver_ministro("AP 2", "2001-01-01", d, comp()) is None  # Bruno Costa só toma posse em 2010


def test_varios_ministros_na_data_usa_o_relator_da_acao():
    assert resolver_ministro("AP 1", "2005-06-01", dec(), comp())["nome_guerra"] == "Ana Silva"  # 2 decisões dela até a data, 1 dele


def test_turma_ou_plenario():
    assert eh_turma("AP 1", "2005-06-01", dec())
    assert not eh_turma("AP 2", "2012-01-01", dec())


def test_tabela_2x2():
    x = pd.DataFrame({"indicado_por_pt": [True] * 4 + [False] * 4, "condenado": [True, True, False, False, True, False, False, False]})
    r = tabela_2x2("teste", x)
    assert (r["julgados_indicados_pt"], r["condenados_indicados_pt"], r["julgados_outros"], r["condenados_outros"]) == (4, 2, 4, 1)
    assert 0 < r["p_fisher"] <= 1
