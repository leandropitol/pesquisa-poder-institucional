"""Verificação de simetria dos status da E9 contra as ações penais do STF julgadas no mérito (D-007, D-048).

Entradas:
- o relatório de navegação com os réus da aba Partes (bruto, lote 1: 99 ações julgadas no mérito);
- data/curadoria/simetria_stf_ap_lista.csv (datas de autuação e de julgamento, resultado);
- data/curadoria/simetria_stf_ap_ligacoes.csv: decisões sobre a ligação réu -> parlamentar da base
  (aceita, aceita_a_conferir, rejeitada, pendente), com motivo;
- data/curadoria/e9_ap470_reus.csv: ligações da AP 470, já decididas na E9.

Ligação automática (sem decisão na curadoria): parlamentar com mandato entre a autuação e o último julgamento de
mérito (ou a última decisão, na ação sem julgamento de mérito), com nome igual ao da aba Partes, ou com todas as palavras do nome parlamentar (pelo menos duas) no nome
civil, correspondência única, e com o primeiro e o último nome coincidentes. Correspondência mais fraca só entra
por decisão na curadoria; sem decisão, fica pendente e é contada.

Partido: filiação do réu na data do primeiro julgamento de mérito; sem filiação vigente, a última iniciada antes.

Para cada status da E9 que exige simetria (réu e denunciado ficam para quando todos os lotes forem lidos, porque o
lote 1 só tem ações julgadas no mérito), grava uma verificação com um resultado por partido do universo do ano.
Contam as ações com assunto do eixo 1 pela regra da E5 e com condenação de ao menos um réu: `encontrado` (ações
com réu parlamentar do partido), `sem_evidencia` (busca registrada com zero resultados) ou, quando o partido só
tem ações de assunto "revisar" na regra da E5, `nao_verificado` com a lista dessas ações.
Governo e oposição ficam `nao_verificado`: a base não tem a composição da base do governo por data. Status em
tribunal estadual (AP 536 no TJMG) não tem universo lido e fica `nao_verificado` para todos os grupos.

Uso:
    python -m src.normalizacao.simetria_stf
"""

import csv
import datetime as dt
import json
import re
from collections import defaultdict

import pandas as pd

from src.base import RAIZ, RegistroIds, acrescentar, ler
from src.coleta.comum import sha256
from src.normalizacao.stf import universo as universo_stf
from src.normalizacao.tse import PALAVRAS_VAZIAS, norm, palavras
from src.validacao.validar import STATUS_COM_SIMETRIA

CUR = RAIZ / "data" / "curadoria"
RAW_STF = RAIZ / "data" / "raw" / "stf"
NAO_PESSOA = re.compile(r"^(MINIST[ÉE]RIO P[ÚU]BLICO|OS MESMOS$)")
SCRIPT = "src.normalizacao.simetria_stf"
FONTE_DADOS = "STF, portal (aba Partes) e Corte Aberta (decisões)"
STATUS_ADIADOS = {"reu", "denunciado"}
SUFIXOS = {"filho", "junior", "neto", "sobrinho"}
CONDENACAO = ("Procedente", "Procedente em parte")
PADRAO = ("Ação penal originária no STF, com assunto do eixo 1 pela regra da E5, julgada por órgão colegiado com condenação de "
          "ao menos um réu (andamento Procedente ou Procedente em parte no Corte Aberta; o resultado por réu não foi lido), 2003 a "
          "2026, com réu que é parlamentar federal da base; partido = filiação do réu na data do primeiro julgamento de mérito "
          "(D-048, lote 1 de 99 ações julgadas no mérito)")
SEM_GOVERNO = "A base não tem a composição da base do governo e da oposição por data; grupo não verificado"
SEM_UNIVERSO = ("Status em tribunal estadual (TJMG): não há universo lido de ações penais estaduais com réu parlamentar para "
                "comparar partidos (D-048)")


def relatorios() -> list:
    return sorted(RAW_STF.glob("*/stf_relatorio_navegacao_partes_ap_lote*.md"))


def so_iniciais(nome: str) -> bool:
    """Nome abreviado em processo sigiloso: só letras soltas, com ou sem pontos e conectivos ("J. A. G. C.", "N.R.C.",
    "C DE L F"), ou uma sigla curta ("PSM")."""
    partes = nome.split()
    letras = [x for x in re.split(r"[\s.]+", nome) if x and x.lower() not in {"de", "da", "do", "das", "dos"}]
    return all(len(x) <= 1 for x in letras) or (len(partes) == 1 and len(partes[0].strip(".")) <= 4)


def ler_reus() -> list[dict]:
    """Réus de todos os lotes lidos. Fica de fora o que não é nome de pessoa: órgão do Ministério Público no campo de
    réu, o texto "OS MESMOS" e nomes só com iniciais (processos em segredo de justiça)."""
    saida = []
    for f in relatorios():
        for l in f.read_text(encoding="utf-8").splitlines():
            if re.match(r"^\| \d+ \|", l):
                c = [x.strip() for x in l.split("|")[1:-1]]
                if c[2] and not NAO_PESSOA.match(c[2]) and not so_iniciais(c[2]):
                    saida.append({"ap": f"AP {c[0]}", "incidente": c[1], "nome": c[2]})
    return saida


