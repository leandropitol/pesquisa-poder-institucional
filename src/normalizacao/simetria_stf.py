"""Verificação de simetria dos status da E9 contra as ações penais do STF (D-007, D-048).

Entradas:
- os relatórios de navegação com os réus da aba Partes (bruto, lotes 1 a 7; o lote 1 tem as 99 ações julgadas no mérito);
- data/curadoria/simetria_stf_ap_lista.csv (datas de autuação e de julgamento, resultado);
- data/curadoria/simetria_stf_ap_ligacoes.csv: decisões sobre a ligação réu -> parlamentar da base
  (aceita, aceita_a_conferir, rejeitada, pendente), com motivo;
- data/curadoria/e9_ap470_reus.csv: ligações da AP 470, já decididas na E9.

Ligação automática (sem decisão na curadoria): parlamentar com mandato entre a autuação e o último julgamento de
mérito (ou a última decisão, na ação sem julgamento de mérito), com nome igual ao da aba Partes, ou com todas as palavras do nome parlamentar (pelo menos duas) no nome
civil, correspondência única, e com o primeiro e o último nome coincidentes. Correspondência mais fraca só entra
por decisão na curadoria; sem decisão, fica pendente e é contada.

Partido: filiação do réu na data do primeiro julgamento de mérito; sem filiação vigente, a última iniciada antes.

Para cada status da E9 que exige simetria, grava uma verificação com um resultado por partido do universo do ano.
Condenação: contam as ações com assunto do eixo 1 pela regra da E5 e com condenação de ao menos um réu (lote 1),
partido na data do primeiro julgamento. Réu: só com todos os lotes lidos; contam todas as ações do eixo 1 em que o
parlamentar é réu, partido na data de autuação. Denunciado não tem padrão lido. Resultado: `encontrado` (ações
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
from src.simetria.governo_oposicao import SAIDA as TABELA_GOVERNO, grupo_na_data, ler_tabela as ler_tabela_governo
from src.validacao.validar import STATUS_COM_SIMETRIA

CUR = RAIZ / "data" / "curadoria"
RAW_STF = RAIZ / "data" / "raw" / "stf"
NAO_PESSOA = re.compile(r"^(MINIST[ÉE]RIO P[ÚU]BLICO|OS MESMOS$|MADEIREIRA |MUNIC[ÍI]PIO DE |ESTADO D[OE] |UNI[ÃA]O FEDERAL)|\b(LTDA|EPP|EIRELI|S/A|S\.A\.|CIA)\b|\s-?\s?ME$|(?<!\bDE)\sS\.?A\.?$|\sS\.A\.\s")  # órgão, ente público, texto e empresa
SCRIPT = "src.normalizacao.simetria_stf"
FONTE_DADOS = "STF, portal (aba Partes) e Corte Aberta (decisões)"
STATUS_ADIADOS = {"reu", "denunciado"}
SUFIXOS = {"filho", "junior", "neto", "sobrinho"}
CONDENACAO = ("Procedente", "Procedente em parte")
PADRAO = ("Ação penal originária no STF, com assunto do eixo 1 pela regra da E5, julgada por órgão colegiado com condenação de "
          "ao menos um réu (andamento Procedente ou Procedente em parte no Corte Aberta; o resultado por réu não foi lido), 2003 a "
          "2026, com réu que é parlamentar federal da base; partido = filiação do réu na data do primeiro julgamento de mérito "
          "(D-048, lote 1 de 99 ações julgadas no mérito)")
PADRAO_REU = ("Ação penal originária no STF, com assunto do eixo 1 pela regra da E5, com réu que é parlamentar federal da base "
              "(aba Partes das 660 ações penais com decisão no Corte Aberta, fora as de 8 de janeiro de 2023; lotes 1 a 7 de D-048), "
              "2003 a 2026; partido = filiação do réu na data de autuação da ação")
PADRAO_GRUPOS = ("; governo e oposição = classificação do partido do réu na mesma data pelas orientações de bancada da Câmara "
                 "(D-050, com blocos decompostos por D-051; relatorios/tabelas/governo_oposicao_partidos.csv)")
SEM_GOVERNO = "A base não tem a composição da base do governo e da oposição por data; grupo não verificado"
SEM_UNIVERSO = ("Status em tribunal estadual (TJMG): não há universo lido de ações penais estaduais com réu parlamentar para "
                "comparar partidos (D-048)")
SEM_UNIVERSO_DE = {"INS-001539": SEM_UNIVERSO}  # TJMG: texto já gravado na primeira versão


def sem_universo(tribunal: str, sigla: dict) -> str:
    return SEM_UNIVERSO_DE.get(tribunal) or (f"Status em processo fora do STF ({sigla.get(tribunal, tribunal)}): não há universo lido de ações "
                                             "penais desse tribunal ou grau com réu político para comparar partidos (D-048)")


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
    réu, o texto "OS MESMOS", empresa (LTDA, ME, EPP, EIRELI, S/A) e nomes só com iniciais (processos em segredo de
    justiça). Ação sem réu rotulado (queixa-crime com querelante e querelado) não tem linha de réu."""
    saida = []
    for f in relatorios():
        for l in f.read_text(encoding="utf-8").splitlines():
            if re.match(r"^\| \d+ \|", l):
                c = [x.strip() for x in l.split("|")[1:-1]]
                if c[2] and not NAO_PESSOA.search(c[2]) and not so_iniciais(c[2]):
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


