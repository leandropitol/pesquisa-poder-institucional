"""Desfechos das ações penais originárias do STF para parlamentares da base (eixo 1, D-065).

Fonte: decisões das ações penais na exportação do Corte Aberta (data/raw/stf/2026-09-24), texto oficial do dispositivo.

Eventos lidos (coluna "Andamento decisão"): Procedente e Procedente em parte -> `condenado_tribunal_superior`; Improcedente -> `absolvido`;
Declarada a extinção da punibilidade -> `punibilidade_extinta` ou `prescrito`, pelo texto.

Quem recebe o status:
- ação com um só réu na lista do portal e texto sem marcador de vários réus: o réu ligado ao parlamentar (regra automática);
- ação com mais de um réu, ou lista incompleta: só linha curada em data/curadoria/stf_desfechos_reus.csv, com o trecho citado conferido no texto;
- extinção da punibilidade: só se o texto traz a causa (morte, prescrição, cumprimento de acordo) e não nomeia outra pessoa; textos sem conteúdo
  ("EM 27/02/2014", "*NI*") ficam nos pendentes.

Vínculo réu -> ator (mais rígido que o da simetria, porque aqui o status vai para a pessoa): vale o nome civil igual ao da candidatura do TSE
ligada ao ator (D-064); ou ligação curada `aceita` / da E9, desde que o réu não tenha sufixo (Júnior, Filho, Neto) que o nome do ator não tem.
`automatica` e `aceita_a_conferir` sem confirmação pelo nome civil ficam nos pendentes.

Saídas: base (status_pessoa_processo); relatorios/tabelas/stf_desfechos.csv (auditoria) e stf_desfechos_pendentes.csv.

Uso:
    python -m src.normalizacao.stf_desfechos
"""

import csv
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, acrescentar, ler
from src.normalizacao.eixo1_registros import ligar
from src.normalizacao.simetria_stf import SUFIXOS, carregar, relatorios
from src.normalizacao.tse import norm
from src.simetria.governo_oposicao import Siglas

CUR = RAIZ / "data" / "curadoria"
DECISOES = RAIZ / "data" / "raw" / "stf" / "2026-09-24" / "stf_corte_aberta_decisoes_AP_Inq_2003-01-08_a_2026-09-23.xlsx"
FORA = {"AP 470", "AP 536"}  # carregadas pela E9 (D-046)
MERITO = {"Procedente": "condenado_tribunal_superior", "Procedente em parte": "condenado_tribunal_superior", "Improcedente": "absolvido"}
EXTINCAO = "Declarada a extinção da punibilidade"
PLURAL = re.compile(r"\b(os|as) (r[ée]us|r[ée]s|acusad|denunciad|querelad)|desmembr|\br[ée]us\b|\bcorr[ée]us\b", re.I)
NOME_OUTRO = re.compile(r"(?:R[ÉE]U|R[ÉE]|ACUSAD[OA]|DENUNCIAD[OA]|QUERELAD[OA]|SENTENCIAD[OA]|INVESTIGAD[OA])\s+((?:[A-ZÀ-Ú][\wÀ-ú]+\s?){2,5})", re.I)
CAUSA = [("morte do agente (art. 107, I, CP)", re.compile(r"[óo]bito|falecimento|art\. ?107,? ?(?:inciso )?I\b(?!V)", re.I), "punibilidade_extinta"),
         ("prescrição da pretensão punitiva", re.compile(r"prescri[çc]", re.I), "prescrito"),
         ("cumprimento de acordo de não persecução penal", re.compile(r"acordo de n[ãa]o persecu", re.I), "punibilidade_extinta")]
PARCIAL = re.compile(r"no que concerne|quanto (?:ao|aos|[àa]s?) (?:crime|delito|infra)|em rela[çc][ãa]o (?:ao|aos|[àa]s?) (?:crime|delito|infra)", re.I)
SCRIPT = "src.normalizacao.stf_desfechos"


def limpo(t: str) -> str:
    return " ".join(re.sub(r"_x000D_", " ", str(t)).split())


def formas(nome: str) -> set[str]:
    """Formas do nome de réu no portal: separa 'A OU B' e tira apelido entre parênteses."""
    return {norm(re.sub(r"\(.*?\)", "", f)) for f in re.split(r"\s+OU\s+", nome)}


