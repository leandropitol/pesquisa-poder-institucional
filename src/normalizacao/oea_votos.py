"""Votações nominais nas atas da Assembleia Geral da OEA (etapa E8, bloco A3).

As atas (transcrição literal das sessões plenárias) registram a chamada de formas diferentes a cada ano:
o Presidente ou o Secretário chama a delegação ("Brasil.", "La Delegación del Brasil, ¿cuál es su voto?",
"Brazil, please cast your vote") e a delegação responde na fala seguinte ("El JEFE DE LA DELEGACIÓN DEL
BRASIL: Sí."). Por isso o ponto de partida é a tabela de curadoria data/curadoria/oea_votacoes.csv, com
uma linha por votação localizada na leitura das atas: o trecho literal do placar oficial (âncora), o objeto
votado e o placar digitado. O script confere tudo contra o texto:

1. a âncora precisa existir literalmente na ata;
2. cada número do placar precisa aparecer na âncora (em algarismos ou por extenso);
3. as falas curtas das delegações no bloco de chamada que antecede a âncora são lidas e contadas
   (`confere` indica se a contagem bate com o placar);
4. o voto do Brasil sai da fala da própria delegação, com o trecho literal guardado como localizador.

Saída em data/staging/oea/votacoes_resumo.csv e votacoes_nominais.csv.

Uso:
    python -m src.normalizacao.oea_votos
"""

import csv
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import pandas as pd

from src.base import RAIZ

RAW = RAIZ / "data" / "raw" / "oea"
CURADORIA = RAIZ / "data" / "curadoria" / "oea_votacoes.csv"
MANIFESTO = RAIZ / "data" / "manifestos" / "oea.csv"
SAIDA = RAIZ / "data" / "staging" / "oea"

PAISES = {
    "antigua y barbuda": "ATG", "antigua and barbuda": "ATG", "argentina": "ARG", "bahamas": "BHS", "barbados": "BRB", "belize": "BLZ",
    "belice": "BLZ", "bolivia": "BOL", "brasil": "BRA", "brazil": "BRA", "canada": "CAN", "chile": "CHL", "colombia": "COL",
    "costa rica": "CRI", "cuba": "CUB", "dominica": "DMA", "ecuador": "ECU", "el salvador": "SLV", "estados unidos": "USA",
    "united states": "USA", "grenada": "GRD", "granada": "GRD", "guatemala": "GTM", "guyana": "GUY", "haiti": "HTI", "honduras": "HND",
    "jamaica": "JAM", "mexico": "MEX", "nicaragua": "NIC", "panama": "PAN", "paraguay": "PRY", "peru": "PER",
    "republica dominicana": "DOM", "dominican republic": "DOM", "saint kitts y nevis": "KNA", "saint kitts and nevis": "KNA",
    "san cristobal y nieves": "KNA", "santa lucia": "LCA", "saint lucia": "LCA", "san vicente y las granadinas": "VCT",
    "saint vincent and the grenadines": "VCT", "suriname": "SUR", "trinidad y tobago": "TTO", "trinidad and tobago": "TTO",
    "uruguay": "URY", "venezuela": "VEN", "estados unidos mexicanos": "MEX",
    # grafias truncadas ou com erro de digitação nas atas ("SAINT KITTS AND ENEVIS", "SAN VICENTE Y LAS GRENADINAS")
    "saint kitts": "KNA", "san vicente": "VCT", "saint vincent": "VCT",
}
RE_PAIS = re.compile(r"\b(" + "|".join(re.escape(p) for p in sorted(PAISES, key=len, reverse=True)) + r")\b")

UNIDADES = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce", "trece", "catorce",
            "quince", "dieciseis", "diecisiete", "dieciocho", "diecinueve", "veinte", "veintiuno", "veintidos", "veintitres", "veinticuatro",
            "veinticinco", "veintiseis", "veintisiete", "veintiocho", "veintinueve", "treinta"]
UNITS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
         "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
EXTENSO = {w: i for i, w in enumerate(UNIDADES)} | {w: i for i, w in enumerate(UNITS)} | {"un": 1, "una": 1, "veintiun": 21}
for i, w in enumerate(UNITS[1:10], 1):
    EXTENSO[f"twenty-{w}"] = 20 + i
    EXTENSO[f"treinta y {UNIDADES[i]}"] = 30 + i
    if i <= 4:
        EXTENSO[f"thirty-{w}"] = 30 + i
