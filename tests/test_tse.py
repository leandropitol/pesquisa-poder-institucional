"""Leitura de valores, tipo de doador e ligação por nome (TSE, etapa E7). Registros fictícios."""

from src.normalizacao.tse import palavras, tipo_doador, valor


def test_valor_em_varios_formatos():
    assert valor("145000") == 145000.0
    assert valor("1.234,56") == 1234.56
    assert valor("1234,5") == 1234.5
    assert valor("#NULO") == 0.0
    assert valor(float("nan")) == 0.0
    assert valor(None) == 0.0


def r(tipo="", fonte="", doc="", nome_doador="", nome_cand=""):
    return {"tipo": tipo, "fonte": fonte, "doc": doc, "nome_doador": nome_doador, "nome_cand": nome_cand}


def test_tipo_de_doador_pelo_texto():
    assert tipo_doador(r("Recursos de pessoas jurídicas")) == "pessoa_juridica"
    assert tipo_doador(r("RECURSOS DE OUTROS CANDIDATOS/COMITÊS")) == "partido"
    assert tipo_doador(r("Recursos próprios")) == "recursos_proprios"
    assert tipo_doador(r("Doações pela Internet")) == "pessoa_fisica_agregado"
    assert tipo_doador(r("Recursos de partido político", "FUNDO ESPECIAL")) == "fundo_publico"


def test_tipo_de_doador_em_2002_pelo_documento_e_nome():
    assert tipo_doador(r(doc="12345678000199", nome_doador="CONSTRUTORA FICTICIA LTDA")) == "pessoa_juridica"
    assert tipo_doador(r(doc="12345678000199", nome_doador="COMITÊ FINANCEIRO ÚNICO XYZ")) == "partido"
    assert tipo_doador(r(doc="12345678901", nome_doador="FULANO DE TAL")) == "pessoa_fisica_agregado"
    assert tipo_doador(r(doc="12345678901", nome_doador="CANDIDATO TESTE", nome_cand="Candidato Teste")) == "recursos_proprios"


def test_palavras_tira_titulos_e_preposicoes():
    assert palavras("Dr. João da Silva") == {"joao", "silva"}
    assert palavras("Coronel Alves") == {"alves"}  # uma palavra só: não basta para ligar (D-043)
