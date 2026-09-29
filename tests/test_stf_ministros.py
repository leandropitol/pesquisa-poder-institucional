"""Testes da composição do STF (D-058). Textos no formato das páginas "Dados e Datas" da Biblioteca do STF, com nomes fictícios."""

from src.coleta.stf_ministros import nome_arquivo
from src.normalizacao.stf_ministros import data_pagina, iso, ler_dados_datas, slug, texto_html, vaga

PAGINA = """Fulano Tal - Dados e Datas
Última atualização:
2026-01-02
INDICAÇÃO PARA O SUPREMO TRIBUNAL FEDERAL
APRECIAÇÃO DA INDICAÇÃO DO PRESIDENTE DA REPÚBLICA PELO SENADO FEDERAL
NOMEAÇÃO PARA O SUPREMO TRIBUNAL FEDERAL
POSSE NO SUPREMO TRIBUNAL FEDERAL
APOSENTAORIA DO SUPREMO TRIBUNAL FEDERAL
INDICAÇÃO PARA O SUPREMO TRIBUNAL FEDERAL
1. BRASIL. Presidência da República. Mensagem nº 12, de 3 de maio de 2010. Encaminha o nome de Fulano Tal na vaga decorrente da aposentadoria do Ministro Beltrano Silva. DOU.
APRECIAÇÃO DA INDICAÇÃO DO PRESIDENTE DA REPÚBLICA PELO SENADO FEDERAL
2. BRASIL. Congresso. Senado. Mensagem nº 4, de 2010. Submete o nome. DSF.
NOMEAÇÃO PARA O SUPREMO TRIBUNAL FEDERAL
3. BRASIL. Decreto de 1º de junho de 2010. Nomeia Fulano Tal, na vaga decorrente da aposentadoria de Beltrano Silva. DOU.
POSSE NO SUPREMO TRIBUNAL FEDERAL
4. BRASIL. Supremo Tribunal Federal. Termo de Posse [em 20 de junho de 2010]. Livro.
APOSENTAORIA DO SUPREMO TRIBUNAL FEDERAL
5. BRASIL. Decreto de 7 de maio de 2020. Concede aposentadoria, a partir do dia 8 de maio de 2020, a Fulano Tal. DOU.
"""


def test_slug_e_iso():
    assert slug("Celso de Mello") == "CelsoMello" and slug("Luís Roberto Barroso") == "LuisRobertoBarroso"
    assert iso("em 1º de junho de 2010") == "2010-06-01" and iso("sem data") == ""


def test_vaga():
    assert vaga("em vaga decorrente da exoneração, a pedido, do Ministro Fulano Tal.") == ("exoneração", "Fulano Tal")
    assert vaga("na vaga decorrente da aposentadoria voluntária do Ministro Beltrano Silva]. DOU") == ("aposentadoria", "Beltrano Silva")
    assert vaga("[...] na vaga decorrente do falecimento do Ministro Sicrano Souza, DOU") == ("falecimento", "Sicrano Souza")


def test_ler_dados_datas():
    d = ler_dados_datas(PAGINA)
    assert (d["mensagem_numero"], d["data_mensagem"], d["data_decreto_nomeacao"], d["data_posse"], d["data_aposentadoria"]) == (
        "12", "2010-05-03", "2010-06-01", "2010-06-20", "2020-05-08")
    assert (d["vaga_motivo"], d["vaga_de"], d["vaga_no_decreto"]) == ("aposentadoria", "Beltrano Silva", "Beltrano Silva")


def test_texto_html_e_data_pagina():
    html = "<html><script>x=1</script><div>Título</div><p>Última atualização:</p><p>2026-01-02</p></html>".encode("utf-8")
    assert texto_html(html) == "Título\nÚltima atualização:\n2026-01-02"
    assert data_pagina(html, "2026-09-29")[0] == "2026-01-02"
    assert data_pagina("<p>27/02/2024 16h50 - Atualizado</p>".encode("utf-8"), "2026-09-29")[0] == "2024-02-27"
    assert data_pagina(b"<p>sem data</p>", "2026-09-29") == ("2026-09-29", "página sem data de publicação; registrada a data de acesso")


def test_nome_arquivo():
    b = "https://portal.stf.jus.br/"
    assert nome_arquivo(b + "ostf/ministros/detalhamentos.asp?detalhamento=INDICACOES&entidade=41") == "indicacoes_presidente_41.json"
    assert nome_arquivo(b + "textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina=RosaWeberDadosDatas") == "dados_datas_RosaWeber.html"
    assert nome_arquivo(b + "ostf/ministros/verMinistro.asp?periodo=STF&id=47") == "biografia_47.html"
    assert nome_arquivo(b + "noticias/verNoticiaDetalhe.asp?idConteudo=528119&ori=1") == "noticia_stf_528119.html"
