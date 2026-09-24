"""Materializa o esquema e os vocabulários:

- data/base/<tabela>.csv: criado só com cabeçalho quando não existe. Um CSV existente
  nunca é sobrescrito; se o cabeçalho divergir do esquema, o script avisa e para.
- data/vocabularios/<nome>.csv: regravados a partir de src/vocabularios.py.
- docs/esquema_dados.md e docs/vocabularios.md: regravados (documentação gerada).

Uso:
    python -m src.estrutura
"""

import csv
import sys
from pathlib import Path

from src.esquema import TABELAS
from src.vocabularios import VOCABULARIOS

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ / "data" / "base"
VOCAB = RAIZ / "data" / "vocabularios"
DOCS = RAIZ / "docs"


def _cabecalho(caminho: Path) -> list[str]:
    with caminho.open(encoding="utf-8", newline="") as f:
        return next(csv.reader(f), [])


def criar_tabelas(base: Path = BASE) -> list[str]:
    base.mkdir(parents=True, exist_ok=True)
    divergencias = []
    for t in TABELAS:
        caminho = base / f"{t.nome}.csv"
        if not caminho.exists():
            with caminho.open("w", encoding="utf-8", newline="") as f:
                csv.writer(f, lineterminator="\n").writerow(t.nomes)
        elif _cabecalho(caminho) != t.nomes:
            divergencias.append(f"{caminho.name}: cabeçalho difere do esquema (migração manual necessária)")
    return divergencias


def gravar_vocabularios(pasta: Path = VOCAB) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    for nome, linhas in VOCABULARIOS.items():
        campos = ["codigo", "rotulo"] + sorted({k for l in linhas for k in l} - {"codigo", "rotulo"})
        with (pasta / f"{nome}.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
            w.writeheader()
            w.writerows(linhas)


def doc_esquema() -> str:
    partes = [
        "# Dicionário de dados\n",
        "Gerado por `python -m src.estrutura` a partir de `src/esquema.py`. Não editar à mão.\n",
        "Cada tabela é um CSV em `data/base/`. Tipos: `id` (PREFIXO-000001), `ref` (referência), `data` "
        "(AAAA, AAAA-MM ou AAAA-MM-DD), `vocab` (vocabulário fechado, ver `docs/vocabularios.md`), `lista` "
        "(identificadores separados por `;`), `bool` (true/false), `iso3` (código de país).\n",
    ]
    grupo = None
    for t in TABELAS:
        if t.grupo != grupo:
            grupo = t.grupo
            partes.append(f"## {grupo.replace('_', ' ').capitalize()}\n")
        extras = []
        if t.prefixo:
            extras.append(f"prefixo `{t.prefixo}`")
        if t.so_cresce:
            extras.append("só cresce (histórico)")
        partes.append(f"### `{t.nome}`\n\n{t.descricao} Chave: `{', '.join(t.chave)}`" + (f"; {'; '.join(extras)}." if extras else ".") + "\n")
        linhas = ["| Coluna | Tipo | Obrigatória | Descrição |", "|---|---|---|---|"]
        for c in t.colunas:
            tipo = c.tipo + (f" (`{c.vocab}`)" if c.vocab else "") + (f" → `{c.fk}`" if c.fk else "")
            linhas.append(f"| `{c.nome}` | {tipo} | {'sim' if c.obrigatoria else ''} | {c.descricao} |")
        partes.append("\n".join(linhas) + "\n")
    return "\n".join(partes)


def doc_vocabularios() -> str:
    partes = ["# Vocabulários fechados\n", "Gerado por `python -m src.estrutura` a partir de `src/vocabularios.py`. Não editar à mão.\n"]
    for nome, linhas in VOCABULARIOS.items():
        extras = sorted({k for l in linhas for k in l} - {"codigo", "rotulo"})
        cab = ["Código", "Rótulo"] + extras
        tabela = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
        for l in linhas:
            tabela.append("| " + " | ".join([f"`{l['codigo']}`", l["rotulo"]] + [l.get(e, "") for e in extras]) + " |")
        partes.append(f"## `{nome}`\n\n" + "\n".join(tabela) + "\n")
    return "\n".join(partes)


def run() -> int:
    divergencias = criar_tabelas()
    gravar_vocabularios()
    (DOCS / "esquema_dados.md").write_text(doc_esquema(), encoding="utf-8")
    (DOCS / "vocabularios.md").write_text(doc_vocabularios(), encoding="utf-8")
    print(f"{len(TABELAS)} tabelas, {len(VOCABULARIOS)} vocabulários")
    for d in divergencias:
        print("AVISO:", d)
    return 1 if divergencias else 0


if __name__ == "__main__":
    sys.exit(run())
