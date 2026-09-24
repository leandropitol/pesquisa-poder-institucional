"""Extração das resoluções e declarações dos volumes da Assembleia Geral da OEA (etapa E8, bloco A3).

Lê os volumes baixados (Word antigo por `antiword`, Word novo por python-docx, notas de rodapé do
arquivo `word/footnotes.xml`), separa cada texto certificado (AG/RES. ou AG/DEC.), com título, data de
aprovação e notas, e aplica o critério aprovado (docs/lista_e8_para_revisao.md, bloco A3):

- `cita_estado_membro`: o título cita nominalmente um Estado membro (ou a questão das Malvinas). Votos
  de agradecimento ao país anfitrião ficam de fora, por não tratarem de situação política, eleitoral
  ou de direitos humanos;
- `carta_democratica_mecanismo`: o texto cita a Carta Democrática Interamericana junto com um dos
  artigos dos mecanismos de ação coletiva (17 a 21).

A saída vai para data/staging/oea/ para revisão; nada entra na base nesta etapa.

Uso:
    python -m src.normalizacao.oea
"""

import csv
import re
import subprocess
import unicodedata
import zipfile
from pathlib import Path

import docx
import pandas as pd

from src.base import RAIZ

MANIFESTO = RAIZ / "data" / "manifestos" / "oea.csv"
SAIDA = RAIZ / "data" / "staging" / "oea"
ANTIWORD = "antiword"

ESTADOS = [
    "Antigua y Barbuda", "Argentina", "Bahamas", "Barbados", "Belice", "Bolivia", "Brasil", "Canadá", "Chile", "Colombia",
    "Costa Rica", "Cuba", "Dominica", "Ecuador", "El Salvador", "Estados Unidos", "Grenada", "Granada", "Guatemala", "Guyana",
    "Haití", "Honduras", "Jamaica", "México", "Nicaragua", "Panamá", "Paraguay", "Perú", "República Dominicana",
    "Saint Kitts y Nevis", "Santa Lucía", "San Vicente y las Granadinas", "Suriname", "Trinidad y Tobago", "Uruguay",
    "Venezuela", "Malvinas",
    # inglês (volume de 2013)
    "Antigua and Barbuda", "Belize", "Brazil", "Canada", "Dominican Republic", "Haiti", "Mexico", "Panama", "Peru",
    "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Trinidad and Tobago", "United States", "Falkland",
]
# Tema de situação política, eleitoral ou de direitos humanos (triagem; decisão final na curadoria)
RE_TEMA = re.compile(r"situaci[oó]n|crisis|democr|elecci|electoral|derechos humanos|paz|golpe|instituciones|magnicidio|solidaridad|"
                     r"apoyo al pueblo|seguridad en hait|situation|democra|election|human rights|peace", re.I)
RE_ESTADO = re.compile(r"\b(" + "|".join(re.escape(e) for e in ESTADOS) + r")\b", re.I)
RE_CABECALHO = re.compile(r"^\s*(AG/(?:RES|DEC)\.\s*\d+\s*\([IVXLCDM]+-[OE]/\d{2}\)(?:\s*rev\.\s*\d)?)\s*$", re.M)
RE_APROVADA = re.compile(r"\((?:Aprobad[ao][^)]*?(\d{1,2}) de (\w+) de (\d{4})|Adopted[^)]*?on (\w+) (\d{1,2}), (\d{4}))\)", re.I)
RE_CARTA_ART = re.compile(r"Carta Democrática Interamericana[^.]{0,300}?art[íi]culos?\s*(1[7-9]|2[01])|art[íi]culos?\s*(1[7-9]|2[01])[^.]{0,120}Carta Democrática", re.I | re.S)
MESES_EN = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"], 1)}
MESES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"], 1)}


def texto_doc(caminho: Path) -> str:
    return subprocess.run([ANTIWORD, "-m", "UTF-8.txt", str(caminho)], capture_output=True).stdout.decode("utf-8", errors="replace")


