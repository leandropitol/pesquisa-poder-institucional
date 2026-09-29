# Relatório de levantamento de dados públicos — Portal do STF

**Data e hora da consulta:** 24/09/2026, entre 14:58 e 15:28 (horário de Brasília)
**Fonte:** https://portal.stf.jus.br e https://transparencia.stf.jus.br (Corte Aberta)
**Escopo:** registro literal do que consta nas páginas oficiais. Sem interpretação de mérito.

## Resumo

- Nada foi baixado além das duas exportações XLSX autorizadas (Anexos A e B). Não houve login, CAPTCHA, 403 ou "acesso negado".
- Tarefa 1 concluída: painéis de Decisões e Acervo abertos, filtros AP e Inq aplicados, exportação XLSX feita nos dois.
- Tarefa 2 concluída para AP 470, HC 164493, HC 193726, Rcl 43007 e para a busca "Banco Master".
- Pendência: listagem de nome, data e URL dos documentos das abas "Peças" e "Decisões" de cada processo (ver seção 4).

## Anexos

| Anexo | Origem | Filtro aplicado | Total no painel | Nome/tamanho do arquivo |
|---|---|---|---|---|
| **A — Planilha de decisões** (XLSX) | Painel Decisões, botão "Decisões" | Classe AP e Inq; Data decisão 08/01/2003 a 23/09/2026 | 17.202 decisões (todas em originários) | Não informado pelo site antes do clique; o download ocorre no navegador. Verificar em Ctrl+J. |
| **B — Planilha de acervo** (XLSX) | Painel Acervo, botão "Processos" | Classe Processo AP e Inq (acervo em tramitação hoje) | 1.331 processos (todos originários) | Idem. |

Confirmação da exportação (console da página): "Exportação em XLSX" seguido de "Exportação concluída com sucesso" às 15:09 (Anexo A) e 15:28 (Anexo B).

**Limitação:** não abri as planilhas. O número de linhas de cada uma deve ser conferido contra os totais da coluna "Total no painel".

## 1. Tarefa 1 — Corte Aberta

### Caminho
Página inicial > rodapé, "Painéis estatísticos - Corte aberta". O link tem `target=_blank` e o clique não navegou na aba. Abri o mesmo endereço do link (sem "/hub/"):
- https://transparencia.stf.jus.br/extensions/corte_aberta/corte_aberta.html

O portal abre cada painel em uma segunda aba do mesmo grupo. Fechei essas abas ao terminar cada uso.

### Painel de Decisões
- **URL:** https://transparencia.stf.jus.br/extensions/decisoes/decisoes.html
- **Padrão ao abrir:** filtrado em "Ano da decisão: 2026" (87.462 decisões).
- **Filtros disponíveis:** Processo, Relator decisão, Ano da decisão, Data decisão (período), Órgão julgador, Tipo decisão, Tipo de origem decisão, Ambiente de julgamento, Andamento decisão, Observação decisão, Classe, Assunto, Ramo direito, Em trâmite?, Meio do processo.
- **Filtro AP e Inq (aplicado):** a Classe aceita seleção múltipla. Selecionei AP e Inq; a faixa de seleção mostrou "Classe Processo, 2 de 47".
- **Período 2003 até hoje (aplicado):** removi o filtro padrão de 2026 e usei o seletor de período. O painel tem dados de 27/01/2000 a 23/09/2026. Digitei 01/01/2003 e o painel ajustou para **08/01/2003** (primeira data com dados). Data final: 23/09/2026.
- **Resultado:** 17.202 decisões, todas em processos originários (0 recursais). Sem o corte de 2003, AP e Inq desde 2000 somavam 17.696.
- **Exportação:** botão "Decisões", topo à direita. Texto exibido: "Exportar dados relacionados a aba corrente em planilha Excel. Reflete o filtro atual." Formato: XLSX. Gerou o **Anexo A**.

### Painel de Acervo
- **URL:** https://transparencia.stf.jus.br/extensions/acervo/acervo.html
- **Abas:** Acervo, Acervo histórico, Situação do acervo, Tempo em tramitação, Partes, ODS | Preferência, Lista de processos.
- **Sem filtro:** 21.958 processos (10.270 originários; 11.688 recursais).
- **Filtro aplicado:** Classe Processo AP e Inq ("2 de 36"). Só AP: 1.274. AP e Inq: **1.331**, todos originários.
- **Exportação:** botão "Processos". Mesmo texto de exportação para Excel. Formato: XLSX. Gerou o **Anexo B**.
- **Observação:** o Acervo é a fotografia dos processos em tramitação. A aba "Acervo histórico" não foi aberta.

