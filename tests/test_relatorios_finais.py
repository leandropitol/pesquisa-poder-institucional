"""Testes do fechamento: formatação, regras de citação e de pessoas no relatório final e na linha do tempo."""

import re

import pandas as pd
import pytest

from src.base import RAIZ
from src.relatorios import linha_do_tempo, relatorio_final
from src.relatorios.util import Fontes, dec, milhar, pct, pv

CPF_FORMATADO = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
ONZE_DIGITOS = re.compile(r"(?<![\w=])\d{11}(?![\w])")


def cpfs_reais() -> set:
    arq = RAIZ / "data" / "staging" / "eixo1" / "candidatos.csv"
    if not arq.exists():
        pytest.skip("arquivo de trabalho com CPF (fora do Git) ausente")
    return set(pd.read_csv(arq, usecols=["cpf"], dtype=str)["cpf"].dropna())


def sem_cpf(texto: str) -> bool:
    if CPF_FORMATADO.search(texto):
        return False
    return not (set(ONZE_DIGITOS.findall(texto)) & cpfs_reais())


def test_formatacao_em_portugues():
    assert milhar(1234567) == "1.234.567"
    assert dec(0.5) == "0,50"
    assert pct(0.1234) == "12,3%"
    assert pv(0.0004) == "p < 0,001"
    assert pv(0.0456) == "p = 0,046"


def test_datajud_nunca_e_citado():
    f = Fontes()
    assert not f.f["licenca"].str.contains("DataJud", case=False).any()
    assert not f.f["titulo"].str.contains("DataJud", case=False).any()


def test_relatorio_final_sem_lixo_sem_cpf_e_com_fonte_em_cada_secao():
    texto = relatorio_final.montar()
    corpo = texto.split("## Apêndice A")[0]
    assert not re.search(r"\bnan\b|\binf\b", corpo, flags=re.I)
    assert sem_cpf(texto)
    assert "DataJud" not in texto
    assert "## 7. Interpretação (separada dos resultados)" in texto
    secoes = re.split(r"\n## ", corpo)
    assert len(secoes) >= 9
    for sec in secoes[1:7]:  # escopo, base, eixo 1, eixo 2, eixo 3 e simetria
        assert "*(Fonte:" in sec


def test_linha_do_tempo_so_status_formal_e_agente_privado_acima_de_reu():
    m = linha_do_tempo.montar()
    privados = m[m["tipo_ator"] == "agente_privado"]
    visiveis = privados[privados["nome_no_texto"]]
    assert visiveis["status"].isin(linha_do_tempo.ACIMA_DE_REU).all()
    assert (privados[~privados["nome_no_texto"]]["nome"] == "").all()
    assert sem_cpf(" ".join(m["frase"]))
    assert m["id_fonte"].notna().all()
