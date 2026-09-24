"""Validador da base (data/base/*.csv) contra o esquema e as regras do CLAUDE.md.

Falhas (código de saída 1):
  - estrutura: tabela ausente ou cabeçalho diferente do esquema;
  - chave duplicada ou vazia, identificador fora do formato PREFIXO-000001;
  - campo obrigatório vazio, tipo inválido, valor fora do vocabulário, referência inexistente;
  - datas: formato, início depois do fim, precisão do evento incompatível com a data;
  - fontes: fonte sem linha na tabela do seu tipo (ou em tabela de outro tipo); evento, relação ou
    afirmação sem fonte ligada;
  - status e fases processuais sustentados por fonte que não seja judicial ou oficial;
  - nível de confiança acima do que as fontes ligadas permitem, ou acima do teto do vocabulário;
  - verificação de simetria com menos de dois grupos, "sem evidência" sem busca de zero resultados,
    "encontrado" sem casos, "não verificado" sem justificativa, ou universo de partidos incompleto;
  - tabelas de histórico (só crescem) com linha apagada ou alterada em relação ao último commit.

Avisos (não bloqueiam a base, bloqueiam relatório):
  - achado com ator filiado sem verificação de simetria;
  - ano sem universo de partidos definido;
  - evento anterior a 2003 (fora do período, só contexto).

Uso:
    python -m src.validacao.validar [--base data/base]
"""

import argparse
import io
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

from src.esquema import POR_NOME, SUBTABELA_DA_FONTE, TABELA_DA_ENTIDADE, TABELAS
from src.vocabularios import NIVEIS, codigos, teto

RAIZ = Path(__file__).resolve().parents[2]
BASE = RAIZ / "data" / "base"
ANO_INICIAL = 2003

RE_DATA = re.compile(r"^\d{4}(-(0[1-9]|1[0-2])(-(0[1-9]|[12]\d|3[01]))?)?$")
FORMATOS = {
    "data": RE_DATA,
    "ano": re.compile(r"^\d{4}$"),
    "iso3": re.compile(r"^[A-Z]{3}$"),
    "inteiro": re.compile(r"^-?\d+$"),
    "decimal": re.compile(r"^-?\d+(\.\d+)?$"),
    "bool": re.compile(r"^(true|false)$"),
    "url": re.compile(r"^https?://\S+$"),
    "sha256": re.compile(r"^[0-9a-f]{64}$"),
    "lista": re.compile(r"^[^;\s]+(;[^;\s]+)*$"),
}
PRECISAO = {"ano": 4, "mes": 7, "dia": 10}
FONTES_FORTES = {"judicial", "legislativa", "orcamentaria", "oficial", "base_de_dados"}
FONTES_PROCESSUAIS = {"judicial", "oficial"}
STATUS_COM_SIMETRIA = {
    "denunciado", "reu", "condenado_1a_instancia", "condenado_2a_instancia",
    "condenado_tribunal_superior", "condenado_transito_em_julgado",
}
VALORES_INDICE = {
    "vdem_row": lambda v: v in {"0", "1", "2", "3"},
    "vdem_ldi": lambda v: bool(FORMATOS["decimal"].match(v)) and 0 <= float(v) <= 1,
    "fh_status": lambda v: v in {"F", "PF", "NF"},
    "fh_total": lambda v: bool(FORMATOS["inteiro"].match(v)) and 0 <= int(v) <= 100,
}


def carregar(base: Path = BASE) -> tuple[dict[str, pd.DataFrame], list[str]]:
    dados, falhas = {}, []
    for t in TABELAS:
        caminho = base / f"{t.nome}.csv"
        if not caminho.exists():
            falhas.append(f"{t.nome}: arquivo ausente")
            dados[t.nome] = pd.DataFrame(columns=t.nomes, dtype=str)
            continue
        df = pd.read_csv(caminho, dtype=str, keep_default_na=False, encoding="utf-8")
        if list(df.columns) != t.nomes:
            falhas.append(f"{t.nome}: cabeçalho difere do esquema")
        dados[t.nome] = df
    return dados, falhas


def _linha(t: str, i: int) -> str:
    return f"{t} (linha {i + 2})"


