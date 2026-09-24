"""Coletor das réguas externas de qualidade democrática (etapa E2).

- V-Dem, versão 16 (março de 2026): arquivo `vdem.RData` do pacote oficial `vdemdata`, publicado
  pelo V-Dem Institute no GitHub, pela tag `V16` (endereço fixo; o download pelo site exige
  formulário com e-mail). Licença dos dados: CC BY-SA 4.0.
- Freedom House, Freedom in the World: planilhas históricas públicas mais recentes encontradas
  (publicadas em fevereiro de 2025). As planilhas da edição 2026 não estão publicadas; a Freedom
  House passou a atendê-las por pedido por e-mail. Uso livre para fins acadêmicos e sem fins
  lucrativos, segundo a própria organização.

Uso:
    python -m src.coleta.reguas --planejar
    python -m src.coleta.reguas
"""

import argparse

from src.base import RegistroIds
from src.coleta.comum import Cliente, Execucao, registrar_busca

ARQUIVOS = {
    "vdem": [("vdem_v16.RData", "https://raw.githubusercontent.com/vdeminstitute/vdemdata/V16/data/vdem.RData")],
    "freedom_house": [
        ("Country_and_Territory_Ratings_and_Statuses_FIW_1973-2024.xlsx",
         "https://freedomhouse.org/sites/default/files/2025-02/Country_and_Territory_Ratings_and_Statuses_FIW_1973-2024.xlsx"),
        ("All_data_FIW_2013-2024.xlsx", "https://freedomhouse.org/sites/default/files/2025-02/All_data_FIW_2013-2024.xlsx"),
    ],
}
SCRIPT = "src.coleta.reguas"


def planejar() -> list[tuple[str, str, int | None]]:
    cliente, saida = Cliente(), []
    for fonte, lista in ARQUIVOS.items():
        for nome, url in lista:
            r = cliente.sessao.head(url, allow_redirects=True, timeout=60)
            saida.append((fonte, nome, int(r.headers["Content-Length"]) if "Content-Length" in r.headers else None))
    return saida


def coletar(data: str | None = None) -> None:
    cliente, ids = Cliente(), RegistroIds()
    for fonte, lista in ARQUIVOS.items():
        execucao = Execucao(fonte, data)
        for nome, url in lista:
            destino = execucao.baixar(cliente, url, nome)
            print(f"{fonte}: {nome} ({destino.stat().st_size / 1e6:.1f} MB)")
        for reg in execucao.fechar():
            registrar_busca({"vdem": "V-Dem Institute, pacote vdemdata (GitHub, tag V16)", "freedom_house": "Freedom House, planilhas históricas"}[fonte],
                            f"arquivo {reg['arquivo'].rsplit('/', 1)[1]}", 1, SCRIPT, execucao.data, {"url": reg["url_base"]}, reg, ids)
    ids.salvar()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--planejar", action="store_true")
    a = ap.parse_args()
    print(planejar()) if a.planejar else coletar()