### Erros encontrados (nenhum era CAPTCHA ou bloqueio de acesso)

| Onde | Mensagem literal | Resolução |
|---|---|---|
| corte_aberta.html, com o painel de Decisões aberto em outra aba | "Ocorreu um erro — Não é possível conectar-se ao mecanismo do Qlik Sense. Causas possíveis: muitas conexões abertas, o serviço está off-line ou problemas de rede." | Fechei a aba extra e recarreguei. |
| acervo.html, em duas tentativas seguidas | Tela parada em "Carregando filtros essenciais… (0/4)"; console com "Erro ao carregar KPI-1-1, tentando novamente" (e CHART-1-1 a CHART-1-4). O erro do Qlik Sense acima reapareceu na tela dos painéis. | Parei; na terceira tentativa, mais tarde, o painel carregou normalmente. |
| https://portal.stf.jus.br/pesquisa/default.asp (busca "Conteúdo e Notícias" por "Banco Master") | "Erro ao buscar resultados." | Duas tentativas, sem sucesso. Usei a consulta processual "Por Parte" (seção 2.5). |

## 2. Tarefa 2 — Processos

Convenções: os andamentos abaixo estão como aparecem na aba "Andamentos" de cada processo, com texto literal curto. A URL de cada linha é a da página do processo, a mesma dos dados gerais. "Órgão julgador" só aparece dentro do texto de andamentos, não no cabeçalho.

### 2.1 AP 470

**Dados gerais**
- Classe e número: AP 470 (número único 0007214-12.2007.1.00.0000)
- URL: https://portal.stf.jus.br/processos/detalhe.asp?incidente=11541
- Relator(a): MIN. LUÍS ROBERTO BARROSO. Redator do acórdão: MIN. LUÍS ROBERTO BARROSO.
- Protocolo: 12/11/2007. Andamento "Autuado" em 12/11/2007.
- Órgão julgador: "TRIBUNAL PLENO" (texto do andamento de 17/12/2012).
- Volume: 8.511 andamentos na página. Extraí só os que indicam fase.

| data | andamento (texto literal) | URL |
|---|---|---|
| 12/11/2007 | Autuado | detalhe.asp?incidente=11541 |
| 12/11/2007 | Distribuído por prevenção — "MIN. JOAQUIM BARBOSA" | idem |
| 17/12/2012 | Procedente em parte — "Decisão de Julgamento TRIBUNAL PLENO Decisão: Prosseguindo no julgamento quanto à questão da perda do mandato eletivo…" | idem |
| 15/03/2013 | Publicado acórdão, DJE (3 registros) | idem |
| 18/04/2013 | Provido em parte — "Decisão de Julgamento TRIBUNAL PLENO Decisão: O Tribunal, por maioria, deu parcial provimento ao agravo regimental…" | idem |
| 22/04/2013 | Publicado acórdão, DJE (3 registros) | idem |
| 03/05/2013 | Transitado(a) em julgado — "…DO ACÓRDÃO PUBLICADO NO DIA 22/4/2013…" | idem |
| 24/09/2013 e 10/10/2013 | Publicado acórdão, DJE | idem |
| 14/11/2013, 15/11/2013, 02/12/2013, 05/12/2013, 12/12/2013, 18/12/2013 | Transitado(a) em julgado (certidões referentes ao acórdão publicado em 10/10/2013) | idem |
| 06/01/2014 e 11/02/2014 | Transitado(a) em julgado (mesmo acórdão, outros réus) | idem |
| 20/02/2014 | Suspenso o julgamento — "…O Tribunal, por unanimidade, aprovou questão de ordem…" | idem |
| 15/05/2014 | Transitado(a) em julgado — "…do acórdão publicado no dia 2/5/2014" | idem |
| 02/09/2014 | Transitado(a) em julgado — "referente ao acórdão publicado em 21/8/2014, relativo aos Embargos Infringentes…" | idem |
| 09/06/2022; 08/02/2023; 09/05/2023; 11/12/2023 (2 registros) | Baixa ao arquivo do STF, Guia nº | idem |

