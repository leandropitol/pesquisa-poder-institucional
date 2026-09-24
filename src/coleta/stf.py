"""Registro das exportações do painel Corte Aberta do STF (etapa E5).

O portal do STF não entrega dados a cliente automatizado (D-009). O autor abriu os painéis no próprio
navegador, com o Claude in Chrome, aplicou os filtros e exportou as planilhas pelo botão do painel
(D-037). Também registra as bases da página de dados abertos do STF baixadas pelo autor, só quando
completas (a página corta a exportação em 5 milhões de células). Este módulo identifica cada arquivo pelo cabeçalho, dá a ele um nome descritivo, move para
data/raw/stf/<data>/, calcula o sha256 e grava manifesto e busca. Não acessa a rede.

Uso:
    python -m src.coleta.stf --data 2026-09-24
"""

import argparse
import csv
import shutil

import pandas as pd

from src.base import RAIZ, RegistroIds
from src.coleta.comum import MANIFESTOS, RAW, registrar_busca, sha256

SCRIPT = "src.coleta.stf"
FONTE_DADOS = "STF, Corte Aberta (exportação feita pelo autor no navegador, D-037)"
# cabeçalho que identifica o painel -> (nome no bruto, URL do painel, filtros aplicados, total mostrado no painel)
EXPORTACOES = {
    "idFatoDecisao": ("stf_corte_aberta_decisoes_AP_Inq_2003-01-08_a_2026-09-23.xlsx", "https://transparencia.stf.jus.br/extensions/decisoes/decisoes.html",
                      {"classe": ["AP", "Inq"], "data_decisao": ["2003-01-08", "2026-09-23"], "botao": "Decisões"}, 17202),
    "Link do processo": ("stf_corte_aberta_acervo_AP_Inq.xlsx", "https://transparencia.stf.jus.br/extensions/acervo/acervo.html",
                         {"classe": ["AP", "Inq"], "recorte": "acervo em tramitação na data da exportação", "botao": "Processos"}, 1331),
}
URL_DADOS_ABERTOS = "https://transparencia.stf.jus.br/extensions/dados_abertos/dados_abertos.html"
LIMITE_CELULAS = 5_000_000
RELATORIO = ("relatorio_stf_pesquisa_documental.md", "stf_relatorio_navegacao.md")


def registrar_manuais(data: str) -> None:
    raiz = RAW / "stf"
    pasta = raiz / data
    pasta.mkdir(parents=True, exist_ok=True)
    ids, regs = RegistroIds(), []
    for f in sorted(p for p in raiz.iterdir() if p.is_file()):
        if f.suffix.lower() == ".xlsx":
            colunas = list(pd.read_excel(f, nrows=0).columns)
            chave = next((k for k in EXPORTACOES if k in colunas), None)
            if chave is None:
                print(f"não identificado, fica onde está: {f.name}")
                continue
            nome, url, filtros, total = EXPORTACOES[chave]
            linhas = len(pd.read_excel(f, dtype=str))
            if linhas != total:
                raise ValueError(f"{f.name}: {linhas} linhas, o painel mostrava {total}")
            consulta = f"exportação {nome} (painel com {total} registros)"
            parametros = {"url": url, "filtros": filtros, "arquivo_original": f.name, "linhas": linhas}
        elif f.suffix.lower() == ".csv":
            # página de dados abertos (https://transparencia.stf.jus.br/extensions/dados_abertos/dados_abertos.html):
            # a exportação é cortada em 5 milhões de células; arquivo que chega perto do limite fica fora (incompleto)
            d = pd.read_csv(f, dtype=str, encoding="utf-8-sig")
            if d.size >= LIMITE_CELULAS * 0.999:
                print(f"incompleto (corte em {LIMITE_CELULAS} células), não registrado: {f.name}")
                continue
            tipo, anos = d["Tipo andamento"].iloc[0], sorted(d["ano_andamento"].unique())
            nome = f"stf_dados_abertos_{tipo}s_{anos[0]}{'' if len(anos) == 1 else '_a_' + anos[-1]}.csv"
            url, linhas = URL_DADOS_ABERTOS, len(d)
            consulta = f"dados abertos: {tipo}s {', '.join(anos)} ({linhas} linhas, todas as classes)"
            parametros = {"url": url, "arquivo_original": f.name, "linhas": linhas, "celulas": int(d.size)}
        elif f.name.startswith("dicionario_") and f.suffix.lower() == ".ods":
            nome, url, linhas = f"stf_dados_abertos_{f.name}", URL_DADOS_ABERTOS, 1
            consulta, parametros = f"dados abertos: {f.name}", {"url": url, "arquivo_original": f.name}
        elif f.name == RELATORIO[0]:
            nome, url = RELATORIO[1], "https://portal.stf.jus.br"
            consulta, linhas = "relatório de navegação do Claude in Chrome no portal do STF (registro auxiliar, não é fonte primária)", 1
            parametros = {"url": url, "arquivo_original": f.name}
        else:
            print(f"não identificado, fica onde está: {f.name}")
            continue
        destino = pasta / nome
        if destino.exists():
            continue
        shutil.move(f, destino)
        reg = {"data_acesso": data, "arquivo": destino.relative_to(RAIZ).as_posix(), "url_base": url, "n_requisicoes": 1,
               "bytes": destino.stat().st_size, "sha256": sha256(destino)}
        regs.append(reg)
        registrar_busca(FONTE_DADOS, consulta, linhas, SCRIPT, data, parametros, reg, ids)
    caminho = MANIFESTOS / "stf.csv"
    novo = not caminho.exists()
    with caminho.open("a", encoding="utf-8", newline="") as m:
        w = csv.DictWriter(m, fieldnames=["data_acesso", "arquivo", "url_base", "n_requisicoes", "bytes", "sha256"], lineterminator="\n")
        if novo:
            w.writeheader()
        w.writerows(regs)
    ids.salvar()
    print(f"{len(regs)} arquivos registrados: {[r['arquivo'] for r in regs]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    registrar_manuais(ap.parse_args().data)
