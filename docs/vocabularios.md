# Vocabulários fechados

Gerado por `python -m src.estrutura` a partir de `src/vocabularios.py`. Não editar à mão.

## `eixo`

| Código | Rótulo |
|---|---|
| `esquemas_ilicitos` | Esquemas ilícitos com trâmite formal |
| `relacoes_externas` | Relações externas com governos da América Latina |
| `poder_institucional` | Concentração ou abuso de poder institucional |

## `nivel_confianca`

| Código | Rótulo |
|---|---|
| `documentado` | Documentado: decisão judicial publicada, votação nominal oficial, dado orçamentário oficial ou ato publicado |
| `sob_investigacao` | Sob investigação: inquérito, denúncia ou processo registrado, sem decisão de mérito |
| `alegado` | Alegado: só jornalismo, declarações ou colaboração premiada |

## `tipo_fonte`

| Código | Rótulo |
|---|---|
| `judicial` | Judicial |
| `legislativa` | Legislativa |
| `orcamentaria` | Orçamentária e financeira |
| `jornalistica` | Jornalística |
| `oficial` | Documento oficial (MP, PF, TCU, CGU, Itamaraty, diário oficial) |
| `base_de_dados` | Base de dados de pesquisa (V-Dem, Freedom House) |

## `classe_jornalistica`

| Código | Rótulo |
|---|---|
| `investigativa` | Reportagem investigativa |
| `factual` | Notícia factual |
| `opiniao` | Opinião, editorial ou coluna |

## `tipo_ator`

| Código | Rótulo |
|---|---|
| `agente_publico` | Agente público |
| `agente_privado` | Agente privado |

## `tipo_instituicao`

| Código | Rótulo |
|---|---|
| `orgao_publico` | Órgão público |
| `tribunal` | Tribunal |
| `ministerio_publico` | Ministério Público |
| `policia` | Polícia |
| `casa_legislativa` | Casa legislativa |
| `tribunal_de_contas` | Tribunal de contas |
| `empresa_estatal` | Empresa estatal |
| `banco_publico` | Banco público |
| `empresa_privada` | Empresa privada |
| `empresa` | Empresa (natureza pública ou privada não classificada) |
| `partido` | Partido político |
| `governo_estrangeiro` | Governo estrangeiro |
| `organismo_multilateral` | Organismo multilateral |
| `rede_partidaria_transnacional` | Rede partidária transnacional |
| `outro` | Outro |

## `poder`

| Código | Rótulo |
|---|---|
| `executivo` | Executivo |
| `legislativo` | Legislativo |
| `judiciario` | Judiciário |
| `ministerio_publico` | Ministério Público |
| `tribunal_de_contas` | Tribunal de contas |
| `nao_se_aplica` | Não se aplica |

## `esfera`

| Código | Rótulo |
|---|---|
| `federal` | Federal |
| `estadual` | Estadual |
| `municipal` | Municipal |
| `estrangeira` | Estrangeira |
| `internacional` | Internacional |
| `nao_se_aplica` | Não se aplica |

## `forma_acesso`

| Código | Rótulo |
|---|---|
| `eleito` | Eleito |
| `nomeado` | Nomeado |
| `concursado` | Concursado |
| `indicado_aprovado` | Indicado e aprovado pelo Senado |
| `outro` | Outro |

## `tipo_caso`

| Código | Rótulo |
|---|---|
| `operacao_policial` | Operação policial |
| `acao_penal` | Ação penal |
| `inquerito` | Inquérito |
| `cpi` | Comissão parlamentar de inquérito |
| `auditoria_tcu` | Auditoria ou tomada de contas do TCU |
| `outro` | Outro |

## `classe_processual`

| Código | Rótulo |
|---|---|
| `acao_penal` | Ação penal |
| `inquerito` | Inquérito |
| `peticao` | Petição |
| `habeas_corpus` | Habeas corpus |
| `adi` | Ação direta de inconstitucionalidade |
| `adpf` | Arguição de descumprimento de preceito fundamental |
| `adc` | Ação declaratória de constitucionalidade |
| `mandado_seguranca` | Mandado de segurança |
| `reclamacao` | Reclamação |
| `recurso_extraordinario` | Recurso extraordinário |
| `recurso_especial` | Recurso especial |
| `acao_civil_publica` | Ação civil pública |
| `acao_improbidade` | Ação de improbidade administrativa |
| `outra` | Outra |

