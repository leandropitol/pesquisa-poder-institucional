"""Composição do STF (D-058): ministros em exercício de 2003 em diante, quem os indicou e quando.

Entradas:
- bruto data/raw/stf_ministros/<data>/ (src.coleta.stf_ministros): detalhamento JSON das indicações por
  presidente (quem indicou quem, segundo o STF) e as páginas "Dados e Datas" da Biblioteca do STF, de onde saem a
  mensagem de indicação, o decreto de nomeação, a vaga, o termo de posse e o decreto de aposentadoria;
  a biografia do portal completa o que a página "Dados e Datas" não traz (falecimento);
- data/curadoria/stf_ministros_atores.csv: ligação a atores já na base (ministros que foram parlamentares e
  presidentes da República);
- data/curadoria/stf_ministros_correcoes.csv: erros e lacunas das páginas do STF corrigidos com outra página oficial
  do bruto; o trecho citado tem de estar no arquivo, e a tabela de correções sai em relatorios/tabelas;
- matéria do Senado (MSF 7/2026): indicação rejeitada, registrada como relação `indicou` com observação e como
  evento `votacao_nominal`.

Saídas: atores, cargos (Ministro do STF, forma_acesso indicado_aprovado, início na posse, fim na aposentadoria
ou falecimento), relacoes (presidente `indicou` ministro, na data da mensagem de indicação), fontes e fonte_oficial.
O partido do presidente não é atributo do ministro e não entra aqui.

Uso:
    python -m src.normalizacao.stf_ministros --data AAAA-MM-DD
"""

import argparse
import csv
import json
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, acrescentar, gravar, ler

RAW = RAIZ / "data" / "raw" / "stf_ministros"
CUR = RAIZ / "data" / "curadoria"
URL_DD = "https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina={}DadosDatas"
URL_IND = "https://portal.stf.jus.br/ostf/ministros/detalhamentos.asp?detalhamento=INDICACOES&entidade={}"
URL_BIO = "https://portal.stf.jus.br/ostf/ministros/verMinistro.asp?periodo=STF&id={}"
MESES = {m: i for i, m in enumerate(["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro",
                                     "outubro", "novembro", "dezembro"], 1)}
DATA = r"(\d{1,2})º?\s+de\s+(" + "|".join(MESES) + r")\s+de\s+(\d{4})"
INICIO_ESTUDO = "2003-01-01"


def norm(s: str) -> str:
    return " ".join(unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii").lower().split())


def slug(nome_guerra: str) -> str:
    """Nome da pasta na Biblioteca do STF: palavras sem acento e sem preposições, com inicial maiúscula."""
    return "".join(p[0].upper() + p[1:] for p in norm(nome_guerra).split() if p not in {"de", "da", "do", "dos", "das"})


def iso(texto: str) -> str:
    m = re.search(DATA, texto, re.I)
    return f"{m.group(3)}-{MESES[m.group(2).lower()]:02d}-{int(m.group(1)):02d}" if m else ""


class _Texto(HTMLParser):
    BLOCOS = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "td", "section", "article"}

    def __init__(self):
        super().__init__()
        self.partes, self._pular = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._pular += 1
        elif tag in self.BLOCOS:
            self.partes.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._pular -= 1
        elif tag in self.BLOCOS:
            self.partes.append("\n")

    def handle_data(self, data):
        if not self._pular:
            self.partes.append(data)


def texto_html(corpo: bytes) -> str:
    try:
        h = corpo.decode("utf-8")
    except UnicodeDecodeError:
        h = corpo.decode("latin-1")
    p = _Texto()
    p.feed(h)
    linhas = [re.sub(r"\s+", " ", l).strip() for l in "".join(p.partes).split("\n")]
    return "\n".join(l for l in linhas if l)


def secoes(texto: str) -> dict[str, str]:
    """Seções da página "Dados e Datas": cada título em maiúsculas seguido de itens numerados."""
    corpo = texto[texto.find("Dados e Datas"):]
    partes = re.split(r"\n([A-ZÁÉÍÓÚÂÊÔÃÕÇ/_ ]{12,})\n(?=\d+\.)", "\n" + corpo)
    return {re.sub(r"[_ ]+", " ", partes[i]).strip(): partes[i + 1] for i in range(1, len(partes) - 1, 2)}


