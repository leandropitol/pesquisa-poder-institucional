"""Portal da Transparência: formatos da CGU, CNPJ e ligação de autor de emenda. Dados fictícios."""

import pandas as pd
import pytest

from src.base import RegistroIds, cnpj_digitos, id_empresa
from src.normalizacao.transparencia import chave_nome, data_br, parlamentar_por_nome, valor_br


def test_formatos_da_cgu():
    assert data_br("14/08/2017") == "2017-08-14" and data_br("") == "" and data_br("31/02/2020") == ""
    assert valor_br("1.234.567,89") == "1234567.89" and valor_br("") == ""
    with pytest.raises(ValueError):
        valor_br("n/d")


def test_cnpj_formatado_e_so_digitos_viram_a_mesma_empresa(tmp_path):
    ids = RegistroIds(caminho=tmp_path / "ids.csv", base=tmp_path)
    antigo = ids.obter("instituicoes", "cnpj:11.222.333/0001-81")  # chave antiga, com máscara
    assert id_empresa(ids, "11222333000181") == antigo
    assert id_empresa(ids, "11.222.333/0001-81") == antigo
    assert id_empresa(ids, "EXEMPRESA") != antigo  # identificador estrangeiro fica separado
    assert cnpj_digitos("11.222.333/0001-81") == "11222333000181"


def test_autor_de_emenda_ligado_por_nome_e_mandato():
    atores = pd.DataFrame({"id_ator": ["ATR-000001", "ATR-000002", "ATR-000003"],
                           "nome": ["Ator D'Teste", "Ator Duplo", "Ator Duplo"]})
    cargos = pd.DataFrame({"id_ator": ["ATR-000001", "ATR-000002", "ATR-000003"],
                           "data_inicio": ["2015-02-01", "2015-02-01", "2019-02-01"], "data_fim": ["2019-01-31", "2019-01-31", ""]})
    achar = parlamentar_por_nome(atores, cargos)
    assert chave_nome("ATOR D'TESTE") == chave_nome("Ator Dteste")
    assert achar("ATOR DTESTE", "2016") == "ATR-000001"
    assert achar("ATOR DTESTE", "2020") == ""          # sem mandato no ano
    assert achar("ATOR DUPLO", "2016") == "ATR-000002"  # homônimo desambiguado pelo mandato
    assert achar("ATOR DUPLO", "2019") == ""            # dois com mandato em 2019: não liga