def checar_colunas(dados: dict[str, pd.DataFrame]) -> list[str]:
    falhas = []
    for t in TABELAS:
        df = dados[t.nome]
        if df.empty or list(df.columns) != t.nomes:
            continue
        chave = df[list(t.chave)]
        if (chave == "").any(axis=None):
            falhas.append(f"{t.nome}: chave vazia")
        for i in df.index[chave.duplicated(keep=False)]:
            falhas.append(f"{_linha(t.nome, i)}: chave duplicada {tuple(chave.loc[i])}")
        if t.prefixo:
            padrao = re.compile(rf"^{t.prefixo}-\d{{6}}$")
            for i, v in df[t.chave[0]].items():
                if v and not padrao.match(v):
                    falhas.append(f"{_linha(t.nome, i)}: identificador fora do formato {t.prefixo}-000001: {v}")
        for c in t.colunas:
            serie = df[c.nome]
            for i, v in serie.items():
                if v == "":
                    if c.obrigatoria:
                        falhas.append(f"{_linha(t.nome, i)}: {c.nome} obrigatório vazio")
                    continue
                if c.tipo in FORMATOS and not FORMATOS[c.tipo].match(v):
                    falhas.append(f"{_linha(t.nome, i)}: {c.nome} com formato inválido para {c.tipo}: {v!r}")
                if c.vocab and v not in codigos(c.vocab):
                    falhas.append(f"{_linha(t.nome, i)}: {c.nome} fora do vocabulário {c.vocab}: {v!r}")
            if c.fk:
                tab, col = c.fk.split(".")
                existentes = set(dados[tab][col]) if col in dados[tab] else set()
                for i, v in serie.items():
                    if v and v not in existentes:
                        falhas.append(f"{_linha(t.nome, i)}: {c.nome} referencia {c.fk} inexistente: {v}")
        for col_tipo, col_id in t.polimorficas:
            for i, (tipo, ident) in df[[col_tipo, col_id]].iterrows():
                destino = TABELA_DA_ENTIDADE.get(tipo)
                if destino and ident not in set(dados[destino][POR_NOME[destino].chave[0]]):
                    falhas.append(f"{_linha(t.nome, i)}: {col_id} não existe em {destino}: {ident}")
    return falhas


def checar_datas(dados: dict[str, pd.DataFrame]) -> tuple[list[str], list[str]]:
    falhas, avisos = [], []
    for t in TABELAS:
        df = dados[t.nome]
        pares = [(a, a.replace("inicio", "fim")) for a in t.nomes if a.endswith("_inicio") and a.replace("inicio", "fim") in t.nomes]
        for ini, fim in pares:
            for i, (a, b) in df[[ini, fim]].iterrows():
                if a and b and RE_DATA.match(a) and RE_DATA.match(b) and a[: min(len(a), len(b))] > b[: min(len(a), len(b))]:
                    falhas.append(f"{_linha(t.nome, i)}: {ini} ({a}) depois de {fim} ({b})")
    ev = dados["eventos"]
    for i, (d, p) in ev[["data", "precisao_data"]].iterrows():
        if p in PRECISAO and d and len(d) != PRECISAO[p]:
            falhas.append(f"{_linha('eventos', i)}: data {d} incompatível com a precisão {p}")
        if d[:4].isdigit() and int(d[:4]) < ANO_INICIAL:
            avisos.append(f"{_linha('eventos', i)}: anterior a {ANO_INICIAL} (contexto, fora do período)")
    return falhas, avisos


def tipos_de_fonte(dados: dict[str, pd.DataFrame]) -> dict[str, str]:
    return dict(zip(dados["fontes"]["id_fonte"], dados["fontes"]["tipo_fonte"]))


def checar_fontes(dados: dict[str, pd.DataFrame]) -> list[str]:
    falhas = []
    tipo = tipos_de_fonte(dados)
    for sub in SUBTABELA_DA_FONTE.values():
        for i, f in dados[sub]["id_fonte"].items():
            if f in tipo and SUBTABELA_DA_FONTE.get(tipo[f]) != sub:
                falhas.append(f"{_linha(sub, i)}: fonte {f} é do tipo {tipo[f]}, não pertence a {sub}")
    for f, tp in tipo.items():
        sub = SUBTABELA_DA_FONTE.get(tp)
        if sub and f not in set(dados[sub]["id_fonte"]):
            falhas.append(f"fontes: {f} ({tp}) sem linha em {sub}")
    for tab in ("fases_processo", "status_pessoa_processo"):
        for i, f in dados[tab]["id_fonte"].items():
            if f in tipo and tipo[f] not in FONTES_PROCESSUAIS:
                falhas.append(f"{_linha(tab, i)}: fonte {f} é {tipo[f]}; status e fases exigem fonte judicial ou oficial")
    return falhas


