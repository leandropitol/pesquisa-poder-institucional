"""Conselhos de Ética da Câmara e do Senado: representações por quebra de decoro parlamentar (D-063), de 2003 em diante.

Entradas (bruto, src.coleta.etica): representações da Câmara (proposições REP com tramitação no Conselho de Ética), processos do
Senado (REP, DEN e PCE) e os Projetos de Resolução do Senado (PRS) gerados por representações.

Unidade: a representação (processo). Por representado, na base: fase `representacao_etica` na apresentação, status
`representado` na mesma data e, quando há decisão nas fontes, um status final:
- `mandato_cassado`: perda de mandato declarada pelo plenário (Resolução da Câmara; PRS aprovado no Senado);
- `sancao_disciplinar`: suspensão de mandato ou censura aprovada;
- `representacao_improcedente`: plenário rejeita o parecer pela perda do mandato ou aprova o parecer pela improcedência (Senado:
  PRS de perda de mandato rejeitado);
- `arquivado`: arquivamento sem decisão de mérito (fim de legislatura, prejudicialidade, inépcia, retirada, indeferimento inicial).
Sem decisão nas fontes, não há status final (ausência registrada como ausência).

Representado: nome extraído da ementa (parte que segue "contra", "em face", "em desfavor") e ligado a parlamentar da base com
mandato na Casa na data (ou até 180 dias antes) por nome normalizado igual, com o nome mais longo prevalecendo; sem ligação
única, o registro fica na lista de não ligados (relatorios/tabelas/etica_nao_ligados.csv) e nas decisões manuais de
data/curadoria/etica_representados.csv.

Uso:
    python -m src.normalizacao.etica
"""

import json
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, ler

RAW = RAIZ / "data" / "raw" / "etica"
CAMARA_ORGAOS = {"COETICA", "CEDPA"}
MARCADOR_ALVO = re.compile(r"\b(contra|em face|em desfavor|em rela[çc][ãa]o (?:a|ao|aos|à|às)|em desfavor)\b", re.I)


def norm(s: str) -> str:
    t = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii").lower()
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", t).split())


def lerjsonl(caminho: Path):
    for linha in caminho.open(encoding="utf-8"):
        yield json.loads(linha)


# ------------------------------------------------------------------ representado
HONORIFICOS = {"dr", "dra", "doutor", "doutora", "professor", "professora", "prof", "delegado", "delegada", "pastor", "pastora", "coronel",
               "capitao", "major", "sargento", "cabo", "general", "juiz", "juiza", "padre", "bispo", "tenente", "comandante", "cel",
               "irmao", "irma", "mestre", "mae", "tio", "tia", "vereador", "seu", "dona"}
SUFIXOS = {"junior", "filho", "neto", "sobrinho", "segundo", "jr"}
LIGACOES = {"de", "da", "do", "dos", "das", "e"}


def chaves_do_nome(nome: str) -> set[str]:
    """Formas do nome parlamentar: completa, sem título (Dr., Professor, Coronel...) e sem sufixo (Junior, Filho, Neto)."""
    t = norm(nome).split()
    sem_titulo = t[1:] if t and t[0] in HONORIFICOS else t
    sem_sufixo = sem_titulo[:-1] if len(sem_titulo) > 2 and sem_titulo[-1] in SUFIXOS else sem_titulo
    return {" ".join(x) for x in (t, sem_titulo, sem_sufixo) if len(x) >= 2}


@dataclass
class Parlamentares:
    """Mandatos (id_ator, casa, início, fim, formas do nome) para achar quem era parlamentar da Casa na data."""

    mandatos: list = field(default_factory=list)

    @classmethod
    def da_base(cls, base: Path = BASE) -> "Parlamentares":
        atores, cargos = ler("atores", base), ler("cargos", base)
        nome = dict(zip(atores["id_ator"], atores["nome"]))
        p = cls()
        for c in cargos.itertuples():
            casa = "CD" if c.cargo.startswith("Deputado") else "SF" if c.cargo.startswith("Senador") else None
            if casa and c.id_ator in nome:
                p.mandatos.append((c.id_ator, casa, c.data_inicio, c.data_fim or "9999-12-31", chaves_do_nome(nome[c.id_ator]),
                                   [x for x in norm(nome[c.id_ator]).split() if x not in HONORIFICOS | SUFIXOS]))
        return p

    def ativos(self, casa: str, data: str):
        limite = (date.fromisoformat(data) - timedelta(days=180)).isoformat()
        return [m for m in self.mandatos if m[1] == casa and m[2] <= data and m[3] >= limite]


def trecho_alvo(ementa: str) -> str:
    """Parte da ementa depois do primeiro marcador de alvo; sem marcador, a ementa inteira."""
    m = MARCADOR_ALVO.search(ementa or "")
    return ementa[m.end():] if m else ementa or ""


