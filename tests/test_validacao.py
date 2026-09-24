"""Testes do esquema e do validador. Todas as entidades são fictícias."""

import csv
import subprocess
from pathlib import Path

import pytest

from src import estrutura
from src.esquema import POR_NOME, TABELAS
from src.validacao.validar import validar
from src.vocabularios import VOCABULARIOS


# ---------------------------------------------------------------- esquema
def test_esquema_consistente():
    prefixos = [t.prefixo for t in TABELAS if t.prefixo]
    assert len(prefixos) == len(set(prefixos))
    for t in TABELAS:
        assert set(t.chave) <= set(t.nomes), t.nome
        for c in t.colunas:
            if c.vocab:
                assert c.vocab in VOCABULARIOS, (t.nome, c.nome)
            if c.fk:
                tab, col = c.fk.split(".")
                assert tab in POR_NOME and col in POR_NOME[tab].nomes, (t.nome, c.nome)
        for tp, _ in t.polimorficas:
            assert POR_NOME[t.nome].colunas[t.nomes.index(tp)].vocab == "tipo_entidade"


def test_vocabularios_com_teto_usam_niveis_validos():
    niveis = {l["codigo"] for l in VOCABULARIOS["nivel_confianca"]}
    for linhas in VOCABULARIOS.values():
        for l in linhas:
            assert l.get("nivel_maximo", "alegado") in niveis


def test_estrutura_nao_sobrescreve_csv_existente(tmp_path):
    estrutura.criar_tabelas(tmp_path)
    alvo = tmp_path / "atores.csv"
    alvo.write_text(alvo.read_text(encoding="utf-8") + "ATR-000001,Ator Teste A,ator teste a,agente_publico,,,\n", encoding="utf-8")
    assert estrutura.criar_tabelas(tmp_path) == []
    assert "Ator Teste A" in alvo.read_text(encoding="utf-8")


