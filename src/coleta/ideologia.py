"""Posição ideológica dos partidos (D-062): Bolognesi, Ribeiro e Codato (2023), "Uma Nova Classificação Ideológica dos
Partidos Políticos Brasileiros", Dados 66(2), doi 10.1590/dados.2023.66.2.303, e a errata (doi ...303e).

A página do artigo e a da errata (SciELO, acesso aberto, CC BY) foram lidas no navegador embutido; o navegador devolve
os bytes em base64 com o sha256 calculado lá. Este módulo confere o sha256, grava no bruto e registra em `buscas`.

Uso:
    python -m src.coleta.ideologia --data AAAA-MM-DD --capturas <arquivo>
"""

import argparse
import base64
import hashlib
from pathlib import Path

from src.base import RegistroIds
from src.coleta.comum import Execucao, registrar_busca
from src.coleta.stf_ministros import ler_captura

SCRIPT = "src.coleta.ideologia"
NOMES = {"zzyM3gzHD4P45WWdytXjZWg": "bolognesi_ribeiro_codato_2023_artigo.html",
         "BfHDDt3rJmcxfG3rYQ8kzZp": "bolognesi_ribeiro_codato_2023_errata.html"}


def importar(arquivos: list[Path], data: str) -> None:
    execucao, ids, feitos = Execucao("ideologia", data), RegistroIds(), []
    for arq in arquivos:
        for p in ler_captura(arq)["paginas"]:
            corpo = base64.b64decode(p["base64"])
            if hashlib.sha256(corpo).hexdigest() != p["sha256"]:
                raise ValueError(f"sha256 não confere: {p['url']}")
            nome = next(v for k, v in NOMES.items() if k in p["url"])
            destino = execucao.pasta / nome
            if destino.exists():
                raise FileExistsError(f"{destino} já existe: data/raw é imutável")
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(corpo)
            execucao.arquivos[nome] = {"url_base": p["url"], "n_requisicoes": 1}
            feitos.append((nome, p["url"]))
    manifesto = {m["arquivo"].rsplit("/", 1)[1]: m for m in execucao.fechar()}
    for nome, url in feitos:
        registrar_busca("SciELO (Dados, revista de ciências sociais)", f"ideologia dos partidos: {nome}", 1, SCRIPT, data, {"url": url}, manifesto[nome], ids)
    ids.salvar()
    print(feitos)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--capturas", nargs="+", type=Path, required=True)
    a = ap.parse_args()
    importar(a.capturas, a.data)