Totais na página: 30 andamentos "Transitado(a) em julgado" (03/05/2013 a 02/09/2014), 94 "Publicado acórdão, DJE", 205 "Ata de Julgamento Publicada, DJE". Último andamento listado: 21/09/2026 (petição).
Nenhum andamento contém "recebimento da denúncia", "extinção" ou "prescrição" (0 ocorrências, buscadas em título e texto).

### 2.2 HC 164493

**Dados gerais**
- Classe e número: HC 164493 (0081750-08.2018.1.00.0000). Processo eletrônico, segredo de justiça; partes só com iniciais.
- URL: https://portal.stf.jus.br/processos/detalhe.asp?incidente=5581966
- Relator(a): MIN. EDSON FACHIN. Redator do acórdão: MIN. GILMAR MENDES.
- Protocolo: 05/11/2018. Andamento "Autuado" em 05/11/2018.
- Órgão julgador: "2ª TURMA" (texto do andamento de 23/03/2021).
- **Conferência de conteúdo:** Origem PR; coator STJ; assuntos "Ação Penal | Nulidade | Suspeição". O termo "Lava Jato" **não aparece** literalmente. A página cita "a Ação Penal n. 5046512-94.2016.4.04.7000/PR" e "o juiz excepto Sérgio Fernando Moro". Registrei os andamentos porque o conteúdo é compatível, mas a página não usa o nome da operação.

| data | andamento (texto literal) | URL |
|---|---|---|
| 05/11/2018 | Autuado | detalhe.asp?incidente=5581966 |
| 05/11/2018 | Distribuído por prevenção — "MIN. EDSON FACHIN. Prevenção do Relator/Sucessor…" | idem |
| 13/12/2018 | Ata de Julgamento Publicada, DJE — "ATA Nº 36, de 04/12/2018" | idem |
| 08/08/2019 | Ata de Julgamento Publicada, DJE — "ATA Nº 17, de 25/06/2019" | idem |
| 17/03/2021 | Ata de Julgamento Publicada, DJE — "ATA Nº 5, de 09/03/2021" | idem |
| 23/03/2021 | Concedida a ordem — "2ª TURMA Decisão: Após a apresentação de voto-vista do Ministro Nunes Marques…, a Turma, por maioria, concedeu a ordem em habeas corpus, determinando a anulação de todos os atos decisórios…" | idem |
| 05/04/2021 | Ata de Julgamento Publicada, DJE — "ATA Nº 7, de 23/03/2021" | idem |
| 04/06/2021 | Publicado acórdão, DJE — "ATA Nº 95/2021" | idem |
| 24/06/2021 | Deferido — MIN. GILMAR MENDES | idem |

Não encontrei "trânsito em julgado" nem "baixa" nos títulos dos andamentos. Andamento mais recente: 15/12/2025.

### 2.3 HC 193726

**Dados gerais**
- Classe e número: HC 193726 (0107332-39.2020.1.00.0000). Processo eletrônico, público.
- URL: https://portal.stf.jus.br/processos/detalhe.asp?incidente=6043118
- Relator(a): MIN. EDSON FACHIN. Redator do acórdão: MIN. GILMAR MENDES.
- Protocolo: 04/11/2020. Andamento "Autuado" em 04/11/2020.
- Órgão julgador: "TRIBUNAL PLENO" (textos de abril e junho de 2021).
- **Conferência de conteúdo:** Origem PR; coator STJ; assuntos "Jurisdição e Competência" e "Ação Penal | Nulidade". A decisão de 08/03/2021 cita "a incompetência da 13ª Vara Federal da Subseção Judiciária de Curitiba". "Lava Jato" **não aparece** literalmente.

