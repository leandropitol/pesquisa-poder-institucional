# Dicionário de dados

Gerado por `python -m src.estrutura` a partir de `src/esquema.py`. Não editar à mão.

Cada tabela é um CSV em `data/base/`. Tipos: `id` (PREFIXO-000001), `ref` (referência), `data` (AAAA, AAAA-MM ou AAAA-MM-DD), `vocab` (vocabulário fechado, ver `docs/vocabularios.md`), `lista` (identificadores separados por `;`), `bool` (true/false), `iso3` (código de país).

## Entidades

### `atores`

Pessoas físicas: agentes públicos e privados. Sem CPF, endereço ou familiares. Chave: `id_ator`; prefixo `ATR`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_ator` | id | sim |  |
| `nome` | texto | sim | Nome como aparece em fonte oficial |
| `nome_normalizado` | texto | sim | Minúsculas, sem acento, para busca e deduplicação |
| `tipo_ator` | vocab (`tipo_ator`) | sim |  |
| `id_camara` | texto |  | Identificador na API de dados abertos da Câmara |
| `id_senado` | texto |  | Código do parlamentar no Senado |
| `observacao` | texto |  |  |

### `filiacoes`

Filiação partidária no tempo. A análise usa a filiação na data do fato. Chave: `id_filiacao`; prefixo `FIL`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_filiacao` | id | sim |  |
| `id_ator` | ref → `atores.id_ator` | sim |  |
| `id_partido` | ref → `instituicoes.id_instituicao` | sim | Instituição de tipo partido |
| `data_inicio` | data | sim |  |
| `data_fim` | data |  |  |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |

### `cargos`

Cargos ocupados no tempo. Chave: `id_cargo`; prefixo `CRG`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_cargo` | id | sim |  |
| `id_ator` | ref → `atores.id_ator` | sim |  |
| `id_instituicao` | ref → `instituicoes.id_instituicao` | sim |  |
| `cargo` | texto | sim |  |
| `forma_acesso` | vocab (`forma_acesso`) | sim |  |
| `data_inicio` | data | sim |  |
| `data_fim` | data |  |  |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |

### `instituicoes`

Órgãos, tribunais, empresas, partidos, governos estrangeiros, organismos e redes partidárias. Chave: `id_instituicao`; prefixo `INS`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_instituicao` | id | sim |  |
| `nome` | texto | sim |  |
| `sigla` | texto |  |  |
| `tipo_instituicao` | vocab (`tipo_instituicao`) | sim |  |
| `poder` | vocab (`poder`) | sim |  |
| `esfera` | vocab (`esfera`) | sim |  |
| `pais_iso3` | iso3 | sim | País sede (BRA para instituições brasileiras) |
| `cnpj` | texto |  | Só para pessoa jurídica brasileira |
| `id_sucessora` | ref → `instituicoes.id_instituicao` |  | Instituição que a sucedeu (fusão ou mudança de nome de partido) |
| `observacao` | texto |  |  |

### `denominacoes_partido`

Siglas e nomes de cada partido (registro no TSE) ao longo do tempo. Mudança de nome ou sigla não cria partido novo. Chave: `id_denominacao`; prefixo `DNP`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_denominacao` | id | sim |  |
| `id_partido` | ref → `instituicoes.id_instituicao` | sim | Instituição de tipo partido |
| `sigla` | texto | sim |  |
| `nome` | texto | sim |  |
| `data_inicio` | data |  | Vazia quando anterior aos registros consultados |
| `data_fim` | data |  | Data da decisão que mudou o nome, fundiu ou incorporou o partido |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |

### `casos`

Agrupamento de processos (operação, ação penal, CPI). Não é unidade de registro. Chave: `id_caso`; prefixo `CAS`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_caso` | id | sim |  |
| `nome` | texto | sim |  |
| `tipo_caso` | vocab (`tipo_caso`) | sim |  |
| `eixo` | vocab (`eixo`) | sim |  |
| `data_inicio` | data | sim |  |
| `criterio_inclusao` | texto | sim | Por que o caso entrou no universo (ver docs/protocolo.md) |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |

### `processos`