def casos_por_partido(lig: dict, lista: pd.DataFrame, filiacoes: pd.DataFrame, id_proc: dict,
                      so_condenacao: bool = True, campo_data: str = "data_primeiro_julgamento", grupo_de=None) -> dict[str, dict[str, set[str]]]:
    """universo da ação (sim, revisar, nao) -> partido -> processos. Padrão de condenação: só ações com condenação,
    partido na data do primeiro julgamento de mérito; padrão de réu: todas as ações, partido na data de autuação.
    Com `grupo_de(partido, data)`, a chave passa a ser o grupo do partido na data (governo, oposição...), D-050/D-051."""
    casos = defaultdict(lambda: defaultdict(set))
    for (ap, _n), atores in lig.items():
        l = lista.loc[ap]
        if so_condenacao and not any(r in CONDENACAO for r in l["resultados"].split("; ")):
            continue
        for a, _d in atores:
            for p in partido_na_data(filiacoes, a, l[campo_data]):
                casos[l["universo"]][grupo_de(p, l[campo_data]) if grupo_de else p].add(id_proc[ap])
    return casos


def carregar() -> dict:
    """Lista das ações lidas (com o universo do eixo 1 pela regra da E5) e ligações réu -> parlamentar."""
    lista = pd.read_csv(CUR / "simetria_stf_ap_lista.csv", dtype=str).fillna("")
    lotes = [re.search(r"lote(\d+)", f.name).group(1) for f in relatorios()]
    todos_lotes = set(lista["lote"]) <= set(lotes)  # o padrão de réu só vale com todas as ações lidas
    lista = lista[lista["lote"].isin(lotes)].set_index("processo")
    atores, cargos, filiacoes = ler("atores").fillna(""), ler("cargos").fillna(""), ler("filiacoes").fillna("")
    proc = ler("processos")
    regras = pd.read_csv(CUR / "assuntos_stf_eixo1.csv", dtype=str)
    u = dict(zip(proc["numero_originario"], universo_stf(proc, dict(zip(regras["caminho_stf"], regras["decisao"])))))
    lista["universo"] = lista.index.map(u)
    reus = ler_reus()
    lig, cont = ligacoes(reus, propor([r for r in reus if r["ap"] != "AP 470"], lista, atores, cargos))
    return {"lista": lista, "lotes": lotes, "todos_lotes": todos_lotes, "atores": atores, "cargos": cargos, "filiacoes": filiacoes,
            "proc": proc, "reus": reus, "lig": lig, "cont": cont}


