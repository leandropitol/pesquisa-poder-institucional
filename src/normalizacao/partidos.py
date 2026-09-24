"""Partidos como registros no TSE, com denominações no tempo (etapa E1).

Lê a captura da página de partidos do TSE (data/raw/tse_partidos) e monta:

- um partido (instituição de tipo `partido`) por registro no TSE. Mudança de nome ou de sigla
  mantém o partido; fusão cria partido novo; incorporação encerra o incorporado;
- `denominacoes_partido`: sigla e nome de cada partido, com início e fim;
- `relacoes`: `fundiu_se_em` e `incorporado_por`, com o processo e a data da decisão do TSE.

`Resolvedor` responde qual partido usava uma sigla numa data. Siglas que o TSE não usa (por
exemplo, "SDD" nos registros da Câmara) são ligadas pelo nome que a própria fonte dá ao partido
(`apelidos_por_nome`). O que não se resolve fica registrado como pendência.

Uso (pela normalização legislativa):
    from src.normalizacao.partidos import montar_partidos
"""

import csv
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from src.base import RAIZ, RegistroIds

RAW = RAIZ / "data" / "raw" / "tse_partidos"
MANIFESTO = RAIZ / "data" / "manifestos" / "tse_partidos.csv"
URL_TSE = "https://www.tse.jus.br/partidos/partidos-registrados-no-tse"


# ------------------------------------------------------------------ texto
def norm_sigla(s: str) -> str:
    return re.sub(r"\s+", "", (s or "").replace("*", "").strip().rstrip(".")).upper()


def norm_nome(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii")
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s.lower()).split())


def sigla_e_nome(texto: str) -> tuple[str, str]:
    """'Partido da Frente Liberal (PFL)' -> ('PFL', 'Partido da Frente Liberal'); 'AVANTE' -> ('AVANTE', 'AVANTE')."""
    t = texto.replace("*", "").strip().rstrip(".").strip()
    m = re.search(r"^(.*)\(([^()]+)\)\s*$", t)
    if m:
        return norm_sigla(m.group(2)), m.group(1).strip()
    return norm_sigla(t), t


def partidos_da_celula(texto: str) -> list[tuple[str, str]]:
    """Separa 'A (X) e B (Y)' em [(X, A), (Y, B)]."""
    partes = re.split(r"(?<=\))\s+e\s+", texto.strip())
    return [sigla_e_nome(p) for p in partes]


def data_iso(texto: str) -> str:
    t = texto.replace("°", "").replace("º", "").strip()
    m = re.match(r"^(\d{1,2})[./](\d{1,2})[./](\d{4})$", t)
    if not m:
        raise ValueError(f"data fora do formato esperado: {texto!r}")
    d, mes, a = m.groups()
    return f"{a}-{int(mes):02d}-{int(d):02d}"


# ------------------------------------------------------------------ linhagem
@dataclass
class Denominacao:
    sigla: str
    nome: str
    inicio: str = ""
    fim: str = ""


@dataclass
class Partido:
    denominacoes: list[Denominacao] = field(default_factory=list)
    fim: str = ""
    destino: tuple[str, "Partido", str, str] | None = None  # (tipo_relacao, partido, processo, localizador)
    registrado: dict | None = None

    @property
    def chave(self) -> str:
        siglas = []
        for d in self.denominacoes:
            if not siglas or siglas[-1] != d.sigla:
                siglas.append(d.sigla)
        return "partido_tse:" + "|".join(siglas) + (f"|ate:{self.fim}" if self.fim else "")

    def adicionar(self, sigla: str, nome: str, inicio: str) -> None:
        self.denominacoes.append(Denominacao(sigla, nome, inicio))


def eventos(tabelas: list[dict]) -> tuple[list[dict], list[dict]]:
    """Eventos (fusão, incorporação, mudança) em ordem de data, e partidos registrados hoje."""
    t = {x["i"]: x["linhas"] for x in tabelas}
    evs = []
    for tipo, i in (("fusao", 1), ("incorporacao", 2), ("mudanca", 3)):
        for n, linha in enumerate(t[i][1:], 1):
            if len(linha) < 5 or not linha[0].strip().isdigit():
                continue
            evs.append({"tipo": tipo, "origens": partidos_da_celula(linha[1]), "destino": sigla_e_nome(linha[2]),
                        "processo": linha[3], "data": data_iso(linha[4]), "localizador": f"tabela {i}, linha {n}"})
    ordem = {"mudanca": 0, "incorporacao": 1, "fusao": 2}
    evs.sort(key=lambda e: (e["data"], ordem[e["tipo"]]))
    registrados = [{"sigla": norm_sigla(l[1]), "nome": l[2].strip(), "deferimento": data_iso(l[3]), "numero": l[5].strip(), "localizador": f"tabela 0, linha {n}"}
                   for n, l in enumerate(t[0][1:], 1) if len(l) >= 6 and l[0].strip().isdigit()]
    return evs, registrados


