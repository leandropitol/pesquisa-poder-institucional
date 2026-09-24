# Protocolo de pesquisa

Versão 0.1, 2026-09-24. Os critérios deste documento foram fixados antes da coleta. Qualquer mudança
entra em `docs/decisoes_metodologicas.md` com data e motivo, e vale para todos os atores igualmente.

## 1. Pergunta

Quais fatores institucionais, decisões e relações entre agentes do Executivo, do Legislativo e do
Judiciário brasileiros, de qualquer partido ou orientação política, se associam de forma documentada a:

1. esquemas ilícitos com trâmite formal;
2. apoio ou financiamento a governos de baixa qualidade democrática na América Latina;
3. episódios de concentração ou abuso de poder institucional.

A pergunta é aberta. O projeto não parte de hipótese partidária e não busca confirmar responsabilidade
de nenhum espectro político.

## 2. Período e unidades

- Período: 2003 até a data da coleta. Eventos anteriores entram só como contexto e são marcados.
- Unidade de registro do eixo 1: o processo (tabela `processos`). Casos só agrupam processos.
- Pessoas: só status formal por processo, com histórico datado (`status_pessoa_processo`).
- Partido de um ator: a filiação na data do fato (`filiacoes`), não a atual.

## 3. Universos (o que entra, antes de olhar os casos)

Casos conhecidos (Mensalão, Petrolão, Lava Jato, Banco Master) são casos de teste: precisam aparecer
porque pertencem ao universo, não porque foram escolhidos.

### Eixo 1, esquemas ilícitos (fase 1)

Ações penais e inquéritos originários no STF e no STJ (e petições criminais conexas) autuados a partir
de 2003, com imputação de ao menos um destes tipos:

- crimes contra a administração pública (Código Penal, Título XI, arts. 312 a 359-H);
- lavagem de dinheiro (Lei 9.613/1998);
- crimes de responsabilidade de prefeitos e vereadores (Decreto-Lei 201/1967), incluídos por emenda em 2026-09-24 (D-039);
- organização criminosa (Lei 12.850/2013) ou associação criminosa conexa;
- falsidade ideológica eleitoral (Código Eleitoral, art. 350) conexa aos anteriores.

No STJ, o universo é descoberto pela API pública do DataJud, com uso restrito (D-022): o DataJud lista os
processos, e o que for citado ou publicado vem da fonte primária do tribunal.

Ações de improbidade (Lei 8.429/1992) entram como processos cíveis, marcadas como tal. Processos de
primeira instância entram quando ligados a um caso cujo processo originário está no universo (por
exemplo, ações da Lava Jato em Curitiba). A ampliação para operações da Polícia Federal e para acórdãos
do TCU fica para a fase 2 e será registrada como decisão.

### Eixo 2, relações externas

- Todas as operações de apoio à exportação de serviços de engenharia do BNDES disponíveis em dados
  abertos, de todos os países de destino (não só da América Latina), para que haja denominador.
- Votos nominais na Assembleia Geral da ONU e na Assembleia Geral e no Conselho Permanente da OEA em
  resoluções sobre situação de direitos humanos ou de democracia em países da América Latina, com o voto
  do Brasil e dos demais países.
- Todos os acordos bilaterais do Brasil registrados pelo Itamaraty, com todos os países.
- Redes partidárias transnacionais, de todas as orientações, com a participação de partidos
  brasileiros: Foro de São Paulo, Foro de Madri, COPPPAL, UPLA, Internacional Socialista, Aliança
  Progressista, Internacional Liberal e International Democrat Union, entre outras que forem
  encontradas. Participação em rede é registrada como relação, não como indício de ilícito.

### Eixo 3, poder institucional (transversal)

- Decisões do STF disponíveis no Corte Aberta (e equivalentes do STJ), monocráticas e colegiadas.
- Uso de foro: declínios de competência e remessas entre instâncias (`fases_processo`).
- Nomeação de pessoa para cargo com foro por prerrogativa enquanto ela tinha status de investigada ou
  denunciada: calculada por código a partir de `cargos` e `status_pessoa_processo`. O relatório registra
  a coincidência de datas, não o motivo.

## 4. Réguas externas fixadas antes da análise

### Qualidade democrática (as duas, lado a lado)

| Régua | Variável | "Baixa qualidade democrática" | Intermediária |
|---|---|---|---|
| V-Dem | Regimes of the World (`v2x_regime`) | autocracia fechada (0) ou autocracia eleitoral (1) | democracia eleitoral (2) |
| Freedom House | status do país (Freedom in the World) | Não Livre (NF) | Parcialmente Livre (PF) |

- O país é classificado no ano da operação, do voto ou do acordo.
- Os resultados saem em separado para cada régua, com a concordância entre elas. Nenhuma das duas é
  combinada num índice próprio.
- A régua vale para todos os governos, de qualquer orientação.
- A base guarda os valores brutos (`qualidade_democratica`); a classificação é calculada por código.

### Decisão monocrática de alto impacto

Decisão monocrática que (a) suspende a eficácia de lei ou ato normativo, ou (b) suspende ou anula ato de
outro Poder. O relatório informa também o tempo até o referendo do colegiado. Os dois atributos são
colunas de `decisoes_judiciais`; o critério é aplicado por código.

## 5. Nível de confiança (regra aplicada pelo validador)

| Nível | Fontes ligadas que sustentam o nível |
|---|---|
| `documentado` | pelo menos uma fonte judicial, legislativa, orçamentária, oficial ou base de dados de pesquisa |
| `sob_investigacao` | pelo menos uma fonte judicial ou oficial sobre procedimento sem decisão de mérito |
| `alegado` | só jornalismo (investigativo ou factual), declarações ou colaboração premiada |

- Jornalismo de opinião sozinho não sustenta registro de fato.
- Conteúdo de colaboração premiada é `alegado` quanto a terceiros, mesmo depois de homologado
  (teto no vocabulário `tipo_relacao`).
- Status de pessoa e fase processual exigem fonte judicial ou oficial.

## 6. Simetria

Todo achado que envolve ator com filiação partidária (afirmação, relação ou status de denunciado, réu ou
condenado) recebe uma verificação:

1. o padrão do achado é descrito de forma reprodutível (tipo de fato, tipificação, período, órgão);
2. o mesmo padrão é buscado para todos os partidos do universo daquele ano (`universo_partidos`) e para
   governo e oposição na época;
3. cada grupo recebe `encontrado` (com os casos), `sem_evidencia` (com a busca de zero resultados) ou
   `nao_verificado` (com justificativa).

Relatório nenhum mostra achado sem a tabela de verificação ao lado.

## 7. O que o projeto não afirma

- Não atribui culpa sem decisão judicial e não trata denúncia, colaboração ou reportagem como prova.
- Não trata ausência de evidência como indício, nem como inocência demonstrada.
- Não infere motivo a partir de coincidência de datas.
- Não classifica governos estrangeiros por critério próprio.