def subsequencia(tokens_nome: list[str], texto: list[str], janela: int = 8) -> bool:
    """Todas as palavras do nome parlamentar (sem título) aparecem no texto, na mesma ordem, dentro de uma janela curta:
    "Paulo Rocha" em "Paulo Roberto Galvão da Rocha"; não casa "Paulo Roberto Pereira" em "Paulo Pereira da Silva"."""
    if len(tokens_nome) < 2:
        return False
    for i, t in enumerate(texto):
        if t != tokens_nome[0]:
            continue
        pos = i
        for x in tokens_nome[1:]:
            achou = next((j for j in range(pos + 1, min(pos + janela, len(texto))) if texto[j] == x), None)
            if achou is None:
                break
            pos = achou
        else:
            return True
    return False


def representados(ementa: str, casa: str, data: str, parl: Parlamentares) -> tuple[list[tuple[str, str]], list[str]]:
    """([(id_ator, método)], nomes ambíguos). Método `nome`: forma do nome contida na ementa (a mais longa prevalece);
    `subsequencia`: só se nada foi achado, todas as palavras do nome parlamentar na ordem, dentro de uma janela curta, com correspondência única entre os parlamentares da Casa na data."""
    texto_l = norm(trecho_alvo(ementa)).split()
    texto = " " + " ".join(texto_l) + " "
    ativos = parl.ativos(casa, data)
    por_chave: dict[str, set] = defaultdict(set)
    for a, _c, _i, _f, chaves, _t in ativos:
        for k in chaves:
            if f" {k} " in texto:
                por_chave[k].add(a)
    chaves = [k for k in por_chave if not any(k != o and k in o for o in por_chave)]
    ligados = sorted({(next(iter(por_chave[k])), "nome") for k in chaves if len(por_chave[k]) == 1})
    ambiguos = sorted(k for k in chaves if len(por_chave[k]) > 1)
    if not chaves:
        achados = {m[0] for m in ativos if subsequencia(m[5], texto_l)}
        if len(achados) == 1:
            ligados = [(next(iter(achados)), "subsequencia")]
        elif achados:
            ambiguos = ["subsequencia:" + ";".join(sorted(achados))]
    return ligados, ambiguos


# ------------------------------------------------------------------ desfecho na Câmara
REGRAS_CAMARA = [  # (status, expressão sobre o despacho, órgão exigido ou None, descrição); vale o último evento decisivo
    ("mandato_cassado", r"Promulgada a Resolu[çc][ãa]o.{0,80}perda d", None, "perda do mandato declarada pelo Plenário (Resolução da Câmara)"),
    ("mandato_cassado", r"Aprovad[oa] o Parecer do Conselho de [ÉE]tica.{0,200}(perda do mandato|cassa)", "PLEN", "Plenário aprovou o parecer pela perda do mandato"),
    ("representacao_improcedente", r"Rejeitad[oa] o Parecer do Conselho de [ÉE]tica.{0,200}(perda|cassa)", "PLEN", "Plenário rejeitou o parecer pela perda do mandato"),
    ("representacao_improcedente", r"Aprovad[oa] o Parecer.{0,200}improced[êe]ncia", "PLEN", "Plenário aprovou o parecer pela improcedência"),
    ("sancao_disciplinar", r"Aprovad[oa].{0,120}(suspens[ãa]o (?:temporária )?d[oe]s? (?:mandato|exerc[íi]cio|prerrogativas)|pena de censura)", None, "suspensão de mandato ou censura aprovada"),
]
ARQUIVO = re.compile(r"\barquiv", re.I)
NAO_ARQUIVO = re.compile(r"desarquiv|Requerimento|REQ |Ofício|Recurso|REC \d", re.I)
MOTIVOS_ARQUIVO = [("inépcia", r"inépcia|inepta"), ("prejudicada", r"prejudic"), ("improcedência (parecer aprovado)", r"improced"),
                   ("fim da legislatura", r"art\. 105|t[ée]rmino da legislatura|fim da legislatura"), ("retirada pelo autor", r"retirad"),
                   ("renúncia ao mandato", r"ren[úu]ncia"), ("perda de objeto", r"perda de objeto|perdeu o objeto")]


def motivo_arquivo(texto: str) -> str:
    return next((m for m, rx in MOTIVOS_ARQUIVO if re.search(rx, texto, re.I)), "arquivada")


def resumo(t: str, n: int = 220) -> str:
    return re.sub(r"\s+", " ", t).strip()[:n]