def vaga(texto: str) -> tuple[str, str]:
    m = re.search(r"vaga decorrente d[aáo]s?\s+(aposentadoria|falecimento|exoneração)(?:\s+voluntária)?(?:,\s*a pedido,)?\s+d[aoe]s?\s+(?:Ministr[oa]\s+)?([^.,;]+)",
                  texto, re.I)
    return (m.group(1).lower(), m.group(2).strip(" []")) if m else ("", "")


def ler_dados_datas(texto: str) -> dict:
    s = secoes(texto)

    def sec(chave: str) -> str:
        return next((v for k, v in s.items() if k.startswith(chave)), "")

    ind, apr, nom, posse, apos = sec("INDICAÇÃO"), sec("APRECIAÇÃO"), sec("NOMEAÇÃO"), sec("POSSE NO SUPREMO"), sec("APOSENTA")
    m_ind = re.search(r"Mensagem nº\s*([\d.]+),?\s+de\s+" + DATA, ind, re.I)
    m_dec = re.search(r"Decreto de\s+" + DATA, nom, re.I)
    vagas = [vaga(t) for t in (ind, apr, nom)]
    v = next((x for x in vagas if x[1]), ("", ""))
    m_posse = re.search(r"em\s+" + DATA, posse, re.I)
    m_ap = re.search(r"a partir d[eo]\s+(?:dia\s+)?" + DATA, apos, re.I) or re.search(r"Decreto de\s+" + DATA, apos, re.I)
    return {"mensagem_numero": m_ind.group(1) if m_ind else "", "data_mensagem": iso(m_ind.group(0)) if m_ind else "",
            "data_decreto_nomeacao": iso(m_dec.group(0)) if m_dec else "",
            "vaga_motivo": v[0], "vaga_de": v[1], "vaga_no_decreto": vagas[2][1],
            "data_posse": iso(m_posse.group(0)) if m_posse else "",
            "data_aposentadoria": iso(m_ap.group(0)) if m_ap else "", "tem_secao_aposentadoria": bool(apos),
            "secoes": list(s)}


def ler_bruto(data: str) -> dict:
    pasta = RAW / data
    indicacoes = []
    for arq in sorted(pasta.glob("indicacoes_presidente_*.json")):
        id_pres = arq.stem.rsplit("_", 1)[1]
        for m in json.loads(arq.read_text(encoding="utf-8"))["ministros"]:
            indicacoes.append({"id_presidente_stf": id_pres, "id_stf": str(m["id"]), "nome_guerra": m["nomeDeGuerra"], "nome_completo": m["nomeCompleto"]})
    lista = texto_html((pasta / "lista_quadro_indicacoes.html").read_bytes())
    presidentes = dict(re.findall(r'data-id-entidade="(\d+)" data-nome-entidade="([^"]+)"', (pasta / "lista_quadro_indicacoes.html").read_bytes().decode("utf-8", "replace")))
    ministros = []
    for i in indicacoes:
        arq = pasta / f"dados_datas_{slug(i['nome_guerra'])}.html"
        if not arq.exists():
            continue  # fora do período: sem página coletada
        d = ler_dados_datas(texto_html(arq.read_bytes()))
        bio = pasta / f"biografia_{i['id_stf']}.html"
        tb = texto_html(bio.read_bytes()) if bio.exists() else ""
        falec = re.search(r"Faleceu\s+(?:dia|em)\s+" + DATA, tb, re.I)
        ministros.append({**i, "presidente": presidentes.get(i["id_presidente_stf"], ""), **d, "arquivo_dados_datas": arq.name,
                          "data_falecimento_bio": iso(falec.group(0)) if falec else ""})
    return {"ministros": ministros, "texto_lista": lista}


