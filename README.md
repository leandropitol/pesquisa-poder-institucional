# Pesquisa documental: poder institucional no Brasil, 2003 a 2026

Base de dados auditável e estudo sobre as relações entre dinheiro, orçamento público, partidos, Justiça e
política externa no Brasil, de 2003 a 2026. Tudo é feito com dados públicos e código aberto: cada número
sai de um script, cada script lê uma base, e cada base aponta para a fonte oficial de origem.

A pergunta é aberta e não parte de hipótese sobre partido ou governo. Regras em `CLAUDE.md`; protocolo,
universos e réguas em `docs/protocolo.md`; decisões metodológicas datadas em `docs/decisoes_metodologicas.md`.

## O livro

**Dinheiro, Justiça e Poder: transformações das relações entre dinheiro, Estado, partidos, Justiça e política
externa no Brasil, 2003–2026** (segunda edição, outubro de 2026).

| Arquivo | Conteúdo |
|---|---|
| [`relatorios/livro/livro.pdf`](relatorios/livro/livro.pdf) | o livro diagramado (17 × 24 cm) |
| [`relatorios/livro/livro.docx`](relatorios/livro/livro.docx) | o mesmo livro em Word |
| `relatorios/livro/figuras/` e `relatorios/livro/tabelas/` | cada gráfico (PNG) e cada tabela (CSV) do livro |
| `relatorios/livro/fichas.json` | ficha de cada gráfico e tabela: pergunta, período, unidade, fonte, tratamento, limitações |
| `relatorios/livro/resultados.json` | todos os números citados no texto |

O livro tem oito partes: método; dinheiro das campanhas; emendas parlamentares; Justiça e controle; partidos;
relações externas; o núcleo analítico (Parte VII), que testa com regras fixadas antes do cálculo se houve
transformações sistêmicas, quando e com que evidência; e o Atlas documental, com registros nominais, fichas e
referências. Cada capítulo termina com o que os dados permitem e não permitem afirmar.

Para refazer o livro a partir da base:

```bash
pip install -r requirements.txt
python -m src.livro             # cálculos, figuras, tabelas, fichas e livro.json
python -m src.livro.diagramar   # livro.docx e livro.pdf (precisa de Node com o pacote docx e de LibreOffice)
```

Detalhes em `src/livro/README.md`.

## O projeto em números

Contagens de 2 de outubro de 2026.

| | |
|---|---|
| Tabelas da base (`data/base/`) | 34, com cerca de 217 mil linhas |
| Emendas parlamentares | 92.364 registros |
| Votos em resoluções da ONU e da OEA | 26.696 |
| Registros de financiamento de campanha | 12.613 |
| Processos judiciais | 10.782 |
| Acordos bilaterais | 7.720 |
| Operações de exportação do BNDES | 2.996 |
| Fontes catalogadas | 342, das quais 326 oficiais |
| Buscas registradas, inclusive as sem resultado | 1.017 |
| Decisões metodológicas documentadas | 79 (D-001 a D-079) |
| Arquivos brutos baixados | cerca de 2.170, com URL, data e sha256 em `data/manifestos/` |

Fontes: TSE, CGU, Tesouro Nacional, STF, TCU, Câmara dos Deputados, Senado Federal, IBGE, BNDES, Itamaraty,
Nações Unidas, OEA, V-Dem e Freedom House.

## Como conferir

- Os arquivos brutos (`data/raw/`, cerca de 2,5 GB) ficam fora do Git. O que está no repositório é o registro
  de cada um em `data/manifestos/`: endereço de origem, data do download e sha256. Quem baixar o mesmo arquivo
  pode comparar a impressão digital.
- `data/base/` traz as tabelas normalizadas, e `data/base/fontes.csv` liga cada registro à sua fonte.
- `data/base/buscas.csv` registra todas as buscas feitas, inclusive as que não encontraram nada.
- `docs/limitacoes.md` lista os vieses conhecidos e a cobertura medida de cada base.

Correções e contestações são bem-vindas pelas *issues* do repositório.

## Estado

Fase 0 (estrutura) concluída. Etapa E1 (Câmara e Senado) coletada e normalizada em 2026-09-24, com partidos ligados ao registro no TSE (fusões, incorporações e mudanças de nome). Etapas E2 (V-Dem e Freedom House), E3 (BNDES), E4 (STJ pelo DataJud, uso restrito), E5 (STF pelo Corte Aberta, exportação feita pelo autor; universo com revisão pendente), E6 (Portal da Transparência) concluídas em 2026-09-24. Etapa E8 em andamento: blocos A1 e A2 (votos na Assembleia Geral e no Conselho de Direitos Humanos da ONU), bloco B (atos bilaterais do Itamaraty), bloco D (filiação de partidos brasileiros a redes transnacionais) e bloco A3 (Assembleia Geral da OEA: votações nominais conferidas contra as atas e resoluções adotadas sem votação; curadoria das resoluções concluída pelo autor). Cobertura e lacunas na parte gerada de `docs/limitacoes.md`. Plano em `docs/plano_coleta.md`.

## Relatórios da base

Saídas geradas por código a partir da base (nenhum número digitado à mão), com fonte citada em cada frase:

| Arquivo | Conteúdo |
|---|---|
| `relatorios/relatorio_final.md` | resultados por eixo, simetria, interpretação separada dos resultados e apêndice de fontes |
| `relatorios/linha_do_tempo.md` | status formais de pessoas em processos, por ano, com partido, grupo (governo ou oposição) e fonte |
| `relatorios/linha_do_tempo_status.csv`, `relatorios/linha_do_tempo_fases_eventos.csv` | os mesmos dados em tabela, mais fases de processo e eventos |
| `docs/nota_metodologica.md` | definições, fontes, regras, métodos estatísticos e índice das decisões metodológicas |
| `docs/limitacoes.md` | vieses conhecidos e cobertura medida na base |

```bash
python -m src.relatorios.limitacoes
python -m src.relatorios.linha_do_tempo
python -m src.relatorios.relatorio_final
python -m src.relatorios.nota_metodologica
```

Recomenda-se revisão jurídica antes de reproduzir os registros nominais: o material nomeia agentes públicos com status formal de processos. Status formal não é juízo sobre os fatos.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `docs/` | protocolo, dicionário de dados e vocabulários (gerados), decisões metodológicas, limitações |
| `data/raw/` | downloads imutáveis, fora do Git |
| `data/manifestos/` | URL, data e sha256 de cada download |
| `data/staging/` | dados normalizados por fonte, fora do Git |
| `data/curadoria/` | registros inseridos à mão (casos, jornalismo), para revisão antes de entrar na base |
| `data/vocabularios/` | vocabulários fechados em CSV (gerados) |
| `data/base/` | tabelas canônicas em CSV, única fonte de verdade |
| `src/` | esquema, coleta, normalização, validação, simetria e relatórios |
| `src/livro/` | scripts e textos que geram o livro |
| `relatorios/` | saída gerada, nunca editada à mão |
| `relatorios/livro/` | o livro (PDF e Word), figuras, tabelas, fichas e resultados |
| `tests/` | testes com entidades fictícias |

## Comandos

```bash
python -m src.estrutura
```

```bash
python -m src.validacao.validar
```

```bash
python -m pytest -q
```
