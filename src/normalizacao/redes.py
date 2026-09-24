"""Leitura das cópias anuais das listas de membros das redes partidárias (etapa E8, bloco D).

Para cada cópia (data/raw/redes/<data>/<rede>/), procura partidos brasileiros de três formas:

- nome sem ambiguidade (tabela data/curadoria/redes_apelidos_partidos.csv), em qualquer ponto da página;
- nome ambíguo (marcado "só vale perto de Brasil/Brazil"), só a até 250 caracteres depois ou 80 antes
  de "Brasil", "Brazil" ou "Brésil";
- sigla, só nos 300 caracteres que seguem "Brasil", "Brazil" ou "Brésil" (é assim que as listas por país
  são escritas).

Cada achado sai com o trecho literal, para revisão. Nada vai para a base nesta etapa: a saída é
data/staging/redes/deteccoes.csv e o quadro rede x ano em data/staging/redes/quadro.csv.

Uso:
    python -m src.normalizacao.redes
"""

import csv
import html
import re
import unicodedata

import pandas as pd

from src.base import RAIZ

MANIFESTO = RAIZ / "data" / "manifestos" / "redes.csv"
APELIDOS = RAIZ / "data" / "curadoria" / "redes_apelidos_partidos.csv"
SAIDA = RAIZ / "data" / "staging" / "redes"
RE_PAIS = re.compile(r"\b(?:Brasil|Brazil|Brésil|BRASIL|BRAZIL)\b")
DEPOIS, ANTES, JANELA_SIGLA = 250, 80, 300


def sem_acento(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def texto_html(conteudo: bytes) -> str:
    for cod in ("utf-8", "cp1252", "latin-1"):
        try:
            h = conteudo.decode(cod)
            break
        except UnicodeDecodeError:
            continue
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?s)<!--.*?-->", " ", h)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", h)).split())


def carregar_apelidos() -> tuple[list[tuple[re.Pattern, str, bool]], dict[str, str]]:
    nomes, siglas = [], {}
    for l in csv.DictReader(APELIDOS.open(encoding="utf-8")):
        perto = "só vale perto" in l["observacao"]
        padrao = re.compile(r"\b" + re.escape(sem_acento(l["apelido"])).replace(r"\ ", r"\s+").replace("'", "['’]?") + r"\b", re.I)
        nomes.append((padrao, l["sigla"], perto))
        siglas[l["sigla"].upper()] = l["sigla"]
    return nomes, siglas


def deteccoes(texto: str, nomes: list, siglas: dict) -> list[dict]:
    """Partidos brasileiros citados na página, com a forma de detecção e o trecho."""
    t = sem_acento(texto)
    marcas = [m.start() for m in RE_PAIS.finditer(t)]
    achados = []
    for padrao, sigla, perto in nomes:
        for m in padrao.finditer(t):
            if perto and not any(m.start() - DEPOIS <= p <= m.end() + ANTES and not (m.start() <= p < m.end()) for p in marcas):
                continue
            achados.append({"sigla": sigla, "via": "nome_perto_do_pais" if perto else "nome", "pos": m.start(),
                            "trecho": texto[max(0, m.start() - 120):m.end() + 120]})
    re_sigla = re.compile(r"(?<![\w-])(" + "|".join(re.escape(s) for s in sorted(siglas, key=len, reverse=True)) + r")(?![\w-])")
    for p in marcas:
        for m in re_sigla.finditer(t[p:p + JANELA_SIGLA]):
            achados.append({"sigla": siglas[m.group(1).upper()], "via": "sigla_apos_pais", "pos": p + m.start(),
                            "trecho": texto[max(0, p - 40):p + JANELA_SIGLA]})
    return achados


def tabela_deteccoes() -> pd.DataFrame:
    """Uma linha por (cópia, partido, forma de detecção); cópias sem partido brasileiro também entram."""
    nomes, siglas = carregar_apelidos()
    linhas = []
    for reg in csv.DictReader(MANIFESTO.open(encoding="utf-8")):
        caminho = RAIZ / reg["arquivo"]
        rede, arquivo = caminho.parent.name, caminho.name
        ts = arquivo.split("_", 1)[0]
        texto = texto_html(caminho.read_bytes())
        vistos = set()
        for a in sorted(deteccoes(texto, nomes, siglas), key=lambda a: ("nome" not in a["via"], a["pos"])):
            if (a["sigla"], a["via"]) in vistos:
                continue
            vistos.add((a["sigla"], a["via"]))
            linhas.append({"id_rede": rede, "ano": ts[:4], "timestamp": ts, "arquivo": reg["arquivo"], "url_arquivo": reg["url_base"],
                           "sigla": a["sigla"], "via": a["via"], "trecho": a["trecho"][:400]})
        if not any(l["arquivo"] == reg["arquivo"] for l in linhas[-50:]):
            linhas.append({"id_rede": rede, "ano": ts[:4], "timestamp": ts, "arquivo": reg["arquivo"], "url_arquivo": reg["url_base"],
                           "sigla": "", "via": "nenhum_partido_brasileiro", "trecho": f"{len(texto)} caracteres de texto"})
    return pd.DataFrame(linhas)


def run() -> None:
    d = tabela_deteccoes()
    SAIDA.mkdir(parents=True, exist_ok=True)
    d.to_csv(SAIDA / "deteccoes.csv", index=False, encoding="utf-8")
    q = d[d["sigla"] != ""].groupby(["id_rede", "ano"])["sigla"].apply(lambda s: " ".join(sorted(set(s)))).unstack(fill_value="")
    q.to_csv(SAIDA / "quadro.csv", encoding="utf-8")
    with pd.option_context("display.width", 250, "display.max_columns", 40, "display.max_colwidth", 22):
        print(q.T.to_string())


if __name__ == "__main__":
    run()