def data_pagina(corpo: bytes, data_acesso: str) -> tuple[str, str]:
    """Data do documento: "Última atualização" (Biblioteca do STF) ou a data da notícia; sem data, a de acesso, com aviso."""
    t = texto_html(corpo)
    m = re.search(r"Última atualização:\s*(\d{4}-\d{2}-\d{2})", t)
    if m:
        return m.group(1), "data = última atualização da página"
    m = re.search(r"\b(\d{2})/(\d{2})/(\d{4})\s+\d{2}h\d{2}", t)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}", "data = publicação da notícia"
    return data_acesso, "página sem data de publicação; registrada a data de acesso"


def ler_csv(nome: str) -> list[dict]:
    return list(csv.DictReader((CUR / nome).open(encoding="utf-8")))


def aplicar_correcoes(ministros: list[dict], data: str) -> list[dict]:
    """Correções com fonte: o trecho citado tem de estar no arquivo do bruto; o valor substitui o lido na página."""
    aplicadas = []
    for c in ler_csv("stf_ministros_correcoes.csv"):
        texto = texto_html((RAW / data / c["arquivo"]).read_bytes())
        if " ".join(c["trecho"].split()) not in " ".join(texto.split()):
            raise ValueError(f"trecho da correção não está em {c['arquivo']}: {c['trecho'][:60]}")
        m = next(x for x in ministros if x["id_stf"] == c["id_stf"])
        aplicadas.append({"id_stf": c["id_stf"], "nome_guerra": m["nome_guerra"], "campo": c["campo"], "lido": m.get(c["campo"], ""),
                          "valor": c["valor"], "arquivo": c["arquivo"], "motivo": c["motivo"]})
        m[c["campo"]] = c["valor"]
        m.setdefault("fontes_corrigidas", {})[c["campo"]] = c["arquivo"]
    return aplicadas


