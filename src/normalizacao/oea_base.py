"""Carga da Assembleia Geral da OEA (etapa E8, bloco A3) em `votos_multilaterais`.

Entram as resoluções com decisão final `inclui` em data/curadoria/oea_resolucoes_ag_curadoria.csv
e as votações de data/curadoria/oea_votacoes.csv com decisão `inclui`, desta forma:

- votação registrada (chamada nominal) em que a contagem lida bate com o placar oficial: voto de cada
  país, com o trecho literal da resposta da delegação;
- votação registrada em que a contagem não bate: só o voto do Brasil, lido na fala da própria delegação;
- votação de mão erguida: nenhuma linha por país (a ata só dá o total); consta das limitações;
- resolução sem votação no plenário (conforme a ata da sessão): uma linha para o Brasil (`consenso` ou
  `consenso_com_nota`) e uma para cada outro país que registrou nota de rodapé (`consenso_com_nota`),
  com o texto da nota;
- resolução de sessão cuja ata não foi obtida: nenhuma linha, porque não dá para dizer se houve
  votação; consta das limitações, com as notas do Brasil, se houver.

A autoria da nota é o primeiro Estado membro citado no início dela ("La Delegación de Brasil no apoya...").

Uso:
    python -m src.normalizacao.oea_base
"""

import csv
import hashlib
import html
import re
import zipfile
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, gravar, ler
from src.normalizacao import oea_votos as ov
from src.normalizacao.oea import CURADORIA as CURADORIA_RES
from src.normalizacao.oea import MANIFESTO, criterio, dividir, texto_doc

RE_SESSAO = re.compile(r"\(([IVXLCDM]+-[OE])/\d{2}\)")
SAIDA = RAIZ / "data" / "staging" / "oea"


def texto_docx_com_notas(caminho: Path) -> tuple[str, list]:
    """Texto do volume com as chamadas de nota como [n], e as notas (posição, número, texto)."""
    with zipfile.ZipFile(caminho) as z:
        doc = z.read("word/document.xml").decode("utf-8")
        fn = z.read("word/footnotes.xml").decode("utf-8") if "word/footnotes.xml" in z.namelist() else ""
    doc = re.sub(r'<w:footnoteReference [^>]*w:id="(\d+)"[^>]*/>', r"[\1]", doc)
    doc = re.sub(r"<w:instrText[^>]*>.*?</w:instrText>", "", doc)  # códigos de campo (índice), fora do texto visível
    doc = re.sub(r"<w:(?:br|cr)\b[^>]*/>", "\n", doc).replace("</w:p>", "\n").replace("<w:tab/>", " ")
    texto = html.unescape(re.sub(r"<[^>]+>", "", doc))
    notas = [(len(texto), m.group(1), " ".join(html.unescape(re.sub(r"<[^>]+>", "", m.group(2).replace("</w:p>", " "))).split()))
             for m in re.finditer(r'<w:footnote [^>]*w:id="(\d+)"[^>]*>(.*?)</w:footnote>', fn, re.S)]
    return texto, notas


def texto_doc_com_notas(caminho: Path) -> tuple[str, list]:
    """No Word antigo (antiword) a nota aparece no corpo como linha "[n]. texto"."""
    texto = texto_doc(caminho)
    notas = [(m.start(), m.group(1), " ".join(m.group(2).split()))
             for m in re.finditer(r"^\s*\[(\d+)\]\.?\s+(.+?)(?=^\s*\[\d+\]\.?\s|\n\s*\n|\Z)", texto, re.M | re.S)]
    return texto, notas


def autor_nota(nota: str) -> str | None:
    t = re.sub(r"^[\s.\d\-–]+", "", ov.sem_acento(nota[:200]))
    m = ov.RE_PAIS.search(t)
    return ov.PAISES[m.group(1)] if m and m.start() < 120 else None


def autores_das_notas(notas: list) -> dict[str, str | None]:
    """Autor de cada nota, na ordem do volume; "Ídem" herda da nota anterior e "Véase nota N" da nota N."""
    autores: dict[str, str | None] = {}
    for _, n, texto in sorted(notas, key=lambda x: int(x[1])):
        t = ov.sem_acento(texto).lstrip(" .")
        ref = re.match(r"(?:vease|ver)\s+(?:la\s+)?nota(?:\s+a\s+pie\s+de\s+pagina)?\s*(?:n[o.]\s*)?(\d+)", t)
        if ref:
            autores.setdefault(n, autores.get(ref.group(1)))
        elif re.match(r"idem\b|ibid", t):
            autores.setdefault(n, autores.get(str(int(n) - 1)))
        else:
            autores.setdefault(n, autor_nota(texto))
    return autores


