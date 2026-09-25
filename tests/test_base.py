"""Registro de identificadores: dois processos gravando no mesmo arquivo não perdem ids."""

from src.base import RegistroIds


def test_salvar_mescla_com_o_arquivo(tmp_path):
    caminho, base = tmp_path / "ids.csv", tmp_path
    a = RegistroIds(caminho, base)
    b = RegistroIds(caminho, base)  # lido antes de `a` gravar
    a.vincular("fontes", "raw:x", "FNT-000001")
    a.salvar()
    b.vincular("fontes", "raw:y", "FNT-000002")
    b.salvar()
    c = RegistroIds(caminho, base)
    assert c.mapa[("fontes", "raw:x")] == "FNT-000001"
    assert c.mapa[("fontes", "raw:y")] == "FNT-000002"


def test_remover_vale_na_mescla(tmp_path):
    caminho, base = tmp_path / "ids.csv", tmp_path
    a = RegistroIds(caminho, base)
    a.vincular("buscas", "antiga", "BSC-000001")
    a.salvar()
    b = RegistroIds(caminho, base)
    b.remover("buscas", "antiga")
    b.vincular("buscas", "nova", "BSC-000001")
    b.salvar()
    c = RegistroIds(caminho, base)
    assert ("buscas", "antiga") not in c.mapa
    assert c.mapa[("buscas", "nova")] == "BSC-000001"