def montar(data: str, ids: RegistroIds, base: Path = BASE) -> dict:
    bruto = ler_bruto(data)
    correcoes = aplicar_correcoes(bruto["ministros"], data)
    lig = {(l["tipo"], l["chave"]): l for l in ler_csv("stf_ministros_atores.csv")}
    stf = ler("instituicoes", base)
    id_stf = stf.loc[stf["sigla"] == "STF", "id_instituicao"].iloc[0]
    manifesto = pd.read_csv(RAIZ / "data" / "manifestos" / "stf_ministros.csv", dtype=str)
    sha = dict(zip(manifesto["arquivo"].str.rsplit("/", n=1).str[1], manifesto["sha256"]))
    atores, cargos, relacoes, rel_fontes, fontes, oficiais, legislativas, fonte_de = [], [], [], [], [], [], [], {}
    titulos = {"dados_datas": "STF, Biblioteca: {} - Dados e Datas", "biografia": "STF: biografia de {}", "noticia_stf": "STF: notícia oficial sobre {}"}
    urls = {"biografia": URL_BIO, "noticia_stf": "https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo={}&ori=1"}
    documentos = {"noticia_stf": "Notícia oficial (portal do STF)", "biografia": "Biografia (portal do STF)", "dados_datas": "Página Dados e Datas (Biblioteca do STF)"}

    def fonte(arquivo: str, titulo: str, url: str, tipo_doc: str) -> str:
        if arquivo in fonte_de:
            return fonte_de[arquivo]
        i = ids.obter("fontes", f"stf_ministros:{arquivo}")
        fonte_de[arquivo] = i
        d_doc, nota = data_pagina((RAW / data / arquivo).read_bytes(), data)
        fontes.append({"id_fonte": i, "tipo_fonte": "oficial", "titulo": titulo, "data_publicacao": d_doc, "url": url, "data_acesso": data,
                       "sha256": sha.get(arquivo, ""), "caminho_raw": f"data/raw/stf_ministros/{data}/{arquivo}", "licenca": "Página pública do STF",
                       "observacao": f"Lida no navegador embutido (mesma origem); bytes conferidos pelo sha256; {nota}"})
        oficiais.append({"id_fonte": i, "id_orgao": id_stf, "tipo_documento": tipo_doc, "data_documento": d_doc, "link": url})
        return i

    def fonte_arquivo(arquivo: str, nome: str) -> str:
        tipo = "noticia_stf" if arquivo.startswith("noticia_stf") else "biografia" if arquivo.startswith("biografia") else "dados_datas"
        num = re.search(r"_(\d+)\.html$", arquivo)
        url = urls[tipo].format(num.group(1)) if tipo in urls else URL_DD.format(arquivo[len("dados_datas_"):-len(".html")])
        return fonte(arquivo, titulos[tipo].format(nome), url, documentos[tipo])

    def ator(tipo: str, chave: str, nome: str) -> str:
        l = lig.get((tipo, chave))
        if l and l["id_ator"]:
            return l["id_ator"]
        a = ids.obter("atores", f"{tipo}:{chave}")
        if a not in {x["id_ator"] for x in atores}:
            atores.append({"id_ator": a, "nome": nome, "nome_normalizado": norm(nome), "tipo_ator": "agente_publico",
                           "observacao": {"stf_ministro": "Ministro do STF (D-058)", "presidente": "Presidente da República que indicou ministro do STF (D-058)",
                                          "indicado": "Indicado ao STF; indicação rejeitada pelo Senado (D-058)"}[tipo]})
        return a

    fora, tabela = [], []
    for m in bruto["ministros"]:
        fc = m.get("fontes_corrigidas", {})
        if m["data_aposentadoria"]:
            fim, motivo, arq_fim = m["data_aposentadoria"], "aposentadoria", fc.get("data_aposentadoria", m["arquivo_dados_datas"])
        elif m.get("data_fim"):
            fim, motivo, arq_fim = m["data_fim"], m.get("motivo_fim", ""), fc["data_fim"]
        elif m["data_falecimento_bio"]:
            fim, motivo, arq_fim = m["data_falecimento_bio"], "falecimento", f"biografia_{m['id_stf']}.html"
        else:
            fim, motivo, arq_fim = "", "", ""
        if fim and fim < INICIO_ESTUDO:
            fora.append(m["nome_guerra"])
            continue
        a = ator("stf_ministro", m["id_stf"], m["nome_completo"])
        p = ator("presidente", m["id_presidente_stf"], m["presidente"])
        f_dd = fonte_arquivo(m["arquivo_dados_datas"], m["nome_guerra"])
        f_ind = fonte(f"indicacoes_presidente_{m['id_presidente_stf']}.json", f"STF: ministros nomeados por {m['presidente']}",
                      URL_IND.format(m["id_presidente_stf"]), "Detalhamento de indicações presidenciais (portal do STF)")
        f_posse = fonte_arquivo(fc["data_posse"], m["nome_guerra"]) if "data_posse" in fc else f_dd
        f_fim = fonte_arquivo(arq_fim, m["nome_guerra"]) if arq_fim else ""
        cargos.append({"id_cargo": ids.obter("cargos", f"stf_ministro:{m['id_stf']}"), "id_ator": a, "id_instituicao": id_stf,
                       "cargo": "Ministro do Supremo Tribunal Federal", "forma_acesso": "indicado_aprovado", "data_inicio": m["data_posse"],
                       "data_fim": fim, "id_fonte": f_posse})
        r = ids.obter("relacoes", f"stf_indicou:{m['id_stf']}")
        relacoes.append({"id_relacao": r, "origem_tipo": "ator", "origem_id": p, "tipo_relacao": "indicou", "destino_tipo": "ator", "destino_id": a,
                         "data_inicio": m["data_mensagem"], "data_fim": "", "eixo": "poder_institucional", "nivel_confianca": "documentado"})
        rel_fontes += [{"id_relacao": r, "id_fonte": f_ind, "localizador": f"ministro id {m['id_stf']}"},
                       {"id_relacao": r, "id_fonte": f_dd,
                        "localizador": f"Indicação: Mensagem nº {m['mensagem_numero']}; Nomeação: decreto de {m['data_decreto_nomeacao']}"}]
        if "data_decreto_nomeacao" in fc:
            rel_fontes.append({"id_relacao": r, "id_fonte": fonte_arquivo(fc["data_decreto_nomeacao"], m["nome_guerra"]), "localizador": "data do decreto de nomeação"})
        tabela.append({**{k: v for k, v in m.items() if k not in ("secoes", "fontes_corrigidas", "motivo_fim")}, "id_ator": a, "id_ator_presidente": p,
                       "data_fim": fim, "motivo_fim": motivo, "id_fonte_posse": f_posse, "id_fonte_fim": f_fim,
                       "vaga_divergente": bool(m["vaga_no_decreto"]) and norm(m["vaga_no_decreto"]) != norm(m["vaga_de"])})

    # indicações rejeitadas pelo Senado (matérias coletadas pela API de dados abertos)
    eventos, ev_fontes = [], []
    for arq in sorted((RAW / data).glob("senado_votacao_*.jsonl")):
        cod = arq.stem.rsplit("_", 1)[1]
        v = json.loads(arq.open(encoding="utf-8").readline())["corpo"][0]
        if v["resultadoVotacao"] != "R":
            continue
        bruto_nome = re.search(r"Senhor\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ ]+?),", v["ementa"]).group(1)
        nome = " ".join(w.lower() if w.lower() in {"de", "da", "do", "dos", "das"} else w.capitalize() for w in bruto_nome.split())
        i = ids.obter("fontes", f"stf_ministros:senado:{cod}")
        link = f"https://www25.senado.leg.br/web/atividade/materias/-/materia/{cod}"
        fontes.append({"id_fonte": i, "tipo_fonte": "legislativa", "titulo": f"Senado: {v['identificacao']} e votação nominal de {v['dataSessao']}",
                       "data_publicacao": v["dataSessao"], "url": link, "data_acesso": data, "sha256": sha.get(arq.name, ""), "caminho_raw": f"data/raw/stf_ministros/{data}/{arq.name}",
                       "licenca": "Dados abertos do Senado Federal", "observacao": "API de dados abertos (matéria, movimentações e votação)"})
        legislativas.append({"id_fonte": i, "casa": "senado_federal", "proposicao": v["identificacao"], "id_votacao": str(v["codigoSessaoVotacao"]),
                             "data": v["dataSessao"], "link_portal": link})
        a = ator("indicado", cod, nome)
        r = ids.obter("relacoes", f"stf_indicou:senado:{cod}")
        relacoes.append({"id_relacao": r, "origem_tipo": "ator", "origem_id": lig[("presidente", "1")]["id_ator"], "tipo_relacao": "indicou",
                         "destino_tipo": "ator", "destino_id": a, "data_inicio": v["dataApresentacao"], "data_fim": v["dataSessao"],
                         "eixo": "poder_institucional", "nivel_confianca": "documentado"})
        rel_fontes.append({"id_relacao": r, "id_fonte": i, "localizador": "ementa (autor: Presidência da República); início = apresentação no Senado "
                           "(a mensagem presidencial nº 1.714/2025 não traz o dia nas fontes coletadas); fim = rejeição em plenário"})
        e = ids.obter("eventos", f"stf_ministros:senado:{cod}")
        eventos.append({"id_evento": e, "data": v["dataSessao"], "precisao_data": "dia", "tipo_evento": "votacao_nominal", "eixo": "poder_institucional",
                        "descricao": f"Senado rejeita a indicação de {nome} ao STF ({v['identificacao']}, vaga de Luís Roberto Barroso): "
                                     f"Sim {v['totalVotosSim']}, Não {v['totalVotosNao']}, abstenção {v['totalVotosAbstencao']}; votação secreta",
                        "pais_iso3": "BRA", "nivel_confianca": "documentado"})
        ev_fontes.append({"id_evento": e, "id_fonte": i, "localizador": f"votação {v['codigoSessaoVotacao']}, informe legislativo de {v['dataSessao']}"})
    return {"atores": atores, "cargos": cargos, "relacoes": relacoes, "relacao_fonte": rel_fontes, "fontes": fontes, "fonte_oficial": oficiais,
            "fonte_legislativa": legislativas, "eventos": eventos, "evento_fonte": ev_fontes, "tabela": pd.DataFrame(tabela),
            "correcoes": pd.DataFrame(correcoes), "fora_do_periodo": fora, "data": data}