## `fase_processual`

| Código | Rótulo |
|---|---|
| `instauracao_inquerito` | Instauração de inquérito |
| `arquivamento_inquerito` | Arquivamento de inquérito |
| `oferecimento_denuncia` | Oferecimento de denúncia |
| `recebimento_denuncia` | Recebimento de denúncia |
| `rejeicao_denuncia` | Rejeição de denúncia |
| `sentenca` | Sentença |
| `acordao_2a_instancia` | Acórdão de segunda instância |
| `acordao_tribunal_superior` | Acórdão de tribunal superior |
| `transito_em_julgado` | Trânsito em julgado |
| `declinio_competencia` | Declínio de competência |
| `remessa_outra_instancia` | Remessa a outra instância |
| `anulacao` | Anulação |
| `prescricao_reconhecida` | Prescrição reconhecida |
| `homologacao_colaboracao` | Homologação de colaboração premiada |
| `extincao_punibilidade` | Extinção da punibilidade |
| `outra` | Outra |

## `status_processual`

| Código | Rótulo | modelo_frase |
|---|---|---|
| `investigado` | investigado | {data}: {ator} passou a investigado em {processo}. |
| `denunciado` | denunciado | {data}: {ator} foi denunciado em {processo}{tipificacao}. |
| `reu` | réu | {data}: {ator} passou a réu em {processo}{tipificacao}. |
| `condenado_1a_instancia` | condenado em primeira instância | {data}: {ator} foi condenado em primeira instância em {processo}{tipificacao}. |
| `condenado_2a_instancia` | condenado em segunda instância | {data}: {ator} foi condenado em segunda instância em {processo}{tipificacao}. |
| `condenado_tribunal_superior` | condenado por tribunal superior | {data}: {ator} foi condenado por tribunal superior em {processo}{tipificacao}. |
| `condenado_transito_em_julgado` | condenado com trânsito em julgado | {data}: a condenação de {ator} em {processo} transitou em julgado{tipificacao}. |
| `absolvido` | absolvido | {data}: {ator} foi absolvido em {processo}. |
| `denuncia_rejeitada` | denúncia rejeitada | {data}: a denúncia contra {ator} em {processo} foi rejeitada. |
| `arquivado` | arquivado | {data}: a investigação sobre {ator} em {processo} foi arquivada. |
| `prescrito` | prescrição reconhecida | {data}: foi reconhecida a prescrição em relação a {ator} em {processo}. |
| `punibilidade_extinta` | punibilidade extinta | {data}: foi declarada extinta a punibilidade de {ator} em {processo}. |
| `condenacao_anulada` | condenação anulada | {data}: a condenação de {ator} em {processo} foi anulada. |
| `processo_anulado` | processo anulado | {data}: o processo {processo} foi anulado em relação a {ator}. |
| `colaborador` | colaborador | {data}: {ator} firmou colaboração premiada homologada em {processo}. |

## `tipo_evento`

| Código | Rótulo |
|---|---|
| `decisao_judicial` | Decisão judicial |
| `votacao_nominal` | Votação nominal |
| `operacao_policial` | Operação policial |
| `oferecimento_denuncia` | Oferecimento de denúncia |
| `contrato_publico` | Contrato público |
| `financiamento` | Financiamento |
| `acordo_bilateral` | Acordo bilateral |
| `voto_multilateral` | Voto em organismo multilateral |
| `nomeacao` | Nomeação |
| `exoneracao` | Exoneração |
| `eleicao` | Eleição |
| `cpi_instalada` | Instalação de CPI |
| `cpi_relatorio_final` | Relatório final de CPI |
| `reuniao_rede_partidaria` | Reunião de rede partidária transnacional |
| `acordo_leniencia` | Acordo de leniência |
| `sancao_administrativa` | Sanção administrativa |
| `outro` | Outro |

## `precisao_data`

| Código | Rótulo |
|---|---|
| `dia` | Dia (AAAA-MM-DD) |
| `mes` | Mês (AAAA-MM) |
| `ano` | Ano (AAAA) |

## `tipo_entidade`

| Código | Rótulo |
|---|---|
| `ator` | Ator (tabela atores) |
| `instituicao` | Instituição |
| `caso` | Caso |
| `processo` | Processo |
| `evento` | Evento |

