"""Registro das buscas do contraste com a imprensa (D-047, D-055, D-056, D-057).

As buscas são feitas pela ferramenta de busca na web do assistente, restritas ao domínio de cada veículo, com a
consulta fixa de cada fato (data/curadoria/imprensa_fatos.csv). Este módulo grava no bruto, sem alteração, o que a
ferramenta devolveu (título e URL de cada link; o resumo automático não é guardado nem usado) e registra cada busca
em `buscas`, inclusive as sem resultado e as sem acesso.

Os veículos sem acesso pela ferramenta foram buscados por agentes no navegador do autor (D-057). Os relatórios
entregues (Markdown com uma tabela por veículo e fato) vão para o bruto com nome padronizado, sem alteração de
conteúdo, e cada busca relatada vai para `buscas`. `ler_relatorio` converte o relatório em registros no mesmo
formato das buscas da ferramenta.

Uso:
    python -m src.coleta.imprensa <arquivo.json> --data AAAA-MM-DD   (lote de buscas da ferramenta)
    python -m src.coleta.imprensa --data AAAA-MM-DD --relatorios      (relatórios deixados em data/raw/imprensa)
    python -m src.coleta.imprensa --data AAAA-MM-DD --fechar          (manifesto do lote do dia)
"""

import argparse
import datetime as dt
import json
import re
import shutil
from pathlib import Path

import pandas as pd

from src.base import RAIZ, RegistroIds
from src.coleta.comum import registrar_busca, sha256

RAW = RAIZ / "data" / "raw" / "imprensa"
CUR = RAIZ / "data" / "curadoria"
MANIFESTO = RAIZ / "data" / "manifestos" / "imprensa.csv"
SCRIPT = "src.coleta.imprensa"
FONTE = "Ferramenta de busca na web do assistente (restrita ao domínio do veículo)"
# arquivo entregue -> (nome no bruto, coleta, descrição da fonte, usado na classificação)
RELATORIOS = {
    "relatorio_imprensa_principais.md": ("navegador_claude_chrome_google.md", "chrome_google",
                                         "Google (site:), via Claude in Chrome no navegador do autor, sem login", True),
    "relatorio_imprensa_principais-chatgpt.md": ("navegador_chatgpt_busca.md", "chatgpt_busca",
                                                 "Buscador web do ChatGPT (site:), relatado pelo agente", True),
    "gemini-code-1790702388647.md": ("navegador_gemini.md", "gemini",
                                     "Relatório do Gemini (ferramenta não identificada)", False),
}


