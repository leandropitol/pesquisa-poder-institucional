"""Registros individuais do TCU e do TSE para parlamentares e eleitos da base (eixo 1, D-064).

Liga os candidatos das eleições gerais de 2002 a 2022 (TSE, consulta_cand, com CPF) aos atores da base e registra, com fonte oficial:
- `contas_julgadas_irregulares`: linha da lista pública do TCU de responsáveis com contas julgadas irregulares (trânsito em julgado de
  2003 em diante) cujo CPF é o de um ator ligado; processo de classe `processo_tcu`;
- `candidatura_indeferida`: candidatura de 2018 ou 2022 com motivo do eixo 1 no arquivo de motivos do TSE, pela mesma regra de D-060 e
  D-061; processo de classe `registro_candidatura` (número do processo do TSE).

O CPF só serve de chave de ligação entre os arquivos: não entra na base, nas tabelas nem nos relatórios. Ligação candidato-ator:
`ligar_atores` de src.normalizacao.tse (nome de urna ou civil, único entre quem tem mandato na legislatura); presidente e governador,
por nome civil exato único na base. Um ator com dois CPF diferentes nas ligações é descartado e listado.

Cada status recebe a verificação de simetria por partido (src.normalizacao.simetria_padrao).

Uso:
    python -m src.normalizacao.eixo1_registros --data AAAA-MM-DD
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import pandas as pd

from src.analise.eixo1 import ANOS_MOTIVO, data_iso, digitos, motivos
from src.base import BASE, RAIZ, RegistroIds, acrescentar, gravar, ler
from src.normalizacao.simetria_padrao import verificar
from src.normalizacao.tse import CARGOS, arquivo, ler_zip, ligar_atores, norm
from src.simetria.governo_oposicao import Siglas

SCRIPT = "src.normalizacao.eixo1_registros"
ANOS_ELEICAO = [2002, 2006, 2010, 2014, 2018, 2022]
INICIO_JANELA = "2003-01-01"
PADRAO_TCU = ("Contas julgadas irregulares pelo TCU, com trânsito em julgado a partir de 2003, de deputado federal, senador, governador ou presidente da "
              "base (CPF na lista pública do TCU); partido = filiação do ator na data do trânsito em julgado (D-064)")
PADRAO_TSE = ("Candidatura de deputado federal, senador, governador ou presidente da base indeferida ou cassada por motivo do eixo 1 (D-060, D-061) nas "
              "eleições gerais de 2018 e 2022; partido = filiação do ator na data da eleição (D-064)")
MANIFESTO_TCU = RAIZ / "data" / "manifestos" / "tcu.csv"
MANIFESTO_TSE = RAIZ / "data" / "manifestos" / "tse.csv"


def cnj(n: str) -> str:
    """NNNNNNNDDAAAAJTROOOO -> NNNNNNN-DD.AAAA.J.TR.OOOO; vazio se não tiver 20 dígitos."""
    n = digitos(n)
    return f"{n[:7]}-{n[7:9]}.{n[9:13]}.{n[13]}.{n[14:16]}.{n[16:]}" if len(n) == 20 else ""


def candidatos_amplos(ano: int) -> pd.DataFrame:
    """Deputados federais e senadores eleitos ou suplentes, governadores eleitos e todos os candidatos a presidente; com CPF."""
    d = ler_zip(arquivo(f"consulta_cand_{ano}.zip"), lambda n: n.endswith("_BRASIL.csv"))
    d = d[d["NM_TIPO_ELEICAO"].map(norm).str.contains("ordinaria") & d["DS_CARGO"].str.upper().isin(CARGOS)].copy()
    d["NR_TURNO"] = d["NR_TURNO"].astype(int)
    primeira = d.groupby(["SG_UF", "SQ_CANDIDATO"])["DT_ELEICAO"].min()
    d = d.sort_values("NR_TURNO").drop_duplicates(["SG_UF", "SQ_CANDIDATO"], keep="last")
    d["cargo"] = d["DS_CARGO"].str.upper()
    sit = d["DS_SIT_TOT_TURNO"].map(norm)
    d["eleito"] = sit.str.startswith("eleito") | (sit == "media")
    manter = (d["cargo"] == "PRESIDENTE") | d["eleito"] | ((d["cargo"].isin(["DEPUTADO FEDERAL", "SENADOR"])) & sit.str.startswith("suplente"))
    d = d[manter].copy()
    d["ano"] = ano
    for c in ("DS_SITUACAO_CANDIDATURA", "DS_DETALHE_SITUACAO_CAND"):  # ausentes em alguns anos
        if c not in d.columns:
            d[c] = ""
    d["cpf"] = d["NR_CPF_CANDIDATO"].map(digitos)
    d["data_eleicao"] = [data_iso(primeira[(u, s)]) for u, s in zip(d["SG_UF"], d["SQ_CANDIDATO"])]
    return d[["ano", "SG_UF", "SQ_CANDIDATO", "cargo", "eleito", "NM_CANDIDATO", "NM_URNA_CANDIDATO", "SG_PARTIDO", "cpf", "data_eleicao",
              "DS_SITUACAO_CANDIDATURA", "DS_DETALHE_SITUACAO_CAND", "DS_SIT_TOT_TURNO"]]


def ligar(atores: pd.DataFrame, cargos: pd.DataFrame, filiacoes: pd.DataFrame, siglas: Siglas) -> tuple[pd.DataFrame, dict]:
    """Candidaturas ligadas a atores, com regras de segurança contra falso vínculo (o CPF põe o registro na pessoa ligada):
    (1) método `nome` (nome civil ou de urna igual ao da base) sempre serve; método `palavras` só se o partido da candidatura consta
    em alguma filiação do ator; (2) um ator só pode ter uma candidatura por eleição e cargo (com mais de uma, só vale se uma única
    é método `nome`); (3) o ator tem de ter um único CPF em todas as candidaturas ligadas. Devolve (ligadas, contagens de descarte)."""
    por_nome = defaultdict(set)
    for i, n in zip(atores["id_ator"], atores["nome_normalizado"]):
        por_nome[n].add(i)
    partidos_de = filiacoes.groupby("id_ator")["id_partido"].agg(set).to_dict()
    partes, desc = [], {"palavras_sem_partido": 0, "candidaturas_repetidas": 0, "cpf_divergente": 0}
    for ano in ANOS_ELEICAO:
        c = candidatos_amplos(ano)
        lig, metodo = ligar_atores(c, atores, cargos)
        chaves = list(zip(c["ano"], c["SG_UF"], c["SQ_CANDIDATO"]))
        c["id_ator"] = [lig.get(k, "") for k in chaves]
        c["metodo"] = [metodo.get(k, "") for k in chaves]
        exec_ = c["cargo"].isin(["PRESIDENTE", "GOVERNADOR"]) & (c["id_ator"] == "")
        for i in c.index[exec_]:
            achados = por_nome.get(norm(c.at[i, "NM_CANDIDATO"]), set())
            if len(achados) == 1:
                c.at[i, "id_ator"], c.at[i, "metodo"] = next(iter(achados)), "nome"
        c = c[c["id_ator"] != ""].copy()
        c["id_partido"] = [siglas(sg, d) or "" for sg, d in zip(c["SG_PARTIDO"], c["data_eleicao"])]
        fraco = (c["metodo"] == "palavras") & pd.Series([p not in partidos_de.get(a, set()) for p, a in zip(c["id_partido"], c["id_ator"])], index=c.index)
        desc["palavras_sem_partido"] += int(fraco.sum())
        c = c[~fraco]
        forte = c[c["metodo"] == "nome"].groupby(["id_ator", "cargo"]).size()
        total = c.groupby(["id_ator", "cargo"]).size()
        rep = [(a, g) for (a, g), n in total.items() if n > 1 and forte.get((a, g), 0) != 1]
        desc["candidaturas_repetidas"] += len(rep)
        rep = set(rep)
        c = c[[(a, g) not in rep for a, g in zip(c["id_ator"], c["cargo"])]]
        multiplas = set(total[total > 1].index)
        c = c[~((c["metodo"] == "palavras") & pd.Series([(a, g) in multiplas for a, g in zip(c["id_ator"], c["cargo"])], index=c.index))]
        partes.append(c)
    l = pd.concat(partes, ignore_index=True)
    l = l[l["cpf"].str.len() == 11]
    por_ator = l.groupby("id_ator")["cpf"].nunique()
    ruins = por_ator[por_ator > 1].index
    desc["cpf_divergente"] = len(ruins)
    return l[~l["id_ator"].isin(ruins)].copy(), {**desc, "atores_cpf_divergente": sorted(ruins)}


def tcu_linhas(cpf_de: dict[str, str], nomes_de: dict[str, set[str]]) -> tuple[pd.DataFrame, dict]:
    """Linhas da lista do TCU cujo CPF é de ator ligado, no intervalo da janela; devolve também as contagens de exclusão."""
    reg = max((m for m in csv.DictReader(MANIFESTO_TCU.open(encoding="utf-8")) if m["arquivo"].endswith("tcu_contas_julgadas_irregulares.csv")),
              key=lambda m: m["data_acesso"])
    d = pd.read_csv(RAIZ / reg["arquivo"], sep="|", encoding="latin-1", dtype=str, skiprows=1)
    d.columns = [norm(c) for c in d.columns]
    col = {c.replace("/", " ").split()[0]: c for c in d.columns}
    d["cpf"] = d[col["cpf"]].map(digitos)
    d = d[d["cpf"].isin(cpf_de)].copy()
    d["id_ator"] = d["cpf"].map(cpf_de)
    confere = [norm(n) in nomes_de[c] for n, c in zip(d[col["nome"]], d["cpf"])]  # o nome da lista do TCU tem de ser o nome civil da candidatura
    nome_diverge = int((~pd.Series(confere, index=d.index)).sum())
    d = d[confere]
    d["transito"] = d[col["transito"]].map(lambda x: data_iso(x) if isinstance(x, str) and x.count("/") == 2 else "")
    n = {"nome_diverge": nome_diverge, "linhas": len(d), "sem_data": int((d["transito"] == "").sum()), "antes_2003": int(((d["transito"] != "") & (d["transito"] < INICIO_JANELA)).sum())}
    d = d[d["transito"] >= INICIO_JANELA]
    out = pd.DataFrame({"id_ator": d["id_ator"], "processo": d[col["processo"]].str.strip(), "url": d[col["link"]], "acordaos": d[col["acordaos"]], "transito": d["transito"]})
    return out.drop_duplicates(["id_ator", "processo"]), {**n, "registradas": len(out.drop_duplicates(["id_ator", "processo"]))}


def tse_linhas(ligadas: pd.DataFrame) -> pd.DataFrame:
    """Candidaturas ligadas de 2018 e 2022 com motivo do eixo 1, pela regra de D-060/D-061 (ficha limpa sempre; demais, se não atingem a lista)."""
    m = motivos()
    m["chave"] = list(zip(m["ano"], m["sq"]))
    lista = set(m.loc[m["lista"], "chave"])
    ficha = set(m.loc[m["ficha_limpa"], "chave"])
    e = m[m["eixo1"]].copy()
    e = e[[(k in ficha) or (k not in lista) for k in e["chave"]]]
    agrup = e.groupby(["ano", "sq"]).agg(motivos=("texto", lambda x: "; ".join(sorted(set(x)))), processos=("processo", lambda x: sorted(set(p for p in x if p)))).reset_index()
    l = ligadas[ligadas["ano"].isin(ANOS_MOTIVO)].copy()
    l["sq"] = l["SQ_CANDIDATO"]
    return l.merge(agrup, on=["ano", "sq"])


def montar(data: str, ids: RegistroIds, base: Path = BASE) -> dict:
    atores, cargos, inst = ler("atores", base), ler("cargos", base), ler("instituicoes", base)
    ligadas, descarte = ligar(atores, cargos, ler("filiacoes", base), Siglas(ler("denominacoes_partido", base)))
    conflitos = [{"id_ator": a} for a in descarte.pop("atores_cpf_divergente")]
    cpf_de = dict(zip(ligadas["cpf"], ligadas["id_ator"]))
    nomes_de = ligadas.assign(n=ligadas["NM_CANDIDATO"].map(norm)).groupby("cpf")["n"].agg(set).to_dict()
    tcu, cont_tcu = tcu_linhas(cpf_de, nomes_de)
    tse = tse_linhas(ligadas)
    tse_id = inst.loc[inst["sigla"] == "TSE", "id_instituicao"].iloc[0]
    tcu_id = ids.obter("instituicoes", "orgao:TCU")
    novas_inst = [{"id_instituicao": tcu_id, "nome": "Tribunal de Contas da União", "sigla": "TCU", "tipo_instituicao": "tribunal_de_contas",
                   "poder": "tribunal_de_contas", "esfera": "federal", "pais_iso3": "BRA"}]
    fontes, oficiais, fonte_de = [], [], {}

    def fonte(reg: dict, orgao: str, tipo_doc: str, titulo: str) -> str:
        arq = reg["arquivo"]
        if arq not in fonte_de:
            i = ids.obter("fontes", f"raw:{arq}")
            fonte_de[arq] = i
            fontes.append({"id_fonte": i, "tipo_fonte": "oficial", "titulo": titulo, "data_publicacao": reg["data_acesso"], "url": reg["url_base"],
                           "data_acesso": reg["data_acesso"], "sha256": reg["sha256"], "caminho_raw": arq, "licenca": "Dados públicos (Lei 12.527/2011)",
                           "observacao": "Lista pública lida pelo coletor do projeto (D-064)"})
            oficiais.append({"id_fonte": i, "id_orgao": orgao, "tipo_documento": tipo_doc, "data_documento": reg["data_acesso"], "link": reg["url_base"]})
        return fonte_de[arq]

    reg_tcu = max((m for m in csv.DictReader(MANIFESTO_TCU.open(encoding="utf-8")) if m["arquivo"].endswith("tcu_contas_julgadas_irregulares.csv")),
                  key=lambda m: m["data_acesso"])
    f_tcu = fonte(reg_tcu, tcu_id, "Lista pública de responsáveis com contas julgadas irregulares", "TCU, certidões: responsáveis com contas julgadas irregulares (lista pública)")
    processos, fases, status, auditoria = [], [], [], []
    vistos_proc = set()
    for r in tcu.itertuples():
        idp = ids.obter("processos", f"tcu:{r.processo}")
        if idp not in vistos_proc:
            vistos_proc.add(idp)
            processos.append({"id_processo": idp, "numero_originario": r.processo, "classe": "processo_tcu", "id_tribunal": tcu_id, "data_autuacao": "",
                              "assuntos_tpu": "Contas julgadas irregulares (TCU)", "url": r.url, "id_fonte": f_tcu})
            fases.append({"id_fase": ids.obter("fases_processo", f"tcu:{r.processo}:transito"), "id_processo": idp, "data": r.transito, "fase": "transito_em_julgado",
                          "id_orgao_julgador": tcu_id, "resumo": f"Trânsito em julgado do julgamento pela irregularidade das contas. Acórdãos: {r.acordaos}", "id_fonte": f_tcu})
        status.append({"id_status": ids.obter("status_pessoa_processo", f"eixo1:tcu:{r.processo}:{r.id_ator}"), "id_ator": r.id_ator, "id_processo": idp,
                       "data": r.transito, "status": "contas_julgadas_irregulares", "tipificacao": "", "id_fonte": f_tcu})
        auditoria.append({"registro": "TCU", "id_ator": r.id_ator, "processo": r.processo, "status": "contas_julgadas_irregulares", "data": r.transito, "detalhe": ""})
    for r in tse.itertuples():
        arq_motivo = arquivo(f"motivo_cassacao_{r.ano}.zip")
        f_mot = fonte(arq_motivo, tse_id, "Conjunto de dados abertos (ZIP)", f"TSE, dados abertos: {Path(arq_motivo['arquivo']).name}")
        for proc in r.processos or [f"SQ{r.sq}"]:  # 2018: o arquivo de motivos não traz o número do processo; vale o sequencial do candidato
            idp = ids.obter("processos", f"tse_rcand:{proc}")
            if idp not in vistos_proc:
                vistos_proc.add(idp)
                processos.append({"id_processo": idp, "numero_cnj": cnj(proc), "numero_originario": digitos(proc) if not proc.startswith("SQ") else f"sequencial do candidato {proc[2:]}", "classe": "registro_candidatura", "id_tribunal": tse_id,
                                  "data_autuacao": "", "assuntos_tpu": f"Registro de candidatura, eleições gerais de {r.ano}", "url": arq_motivo["url_base"], "id_fonte": f_mot})
            tip = (f"motivos no arquivo do TSE: {r.motivos}; situação da candidatura no arquivo de candidatos: {r.DS_SITUACAO_CANDIDATURA}"
                   f" ({r.DS_DETALHE_SITUACAO_CAND}); resultado: {r.DS_SIT_TOT_TURNO}. Data = eleição (o arquivo não informa a data da decisão)")
            status.append({"id_status": ids.obter("status_pessoa_processo", f"eixo1:tse:{proc}:{r.id_ator}"), "id_ator": r.id_ator, "id_processo": idp,
                           "data": r.data_eleicao, "status": "candidatura_indeferida", "tipificacao": tip, "id_fonte": f_mot})
            auditoria.append({"registro": "TSE", "id_ator": r.id_ator, "processo": proc, "status": "candidatura_indeferida", "data": r.data_eleicao,
                              "detalhe": f"{r.ano} {r.cargo}: {r.motivos}"})
    tcu_st = [{"id_status": s["id_status"], "id_ator": s["id_ator"], "data": s["data"]} for s in status if s["status"] == "contas_julgadas_irregulares"]
    tse_st = [{"id_status": s["id_status"], "id_ator": s["id_ator"], "data": s["data"]} for s in status if s["status"] == "candidatura_indeferida"]
    b1, v1, r1 = verificar(tcu_st, PADRAO_TCU, "eixo1|tcu", ids, data, SCRIPT, base)
    b2, v2, r2 = verificar(tse_st, PADRAO_TSE, "eixo1|tse", ids, data, SCRIPT, base)
    par = ler("cargos", base)
    par = par[par["cargo"].str.startswith(("Deputado", "Senador")) & ((par["data_fim"].fillna("") == "") | (par["data_fim"].fillna("") >= INICIO_JANELA))]
    alcance = {"parlamentares_base": par["id_ator"].nunique(), "parlamentares_ligados": len(set(par["id_ator"]) & set(ligadas["id_ator"])),
               "atores_ligados": ligadas["id_ator"].nunique(), "descarte_ligacao": descarte, "tcu": cont_tcu, "tse_candidaturas": len(tse)}
    return {"instituicoes": novas_inst, "fontes": fontes, "fonte_oficial": oficiais, "processos": processos, "fases_processo": fases,
            "status_pessoa_processo": status, "buscas": b1 + b2, "verificacoes_simetria": v1 + v2, "verificacao_resultado": r1 + r2,
            "auditoria": pd.DataFrame(auditoria), "alcance": alcance, "ligados": ligadas[["id_ator", "ano", "cargo", "metodo"]].sort_values(["id_ator", "ano"]), "conflitos": pd.DataFrame(conflitos)}


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
    r["auditoria"].to_csv(saida / "eixo1_registros.csv", index=False, encoding="utf-8")
    r["conflitos"].to_csv(saida / "eixo1_registros_conflitos_cpf.csv", index=False, encoding="utf-8")
    r["ligados"].to_csv(saida / "eixo1_atores_ligados.csv", index=False, encoding="utf-8")
    print(r["alcance"])
    print(r["auditoria"].groupby(["registro", "status"]).size().to_dict())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    run(ap.parse_args().data)