Processos judiciais e procedimentos formais. Unidade de registro do eixo 1. Chave: `id_processo`; prefixo `PRC`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_processo` | id | sim |  |
| `numero_cnj` | texto |  | Numeração única CNJ, quando existir |
| `numero_originario` | texto | sim | Ex.: AP 470, Inq 4.130 |
| `classe` | vocab (`classe_processual`) | sim |  |
| `id_tribunal` | ref → `instituicoes.id_instituicao` | sim |  |
| `id_relator_atual` | ref → `atores.id_ator` |  |  |
| `data_autuacao` | data | sim |  |
| `id_caso` | ref → `casos.id_caso` |  |  |
| `sigilo` | bool | sim |  |
| `url` | url | sim |  |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |

### `fases_processo`

Histórico de fases de cada processo. Chave: `id_fase`; prefixo `FAS`; só cresce (histórico).

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_fase` | id | sim |  |
| `id_processo` | ref → `processos.id_processo` | sim |  |
| `data` | data | sim |  |
| `fase` | vocab (`fase_processual`) | sim |  |
| `id_orgao_julgador` | ref → `instituicoes.id_instituicao` |  |  |
| `resumo` | texto |  | Resumo factual curto do dispositivo |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |

### `status_pessoa_processo`

Histórico do status formal de cada pessoa em cada processo. O vigente é o de data mais recente. Chave: `id_status`; prefixo `STA`; só cresce (histórico).

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_status` | id | sim |  |
| `id_ator` | ref → `atores.id_ator` | sim |  |
| `id_processo` | ref → `processos.id_processo` | sim |  |
| `data` | data | sim |  |
| `status` | vocab (`status_processual`) | sim |  |
| `tipificacao` | texto |  | Crime ou ato imputado como consta da peça, com artigo |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte judicial ou oficial |

### `eventos`

Fatos datados que alimentam a linha do tempo. Chave: `id_evento`; prefixo `EVT`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_evento` | id | sim |  |
| `data` | data | sim |  |
| `precisao_data` | vocab (`precisao_data`) | sim |  |
| `tipo_evento` | vocab (`tipo_evento`) | sim |  |
| `eixo` | vocab (`eixo`) | sim |  |
| `descricao` | texto | sim | Frase factual curta, sem adjetivos |
| `pais_iso3` | iso3 | sim |  |
| `valor` | decimal |  |  |
| `moeda` | vocab (`moeda`) |  |  |
| `id_processo` | ref → `processos.id_processo` |  |  |
| `nivel_confianca` | vocab (`nivel_confianca`) | sim |  |

### `relacoes`

Relações entre entidades (membro de, financiou, controla…). Chave: `id_relacao`; prefixo `REL`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_relacao` | id | sim |  |
| `origem_tipo` | vocab (`tipo_entidade`) | sim |  |
| `origem_id` | texto | sim |  |
| `tipo_relacao` | vocab (`tipo_relacao`) | sim |  |
| `destino_tipo` | vocab (`tipo_entidade`) | sim |  |
| `destino_id` | texto | sim |  |
| `data_inicio` | data | sim |  |
| `data_fim` | data |  |  |
| `eixo` | vocab (`eixo`) |  | Vazio em relações estruturais (por exemplo, fusão de partidos) |
| `nivel_confianca` | vocab (`nivel_confianca`) | sim |  |

### `afirmacoes`

Afirmações que os relatórios podem fazer, em forma sujeito-predicado-objeto. Chave: `id_afirmacao`; prefixo `AFI`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_afirmacao` | id | sim |  |
| `sujeito_tipo` | vocab (`tipo_entidade`) | sim |  |
| `sujeito_id` | texto | sim |  |
| `predicado` | vocab (`predicado_afirmacao`) | sim |  |
| `objeto_tipo` | vocab (`tipo_entidade`) | sim |  |
| `objeto_id` | texto | sim |  |
| `data` | data | sim |  |
| `valor` | decimal |  |  |
| `moeda` | vocab (`moeda`) |  |  |
| `eixo` | vocab (`eixo`) | sim |  |
| `nivel_confianca` | vocab (`nivel_confianca`) | sim |  |
| `observacao_interna` | texto |  | Nunca vai para relatório |

## Fontes

### `fontes`

Registro comum de toda fonte. Cada fonte tem uma linha na tabela do seu tipo. Chave: `id_fonte`; prefixo `FNT`; só cresce (histórico).

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_fonte` | id | sim |  |
| `tipo_fonte` | vocab (`tipo_fonte`) | sim |  |
| `titulo` | texto | sim |  |
| `data_publicacao` | data | sim |  |
| `url` | url | sim |  |
| `url_arquivada` | url |  | Cópia em arquivo da web (Wayback, archive.today) |
| `data_acesso` | data | sim |  |
| `sha256` | sha256 |  | Do arquivo bruto em data/raw, quando baixado |
| `caminho_raw` | texto |  |  |
| `licenca` | texto |  |  |
| `observacao` | texto |  |  |

### `fonte_judicial`

Campos obrigatórios da fonte judicial. Chave: `id_fonte`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_fonte` | ref → `fontes.id_fonte` | sim |  |
| `numero_processo` | texto | sim |  |
| `id_orgao` | ref → `instituicoes.id_instituicao` | sim |  |
| `data_documento` | data | sim |  |
| `fase_processual` | vocab (`fase_processual`) | sim |  |
| `tipo_documento` | texto | sim | Decisão, acórdão, denúncia, despacho… |
| `link_publico` | url | sim |  |