| data | andamento (texto literal) | URL |
|---|---|---|
| 04/11/2020 | Autuado | detalhe.asp?incidente=6043118 |
| 04/11/2020 | Distribuído por prevenção — "MIN. EDSON FACHIN. Prevenção do Relator/Sucessor…" | idem |
| 08/03/2021 | Deferido — MIN. EDSON FACHIN: "…concedo a ordem de habeas corpus para declarar a incompetência da 13ª Vara Federal da Subseção Judiciária de Curitiba…" | idem |
| 14/04/2021 | Agravo regimental não provido — "TRIBUNAL PLENO Decisão: (AgR-AgR) O Tribunal, por maioria, negou provimento ao agravo regimental interposto contra a decisão de afetação…" | idem |
| 15/04/2021 | Agravo regimental não provido — "(AgR) O Tribunal, por maioria, negou provimento ao agravo regimental…" | idem |
| 22/04/2021 | Agravo regimental não provido — "(AgR) Nesta assentada, o Plenário apreciou a questão relativa à competência do juízo…" | idem |
| 11/05/2021 | Indeferido — MIN. EDSON FACHIN | idem |
| 23/06/2021 | Agravo regimental provido — "(Seg-AgR) O Tribunal, por maioria, deu provimento ao…" | idem |
| 01/09/2021 (2 registros); 07/10/2021 | Publicado acórdão, DJE | idem |
| 11/05/2022 | Transitado(a) em julgado — "Certidão de trânsito em julgado" | idem |
| 19/05/2022 | Baixa ao arquivo do STF, Guia nº | idem |
| 01/04/2024 | Baixa ao arquivo do STF, Guia nº | idem |

### 2.4 Rcl 43007

**Dados gerais**
- Classe e número: Rcl 43007 (0101589-48.2020.1.00.0000). Processo eletrônico, público.
- URL: https://portal.stf.jus.br/processos/detalhe.asp?incidente=5990778
- Relator(a): MIN. DIAS TOFFOLI. Reclamante: LUIZ INACIO LULA DA SILVA.
- Protocolo: 27/08/2020. Andamento "Autuado" em 27/08/2020.
- Órgão julgador: não verificado.
- **Conferência de conteúdo:** Origem DF; assuntos "Garantias Constitucionais" e "Ação Penal | Provas". Os textos das decisões citam literalmente "Força Tarefa Lava Jato", o "Acordo de Leniência 5020175-34.2017.4.04.7000" e a "13ª Vara Federal Criminal da Subseção Judiciária de Curitiba/PR". Total na página: 1.716 andamentos.

| data | andamento (texto literal) | URL |
|---|---|---|
| 27/08/2020 | Autuado | detalhe.asp?incidente=5990778 |
| 16/11/2020 | Procedente — MIN. RICARDO LEWANDOWSKI: "julgo procedente o pedido para, confirmando a medida cautelar, determinar ao Juízo da 13ª Vara Federal Criminal da Subseção Judiciária de Curitiba/PR que libere…" | idem |
| 24/11/2020 (2 registros) | Embargos rejeitados | idem |
| 05/02/2021 | Improcedente — MIN. RICARDO LEWANDOWSKI (terceiros embargos de declaração) | idem |
| 15/04/2021; 19/05/2021 | Publicado acórdão, DJE | idem |
| 22/04/2021 | Embargos rejeitados | idem |
| 17/05/2021; 18/12/2021 (4 registros); 21/02/2022 | Agravo regimental não provido | idem |
| 26/01/2022 (3 registros); 31/01/2022; 24/03/2022 | Publicado acórdão, DJE | idem |
| 29/03/2023 | Embargos rejeitados | idem |
| 01/07/2023 (2 registros); 02/08/2023; 07/02/2024 (2 registros) | Baixa ao arquivo do STF, Guia nº (guias 1910, 2099, 3000, 3002) | idem |
| 06/09/2023 | Procedente — Decisão monocrática, MIN. DIAS TOFFOLI: "…concedo a extensão da ordem, em definitivo e com efeitos erga omnes, para declarar a imprestabilidade dos elementos de prova obtidos a part…" | idem |

### 2.5 Banco Master

