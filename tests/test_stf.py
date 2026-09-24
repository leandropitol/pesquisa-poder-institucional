"""Regra de assuntos e de fases do STF (etapa E5). Caminhos de assunto como os do Corte Aberta; nenhum dado de pessoa."""

from src.normalizacao.stf import numero_cnj, regra_caminho

TPU = {"PECULATO": ("inclui", "CP art. 312"), "CRIMES DE RESPONSABILIDADE": ("exclui", "DL 201/1967"),
       "CALUNIA": ("exclui", "fora"), "CRIMES CONTRA A HONRA": ("exclui", "fora"), "FALSIDADE IDEOLOGICA": ("conexo", "CP art. 299"),
       "CRIMES DA LEI DE LICITACOES": ("inclui", "Lei 8.666/1993")}


def d(caminho):
    return regra_caminho(caminho, TPU)[0]


def test_titulo_xi_entra_inteiro_por_capitulo():
    assert d("DIREITO PENAL | CRIMES PRATICADOS POR PARTICULAR CONTRA A ADMINISTRAÇÃO EM GERAL | DESACATO") == "inclui"
    assert d("DIREITO PENAL | CRIMES CONTRA A ADMINISTRAÇÃO DA JUSTIÇA | COAÇÃO NO CURSO DO PROCESSO") == "inclui"
    assert d("DIREITO PENAL | CRIMES PRATICADOS POR FUNCIONÁRIOS PÚBLICOS CONTRA A ADMINISTRAÇÃO EM GERAL") == "inclui"


def test_nome_da_tabela_do_stj_herda_decisao():
    assert d("DIREITO PENAL | CRIMES PREVISTOS NA LEGISLAÇÃO EXTRAVAGANTE | CRIMES DA LEI DE LICITAÇÕES") == "inclui"
    assert d("DIREITO PENAL | CRIMES PREVISTOS NA LEGISLAÇÃO EXTRAVAGANTE | CRIMES DE RESPONSABILIDADE") == "exclui"
    assert d("DIREITO PENAL | CRIMES CONTRA A FÉ PÚBLICA | FALSIDADE IDEOLÓGICA") == "conexo"


def test_eleitoral_so_art_350_como_conexo():
    assert d("DIREITO PENAL | CRIMES PREVISTOS NA LEGISLAÇÃO EXTRAVAGANTE | CRIMES ELEITORAIS") == "conexo"
    assert d("DIREITO ELEITORAL | CRIMES ELEITORAIS | CRIMES CONTRA A FÉ PÚBLICA ELEITORAL |FALSIDADE IDEOLÓGICA") == "conexo"
    assert d("DIREITO PENAL | CRIMES PREVISTOS NA LEGISLAÇÃO EXTRAVAGANTE | CRIMES ELEITORAIS | CALÚNIA") == "exclui"


def test_generico_e_administrativo_ficam_indeterminados():
    assert d("DIREITO PROCESSUAL PENAL | AÇÃO PENAL") == "indeterminado"
    assert d("*NI*") == "indeterminado"
    assert d("DIREITO PENAL | CRIMES PREVISTOS NA LEGISLAÇÃO EXTRAVAGANTE") == "indeterminado"
    assert d("DIREITO ADMINISTRATIVO E OUTRAS MATÉRIAS DE DIREITO PÚBLICO | LICITAÇÕES") == "indeterminado"


def test_categoria_excluida_e_residual():
    assert d("DIREITO PENAL | CRIMES CONTRA A HONRA | DIFAMAÇÃO") == "exclui"
    assert d("DIREITO PENAL | LESÃO CORPORAL") == "exclui"


def test_numero_cnj():
    assert numero_cnj("99326980620111000000") == "9932698-06.2011.1.00.0000"
    assert numero_cnj("123") == ""