def desfecho_camara(eventos: list[dict], situacao: str | None) -> dict | None:
    """Último evento decisivo. Decisão de mérito (cassação, sanção, improcedência) vale mais que arquivamento posterior."""
    ev = sorted(eventos, key=lambda e: (e["dataHora"], e.get("sequencia") or 0))
    merito, arquivo = None, None
    for e in ev:
        t = re.sub(r"\s+", " ", e.get("despacho") or "")
        for status, rx, orgao, desc in REGRAS_CAMARA:
            if re.search(rx, t, re.I) and (orgao is None or e.get("siglaOrgao") == orgao):
                merito = {"status": status, "data": e["dataHora"][:10], "tipificacao": desc, "evidencia": resumo(t), "orgao": e.get("siglaOrgao")}
                break
        else:
            if ARQUIVO.search(t) and not NAO_ARQUIVO.search(t) and e.get("siglaOrgao") in ("MESA", "PLEN", "COETICA", "CEDPA", "CCJC", "SGM", "DEPRO"):
                arquivo = {"status": "arquivado", "data": e["dataHora"][:10], "tipificacao": motivo_arquivo(t), "evidencia": resumo(t), "orgao": e.get("siglaOrgao")}
    if merito:
        return merito
    if arquivo:
        return arquivo
    if situacao in ("Arquivada", "Retirado pelo(a) Autor(a)"):
        return {"status": "arquivado", "data": ev[-1]["dataHora"][:10], "tipificacao": f"situação na fonte: {situacao}", "evidencia": f"situação: {situacao}", "orgao": ""}
    return None


def pareceres_camara(eventos: list[dict]) -> list[dict]:
    """Fases de parecer do Conselho e de deliberação do plenário, com o texto do despacho."""
    fases, vistos = [], set()
    for e in sorted(eventos, key=lambda e: (e["dataHora"], e.get("sequencia") or 0)):
        t = re.sub(r"\s+", " ", e.get("despacho") or "")
        org = e.get("siglaOrgao")
        fase = None
        if org in CAMARA_ORGAOS and re.search(r"^(Aprovado|Rejeitado)[a-z]* .{0,60}[Pp]arecer|Parecer d[oa]s? Relator", t):
            fase = "parecer_conselho_etica"
        elif org == "PLEN" and re.search(r"^(Aprovad[oa]|Rejeitad[oa]) .{0,80}([Pp]arecer|Representa[çc][ãa]o)", t):
            fase = "deliberacao_plenario"
        if fase and (fase, e["dataHora"][:10], t[:60]) not in vistos:
            vistos.add((fase, e["dataHora"][:10], t[:60]))
            fases.append({"fase": fase, "data": e["dataHora"][:10], "resumo": resumo(t), "orgao": org})
    return fases


# ------------------------------------------------------------------ carga do bruto
PASTA_REP, PASTA_PRS = "2026-09-29-b", "2026-09-29-c"
CUR = RAIZ / "data" / "curadoria"
EMENTA_ETICA = re.compile(r"decoro|disciplinar|cassa[çc]|perda de mandato", re.I)
SITUACAO_SENADO_ARQUIVO = {"ARQUIVADA": "arquivada", "INDEFERIDA": "indeferida pelo Presidente do Conselho", "REJEITADA": "rejeitada",
                           "PREJUDICADA": "prejudicada"}


def url_camara(i: int) -> str:
    return f"https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao={i}"


def url_senado(codigo: int) -> str:
    return f"https://www25.senado.leg.br/web/atividade/materias/-/materia/{codigo}"


def carregar_camara() -> list[dict]:
    pasta = RAW / PASTA_REP
    det = {r["corpo"]["dados"]["id"]: r["corpo"]["dados"] for r in lerjsonl(pasta / "camara_rep_detalhe.jsonl")}
    tr = {r["params"]["id"]: (r["corpo"]["dados"] if r["corpo"] else []) for r in lerjsonl(pasta / "camara_rep_tramitacoes.jsonl")}
    saida = []
    for i, ev in tr.items():
        if not any(e.get("siglaOrgao") in CAMARA_ORGAOS or "COETICA" in (e.get("despacho") or "") for e in ev):
            continue
        d = det[i]
        saida.append({"casa": "CD", "chave": f"REP {d['numero']}/{d['ano']}", "id_api": i, "data": d["dataApresentacao"][:10], "ementa": d["ementa"],
                      "url": url_camara(i), "eventos": ev, "situacao": (d.get("statusProposicao") or {}).get("descricaoSituacao")})
    return sorted(saida, key=lambda p: (p["data"], p["chave"]))