def linhagem(tabelas: list[dict]) -> list[Partido]:
    evs, registrados = eventos(tabelas)
    ativo: dict[str, Partido] = {}
    ultimo_com_sigla: dict[str, Partido] = {}
    todos: list[Partido] = []

    def novo(sigla: str, nome: str, inicio: str = "") -> Partido:
        p = Partido()
        p.adicionar(sigla, nome, inicio)
        todos.append(p)
        ativo[sigla] = ultimo_com_sigla[sigla] = p
        return p

    def pegar(sigla: str, nome: str) -> Partido:
        return ativo.pop(sigla, None) or novo_e_remove(sigla, nome)

    def novo_e_remove(sigla: str, nome: str) -> Partido:
        p = novo(sigla, nome)
        ativo.pop(sigla)
        return p

    def encerrar(p: Partido, data: str) -> None:
        p.denominacoes[-1].fim = data
        p.fim = data

    for e in evs:
        if e["tipo"] == "mudanca":
            (s0, n0), (s1, n1) = e["origens"][0], e["destino"]
            p = pegar(s0, n0)
            p.denominacoes[-1].fim = e["data"]
            p.adicionar(s1, n1, e["data"])
            ativo[s1] = ultimo_com_sigla[s1] = p
        elif e["tipo"] == "incorporacao":
            s1, n1 = e["destino"]
            alvo = ativo.get(s1) or ultimo_com_sigla.get(s1) or novo(s1, n1)
            for s0, n0 in e["origens"]:
                p = pegar(s0, n0)
                encerrar(p, e["data"])
                p.destino = ("incorporado_por", alvo, e["processo"], e["localizador"])
        else:  # fusão
            s1, n1 = e["destino"]
            origens = [pegar(s0, n0) for s0, n0 in e["origens"]]
            p_novo = novo(s1, n1, e["data"])
            for p in origens:
                encerrar(p, e["data"])
                p.destino = ("fundiu_se_em", p_novo, e["processo"], e["localizador"])
    for r in registrados:
        p = ativo.get(r["sigla"]) or novo(r["sigla"], r["nome"], r["deferimento"])
        p.registrado = r
        if not p.denominacoes[0].inicio:
            p.denominacoes[0].inicio = r["deferimento"]
        p.denominacoes[-1].nome = r["nome"]
    return todos


def vivo(p: Partido, data: str) -> bool:
    ini = p.denominacoes[0].inicio
    return (not ini or ini[:len(data)] <= data) and (not p.fim or data < p.fim)


class Resolvedor:
    """Qual partido usava a sigla na data? Devolve (partido, método).

    Métodos, em ordem: `vigencia` (a denominação com essa sigla estava em vigor na data);
    `partido_existente` (a fonte usou a sigla fora da vigência, e só um dos partidos que já usaram a
    sigla existia na data; é o caso de fontes que gravam a sigla atual em registros antigos);
    `mais_proxima` (denominação mais próxima no tempo); `sem_correspondencia`."""

    def __init__(self, partidos: list[Partido], apelidos: dict[str, list[str]] | None = None):
        self.por_sigla: dict[str, list[tuple[Denominacao, Partido]]] = {}
        for p in partidos:
            for d in p.denominacoes:
                self.por_sigla.setdefault(d.sigla, []).append((d, p))
        self.apelidos = apelidos or {}

    def __call__(self, sigla: str, data: str) -> tuple[Partido | None, str]:
        s = norm_sigla(sigla)
        siglas = [s] if s in self.por_sigla else self.apelidos.get(s, [])
        cands = [c for x in siglas for c in self.por_sigla.get(x, [])]
        if not cands:
            return None, "sem_correspondencia"
        for d, p in cands:
            if (not d.inicio or d.inicio[:len(data)] <= data) and (not d.fim or data < d.fim):
                return p, "vigencia"
        existentes = {id(p): p for _, p in cands if vivo(p, data)}
        if len(existentes) == 1:
            return next(iter(existentes.values())), "partido_existente"

        def distancia(d: Denominacao) -> int:
            return min(abs_dias(data, x) for x in (d.inicio, d.fim) if x) if (d.inicio or d.fim) else 10**9
        return min(cands, key=lambda c: distancia(c[0]))[1], "mais_proxima"


def abs_dias(a: str, b: str) -> int:
    from datetime import date
    da = date.fromisoformat((a + "-01-01")[:10] if len(a) == 4 else (a + "-01")[:10] if len(a) == 7 else a)
    db = date.fromisoformat((b + "-01-01")[:10] if len(b) == 4 else (b + "-01")[:10] if len(b) == 7 else b)
    return abs((da - db).days)