A busca de notícias falhou (ver erros na seção 1). Usei a consulta processual **"Por Parte"** com "Banco Master". A página de resultados (https://portal.stf.jus.br/processos/listarPartes.asp) depende da sessão e não tem URL estável. **Não verifiquei se algum desses processos se relaciona ao caso de liquidação do banco.** A busca por nome de parte pode trazer processos sem relação entre si.

**Em trâmite (2)**

| Processo | Nº único | Parte | Autuação | URL |
|---|---|---|---|---|
| Rcl 97917 | 0180303-12.2026.1.00.0000 | BANCO MASTER S/A - EM LIQUIDACAO EXTRAJUDICIAL | 24/07/2026 | https://portal.stf.jus.br/processos/detalhe.asp?incidente=7653088 |
| RE 1479792 | 5034003-69.2021.4.03.6100 | BANCO MASTER S/A | 22/02/2024 | https://portal.stf.jus.br/processos/detalhe.asp?incidente=6853613 |

**Rcl 97917** — relator MIN. FLÁVIO DINO; origem RO; reclamado Tribunal de Justiça do Estado de Rondônia; assunto "Direito do Consumidor | Superendividamento".

| data | andamento (texto literal) | URL |
|---|---|---|
| 23/07/2026 | Protocolado — "Petição Inicial (nº 94174) recebida em 23/07/2026…" | detalhe.asp?incidente=7653088 |
| 24/07/2026 | Autuado | idem |
| 01/09/2026 | Negado seguimento — Decisão monocrática — MIN. FLÁVIO DINO | idem |
| 02/09/2026 | Publicação, DJE — "Divulgado em 01/09/2026" | idem |

**RE 1479792** — relator MIN. GILMAR MENDES; origem SP (TRF 3ª Região); recorrente "BANCO MASTER S/A E OUTRO(A/S)"; recorrida União; assunto tributário (IRPJ, compensação).

| data | andamento (texto literal) | URL |
|---|---|---|
| 22/02/2024 | Protocolado — "PROCESSO PROTOCOLADO VIA SISTEMA STF-TRIBUNAIS." | detalhe.asp?incidente=6853613 |
| 23/02/2024 | Autuado | idem |
| 29/02/2024 | Distribuído — Certidão, MIN. GILMAR MENDES | idem |
| 10/01/2025 | Negado seguimento — Decisão monocrática — MIN. GILMAR MENDES | idem |
| 05/02/2025 | Interposto agravo regimental — "Juntada Petição: 11480/2025" | idem |

**Fora de trâmite (9)** — listados na busca por parte; páginas não abertas.

| Processo | Nº único | Autuação |
|---|---|---|
| ARE 1620035 | 0509750-41.2024.8.04.0001 | 21/08/2026 |
| ARE 1615475 | 5077482-61.2023.4.02.5101 | 15/07/2026 |
| ARE 1612271 | 2242601-32.2025.8.26.0000 | 24/06/2026 |
| Rcl 95516 | 0175129-22.2026.1.00.0000 | 28/05/2026 |
| ARE 1570184 | 1006099-60.2023.8.26.0196 | 17/09/2025 |
| ARE 1565238 | 0436478-14.2024.8.04.0001 | 22/08/2025 |
| ARE 1533346 | 0666886-72.2022.8.04.0001 | 04/02/2025 |
| ARE 1514194 | 0807151-72.2023.8.19.0066 | 11/09/2024 |
| ARE 1450318 | 0828354-28.2022.8.19.0001 | 03/08/2023 |

## 3. Não encontrado, e onde procurei

| Item | Onde procurei | Resultado |
|---|---|---|
| Recebimento de denúncia na AP 470 | Título e texto dos 8.511 andamentos da página | Nenhuma entrada |
| Extinção e prescrição na AP 470 | Idem | 0 ocorrências |
| Trânsito em julgado ou baixa no HC 164493 | Títulos dos andamentos | Nada |
| Órgão julgador da Rcl 43007 | Cabeçalho e trechos lidos | Não verificado |
| Notícias sobre "Banco Master" | Busca "Conteúdo e Notícias" do portal | Erro do site em duas tentativas. Nenhuma outra fonte usada. |
| Termo "Lava Jato" nos HC 164493 e HC 193726 | Andamentos e aba Decisões | Ausente. Aparece só na Rcl 43007. |
| Nomes finais e tamanhos dos Anexos A e B | Página do painel antes do clique | O site não informa; conferir no navegador |
| Exportação por clique direito sobre a tabela | Não testado | Só li a dica do botão de exportação |

## 4. Pendência: documentos das abas "Peças" e "Decisões"

A listagem com nome, data e URL não foi feita. Só a aba "Decisões" da AP 470 tem cerca de 98 links de download (`downloadPeca.asp` e `downloadTexto.asp`), e as URLs têm parâmetros de consulta que minha ferramenta de leitura bloqueou. Não contornei o bloqueio. Nenhum documento foi baixado.

## 5. Desvios operacionais

- O portal abre os painéis do Corte Aberta em nova aba, então a regra de "só nesta aba" não pôde ser cumprida à letra. Fechei as abas extras ao terminar cada uso.
- O aviso de cookies do portal ficou sem resposta (não cliquei em "Estou ciente").

**Fim do relatório.**