def sig(nome: str) -> list[str]:
    return [p.strip(".") for p in norm(nome).split() if p.strip(".") not in PALAVRAS_VAZIAS | SUFIXOS]


def propor(reus: list[dict], lista: pd.DataFrame, atores: pd.DataFrame, cargos: pd.DataFrame) -> list[dict]:
    """Ligações automáticas fortes e candidatas fracas (a decidir na curadoria)."""
    nome = dict(zip(atores["id_ator"], atores["nome_normalizado"]))
    parl = cargos[cargos["cargo"].str.startswith(("Deputado", "Senador"))]
    saida = []
    for r in reus:
        l = lista.loc[r["ap"]]
        fim = l["data_ultimo_julgamento"] or l["data_ultima_decisao"]  # ação sem julgamento de mérito: última decisão
        c = parl[(parl["data_inicio"] <= fim) & ((parl["data_fim"] == "") | (parl["data_fim"] >= l["data_autuacao"]))]
        ok = set(c["id_ator"])
        formas = [v.strip() for v in re.split(r"\s+OU\s+", r["nome"])]
        iguais = {a for a in ok if nome[a] in {norm(v) for v in formas}}
        contidos = {a for a in ok if len(palavras(nome[a])) >= 2 and any(palavras(nome[a]) <= palavras(v) for v in formas)}
        achados = iguais if len(iguais) == 1 else contidos
        for a in achados:
            forte = len(achados) == 1 and (a in iguais or any(sig(nome[a])[:1] == sig(v)[:1] and sig(nome[a])[-1:] == sig(v)[-1:] for v in formas))
            saida.append({**r, "id_ator": a, "forte": forte})
    repetidos = pd.Series([(x["ap"], x["id_ator"]) for x in saida]).value_counts()
    for x in saida:  # dois réus da mesma ação com o mesmo parlamentar: nenhum fica automático
        if repetidos[(x["ap"], x["id_ator"])] > 1:
            x["forte"] = False
    return saida


def ligacoes(reus: list[dict], propostas: list[dict]) -> tuple[dict, dict]:
    """(ap, nome) -> [(id_ator, decisão)] e contagem de pendências."""
    cur = defaultdict(list)
    for c in csv.DictReader((CUR / "simetria_stf_ap_ligacoes.csv").open(encoding="utf-8")):
        cur[(f"AP {c['ap']}", c["nome_partes"])].append(c)
    lig, cont = defaultdict(list), defaultdict(int)
    for (ap, n), cs in cur.items():
        for c in cs:
            if c["decisao"] in ("aceita", "aceita_a_conferir"):
                lig[(ap, n)].append((c["id_ator"], c["decisao"]))
            cont[c["decisao"]] += 1
    for p in propostas:
        k = (p["ap"], p["nome"])
        if k in cur:
            continue
        if p["forte"]:
            lig[k].append((p["id_ator"], "automatica"))
            cont["automatica"] += 1
        else:
            cont["pendente_sem_decisao"] += 1
    for r in csv.DictReader((CUR / "e9_ap470_reus.csv").open(encoding="utf-8")):
        if r["id_ator"]:
            lig[("AP 470", r["nome_partes"])] = [(r["id_ator"], "e9:" + r["metodo"])]
    return lig, cont


def partido_na_data(filiacoes: pd.DataFrame, ator: str, data: str) -> set[str]:
    f = filiacoes[filiacoes["id_ator"] == ator]
    vig = f[(f["data_inicio"] <= data) & ((f["data_fim"] == "") | (f["data_fim"] >= data))]
    if len(vig):
        return set(vig["id_partido"])
    antes = f[f["data_inicio"] <= data].sort_values("data_inicio")
    return {antes["id_partido"].iloc[-1]} if len(antes) else set()


def casos_por_partido(lig: dict, lista: pd.DataFrame, filiacoes: pd.DataFrame, id_proc: dict) -> dict[str, dict[str, set[str]]]:
    """universo da ação (sim, revisar, nao) -> partido -> processos, só ações com condenação."""
    casos = defaultdict(lambda: defaultdict(set))
    for (ap, _n), atores in lig.items():
        l = lista.loc[ap]
        if not any(r in CONDENACAO for r in l["resultados"].split("; ")):
            continue
        for a, _d in atores:
            for p in partido_na_data(filiacoes, a, l["data_primeiro_julgamento"]):
                casos[l["universo"]][p].add(id_proc[ap])
    return casos


