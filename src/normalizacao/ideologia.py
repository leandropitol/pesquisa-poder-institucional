"""Posição ideológica dos partidos (D-062): Tabela 1 de Bolognesi, Ribeiro e Codato (2023), lida do bruto.

Cada sigla da tabela é ligada ao partido da base pela denominação vigente em 30/06/2018 (ano do survey). Como o escore
é do partido (id da base), a mudança só de nome herda o escore; partido criado por fusão depois de 2018 não tem linha.
Todas as siglas precisam ser resolvidas; sem correspondência, o script para.

Saídas: posicao_ideologica, fontes e fonte_base_dados.

Uso:
    python -m src.normalizacao.ideologia --data AAAA-MM-DD
"""

import argparse
import html
import re

from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, gravar, ler
from src.simetria.governo_oposicao import Siglas

ARQ = "bolognesi_ribeiro_codato_2023_artigo.html"
DATA_REFERENCIA = "2018-06-30"
ROTULO = {"Progressistas": "PP", "Podemos": "PODEMOS", "Rede": "REDE", "Avante": "AVANTE", "Patriota": "PATRIOTA",
          "Novo": "NOVO", "Pros": "PROS", "SDD": "SOLIDARIEDADE"}
CORTES = [(1.5, "extrema_esquerda"), (3.0, "esquerda"), (4.49, "centro_esquerda"), (5.5, "centro"), (7.0, "centro_direita"),
          (8.5, "direita"), (10.0, "extrema_direita")]


def faixa(media: float) -> str:
    """Cortes do artigo; os limites publicados têm duas casas (1,5 | 1,51; 4,49 | 4,5)."""
    return next(f for teto, f in CORTES if round(media, 2) <= teto)


def num(x: str) -> str:
    return x.strip().replace(",", ".")


def tabela_1(corpo: bytes) -> pd.DataFrame:
    h = corpo.decode("utf-8")
    t = next(x for x in re.findall(r"<table.*?</table>", h, re.S) if "Desvio Padr" in x)
    linhas = [[html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)]
              for tr in re.findall(r"<tr.*?</tr>", t, re.S)]
    cab, dados = linhas[0], [l for l in linhas[1:] if l]
    if cab[:6] != ["Partido", "Média", "Mediana", "Moda", "Desvio Padrão", "N"]:
        raise ValueError(f"cabeçalho inesperado: {cab}")
    return pd.DataFrame(dados, columns=cab)


def montar(data: str, ids: RegistroIds, base: Path = BASE) -> dict:
    arq = RAIZ / "data" / "raw" / "ideologia" / data / ARQ
    t = tabela_1(arq.read_bytes())
    siglas = Siglas(ler("denominacoes_partido", base))
    man = pd.read_csv(RAIZ / "data" / "manifestos" / "ideologia.csv", dtype=str)
    sha = man.loc[man["arquivo"].str.endswith(ARQ), "sha256"].iloc[-1]
    f = ids.obter("fontes", "ideologia:bolognesi_ribeiro_codato_2023")
    fonte = {"id_fonte": f, "tipo_fonte": "base_de_dados", "data_publicacao": "2023-05-22",
             "titulo": "Bolognesi, Ribeiro e Codato (2023). Uma Nova Classificação Ideológica dos Partidos Políticos Brasileiros. Dados 66(2)",
             "url": "https://doi.org/10.1590/dados.2023.66.2.303", "data_acesso": data, "sha256": sha,
             "caminho_raw": arq.relative_to(RAIZ).as_posix(), "licenca": "CC BY (SciELO, acesso aberto)",
             "observacao": "Tabela 1 (escala esquerda-direita, 0 a 10, survey de 2018). A errata (doi ...303e) corrige só a Figura 2"}
    sub = {"id_fonte": f, "organizacao": "Dados, Revista de Ciências Sociais (IESP-UERJ)", "conjunto": "Tabela 1",
           "versao": "2023, com errata de 2024", "variavel": "média, mediana, moda, desvio-padrão e N por partido", "link": fonte["url"]}
    linhas, sem = [], []
    for r in t.itertuples(index=False):
        rot = r[0]
        p = siglas(ROTULO.get(rot, rot), DATA_REFERENCIA)
        if not p:
            sem.append(rot)
            continue
        media = float(num(r[1]))
        linhas.append({"id_partido": p, "escala": "brc_2018", "ano_referencia": "2018", "rotulo_fonte": rot, "media": num(r[1]),
                       "mediana": num(r[2]), "moda": num(r[3]), "desvio_padrao": num(r[4]), "n": r[5].strip(), "faixa": faixa(media), "id_fonte": f})
    if sem:
        raise ValueError(f"siglas sem partido na base em {DATA_REFERENCIA}: {sem}")
    if len({l["id_partido"] for l in linhas}) != len(linhas):
        raise ValueError("duas siglas da tabela caíram no mesmo partido")
    return {"posicao_ideologica": linhas, "fonte": fonte, "sub": sub}


def run(data: str) -> None:
    ids = RegistroIds()
    r = montar(data, ids)
    for nome, chave, novos in (("fontes", "id_fonte", [r["fonte"]]), ("fonte_base_dados", "id_fonte", [r["sub"]])):
        atual = ler(nome)
        gravar(nome, pd.concat([atual[~atual[chave].isin([x[chave] for x in novos])], pd.DataFrame(novos, dtype=str)], ignore_index=True))
    atual = ler("posicao_ideologica")
    novos = pd.DataFrame(r["posicao_ideologica"], dtype=str)
    gravar("posicao_ideologica", pd.concat([atual[atual["escala"] != "brc_2018"], novos], ignore_index=True))
    ids.salvar()
    print(novos.groupby("faixa").size().to_dict(), len(novos))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    run(ap.parse_args().data)
