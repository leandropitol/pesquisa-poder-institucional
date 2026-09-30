"""Testes dos desfechos das ações penais do STF (D-065)."""

from src.normalizacao.stf_desfechos import PLURAL, classificar_extincao, formas, limpo, vinculo


def test_formas_separa_ou_e_apelido():
    assert formas("ANÍBAL FERREIRA GOMES OU ANÍBAL GOMES") == {"anibal ferreira gomes", "anibal gomes"}
    assert formas("LUIZ CARLOS DA SILVA (PROFESSOR LUIZINHO)") == {"luiz carlos da silva"}


def test_vinculo_civil_curada_e_sufixo():
    civ = {"A1": {"nelson meurer"}}
    assert vinculo("NELSON MEURER", "A1", "automatica", "nelson meurer", civ) == "civil"
    # sufixo no réu que o ator não tem: só vale pelo nome civil
    assert vinculo("NELSON MEURER JÚNIOR", "A1", "aceita", "nelson meurer", civ) == ""
    assert vinculo("FULANO SILVA", "A2", "aceita", "fulano silva", {}) == "curada"
    assert vinculo("FULANO SILVA", "A2", "automatica", "fulano silva", {}) == ""
    assert vinculo("FULANO SILVA", "A2", "e9:nome_igual", "fulano silva", {}) == "curada"


def test_extincao_exige_causa_e_nao_nomear_outra_pessoa():
    assert classificar_extincao("declarou extinta a punibilidade pela prescrição da pretensão punitiva", "JADER BARBALHO") == ("prescrito", "prescrição da pretensão punitiva")
    assert classificar_extincao("EM 27/02/2014", "JOÃO RIBEIRO") is None
    assert classificar_extincao("*NI*", "JOÃO RIBEIRO") is None
    assert classificar_extincao("DECRETO EXTINTA A PUNIBILIDADE DO RÉU RAIMUNDO ANTÔNIO FILHO, ART. 107, INCISO I", "JACKSON BARRETO DE LIMA") is None
    st, _ = classificar_extincao("com base no atestado de óbito, declaro extinta a punibilidade do réu CLODOVIL HERNANDES", "CLODOVIL HERNANDES")
    assert st == "punibilidade_extinta"


def test_marcador_de_varios_reus_e_limpeza():
    assert PLURAL.search("absolveu os réus")
    assert PLURAL.search("desmembrou a ação penal")
    assert not PLURAL.search("absolveu o réu Sérgio Ivan Moraes")
    assert limpo("a_x000D_ b\n c") == "a b c"
