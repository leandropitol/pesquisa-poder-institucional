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
# (coluna que identifica o painel, classes presentes) -> (nome no bruto, URL do painel, filtros aplicados, total mostrado no painel)
URL_DECISOES = "https://transparencia.stf.jus.br/extensions/decisoes/decisoes.html"
URL_ACERVO = "https://transparencia.stf.jus.br/extensions/acervo/acervo.html"
EXPORTACOES = {
    ("idFatoDecisao", ("AP", "Inq")): ("stf_corte_aberta_decisoes_AP_Inq_2003-01-08_a_2026-09-23.xlsx", URL_DECISOES,
                                       {"classe": ["AP", "Inq"], "data_decisao": ["2003-01-08", "2026-09-23"], "botao": "Decisões"}, 17202),
    ("Link do processo", ("AP", "Inq")): ("stf_corte_aberta_acervo_AP_Inq.xlsx", URL_ACERVO,
                                          {"classe": ["AP", "Inq"], "recorte": "acervo em tramitação na data da exportação", "botao": "Processos"}, 1331),
    ("idFatoDecisao", ("Pet",)): ("stf_corte_aberta_decisoes_Pet_penal_2003-02-05_a_2026-09-24.xlsx", URL_DECISOES,
                                  {"classe": ["Pet"], "ramo_direito": ["DIREITO PENAL", "DIREITO PENAL MILITAR", "DIREITO PROCESSUAL PENAL"],
                                   "data_decisao": ["2003-02-05", "2026-09-24"], "botao": "Decisões"}, 10994),
    ("Link do processo", ("Pet",)): ("stf_corte_aberta_acervo_Pet_criminal.xlsx", URL_ACERVO,
                                     {"classe": ["Pet"], "processo_criminal": "Criminal", "recorte": "acervo em tramitação na data da exportação",
                                      "botao": "Processos"}, 719),
}


def identificar(d: pd.DataFrame) -> tuple | None:
    """Chave de EXPORTACOES pela coluna característica do painel e pelas classes presentes na planilha."""
    classes = tuple(sorted(d["Processo"].str.split().str[0].unique())) if "Processo" in d else ()
    return next(((c, k) for c, k in EXPORTACOES if c in d.columns and tuple(sorted(k)) == classes), None)
URL_DADOS_ABERTOS = "https://transparencia.stf.jus.br/extensions/dados_abertos/dados_abertos.html"
LIMITE_CELULAS = 5_000_000
PORTAL_STF, PORTAL_TJMG = "https://portal.stf.jus.br", "https://www.tjmg.jus.br"
# arquivo entregue -> (nome no bruto, portal, quem navegou); o desfecho da AP 536 está no TJMG, para onde o STF declinou
RELATORIOS = {"relatorio_stf_pesquisa_documental.md": ("stf_relatorio_navegacao.md", PORTAL_STF, "Claude in Chrome"),
              "relatorio_corte_aberta.md": ("stf_relatorio_navegacao_peticoes.md", PORTAL_STF, "Claude in Chrome"),
              "relatorio_status_processual_reus.md": ("stf_relatorio_navegacao_reus_ap470_ap536.md", PORTAL_STF, "Claude in Chrome"),
              "AP470_relatorio_final.md": ("stf_relatorio_navegacao_ap470_embargos_noticias.md", PORTAL_STF, "Claude in Chrome"),
              "relatorio_partes_ap_lote1.md": ("stf_relatorio_navegacao_partes_ap_lote1.md", PORTAL_STF, "Claude in Chrome"),
              "relatorio_eduardo_azeredo_tjmg.md": ("tjmg_relatorio_navegacao_ap536_azeredo.md", PORTAL_TJMG, "Claude in Chrome"),
              "verificacao_claude_tjmg_acordaos.md": ("tjmg_verificacao_navegacao_acordaos_azeredo.md", PORTAL_TJMG,
                                                      "Claude Code no navegador embutido")}


def registrar_manuais(data: str) -> None:
    raiz = RAW / "stf"
    pasta = raiz / data
    pasta.mkdir(parents=True, exist_ok=True)
    ids, regs = RegistroIds(), []
    for f in sorted(p for p in raiz.iterdir() if p.is_file()):
        if f.suffix.lower() == ".xlsx":
            d = pd.read_excel(f, dtype=str)
            chave = identificar(d)
            if chave is None:
                print(f"não identificado, fica onde está: {f.name}")
                continue
            nome, url, filtros, total = EXPORTACOES[chave]
            anteriores = sorted(raiz.glob(f"*/{nome}"))  # já registrado em qualquer data
            if anteriores:
                igual = d.equals(pd.read_excel(anteriores[-1], dtype=str))
                print(f"{'cópia idêntica' if igual else 'ATENÇÃO: conteúdo diferente'} de {nome} já registrado; fica onde está: {f.name}")
                continue
            linhas = len(d)
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
        elif f.name in RELATORIOS:
            nome, url, quem = RELATORIOS[f.name]
            portal = "STF" if url == PORTAL_STF else "TJMG"
            consulta = f"relatório de navegação do {quem} no portal do {portal} (arquivo {nome}; registro auxiliar, não é fonte primária)"
            linhas = 1
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
