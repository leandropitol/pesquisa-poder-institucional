"""Composição do STF: ministros em exercício de 2003 em diante, indicação presidencial e aprovação no Senado (D-058).

Fontes primárias:
  1. Portal do STF, lido no navegador embutido (o portal recusa clientes Python): listas de ministros por
     antiguidade e por indicação presidencial, o detalhamento JSON das indicações por presidente, a página
     "Composição Atual", notícias oficiais que completam datas ausentes, as páginas "Dados e Datas" da Biblioteca (mensagem de indicação, apreciação no Senado,
     decreto de nomeação, termo de posse e decreto de aposentadoria, com citação do DOU) e as biografias.
     O navegador devolve cada resposta em base64 com o sha256 calculado lá; este módulo confere o sha256,
     grava os bytes sem alteração e registra cada página em `buscas`.
  2. Senado, dados abertos: matéria, movimentações e votação de mensagens de indicação ao STF
     (por ora, a MSF 7/2026, rejeitada).

Uso:
    python -m src.coleta.stf_ministros --data AAAA-MM-DD --capturas <arquivo> [<arquivo> ...]
    python -m src.coleta.stf_ministros --data AAAA-MM-DD --senado 173452
"""

import argparse
import base64
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from src.base import RegistroIds
from src.coleta.comum import Cliente, Execucao, registrar_busca

SCRIPT = "src.coleta.stf_ministros"
FONTE_STF = "Portal do STF (navegador embutido, mesma origem)"
FONTE_SENADO = "Senado, dados abertos"
API_SENADO = "https://legis.senado.leg.br/dadosabertos"


def nome_arquivo(url: str) -> str:
    """Nome estável no bruto a partir da URL da página do STF."""
    q = {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}
    if "detalhamento" in q:
        return f"indicacoes_presidente_{q['entidade']}.json"
    if "consulta" in q:
        return f"lista_{q['consulta'].lower()}.html"
    if "pagina" in q:
        pagina = q["pagina"]
        return "composicao_atual.html" if pagina == "ComposicaoAtual" else f"dados_datas_{re.sub('DadosDatas$', '', pagina)}.html"
    if urlparse(url).path.endswith("verNoticiaDetalhe.asp"):
        return f"noticia_stf_{q['idConteudo']}.html"
    if urlparse(url).path.endswith("verMinistro.asp"):
        return f"biografia_{q['id']}.html"
    raise ValueError(f"URL não prevista: {url}")


def ler_captura(caminho: Path) -> dict:
    """Arquivo salvo pela ferramenta do navegador: lista [{type, text}] cujo texto começa por uma string JSON."""
    externo = json.loads(caminho.read_text(encoding="utf-8"))
    texto, _ = json.JSONDecoder().raw_decode(externo[0]["text"])
    return json.loads(texto)


def importar_capturas(arquivos: list[Path], data: str) -> None:
    execucao, ids = Execucao("stf_ministros", data), RegistroIds()
    regs = []
    for arq in arquivos:
        lote = ler_captura(arq)
        for p in lote["paginas"]:
            corpo = base64.b64decode(p["base64"])
            if hashlib.sha256(corpo).hexdigest() != p["sha256"] or len(corpo) != p["bytes"]:
                raise ValueError(f"sha256 ou tamanho não confere: {p['url']}")
            nome = nome_arquivo(p["url"])
            destino = execucao.pasta / nome
            if destino.exists():
                raise FileExistsError(f"{destino} já existe: data/raw é imutável")
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(corpo)
            execucao.arquivos[nome] = {"url_base": p["url"], "n_requisicoes": 1}
            regs.append((nome, p, lote["lote"]))
    manifesto = {r["arquivo"].rsplit("/", 1)[1]: r for r in execucao.fechar()}
    for nome, p, lote in regs:
        registrar_busca(FONTE_STF, f"{lote}: {p['url']}", 1 if p["status"] == 200 else 0, SCRIPT, data,
                        {"url": p["url"], "status": p["status"]}, manifesto[nome], ids)
    ids.salvar()
    print(f"{len(regs)} páginas do STF gravadas em {execucao.pasta}")


def baixar_senado(codigos: list[str], data: str) -> None:
    cliente, execucao, ids = Cliente(), Execucao("stf_ministros", data), RegistroIds()
    chamadas = []
    for cod in codigos:
        for arquivo, url in [(f"senado_materia_{cod}.jsonl", f"{API_SENADO}/materia/{cod}.json"),
                             (f"senado_movimentacoes_{cod}.jsonl", f"{API_SENADO}/materia/movimentacoes/{cod}.json"),
                             (f"senado_votacao_{cod}.jsonl", f"{API_SENADO}/votacao?codigoMateria={cod}")]:
            r = cliente.get(url, headers={"Accept": "application/json"})
            execucao.gravar(arquivo, url, r, {"codigo_materia": cod})
            r.raise_for_status()
            chamadas.append((arquivo, url, cod))
    manifesto = {r["arquivo"].rsplit("/", 1)[1]: r for r in execucao.fechar()}
    for arquivo, url, cod in chamadas:
        registrar_busca(FONTE_SENADO, f"matéria {cod}: {url}", 1, SCRIPT, execucao.data, {"codigo_materia": cod}, manifesto[arquivo], ids)
    ids.salvar()
    print(f"{len(chamadas)} respostas do Senado gravadas")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--capturas", nargs="*", type=Path, default=[])
    ap.add_argument("--senado", nargs="*", default=[])
    a = ap.parse_args()
    if a.capturas:
        importar_capturas(a.capturas, a.data)
    if a.senado:
        baixar_senado(a.senado, a.data)
