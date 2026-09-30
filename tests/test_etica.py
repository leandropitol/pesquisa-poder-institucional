"""Testes dos Conselhos de Ética (D-063)."""

from src.normalizacao.etica import chaves_do_nome, desfecho_camara, desfecho_senado, subsequencia, trecho_alvo


def test_chaves_do_nome_sem_titulo_e_sufixo():
    assert chaves_do_nome("Dr. Rosinha") == {"dr rosinha"}  # o nome sem título teria uma palavra só
    assert {"professor irapuan teixeira", "irapuan teixeira"} <= chaves_do_nome("Professor Irapuan Teixeira")
    assert "jose vieira" in chaves_do_nome("José Vieira Junior")
    assert chaves_do_nome("Lula") == set()  # uma palavra só não serve de chave


def test_trecho_alvo_ignora_quem_representa():
    e = "Representação do PSOL contra o Deputado Fulano de Tal"
    assert "psol" not in trecho_alvo(e).lower() and "Fulano" in trecho_alvo(e)
    assert trecho_alvo("Sem marcador Fulano") == "Sem marcador Fulano"


def test_subsequencia_ordem_e_janela():
    texto = "paulo roberto galvao da rocha".split()
    assert subsequencia(["paulo", "rocha"], texto)
    assert not subsequencia(["rocha", "paulo"], texto)
    assert not subsequencia(["paulo", "pereira"], "paulo pereira da silva roberto".split()[:1] + ["silva"])
    assert not subsequencia(["paulo"], texto)


def ev(data, despacho, orgao="PLEN", seq=1):
    return {"dataHora": data + "T10:00", "despacho": despacho, "siglaOrgao": orgao, "sequencia": seq}


def test_desfecho_camara_cassacao_prevalece_sobre_arquivo_posterior():
    eventos = [ev("2005-09-14", "Promulgada a Resolução nº 33, de 2005, que declara a perda de mandato do Dep. X."),
               ev("2005-10-01", "Arquivado.", "MESA")]
    r = desfecho_camara(eventos, None)
    assert r["status"] == "mandato_cassado" and r["data"] == "2005-09-14"


def test_desfecho_camara_parecer_rejeitado_e_improcedente():
    r = desfecho_camara([ev("2012-05-01", "Rejeitado o Parecer do Conselho de Ética e Decoro Parlamentar pela cassação do mandato.")], None)
    assert r["status"] == "representacao_improcedente"


def test_desfecho_camara_sem_evento_decisivo():
    assert desfecho_camara([ev("2020-01-01", "Recebimento do Requerimento", "MESA")], "Em tramitação") is None


def test_desfecho_camara_arquivamento_pela_situacao():
    r = desfecho_camara([ev("2020-01-01", "Despacho qualquer", "MESA")], "Arquivada")
    assert r["status"] == "arquivado"


def test_desfecho_senado_estruturado():
    base = {"prs": None, "deliberacao": {}, "situacao": "", "data_situacao": ""}
    aprovado = dict(base, prs={"identificacao": "PRS 1/2000", "deliberacao": {"siglaTipo": "APROVADA_NO_PLENARIO", "data": "2000-06-28", "tipoDeliberacao": "Aprovada"}})
    assert desfecho_senado(aprovado)["status"] == "mandato_cassado"
    rejeitado = dict(base, prs={"identificacao": "PRS 2/2000", "deliberacao": {"siglaTipo": "REJEITADO_PLENARIO", "data": "2000-06-28", "tipoDeliberacao": "Rejeitado"}})
    assert desfecho_senado(rejeitado)["status"] == "representacao_improcedente"
    indeferida = dict(base, deliberacao={"tipoDeliberacao": "Indeferida pelo Conselho de Ética", "data": "2010-01-01"})
    assert desfecho_senado(indeferida)["status"] == "arquivado"
    assert desfecho_senado(base) is None
