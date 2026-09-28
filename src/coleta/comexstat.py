"""Coletor do ComexStat (MDIC): exportações e importações brasileiras por país e mês, em valor FOB (D-054).

Baixa, sem alteração:
  - a tabela oficial de países com código ISO (PAIS.csv, página de tabelas auxiliares da base de dados);
  - para cada ano de 2003 até o atual e cada fluxo (exportação, importação), a resposta da API pública
    (POST /general, detalhamento por país, métrica FOB, com detalhe mensal).

A API limita a frequência de consultas (HTTP 429): o cliente espera entre as consultas e tenta de novo.
O servidor da tabela de países usa cadeia de certificados que o pacote certifi não reconhece; a leitura usa o
repositório de certificados do sistema operacional, com verificação ligada.

Uso:
    python -m src.coleta.comexstat
"""

import datetime as dt
import ssl
import urllib.request

from src.base import RegistroIds
from src.coleta.comum import USER_AGENT, Cliente, Execucao, registrar_busca

API = "https://api-comexstat.mdic.gov.br/general?language=pt"
PAIS = "https://balanca.economia.gov.br/balanca/bd/tabelas/PAIS.csv"
FONTE = "ComexStat (MDIC), API pública e tabelas auxiliares"
SCRIPT = "src.coleta.comexstat"
ANO_INICIAL = 2003


def baixar_sistema(ex: Execucao, url: str, arquivo: str) -> None:
    """Download com o repositório de certificados do sistema (verificação ligada)."""
    destino = ex.pasta / arquivo
    if destino.exists():
        raise FileExistsError(f"{destino} já existe: data/raw é imutável")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=120) as r:
        conteudo = r.read()
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(conteudo)
    ex.arquivos[arquivo] = {"url_base": url, "n_requisicoes": 1}


def coletar(data: str | None = None) -> None:
    cliente, ids, ex = Cliente(pausa=12.0, tempo_limite=180), RegistroIds(), Execucao("comexstat", data)
    baixar_sistema(ex, PAIS, "PAIS.csv")
    hoje = dt.date.today()
    n = {}
    for ano in range(ANO_INICIAL, hoje.year + 1):
        fim = f"{ano}-12" if ano < hoje.year else f"{ano}-{hoje.month:02d}"
        for fluxo in ("export", "import"):
            corpo = {"flow": fluxo, "monthDetail": True, "period": {"from": f"{ano}-01", "to": fim}, "details": ["country"], "metrics": ["metricFOB"]}
            for _tentativa in range(6):
                r = cliente.post(API, corpo, headers={"Content-Type": "application/json"})
                if r.status_code != 429:
                    break
            r.raise_for_status()
            d = ex.gravar(f"{fluxo}_pais_mes.jsonl", API, r, corpo)
            n[(fluxo, ano)] = len(d["data"]["list"])
            print(f"{fluxo} {ano}: {n[(fluxo, ano)]} linhas")
    for reg in ex.fechar():
        nome = reg["arquivo"].rsplit("/", 1)[1]
        linhas = sum(v for (f, _a), v in n.items() if nome.startswith(f)) if nome.endswith(".jsonl") else 1
        registrar_busca(FONTE, f"arquivo {nome}", linhas, SCRIPT, ex.data, {"url": reg["url_base"], "anos": f"{ANO_INICIAL}-{hoje.year}"}, reg, ids)
    ids.salvar()


if __name__ == "__main__":
    coletar()
