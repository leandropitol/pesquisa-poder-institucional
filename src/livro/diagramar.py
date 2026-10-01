"""Diagrama o livro: gera o .docx, ativa margens espelhadas, converte para PDF e preenche o sumário com as páginas.

Uso, na raiz do repositório, depois de `python -m src.livro`:
    python -m src.livro.diagramar

Passos: (1) `node src/livro/docx/montar_docx.js` lê livro.json e paginas.json; (2) acrescenta <w:mirrorMargins/> ao
settings.xml do .docx (a biblioteca docx não expõe essa opção); (3) converte com o LibreOffice; (4) localiza no PDF a
página de cada título do sumário e grava paginas.json; repete até as páginas pararem de mudar (no máximo 4 vezes).
Precisa de Node com o pacote docx, LibreOffice (soffice) e pdftotext (poppler).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "relatorios" / "livro"
DOCX, PDF, PAG = SAIDA / "livro.docx", SAIDA / "livro.pdf", SAIDA / "paginas.json"


def espelhar(docx: Path) -> None:
    tmp = docx.with_suffix(".tmp.docx")
    with zipfile.ZipFile(docx) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            data = zi.read(it.filename)
            if it.filename == "word/settings.xml" and b"mirrorMargins" not in data:
                s = data.decode("utf-8")
                m = re.search(r"<w:zoom[^>]*/>", s) or re.search(r"<w:settings[^>]*>", s)
                s = s[:m.end()] + "<w:mirrorMargins/>" + s[m.end():]
                data = s.encode("utf-8")
            zo.writestr(it, data)
    tmp.replace(docx)


def pdf(docx: Path) -> None:
    soffice = os.environ.get("SOFFICE") or shutil.which("soffice") or shutil.which("libreoffice")
    with tempfile.TemporaryDirectory() as perfil:
        subprocess.run([soffice, f"-env:UserInstallation=file://{perfil}", "--headless", "--convert-to", 'pdf:writer_pdf_Export:{"IsSkipEmptyPages":{"type":"boolean","value":"false"}}', "--outdir", str(SAIDA), str(docx)],
                       check=True, capture_output=True, timeout=900)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\s+", " ", s).strip()


def paginas() -> dict:
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout).group(1))
    txt = subprocess.run(["pdftotext", "-layout", str(PDF), "-"], capture_output=True, text=True).stdout.split("\f")
    linhas = [[norm(l) for l in p.splitlines() if l.strip()] for p in txt[:n]]
    blocos = json.loads((SAIDA / "livro.json").read_text(encoding="utf-8"))["blocos"]
    titulos = [b["x"] for b in blocos if b["t"] == "part" or (b["t"] == "h1" and re.match(r"^(\d+\.|[A-H]\. )", b["x"]))]
    # o corpo começa na página em que "Apresentação" aparece sozinha como título, depois do sumário
    ini_sum = next(i for i, p in enumerate(linhas) if p and p[0] == "Sumário")
    pos, achado = ini_sum + 1, {}
    while pos < n and not (linhas[pos] and linhas[pos][0] == norm(titulos[0])):
        pos += 1
    corpo = pos
    for t in titulos:
        alvo = norm(t)[:38]
        for i in range(pos, n):
            pagina = " ".join(linhas[i])
            if any(l.startswith(alvo[:25]) for l in linhas[i]) and alvo in pagina:
                achado[t] = i - corpo + 1; pos = i; break
    falta = [t for t in titulos if t not in achado]
    if falta:
        print("títulos não localizados:", falta)
    return achado


def main() -> None:
    anterior = None
    for volta in range(4):
        subprocess.run(["node", str(RAIZ / "src/livro/docx/montar_docx.js")], check=True, cwd=RAIZ,
                       env={**os.environ, "NODE_PATH": os.environ.get("NODE_PATH") or subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()})
        espelhar(DOCX)
        pdf(DOCX)
        pg = paginas()
        print(f"volta {volta + 1}: {len(pg)} títulos paginados")
        if pg == anterior:
            break
        PAG.write_text(json.dumps(pg, ensure_ascii=False, indent=1), encoding="utf-8")
        anterior = pg


if __name__ == "__main__":
    main()
