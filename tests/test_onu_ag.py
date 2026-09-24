"""Critério de seleção das resoluções da Assembleia Geral da ONU (bloco A1). Títulos fictícios."""

from src.normalizacao.onu_ag import criterio, titulo_curto


def test_criterio_direitos_humanos_de_qualquer_pais():
    assert criterio("Situation of human rights in Pais Teste : resolution / adopted by the General Assembly", "") == "direitos_humanos_pais"
    assert criterio("The human rights situation in Pais Teste", "") == "direitos_humanos_pais"


def test_criterio_america_latina_por_titulo_ou_agenda():
    assert criterio("Necessity of ending the embargo against Cuba", "") == "cita_america_latina"
    assert criterio("Some programme", "Question of the Falkland Islands (Malvinas)") == "cita_america_latina"
    assert criterio("Report on Chile", "") == "cita_america_latina"


def test_sem_criterio_e_sem_falso_positivo_por_parte_de_palavra():
    assert criterio("Oceans and the law of the sea", "") == ""
    assert criterio("Chilean-style reforms elsewhere", "") == ""  # 'Chile' só como palavra inteira


def test_titulo_curto():
    assert titulo_curto("Situation of human rights in X : resolution / adopted by the General Assembly") == "Situation of human rights in X"
