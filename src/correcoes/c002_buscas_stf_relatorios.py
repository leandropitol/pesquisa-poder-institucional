"""Correção C-002 (D-035): chave repetida no registro de buscas dos relatórios de navegação do STF.

Os relatórios do Claude in Chrome registrados no mesmo dia tinham a mesma consulta ("relatório de navegação
do Claude in Chrome no portal do STF ...") e, por isso, a mesma chave. A consulta passa a trazer o nome do
arquivo gravado no bruto; a linha repetida recebe identificador novo, e a linha antiga, já gravada em
commit, fica listada em data/curadoria/correcoes_historico.csv.

Idempotente.

Uso:
    python -m src.correcoes.c002_buscas_stf_relatorios
"""

import csv
import io
import json
import subprocess

import pandas as pd

from src.base import RAIZ, RegistroIds, gravar, ler
from src.correcoes.c001_buscas_oea import CAMPOS, CORRECOES, sha1_linha

SCRIPT = "src.coleta.stf"
PREFIXO = "relatório de navegação do Claude in Chrome no portal do STF"


def run() -> None:
    ids = RegistroIds()
    b = ler("buscas")
    head = pd.read_csv(io.BytesIO(subprocess.run(["git", "show", "HEAD:data/base/buscas.csv"], cwd=RAIZ, capture_output=True).stdout),
                       dtype=str, keep_default_na=False)
    no_head = set(map(tuple, head.itertuples(index=False)))
    correcoes = list(csv.DictReader(CORRECOES.open(encoding="utf-8"))) if CORRECOES.exists() else []
    vistos = {}
    for i, l in b.iterrows():
        if l["script"] != SCRIPT or not l["consulta"].startswith(PREFIXO) or "(arquivo " in l["consulta"]:
            continue
        linha, id_antigo = tuple(l), l["id_busca"]
        arquivo = l["caminho_raw"].rsplit("/", 1)[-1]
        consulta = f"{PREFIXO} (arquivo {arquivo}; registro auxiliar, não é fonte primária)"
        repetida = id_antigo in vistos
        vistos.setdefault(id_antigo, i)
        novo = ids.obter("buscas", f"{SCRIPT}|{l['data']}|{consulta}") if repetida else id_antigo
        if not repetida:
            ids.vincular("buscas", f"{SCRIPT}|{l['data']}|{consulta}", novo)
        b.loc[i, ["id_busca", "consulta"]] = [novo, consulta]
        if linha in no_head:
            correcoes.append({"id_correcao": f"C-002.{len(correcoes) + 1}", "tabela": "buscas", "sha1_linha_antiga": sha1_linha(linha),
                              "id_novo": novo, "motivo": f"chave repetida {id_antigo} (consulta sem nome do arquivo); nova consulta: {consulta}",
                              "decisao": "D-035"})
    gravar("buscas", b)
    ids.salvar()
    unicas = list({c["sha1_linha_antiga"]: c for c in correcoes}.values())
    with CORRECOES.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, lineterminator="\n")
        w.writeheader()
        w.writerows(unicas)
    print(f"correções documentadas: {len(unicas)}")


if __name__ == "__main__":
    run()