def run() -> None:
    ids = RegistroIds()
    hoje = dt.date.today().isoformat()
    c = carregar()
    lista, lotes, todos_lotes, filiacoes, proc, reus, lig, cont = (c[k] for k in ("lista", "lotes", "todos_lotes", "filiacoes", "proc", "reus", "lig", "cont"))
    id_proc = dict(zip(proc["numero_originario"], proc["id_processo"]))
    inst = ler("instituicoes")
    sigla = dict(zip(inst["id_instituicao"], inst["sigla"]))
    universo = ler("universo_partidos")
    existentes_b = set(ler("buscas")["id_busca"])
    lote1 = next(f for f in relatorios() if f.name.endswith("lote1.md"))  # as ações julgadas no mérito estão no lote 1
    arquivos = {f.relative_to(RAIZ).as_posix(): sha256(f) for f in relatorios()}
    # padrão -> (status cobertos, casos por universo, prefixo da busca, texto da consulta, arquivo bruto, sha256, parâmetros)
    padroes = {"condenacao": (STATUS_COM_SIMETRIA - STATUS_ADIADOS, casos_por_partido(lig, lista, filiacoes, id_proc), "lote1",
                              "ações penais do STF do eixo 1 com condenação (D-048, lote 1) com réu parlamentar federal filiado a {s} ({p}) na data do julgamento",
                              lote1.relative_to(RAIZ).as_posix(), sha256(lote1), {"lote": 1, "n_acoes": len(lista)}, PADRAO)}
    if todos_lotes:
        padroes["reu"] = ({"reu"}, casos_por_partido(lig, lista, filiacoes, id_proc, so_condenacao=False, campo_data="data_autuacao"), "reu",
                          "ações penais do STF do eixo 1 (D-048, lotes 1 a 7) com réu parlamentar federal filiado a {s} ({p}) na data de autuação",
                          "data/raw/stf/*/stf_relatorio_navegacao_partes_ap_lote*.md", "", {"lotes": sorted(lotes), "n_acoes": len(lista), "arquivos_sha256": arquivos},
                          PADRAO_REU)
    buscas, busca_de = [], {}
    for nome, (_st, por_u, chave, texto, arq, sha, par, _pd) in padroes.items():
        for p in sorted(set(universo["id_partido"])):
            i = ids.obter("buscas", f"{SCRIPT}|{chave}|{p}")
            busca_de[(nome, p)] = i
            if i not in existentes_b:
                buscas.append({"id_busca": i, "data": hoje, "fonte_dados": FONTE_DADOS, "consulta": texto.format(s=sigla.get(p, p), p=p),
                               "parametros_json": json.dumps({**par, "id_partido": p}, ensure_ascii=False, sort_keys=True),
                               "n_resultados": str(len(por_u["sim"].get(p, ()))), "sha256_resposta": sha, "caminho_raw": arq, "script": SCRIPT})
    # governo e oposição (D-050/D-051): grupo do partido do réu na data do caso; ativa a segunda versão das verificações
    por_grupo = {}
    if TABELA_GOVERNO.exists():
        tab = ler_tabela_governo()
        memo = {}

        def grupo(p: str, d: str) -> str:
            if (p, d) not in memo:
                memo[(p, d)] = grupo_na_data(tab, p, d)
            return memo[(p, d)]

        por_grupo = {"condenacao": casos_por_partido(lig, lista, filiacoes, id_proc, grupo_de=grupo)}
        if todos_lotes:
            por_grupo["reu"] = casos_por_partido(lig, lista, filiacoes, id_proc, so_condenacao=False, campo_data="data_autuacao", grupo_de=grupo)
        for nome, por_g in por_grupo.items():
            _st, _pu, chave, texto, arq, sha, par, _pd = padroes[nome]
            for g in ("governo", "oposicao"):
                i = ids.obter("buscas", f"{SCRIPT}|{chave}|grupo:{g}")
                busca_de[(nome, g)] = i
                if i not in existentes_b:
                    rotulo = "base do governo" if g == "governo" else "oposição"
                    buscas.append({"id_busca": i, "data": hoje, "fonte_dados": FONTE_DADOS + "; Câmara, orientações de bancada (D-050/D-051)",
                                   "consulta": texto.replace("filiado a {s} ({p})", f"de partido classificado como {rotulo}").format(),
                                   "parametros_json": json.dumps({**par, "grupo": g, "tabela": TABELA_GOVERNO.relative_to(RAIZ).as_posix()},
                                                                 ensure_ascii=False, sort_keys=True),
                                   "n_resultados": str(len(por_g["sim"].get(g, ()))), "sha256_resposta": sha, "caminho_raw": arq, "script": SCRIPT})
    status = ler("status_pessoa_processo")
    trib = dict(zip(proc["id_processo"], proc["id_tribunal"]))
    stf = ids.obter("instituicoes", "orgao:STF")
    filiados = set(filiacoes["id_ator"])
    existentes_v = set(ler("verificacoes_simetria")["id_verificacao"])
    vs, vr = [], []
    alvo = [(nome, s) for nome, (sts, *_r) in padroes.items() for _, s in status[status["status"].isin(sts) & status["id_ator"].isin(filiados)].iterrows()]
    for nome, s in alvo:
        _st, por_u, _c, _t, _a, _s, _p, padrao = padroes[nome]
        casos, revisar = por_u["sim"], por_u["revisar"]
        no_stf = trib.get(s["id_processo"]) == stf
        # segunda versão (com governo e oposição) só para status no STF; a primeira fica no histórico (D-050)
        v2 = no_stf and nome in por_grupo
        v = ids.obter("verificacoes_simetria", f"{SCRIPT}|{'v2|' if v2 else ''}status_pessoa_processo|{s['id_status']}")
        if v in existentes_v:
            continue
        ano = s["data"][:4]
        vs.append({"id_verificacao": v, "achado_tabela": "status_pessoa_processo", "achado_id": s["id_status"],
                   "padrao_buscado": (padrao + (PADRAO_GRUPOS if v2 else "")) if no_stf
                   else "Status formal em ação penal de tribunal estadual com réu que é parlamentar federal da base",
                   "ano_referencia": ano, "data": hoje, "script": SCRIPT})
        grupos = [("partido", p) for p in sorted(universo.loc[universo["ano"] == ano, "id_partido"])] + [("governo", "governo"), ("oposicao", "oposicao")]
        for tipo, g in grupos:
            linha = {"id_resultado": ids.obter("verificacao_resultado", f"{v}|{g}"), "id_verificacao": v, "grupo_tipo": tipo, "grupo_id": g}
            c_g, r_g = (casos, revisar) if tipo == "partido" else (por_grupo[nome]["sim"], por_grupo[nome]["revisar"]) if v2 else ({}, {})
            if tipo != "partido" and not v2:
                linha.update(resultado="nao_verificado", justificativa=SEM_GOVERNO if no_stf else sem_universo(trib.get(s["id_processo"]), sigla))
            elif not no_stf:
                linha.update(resultado="nao_verificado", justificativa=sem_universo(trib.get(s["id_processo"]), sigla))
            elif c_g.get(g):
                linha.update(resultado="encontrado", n_casos=str(len(c_g[g])), ids_encontrados=";".join(sorted(c_g[g])), id_busca=busca_de[(nome, g)])
            elif r_g.get(g):
                linha.update(resultado="nao_verificado", id_busca=busca_de[(nome, g)],
                             justificativa=f"Sem ação do eixo 1, mas com ação de assunto a revisar na regra da E5: {';'.join(sorted(r_g[g]))}")
            else:
                linha.update(resultado="sem_evidencia", n_casos="0", id_busca=busca_de[(nome, g)])
            vr.append(linha)
    acrescentar("buscas", buscas)
    acrescentar("verificacoes_simetria", vs)
    acrescentar("verificacao_resultado", vr)
    ids.salvar()
    n_lig = sum(len(v) for v in lig.values())
    print(f"réus: {len(reus)}; ligações a parlamentares: {n_lig} ({dict(cont)})")
    for nome, (_st, por_u, *_r) in padroes.items():
        print(f"[{nome}] ações do eixo 1 por partido: { {sigla.get(p, p): len(c) for p, c in sorted(por_u['sim'].items(), key=lambda x: -len(x[1]))} }")
        print(f"[{nome}] ações a revisar por partido: { {sigla.get(p, p): len(c) for p, c in por_u['revisar'].items()} }")
    print(f"buscas: {len(buscas)}; verificações: {len(vs)}; resultados: {len(vr)}")


if __name__ == "__main__":
    run()
