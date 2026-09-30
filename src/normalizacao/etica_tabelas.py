"""Montagem das tabelas da base a partir das representações dos Conselhos de Ética (D-063); regras e leitura em src.normalizacao.etica.

Saídas na base: instituicoes (os dois Conselhos), fontes, fonte_oficial, processos, fases_processo, status_pessoa_processo e a verificação de
simetria dos status adversos. Saídas de auditoria: relatorios/tabelas/etica_desfechos.csv (um registro por representado, com o texto que
sustenta o desfecho) e etica_nao_ligados.csv (representações sem parlamentar ligado).

Uso:
    python -m src.normalizacao.etica_tabelas --data AAAA-MM-DD
"""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, acrescentar, gravar, ler
from src.normalizacao.etica import (PASTA_PRS, PASTA_REP, RAW, Parlamentares, carregar_camara, carregar_senado, desfecho_camara, desfecho_senado,
                                    ler_csv, lerjsonl, nomeado, pareceres_camara, resolver_representados, resumo)
from src.normalizacao.simetria_padrao import verificar

PADRAO_ADVERSO = ("Status adverso em processo do Conselho de Ética da Câmara ou do Senado (mandato cassado ou sanção disciplinar aprovada), "
                  "de 2003 a 2026, em parlamentar federal; partido = filiação do parlamentar na data da decisão (D-063)")
SCRIPT = "src.normalizacao.etica_tabelas"


def texto_bruto(nome: str) -> str:
    """Conteúdo de um arquivo do bruto sem quebras de linha nem escapes JSON, para conferir trechos citados."""
    partes = []
    for pasta in (PASTA_REP, PASTA_PRS):
        arq = RAW / pasta / nome
        if arq.exists():
            partes += [json.dumps(r["corpo"], ensure_ascii=False) for r in lerjsonl(arq)]
    return " ".join(re.sub(r"\\n|\\r|\s+", " ", x) for x in partes)


def desfechos_manuais() -> dict:
    """Decisões lidas do texto do bruto e curadas; o trecho citado tem de estar no arquivo."""
    saida, cache = defaultdict(list), {}
    for r in ler_csv("etica_desfechos.csv"):
        if r["arquivo"] not in cache:
            cache[r["arquivo"]] = " ".join(texto_bruto(r["arquivo"]).split())
        if " ".join(r["trecho"].split()) not in cache[r["arquivo"]]:
            raise ValueError(f"trecho não encontrado em {r['arquivo']}: {r['trecho'][:70]}")
        saida[(r["casa"], r["processo"])].append(r)
    return saida


