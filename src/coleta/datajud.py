"""Coletor da API pública do DataJud (CNJ), etapa E4 (STJ).

Uso restrito (D-022): serve só para descobrir o universo de processos (número, classe, assuntos,
datas, órgão julgador, movimentos). Nada daqui é publicado nem cruzado com pessoas; relatórios citam
a fonte primária do tribunal. Limite do termo de uso: 120 requisições por minuto (usamos pausa de
0,6 s, até 100 por minuto).

A chave pública é lida a cada execução na página de acesso do CNJ (D-023) e nunca é gravada.

Uso:
    python -m src.coleta.datajud --explorar       # estrutura, classes e assuntos (poucas requisições)
    python -m src.coleta.datajud --planejar       # conta os processos do universo
    python -m src.coleta.datajud                  # coleta o universo
"""

import argparse
import json
import re

from src.base import RegistroIds
from src.coleta.comum import Cliente, Execucao, registrar_busca

PAGINA_ACESSO = "https://datajud-wiki.cnj.jus.br/api-publica/acesso/"
ENDPOINT = "https://api-publica.datajud.cnj.jus.br/api_publica_{tribunal}/_search"
SCRIPT = "src.coleta.datajud"
PAUSA = 0.6


def chave_publica(cliente: Cliente) -> str:
    r = cliente.get(PAGINA_ACESSO, headers={"Accept": "text/html"})
    r.raise_for_status()
    m = re.search(r"APIKey\s+([A-Za-z0-9+/=_-]{20,})", re.sub(r"<[^>]+>", " ", r.text))
    if not m:
        raise RuntimeError("chave pública não encontrada na página de acesso do DataJud")
    return m.group(1)


class DataJud:
    def __init__(self, tribunal: str = "stj"):
        self.cliente = Cliente(pausa=PAUSA)
        self.url = ENDPOINT.format(tribunal=tribunal)
        self._cabecalho = {"Authorization": f"APIKey {chave_publica(self.cliente)}", "Content-Type": "application/json"}

    def consultar(self, corpo: dict, execucao: Execucao | None = None, arquivo: str = "") -> dict:
        r = self.cliente.post(self.url, corpo, headers=self._cabecalho)
        dados = execucao.gravar(arquivo, self.url, r, corpo) if execucao else r.json()
        r.raise_for_status()
        return dados


def explorar() -> None:
    dj, ex, ids = DataJud(), Execucao("datajud_stj"), RegistroIds()
    amostra = dj.consultar({"size": 1, "query": {"match_all": {}}}, ex, "exploracao.jsonl")
    print("total de documentos (limite de contagem 10000 se não exato):", amostra["hits"]["total"])
    doc = amostra["hits"]["hits"][0]["_source"]
    print("campos:", sorted(doc))
    print(json.dumps({k: doc[k] for k in doc if k != "movimentos"}, ensure_ascii=False)[:1500])
    print("exemplo de movimento:", json.dumps((doc.get("movimentos") or [{}])[0], ensure_ascii=False)[:400])
    aggs = dj.consultar({"size": 0, "query": {"match_all": {}}, "track_total_hits": True,
                         "aggs": {"classes": {"terms": {"field": "classe.codigo", "size": 400}},
                                  "nomes": {"terms": {"field": "classe.nome.keyword", "size": 400}}}}, ex, "exploracao.jsonl")
    print("total exato:", aggs["hits"]["total"])
    for b in aggs.get("aggregations", {}).get("nomes", {}).get("buckets", []):
        if re.search(r"penal|inqu|peti|crime|criminal|improbidade", b["key"], re.I):
            print(f"  classe: {b['key']}: {b['doc_count']}")
    for reg in ex.fechar():
        registrar_busca("DataJud (CNJ), API pública, STJ", "exploração: estrutura do documento e classes processuais", 2, SCRIPT, ex.data,
                        {"endpoint": dj.url}, reg, ids)
    ids.salvar()


CLASSES_ORIGINARIAS = ["Ação Penal", "Inquérito"]


def coletar(classes: list[str] = CLASSES_ORIGINARIAS, data: str | None = None) -> None:
    """Todas as ações penais e inquéritos do STJ na API pública, com movimentos, paginados por search_after."""
    dj, ex, ids = DataJud(), Execucao("datajud_stj", data), RegistroIds()
    corpo = {"size": 500, "track_total_hits": True, "query": {"terms": {"classe.nome.keyword": classes}},
             "sort": [{"@timestamp": "asc"}, {"numeroProcesso.keyword": "asc"}]}
    total, n = None, 0
    while True:
        r = dj.consultar(corpo, ex, "processos_originarios_penais.jsonl")
        total = r["hits"]["total"]["value"]
        hits = r["hits"]["hits"]
        n += len(hits)
        if not hits or n >= total:
            break
        corpo["search_after"] = hits[-1]["sort"]
    print(f"{n} de {total} processos")
    for reg in ex.fechar():
        registrar_busca("DataJud (CNJ), API pública, STJ", f"processos das classes {', '.join(classes)} (todos os anos, nível de sigilo público)",
                        total, SCRIPT, ex.data, {"classes": classes, "endpoint": dj.url}, reg, ids)
    ids.salvar()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--explorar", action="store_true")
    a = ap.parse_args()
    explorar() if a.explorar else coletar()