def registrar(registros: list[dict], data: str) -> None:
    """Cada registro: {fato, veiculo, dominio, consulta, acesso ('ok' | 'sem_acesso' | 'bloqueado'), links: [{title, url}]}."""
    pasta = RAW / data
    pasta.mkdir(parents=True, exist_ok=True)
    arq = pasta / "buscas.jsonl"
    with arq.open("a", encoding="utf-8", newline="\n") as f:
        for r in registros:
            f.write(json.dumps({**r, "registrado_em": dt.datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False) + "\n")
    ids = RegistroIds()
    reg = {"arquivo": arq.relative_to(RAIZ).as_posix(), "sha256": ""}  # arquivo cresce ao longo do dia; sha256 fica no manifesto ao fechar
    for r in registros:
        consulta = f"{r['fato']} | {r['veiculo']} ({r['dominio']}): {r['consulta']}"
        registrar_busca(FONTE, consulta, len(r["links"]) if r["acesso"] == "ok" else 0, SCRIPT, data,
                        {"fato": r["fato"], "dominio": r["dominio"], "acesso": r["acesso"]}, reg, ids)
    ids.salvar()


def _manifesto(linha: str) -> None:
    novo = not MANIFESTO.exists()
    with MANIFESTO.open("a", encoding="utf-8", newline="") as m:
        if novo:
            m.write("data_acesso,arquivo,url_base,n_requisicoes,bytes,sha256\n")
        m.write(linha + "\n")


def fechar_manifesto(data: str) -> None:
    arq = RAW / data / "buscas.jsonl"
    n = sum(1 for _ in arq.open(encoding="utf-8"))
    _manifesto(f"{data},{arq.relative_to(RAIZ).as_posix()},ferramenta de busca na web,{n},{arq.stat().st_size},{sha256(arq)}")


def _celulas(linha: str) -> list[str]:
    partes = re.split(r"(?<!\\)\|", linha.strip().strip("|"))
    return [p.strip().replace("\\|", "|") for p in partes]


def ler_relatorio(texto: str, veiculos: pd.DataFrame, fatos: pd.DataFrame) -> list[dict]:
    """Registros {fato, veiculo, dominio, consulta, acesso, links: [{title, url, data_exibida}]} de um relatório.

    Seção de veículo: título que contém o nome de um veículo. Seção de fato: título que começa por Fnn. Linha de
    tabela com posição numérica é um link; a palavra "bloqueado" na seção marca a busca como bloqueada; seção sem
    link e sem bloqueio é busca com acesso e sem resultado."""
    nomes = veiculos.set_index("veiculo")["dominio"].to_dict()
    consultas = fatos.set_index("id_fato")["consulta"].to_dict()
    regs, veic, atual = [], None, None

    def fechar():
        if atual:
            regs.append({"fato": atual["fato"], "veiculo": veic, "dominio": nomes[veic], "consulta": consultas[atual["fato"]],
                         "acesso": "bloqueado" if atual["bloq"] else "ok", "links": [] if atual["bloq"] else atual["links"]})

    for linha in texto.splitlines():
        s = linha.strip()
        if s.startswith("#") or s == "---":
            fechar()
            atual = None
            m = re.match(r"#+\s*(F\d{2})\b", s)
            if m and veic and m.group(1) in consultas:
                atual = {"fato": m.group(1), "bloq": False, "links": []}
            elif s.startswith("#"):
                achados = [v for v in nomes if v.casefold() in s.casefold()]
                veic = achados[0] if achados else (veic if m else None)
            continue
        if not atual:
            continue
        if s.startswith("|"):
            c = _celulas(s)
            if c and c[0].isdigit() and len(c) >= 3:
                atual["links"].append({"title": c[1], "url": c[2], "data_exibida": c[3] if len(c) > 3 else ""})
                continue
        if "bloquead" in s.casefold():
            atual["bloq"] = True
    fechar()
    return regs


def registrar_relatorios(data: str) -> None:
    veic = pd.read_csv(CUR / "imprensa_veiculos.csv", dtype=str)
    fatos = pd.read_csv(CUR / "imprensa_fatos.csv", dtype=str)
    pasta = RAW / data
    pasta.mkdir(parents=True, exist_ok=True)
    ids = RegistroIds()
    for original, (nome, coleta, fonte, usado) in RELATORIOS.items():
        origem, destino = RAW / original, pasta / nome
        if destino.exists() or not origem.exists():
            continue
        shutil.move(origem, destino)
        reg = {"arquivo": destino.relative_to(RAIZ).as_posix(), "sha256": sha256(destino)}
        regs = ler_relatorio(destino.read_text(encoding="utf-8"), veic, fatos)
        _manifesto(f"{data},{reg['arquivo']},relatório de navegação: {coleta} (arquivo entregue {original}),{len(regs)},"
                   f"{destino.stat().st_size},{reg['sha256']}")
        if not usado:
            print(f"{nome}: guardado no bruto, fora da classificação (D-057)")
            continue
        for r in regs:
            consulta = f"{r['fato']} | {r['veiculo']} ({r['dominio']}) | {coleta}: {r['consulta']}"
            registrar_busca(fonte, consulta, len(r["links"]), SCRIPT, data,
                            {"fato": r["fato"], "dominio": r["dominio"], "acesso": r["acesso"], "coleta": coleta}, reg, ids)
        print(f"{nome}: {len(regs)} buscas ({sum(r['acesso'] == 'ok' for r in regs)} com acesso)")
    ids.salvar()


def relatorios_usados(data: str | None = None) -> list[dict]:
    """Registros dos relatórios usados na classificação, com a coleta de origem."""
    veic = pd.read_csv(CUR / "imprensa_veiculos.csv", dtype=str)
    fatos = pd.read_csv(CUR / "imprensa_fatos.csv", dtype=str)
    saida = []
    for nome, coleta, _, usado in RELATORIOS.values():
        if not usado:
            continue
        for arq in sorted(RAW.glob(f"{data or '*'}/{nome}")):
            saida += [{**r, "coleta": coleta} for r in ler_relatorio(arq.read_text(encoding="utf-8"), veic, fatos)]
    return saida


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo", nargs="?")
    ap.add_argument("--data", required=True)
    ap.add_argument("--fechar", action="store_true")
    ap.add_argument("--relatorios", action="store_true")
    a = ap.parse_args()
    if a.fechar:
        fechar_manifesto(a.data)
    elif a.relatorios:
        registrar_relatorios(a.data)
    else:
        registrar(json.loads(Path(a.arquivo).read_text(encoding="utf-8")), a.data)