def eventos() -> pd.DataFrame:
    d = pd.read_excel(DECISOES, dtype=str)
    d = d[d["Processo"].str.startswith("AP ")]
    d = d[d["Andamento decisão"].isin(list(MERITO) + [EXTINCAO])].copy()
    d = d.rename(columns={"Andamento decisão": "andamento", "Assuntos do processo": "assunto"})
    d["data"] = d["Data da decisão"].str[:10]
    d["texto"] = d["Observação do andamento"].map(limpo)
    return d.sort_values(["Processo", "data"])


def reus_por_ap() -> dict[str, list[str]]:
    """Todas as linhas de réu do portal por ação, inclusive as que não são pessoa (para contar réus)."""
    saida: dict[str, list[str]] = defaultdict(list)
    for f in relatorios():
        for l in f.read_text(encoding="utf-8").splitlines():
            if re.match(r"^\| \d+ \|", l):
                c = [x.strip() for x in l.split("|")[1:-1]]
                saida[f"AP {c[0]}"].append(c[2])
    return saida


def nomes_civis(atores, cargos, filiacoes, base) -> dict[str, set[str]]:
    lig, _ = ligar(atores, cargos, filiacoes, Siglas(ler("denominacoes_partido", base)))
    return lig.assign(n=lig["NM_CANDIDATO"].map(norm)).groupby("id_ator")["n"].agg(set).to_dict()


def vinculo(nome_reu: str, ator: str, decisao: str, nome_ator: str, civ: dict) -> str:
    """'civil', 'curada' ou '' (não serve)."""
    fs = formas(nome_reu)
    if fs & civ.get(ator, set()):
        return "civil"
    sufixo = any(t in SUFIXOS for f in fs for t in f.split()) and not any(t in SUFIXOS for t in nome_ator.split())
    if sufixo:
        return ""
    return "curada" if decisao == "aceita" or decisao.startswith("e9:") else ""


def classificar_extincao(texto: str, nome_reu: str) -> tuple[str, str] | None:
    """(status, causa) se o texto traz causa e não nomeia outra pessoa."""
    for m in NOME_OUTRO.finditer(texto):
        toks = {t for t in norm(m.group(1)).split() if len(t) > 3}
        if toks and not toks & {t for t in norm(nome_reu).split() if len(t) > 3}:
            return None
    for causa, rx, status in CAUSA:
        if rx.search(texto):
            return status, causa
    return None


