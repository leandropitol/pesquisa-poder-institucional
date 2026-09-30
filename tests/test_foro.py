"""Testes do estudo do foro (D-068): hierarquia do desfecho, Kaplan-Meier e incidência acumulada."""

import numpy as np
import pandas as pd

from src.analise.foro import CORTE, classificar, incidencia, mediana_km


def dec(linhas, tramita="Não", baixa="10/05/2015 10:00:00"):
    return pd.DataFrame([{"data": d, "Andamento decisão": a, "Indicador de tramitação": tramita, "Data baixa": baixa} for d, a in linhas])


def test_merito_prevalece_sobre_extincao_e_declinio():
    x = dec([("2010-01-01", "Declarada a extinção da punibilidade"), ("2011-01-01", "Procedente"), ("2012-01-01", "Declinada a competência")])
    assert classificar(x) == ("merito", "2011-01-01")


def test_declinio_prevalece_sobre_tramitacao():
    x = dec([("2010-01-01", "Declinada a competência")], tramita="Sim", baixa="*NI*")
    assert classificar(x) == ("declinio", "2010-01-01")


def test_extincao_parcial_em_acao_que_tramita_nao_e_final():
    x = dec([("2010-01-01", "Declarada a extinção da punibilidade")], tramita="Sim", baixa="*NI*")
    assert classificar(x) == ("em_tramitacao", CORTE)


def test_outro_encerramento_usa_a_baixa():
    x = dec([("2010-01-01", "DECISÃO DO RELATOR")])
    assert classificar(x) == ("outro", "2015-05-10")


def test_kaplan_meier_e_incidencia():
    t = np.array([1.0, 2.0, 3.0, 4.0])
    e = np.array([1, 1, 1, 1])
    assert mediana_km(t, e) == 2.0
    causa = np.array(["merito", "declinio", "merito", "declinio"])
    total = incidencia(t, causa, "merito", 10) + incidencia(t, causa, "declinio", 10)
    assert abs(total - 1.0) < 1e-9  # sem censura, as incidências somam 1
    assert abs(incidencia(t, causa, "merito", 1.5) - 0.25) < 1e-9
    # censura: a quarta ação sai do risco sem evento
    assert abs(incidencia(t, np.array(["merito", "declinio", "merito", ""]), "merito", 10) - 0.5) < 1e-9