def carregar_senado() -> list[dict]:
    pasta = RAW / PASTA_REP
    lista = {}
    for r in lerjsonl(pasta / "senado_rep_por_ano.jsonl"):
        for p in r["corpo"] or []:
            lista[p["id"]] = p
    det = {r["corpo"]["id"]: r["corpo"] for r in lerjsonl(pasta / "senado_rep_detalhe.jsonl")}
    prs = {}
    for r in lerjsonl(RAW / PASTA_PRS / "senado_prs_detalhe.jsonl"):
        prs[r["params"]["origem"]] = r["corpo"]
    saida = []
    for i, p in lista.items():
        if not EMENTA_ETICA.search(p["ementa"]):
            continue
        d = det[i]
        saida.append({"casa": "SF", "chave": p["identificacao"], "id_api": i, "data": p["dataApresentacao"], "ementa": p["ementa"],
                      "url": url_senado(p["codigoMateria"]), "situacao": (d.get("situacaoAtual") or "").strip(),
                      "data_situacao": d.get("dataSituacaoAtual") or "", "deliberacao": d.get("deliberacao") or {}, "prs": prs.get(p["identificacao"])})
    return sorted(saida, key=lambda p: (p["data"], p["chave"]))


def ler_csv(nome: str) -> list[dict]:
    import csv

    arq = CUR / nome
    return list(csv.DictReader(arq.open(encoding="utf-8"))) if arq.exists() else []


# ------------------------------------------------------------------ representados (automático + curadoria)
def resolver_representados(processos: list[dict], parl: Parlamentares) -> tuple[dict, list[dict]]:
    """(casa, chave) -> [(id_ator, método)]; lista de não ligados. A curadoria (etica_representados.csv) substitui o automático."""
    manual = defaultdict(list)
    for r in ler_csv("etica_representados.csv"):
        manual[(r["casa"], r["processo"])].append(r)
    por_processo, nao = {}, []
    for p in processos:
        ch = (p["casa"], p["chave"])
        if ch in manual:
            ids = [(r["id_ator"], "curadoria") for r in manual[ch] if r["id_ator"].startswith("ATR-")]
            for r in manual[ch]:  # a curadoria só vale se o ator tinha mandato na Casa na data
                if r["id_ator"].startswith("ATR-") and not any(m[0] == r["id_ator"] for m in parl.ativos(p["casa"], p["data"])):
                    raise ValueError(f"{ch}: {r['id_ator']} sem mandato na Casa em {p['data']}")
            por_processo[ch] = ids
            if not ids:
                nao.append({"casa": p["casa"], "processo": p["chave"], "motivo": manual[ch][0]["motivo"], "ementa": resumo(p["ementa"], 200)})
            continue
        lig, amb = representados(p["ementa"], p["casa"], p["data"], parl)
        por_processo[ch] = lig
        if not lig or amb:
            nao.append({"casa": p["casa"], "processo": p["chave"], "motivo": ("ambíguo: " + "; ".join(amb)) if amb else "sem parlamentar da Casa achado na ementa",
                        "ementa": resumo(p["ementa"], 200)})
    return por_processo, nao


def nomeado(ator: str, texto: str, parl: Parlamentares) -> bool:
    """O nome parlamentar do ator aparece no texto (usado para atribuir decisão a um representado em processo com vários)."""
    t = " " + norm(texto) + " "
    mand = next((m for m in parl.mandatos if m[0] == ator), None)
    return bool(mand) and (any(f" {k} " in t for k in mand[4]) or subsequencia(mand[5], norm(texto).split()))


DELIBERACAO_SENADO_ARQUIVO = ("Indeferida pelo Conselho de Ética", "Inadmitida a Denúncia", "Arquivada por inépcia da inicial", "Arquivada ao final da Legislatura")


def desfecho_senado(p: dict) -> dict | None:
    """Estruturado: PRS gerado pela representação (plenário), deliberação do Conselho ou situação final; o restante fica sem desfecho."""
    prs, delib = p["prs"], p["deliberacao"]
    if prs:
        d = prs.get("deliberacao") or {}
        if d.get("siglaTipo") == "APROVADA_NO_PLENARIO":
            return {"status": "mandato_cassado", "data": d["data"], "tipificacao": f"{prs['identificacao']} aprovado pelo Plenário do Senado", "evidencia": f"{prs['identificacao']}: {d.get('tipoDeliberacao')}"}
        if d.get("siglaTipo") == "REJEITADO_PLENARIO":
            return {"status": "representacao_improcedente", "data": d["data"], "tipificacao": f"{prs['identificacao']} (perda do mandato) rejeitado pelo Plenário do Senado",
                    "evidencia": f"{prs['identificacao']}: {d.get('tipoDeliberacao')}"}
    if any((delib.get("tipoDeliberacao") or "").startswith(x) for x in DELIBERACAO_SENADO_ARQUIVO) and delib.get("data"):
        return {"status": "arquivado", "data": delib["data"], "tipificacao": delib["tipoDeliberacao"], "evidencia": f"deliberação: {delib['tipoDeliberacao']}"}
    if p["situacao"] in SITUACAO_SENADO_ARQUIVO and p["data_situacao"]:
        return {"status": "arquivado", "data": p["data_situacao"], "tipificacao": SITUACAO_SENADO_ARQUIVO[p["situacao"]], "evidencia": f"situação: {p['situacao']}"}
    return None