def resolucoes_do_volume(caminho: Path) -> list[dict]:
    """Textos certificados do volume, cada um com suas notas de rodapé (número, texto, autor).

    Quando o leitor não traz as chamadas de nota no corpo (volume de 2010 lido pelo antiword), a nota é
    ligada à resolução que cita no título o mesmo Estado que a nota cita (`vinculo_notas` = por_citacao)."""
    texto, notas = texto_docx_com_notas(caminho) if caminho.suffix.lower() == ".docx" else texto_doc_com_notas(caminho)
    sem_chamadas = bool(notas) and not re.search(r"\[\d+\](?!\.?\s)", re.sub(r"^\s*\[\d+\]\.?\s", "", texto, flags=re.M))
    autores = autores_das_notas(notas)
    saida = []
    for it in dividir(texto):
        titulo = re.sub(r"\s+", " ", re.sub(r"\[\d+\]|/", " ", it["titulo"])).strip()
        suas = []
        if sem_chamadas:
            citados = set(ov.RE_PAIS.findall(ov.sem_acento(titulo)))
            for _, n, t in notas:
                if citados and citados & set(ov.RE_PAIS.findall(ov.sem_acento(t))):
                    suas.append({"numero": n, "texto": t, "autor": autores.get(n)})
        else:
            pos = texto.find(it["corpo"])
            for n in dict.fromkeys(re.findall(r"\[(\d+)\](?!\.)", it["titulo"] + it["corpo"])):
                # a definição da nota é a primeira com esse número depois do início do texto certificado
                defs = [x for x in notas if x[1] == n and x[0] >= pos] or [x for x in notas if x[1] == n]
                if defs:
                    suas.append({"numero": n, "texto": defs[0][2], "autor": autores.get(n)})
        saida.append({**it, "titulo": titulo, "notas": suas, "vinculo_notas": "por_citacao" if sem_chamadas else "chamada"})
    return saida


def chave_votacao(v: dict) -> str:
    return hashlib.sha1(v["ancora_placar"].encode("utf-8")).hexdigest()[:12]


