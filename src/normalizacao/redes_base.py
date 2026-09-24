"""Carga das filiações de partidos brasileiros a redes partidárias transnacionais (etapa E8, bloco D).

Entram só os pares (rede, sigla) com decisão `aceita` em data/curadoria/redes_membros_curadoria.csv,
com o papel registrado ali (`membro_de` ou `observador_de`). O partido é o registro no TSE vigente na
data da cópia (Resolvedor de src/normalizacao/partidos.py).

Período: por ano. Um ano conta como "observado" quando alguma cópia daquele ano lista o partido, e como
"não observado" quando a rede tem, naquele ano, cópia com algum partido brasileiro, mas não este. Anos
sem cópia informativa não interrompem o período. `data_inicio` e `data_fim` são a primeira e a última
observação no arquivo, não as datas de filiação e saída; `data_fim` fica vazia quando o partido está na
cópia mais recente da rede, desde que ela seja de 2026. Cada relação é ligada à primeira e à última cópia
que a sustentam, com o trecho literal como localizador.

Uso:
    python -m src.normalizacao.redes_base
"""

import csv
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, gravar, ler
from src.normalizacao.partidos import Resolvedor, linhagem, ultima_captura
from src.normalizacao.redes import tabela_deteccoes

FONTES_REDES = RAIZ / "data" / "curadoria" / "redes_fontes.csv"
CURADORIA = RAIZ / "data" / "curadoria" / "redes_membros_curadoria.csv"
MANIFESTO = RAIZ / "data" / "manifestos" / "redes.csv"
ANO_ATUAL = "2026"
TIPO = {"rede_partidaria": "rede_partidaria_transnacional", "forum_nao_partidario": "forum_politico_nao_partidario"}
RELACAO = {"membro": "membro_de", "observador": "observador_de"}


def data_iso(ts: str) -> str:
    return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"


def periodos(anos_obs: dict[str, list[str]], anos_info: set[str]) -> list[tuple[list[str], bool]]:
    """Blocos de anos observados; interrompe só em ano informativo sem o partido. Devolve (timestamps, aberto_no_fim)."""
    blocos, atual = [], []
    for ano in sorted(anos_info | set(anos_obs)):
        if ano in anos_obs:
            atual += anos_obs[ano]
        elif atual:
            blocos.append((sorted(atual), False))
            atual = []
    if atual:
        blocos.append((sorted(atual), True))
    return blocos


