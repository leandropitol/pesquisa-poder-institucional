"""Gera todo o material do livro: python -m src.livro (depois: node src/livro/docx/montar_docx.js)."""
from . import atlas, externos, montar, parte1, parte2, parte3, parte4, parte5, parte6, parte7

if __name__ == "__main__":
    externos.main()
    # a ordem importa: as partes 1 e 7 leem resultados das demais
    for m in (parte2, parte3, parte4, parte5, parte6, parte7, parte1, atlas):
        m.main()
    montar.main()
