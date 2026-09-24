"""Normalização da etapa E1 (Câmara e Senado) para data/base.

Lê a coleta mais recente de data/raw/camara e data/raw/senado e gera:

- `instituicoes`: Câmara, Senado, TSE e os partidos como registros no TSE (src/normalizacao/partidos.py);
  cada sigla dos registros é ligada ao partido que a usava na data (resumo em
  data/curadoria/partidos_resolucao_siglas.csv);
- `denominacoes_partido` e `relacoes` de fusão e incorporação entre partidos, com fonte no TSE;
- `atores`: deputados e senadores das legislaturas 52 em diante; a mesma pessoa nas duas Casas vira um
  só ator quando o nome parlamentar normalizado e a UF coincidem de forma única (lista em
  data/curadoria/equivalencias_atores_automaticas.csv; casos ambíguos em ..._pendentes.csv; decisões
  manuais em ..._manuais.csv prevalecem);
- `filiacoes`: Senado, com datas de filiação e desfiliação; Câmara, pelos períodos observados no
  histórico do deputado durante o mandato (o que acontece fora do mandato não é observado);
- `cargos`: mandatos de deputado federal (por legislatura) e de senador (por mandato);
- `universo_partidos`: para cada ano, partidos com ao menos um deputado em exercício em 2 de fevereiro;
- `fontes` e `fonte_oficial`: um registro por arquivo bruto usado.

Uso:
    python -m src.normalizacao.legislativo
"""

import csv
import datetime as dt
import json
import unicodedata
from collections import defaultdict
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, gravar, ler
from src.normalizacao.partidos import Resolvedor, apelidos_por_nome, montar_partidos

RAW = RAIZ / "data" / "raw"
MANIFESTOS = RAIZ / "data" / "manifestos"
CURADORIA = RAIZ / "data" / "curadoria"
LEGISLATURA_INICIAL = 52
INICIO_PERIODO = "2003-01-01"
DIA_UNIVERSO = "02-02"
SEM_PARTIDO = {"", "S.PART.", "S.PART", "S/PARTIDO", "S/PART.", "S/PART", "SEM PARTIDO", "S/P"}
EXERCICIO = "Exercício"
LICENCA = "Dados abertos (Lei 12.527/2011)"