# ---------------------------------------------------------------- base fictícia
def montar(pasta: Path, linhas: dict[str, list[dict]]) -> Path:
    estrutura.criar_tabelas(pasta)
    for nome, regs in linhas.items():
        cols = POR_NOME[nome].nomes
        with (pasta / f"{nome}.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            w.writerows([{c: r.get(c, "") for c in cols} for r in regs])
    return pasta


URL = "https://exemplo.invalid/doc"


def base_valida() -> dict[str, list[dict]]:
    return {
        "instituicoes": [
            {"id_instituicao": "INS-000001", "nome": "Tribunal Teste", "tipo_instituicao": "tribunal", "poder": "judiciario", "esfera": "federal", "pais_iso3": "BRA"},
            {"id_instituicao": "INS-000002", "nome": "Partido Teste A", "tipo_instituicao": "partido", "poder": "nao_se_aplica", "esfera": "federal", "pais_iso3": "BRA"},
            {"id_instituicao": "INS-000003", "nome": "Partido Teste B", "tipo_instituicao": "partido", "poder": "nao_se_aplica", "esfera": "federal", "pais_iso3": "BRA"},
        ],
        "atores": [{"id_ator": "ATR-000001", "nome": "Ator Teste A", "nome_normalizado": "ator teste a", "tipo_ator": "agente_publico"}],
        "fontes": [
            {"id_fonte": "FNT-000001", "tipo_fonte": "judicial", "titulo": "Decisão fictícia", "data_publicacao": "2010-05-03", "url": URL, "data_acesso": "2026-09-24"},
            {"id_fonte": "FNT-000002", "tipo_fonte": "oficial", "titulo": "Lista fictícia de bancadas", "data_publicacao": "2010-02-01", "url": URL, "data_acesso": "2026-09-24"},
            {"id_fonte": "FNT-000003", "tipo_fonte": "jornalistica", "titulo": "Coluna fictícia", "data_publicacao": "2010-05-04", "url": URL, "data_acesso": "2026-09-24"},
        ],
        "fonte_judicial": [{"id_fonte": "FNT-000001", "numero_processo": "AP 1", "id_orgao": "INS-000001", "data_documento": "2010-05-03",
                            "fase_processual": "recebimento_denuncia", "tipo_documento": "acórdão", "link_publico": URL}],
        "fonte_oficial": [{"id_fonte": "FNT-000002", "id_orgao": "INS-000001", "tipo_documento": "lista", "data_documento": "2010-02-01", "link": URL}],
        "fonte_jornalistica": [{"id_fonte": "FNT-000003", "veiculo": "Veículo Teste", "classe_jornalistica": "opiniao"}],
        "filiacoes": [{"id_filiacao": "FIL-000001", "id_ator": "ATR-000001", "id_partido": "INS-000002", "data_inicio": "2005", "id_fonte": "FNT-000002"}],
        "processos": [{"id_processo": "PRC-000001", "numero_originario": "AP 1", "classe": "acao_penal", "id_tribunal": "INS-000001",
                       "data_autuacao": "2009-11", "sigilo": "false", "url": URL, "id_fonte": "FNT-000001"}],
        "status_pessoa_processo": [{"id_status": "STA-000001", "id_ator": "ATR-000001", "id_processo": "PRC-000001", "data": "2010-05-03",
                                    "status": "reu", "tipificacao": "art. 317 do CP", "id_fonte": "FNT-000001"}],
        "buscas": [{"id_busca": "BSC-000001", "data": "2026-09-24", "fonte_dados": "base fictícia", "consulta": "réu, art. 317, 2010, Partido Teste B",
                    "n_resultados": "0", "script": "tests"}],
        "verificacoes_simetria": [{"id_verificacao": "VSM-000001", "achado_tabela": "status_pessoa_processo", "achado_id": "STA-000001",
                                   "padrao_buscado": "réu em ação penal originária, art. 317, 2010", "ano_referencia": "2010", "data": "2026-09-24", "script": "tests"}],
        "verificacao_resultado": [
            {"id_resultado": "VRS-000001", "id_verificacao": "VSM-000001", "grupo_tipo": "partido", "grupo_id": "INS-000002",
             "resultado": "encontrado", "n_casos": "1", "ids_encontrados": "STA-000001"},
            {"id_resultado": "VRS-000002", "id_verificacao": "VSM-000001", "grupo_tipo": "partido", "grupo_id": "INS-000003",
             "resultado": "sem_evidencia", "id_busca": "BSC-000001"},
        ],
        "universo_partidos": [
            {"ano": "2010", "id_partido": "INS-000002", "criterio": "bancada fictícia", "id_fonte": "FNT-000002"},
            {"ano": "2010", "id_partido": "INS-000003", "criterio": "bancada fictícia", "id_fonte": "FNT-000002"},
        ],
    }


def rodar(tmp_path, linhas):
    return validar(montar(tmp_path, linhas), raiz=tmp_path, historico=False)


def test_base_vazia_e_valida(tmp_path):
    assert rodar(tmp_path, {}) == ([], [])


def test_base_ficticia_valida(tmp_path):
    assert rodar(tmp_path, base_valida()) == ([], [])


def _com(**mudancas):
    b = base_valida()
    for tabela, regs in mudancas.items():
        b[tabela] = regs
    return b


def test_status_com_fonte_jornalistica_falha(tmp_path):
    b = base_valida()
    b["status_pessoa_processo"][0]["id_fonte"] = "FNT-000003"
    falhas, _ = rodar(tmp_path, b)
    assert any("exigem fonte judicial ou oficial" in f for f in falhas)


def test_formato_vocabulario_e_referencia(tmp_path):
    b = base_valida()
    b["atores"][0]["id_ator"] = "ATR-1"
    b["atores"][0]["tipo_ator"] = "politico"
    b["processos"][0]["data_autuacao"] = "2009-13"
    falhas, _ = rodar(tmp_path, b)
    texto = "\n".join(falhas)
    assert "fora do formato ATR-000001" in texto
    assert "fora do vocabulário tipo_ator" in texto
    assert "formato inválido para data" in texto
    assert "referencia atores.id_ator inexistente" in texto


def test_fonte_sem_subtabela_falha(tmp_path):
    b = base_valida()
    b["fonte_oficial"] = []
    falhas, _ = rodar(tmp_path, b)
    assert any("sem linha em fonte_oficial" in f for f in falhas)


def _afirmacao(nivel, fonte, predicado="recebeu_valor"):
    return {
        "afirmacoes": [{"id_afirmacao": "AFI-000001", "sujeito_tipo": "instituicao", "sujeito_id": "INS-000001", "predicado": predicado,
                        "objeto_tipo": "instituicao", "objeto_id": "INS-000002", "data": "2010", "eixo": "esquemas_ilicitos", "nivel_confianca": nivel}],
        "afirmacao_fonte": [{"id_afirmacao": "AFI-000001", "id_fonte": fonte}],
    }


def test_afirmacao_so_com_opiniao_falha(tmp_path):
    falhas, _ = rodar(tmp_path, _com(**_afirmacao("alegado", "FNT-000003")))
    assert any("só por jornalismo de opinião" in f for f in falhas)


def test_nivel_acima_do_que_as_fontes_sustentam(tmp_path):
    b = _com(**_afirmacao("documentado", "FNT-000003"))
    b["fonte_jornalistica"][0]["classe_jornalistica"] = "investigativa"
    falhas, _ = rodar(tmp_path, b)
    assert any("só sustentam alegado" in f for f in falhas)


def test_teto_do_vocabulario(tmp_path):
    falhas, _ = rodar(tmp_path, _com(**_afirmacao("documentado", "FNT-000001", predicado="declarou")))
    assert any("tem teto alegado" in f for f in falhas)


def test_afirmacao_sem_fonte_falha(tmp_path):
    b = _com(**_afirmacao("documentado", "FNT-000001"))
    b["afirmacao_fonte"] = []
    falhas, _ = rodar(tmp_path, b)
    assert any("sem fonte ligada" in f for f in falhas)


def test_sem_evidencia_exige_busca_com_zero(tmp_path):
    b = base_valida()
    b["buscas"][0]["n_resultados"] = "3"
    falhas, _ = rodar(tmp_path, b)
    assert any("'sem_evidencia' exige busca" in f for f in falhas)


def test_universo_de_partidos_incompleto(tmp_path):
    b = base_valida()
    b["verificacao_resultado"][1].update({"grupo_tipo": "oposicao", "grupo_id": "oposicao"})
    falhas, _ = rodar(tmp_path, b)
    assert any("não cobre 1 partido" in f for f in falhas)


def test_achado_sem_verificacao_vira_aviso(tmp_path):
    b = base_valida()
    b["verificacoes_simetria"], b["verificacao_resultado"] = [], []
    falhas, avisos = rodar(tmp_path, b)
    assert falhas == []
    assert any("não tem verificação de simetria" in a for a in avisos)


def test_nao_verificado_exige_justificativa(tmp_path):
    b = base_valida()
    b["verificacao_resultado"][1].update({"resultado": "nao_verificado", "id_busca": ""})
    falhas, _ = rodar(tmp_path, b)
    assert any("exige justificativa" in f for f in falhas)


def test_precisao_do_evento(tmp_path):
    b = _com(
        eventos=[{"id_evento": "EVT-000001", "data": "2010-05", "precisao_data": "dia", "tipo_evento": "decisao_judicial", "eixo": "esquemas_ilicitos",
                  "descricao": "Decisão fictícia", "pais_iso3": "BRA", "nivel_confianca": "documentado"}],
        evento_fonte=[{"id_evento": "EVT-000001", "id_fonte": "FNT-000001"}],
    )
    falhas, _ = rodar(tmp_path, b)
    assert any("incompatível com a precisão dia" in f for f in falhas)


def test_indice_democracia_invalido(tmp_path):
    b = _com(qualidade_democratica=[{"pais_iso3": "XXA", "ano": "2010", "indice": "fh_status", "valor": "livre", "id_fonte": "FNT-000002"}])
    falhas, _ = rodar(tmp_path, b)
    assert any("inválido para fh_status" in f for f in falhas)


def test_historico_so_cresce(tmp_path):
    base = montar(tmp_path / "data" / "base", base_valida())
    git = ["git", "-c", "user.name=teste", "-c", "user.email=teste@exemplo.invalid"]
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(git + ["add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(git + ["commit", "-q", "-m", "base"], cwd=tmp_path, check=True)
    assert validar(base, raiz=tmp_path)[0] == []
    b = base_valida()
    b["status_pessoa_processo"][0]["status"] = "absolvido"  # alterar em vez de acrescentar linha
    montar(base, b)
    falhas, _ = validar(base, raiz=tmp_path)
    assert any("status_pessoa_processo: 1 linha(s)" in f for f in falhas)
