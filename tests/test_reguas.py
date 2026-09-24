"""Réguas externas: classificação do protocolo e ligação de nomes de país. Dados fictícios."""

import pandas as pd

from src.normalizacao import reguas
from src.normalizacao.reguas import classificar, codigos_fh


def test_classificacao_do_protocolo():
    assert [classificar("vdem_row", v) for v in "0123"] == ["baixa", "baixa", "intermediaria", "alta"]
    assert [classificar("fh_status", v) for v in ("NF", "PF", "F")] == ["baixa", "intermediaria", "alta"]
    assert classificar("vdem_ldi", "0.5") is None and classificar("fh_total", "50") is None


def test_ligacao_de_nomes_por_nome_normalizado_e_curadoria(tmp_path, monkeypatch):
    (tmp_path / "paises_freedom_house.csv").write_text(
        "nome_freedom_house,pais_iso3,justificativa\nPais Grafia Diferente,PGD,teste\nPais Extinto,,fora do período\n", encoding="utf-8")
    monkeypatch.setattr(reguas, "CURADORIA", tmp_path)
    vdem = pd.DataFrame({"country_name": ["País Um", "Outro Nome"], "country_text_id": ["PUM", "PGD"]})
    mapa, faltam = codigos_fh({"Pais Um", "Pais Grafia Diferente", "Pais Extinto", "Pais Novo"}, vdem)
    assert mapa == {"Pais Um": "PUM", "Pais Grafia Diferente": "PGD"}
    assert faltam == ["Pais Novo"]