# ------------------------------------------------------------------ funções puras
def normalizar_nome(nome: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", nome or "").encode("ascii", "ignore").decode("ascii")
    return " ".join(sem_acento.lower().split())


def sigla_valida(sigla: str | None) -> str | None:
    s = (sigla or "").strip().upper()
    return None if s in SEM_PARTIDO else s


def _data(valor: str | None) -> str:
    return (valor or "")[:10]


def periodos_camara(historico: list[dict], legislaturas: dict[int, tuple[str, str]], hoje: str) -> tuple[list[dict], list[dict]]:
    """Cargos (um por legislatura com exercício) e filiações observadas de um deputado.

    Registros com data fora do intervalo da própria legislatura são ignorados: a API marca
    "Nome no início da legislatura" com datas de legislaturas posteriores. Legislatura sem nenhum
    registro de exercício (suplente não convocado) não gera cargo nem filiação."""
    cargos, filiacoes = [], []
    por_leg: dict[int, list[dict]] = defaultdict(list)
    for r in historico:
        leg = r.get("idLegislatura")
        if not leg or leg < LEGISLATURA_INICIAL:
            continue
        ini, fim_l = legislaturas.get(leg, ("", ""))
        d = _data(r.get("dataHora"))
        if ini and not (ini <= d <= fim_l):
            continue
        por_leg[leg].append(r)
    for leg, recs in sorted(por_leg.items()):
        recs = sorted(recs, key=lambda r: r["dataHora"] or "")
        exercicio = [r for r in recs if r.get("situacao") == EXERCICIO]
        if not exercicio:
            continue
        ref = exercicio[0]
        inicio = _data(ref["dataHora"])
        ultimo = recs[-1]
        fim_leg = legislaturas.get(leg, ("", ""))[1]
        if ultimo.get("situacao") not in (None, EXERCICIO):
            fim = _data(ultimo["dataHora"])
        else:
            fim = fim_leg if fim_leg and fim_leg < hoje else ""
        cargos.append({"legislatura": leg, "inicio": inicio, "fim": fim, "condicao": ref.get("condicaoEleitoral") or "",
                       "uf": ref.get("siglaUf") or ""})
        atual = None
        for r in recs:
            s = sigla_valida(r.get("siglaPartido"))
            d = _data(r["dataHora"])
            if atual and s != atual["sigla"]:
                atual["fim"] = d
                filiacoes.append(atual)
                atual = None
            if s and atual is None:
                atual = {"sigla": s, "inicio": d, "fim": "", "legislatura": leg}
        if atual:
            atual["fim"] = fim
            filiacoes.append(atual)
    return cargos, filiacoes


def universo_do_ano(historicos: dict[int, list[dict]], legislaturas: dict[int, tuple[str, str]], ano: int) -> set[str]:
    """Partidos com ao menos um deputado em exercício em 2 de fevereiro do ano."""
    dia = f"{ano}-{DIA_UNIVERSO}"
    legs = [l for l, (ini, fim) in legislaturas.items() if ini <= dia <= fim]
    if not legs:
        return set()
    leg = legs[0]
    partidos = set()
    for recs in historicos.values():
        antes = sorted((r for r in recs if r.get("idLegislatura") == leg and _data(r["dataHora"]) <= dia), key=lambda r: r["dataHora"])
        if antes and antes[-1].get("situacao") == EXERCICIO:
            s = sigla_valida(antes[-1].get("siglaPartido"))
            if s:
                partidos.add(s)
    return partidos


def cargo_senado(mandato: dict, hoje: str) -> dict:
    prim = mandato.get("PrimeiraLegislaturaDoMandato") or {}
    seg = mandato.get("SegundaLegislaturaDoMandato") or {}
    fim = seg.get("DataFim") or prim.get("DataFim") or ""
    return {"codigo": mandato.get("CodigoMandato", ""), "inicio": prim.get("DataInicio", ""), "fim": fim if fim and fim < hoje else "",
            "participacao": mandato.get("DescricaoParticipacao", ""), "uf": mandato.get("UfParlamentar", "")}


def equivalencias(camara: dict[str, dict], senado: dict[str, dict], manuais: list[dict]) -> tuple[list[tuple[str, str, str]], list[tuple[str, str]]]:
    """(id_camara, codigo_senado, método) para a mesma pessoa, e pares ambíguos para revisão.

    `camara` e `senado`: id -> {"nomes": set de nomes normalizados, "ufs": set de UFs}."""
    decididos = {(m["id_camara"], m["id_senado"]): m["decisao"] for m in manuais}
    por_nome: dict[str, set[str]] = defaultdict(set)
    for ident, info in camara.items():
        for n in info["nomes"]:
            por_nome[n].add(ident)
    candidatos: dict[str, set[str]] = {}
    for cod, info in senado.items():
        cands = set().union(*(por_nome.get(n, set()) for n in info["nomes"])) if info["nomes"] else set()
        candidatos[cod] = {c for c in cands if camara[c]["ufs"] & info["ufs"]}
    usados = defaultdict(list)
    for cod, cands in candidatos.items():
        for c in cands:
            usados[c].append(cod)
    pares, ambiguos = [], []
    for cod, cands in sorted(candidatos.items()):
        for c in sorted(cands):
            if decididos.get((c, cod)) == "pessoas_diferentes":
                continue
            if len(cands) == 1 and len(usados[c]) == 1:
                pares.append((c, cod, "automatico_nome_uf"))
            elif decididos.get((c, cod)) != "mesma_pessoa":
                ambiguos.append((c, cod))
    pares += [(c, s, "manual") for (c, s), d in decididos.items() if d == "mesma_pessoa" and (c, s, "automatico_nome_uf") not in pares]
    return pares, ambiguos


# ------------------------------------------------------------------ leitura da coleta
def ler_jsonl(caminho: Path) -> list[dict]:
    with caminho.open(encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def ultima_coleta(fonte: str) -> tuple[str, list[dict]]:
    manifesto = list(csv.DictReader((MANIFESTOS / f"{fonte}.csv").open(encoding="utf-8")))
    data = max(m["data_acesso"] for m in manifesto)
    return data, [m for m in manifesto if m["data_acesso"] == data]


def _por_arquivo(registros: list[dict], nome: str) -> dict:
    return next(r for r in registros if r["arquivo"].endswith("/" + nome))


# ------------------------------------------------------------------ montagem
TITULOS = {
    ("camara", "legislaturas.jsonl"): "Câmara dos Deputados, API de dados abertos v2: legislaturas",
    ("camara", "deputados_por_legislatura.jsonl"): "Câmara dos Deputados, API de dados abertos v2: deputados por legislatura",
    ("camara", "historicos.jsonl"): "Câmara dos Deputados, API de dados abertos v2: histórico de partido e situação dos deputados",
    ("camara", "partidos.jsonl"): "Câmara dos Deputados, API de dados abertos v2: partidos",
    ("senado", "senadores_por_legislatura.jsonl"): "Senado Federal, dados abertos: senadores e mandatos por legislatura",
    ("senado", "filiacoes.jsonl"): "Senado Federal, dados abertos: filiações partidárias dos senadores",
}


def montar(hoje: str | None = None, base: Path = BASE) -> dict:
    hoje = hoje or dt.date.today().isoformat()
    ids = RegistroIds(base=base)
    data_c, man_c = ultima_coleta("camara")
    data_s, man_s = ultima_coleta("senado")
    arquivos = {("camara", m["arquivo"].rsplit("/", 1)[1]): m for m in man_c} | {("senado", m["arquivo"].rsplit("/", 1)[1]): m for m in man_s}

    # instituições fixas
    casa = {"camara": ids.obter("instituicoes", "casa:camara"), "senado": ids.obter("instituicoes", "casa:senado")}
    instituicoes = {
        casa["camara"]: {"id_instituicao": casa["camara"], "nome": "Câmara dos Deputados", "sigla": "CD", "tipo_instituicao": "casa_legislativa",
                         "poder": "legislativo", "esfera": "federal", "pais_iso3": "BRA"},
        casa["senado"]: {"id_instituicao": casa["senado"], "nome": "Senado Federal", "sigla": "SF", "tipo_instituicao": "casa_legislativa",
                         "poder": "legislativo", "esfera": "federal", "pais_iso3": "BRA"},
    }

    # fontes
    fontes, oficiais, fonte_de = [], [], {}
    for (orig, nome), m in arquivos.items():
        f = ids.obter("fontes", f"raw:{m['arquivo']}")
        fonte_de[(orig, nome)] = f
        fontes.append({"id_fonte": f, "tipo_fonte": "oficial", "titulo": TITULOS.get((orig, nome), nome), "data_publicacao": m["data_acesso"],
                       "url": m["url_base"], "data_acesso": m["data_acesso"], "sha256": m["sha256"], "caminho_raw": m["arquivo"], "licenca": LICENCA,
                       "observacao": f"{m['n_requisicoes']} requisições; resposta bruta em JSONL"})
        oficiais.append({"id_fonte": f, "id_orgao": casa[orig], "tipo_documento": "Resposta da API de dados abertos (JSONL)",
                         "data_documento": m["data_acesso"], "link": m["url_base"]})

    def corpos(orig, nome):
        return [l["corpo"] for l in ler_jsonl(RAIZ / arquivos[(orig, nome)]["arquivo"]) if l["status"] == 200 and l["corpo"]]

    # Câmara
    legislaturas = {l["id"]: (l["dataInicio"], l["dataFim"]) for c in corpos("camara", "legislaturas.jsonl") for l in c["dados"]}
    nomes_partido = {}
    for c in corpos("camara", "partidos.jsonl"):
        d = c.get("dados") or {}
        if d.get("sigla"):
            nomes_partido[d["sigla"].strip().upper()] = d.get("nome", "").strip()
    historicos: dict[int, list[dict]] = defaultdict(list)
    for c in corpos("camara", "historicos.jsonl"):
        for r in c["dados"]:
            historicos[r["id"]].append(r)
    for c in corpos("camara", "deputados_por_legislatura.jsonl"):
        for d in c["dados"]:
            historicos.setdefault(d["id"], [])
    periodos = {dep: periodos_camara(recs, legislaturas, hoje) for dep, recs in historicos.items()}
    sem_exercicio = [dep for dep, (cs, _) in periodos.items() if not cs]
    camara_info = {}
    for dep, recs in historicos.items():
        if not periodos[dep][0]:
            continue  # nunca esteve em exercício desde 2003 (suplente não convocado)
        recs_leg = [r for r in recs if (r.get("idLegislatura") or 0) >= LEGISLATURA_INICIAL]
        camara_info[str(dep)] = {"nomes": {normalizar_nome(r.get("nome", "")) for r in recs_leg if r.get("nome")},
                                 "ufs": {r.get("siglaUf") for r in recs_leg if r.get("siglaUf")},
                                 "nome": (sorted(recs_leg, key=lambda r: r["dataHora"] or "")[-1].get("nome", "").strip() if recs_leg else "")}

    # Senado
    senado_info: dict[str, dict] = {}
    mandatos: dict[str, dict[str, dict]] = defaultdict(dict)
    for c in corpos("senado", "senadores_por_legislatura.jsonl"):
        lista = c["ListaParlamentarLegislatura"]["Parlamentares"]["Parlamentar"]
        for p in lista if isinstance(lista, list) else [lista]:
            ident = p["IdentificacaoParlamentar"]
            cod = ident["CodigoParlamentar"]
            info = senado_info.setdefault(cod, {"nomes": set(), "ufs": set(), "nome": ident.get("NomeParlamentar", "").strip()})
            info["nomes"] |= {normalizar_nome(ident.get("NomeParlamentar", "")), normalizar_nome(ident.get("NomeCompletoParlamentar", ""))} - {""}
            ms = (p.get("Mandatos") or {}).get("Mandato", [])
            for m in ms if isinstance(ms, list) else [ms]:
                mandatos[cod][m.get("CodigoMandato", "")] = m
                if m.get("UfParlamentar"):
                    info["ufs"].add(m["UfParlamentar"])
    filiacoes_senado: dict[str, list[dict]] = defaultdict(list)
    filiacoes_sem_data: list[str] = []  # filiação sem data nem ano de início: fica fora (lacuna)
    for c in corpos("senado", "filiacoes.jsonl"):
        parl = c.get("FiliacaoParlamentar", {}).get("Parlamentar", {})
        fs = (parl.get("Filiacoes") or {}).get("Filiacao", [])
        for f in fs if isinstance(fs, list) else [fs]:
            partido = f.get("Partido") or {}
            s = sigla_valida(partido.get("SiglaPartido"))
            if s:
                nomes_partido.setdefault(s, (partido.get("NomePartido") or "").strip())
                inicio = _data(f.get("DataFiliacao")) or (f.get("AnoFiliacao") or "")[:4]
                fim = _data(f.get("DataDesfiliacao")) or (f.get("AnoDesfiliacao") or "")[:4]
                if not inicio:
                    filiacoes_sem_data.append(parl.get("Codigo", ""))
                    continue
                reg = {"sigla": s, "inicio": inicio, "fim": fim}
                if reg not in filiacoes_senado[parl.get("Codigo", "")]:
                    filiacoes_senado[parl.get("Codigo", "")].append(reg)

    # equivalências entre Casas
    manuais_arq = CURADORIA / "equivalencias_atores_manuais.csv"
    manuais = list(csv.DictReader(manuais_arq.open(encoding="utf-8"))) if manuais_arq.exists() else []
    pares, ambiguos = equivalencias(camara_info, senado_info, manuais)

    atores = {}
    for dep, info in camara_info.items():
        a = ids.obter("atores", f"camara:{dep}")
        atores[a] = {"id_ator": a, "nome": info["nome"], "nome_normalizado": normalizar_nome(info["nome"]), "tipo_ator": "agente_publico", "id_camara": dep}
    conflitos = []
    for dep, cod, metodo in pares:
        a = ids.obter("atores", f"camara:{dep}")
        if ids.existe("atores", f"senado:{cod}") and ids.obter("atores", f"senado:{cod}") != a:
            conflitos.append((dep, cod))
        ids.vincular("atores", f"senado:{cod}", a)
        atores[a]["id_senado"] = cod
    for cod, info in senado_info.items():
        a = ids.obter("atores", f"senado:{cod}")
        if a not in atores:
            atores[a] = {"id_ator": a, "nome": info["nome"], "nome_normalizado": normalizar_nome(info["nome"]), "tipo_ator": "agente_publico", "id_senado": cod}

    # partidos: registro no TSE vigente na data (src/normalizacao/partidos.py)
    tse = montar_partidos(ids)
    for i in tse["instituicoes"]:
        instituicoes[i["id_instituicao"]] = i
    fontes += tse["fontes"]
    oficiais += tse["fonte_oficial"]
    apelidos = apelidos_por_nome(tse["partidos"], nomes_partido)
    resolver = Resolvedor(tse["partidos"], apelidos)
    resolucao: dict[str, dict] = defaultdict(lambda: {"vigencia": 0, "partido_existente": 0, "mais_proxima": 0, "sem_correspondencia": 0, "destino": set()})

    def partido(sigla: str, data: str) -> str:
        p, metodo = resolver(sigla, data)
        r = resolucao[sigla]
        r[metodo] += 1
        if p is not None:
            i = tse["id_de"][id(p)]
            r["destino"].add(i)
            return i
        i = ids.obter("instituicoes", f"partido_sem_tse:{sigla}")
        r["destino"].add(i)
        instituicoes.setdefault(i, {"id_instituicao": i, "nome": nomes_partido.get(sigla) or sigla, "sigla": sigla, "tipo_instituicao": "partido",
                                    "poder": "nao_se_aplica", "esfera": "federal", "pais_iso3": "BRA",
                                    "observacao": "Sigla dos registros da Câmara ou do Senado sem correspondência na página do TSE consultada"})
        return i

    filiacoes, cargos = [], []
    f_hist, f_sen_fil, f_sen_leg = fonte_de[("camara", "historicos.jsonl")], fonte_de[("senado", "filiacoes.jsonl")], fonte_de[("senado", "senadores_por_legislatura.jsonl")]
    for dep, (cs, fs) in periodos.items():
        if not cs:
            continue
        a = ids.obter("atores", f"camara:{dep}")
        for c in cs:
            cond = {"Titular": " (titular)", "Suplente": " (suplente)"}.get(c["condicao"], "")
            cargos.append({"id_cargo": ids.obter("cargos", f"camara:{dep}:{c['legislatura']}"), "id_ator": a, "id_instituicao": casa["camara"],
                           "cargo": f"Deputado federal{cond}, legislatura {c['legislatura']}", "forma_acesso": "eleito",
                           "data_inicio": c["inicio"], "data_fim": c["fim"], "id_fonte": f_hist})
        for f in fs:
            filiacoes.append({"id_filiacao": ids.obter("filiacoes", f"camara:{dep}:{f['legislatura']}:{f['sigla']}:{f['inicio']}"), "id_ator": a,
                              "id_partido": partido(f["sigla"], f["inicio"]), "data_inicio": f["inicio"], "data_fim": f["fim"], "id_fonte": f_hist})
    for cod, ms in mandatos.items():
        a = ids.obter("atores", f"senado:{cod}")
        for m in ms.values():
            c = cargo_senado(m, hoje)
            if not c["inicio"]:
                continue
            cargos.append({"id_cargo": ids.obter("cargos", f"senado:{cod}:{c['codigo']}"), "id_ator": a, "id_instituicao": casa["senado"],
                           "cargo": f"Senador ({c['participacao'].lower()})".replace(" ()", ""), "forma_acesso": "eleito",
                           "data_inicio": c["inicio"], "data_fim": c["fim"], "id_fonte": f_sen_leg})
    for cod, fs in filiacoes_senado.items():
        if not ids.existe("atores", f"senado:{cod}"):
            continue
        a = ids.obter("atores", f"senado:{cod}")
        for f in fs:
            if f["fim"] and f["fim"] < INICIO_PERIODO:
                continue  # filiação encerrada antes do período
            filiacoes.append({"id_filiacao": ids.obter("filiacoes", f"senado:{cod}:{f['sigla']}:{f['inicio']}:{f['fim']}"), "id_ator": a,
                              "id_partido": partido(f["sigla"], f["inicio"]), "data_inicio": f["inicio"], "data_fim": f["fim"], "id_fonte": f_sen_fil})

    universo = []
    for ano in range(int(INICIO_PERIODO[:4]), int(hoje[:4]) + 1):
        dia = f"{ano}-{DIA_UNIVERSO}"
        for i in sorted({partido(s, dia) for s in universo_do_ano(historicos, legislaturas, ano)}):
            universo.append({"ano": str(ano), "id_partido": i, "criterio": f"Partido com ao menos um deputado federal em exercício em {DIA_UNIVERSO[3:]}/{DIA_UNIVERSO[:2]}/{ano}, pelo histórico da Câmara",
                             "id_fonte": f_hist})

    return {"ids": ids, "instituicoes": list(instituicoes.values()), "atores": list(atores.values()), "fontes": fontes, "fonte_oficial": oficiais,
            "filiacoes": filiacoes, "cargos": cargos, "universo_partidos": universo, "pares": pares, "ambiguos": ambiguos, "conflitos": conflitos,
            "camara_info": camara_info, "senado_info": senado_info, "datas": (data_c, data_s), "sem_exercicio": sem_exercicio, "filiacoes_sem_data": filiacoes_sem_data,
            "denominacoes_partido": tse["denominacoes_partido"], "relacoes": tse["relacoes"], "relacao_fonte": tse["relacao_fonte"],
            "resolucao_siglas": resolucao, "apelidos": apelidos}


def _mesclar(nome: str, novas: list[dict], base: Path, remover=None) -> pd.DataFrame:
    atual = ler(nome, base)
    chave = [c for c in atual.columns if c in ("id_instituicao", "id_ator")] or None
    if remover is not None:
        atual = atual[~remover(atual)]
    novo = pd.DataFrame(novas, dtype=str)
    if chave:
        atual = atual[~atual[chave[0]].isin(novo[chave[0]])]
    return pd.concat([atual, novo], ignore_index=True)


def gravar_resultado(r: dict, base: Path = BASE) -> None:
    fontes_leg = {f["id_fonte"] for f in r["fontes"]}
    antigas = ler("fontes", base)
    fontes_leg |= set(antigas.loc[antigas["caminho_raw"].str.match(r"data/raw/(camara|senado)/"), "id_fonte"])
    for nome in ("fontes", "fonte_oficial"):
        existentes = set(ler(nome, base)["id_fonte"])
        novas = [l for l in r[nome] if l["id_fonte"] not in existentes]
        gravar(nome, pd.concat([ler(nome, base), pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    # partidos: o conjunto do TSE (mais siglas sem correspondência) substitui os anteriores
    gravar("instituicoes", _mesclar("instituicoes", r["instituicoes"], base, remover=lambda df: df["tipo_instituicao"] == "partido"), base)
    gravar("denominacoes_partido", pd.DataFrame(r["denominacoes_partido"], dtype=str), base)
    tipos_partido = {"fundiu_se_em", "incorporado_por"}
    antigas_rel = ler("relacoes", base)
    ids_rel_partido = set(antigas_rel.loc[antigas_rel["tipo_relacao"].isin(tipos_partido), "id_relacao"])
    gravar("relacoes", _mesclar("relacoes", r["relacoes"], base, remover=lambda df: df["tipo_relacao"].isin(tipos_partido)), base)
    gravar("relacao_fonte", _mesclar("relacao_fonte", r["relacao_fonte"], base, remover=lambda df: df["id_relacao"].isin(ids_rel_partido)), base)
    # atores das Casas são substituídos pelo conjunto da coleta atual (quem tem id_camara ou id_senado)
    gravar("atores", _mesclar("atores", r["atores"], base, remover=lambda df: (df["id_camara"] != "") | (df["id_senado"] != "")), base)
    for nome in ("filiacoes", "cargos", "universo_partidos"):
        gravar(nome, _mesclar(nome, r[nome], base, remover=lambda df: df["id_fonte"].isin(fontes_leg)), base)
    r["ids"].salvar()
    CURADORIA.mkdir(parents=True, exist_ok=True)
    manuais = CURADORIA / "equivalencias_atores_manuais.csv"
    if not manuais.exists():
        manuais.write_text("id_camara,id_senado,decisao,justificativa\n", encoding="utf-8")
    with (CURADORIA / "equivalencias_atores_automaticas.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["id_camara", "nome_camara", "id_senado", "nome_senado", "metodo"])
        for c, s, m in sorted(r["pares"]):
            w.writerow([c, r["camara_info"][c]["nome"], s, r["senado_info"][s]["nome"], m])
    inst = {i["id_instituicao"]: i for i in r["instituicoes"]}
    with (CURADORIA / "partidos_resolucao_siglas.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        metodos = ["vigencia", "partido_existente", "mais_proxima", "sem_correspondencia"]
        w.writerow(["sigla_fonte", "apelido_para_siglas_tse", "partidos"] + [f"registros_{m}" for m in metodos])
        for s, info in sorted(r["resolucao_siglas"].items()):
            destinos = sorted(info["destino"])
            w.writerow([s, " ".join(r["apelidos"].get(s, [])), "; ".join(f"{d} ({inst[d]['sigla']})" for d in destinos)] + [info[m] for m in metodos])
    with (CURADORIA / "equivalencias_atores_pendentes.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["id_camara", "nome_camara", "id_senado", "nome_senado", "motivo"])
        for c, s in sorted(r["ambiguos"]):
            w.writerow([c, r["camara_info"][c]["nome"], s, r["senado_info"][s]["nome"], "nome e UF coincidem com mais de um registro"])


def run() -> None:
    r = montar()
    gravar_resultado(r)
    print(f"coletas: Câmara {r['datas'][0]}, Senado {r['datas'][1]}")
    for nome in ("instituicoes", "atores", "filiacoes", "cargos", "universo_partidos", "fontes"):
        print(f"{nome}: {len(r[nome])}")
    soma = {m: sum(v[m] for v in r["resolucao_siglas"].values()) for m in ("vigencia", "partido_existente", "mais_proxima", "sem_correspondencia")}
    print(f"resolução de siglas para o registro do TSE: {soma}; apelidos por nome: {r['apelidos']}")
    print(f"filiações do Senado sem data de início (fora da base): {len(r['filiacoes_sem_data'])}")
    print(f"deputados listados sem exercício desde 2003 (fora da base): {len(r['sem_exercicio'])}")
    print(f"mesma pessoa nas duas Casas: {len(r['pares'])}; pares ambíguos para revisão: {len(r['ambiguos'])}; conflitos de id: {len(r['conflitos'])}")


if __name__ == "__main__":
    run()