EXTENSO |= {"twenty": 20, "thirty": 30}
RE_EXTENSO = re.compile(r"\b(" + "|".join(re.escape(w) for w in sorted(EXTENSO, key=len, reverse=True)) + r")\b")

# Fala: rótulo do orador em maiúsculas ("El JEFE DE LA DELEGACIÓN DEL BRASIL:") seguido do que foi dito
RE_TURNO = re.compile(r"\b(?:El|La|Los|Las|EL|LA)\s+([A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜé ,.\-]{2,150}?)\s*:\s")
MESA = re.compile(r"PRESIDENT|SECRETARI|ESCRUT", re.I)
FALA_VOTO = 250    # resposta de voto é curta; falas longas são debate
FALA_DEBATE = 600  # fala longa encerra (para trás) o bloco da chamada
RE_REPETICAO = re.compile(r"(" + RE_PAIS.pattern + r")\s*,?\s*(?:votes?\s+|vota\s+)?(yes|no|in favou?r|against|abstains?|abstained|abstention|a favor|en contra|abstenci[oó]n)\b")
MESES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"], 1)}


def sem_acento(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower().strip()


def pais_no_rotulo(rotulo: str) -> str | None:
    m = RE_PAIS.search(sem_acento(rotulo))
    return PAISES[m.group(1)] if m else None


def normalizar_voto(v: str) -> str | None:
    v = sem_acento(v)
    if re.search(r"abst", v):
        return "abstencao"
    if re.search(r"en contra|against|opposed|\bcontra\b|\bno\b|\bnao\b", v):
        return "nao"
    if re.search(r"a favor|in favou?r|faveur|in support|\bsi\b|\bsim\b|\byes\b|\boui\b|afirmativ", v):
        return "sim"
    return None


def numeros(trecho: str) -> set[int]:
    """Números citados no trecho, em algarismos ou por extenso (espanhol e inglês)."""
    t = sem_acento(trecho)
    return {int(x) for x in re.findall(r"\d+", t)} | {EXTENSO[w] for w in RE_EXTENSO.findall(t)}


def placar_confere_ancora(placar: dict, ancora: str) -> list[str]:
    """Campos do placar cujo número não aparece na âncora (lista vazia = digitação conferida)."""
    achados = numeros(ancora)
    return [k for k, v in placar.items() if v and v not in achados]


def turnos(t: str) -> list[tuple[int, int, str, str]]:
    """(início, fim, rótulo, fala) de cada fala do texto."""
    ms = list(RE_TURNO.finditer(t))
    return [(m.start(), ms[i + 1].start() if i + 1 < len(ms) else len(t), m.group(1).strip(), t[m.end():ms[i + 1].start() if i + 1 < len(ms) else len(t)].strip())
            for i, m in enumerate(ms)]


def bloco_da_chamada(ts: list, pos: int, inicio_min: int = 0) -> list:
    """Falas da chamada: do placar para trás, até a primeira fala longa (debate) ou até a votação anterior."""
    i = max((k for k, x in enumerate(ts) if x[0] <= pos), default=-1)
    bloco = []
    for x in reversed(ts[:i]):
        if x[0] < inicio_min or len(x[3]) > FALA_DEBATE:
            break
        bloco.append(x)
    return bloco[::-1]


def ler_votos(bloco: list) -> tuple[dict, dict]:
    """Votos por país (última resposta vale) e o trecho literal de cada resposta."""
    votos, trechos = {}, {}
    for ini, fim, rotulo, fala in bloco:
        if MESA.search(rotulo) or len(fala) > FALA_VOTO:
            continue
        iso, voto = pais_no_rotulo(rotulo), normalizar_voto(fala)
        if iso and voto:
            votos[iso], trechos[iso] = voto, f"{rotulo}: {fala}"[:300]
    for ini, fim, rotulo, fala in bloco:  # a mesa repete o voto de quem respondeu sem dizê-lo ("Thank you")
        if not MESA.search(rotulo):
            continue
        for m in RE_REPETICAO.finditer(sem_acento(fala)):
            if re.match(r"\s*(?:esta\s+)?presente|\s*present", sem_acento(fala)[m.end():]):
                continue  # "Uruguay, no está presente": ausência, não voto contrário
            iso, voto = PAISES[m.group(2)], normalizar_voto(m.group(3))
            if iso not in votos and voto:
                votos[iso], trechos[iso] = voto, f"{rotulo} (repetição da mesa): {fala}"[:300]
    return votos, trechos


def data_da_sessao(t: str, pos: int) -> str:
    datas = [m for m in re.finditer(r"Fecha:\s*(\d{1,2}) de (\w+) de (\d{4})", t) if m.start() < pos]
    if not datas:
        return ""
    d, mes, ano = datas[-1].groups()
    return f"{ano}-{MESES[sem_acento(mes)]:02d}-{int(d):02d}"


@lru_cache(maxsize=None)
def texto_ata(nome: str) -> str:
    from src.normalizacao.oea import texto_doc, texto_docx
    caminho = next(RAW.glob(f"*/{nome}"))
    return " ".join((texto_docx(caminho) if caminho.suffix.lower() == ".docx" else texto_doc(caminho)).split())


def conferir(linha: dict, t: str, inicio_min: int = 0) -> dict:
    pos = t.find(linha["ancora_placar"])
    if pos < 0:
        raise ValueError(f"âncora não encontrada em {linha['ata']}: {linha['ancora_placar'][:60]}")
    placar = {k: int(linha[f"placar_{k}"] or 0) for k in ("sim", "nao", "abstencao", "ausente")}
    faltam = placar_confere_ancora(placar, linha["ancora_placar"])
    if faltam:
        raise ValueError(f"placar digitado não aparece na âncora ({faltam}): {linha['ancora_placar'][:60]}")
    votos, trechos = ({}, {})
    if linha["modalidade"] == "votacao_registrada":
        votos, trechos = ler_votos(bloco_da_chamada(turnos(t), pos, inicio_min))
    contagem = {k: sum(1 for v in votos.values() if v == k) for k in ("sim", "nao", "abstencao")}
    return {"posicao": pos, "data": data_da_sessao(t, pos), "placar": placar, "contagem": contagem,
            "confere": bool(votos) and all(contagem[k] == placar[k] for k in contagem), "votos": votos, "trechos": trechos}


def votacoes() -> list[dict]:
    cur = list(csv.DictReader(CURADORIA.open(encoding="utf-8")))
    saida, anterior = [], {}
    for linha in sorted(cur, key=lambda l: (l["ata"], texto_ata(l["ata"]).find(l["ancora_placar"]))):
        t = texto_ata(linha["ata"])
        r = conferir(linha, t, anterior.get(linha["ata"], 0))
        anterior[linha["ata"]] = r["posicao"] + len(linha["ancora_placar"])
        saida.append({**linha, **r})
    return saida


def run() -> None:
    vs = votacoes()
    resumo, linhas = [], []
    for i, v in enumerate(vs, 1):
        ident = f"{v['ata']}@{v['posicao']}"
        resumo.append({"votacao": ident, "data": v["data"], "objeto": v["objeto"], "simbolo": v["simbolo"], "descricao": v["descricao"], "decisao": v["decisao"],
                       **{f"placar_{k}": x for k, x in v["placar"].items()}, **{f"lidos_{k}": x for k, x in v["contagem"].items()},
                       "confere": v["confere"], "voto_brasil": v["votos"].get("BRA", ""), "trecho_brasil": v["trechos"].get("BRA", "")})
        linhas += [{"votacao": ident, "pais_iso3": p, "voto": x, "trecho": v["trechos"][p]} for p, x in sorted(v["votos"].items())]
    SAIDA.mkdir(parents=True, exist_ok=True)
    r = pd.DataFrame(resumo)
    r.to_csv(SAIDA / "votacoes_resumo.csv", index=False, encoding="utf-8")
    pd.DataFrame(linhas).to_csv(SAIDA / "votacoes_nominais.csv", index=False, encoding="utf-8")
    with pd.option_context("display.width", 250, "display.max_colwidth", 60):
        print(r[["data", "objeto", "simbolo", "placar_sim", "placar_nao", "placar_abstencao", "lidos_sim", "lidos_nao", "lidos_abstencao", "confere", "voto_brasil", "trecho_brasil"]].to_string())


if __name__ == "__main__":
    run()
