# CLAUDE.md — Pesquisa documental sobre poder institucional no Brasil, 2003 até hoje

> Instruções permanentes para o Claude Code neste repositório. Ler inteiro antes de qualquer tarefa.
> Em caso de conflito entre este arquivo e um pedido pontual, perguntar antes de agir.

## 1. Pergunta de pesquisa (aberta, não confirmatória)

Quais fatores institucionais, decisões e relações entre agentes do Executivo, do Legislativo e do
Judiciário brasileiros, de qualquer partido ou orientação política, se associam de forma documentada:

1. a esquemas ilícitos com trâmite formal (eixo `esquemas_ilicitos`);
2. a apoio ou financiamento a governos de baixa qualidade democrática na América Latina
   (eixo `relacoes_externas`);
3. a episódios de concentração ou abuso de poder institucional (eixo `poder_institucional`,
   transversal aos outros dois).

Protocolo completo, universos e critérios fixados antes da coleta: `docs/protocolo.md`.

## 2. Regras metodológicas obrigatórias

1. **Sem hipótese partidária.** Nenhuma análise busca confirmar responsabilidade de um espectro político.
2. **Simetria ativa.** Todo achado que envolve ator com filiação partidária gera uma verificação em
   `verificacoes_simetria`, com resultado por partido (e por governo e oposição na época do fato) em
   `verificacao_resultado`. Relatório nenhum sai com achado sem verificação.
3. **Ausência é registrada, nunca inferida.** "Sem evidência" só existe quando há uma busca em
   `buscas` que devolveu zero resultados. Sem busca, o resultado é `nao_verificado`. Ausência de
   evidência nunca é tratada como indício, em nenhuma direção.
4. **A unidade de registro é o processo, não a narrativa.** `casos` só agrupam processos.
5. **Pessoas: só status formal.** O status de uma pessoa sai de `status_pessoa_processo`, com fonte
   judicial ou oficial, e segue o vocabulário fechado (investigado, denunciado, réu, condenado por
   instância, absolvido, arquivado, prescrito, condenação anulada etc.). Nunca inferir culpa onde não há
   decisão. Absolvições, anulações e prescrições são registradas com o mesmo cuidado que condenações.
6. **Histórico só cresce.** `fases_processo`, `status_pessoa_processo`, `fontes`, `buscas`,
   `verificacoes_simetria` e `verificacao_resultado` só recebem linhas novas. Uma mudança de status é
   uma linha nova com data, e o status vigente é calculado. O validador compara com o último commit.
7. **Nível de confiança com regra fixa** (ver `docs/protocolo.md`, seção 5): `documentado`,
   `sob_investigacao` ou `alegado`. O conteúdo de colaboração premiada é `alegado` quanto a terceiros,
   mesmo depois de homologado. Registro sustentado só por jornalismo de opinião não sustenta fato.
8. **Réguas externas fixadas antes de olhar os dados.** Qualidade democrática: V-Dem e Freedom House,
   lado a lado. Critérios de "alto impacto" e universos de casos: `docs/protocolo.md`.
9. **Denominador sempre.** Toda afirmação de associação compara com o universo (todas as operações,
   todas as decisões, todos os partidos), não com uma lista de exemplos.

## 3. Relatórios

- Relatórios são saída da base, nunca texto avulso. Cada frase vem de um registro com fonte, e cada
  fonte aparece citada.
- A linha do tempo é gerada a partir de `eventos`, `fases_processo` e `status_pessoa_processo`.
- `docs/limitacoes.md` acompanha todo relatório: parte escrita (vieses conhecidos) e parte gerada
  (cobertura e lacunas medidas na base).
- Resultados separados de interpretação.

## 4. Linguagem (código, relatórios e documentos)

| Evitar | Usar |
|---|---|
| corrupto, bandido, quadrilha, ladrão | o status formal: "denunciado por corrupção passiva (art. 317 do CP) em …" |
| "organização criminosa" como adjetivo | só como tipificação citada da peça processual |
| culpado, envolvido, implicado | investigado, denunciado, réu, condenado em primeira instância |
| "ditadura", "regime" como rótulo próprio | a classificação da régua: "autocracia eleitoral (V-Dem RoW)", "Não Livre (Freedom House)" |
| "esquema do partido X" | o processo, seus réus e o status de cada um |
| "não há provas contra" | "nenhuma busca registrada encontrou" ou "não verificado" |

Linguagem descritiva, sem adjetivos valorativos. A mesma formulação para atores de qualquer partido.

## 5. Dados pessoais (LGPD)

- Minimização: sem CPF, endereço, dados de saúde ou familiares que não sejam agentes públicos.
- Agentes privados (`tipo_ator = agente_privado`) só aparecem por nome em relatório com status formal
  de réu ou acima, ou quando a própria decisão pública os nomeia.
- Doações de pessoas físicas ao TSE entram agregadas, não por doador.
- Antes de qualquer publicação, recomendar revisão jurídica ao autor.

## 6. Auditabilidade e segurança

1. `data/raw/` é imutável e fica fora do Git. Cada arquivo baixado gera uma linha em
   `data/manifestos/` (URL, data, sha256) e uma linha em `buscas`.
2. `data/base/` (CSV) é a única fonte de verdade. Parquet e DuckDB em `data/derivados/` são gerados.
3. Nenhum número digitado à mão em relatório. Tudo sai de script.
4. Esquema em `src/esquema.py` e vocabulários em `src/vocabularios.py`. Mudou o esquema, rodar
   `python -m src.estrutura` (regenera dicionário e vocabulários) e `python -m src.validacao.validar`.
5. Chaves de API só em variável de ambiente (por exemplo `TRANSPARENCIA_API_KEY`), nunca no código.
   Respeitar limites de requisição (backoff exponencial). Downloads acima de 50 MB pedem autorização.
6. Repositório Git **local** por enquanto. Não criar remoto, não dar push e não tornar nada público
   sem pedido explícito do autor. Commits só quando o autor pedir.

## 7. Padrões de código

- Python 3.12, `pandas`, `pyarrow`, `requests`; `duckdb` quando houver consultas analíticas.
- Funções puras e testáveis. Testes em `tests/` usam somente entidades fictícias ("Ator Teste A").
- Chaves no formato `PREFIXO-000001` (ver `src/esquema.py`).
- Datas ISO parciais conforme a precisão: `AAAA`, `AAAA-MM` ou `AAAA-MM-DD`.
