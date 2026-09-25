"""Coletor das resoluções do Conselho de Direitos Humanos da ONU (etapa E8, bloco A2).

A lista de votos de cada resolução adotada por votação registrada vem no fim do próprio texto oficial
("[Adopted by a recorded vote of 23 to 13, with 11 abstentions. The voting was as follows: In favour:
...]"). O site do Alto Comissariado recusa cliente automatizado (D-009); o repositório de documentos da
ONU entrega cada resolução pelo símbolo:
https://documents.un.org/api/symbol/access?s=A/HRC/RES/<sessão>/<n>&l=en&t=pdf

O repositório só entrega resoluções avulsas da 12ª sessão (2009) em diante; as das sessões 1 a 11 vêm dos
relatórios anuais do Conselho à Assembleia Geral (RELATORIOS). O coletor percorre as sessões ordinárias
de 12 a 70 e as especiais de S-1 a S-45, resolução por resolução, e encerra cada sessão depois de 3
símbolos seguidos sem documento. Grava os PDFs em data/raw/conselho_dh/<data>/.

Uso:
    python -m src.coleta.conselho_dh
"""

import argparse

from src.base import RegistroIds
from src.coleta.comum import Cliente, Execucao, registrar_busca

URL = "https://documents.un.org/api/symbol/access?s={simbolo}&l=en&t=pdf"
SCRIPT = "src.coleta.conselho_dh"
FONTE = "Nações Unidas, repositório oficial de documentos (resoluções do Conselho de Direitos Humanos)"


def simbolo(sessao: str, n: int) -> str:
    return f"A/HRC/RES/{sessao}/{n}"


def baixar_sessao(cliente: Cliente, ex: Execucao, sessao: str) -> int:
    n, faltas, achadas = 1, 0, 0
    while faltas < 3:
        s = simbolo(sessao, n)
        r = cliente.get(URL.format(simbolo=s), headers={"Accept": "*/*"})
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("application/pdf"):
            destino = ex.pasta / f"A_HRC_RES_{sessao}_{n}.pdf"
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(r.content)
            ex.arquivos[destino.name] = {"url_base": URL.format(simbolo=s), "n_requisicoes": 1}
            achadas, faltas = achadas + 1, 0
        else:
            faltas += 1
        n += 1
    return achadas


# Resoluções das sessões 1 a 11 (2006 a meados de 2009) não têm símbolo próprio no repositório; estão nos
# relatórios anuais do Conselho à Assembleia Geral. O de 2006 (A/61/53) não está disponível no repositório.
RELATORIOS = ["A/61/53", "A/62/53", "A/63/53", "A/63/53/Add.1", "A/64/53"]
PRIMEIRA_SESSAO_AVULSA, ULTIMA_SESSAO, ULTIMA_ESPECIAL = 12, 70, 45


def baixar_documento(cliente: Cliente, ex: Execucao, s: str) -> bool:
    r = cliente.get(URL.format(simbolo=s), headers={"Accept": "*/*"})
    if r.status_code == 200 and r.headers.get("content-type", "").startswith("application/pdf"):
        destino = ex.pasta / (s.replace("/", "_") + ".pdf")
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(r.content)
        ex.arquivos[destino.name] = {"url_base": URL.format(simbolo=s), "n_requisicoes": 1}
        return True
    return False


def coletar(data: str | None = None) -> None:
    cliente, ex = Cliente(pausa=1.0, tempo_limite=120), Execucao("conselho_dh", data)
    resumo = [(f"relatório {r}", int(baixar_documento(cliente, ex, r))) for r in RELATORIOS]
    sessoes = [str(k) for k in range(PRIMEIRA_SESSAO_AVULSA, ULTIMA_SESSAO + 1)] + [f"S-{k}" for k in range(1, ULTIMA_ESPECIAL + 1)]
    for sessao in sessoes:
        achadas = baixar_sessao(cliente, ex, sessao)
        resumo.append((f"resoluções da sessão {sessao} (A/HRC/RES/{sessao}/n)", achadas))
        print(f"sessão {sessao}: {achadas} resoluções")
    regs = ex.fechar()
    ids = RegistroIds()
    for consulta, achadas in resumo:
        registrar_busca(FONTE, consulta, achadas, SCRIPT, ex.data, {}, None, ids)
    ids.salvar()
    print(f"{len(regs)} documentos gravados")


if __name__ == "__main__":
    argparse.ArgumentParser().parse_args()
    coletar()
