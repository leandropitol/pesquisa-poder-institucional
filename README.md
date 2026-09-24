# Pesquisa documental: poder institucional no Brasil, 2003 até hoje

Base de dados auditável sobre processos, decisões e relações entre agentes do Executivo, do Legislativo
e do Judiciário brasileiros, de qualquer partido, em três eixos: esquemas ilícitos com trâmite formal,
relações externas com governos da América Latina e concentração ou abuso de poder institucional.

A pergunta é aberta e não parte de hipótese partidária. Regras em `CLAUDE.md`; protocolo, universos e
réguas em `docs/protocolo.md`.

## Estado

Fase 0 (estrutura) concluída. Etapa E1 (Câmara e Senado) coletada e normalizada em 2026-09-24, com partidos ligados ao registro no TSE (fusões, incorporações e mudanças de nome). Etapas E2 (V-Dem e Freedom House), E3 (BNDES) E4 (STJ pelo DataJud, uso restrito) e E6 (Portal da Transparência) concluídas em 2026-09-24. Etapa E8 em andamento: bloco A1 (votos da Assembleia Geral da ONU) e bloco A3 (Assembleia Geral da OEA: votações nominais conferidas contra as atas e resoluções adotadas sem votação; curadoria das resoluções concluída pelo autor). Cobertura e lacunas na parte gerada de `docs/limitacoes.md`. Plano em `docs/plano_coleta.md`.

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
| `relatorios/` | saída gerada, nunca editada à mão |
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