def montar(data: str, ids: RegistroIds, base: Path = BASE) -> dict:
    parl = Parlamentares.da_base(base)
    processos = carregar_camara() + carregar_senado()
    por_processo, nao_ligados = resolver_representados(processos, parl)
    manuais = desfechos_manuais()
    inst = ler("instituicoes", base)
    casa_id = {c: inst.loc[inst["sigla"] == c, "id_instituicao"].iloc[0] for c in ("CD", "SF")}
    ce = {c: ids.obter("instituicoes", f"orgao:CE:{c}") for c in ("CD", "SF")}
    novas_inst = [{"id_instituicao": ce["CD"], "nome": "Conselho de Ética e Decoro Parlamentar da Câmara dos Deputados", "sigla": "CEDP-CD",
                   "tipo_instituicao": "orgao_publico", "poder": "legislativo", "esfera": "federal", "pais_iso3": "BRA"},
                  {"id_instituicao": ce["SF"], "nome": "Conselho de Ética e Decoro Parlamentar do Senado Federal", "sigla": "CEDP-SF",
                   "tipo_instituicao": "orgao_publico", "poder": "legislativo", "esfera": "federal", "pais_iso3": "BRA"}]
    man = pd.read_csv(RAIZ / "data" / "manifestos" / "etica.csv", dtype=str)
    sha = {(r.arquivo.split("/")[-2], r.arquivo.split("/")[-1]): r.sha256 for r in man.itertuples()}
    fontes, oficiais, fonte_de = [], [], {}

    def fonte(chave, pasta, arquivo, titulo, url, casa, tipo_doc) -> str:
        if chave in fonte_de:
            return fonte_de[chave]
        i = ids.obter("fontes", f"etica:{chave}")
        fonte_de[chave] = i
        fontes.append({"id_fonte": i, "tipo_fonte": "oficial", "titulo": titulo, "data_publicacao": pasta[:10], "url": url, "data_acesso": pasta[:10],
                       "sha256": sha.get((pasta, arquivo), ""), "caminho_raw": f"data/raw/etica/{pasta}/{arquivo}", "licenca": "Dados abertos",
                       "observacao": "Registro oficial de tramitação, lido pela API de dados abertos"})
        oficiais.append({"id_fonte": i, "id_orgao": casa_id[casa], "tipo_documento": tipo_doc, "data_documento": pasta[:10], "link": url})
        return i

    f_cd = fonte("cd_tramitacoes", PASTA_REP, "camara_rep_tramitacoes.jsonl", "Câmara dos Deputados, dados abertos: tramitações das representações (REP)",
                 "https://dadosabertos.camara.leg.br/api/v2/proposicoes/{id}/tramitacoes", "CD", "Tramitação de proposição")
    f_sf = fonte("sf_processos", PASTA_REP, "senado_rep_detalhe.jsonl", "Senado Federal, dados abertos: processos do Conselho de Ética (REP, DEN, PCE)",
                 "https://legis.senado.leg.br/dadosabertos/processo/{id}", "SF", "Processo legislativo")
    f_prs = fonte("sf_prs", PASTA_PRS, "senado_prs_detalhe.jsonl", "Senado Federal, dados abertos: Projetos de Resolução do Senado gerados por representações",
                  "https://legis.senado.leg.br/dadosabertos/processo/{id}", "SF", "Processo legislativo")
    processos_out, fases, status, auditoria = [], [], [], []

    def add_status(chave_proc, id_proc, ator, st, d, tip, fonte_id):
        status.append({"id_status": ids.obter("status_pessoa_processo", f"etica:{chave_proc}:{ator}:{st}"), "id_ator": ator, "id_processo": id_proc,
                       "data": d, "status": st, "tipificacao": tip, "id_fonte": fonte_id})

    for p in processos:
        alvos = por_processo[(p["casa"], p["chave"])]
        if not alvos:
            continue
        cp = f"{p['casa']}:{p['chave']}"
        idp = ids.obter("processos", f"etica:{cp}")
        f_base = f_cd if p["casa"] == "CD" else f_sf
        processos_out.append({"id_processo": idp, "numero_originario": p["chave"], "classe": "representacao_etica", "id_tribunal": ce[p["casa"]],
                              "data_autuacao": p["data"], "assuntos_tpu": "Quebra de decoro parlamentar (art. 55, II, CF)", "url": p["url"], "id_fonte": f_base})
        fases.append({"id_fase": ids.obter("fases_processo", f"etica:{cp}:{p['data']}:representacao_etica"), "id_processo": idp, "data": p["data"],
                      "fase": "representacao_etica", "id_orgao_julgador": ce[p["casa"]], "resumo": resumo(p["ementa"]), "id_fonte": f_base})
        if p["casa"] == "CD":
            des = desfecho_camara(p["eventos"], p["situacao"])
            for f in pareceres_camara(p["eventos"]):
                fases.append({"id_fase": ids.obter("fases_processo", f"etica:{cp}:{f['data']}:{f['fase']}:{f['resumo'][:40]}"), "id_processo": idp,
                              "data": f["data"], "fase": f["fase"], "id_orgao_julgador": ce["CD"], "resumo": f["resumo"], "id_fonte": f_cd})
            fonte_des = f_cd
        else:
            des = desfecho_senado(p)
            delib = p["deliberacao"]
            if delib.get("data") and delib.get("tipoDeliberacao"):
                fases.append({"id_fase": ids.obter("fases_processo", f"etica:{cp}:{delib['data']}:parecer_conselho_etica"), "id_processo": idp,
                              "data": delib["data"], "fase": "parecer_conselho_etica", "id_orgao_julgador": ce["SF"], "resumo": delib["tipoDeliberacao"], "id_fonte": f_sf})
            dp = (p["prs"] or {}).get("deliberacao") or {}
            if dp.get("data"):
                fases.append({"id_fase": ids.obter("fases_processo", f"etica:{cp}:{dp['data']}:deliberacao_plenario"), "id_processo": idp, "data": dp["data"],
                              "fase": "deliberacao_plenario", "id_orgao_julgador": casa_id["SF"],
                              "resumo": f"{p['prs']['identificacao']}: {dp.get('tipoDeliberacao')}", "id_fonte": f_prs})
            fonte_des = f_prs if des and des["status"] in ("mandato_cassado", "representacao_improcedente") else f_sf
        for ator, metodo in alvos:
            add_status(cp, idp, ator, "representado", p["data"], "", f_base)
            fin = None
            for m in manuais.get((p["casa"], p["chave"]), []):
                if m["id_ator"] == ator:
                    fin = {"status": m["status"], "data": m["data"], "tipificacao": m["tipificacao"], "evidencia": m["trecho"], "origem": "curadoria"}
                    fonte_des = f_sf
            if fin is None and des and (len(alvos) == 1 or des["status"] == "arquivado" or nomeado(ator, des["evidencia"], parl)):
                fin = {**des, "origem": "regra"}
            if fin:
                add_status(cp, idp, ator, fin["status"], fin["data"], fin["tipificacao"], fonte_des)
            auditoria.append({"casa": p["casa"], "processo": p["chave"], "id_ator": ator, "ligacao": metodo, "apresentacao": p["data"],
                              "status_final": fin["status"] if fin else "", "data_final": fin["data"] if fin else "",
                              "tipificacao": fin["tipificacao"] if fin else "", "evidencia": fin["evidencia"] if fin else "",
                              "origem": fin["origem"] if fin else "", "ementa": resumo(p["ementa"], 160)})
    fases = list({f["id_fase"]: f for f in fases}.values())  # a mesma fase pode aparecer em mais de um evento com o mesmo texto
    adversos = [{"id_status": s["id_status"], "id_ator": s["id_ator"], "data": s["data"]} for s in status if s["status"] in ("mandato_cassado", "sancao_disciplinar")]
    buscas, vs, vr = verificar(adversos, PADRAO_ADVERSO, "etica|adverso", ids, data, SCRIPT, base)
    return {"instituicoes": novas_inst, "fontes": fontes, "fonte_oficial": oficiais, "processos": processos_out, "fases_processo": fases,
            "status_pessoa_processo": status, "buscas": buscas, "verificacoes_simetria": vs, "verificacao_resultado": vr,
            "auditoria": pd.DataFrame(auditoria), "nao_ligados": pd.DataFrame(nao_ligados)}


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    for nome, chave in (("instituicoes", "id_instituicao"), ("fontes", "id_fonte"), ("fonte_oficial", "id_fonte"), ("processos", "id_processo")):
        atual = ler(nome, base)
        novos = pd.DataFrame(r[nome], dtype=str)
        gravar(nome, pd.concat([atual[~atual[chave].isin(novos[chave])], novos], ignore_index=True), base)
    for nome, chave in (("fases_processo", "id_fase"), ("status_pessoa_processo", "id_status"), ("buscas", "id_busca"),
                        ("verificacoes_simetria", "id_verificacao"), ("verificacao_resultado", "id_resultado")):
        existentes = set(ler(nome, base)[chave])
        acrescentar(nome, [x for x in r[nome] if x[chave] not in existentes], base)
    ids.salvar()


def run(data: str) -> None:
    ids = RegistroIds()
    r = montar(data, ids)
    gravar_resultado(r, ids)
    saida = RAIZ / "relatorios" / "tabelas"
    r["auditoria"].to_csv(saida / "etica_desfechos.csv", index=False, encoding="utf-8")
    r["nao_ligados"].to_csv(saida / "etica_nao_ligados.csv", index=False, encoding="utf-8")
    a = r["auditoria"]
    print(f"processos: {len(r['processos'])}; fases: {len(r['fases_processo'])}; status: {len(r['status_pessoa_processo'])}; não ligados: {len(r['nao_ligados'])}")
    print(a["status_final"].replace("", "sem desfecho").value_counts().to_dict())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    run(ap.parse_args().data)
