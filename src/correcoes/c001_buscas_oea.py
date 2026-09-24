"""Correção C-001 (D-035): chaves repetidas no registro de buscas da coleta da OEA.

O coletor montava a consulta de falha como "volume da sessão X (falha no download)". Duas situações
repetiram a chave: a sessão extraordinária de 2009 tem dois arquivos, e a coleta das atas usou a
mesma consulta da coleta dos volumes. As atas também ficaram rotuladas como volumes.

A correção:
1. linhas ainda não gravadas em commit: a consulta passa a trazer o tipo e o nome do arquivo ("ata
   atas_2005_XXXV-O_AC00917T04.DOC (falha no download)"), com a fonte de dados das atas; a chave
   repetida recebe identificador novo;
2. linha já gravada em commit (segundo arquivo da sessão extraordinária de 2009): recebe identificador
   novo e consulta com o nome do arquivo. A linha antiga fica listada em
   data/curadoria/correcoes_historico.csv, que o validador aceita como alteração documentada.

Idempotente: rodar de novo não muda nada.

Uso:
    python -m src.correcoes.c001_buscas_oea
"""

import csv
import hashlib
import io
import json
import subprocess

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, gravar, ler

SCRIPT = "src.coleta.oea"
FONTE_ATAS = "OEA, atas das sessões plenárias da Assembleia Geral"
CORRECOES = RAIZ / "data" / "curadoria" / "correcoes_historico.csv"
CAMPOS = ["id_correcao", "tabela", "sha1_linha_antiga", "id_novo", "motivo", "decisao"]


def sha1_linha(valores) -> str:
    return hashlib.sha1("\x1f".join(map(str, valores)).encode("utf-8")).hexdigest()


def nome_do_arquivo(url: str, ano_sessao: dict, atas: bool) -> str:
    arq = url.rsplit("/", 1)[1]
    ano, sessao = ano_sessao[url]
    return f"{'atas_' if atas else ''}{ano}_{sessao}_{arq}"


def run() -> None:
    ids = RegistroIds()
    b = ler("buscas")
    r = subprocess.run(["git", "show", "HEAD:data/base/buscas.csv"], cwd=RAIZ, capture_output=True)
    head = pd.read_csv(io.BytesIO(r.stdout), dtype=str, keep_default_na=False)
    no_head = set(map(tuple, head.itertuples(index=False)))
    urls_atas, ano_sessao = set(), {}
    for lista, atas in (("oea_volumes.csv", False), ("oea_atas.csv", True)):
        for l in csv.DictReader((RAIZ / "data" / "curadoria" / lista).open(encoding="utf-8")):
            ano_sessao[l["url"]] = (l["ano"], l["sessao"])
            if atas:
                urls_atas.add(l["url"])
    correcoes = list(csv.DictReader(CORRECOES.open(encoding="utf-8"))) if CORRECOES.exists() else []
    vistos = {}
    for i, l in b.iterrows():
        if l["script"] != SCRIPT:
            continue
        linha, id_antigo = tuple(l), l["id_busca"]
        url = json.loads(l["parametros_json"] or "{}").get("url", "")
        atas = url in urls_atas
        consulta, fonte = l["consulta"], l["fonte_dados"]
        if atas:
            fonte = FONTE_ATAS + (" (download manual do autor, D-034)" if "manual" in fonte else "")
            consulta = consulta.replace("volume atas_", "ata atas_", 1)
        if "(falha no download)" in consulta and url in ano_sessao:
            consulta = f"{'ata' if atas else 'volume'} {nome_do_arquivo(url, ano_sessao, atas)} (falha no download)"
        chave_antiga = f"{SCRIPT}|{l['data']}|{l['consulta']}"
        repetida = l["id_busca"] in vistos and vistos[l["id_busca"]] != i
        vistos.setdefault(l["id_busca"], i)
        if (consulta == l["consulta"] and fonte == l["fonte_dados"] and not repetida) or (linha in no_head and not repetida):
            continue  # linha gravada em commit só muda quando a chave é repetida
        novo = l["id_busca"]
        chave_nova = f"{SCRIPT}|{l['data']}|{consulta}"
        if repetida:
            novo = ids.obter("buscas", chave_nova)
        else:
            ids.vincular("buscas", chave_nova, novo)
            if ids.mapa.get(("buscas", chave_antiga)) == novo and chave_antiga != chave_nova:
                del ids.mapa[("buscas", chave_antiga)]
        b.loc[i, ["id_busca", "consulta", "fonte_dados"]] = [novo, consulta, fonte]
        if linha in no_head:
            correcoes.append({"id_correcao": f"C-001.{len(correcoes) + 1}", "tabela": "buscas", "sha1_linha_antiga": sha1_linha(linha), "id_novo": novo,
                              "motivo": f"chave repetida {id_antigo} (consulta sem nome do arquivo); nova consulta: {consulta}",
                              "decisao": "D-035"})
    gravar("buscas", b)
    ids.salvar()
    unicas = list({c["sha1_linha_antiga"]: c for c in correcoes}.values())
    with CORRECOES.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, lineterminator="\n")
        w.writeheader()
        w.writerows(unicas)
    print(f"buscas corrigidas; correções de linhas já gravadas: {len(unicas)}")


if __name__ == "__main__":
    run()