def montar(ids: RegistroIds) -> dict:
    redes = {}
    for l in csv.DictReader(FONTES_REDES.open(encoding="utf-8")):
        redes.setdefault(l["id_rede"], l)
    cur = {(l["id_rede"], l["sigla"]): l for l in csv.DictReader(CURADORIA.open(encoding="utf-8"))}
    man = {m["arquivo"]: m for m in csv.DictReader(MANIFESTO.open(encoding="utf-8"))}
    d = tabela_deteccoes()
    achados = d[d["sigla"] != ""]
    pendentes = sorted({(r, s) for r, s in zip(achados["id_rede"], achados["sigla"]) if (r, s) not in cur})
    aceitos = achados[[cur.get((r, s), {}).get("decisao") == "aceita" for r, s in zip(achados["id_rede"], achados["sigla"])]]

    _, tabelas = ultima_captura()
    partidos = linhagem(tabelas)
    resolver = Resolvedor(partidos)

    inst, id_rede = [], {}
    for r, l in redes.items():
        id_rede[r] = ids.obter("instituicoes", f"rede:{r}")
        inst.append({"id_instituicao": id_rede[r], "nome": l["nome"], "sigla": r, "tipo_instituicao": TIPO[l["tipo"]],
                     "poder": "nao_se_aplica", "esfera": "internacional", "pais_iso3": ""})
    fontes, oficiais, f_de = [], [], {}

    def fonte(arquivo: str, rede: str) -> str:
        if arquivo not in f_de:
            m = man[arquivo]
            ts = Path(arquivo).name.split("_", 1)[0]
            original = m["url_base"].split("id_/", 1)[-1]
            f = ids.obter("fontes", f"raw:{arquivo}")
            fontes.append({"id_fonte": f, "tipo_fonte": "oficial", "titulo": f"{redes[rede]['nome']}: página de membros, cópia de {data_iso(ts)} no Internet Archive",
                           "data_publicacao": data_iso(ts), "url": original, "url_arquivada": f"https://web.archive.org/web/{ts}/{original}",
                           "data_acesso": m["data_acesso"], "sha256": m["sha256"], "caminho_raw": arquivo,
                           "licenca": "Página pública da própria rede; cópia do Internet Archive", "observacao": "Lista de membros publicada pela rede (bloco D)"})
            oficiais.append({"id_fonte": f, "id_orgao": id_rede[rede], "tipo_documento": "Página de membros da rede (cópia arquivada)",
                             "data_documento": data_iso(ts), "link": f"https://web.archive.org/web/{ts}/{original}"})
            f_de[arquivo] = f
        return f_de[arquivo]

    relacoes, rel_fonte, resolucao = [], [], []
    for rede, g in aceitos.groupby("id_rede"):
        info = set(achados[achados["id_rede"] == rede]["ano"])
        por_partido: dict[str, dict] = {}
        for _, x in g.iterrows():
            p, metodo = resolver(x["sigla"], data_iso(x["timestamp"]))
            if p is None:
                resolucao.append((rede, x["sigla"], "sem_correspondencia"))
                continue
            e = por_partido.setdefault(p.chave, {"partido": p, "papel": cur[(rede, x["sigla"])]["papel"], "anos": {}, "prova": {}})
            e["anos"].setdefault(x["ano"], []).append(x["timestamp"])
            e["prova"].setdefault(x["timestamp"], (x["arquivo"], x["trecho"]))
            resolucao.append((rede, x["sigla"], metodo))
        for chave, e in por_partido.items():
            for tss, aberto in periodos(e["anos"], info):
                ini, fim = tss[0], tss[-1]
                r = ids.obter("relacoes", f"rede:{rede}:{chave}:{ini[:8]}")
                relacoes.append({"id_relacao": r, "origem_tipo": "instituicao", "origem_id": ids.obter("instituicoes", chave),
                                 "tipo_relacao": RELACAO[e["papel"]], "destino_tipo": "instituicao", "destino_id": id_rede[rede],
                                 "data_inicio": data_iso(ini), "data_fim": "" if aberto and fim[:4] == ANO_ATUAL else data_iso(fim),
                                 "eixo": "relacoes_externas", "nivel_confianca": "documentado"})
                for ts in dict.fromkeys((ini, fim)):
                    arquivo, trecho = e["prova"][ts]
                    rel_fonte.append({"id_relacao": r, "id_fonte": fonte(arquivo, rede), "localizador": " ".join(trecho.split())[:300]})
    return {"instituicoes": inst, "fontes": fontes, "fonte_oficial": oficiais, "relacoes": relacoes, "relacao_fonte": rel_fonte,
            "pendentes": pendentes, "resolucao": resolucao}


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    for nome in ("fontes", "fonte_oficial"):
        atual = ler(nome, base)
        novas = [l for l in r[nome] if l["id_fonte"] not in set(atual["id_fonte"])]
        gravar(nome, pd.concat([atual, pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    atual = ler("instituicoes", base)
    novas = pd.DataFrame(r["instituicoes"], dtype=str)
    gravar("instituicoes", pd.concat([atual[~atual["id_instituicao"].isin(novas["id_instituicao"])], novas], ignore_index=True), base)
    atual = ler("relacoes", base)
    novas_r = pd.DataFrame(r["relacoes"], dtype=str)
    redes = set(novas["id_instituicao"])
    mantidas = atual[~(atual["tipo_relacao"].isin(RELACAO.values()) & atual["destino_id"].isin(redes))]
    gravar("relacoes", pd.concat([mantidas, novas_r], ignore_index=True), base)
    atual = ler("relacao_fonte", base)
    gravar("relacao_fonte", pd.concat([atual[atual["id_relacao"].isin(mantidas["id_relacao"])], pd.DataFrame(r["relacao_fonte"], dtype=str)],
                                      ignore_index=True).drop_duplicates(["id_relacao", "id_fonte"]), base)
    ids.salvar()


def run() -> None:
    ids = RegistroIds()
    r = montar(ids)
    if r["pendentes"]:
        raise SystemExit(f"pares (rede, sigla) sem decisão em {CURADORIA.name}: {r['pendentes']}")
    gravar_resultado(r, ids)
    rel = pd.DataFrame(r["relacoes"])
    nomes = dict(zip(ler("instituicoes")["id_instituicao"], ler("instituicoes")["sigla"]))
    rel["partido"], rel["rede"] = rel["origem_id"].map(nomes), rel["destino_id"].map(nomes)
    print(rel[["rede", "partido", "tipo_relacao", "data_inicio", "data_fim"]].sort_values(["rede", "partido", "data_inicio"]).to_string(index=False))
    print("resolução de siglas:", pd.Series([m for _, _, m in r["resolucao"]]).value_counts().to_dict())


if __name__ == "__main__":
    run()
