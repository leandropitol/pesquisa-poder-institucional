"""Normalização dos atos bilaterais do Concórdia (etapa E8, bloco B) para `acordos_bilaterais`.

Entram todos os atos bilaterais (tipo BL) com um país como outra parte, de todos os anos, para dar
denominador (protocolo, eixo 2). O país vem da lista de países do próprio Concórdia (nome e sigla ISO)
e, para os nomes que não estão nela, de data/curadoria/concordia_partes.csv (Estados extintos, grafias
diferentes). Atos com organismo internacional como outra parte ficam fora da tabela e são contados nas
limitações. A data de entrada em vigor vem do detalhe do ato, coletado para os atos de 2003 em diante.

Uso:
    python -m src.normalizacao.concordia
"""

import csv
import json
import unicodedata
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, gravar, ler

MANIFESTO = RAIZ / "data" / "manifestos" / "concordia.csv"
CURADORIA = RAIZ / "data" / "curadoria" / "concordia_partes.csv"
LINK = "https://concordia.itamaraty.gov.br/detalhamento-acordo/{id}"


def norm(s: str | None) -> str:
    return " ".join(unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii").lower().split())


def data_iso(s: str | None) -> str:
    s = (s or "").strip()
    return f"{s[6:10]}-{s[3:5]}-{s[0:2]}" if len(s) == 10 and s[2] == "/" and s[5] == "/" else ""


def ultimo(nome: str) -> dict | None:
    man = [m for m in csv.DictReader(MANIFESTO.open(encoding="utf-8")) if m["arquivo"].endswith("/" + nome)]
    return max(man, key=lambda m: m["data_acesso"]) if man else None


def linhas_jsonl(reg: dict) -> list:
    with (RAIZ / reg["arquivo"]).open(encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def mapa_partes() -> dict[str, tuple[str, str]]:
    """Nome normalizado da outra parte -> (decisão, ISO3)."""
    reg = ultimo("paises.jsonl")
    mapa = {norm(p["Nome"]): ("pais", p["Sigla"]) for l in linhas_jsonl(reg) for p in l["corpo"]}
    for l in csv.DictReader(CURADORIA.open(encoding="utf-8")):
        mapa[norm(l["parte"])] = (l["decisao"], l["pais_iso3"])
    return mapa


def tema(assuntos: list | None) -> str:
    principais = [a["Nome"] for a in (assuntos or []) if a.get("IsPrincipal")] or [a["Nome"] for a in (assuntos or [])]
    return "; ".join(principais)


def montar(ids: RegistroIds) -> dict:
    reg_lista, reg_det = ultimo("lista_atos.jsonl"), ultimo("detalhes_bilaterais.jsonl")
    itens = [i for l in linhas_jsonl(reg_lista) for i in l["corpo"]["Items"]]
    detalhes = {}
    if reg_det:
        for l in linhas_jsonl(reg_det):
            if l["corpo"]:
                detalhes[str(l["params"]["id"])] = l["corpo"]
    mre = ids.obter("instituicoes", "orgao:MRE")
    inst = [{"id_instituicao": mre, "nome": "Ministério das Relações Exteriores", "sigla": "MRE", "tipo_instituicao": "orgao_publico",
             "poder": "executivo", "esfera": "federal", "pais_iso3": "BRA"}]
    fontes, oficiais = [], []
    for reg, titulo in ((reg_lista, "lista de todos os atos"), (reg_det, "detalhe dos atos bilaterais de 2003 em diante")):
        if not reg:
            continue
        f = ids.obter("fontes", f"raw:{reg['arquivo']}")
        fontes.append({"id_fonte": f, "tipo_fonte": "oficial", "titulo": f"Itamaraty, Concórdia (atos internacionais): {titulo}", "data_publicacao": reg["data_acesso"],
                       "url": "https://concordia.itamaraty.gov.br/", "data_acesso": reg["data_acesso"], "sha256": reg["sha256"], "caminho_raw": reg["arquivo"],
                       "licenca": "Dados públicos (Lei 12.527/2011)", "observacao": "Interface pública usada pelo próprio site (aplicacao.itamaraty.gov.br/ApiConcordia)"})
        oficiais.append({"id_fonte": f, "id_orgao": mre, "tipo_documento": "Registro de atos internacionais (Concórdia)", "data_documento": reg["data_acesso"],
                         "link": "https://concordia.itamaraty.gov.br/"})
    f_lista = ids.obter("fontes", f"raw:{reg_lista['arquivo']}")
    f_det = ids.obter("fontes", f"raw:{reg_det['arquivo']}") if reg_det else ""
    partes = mapa_partes()
    acordos, contagem = [], {"organismo": 0, "sem_parte": 0, "sem_data": 0, "pais": 0, "nao_bilateral": 0}
    for i in itens:
        if i["TipoAcordo"] != "BL":
            contagem["nao_bilateral"] += 1
            continue
        decisao, iso = partes.get(norm(i.get("OutraParte")), ("organismo", ""))
        if decisao != "pais":
            contagem[decisao] += 1
            continue
        assinatura = data_iso(i.get("DataCelebracao"))
        if not assinatura:
            contagem["sem_data"] += 1
            continue
        det = detalhes.get(str(i["Id"]))
        vigor = data_iso(((det or {}).get("Vigencia") or {}).get("DataEntradaVigor"))
        acordos.append({"id_acordo": ids.obter("acordos_bilaterais", f"concordia:{i['Id']}"), "pais_iso3": iso, "titulo": i["Titulo"].strip(),
                        "tema": tema(i.get("Assuntos")) or "Não informado", "data_assinatura": assinatura, "data_vigencia": vigor,
                        "situacao": i.get("Vigencia") or "", "id_concordia": str(i["Id"]), "link": LINK.format(id=i["Id"]),
                        "id_fonte": f_det if det else f_lista})
        contagem["pais"] += 1
    return {"instituicoes": inst, "fontes": fontes, "fonte_oficial": oficiais, "acordos_bilaterais": acordos, "contagem": contagem,
            "detalhes": len(detalhes)}


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    for nome in ("fontes", "fonte_oficial"):
        atual = ler(nome, base)
        novas = [l for l in r[nome] if l["id_fonte"] not in set(atual["id_fonte"])]
        gravar(nome, pd.concat([atual, pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    atual = ler("instituicoes", base)
    novas = pd.DataFrame(r["instituicoes"], dtype=str)
    gravar("instituicoes", pd.concat([atual[~atual["id_instituicao"].isin(novas["id_instituicao"])], novas], ignore_index=True), base)
    gravar("acordos_bilaterais", pd.DataFrame(r["acordos_bilaterais"], dtype=str), base)
    ids.salvar()


def run() -> None:
    ids = RegistroIds()
    r = montar(ids)
    gravar_resultado(r, ids)
    a = pd.DataFrame(r["acordos_bilaterais"])
    print(f"contagem: {r['contagem']}; detalhes lidos: {r['detalhes']}")
    print(f"atos bilaterais com país: {len(a)}; desde 2003: {int((a['data_assinatura'] >= '2003').sum())}; com data de vigência: {int((a['data_vigencia'] != '').sum())}")


if __name__ == "__main__":
    run()