def montar(ids: RegistroIds) -> dict:
    man = list(csv.DictReader(MANIFESTO.open(encoding="utf-8")))
    arquivos = {m["arquivo"].rsplit("/", 1)[1]: m for m in man if (RAIZ / m["arquivo"]).exists()}
    atas = {re.match(r"atas_\d{4}_([IVXLCDM]+-[OE])_", n).group(1): n for n in arquivos if n.startswith("atas_")}
    volumes = {n: m for n, m in arquivos.items() if not n.startswith("atas_")}
    cur = pd.read_csv(CURADORIA_RES, dtype=str, keep_default_na=False)
    incluidas = set(cur.loc[cur["decisao_final"] == "inclui", "simbolo"])
    pendentes = set(cur.loc[cur["decisao_final"] == "", "simbolo"])

    ag = ids.obter("instituicoes", "organismo:OEA_AG")
    inst = [{"id_instituicao": ag, "nome": "Assembleia Geral da Organização dos Estados Americanos", "sigla": "AG/OEA",
             "tipo_instituicao": "organismo_multilateral", "poder": "nao_se_aplica", "esfera": "internacional", "pais_iso3": ""}]
    fontes, oficiais, fonte_de = [], [], {}

    def fonte(nome: str) -> str:
        if nome not in fonte_de:
            reg = arquivos[nome]
            ata = nome.startswith("atas_")
            ano, sessao = re.match(r"(?:atas_)?(\d{4})_([IVXLCDM]+-[OE])_", nome).groups()
            f = ids.obter("fontes", f"raw:{reg['arquivo']}")
            tipo = "Atas textuais das sessões plenárias" if ata else "Actas y Documentos, volume I (declarações e resoluções aprovadas)"
            fontes.append({"id_fonte": f, "tipo_fonte": "oficial", "titulo": f"OEA, Assembleia Geral, sessão {sessao} ({ano}): {tipo}",
                           "data_publicacao": ano, "url": reg["url_base"], "data_acesso": reg["data_acesso"], "sha256": reg["sha256"],
                           "caminho_raw": reg["arquivo"], "licenca": "Documento oficial da OEA; licença não informada no documento",
                           "observacao": "data_publicacao = ano da sessão (o documento não traz data de publicação); índice em https://www.oas.org/es/council/AG/"})
            oficiais.append({"id_fonte": f, "id_orgao": ag, "tipo_documento": tipo, "data_documento": ano, "link": reg["url_base"]})
            fonte_de[nome] = f
        return fonte_de[nome]

    # votações conferidas contra as atas
    votacoes = [v for v in ov.votacoes() if v["decisao"] == "inclui"]
    votada = {v["simbolo"]: v for v in votacoes if v["objeto"] == "resolucao" and v["simbolo"]}

    votos, sem_ata, notas_brasil = [], [], []

    def linhas_votacao(v: dict, resolucao: str, titulo: str, crit: str, data: str, chave: str) -> None:
        if v["modalidade"] != "votacao_registrada":
            return
        paises = v["votos"] if v["confere"] else {p: x for p, x in v["votos"].items() if p == "BRA"}
        for p, x in sorted(paises.items()):
            votos.append({"id_voto": ids.obter("votos_multilaterais", f"oea:{chave}:{p}"), "id_organismo": ag, "resolucao": resolucao, "titulo": titulo,
                          "tema": "", "criterio_inclusao": crit, "data": data, "pais_iso3": p, "voto": x, "link": arquivos[v["ata"]]["url_base"],
                          "modalidade": "votacao_registrada", "trecho": v["trechos"][p], "id_fonte": fonte(v["ata"])})

    resolucoes = {}
    for nome in sorted(volumes):
        for r in resolucoes_do_volume(RAIZ / volumes[nome]["arquivo"]):
            resolucoes.setdefault(r["simbolo"], {**r, "volume": nome})
    for sim in sorted(incluidas):
        r = resolucoes.get(sim)
        if r is None:
            continue
        crit = criterio(r["titulo"], r["corpo"]) or "curadoria"
        autores = {}
        for n in r["notas"]:
            if n["autor"]:
                autores.setdefault(n["autor"], n["texto"])
        if "BRA" in autores:
            notas_brasil.append({"simbolo": sim, "data": r["data"], "titulo": r["titulo"], "nota": autores["BRA"]})
        if sim in votada:
            linhas_votacao(votada[sim], sim, r["titulo"], crit, r["data"], sim)
            continue
        sessao = RE_SESSAO.search(sim).group(1)
        if sessao not in atas:
            sem_ata.append({"simbolo": sim, "data": r["data"], "titulo": r["titulo"], "nota_brasil": autores.get("BRA", "")})
            continue
        for p in sorted({"BRA"} | set(autores)):
            votos.append({"id_voto": ids.obter("votos_multilaterais", f"oea:{sim}:{p}"), "id_organismo": ag, "resolucao": sim, "titulo": r["titulo"],
                          "tema": "", "criterio_inclusao": crit, "data": r["data"], "pais_iso3": p,
                          "voto": "consenso_com_nota" if p in autores else "consenso", "link": arquivos[r["volume"]]["url_base"],
                          "modalidade": "sem_votacao", "trecho": autores.get(p, "")[:600], "id_fonte": fonte(r["volume"])})
        fonte(atas[sessao])  # a ata sustenta a ausência de votação

    for v in votacoes:  # emendas e votações de procedimento
        if v["objeto"] == "resolucao":
            continue
        chave = chave_votacao(v)
        resolucao = f"{v['simbolo']}, emenda" if v["objeto"] == "emenda" else f"Votação de procedimento ({v['data']})"
        linhas_votacao(v, resolucao, v["descricao"], "votacao_registrada_sobre_estado_membro", v["data"], chave)

    return {"instituicoes": inst, "fontes": fontes, "fonte_oficial": oficiais, "votos_multilaterais": votos, "votacoes": votacoes,
            "sem_ata": sem_ata, "notas_brasil": notas_brasil, "pendentes": sorted(pendentes)}


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    for nome in ("fontes", "fonte_oficial"):
        atual = ler(nome, base)
        novas = [l for l in r[nome] if l["id_fonte"] not in set(atual["id_fonte"])]
        gravar(nome, pd.concat([atual, pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    atual = ler("instituicoes", base)
    novas = pd.DataFrame(r["instituicoes"], dtype=str)
    gravar("instituicoes", pd.concat([atual[~atual["id_instituicao"].isin(novas["id_instituicao"])], novas], ignore_index=True), base)
    atual = ler("votos_multilaterais", base)
    org = novas["id_instituicao"].iloc[0]
    gravar("votos_multilaterais", pd.concat([atual[atual["id_organismo"] != org], pd.DataFrame(r["votos_multilaterais"], dtype=str)], ignore_index=True), base)
    ids.salvar()
    SAIDA.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(r["sem_ata"]).to_csv(SAIDA / "resolucoes_sem_ata.csv", index=False, encoding="utf-8")
    pd.DataFrame(r["notas_brasil"]).to_csv(SAIDA / "notas_do_brasil.csv", index=False, encoding="utf-8")


def run() -> None:
    ids = RegistroIds()
    r = montar(ids)
    gravar_resultado(r, ids)
    vm = pd.DataFrame(r["votos_multilaterais"])
    print(f"linhas: {len(vm)}; por modalidade: {vm['modalidade'].value_counts().to_dict()}; resoluções/votações: {vm['resolucao'].nunique()}")
    print("Brasil:")
    print(vm[vm["pais_iso3"] == "BRA"][["data", "resolucao", "voto", "trecho"]].to_string(max_colwidth=70))
    print(f"sem ata: {[x['simbolo'] for x in r['sem_ata']]}; notas do Brasil: {len(r['notas_brasil'])}; pendentes de decisão: {len(r['pendentes'])}")


if __name__ == "__main__":
    run()