def texto_docx(caminho: Path) -> str:
    d = docx.Document(str(caminho))
    corpo = "\n".join(p.text for p in d.paragraphs)
    notas = ""
    with zipfile.ZipFile(caminho) as z:
        if "word/footnotes.xml" in z.namelist():
            xml = z.read("word/footnotes.xml").decode("utf-8")
            notas = "\n".join(re.sub(r"<[^>]+>", "", n) for n in re.findall(r"<w:footnote [^>]*>(.*?)</w:footnote>", xml, re.S))
    return corpo + "\n\n[NOTAS]\n" + notas


def sem_acento(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def dividir(texto: str) -> list[dict]:
    """Textos certificados: cada cabeçalho sozinho na linha seguido de título e '(Aprobada ...)'."""
    marcas = list(RE_CABECALHO.finditer(texto))
    itens = []
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        corpo = texto[m.end():fim]
        ap = RE_APROVADA.search(corpo[:1500])
        if not ap:
            continue  # sumário ou citação, não o texto certificado
        titulo = " ".join(corpo[:ap.start()].split())
        if ap.group(1):
            dia, mes, ano = ap.group(1), MESES.get(sem_acento(ap.group(2).lower()), 0), ap.group(3)
        else:
            dia, mes, ano = ap.group(5), MESES_EN.get(ap.group(4).lower(), 0), ap.group(6)
        data = f"{ano}-{mes:02d}-{int(dia):02d}" if mes else ano
        itens.append({"simbolo": " ".join(m.group(1).split()), "titulo": titulo, "data": data, "corpo": corpo})
    vistos, unicos = set(), []
    for it in itens:
        if it["simbolo"] not in vistos:
            vistos.add(it["simbolo"])
            unicos.append(it)
    return unicos


def criterio(titulo: str, corpo: str) -> str:
    if RE_ESTADO.search(titulo) and not re.match(r"\s*(voto de agradecimiento|vote of thanks|vote of appreciation)", titulo, re.I):
        return "cita_estado_membro"
    if RE_CARTA_ART.search(corpo):
        return "carta_democratica_mecanismo"
    return ""


def notas_do_brasil(texto_completo: str, simbolo: str) -> str:
    """Trechos de notas de rodapé em que o Brasil aparece (reserva, declaração de voto)."""
    trechos = [t.strip() for t in re.split(r"\n\s*\n", texto_completo) if re.search(r"\bBrasil\b", t) and len(t) < 3000]
    return " | ".join(trechos)[:2000]


def run() -> None:
    man = list(csv.DictReader(MANIFESTO.open(encoding="utf-8")))
    SAIDA.mkdir(parents=True, exist_ok=True)
    linhas = []
    for reg in man:
        caminho = RAIZ / reg["arquivo"]
        if not caminho.exists():
            continue
        texto = texto_docx(caminho) if caminho.suffix.lower() == ".docx" else texto_doc(caminho)
        for it in dividir(texto):
            c = criterio(it["titulo"], it["corpo"])
            linhas.append({"volume": caminho.name, "simbolo": it["simbolo"], "data": it["data"], "titulo": it["titulo"][:300], "criterio": c,
                           "cita_brasil_no_texto": "sim" if re.search(r"\bBrasil\b", it["corpo"]) else "",
                           "trechos_brasil": notas_do_brasil(it["corpo"], it["simbolo"]) if c else ""})
    df = pd.DataFrame(linhas)
    df.to_csv(SAIDA / "resolucoes_ag_oea.csv", index=False, encoding="utf-8")
    sel = df[df["criterio"] != ""].copy()
    sel["triagem_tema"] = ["sim" if RE_TEMA.search(t) else "nao" for t in sel["titulo"]]
    sel.to_csv(SAIDA / "resolucoes_ag_oea_selecionadas.csv", index=False, encoding="utf-8")
    print(f"textos certificados: {len(df)} em {df['volume'].nunique()} volumes; selecionados: {sel['criterio'].value_counts().to_dict()}")


if __name__ == "__main__":
    run()