def montar(data: str, ids: RegistroIds, base: Path = BASE) -> dict:
    c = carregar()
    lig, lista, proc = c["lig"], c["lista"], c["proc"]
    atores, cargos, filiacoes = c["atores"], c["cargos"], c["filiacoes"]
    nome_ator = dict(zip(atores["id_ator"], atores["nome_normalizado"]))
    civ = nomes_civis(ler("atores", base), ler("cargos", base), ler("filiacoes", base), base)
    id_proc = dict(zip(proc["numero_originario"], proc["id_processo"]))
    ev, reus = eventos(), reus_por_ap()
    por_ap = defaultdict(list)
    for (ap, nome), v in lig.items():
        por_ap[ap].append((nome, v))
    fonte = "FNT-000046"
    existentes = {(a, p, s) for a, p, s in zip(ler("status_pessoa_processo", base)["id_ator"], ler("status_pessoa_processo", base)["id_processo"], ler("status_pessoa_processo", base)["status"])}
    status, auditoria, pendentes = [], [], []

    ja = set(ler("status_pessoa_processo", base)["id_status"])

    def registrar(ap, ator, st, dt, tip, evidencia, origem, vinc, nome_reu):
        idp = id_proc[ap]
        i = ids.obter("status_pessoa_processo", f"stf_desfecho:{ap}:{ator}:{st}:{dt}")
        if i not in ja:
            if (ator, idp, st) in existentes:  # já registrado por outra fonte (E9): não duplica
                return
            existentes.add((ator, idp, st))
            status.append({"id_status": i, "id_ator": ator, "id_processo": idp, "data": dt, "status": st, "tipificacao": tip, "id_fonte": fonte})
        auditoria.append({"ap": ap, "id_ator": ator, "status": st, "data": dt, "origem": origem, "vinculo": vinc, "nome_no_portal": nome_reu,
                          "tipificacao": tip, "evidencia": evidencia[:300]})

    def pendente(ap, dt, andamento, motivo, ator=""):
        pendentes.append({"ap": ap, "data": dt, "andamento": andamento, "id_ator": ator, "motivo": motivo})

    curadas = defaultdict(list)
    for r in csv.DictReader((CUR / "stf_desfechos_reus.csv").open(encoding="utf-8")):
        curadas[r["ap"]].append(r)
    textos = defaultdict(dict)
    for r in ev.itertuples():
        textos[r.Processo][r.data] = textos[r.Processo].get(r.data, "") + " " + r.texto
    for ap, lista_c in curadas.items():
        for r in lista_c:
            t = " ".join(textos[ap].get(r["data"], "").split())
            if " ".join(r["trecho"].split()) not in t:
                raise ValueError(f"trecho não encontrado em {ap} de {r['data']}: {r['trecho'][:70]}")
            ligs = [(n, v) for n, vs in por_ap[ap] for v in vs if v[0] == r["id_ator"]]
            if r["vinculo_manual"]:
                registrar(ap, r["id_ator"], r["status"], r["data"], r["tipificacao"], r["trecho"], "curadoria", "manual: " + r["vinculo_manual"][:120], "")
                continue
            ok = next(((n, vinculo(n, r["id_ator"], v[1], nome_ator[r["id_ator"]], civ), v[1]) for n, v in ligs if vinculo(n, r["id_ator"], v[1], nome_ator[r["id_ator"]], civ)), None)
            if ok:
                registrar(ap, r["id_ator"], r["status"], r["data"], r["tipificacao"], r["trecho"], "curadoria", ok[1], ok[0])
            else:
                pendente(ap, r["data"], r["status"], "vínculo do réu com o ator sem confirmação pelo nome civil", r["id_ator"])
    for r in ev.itertuples():
        ap, dt, andam, texto = r.Processo, r.data, r.andamento, r.texto
        if ap in FORA or ap not in por_ap or ap in curadas or ap not in id_proc:
            continue
        nomes = reus.get(ap, [])
        if len(nomes) != 1 or PLURAL.search(texto):
            pendente(ap, dt, andam, "mais de um réu na lista do portal ou no texto, sem linha curada")
            continue
        if len(por_ap[ap]) != 1:
            pendente(ap, dt, andam, "mais de um réu ligado a parlamentar, sem linha curada")
            continue
        nome_reu, ligs = por_ap[ap][0]
        if nome_reu != nomes[0]:
            pendente(ap, dt, andam, "réu ligado não é o único da lista")
            continue
        assunto = f"assunto no STF: {r.assunto}" if andam in MERITO else ""
        nota = " (o julgamento também tratou de prescrição ou extinção da punibilidade de parte das imputações)" if andam in MERITO and re.search(r"prescri|extint", texto, re.I) else ""
        if andam in MERITO:
            st, tip = MERITO[andam], (assunto + nota)[:400]
        else:
            k = classificar_extincao(texto, nome_reu)
            if not k:
                pendente(ap, dt, andam, "texto da decisão sem causa identificável ou sem o nome do réu")
                continue
            st, tip = k[0], k[1]
            if PARCIAL.search(texto):
                tip += " (em relação a parte das imputações; ver decisão)"
        for ator, decisao in ligs:
            v = vinculo(nome_reu, ator, decisao, nome_ator[ator], civ)
            if v:
                registrar(ap, ator, st, dt, tip, texto, "regra", v, nome_reu)
            else:
                pendente(ap, dt, andam, f"vínculo réu-ator sem confirmação ({decisao})", ator)
    return {"status": status, "auditoria": pd.DataFrame(auditoria), "pendentes": pd.DataFrame(pendentes).drop_duplicates()}


def run(data: str) -> None:
    ids = RegistroIds()
    r = montar(data, ids)
    acrescentar("status_pessoa_processo", r["status"])
    ids.salvar()
    saida = RAIZ / "relatorios" / "tabelas"
    r["auditoria"].to_csv(saida / "stf_desfechos.csv", index=False, encoding="utf-8")
    r["pendentes"].to_csv(saida / "stf_desfechos_pendentes.csv", index=False, encoding="utf-8")
    print(f"status novos: {len(r['status'])}; na auditoria: {len(r['auditoria'])}", r["auditoria"]["status"].value_counts().to_dict())
    print(r["auditoria"]["origem"].value_counts().to_dict(), r["auditoria"]["vinculo"].str[:6].value_counts().to_dict())
    print(f"pendentes: {len(r['pendentes'])}", r["pendentes"]["motivo"].value_counts().to_dict())


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="2026-09-30")
    run(ap.parse_args().data)
