"""Testes do contraste com a imprensa (D-055, D-056). Veículos e títulos fictícios."""

import pandas as pd

from src.analise.imprensa import conferir, titulo_confere

FATOS = pd.DataFrame({"id_fato": ["X1"]})
VEIC = pd.DataFrame({"veiculo": ["Alfa", "Beta", "Gama"], "papel": ["principal", "principal", "reserva"],
                     "situacao_acesso": ["ok", "sem_acesso", "ok"]})
LINKS = [{"title": "Tribunal adia julgamento - Alfa", "url": "u1"}, {"title": "Tribunal condena  Fulano \n por peculato - Alfa", "url": "u2"}]
BUS = pd.DataFrame([{"fato": "X1", "veiculo": "Alfa", "acesso": "ok", "links": LINKS},
                    {"fato": "X1", "veiculo": "Gama", "acesso": "ok", "links": []},
                    {"fato": "X1", "veiculo": "Beta", "acesso": "sem_acesso", "links": []}])


def cont(*linhas):
    return pd.DataFrame(linhas, columns=["id_fato", "veiculo", "resultado", "posicao", "titulo"])


def test_titulo_confere():
    assert titulo_confere("Tribunal condena Fulano por peculato", LINKS[1]["title"])
    assert titulo_confere("Tribunal condena Fulano ...", LINKS[1]["title"])
    assert not titulo_confere("Tribunal absolve Fulano", LINKS[1]["title"])


def test_classificacao_completa_passa():
    c = cont(("X1", "Alfa", "concorda", "2", "Tribunal condena Fulano por peculato"), ("X1", "Gama", "sem_resultado", "", ""))
    assert conferir(FATOS, VEIC, c, BUS) == []


def test_falhas_detectadas():
    c = cont(("X1", "Alfa", "concorda", "1", "Tribunal condena Fulano por peculato"),
             ("X1", "Beta", "sem_resultado", "", ""),
             ("X1", "Gama", "sem_resultado", "1", ""))
    erros = conferir(FATOS, VEIC, c, BUS)
    assert any("Alfa: título não confere" in e for e in erros)
    assert any("Beta: veículo fora de uso" in e for e in erros)
    assert any("Gama: posição indevida" in e for e in erros)


def test_linha_faltando_e_resultado_invalido():
    c = cont(("X1", "Alfa", "talvez", "", ""))
    erros = conferir(FATOS, VEIC, c, BUS)
    assert any("Gama: 0 linhas" in e for e in erros)
    assert any("resultado inválido" in e for e in erros)
