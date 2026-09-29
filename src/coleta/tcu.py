"""Coletor das listas públicas do TCU (D-060): responsáveis com contas julgadas irregulares (trânsito em julgado), as
listas para fins eleitorais de 2018 e 2022 e a de inabilitados para função pública.

Fonte: a API pública da Plataforma de Certidões do TCU (https://certidoes.apps.tcu.gov.br), a mesma que a página de
listas usa para o botão de exportação em CSV (POST /api/publico/<lista>/exportar-para-csv, até 50.000 linhas). O CSV
é gravado no bruto sem alteração. Os arquivos trazem CPF: ele serve só para ligar registros (D-060) e não vai para a
base nem para relatórios.

Uso:
    python -m src.coleta.tcu --data AAAA-MM-DD
"""

import argparse

from src.base import RegistroIds
from src.coleta.comum import Cliente, Execucao, registrar_busca

API = "https://certidoes.apps.tcu.gov.br/api/publico"
SCRIPT = "src.coleta.tcu"
LISTAS = [  # (lista na API, parâmetros, arquivo no bruto)
    ("responsaveis-contas-irregulares", {}, "tcu_contas_julgadas_irregulares.csv"),
    ("responsaveis-fins-eleitorais", {"anoEleicao": "2018"}, "tcu_contas_irregulares_fins_eleitorais_2018.csv"),
    ("responsaveis-fins-eleitorais", {"anoEleicao": "2022"}, "tcu_contas_irregulares_fins_eleitorais_2022.csv"),
    ("responsaveis-inabilitados", {}, "tcu_inabilitados_funcao_publica.csv"),
]


def coletar(data: str | None = None) -> None:
    cliente, execucao, ids = Cliente(tempo_limite=300), Execucao("tcu", data), RegistroIds()
    feitas = []
    for lista, params, arquivo in LISTAS:
        url = f"{API}/{lista}/exportar-para-csv?" + "&".join(f"{k}={v}" for k, v in {"paginaAtual": "1", "tamanhoPagina": "50000", **params}.items())
        r = cliente.post(url, {}, headers={"Accept": "text/csv, */*"})
        r.raise_for_status()
        destino = execucao.pasta / arquivo
        if destino.exists():
            raise FileExistsError(f"{destino} já existe: data/raw é imutável")
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(r.content)
        execucao.arquivos[arquivo] = {"url_base": url, "n_requisicoes": 1}
        linhas = max(r.content.count(b"\n") - 1, 0)
        feitas.append((arquivo, lista, params, linhas))
        print(f"{arquivo}: {len(r.content)} bytes, ~{linhas} linhas")
    manifesto = {m["arquivo"].rsplit("/", 1)[1]: m for m in execucao.fechar()}
    for arquivo, lista, params, linhas in feitas:
        registrar_busca("TCU, Plataforma de Certidões (API pública)", f"{lista} {params}".strip(), linhas, SCRIPT, execucao.data,
                        {"lista": lista, **params}, manifesto[arquivo], ids)
    ids.salvar()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data")
    coletar(ap.parse_args().data)
