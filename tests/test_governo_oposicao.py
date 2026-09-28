"""Testes da classificação de governo e oposição (D-050, D-051). Entidades fictícias."""

import pandas as pd

from src.simetria.governo_oposicao import Siglas, concordancia, grupo_de, grupo_na_data, membros_bloco, segmento


def test_membros_bloco():
    assert membros_bloco("PpMdbPtb") == ["PP", "MDB", "PTB"]
    assert membros_bloco("Bl MdbPsdRepPode") == ["MDB", "PSD", "REPUBLICANOS", "PODE"]
    assert membros_bloco("PsbPdtPCdoBPmnPrb") == ["PSB", "PDT", "PCDOB", "PMN", "PRB"]
    assert membros_bloco("Bl PlFdrPTUniPp...") == ["PL", "PT", "PCDOB", "PV", "UNIÃO", "PP"]
    assert membros_bloco("PL/PSL") == ["PL", "PSL"]


def test_regra_de_grupo():
    assert grupo_de(0.9, 30) == "governo" and grupo_de(2 / 3, 30) == "governo"
    assert grupo_de(0.6, 30) == "nenhum" and grupo_de(0.5, 30) == "nenhum" and grupo_de(0.49, 30) == "oposicao"
    assert grupo_de(1.0, 9) == "sem_classificacao"


def test_concordancia_so_sim_e_nao():
    g = pd.DataFrame({"orientacao": ["Sim", "Não", "Obstrução", "Liberado", "Sim"], "gov": ["Sim", "Sim", "Não", "Sim", "Obstrução"]})
    assert concordancia(g) == (2, 1, 0.5)
    n, k, _ = concordancia(g, obstrucao_como_nao=True)
    assert (n, k) == (4, 2)


def test_segmento_e_grupo_na_data():
    pres = pd.DataFrame({"presidente": ["A", "B"], "inicio": ["2015-01-01", "2016-05-12"], "fim": ["2016-05-11", "2018-12-31"]})
    assert segmento("2016-03-01", pres) == ("A", "2016-01-01", "2016-05-11")
    assert segmento("2016-06-01", pres) == ("B", "2016-05-12", "2016-12-31")
    t = pd.DataFrame({"id_partido": ["P1", "P1"], "inicio": ["2016-01-01", "2016-05-12"], "fim": ["2016-05-11", "2016-12-31"],
                      "grupo": ["governo", "oposicao"]})
    assert grupo_na_data(t, "P1", "2016-06-01") == "oposicao" and grupo_na_data(t, "P2", "2016-06-01") == "sem_classificacao"


def test_siglas_por_vigencia():
    d = pd.DataFrame({"id_partido": ["X1", "X2", "X2"], "sigla": ["PL", "PR", "PL"], "data_inicio": ["", "2006-12-19", "2019-02-09"],
                      "data_fim": ["2006-12-19", "2019-02-09", ""]})
    s = Siglas(d)
    assert s("PL", "2004-01-01") == "X1" and s("PL", "2020-01-01") == "X2" and s("PR", "2010-01-01") == "X2"
