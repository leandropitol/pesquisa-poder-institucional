# Livro "Dinheiro, Justiça e Poder"

Scripts que geram, a partir de `data/base/`, `relatorios/tabelas/` e `data/curadoria/`, todo o material do livro:
números do texto (`relatorios/livro/resultados.json`), figuras (`relatorios/livro/figuras/`), tabelas
(`relatorios/livro/tabelas/`), fichas de cada gráfico e tabela (`relatorios/livro/fichas.json`) e o arquivo final
(`relatorios/livro/livro.docx`). Nenhum número do texto é digitado à mão: os textos em `textos/` usam marcadores
`{{chave:dN}}` preenchidos com os resultados.

```bash
pip install -r requirements.txt          # inclui matplotlib, openpyxl, pillow, scipy e statsmodels
python -m src.livro                      # cálculos, figuras, tabelas, fichas e livro.json
cd src/livro/docx && npm install && node montar_docx.js   # livro.docx
```

Dependências de dados fora do Git: `data/raw/tesouro/2026-09-30/serie_historica_dez25.xlsx` (sha256 em
`data/manifestos/tesouro.csv`) e os arquivos `consulta_cand_*.zip` do TSE (sha256 em `data/manifestos/tse.csv`).
Decisões que fixam as regras do livro: D-069 a D-079 em `docs/decisoes_metodologicas.md` (D-074 a D-079 para o núcleo analítico da Parte VII).

| Módulo | Conteúdo |
|---|---|
| `externos.py` | extrai do RTN do Tesouro a despesa total, as discricionárias e o FEFC |
| `parte1.py` | cobertura das bases, cadeia de custódia, graus de afirmação, esquemas, universos e testes |
| `parte2.py` | receitas de campanha (D1–D5, D8–D10) |
| `parte3.py` | emendas parlamentares (M1–M8) |
| `parte4.py` | STF, TCU, TSE e CGU (J1–J10) |
| `parte5.py` | partidos, alinhamento, Conselhos de Ética, redes (P1–P7) |
| `parte6.py` | réguas de democracia, votos, BNDES, comércio, acordos (X1–X7) |
| `parte7.py` | número efetivo de partidos por ano e marcos normativos |
| `nucleo_series.py` | séries anuais do painel ampliado da Parte VII, reeleição (D-076), emendas, estoque do STF, votos |
| `nucleo.py` | núcleo analítico: janelas de inflexão, matriz sistêmica, hipóteses H1–H4, modelo provisório (D-074 a D-079) |
| `atlas.py` | registros nominais com contexto e casos de referência |
| `matriz.py` | matriz de transformação do catálogo anterior para os capítulos |
| `montar.py` | junta textos, resultados, figuras e tabelas em `livro.json` |
| `docx/montar_docx.js` | gera o `.docx` (npm `docx`) |