def run() -> None:
    ids = RegistroIds()
    hoje = dt.date.today().isoformat()
    lista = pd.read_csv(CUR / "simetria_stf_ap_lista.csv", dtype=str).fillna("")
    lotes = [re.search(r"lote(\d+)", f.name).group(1) for f in relatorios()]
    lista = lista[lista["lote"].isin(lotes)].set_index("processo")
    atores, cargos, filiacoes = ler("atores").fillna(""), ler("cargos").fillna(""), ler("filiacoes").fillna("")
    proc = ler("processos")
    id_proc = dict(zip(proc["numero_originario"], proc["id_processo"]))
    regras = pd.read_csv(CUR / "assuntos_stf_eixo1.csv", dtype=str)
    u = dict(zip(proc["numero_originario"], universo_stf(proc, dict(zip(regras["caminho_stf"], regras["decisao"])))))
    lista["universo"] = lista.index.map(u)
    reus = ler_reus()
    lig, cont = ligacoes(reus, propor([r for r in reus if r["ap"] != "AP 470"], lista, atores, cargos))
    por_u = casos_por_partido(lig, lista, filiacoes, id_proc)
    casos, revisar = por_u["sim"], por_u["revisar"]
    inst = ler("instituicoes")
    sigla = dict(zip(inst["id_instituicao"], inst["sigla"]))
    universo = ler("universo_partidos")
    lote1 = next(f for f in relatorios() if f.name.endswith("lote1.md"))  # as ações julgadas no mérito estão no lote 1
    reg = {"arquivo": lote1.relative_to(RAIZ).as_posix(), "sha256": sha256(lote1)}
    existentes_b = set(ler("buscas")["id_busca"])
    buscas, busca_de = [], {}
    for p in sorted(set(universo["id_partido"])):
        consulta = (f"ações penais do STF do eixo 1 com condenação (D-048, lote 1) com réu parlamentar federal filiado a "
                    f"{sigla.get(p, p)} ({p}) na data do julgamento")
        i = ids.obter("buscas", f"{SCRIPT}|lote1|{p}")
        busca_de[p] = i
        if i not in existentes_b:
            buscas.append({"id_busca": i, "data": hoje, "fonte_dados": FONTE_DADOS, "consulta": consulta,
                           "parametros_json": json.dumps({"lote": 1, "id_partido": p, "n_acoes": len(lista)}, ensure_ascii=False, sort_keys=True),
                           "n_resultados": str(len(casos.get(p, ()))), "sha256_resposta": reg["sha256"], "caminho_raw": reg["arquivo"], "script": SCRIPT})
    status = ler("status_pessoa_processo")
    trib = dict(zip(proc["id_processo"], proc["id_tribunal"]))
    stf = ids.obter("instituicoes", "orgao:STF")
    filiados = set(filiacoes["id_ator"])
    alvo = status[status["status"].isin(STATUS_COM_SIMETRIA - STATUS_ADIADOS) & status["id_ator"].isin(filiados)]
    existentes_v = set(ler("verificacoes_simetria")["id_verificacao"])
    vs, vr = [], []
    for _, s in alvo.iterrows():
        v = ids.obter("verificacoes_simetria", f"{SCRIPT}|status_pessoa_processo|{s['id_status']}")
        if v in existentes_v:
            continue
        ano = s["data"][:4]
        no_stf = trib.get(s["id_processo"]) == stf
        vs.append({"id_verificacao": v, "achado_tabela": "status_pessoa_processo", "achado_id": s["id_status"],
                   "padrao_buscado": PADRAO if no_stf else "Status formal em ação penal de tribunal estadual com réu que é parlamentar federal da base",
                   "ano_referencia": ano, "data": hoje, "script": SCRIPT})
        grupos = [("partido", p) for p in sorted(universo.loc[universo["ano"] == ano, "id_partido"])] + [("governo", "governo"), ("oposicao", "oposicao")]
        for tipo, g in grupos:
            linha = {"id_resultado": ids.obter("verificacao_resultado", f"{v}|{g}"), "id_verificacao": v, "grupo_tipo": tipo, "grupo_id": g}
            if tipo != "partido":
                linha.update(resultado="nao_verificado", justificativa=SEM_GOVERNO)
            elif not no_stf:
                linha.update(resultado="nao_verificado", justificativa=SEM_UNIVERSO)
            elif casos.get(g):
                linha.update(resultado="encontrado", n_casos=str(len(casos[g])), ids_encontrados=";".join(sorted(casos[g])), id_busca=busca_de[g])
            elif revisar.get(g):
                linha.update(resultado="nao_verificado", id_busca=busca_de[g],
                             justificativa=f"Sem ação do eixo 1, mas com ação de assunto a revisar na regra da E5: {';'.join(sorted(revisar[g]))}")
            else:
                linha.update(resultado="sem_evidencia", n_casos="0", id_busca=busca_de[g])
            vr.append(linha)
    acrescentar("buscas", buscas)
    acrescentar("verificacoes_simetria", vs)
    acrescentar("verificacao_resultado", vr)
    ids.salvar()
    n_lig = sum(len(v) for v in lig.values())
    print(f"réus: {len(reus)}; ligações a parlamentares: {n_lig} ({dict(cont)})")
    print(f"ações do eixo 1 com condenação, por partido: { {f'{sigla.get(p, p)} {p}': sorted(c) for p, c in casos.items()} }")
    print(f"ações a revisar com condenação, por partido: { {f'{sigla.get(p, p)} {p}': sorted(c) for p, c in revisar.items()} }")
    print(f"buscas: {len(buscas)}; verificações: {len(vs)}; resultados: {len(vr)}")


if __name__ == "__main__":
    run()