def apelidos_por_nome(partidos: list[Partido], siglas_fonte: dict[str, str]) -> dict[str, list[str]]:
    """Liga sigla da fonte sem correspondência no TSE às siglas do partido do TSE com o mesmo nome.

    `siglas_fonte`: sigla -> nome, como a própria fonte (Câmara, Senado) publica. Só liga quando o
    nome normalizado aponta para um único partido."""
    por_nome: dict[str, dict[int, Partido]] = {}
    conhecidas = {d.sigla for p in partidos for d in p.denominacoes}
    for p in partidos:
        for d in p.denominacoes:
            por_nome.setdefault(norm_nome(d.nome), {})[id(p)] = p
    saida = {}
    for s, nome in siglas_fonte.items():
        s = norm_sigla(s)
        if s in conhecidas:
            continue
        alvo = list(por_nome.get(norm_nome(nome), {}).values())
        if len(alvo) == 1:
            saida[s] = sorted({d.sigla for d in alvo[0].denominacoes})
    return saida


# ------------------------------------------------------------------ base
def ultima_captura() -> tuple[dict, list[dict]]:
    man = list(csv.DictReader(MANIFESTO.open(encoding="utf-8")))
    reg = max(man, key=lambda m: m["data_acesso"])
    return reg, json.loads((RAIZ / reg["arquivo"]).read_text(encoding="utf-8"))["tabelas"]


def montar_partidos(ids: RegistroIds) -> dict:
    reg, tabelas = ultima_captura()
    partidos = linhagem(tabelas)
    tse = ids.obter("instituicoes", "orgao:TSE")
    fonte = ids.obter("fontes", f"raw:{reg['arquivo']}")
    instituicoes = [{"id_instituicao": tse, "nome": "Tribunal Superior Eleitoral", "sigla": "TSE", "tipo_instituicao": "tribunal",
                     "poder": "judiciario", "esfera": "federal", "pais_iso3": "BRA"}]
    fontes = [{"id_fonte": fonte, "tipo_fonte": "oficial", "titulo": "Tribunal Superior Eleitoral: partidos registrados; fusões, incorporações e mudanças de nome ou sigla",
               "data_publicacao": reg["data_acesso"], "url": URL_TSE, "data_acesso": reg["data_acesso"], "sha256": reg["sha256"],
               "caminho_raw": reg["arquivo"], "licenca": "Dados públicos (Lei 12.527/2011)",
               "observacao": "Tabelas extraídas do DOM no navegador do aplicativo (D-015); sha256 conferido com o calculado no navegador"}]
    oficiais = [{"id_fonte": fonte, "id_orgao": tse, "tipo_documento": "Página institucional com tabelas de partidos", "data_documento": reg["data_acesso"], "link": URL_TSE}]
    id_de = {id(p): ids.obter("instituicoes", p.chave) for p in partidos}
    denominacoes, relacoes, rel_fonte = [], [], []
    for p in partidos:
        ult = p.denominacoes[-1]
        obs = "Registro no TSE"
        if p.registrado:
            obs += f", deferido em {p.registrado['deferimento']}, legenda {p.registrado['numero']}"
        if p.fim:
            obs += f"; encerrado em {p.fim}"
        instituicoes.append({"id_instituicao": id_de[id(p)], "nome": ult.nome, "sigla": ult.sigla, "tipo_instituicao": "partido",
                             "poder": "nao_se_aplica", "esfera": "federal", "pais_iso3": "BRA",
                             "id_sucessora": id_de[id(p.destino[1])] if p.destino else "", "observacao": obs})
        for d in p.denominacoes:
            denominacoes.append({"id_denominacao": ids.obter("denominacoes_partido", f"{p.chave}:{d.sigla}:{d.inicio}"), "id_partido": id_de[id(p)],
                                 "sigla": d.sigla, "nome": d.nome, "data_inicio": d.inicio, "data_fim": d.fim, "id_fonte": fonte})
        if p.destino:
            tipo, alvo, processo, loc = p.destino
            r = ids.obter("relacoes", f"{p.chave}>{tipo}")
            relacoes.append({"id_relacao": r, "origem_tipo": "instituicao", "origem_id": id_de[id(p)], "tipo_relacao": tipo,
                             "destino_tipo": "instituicao", "destino_id": id_de[id(alvo)], "data_inicio": p.fim, "nivel_confianca": "documentado"})
            rel_fonte.append({"id_relacao": r, "id_fonte": fonte, "localizador": f"{loc}; {processo}"})
    return {"partidos": partidos, "id_de": id_de, "instituicoes": instituicoes, "fontes": fontes, "fonte_oficial": oficiais,
            "denominacoes_partido": denominacoes, "relacoes": relacoes, "relacao_fonte": rel_fonte, "fonte": fonte}