PADRAO_SIMETRIA = ("Relação 'indicou' entre Presidente da República e indicado ao STF (D-058). Indicações anteriores a 2003 comparadas "
                   "com o universo de partidos de 2003, primeiro ano do estudo")
JUSTIFICATIVA = ("Indicação ao STF é ato constitucional de todo presidente, e a coleta cobre todas as indicações dos presidentes que nomearam "
                 "ministros em exercício de 2003 em diante, mais a indicação rejeitada de 2026, sem seleção por partido (D-058). A comparação "
                 "por partido do presidente não foi feita: a base não tem a filiação dos presidentes nas datas das indicações")


def verificar_simetria(relacoes: list[dict], ids: RegistroIds, data: str, base: Path = BASE) -> tuple[list[dict], list[dict]]:
    filiados = set(ler("filiacoes", base)["id_ator"])
    universo = ler("universo_partidos", base)
    existentes = set(ler("verificacoes_simetria", base)["id_verificacao"])
    vs, vr = [], []
    for r in relacoes:
        if r["origem_id"] not in filiados and r["destino_id"] not in filiados:
            continue
        v = ids.obter("verificacoes_simetria", f"stf_ministros|relacoes|{r['id_relacao']}")
        if v in existentes:
            continue
        ano = max(r["data_inicio"][:4], "2003")
        vs.append({"id_verificacao": v, "achado_tabela": "relacoes", "achado_id": r["id_relacao"], "padrao_buscado": PADRAO_SIMETRIA,
                   "ano_referencia": ano, "data": data, "script": "src.normalizacao.stf_ministros"})
        for g in sorted(universo.loc[universo["ano"] == ano, "id_partido"]):
            vr.append({"id_resultado": ids.obter("verificacao_resultado", f"{v}|{g}"), "id_verificacao": v, "grupo_tipo": "partido", "grupo_id": g,
                       "resultado": "nao_verificado", "justificativa": JUSTIFICATIVA})
    return vs, vr


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    for nome, chave in (("fontes", "id_fonte"), ("fonte_oficial", "id_fonte"), ("fonte_legislativa", "id_fonte"), ("atores", "id_ator"),
                        ("cargos", "id_cargo"), ("relacoes", "id_relacao"), ("eventos", "id_evento")):
        atual = ler(nome, base)
        novos = pd.DataFrame(r[nome], dtype=str)
        if len(novos):
            gravar(nome, pd.concat([atual[~atual[chave].isin(novos[chave])], novos], ignore_index=True), base)
    for nome, col in (("relacao_fonte", "id_relacao"), ("evento_fonte", "id_evento")):
        atual = ler(nome, base)
        feitas = set(atual[col] + "|" + atual["id_fonte"])
        acrescentar(nome, [x for x in r[nome] if f"{x[col]}|{x['id_fonte']}" not in feitas], base)
    vs, vr = verificar_simetria(r["relacoes"], ids, r["data"], base)
    acrescentar("verificacoes_simetria", vs, base)
    acrescentar("verificacao_resultado", vr, base)
    ids.salvar()


def run(data: str) -> None:
    ids = RegistroIds()
    r = montar(data, ids)
    gravar_resultado(r, ids)
    r["tabela"].to_csv(RAIZ / "relatorios" / "tabelas" / "stf_composicao.csv", index=False, encoding="utf-8")
    r["correcoes"].to_csv(RAIZ / "relatorios" / "tabelas" / "stf_composicao_correcoes.csv", index=False, encoding="utf-8")
    print(f"ministros: {len(r['cargos'])}; atores novos: {len(r['atores'])}; eventos: {len(r['eventos'])}; fora do período: {r['fora_do_periodo']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    run(ap.parse_args().data)
