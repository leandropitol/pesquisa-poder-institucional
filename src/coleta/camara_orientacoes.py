"""Coletor das votações e das orientações de bancada da Câmara dos Deputados (arquivos anuais de dados abertos), D-050.

Baixa, para cada ano de 2003 até o atual, sem alteração:
  - votacoes-{ano}.csv: uma linha por votação (data, órgão, descrição);
  - votacoesOrientacoes-{ano}.csv: uma linha por orientação de bancada em cada votação, inclusive a do Governo
    (siglaBancada "GOV.").

Os arquivos servem para classificar, por partido e período, o alinhamento com a orientação do Governo (base do
governo, oposição ou nenhum dos dois), usado na verificação de simetria (D-007). Não trazem CPF.

Uso:
    python -m src.coleta.camara_orientacoes
"""

import datetime as dt

from src.base import RegistroIds
from src.coleta.comum import Cliente, Execucao, registrar_busca

URL = "https://dadosabertos.camara.leg.br/arquivos/{tipo}/csv/{tipo}-{ano}.csv"
FONTE = "Câmara dos Deputados, dados abertos (arquivos anuais)"
SCRIPT = "src.coleta.camara_orientacoes"
ANO_INICIAL = 2003


def coletar(data: str | None = None) -> None:
    cliente, ids, ex = Cliente(pausa=1.0, tempo_limite=180), RegistroIds(), Execucao("camara_orientacoes", data)
    falhas = []
    for ano in range(ANO_INICIAL, dt.date.today().year + 1):
        for tipo in ("votacoes", "votacoesOrientacoes"):
            url = URL.format(tipo=tipo, ano=ano)
            try:
                ex.baixar(cliente, url, f"{tipo}-{ano}.csv")
            except Exception as e:  # noqa: BLE001 — falha de um arquivo não interrompe; fica registrada como busca sem resultado
                falhas.append((tipo, ano, url, str(e)))
                print(f"FALHA {tipo} {ano}: {e}")
    for reg in ex.fechar():
        nome = reg["arquivo"].rsplit("/", 1)[1]
        registrar_busca(FONTE, f"arquivo {nome}", 1, SCRIPT, ex.data, {"url": reg["url_base"]}, reg, ids)
    for tipo, ano, url, erro in falhas:
        registrar_busca(FONTE, f"arquivo {tipo}-{ano}.csv (falha no download)", 0, SCRIPT, ex.data, {"url": url, "erro": erro}, None, ids)
    ids.salvar()
    print(f"{len(ex.arquivos)} arquivos baixados; {len(falhas)} falhas")


if __name__ == "__main__":
    coletar()