### `fonte_legislativa`

Campos obrigatórios da fonte legislativa. Chave: `id_fonte`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_fonte` | ref → `fontes.id_fonte` | sim |  |
| `casa` | vocab (`casa_legislativa`) | sim |  |
| `proposicao` | texto | sim |  |
| `id_votacao` | texto |  | Identificador da votação nominal no portal da Casa |
| `data` | data | sim |  |
| `link_portal` | url | sim |  |

### `fonte_orcamentaria`

Campos obrigatórios da fonte orçamentária e financeira. Chave: `id_fonte`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_fonte` | ref → `fontes.id_fonte` | sim |  |
| `id_orgao` | ref → `instituicoes.id_instituicao` | sim |  |
| `valor` | decimal | sim |  |
| `moeda` | vocab (`moeda`) | sim |  |
| `ano` | ano | sim |  |
| `conjunto_dados` | texto | sim |  |
| `link_dado_aberto` | url | sim |  |

### `fonte_jornalistica`

Campos obrigatórios da fonte jornalística. Chave: `id_fonte`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_fonte` | ref → `fontes.id_fonte` | sim |  |
| `veiculo` | texto | sim |  |
| `classe_jornalistica` | vocab (`classe_jornalistica`) | sim |  |

### `fonte_oficial`

Documento oficial não judicial (MP, PF, TCU, CGU, Itamaraty, diário oficial). Chave: `id_fonte`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_fonte` | ref → `fontes.id_fonte` | sim |  |
| `id_orgao` | ref → `instituicoes.id_instituicao` | sim |  |
| `tipo_documento` | texto | sim |  |
| `data_documento` | data | sim |  |
| `link` | url | sim |  |

### `fonte_base_dados`

Base de dados de pesquisa (V-Dem, Freedom House). Chave: `id_fonte`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_fonte` | ref → `fontes.id_fonte` | sim |  |
| `organizacao` | texto | sim |  |
| `conjunto` | texto | sim |  |
| `versao` | texto | sim |  |
| `variavel` | texto |  |  |
| `link` | url | sim |  |

### `evento_fonte`

Fontes de cada evento. Chave: `id_evento, id_fonte`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_evento` | ref → `eventos.id_evento` | sim |  |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |
| `localizador` | texto |  | Página, parágrafo ou item na fonte |

### `relacao_fonte`

Fontes de cada relação. Chave: `id_relacao, id_fonte`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_relacao` | ref → `relacoes.id_relacao` | sim |  |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |
| `localizador` | texto |  |  |

### `afirmacao_fonte`

Fontes de cada afirmação. Chave: `id_afirmacao, id_fonte`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_afirmacao` | ref → `afirmacoes.id_afirmacao` | sim |  |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |
| `localizador` | texto |  |  |

## Rastreabilidade

### `buscas`

Toda consulta de coleta. É o registro formal de ausência (n_resultados = 0). Chave: `id_busca`; prefixo `BSC`; só cresce (histórico).

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_busca` | id | sim |  |
| `data` | data | sim |  |
| `fonte_dados` | texto | sim | API ou portal consultado |
| `consulta` | texto | sim | Descrição reprodutível da consulta |
| `parametros_json` | texto |  |  |
| `n_resultados` | inteiro | sim |  |
| `sha256_resposta` | sha256 |  |  |
| `caminho_raw` | texto |  |  |
| `script` | texto | sim |  |

### `verificacoes_simetria`

Verificação de casos equivalentes em outros partidos para um achado. Chave: `id_verificacao`; prefixo `VSM`; só cresce (histórico).

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_verificacao` | id | sim |  |
| `achado_tabela` | texto | sim | afirmacoes, relacoes ou status_pessoa_processo |
| `achado_id` | texto | sim |  |
| `padrao_buscado` | texto | sim | Padrão descrito de forma reprodutível |
| `ano_referencia` | ano | sim | Ano do fato, que define o universo de partidos |
| `data` | data | sim |  |
| `script` | texto | sim |  |

### `verificacao_resultado`