## `tipo_relacao`

| Código | Rótulo | nivel_maximo |
|---|---|---|
| `membro_de` | é membro de |  |
| `parte_em_contrato` | é parte em contrato com |  |
| `financiou` | financiou |  |
| `controla` | controla |  |
| `subsidiaria_de` | é subsidiária de |  |
| `participou_de` | participou de |  |
| `representou_brasil_em` | representou o Brasil em |  |
| `indicou` | indicou |  |
| `relator_de` | foi relator de |  |
| `fundiu_se_em` | fundiu-se em |  |
| `incorporado_por` | foi incorporado por |  |
| `signataria_de` | é signatária de |  |
| `sancionada_em` | foi sancionada em |  |
| `citado_em_colaboracao` | foi citado em colaboração premiada de | alegado |
| `citado_em_reportagem` | foi citado em reportagem sobre | alegado |

## `predicado_afirmacao`

| Código | Rótulo | modelo_frase | nivel_maximo |
|---|---|---|---|
| `recebeu_valor` | recebeu valor de | {data}: {sujeito} recebeu valor de {objeto}{valor}. |  |
| `pagou_valor` | pagou valor a | {data}: {sujeito} pagou valor a {objeto}{valor}. |  |
| `autorizou` | autorizou | {data}: {sujeito} autorizou {objeto}. |  |
| `indicou_para_cargo` | indicou para cargo | {data}: {sujeito} indicou {objeto} para cargo. |  |
| `interveio_em` | interveio em | {data}: {sujeito} interveio em {objeto}. |  |
| `declarou` | declarou sobre | {data}: {sujeito} declarou sobre {objeto}. | alegado |
| `negou` | negou | {data}: {sujeito} negou {objeto}. |  |
| `outro` | outro | {data}: {sujeito}, {objeto}. |  |

## `resultado_verificacao`

| Código | Rótulo |
|---|---|
| `encontrado` | Casos equivalentes encontrados |
| `sem_evidencia` | Busca registrada sem resultados |
| `nao_verificado` | Não verificado |

## `grupo_verificacao`

| Código | Rótulo |
|---|---|
| `partido` | Partido |
| `governo` | Base do governo na época |
| `oposicao` | Oposição na época |

## `casa_legislativa`

| Código | Rótulo |
|---|---|
| `camara_deputados` | Câmara dos Deputados |
| `senado_federal` | Senado Federal |
| `congresso_nacional` | Congresso Nacional |
| `outra` | Outra |

## `tipo_decisao`

| Código | Rótulo |
|---|---|
| `monocratica` | Monocrática |
| `colegiada` | Colegiada |

## `voto_multilateral`

| Código | Rótulo |
|---|---|
| `sim` | Sim |
| `nao` | Não |
| `abstencao` | Abstenção |
| `ausente` | Ausente |
| `consenso` | Adotada sem votação, conforme a ata; o país não registrou nota |
| `consenso_com_nota` | Adotada sem votação, conforme a ata; o país registrou nota de rodapé no texto certificado |

## `modalidade_votacao`

| Código | Rótulo |
|---|---|
| `votacao_registrada` | Votação registrada ou nominal, com voto de cada país |
| `votacao_mao_erguida` | Votação de mão erguida, só com o total |
| `sem_votacao` | Adotada sem votação (consenso ou aclamação) |

## `indice_democracia`

| Código | Rótulo |
|---|---|
| `vdem_row` | V-Dem Regimes of the World (0 a 3) |
| `vdem_ldi` | V-Dem Liberal Democracy Index (0 a 1) |
| `fh_status` | Freedom House, status (F, PF, NF) |
| `fh_total` | Freedom House, pontuação total (-4 a 100; direitos políticos podem ficar negativos) |

## `doador_tipo`

| Código | Rótulo |
|---|---|
| `pessoa_juridica` | Pessoa jurídica |
| `pessoa_fisica_agregado` | Pessoas físicas, agregado |
| `partido` | Partido |
| `recursos_proprios` | Recursos próprios |
| `fundo_publico` | Fundo público (FEFC ou Fundo Partidário) |
| `outro` | Outro |

## `moeda`

| Código | Rótulo |
|---|---|
| `BRL` | Real |
| `USD` | Dólar americano |
| `EUR` | Euro |
| `outra` | Outra |