def fontes_ligadas(dados: dict[str, pd.DataFrame], tabela: str) -> dict[str, list[str]]:
    ligacao, col = {"eventos": ("evento_fonte", "id_evento"), "relacoes": ("relacao_fonte", "id_relacao"), "afirmacoes": ("afirmacao_fonte", "id_afirmacao")}[tabela]
    saida: dict[str, list[str]] = {}
    for reg, f in dados[ligacao][[col, "id_fonte"]].itertuples(index=False):
        saida.setdefault(reg, []).append(f)
    return saida


def nivel_permitido(tipos: set[str], classes_jornalisticas: set[str]) -> str | None:
    """Maior nível de confiança que um conjunto de fontes sustenta (None: não sustenta fato)."""
    if tipos & FONTES_FORTES:
        return "documentado"
    if tipos & FONTES_PROCESSUAIS:
        return "sob_investigacao"
    if tipos == {"jornalistica"} and classes_jornalisticas <= {"opiniao"}:
        return None
    return "alegado"


def checar_confianca(dados: dict[str, pd.DataFrame]) -> list[str]:
    falhas = []
    tipo = tipos_de_fonte(dados)
    classe = dict(zip(dados["fonte_jornalistica"]["id_fonte"], dados["fonte_jornalistica"]["classe_jornalistica"]))
    vocab_teto = {"relacoes": ("tipo_relacao", "tipo_relacao"), "afirmacoes": ("predicado", "predicado_afirmacao")}
    for tabela in ("eventos", "relacoes", "afirmacoes"):
        t = POR_NOME[tabela]
        chave = t.chave[0]
        ligadas = fontes_ligadas(dados, tabela)
        for i, linha in dados[tabela].iterrows():
            fs = ligadas.get(linha[chave], [])
            if not fs:
                falhas.append(f"{_linha(tabela, i)}: {linha[chave]} sem fonte ligada")
                continue
            tipos = {tipo.get(f, "") for f in fs}
            permitido = nivel_permitido(tipos, {classe.get(f, "") for f in fs if tipo.get(f) == "jornalistica"})
            nivel = linha["nivel_confianca"]
            if nivel not in NIVEIS:
                continue
            if permitido is None:
                falhas.append(f"{_linha(tabela, i)}: {linha[chave]} sustentado só por jornalismo de opinião")
            elif NIVEIS.index(nivel) > NIVEIS.index(permitido):
                falhas.append(f"{_linha(tabela, i)}: {linha[chave]} marcado como {nivel}, mas as fontes só sustentam {permitido}")
            if tabela in vocab_teto:
                col, voc = vocab_teto[tabela]
                limite = teto(voc, linha[col])
                if limite and NIVEIS.index(nivel) > NIVEIS.index(limite):
                    falhas.append(f"{_linha(tabela, i)}: {linha[col]} tem teto {limite}, marcado como {nivel}")
    return falhas


def achados_com_ator_filiado(dados: dict[str, pd.DataFrame]) -> list[tuple[str, str, str]]:
    """(tabela, id, ano) de cada achado que exige verificação de simetria."""
    filiados = set(dados["filiacoes"]["id_ator"])
    achados = []
    for tabela, pares in (("afirmacoes", POR_NOME["afirmacoes"].polimorficas), ("relacoes", POR_NOME["relacoes"].polimorficas)):
        chave = POR_NOME[tabela].chave[0]
        data_col = "data" if tabela == "afirmacoes" else "data_inicio"
        for _, l in dados[tabela].iterrows():
            if any(l[tp] == "ator" and l[ident] in filiados for tp, ident in pares):
                achados.append((tabela, l[chave], l[data_col][:4]))
    for _, l in dados["status_pessoa_processo"].iterrows():
        if l["status"] in STATUS_COM_SIMETRIA and l["id_ator"] in filiados:
            achados.append(("status_pessoa_processo", l["id_status"], l["data"][:4]))
    return achados


