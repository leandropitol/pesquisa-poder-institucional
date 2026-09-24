"""Funções puras da normalização da etapa E1. Dados fictícios."""

from src.normalizacao.legislativo import cargo_senado, equivalencias, normalizar_nome, periodos_camara, sigla_valida, universo_do_ano

LEGS = {52: ("2003-02-01", "2007-01-31"), 53: ("2007-02-01", "2011-01-31")}


def r(data, sigla, situacao="Exercício", leg=52, cond="Titular"):
    return {"dataHora": data, "siglaPartido": sigla, "situacao": situacao, "idLegislatura": leg, "condicaoEleitoral": cond, "siglaUf": "ZZ"}


def test_normalizacao_de_nome_e_sigla():
    assert normalizar_nome("  Áéio  Ñeves ") == "aeio neves"
    assert sigla_valida(" pt ") == "PT"
    assert sigla_valida("S.PART.") is None and sigla_valida(None) is None


def test_mudanca_de_partido_fecha_o_periodo_na_data_da_troca():
    hist = [r("2003-02-01T00:00", "AAA", None), r("2003-02-01T12:00", "AAA"), r("2005-09-30T10:00", "BBB")]
    cargos, filiacoes = periodos_camara(hist, LEGS, "2026-09-24")
    assert cargos == [{"legislatura": 52, "inicio": "2003-02-01", "fim": "2007-01-31", "condicao": "Titular", "uf": "ZZ"}]
    assert [(f["sigla"], f["inicio"], f["fim"]) for f in filiacoes] == [("AAA", "2003-02-01", "2005-09-30"), ("BBB", "2005-09-30", "2007-01-31")]


def test_saida_antes_do_fim_da_legislatura_encerra_o_cargo():
    hist = [r("2007-02-01T12:00", "AAA", leg=53), r("2008-03-10T09:00", "AAA", "Fim de Mandato", leg=53)]
    cargos, filiacoes = periodos_camara(hist, LEGS, "2026-09-24")
    assert cargos[0]["fim"] == "2008-03-10"
    assert filiacoes[0]["fim"] == "2008-03-10"


def test_legislatura_em_curso_fica_sem_fim():
    cargos, _ = periodos_camara([r("2007-02-01T12:00", "AAA", leg=53)], LEGS, "2008-01-01")
    assert cargos[0]["fim"] == ""


def test_periodo_sem_partido_nao_vira_filiacao():
    hist = [r("2003-02-01T12:00", "AAA"), r("2004-01-10T00:00", "S.PART."), r("2004-06-01T00:00", "BBB")]
    _, filiacoes = periodos_camara(hist, LEGS, "2026-09-24")
    assert [(f["sigla"], f["inicio"], f["fim"]) for f in filiacoes] == [("AAA", "2003-02-01", "2004-01-10"), ("BBB", "2004-06-01", "2007-01-31")]


def test_legislaturas_anteriores_a_2003_ficam_fora():
    cargos, filiacoes = periodos_camara([r("1999-02-01T12:00", "AAA", leg=51)], LEGS, "2026-09-24")
    assert cargos == [] and filiacoes == []


def test_universo_do_ano_conta_so_quem_esta_em_exercicio():
    historicos = {
        1: [r("2003-02-01T12:00", "AAA")],
        2: [r("2003-02-01T12:00", "BBB"), r("2003-12-01T00:00", "BBB", "Afastado")],
        3: [r("2003-02-01T12:00", "CCC", "Afastado")],
        4: [r("2004-05-01T00:00", "DDD")],  # entrou depois da data de referência
    }
    assert universo_do_ano(historicos, LEGS, 2003) == {"AAA", "BBB"}
    assert universo_do_ano(historicos, LEGS, 2004) == {"AAA"}
    assert universo_do_ano(historicos, LEGS, 2012) == set()


def test_mandato_de_senador():
    m = {"CodigoMandato": "9", "UfParlamentar": "ZZ", "DescricaoParticipacao": "Titular",
         "PrimeiraLegislaturaDoMandato": {"DataInicio": "2003-02-01", "DataFim": "2007-01-31"},
         "SegundaLegislaturaDoMandato": {"DataInicio": "2007-02-01", "DataFim": "2011-01-31"}}
    assert cargo_senado(m, "2026-09-24") == {"codigo": "9", "inicio": "2003-02-01", "fim": "2011-01-31", "participacao": "Titular", "uf": "ZZ"}
    assert cargo_senado(m, "2010-01-01")["fim"] == ""


def test_equivalencia_unica_ambigua_e_decisao_manual():
    camara = {"1": {"nomes": {"ator teste a"}, "ufs": {"ZZ"}}, "2": {"nomes": {"ator teste b"}, "ufs": {"ZZ"}},
              "3": {"nomes": {"ator teste b"}, "ufs": {"ZZ"}}, "4": {"nomes": {"ator teste c"}, "ufs": {"YY"}}}
    senado = {"10": {"nomes": {"ator teste a"}, "ufs": {"ZZ"}}, "20": {"nomes": {"ator teste b"}, "ufs": {"ZZ"}},
              "40": {"nomes": {"ator teste c"}, "ufs": {"ZZ"}}}
    pares, ambiguos = equivalencias(camara, senado, [])
    assert pares == [("1", "10", "automatico_nome_uf")]
    assert sorted(ambiguos) == [("2", "20"), ("3", "20")]  # mesmo nome e UF: revisão humana
    pares, ambiguos = equivalencias(camara, senado, [{"id_camara": "3", "id_senado": "20", "decisao": "mesma_pessoa"},
                                                     {"id_camara": "2", "id_senado": "20", "decisao": "pessoas_diferentes"}])
    assert ("3", "20", "manual") in pares and ambiguos == []


def test_marcador_fora_da_legislatura_e_suplente_sem_exercicio_sao_ignorados():
    hist = [
        r("2003-02-01T12:00", "AAA"), r("2007-01-31T23:59", "AAA", "FIM_MANDATO"),
        r("2023-02-01T00:00", "AAA", None),  # marcador da API com data de outra legislatura
        r("2007-02-01T00:00", "AAA", None, leg=53), r("2007-02-05T00:00", "AAA", "SUPLENCIA", leg=53, cond="Suplente"),
    ]
    cargos, filiacoes = periodos_camara(hist, LEGS, "2026-09-24")
    assert [(c["legislatura"], c["inicio"], c["fim"]) for c in cargos] == [(52, "2003-02-01", "2007-01-31")]
    assert [(f["legislatura"], f["inicio"], f["fim"]) for f in filiacoes] == [(52, "2003-02-01", "2007-01-31")]