Resultado por partido, e por governo e oposição, de cada verificação. Chave: `id_resultado`; prefixo `VRS`; só cresce (histórico).

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_resultado` | id | sim |  |
| `id_verificacao` | ref → `verificacoes_simetria.id_verificacao` | sim |  |
| `grupo_tipo` | vocab (`grupo_verificacao`) | sim |  |
| `grupo_id` | texto | sim | id_instituicao do partido, ou 'governo' / 'oposicao' |
| `resultado` | vocab (`resultado_verificacao`) | sim |  |
| `n_casos` | inteiro |  |  |
| `ids_encontrados` | lista |  |  |
| `id_busca` | ref → `buscas.id_busca` |  |  |
| `justificativa` | texto |  | Obrigatória quando não verificado |

### `universo_partidos`

Partidos que toda verificação de um ano deve cobrir. Chave: `ano, id_partido`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `ano` | ano | sim |  |
| `id_partido` | ref → `instituicoes.id_instituicao` | sim |  |
| `criterio` | texto | sim | Ex.: bancada na Câmara no início do ano |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |

## Eixo relacoes externas

### `qualidade_democratica`

Valores brutos das réguas externas, por país e ano. A classificação é calculada por código. Chave: `pais_iso3, ano, indice`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `pais_iso3` | iso3 | sim |  |
| `ano` | ano | sim |  |
| `indice` | vocab (`indice_democracia`) | sim |  |
| `valor` | texto | sim |  |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |

### `operacoes_exportacao_bndes`

Todas as operações de apoio à exportação de serviços do BNDES (universo, não amostra). Chave: `id_operacao`; prefixo `BND`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_operacao` | id | sim |  |
| `numero_contrato` | texto |  |  |
| `data_contratacao` | data | sim |  |
| `pais_iso3` | iso3 | sim |  |
| `id_exportadora` | ref → `instituicoes.id_instituicao` | sim |  |
| `id_devedor` | ref → `instituicoes.id_instituicao` |  | Governo ou entidade importadora |
| `descricao_projeto` | texto | sim |  |
| `modalidade` | texto |  |  |
| `valor` | decimal | sim |  |
| `moeda` | vocab (`moeda`) | sim |  |
| `situacao` | texto |  | Situação de pagamento informada pelo BNDES |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |

### `votos_multilaterais`

Votos por país em resoluções de organismos multilaterais (Brasil e demais países). Chave: `id_voto`; prefixo `VOT`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_voto` | id | sim |  |
| `id_organismo` | ref → `instituicoes.id_instituicao` | sim |  |
| `resolucao` | texto | sim |  |
| `tema` | texto | sim |  |
| `data` | data | sim |  |
| `pais_iso3` | iso3 | sim |  |
| `voto` | vocab (`voto_multilateral`) | sim |  |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |

### `acordos_bilaterais`

Acordos bilaterais do Brasil (todos os países, para ter denominador). Chave: `id_acordo`; prefixo `ACO`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_acordo` | id | sim |  |
| `pais_iso3` | iso3 | sim |  |
| `titulo` | texto | sim |  |
| `tema` | texto | sim |  |
| `data_assinatura` | data | sim |  |
| `data_vigencia` | data |  |  |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |

## Eixo poder institucional

### `decisoes_judiciais`

Decisões (universo do Corte Aberta e equivalentes), com atributos para o critério de alto impacto. Chave: `id_decisao`; prefixo `DEC`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_decisao` | id | sim |  |
| `id_processo` | ref → `processos.id_processo` | sim |  |
| `data` | data | sim |  |
| `tipo_decisao` | vocab (`tipo_decisao`) | sim |  |
| `id_relator` | ref → `atores.id_ator` |  |  |
| `resultado` | texto | sim |  |
| `suspende_ato_normativo` | bool | sim |  |
| `atinge_ato_de_outro_poder` | bool | sim |  |
| `data_referendo` | data |  | Data em que o colegiado apreciou a decisão monocrática |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |

## Financiamento

### `doacoes_campanha`

Receitas de campanha (TSE). Pessoas físicas só em agregado. Chave: `id_doacao`; prefixo `DOA`.

| Coluna | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `id_doacao` | id | sim |  |
| `ano_eleicao` | ano | sim |  |
| `id_ator` | ref → `atores.id_ator` | sim | Candidato |
| `doador_tipo` | vocab (`doador_tipo`) | sim |  |
| `id_doador` | ref → `instituicoes.id_instituicao` |  | Só para pessoa jurídica ou partido |
| `valor` | decimal | sim |  |
| `id_fonte` | ref → `fontes.id_fonte` | sim | Fonte que sustenta o registro |