def checar_simetria(dados: dict[str, pd.DataFrame]) -> tuple[list[str], list[str]]:
    falhas, avisos = [], []
    vs, vr = dados["verificacoes_simetria"], dados["verificacao_resultado"]
    buscas = dict(zip(dados["buscas"]["id_busca"], dados["buscas"]["n_resultados"]))
    verificados = set(zip(vs["achado_tabela"], vs["achado_id"]))
    for tabela, ident, _ano in achados_com_ator_filiado(dados):
        if (tabela, ident) not in verificados:
            avisos.append(f"{tabela}: {ident} envolve ator filiado e não tem verificação de simetria (bloqueia relatório)")

    for i, l in vr.iterrows():
        r = l["resultado"]
        if r == "sem_evidencia" and buscas.get(l["id_busca"]) != "0":
            falhas.append(f"{_linha('verificacao_resultado', i)}: 'sem_evidencia' exige busca registrada com zero resultados")
        if r == "encontrado" and (not l["n_casos"].isdigit() or int(l["n_casos"]) == 0 or not l["ids_encontrados"]):
            falhas.append(f"{_linha('verificacao_resultado', i)}: 'encontrado' exige n_casos > 0 e ids_encontrados")
        if r == "nao_verificado" and not l["justificativa"]:
            falhas.append(f"{_linha('verificacao_resultado', i)}: 'nao_verificado' exige justificativa")

    universo = dados["universo_partidos"]
    for _, v in vs.iterrows():
        res = vr[vr["id_verificacao"] == v["id_verificacao"]]
        if res["grupo_id"].nunique() < 2:
            falhas.append(f"verificacoes_simetria: {v['id_verificacao']} com menos de dois grupos comparados")
        partidos_ano = set(universo.loc[universo["ano"] == v["ano_referencia"], "id_partido"])
        if not partidos_ano:
            avisos.append(f"verificacoes_simetria: {v['id_verificacao']} sem universo de partidos para {v['ano_referencia']}")
            continue
        faltam = partidos_ano - set(res.loc[res["grupo_tipo"] == "partido", "grupo_id"])
        if faltam:
            falhas.append(f"verificacoes_simetria: {v['id_verificacao']} não cobre {len(faltam)} partido(s) do universo de {v['ano_referencia']}: {', '.join(sorted(faltam))}")
    return falhas, avisos


def checar_indices(dados: dict[str, pd.DataFrame]) -> list[str]:
    falhas = []
    for i, (ind, val) in dados["qualidade_democratica"][["indice", "valor"]].iterrows():
        if ind in VALORES_INDICE and not VALORES_INDICE[ind](val):
            falhas.append(f"{_linha('qualidade_democratica', i)}: valor {val!r} inválido para {ind}")
    return falhas


def checar_historico(dados: dict[str, pd.DataFrame], raiz: Path = RAIZ, base: Path = BASE) -> list[str]:
    """Tabelas que só crescem: toda linha do último commit precisa continuar igual."""
    falhas = []
    for t in TABELAS:
        if not t.so_cresce:
            continue
        rel = (base / f"{t.nome}.csv").resolve().relative_to(raiz.resolve()).as_posix()
        r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=raiz, capture_output=True)
        if r.returncode != 0:
            continue  # sem commit anterior
        antes = pd.read_csv(io.BytesIO(r.stdout), dtype=str, keep_default_na=False)
        atual = set(map(tuple, dados[t.nome].astype(str).itertuples(index=False)))
        perdidas = [l for l in map(tuple, antes.astype(str).itertuples(index=False)) if l not in atual]
        if perdidas:
            falhas.append(f"{t.nome}: {len(perdidas)} linha(s) do último commit apagada(s) ou alterada(s); o histórico só cresce")
    return falhas


def validar(base: Path = BASE, raiz: Path = RAIZ, historico: bool = True) -> tuple[list[str], list[str]]:
    dados, falhas = carregar(base)
    avisos: list[str] = []
    falhas += checar_colunas(dados)
    f, a = checar_datas(dados)
    falhas += f
    avisos += a
    falhas += checar_fontes(dados)
    falhas += checar_confianca(dados)
    f, a = checar_simetria(dados)
    falhas += f
    avisos += a
    falhas += checar_indices(dados)
    if historico:
        falhas += checar_historico(dados, raiz, base)
    return falhas, avisos


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=str(BASE))
    args = ap.parse_args()
    falhas, avisos = validar(Path(args.base))
    for f in falhas:
        print("FALHA:", f)
    for a in avisos:
        print("AVISO:", a)
    n = sum(len(pd.read_csv(Path(args.base) / f"{t.nome}.csv", dtype=str)) for t in TABELAS if (Path(args.base) / f"{t.nome}.csv").exists())
    print(f"{len(TABELAS)} tabelas, {n} registros: {len(falhas)} falha(s), {len(avisos)} aviso(s)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
