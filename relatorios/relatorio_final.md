# Relatório final: fatores institucionais e relações entre agentes dos Poderes, Brasil, 2003 a 2026

Gerado por código a partir da base auditável (commit 4d56720). Linguagem descritiva e a mesma para atores de qualquer partido; status formal de pessoa nunca é culpa. Resultados (seções 2 a 6) ficam separados da interpretação (seção 7). Recomenda-se revisão jurídica antes de qualquer publicação. Documentos que acompanham: `docs/nota_metodologica.md`, `docs/limitacoes.md` e `relatorios/linha_do_tempo.md`.

## 1. Escopo e limites

O estudo reúne, em forma de registro documental e de 2003 até hoje, processos, decisões e relações entre agentes dos três Poderes, de qualquer partido, em três eixos: esquemas ilícitos com trâmite formal (eixo 1), relações externas com governos de baixa qualidade democrática (eixo 2) e concentração ou abuso de poder institucional (eixo 3). A pergunta é aberta e nenhuma análise parte de hipótese sobre um espectro político. *(Fonte: `docs/protocolo.md`, seção 1; `CLAUDE.md`, seção 1)*

O estudo não atribui culpa sem decisão judicial, não trata denúncia, colaboração ou reportagem como prova, não trata ausência de evidência como indício nem como inocência, não infere motivo de coincidência de datas e não classifica governos estrangeiros por critério próprio. *(Fonte: `docs/protocolo.md`, seção 7)*

Dados pessoais: sem CPF, endereço ou dados familiares; agente privado só aparece por nome com status formal de réu ou acima. Recomenda-se revisão jurídica antes de qualquer publicação. *(Fonte: `CLAUDE.md`, seção 5)*

## 2. A base

A base tem 2.861 atores (2.798 agentes públicos e 63 agentes privados), 10.782 processos, 1.296 status formais de pessoa, 7.526 fases de processo e 1.017 buscas registradas. *(Fonte: fontes FNT-000001, FNT-000002, FNT-000003 e mais 129)*

Processos por classe: Petição: 4.817; Ação penal: 2.633; Inquérito: 2.623; Representação por quebra de decoro parlamentar (Conselho de Ética): 445; Processo de contas do Tribunal de Contas da União: 256; Registro de candidatura (Justiça Eleitoral): 4; Habeas corpus: 2; Reclamação: 2. *(Fonte: `data/base/processos.csv`)*

Status formais por tipo: representado: 481; arquivado: 297; contas julgadas irregulares: 262; absolvido: 74; condenado por tribunal superior: 45; réu: 40; prescrição reconhecida: 30; punibilidade extinta: 15; representação improcedente: 14; condenado em primeira instância: 10; mandato cassado: 8; sanção disciplinar: 5; candidatura indeferida ou cassada: 4; investigado: 4; condenado em segunda instância: 3; condenação anulada: 2; processo anulado: 1; denúncia rejeitada: 1. *(Fonte: `data/base/status_pessoa_processo.csv`)*

## 3. Eixo 1: esquemas ilícitos com trâmite formal

### 3.1 Ações penais originárias no STF

Nas legislaturas 52 a 55, 125 de 2.890 parlamentares-legislatura (4,3%) foram réus em ação penal do STF com assunto do eixo 1, e 14 tiveram ação com condenação no mérito. *(Fonte: `relatorios/tabelas/simetria_taxa_bancada.csv`; fontes FNT-000046, FNT-000047, FNT-000231 e mais 1; D-048, D-049)*

Entre os 9 partidos com bancada de 100 ou mais parlamentares-legislatura, a taxa de réus vai de 2,3% (PSB) a 7,1% (PTB); em 36 de 36 pares os intervalos de 95% se sobrepõem. *(Fonte: `relatorios/tabelas/simetria_taxa_bancada.csv`; D-049)*

Antes da restrição do foro (2003-2019), a taxa de parlamentares-ano réus é 1,16% na base do governo e 1,09% na oposição. *(Fonte: `relatorios/tabelas/simetria_taxa_governo_oposicao.csv`; D-050, D-051)*

Desfechos registrados por pessoa: 137 status lidos no texto oficial das decisões do STF (absolvido: 64; prescrição reconhecida: 30; condenado por tribunal superior: 27; punibilidade extinta: 15; denúncia rejeitada: 1); os de mérito são 91, e os demais encerram a ação sem julgar o mérito (prescrição, extinção da punibilidade, rejeição da denúncia). *(Fonte: `relatorios/tabelas/stf_desfechos.csv`; fontes FNT-000046, FNT-000256, FNT-000258 e mais 31; D-065, D-066)*

Das 90 ações julgadas no mérito com réu parlamentar, 90 têm o desfecho registrado na pessoa (93 parlamentares x ação). *(Fonte: `relatorios/tabelas/stf_desfechos_cobertura.csv`; D-065)*

Entre os parlamentares julgados no mérito, 31,2% foram condenados; a proporção não se distingue entre os 7 partidos com 5 ou mais julgados (p = 0,761) nem entre base do governo e oposição (p = 1,000). *(Fonte: `relatorios/tabelas/stf_desfechos_taxas.csv`; `relatorios/tabelas/stf_desfechos_homogeneidade.csv`; D-065)*

### 3.2 Conselhos de Ética da Câmara e do Senado

Há 481 vínculos entre representação por quebra de decoro e parlamentar, em 445 processos de 2003 a 2026; 157 vínculos não têm desfecho nos campos estruturados das fontes. *(Fonte: `relatorios/tabelas/etica_desfechos.csv`; fontes FNT-000306, FNT-000307, FNT-000308; D-063)*

Desfechos registrados: arquivado: 297; representação improcedente: 14; mandato cassado: 8; sanção disciplinar: 5. *(Fonte: `relatorios/tabelas/etica_desfechos.csv`; D-063)*

Entre os partidos com 30 ou mais parlamentares-legislatura, a parcela de parlamentares alvo de representação vai de 0,0% (PV) a 47,6% (PSOL, 20 de 42); as taxas diferem entre partidos (p < 0,001, sem a 52ª legislatura) e não se correlacionam com a posição ideológica (|rho| de 0,02 a 0,15; menor p = 0,598). *(Fonte: `relatorios/tabelas/etica_taxas.csv`; `relatorios/tabelas/etica_homogeneidade.csv`; `relatorios/tabelas/etica_correlacao.csv`; D-063, D-062)*

No período inteiro, a parcela de parlamentares-ano alvo de representação é 1,9% na base do governo e 2,2% na oposição (p = 0,272); 3 de 5 períodos presidenciais têm diferença significativa, com sentido diferente entre eles (Lula 1 e 2: maior na base do governo; Temer (e Dilma até 11/05/2016): maior na oposição; Lula 3: maior na oposição). *(Fonte: `relatorios/tabelas/etica_governo_periodo.csv`; D-063, D-050)*

Mandato cassado ou sanção disciplinar aprovada: 13 vínculos, número pequeno demais para distinguir partidos (p = 0,713). *(Fonte: `relatorios/tabelas/etica_homogeneidade.csv`; D-063)*

### 3.3 Contas julgadas irregulares (TCU) e candidaturas indeferidas (TSE)

A base registra 262 status de contas julgadas irregulares (trânsito em julgado de 2003 em diante) em 84 atores e 4 de candidatura indeferida por motivo do eixo 1 (2018 e 2022) em 4 atores; a ligação entre lista pública e ator usa o CPF e o nome civil da candidatura, e o CPF não entra na base. *(Fonte: `relatorios/tabelas/eixo1_registros.csv`; fontes FNT-000071, FNT-000072, FNT-000073 e mais 6; D-064)*

A ligação cobre 96,8% das unidades parlamentar-legislatura. *(Fonte: `relatorios/tabelas/eixo1_parlamentares_cobertura.csv`; D-064)*

Entre os parlamentares com candidatura ligada, a parcela com contas irregulares já transitadas até o fim da legislatura não difere entre partidos (p = 0,427), não se correlaciona com o escore ideológico (|rho| de 0,01 a 0,12) e é 0,75% na base do governo e 0,86% na oposição (p = 0,556). *(Fonte: `relatorios/tabelas/eixo1_parlamentares_homogeneidade.csv`; `relatorios/tabelas/eixo1_parlamentares_correlacao.csv`; `relatorios/tabelas/eixo1_parlamentares_governo_periodo.csv`; D-064)*

No universo dos candidatos eleitos de 2010 a 2022, a parcela com contas irregulares até a eleição é 1,11% entre partidos da base do governo e 1,66% na oposição, com intervalos de 95% que se sobrepõem; a diferença entre partidos dessa parcela tem p = 0,421 e a de candidaturas indeferidas por motivo do eixo 1, p = 0,020, com apenas 4 candidaturas indeferidas entre 3.496 eleitos. *(Fonte: `relatorios/tabelas/eixo1_taxas.csv`; `relatorios/tabelas/eixo1_homogeneidade.csv`; D-060, D-061)*

No universo de todos os candidatos às eleições gerais de 2010 a 2022, a parcela com contas irregulares até a eleição difere entre partidos (p < 0,001) e a de candidaturas indeferidas por motivo do eixo 1 também (p < 0,001); entre os partidos com 200 ou mais candidatos, as maiores parcelas de contas irregulares são MDB 1,29% (67 de 5.213); PT 1,08% (56 de 5.200); PP 1,07% (41 de 3.832) e as de candidaturas indeferidas, AGIR 2,16% (39 de 1.809); DC 1,62% (26 de 1.601); UNIÃO 1,23% (19 de 1.546). Essas taxas dependem também do número e do perfil dos candidatos de cada partido e não medem a conduta do partido; em 2022, a cassação por fraude à cota de gênero atinge a lista inteira e é tratada à parte em D-061. *(Fonte: `relatorios/tabelas/eixo1_taxas.csv`; `relatorios/tabelas/eixo1_homogeneidade.csv`; D-060, D-061)*

### 3.4 Posição ideológica dos partidos

Das 10 correlações entre o escore ideológico e as taxas por partido (STF, TCU e TSE), 0 têm p abaixo de 0,05; a de menor p (TSE, tse_indeferimento, candidatos) tem rho = 0,32 (p = 0,057). *(Fonte: `relatorios/tabelas/ideologia_correlacao.csv`; fontes FNT-000305; D-062)*

### 3.5 Contraste com a imprensa

Para 12 fatos oficiais já na base, buscou-se cobertura em 10 veículos (busca em ferramenta de pesquisa): em 71 de 120 buscas havia matéria que concorda com o fato oficial, em 1 matéria que diverge, em 4 menção sem o resultado e em 44 nenhum resultado; "sem resultado" mede também a ferramenta de busca. *(Fonte: `relatorios/tabelas/imprensa_contraste_por_veiculo.csv`; `relatorios/tabelas/imprensa_contraste_por_fato.csv`; D-055, D-056)*

Os fatos F08, F09, F11 têm matéria em todos os veículos em uso; F04 (Lava Jato / 5026212) e F03 (AP 536 / TJMG) têm matéria em 1 e 1 dos 10 veículos. *(Fonte: `relatorios/tabelas/imprensa_contraste_por_fato.csv`; D-055)*

Uma segunda coleta, no navegador, registrou 26 buscas com matéria concordante, 0 divergente e 23 sem resultado em 4 veículos; as coletas divergem entre si para a Folha em vários fatos, o que mostra o efeito da ferramenta. *(Fonte: `relatorios/tabelas/imprensa_navegador_por_veiculo.csv`; `relatorios/tabelas/imprensa_navegador_folha_por_coleta.csv`; D-056)*

## 4. Eixo 2: relações externas e qualidade democrática

Um país é de baixa qualidade democrática (BQD) quando é Não Livre na Freedom House ou autocracia (fechada ou eleitoral) no V-Dem Regimes of the World, no ano do fato; as duas réguas são apresentadas lado a lado e não são combinadas. *(Fonte: fontes FNT-000008, FNT-000009, FNT-000010; D-053)*

### 4.1 Votos em resoluções de escrutínio sobre países (ONU e OEA)

Em resoluções de escrutínio cujo alvo é BQD pela Freedom House, a parcela de votos favoráveis do Brasil vai de 14,3% (Luiz Inácio Lula da Silva (2023-)) a 78,3% (Dilma Rousseff (2011-2014)); a média de democracias nas mesmas resoluções vai de 71,7% a 87,7%. *(Fonte: `relatorios/tabelas/eixo2_votos_por_governo.csv`; `relatorios/tabelas/eixo2_votos_por_resolucao.csv`; fontes FNT-000019, FNT-000020, FNT-000021 e mais 172; D-053)*

| Governo | Resoluções | Brasil, parcela de sim | Democracias, média de sim | América Latina, média de sim |
|---|---|---|---|---|
| Luiz Inácio Lula da Silva (2003-2006) | 15 | 53,3% | 71,7% | 53,0% |
| Luiz Inácio Lula da Silva (2007-2010) | 18 | 44,4% | 78,3% | 47,9% |
| Dilma Rousseff (2011-2014) | 23 | 78,3% | 87,7% | 62,9% |
| Dilma Rousseff (2015-2016) | 5 | 60,0% | 82,9% | 57,8% |
| Michel Temer (2016-2018) | 25 | 66,7% | 78,1% | 53,0% |
| Jair Messias Bolsonaro (2019-2022) | 70 | 72,9% | 85,9% | 62,9% |
| Luiz Inácio Lula da Silva (2023-) | 16 | 14,3% | 84,7% | 69,9% |

Régua V-Dem (mesmas resoluções, alvo BQD pelo V-Dem):

| Governo | Resoluções | Brasil, parcela de sim | Democracias, média de sim | América Latina, média de sim |
|---|---|---|---|---|
| Luiz Inácio Lula da Silva (2003-2006) | 15 | 53,3% | 71,7% | 53,0% |
| Luiz Inácio Lula da Silva (2007-2010) | 18 | 44,4% | 78,3% | 47,9% |
| Dilma Rousseff (2011-2014) | 23 | 78,3% | 87,7% | 62,9% |
| Dilma Rousseff (2015-2016) | 5 | 60,0% | 82,9% | 57,8% |
| Michel Temer (2016-2018) | 30 | 72,4% | 79,3% | 57,5% |
| Jair Messias Bolsonaro (2019-2022) | 70 | 72,9% | 85,9% | 62,9% |
| Luiz Inácio Lula da Silva (2023-) | 26 | 29,2% | 84,7% | 68,0% |

### 4.2 Apoio à exportação (BNDES)

A parcela das operações de apoio à exportação do BNDES com destino BQD pela Freedom House vai de 0,9% a 19,8% entre os governos; a parcela do valor de serviços de engenharia com destino BQD só existe nos governos com esse tipo de operação (Luiz Inácio Lula da Silva (2003-2006), Luiz Inácio Lula da Silva (2007-2010), Dilma Rousseff (2011-2014), Dilma Rousseff (2015-2016)) e chega a 36,8% em Luiz Inácio Lula da Silva (2007-2010). *(Fonte: `relatorios/tabelas/eixo2_bndes_por_governo.csv`; fontes FNT-000011, FNT-000012; D-053)*

| Governo | Operações | Parcela BQD (FH) | Parcela BQD (V-Dem) |
|---|---|---|---|
| Luiz Inácio Lula da Silva (2003-2006) | 259 | 4,7% | 6,1% |
| Luiz Inácio Lula da Silva (2007-2010) | 444 | 19,8% | 21,2% |
| Dilma Rousseff (2011-2014) | 660 | 12,6% | 14,0% |
| Dilma Rousseff (2015-2016) | 70 | 4,3% | 7,1% |
| Michel Temer (2016-2018) | 357 | 1,7% | 1,7% |
| Jair Messias Bolsonaro (2019-2022) | 459 | 0,9% | 1,5% |
| Luiz Inácio Lula da Silva (2023-) | 566 | 3,0% | 3,1% |

### 4.3 Comércio exterior (exportações, ComexStat)

A parcela das exportações brasileiras com destino BQD pela Freedom House vai de 14,2% a 40,1% entre os governos, com a China como primeiro destino BQD em todos os governos (China, 29,6% das exportações no governo mais recente). A parcela de exportações para países sem classificação na Freedom House é 47,3% no governo mais recente, contra no máximo 3,8% nos anteriores, o que limita a comparação desse governo. *(Fonte: `relatorios/tabelas/eixo2_comercio_por_governo.csv`; D-054)*

| Governo | Meses | Parcela BQD (FH) | Parcela BQD (V-Dem) | Sem classificação (FH) |
|---|---|---|---|---|
| Luiz Inácio Lula da Silva (2003-2006) | 48 | 14,2% | 20,9% | 3,2% |
| Luiz Inácio Lula da Silva (2007-2010) | 48 | 21,2% | 29,7% | 3,8% |
| Dilma Rousseff (2011-2014) | 48 | 28,3% | 36,1% | 3,8% |
| Dilma Rousseff (2015-2016) | 16 | 31,1% | 37,8% | 2,9% |
| Michel Temer (2016-2018) | 32 | 35,1% | 41,9% | 2,5% |
| Jair Messias Bolsonaro (2019-2022) | 48 | 40,0% | 48,6% | 1,0% |
| Luiz Inácio Lula da Silva (2023-) | 44 | 40,1% | 50,0% | 47,3% |

### 4.4 Atos bilaterais (Itamaraty)

Nos atos bilaterais registrados, a parcela com país BQD pela Freedom House vai de 12,1% (Dilma Rousseff (2015-2016)) a 25,8% (Luiz Inácio Lula da Silva (2023-)); a parcela de países BQD no mundo no mesmo período vai de 23,2% a 29,5%. *(Fonte: `relatorios/tabelas/eixo2_acordos_por_governo.csv`; fontes FNT-000069, FNT-000070; D-053)*

### 4.5 Redes partidárias transnacionais

Foram registradas 20 participações de partidos brasileiros em 8 redes partidárias transnacionais de várias orientações (por exemplo, Foro de São Paulo: 7 partido(s); Conferência Permanente de Partidos Políticos da América Latina e do Caribe: 3 partido(s); Aliança Progressista: 2 partido(s)); participação em rede é relação, não indício de ilícito. *(Fonte: `relatorios/tabelas/eixo2_redes_partidarias.csv`; fontes FNT-000048, FNT-000049, FNT-000050 e mais 18; D-053)*

## 5. Eixo 3: poder institucional

Entraram as partes que os dados em mãos permitem calcular. Ficam fora a nomeação para cargo com foro durante status de investigado ou denunciado (a base não tem cargos de ministro de Estado) e a decisão monocrática de alto impacto (a exportação do Corte Aberta cobre só ação penal, inquérito e petição penal); a tabela `decisoes_judiciais` está vazia. *(Fonte: D-067)*

### 5.1 Relator e presidente que indicou

Dos 93 julgamentos de parlamentares no mérito, 29,2% (19 de 65) dos decididos por ministro indicado por presidente do PT terminaram em condenação, contra 35,7% (10 de 28) dos decididos por ministro indicado por outro presidente (p = 0,627). *(Fonte: `relatorios/tabelas/eixo3_relator_2x2.csv`; `relatorios/tabelas/eixo3_relator_ministros.csv`; `relatorios/tabelas/eixo3_relator_presidentes.csv`; fontes FNT-000046; D-067, D-065)*

### 5.2 Uso do foro

Em 386 pares ação penal x réu parlamentar com vínculo confirmado, 143 têm decisão de declínio de competência, 50 delas com o réu ainda em mandato na data. A parcela com declínio é 35,0% entre réus de partidos da base do governo e 52,3% entre os da oposição (p = 0,011) e difere entre partidos (p = 0,001); dentro de cada um dos 4 períodos presidenciais com os dois grupos a taxa é maior na oposição em 4, sem diferença significativa em nenhum período isolado. *(Fonte: `relatorios/tabelas/eixo3_foro_taxas.csv`; `relatorios/tabelas/eixo3_foro_testes.csv`; `relatorios/tabelas/eixo3_foro_governo_periodo.csv`; D-067)*

## 6. Simetria

Dos 331 status de atores com filiação que exigem verificação de simetria (denúncia, réu, condenação, candidatura indeferida, contas irregulares, cassação e sanção), 331 têm a verificação registrada; as 465 verificações têm 10.952 resultados por partido, governo ou oposição: encontrado: 6.467; sem_evidencia: 3.771; nao_verificado: 714. `sem_evidencia` só existe com busca registrada de zero resultados; `nao_verificado` indica grupo sem universo lido ou sem busca. *(Fonte: fontes FNT-000001, FNT-000002, FNT-000003 e mais 113; D-007, D-048, D-065)* *(Fonte: `data/base/verificacoes_simetria.csv`, `data/base/verificacao_resultado.csv`)*

## 7. Interpretação (separada dos resultados)

Esta seção lê os resultados acima; não produz registro novo e pode ser lida separadamente. Cada leitura indica de onde vem.

1. **Muitos testes, poucos casos.** As tabelas trazem 119 testes (homogeneidade, correlação, Fisher), dos quais 35 (29,4%) têm p abaixo de 0,05; ao acaso, sem correção, se esperariam cerca de 5,0%. Os testes não são independentes (os mesmos partidos entram em recortes vizinhos). A maior parte vem das comparações entre partidos no universo de todos os candidatos (seção 3.3), com dezenas de milhares de candidaturas, em que o teste detecta diferenças pequenas de taxa e a composição de candidatos de cada partido pesa; esses testes descrevem que as taxas diferem, não por quê. Distribuição dos com p < 0,05 por tabela: eixo1_homogeneidade (20 de 32); eixo1_parlamentares_governo_periodo (1 de 12); eixo3_foro_testes (8 de 12); etica_governo_periodo (3 de 12); etica_homogeneidade (3 de 6). Diferenças isoladas não sustentam conclusão; importam as que se repetem em recortes diferentes.

2. **Posição ideológica.** Nas 20 correlações entre o escore ideológico do partido e uma taxa (STF, ética, TCU, TSE), 0 têm p abaixo de 0,05. Com o número de partidos disponível (15 a 35), o teste só distinguiria associações fortes; o resultado diz que nenhuma associação forte aparece, não que não exista nenhuma.

3. **Onde há diferença entre partidos, ela se concentra.** A diferença entre partidos na parcela alvo de representação nos Conselhos de Ética vem de poucos casos: o PSOL, com poucos parlamentares e muitas representações, e o antigo PL e o PRONA na 52ª legislatura (episódio das ambulâncias, 2005-2006), conforme a sensibilidade sem a 52ª legislatura em D-063. A diferença no declínio de competência tem o mesmo sentido (maior na oposição) em 4 dos 4 períodos presidenciais com os dois grupos, mas nenhum período isolado a confirma; a medida não distingue o motivo do declínio.

4. **Governo e oposição.** Na ética, dos períodos presidenciais com diferença significativa na parcela alvo de representação, 3 têm sentidos diferentes (Lula 1 e 2: maior na base do governo; Temer (e Dilma até 11/05/2016): maior na oposição; Lula 3: maior na oposição), o que não indica padrão estável. No STF, a proporção de condenados entre julgados no mérito não difere entre base do governo e oposição (p = 1,000), nem as contas irregulares do TCU (p = 0,556).

5. **Desfechos de processo.** Entre os parlamentares julgados no mérito no STF, a proporção de condenados não difere entre partidos (p = 0,761) nem entre relatores indicados por presidentes do PT e de outros partidos (p = 0,627); com dezenas de julgamentos por recorte, o teste não tem poder para diferenças moderadas.

6. **Eixo 2.** As parcelas de votos, operações de crédito, exportações e atos bilaterais com países BQD variam entre governos, em sentidos diferentes conforme o indicador e a régua (Freedom House ou V-Dem). A parcela de exportações para países BQD cresce a cada governo (14,2% a 40,1%), enquanto a parcela das exportações para a China passa de 6,1% a 29,6% no mesmo intervalo; o estudo não atribui essa variação a decisão de governo.

7. **O que os dados não sustentam.** Não há, nestes dados, base para afirmar que um partido, espectro ou governo concentre esquemas ilícitos, apoio a países BQD ou abuso de poder institucional. Também não sustentam o contrário: as coberturas são parciais (por exemplo, inquéritos sem lista de réus, primeira instância e tribunais estaduais sem universo lido, sanções administrativas só de pessoas jurídicas) e ausência de registro não é evidência de ausência. As limitações completas estão em `docs/limitacoes.md`.

## 8. Limitações

As limitações conhecidas (vieses) e a cobertura medida na base estão em `docs/limitacoes.md`, que acompanha este relatório. Seções da parte gerada: Fontes judiciais; Esforço investigativo e cobertura; Dados administrativos; Réguas externas; Desenho do projeto; Registros por tabela; Buscas; Lacunas medidas na etapa E1 (Câmara e Senado); Réguas externas (etapa E2); BNDES, operações de exportação (etapa E3); STF pelo Corte Aberta (etapa E5); Portal da Transparência (etapa E6); Votos em organismos multilaterais (etapa E8, bloco A); Redes partidárias transnacionais (etapa E8, bloco D); Atos bilaterais do Brasil (etapa E8, bloco B); TSE: candidatos e receitas de campanha (etapa E7); Casos-teste (etapa E9); Verificação de simetria dos status da E9; Eixo 2: métricas por governo (D-053); Contraste com a imprensa (D-055, D-056); Eixo 1 ampliado: candidatos, TSE e TCU (D-060, D-061); Posição ideológica dos partidos (D-062); Conselhos de Ética (D-063); Registros individuais do TCU e do TSE (D-064); Desfechos das ações penais do STF por pessoa (D-065); Eixo 3: relator x presidente que indicou e uso do foro (D-067); Composição do STF (D-058); Validador.

## 9. Reprodução

Este relatório é gerado por `python -m src.relatorios.relatorio_final` a partir de `data/base` e de `relatorios/tabelas` (commit 4d56720). A ordem completa de geração está em `docs/nota_metodologica.md`, seção 7. Os números mudam se a base mudar; o commit identifica a versão.

## Apêndice A. Fontes citadas

| Id | Tipo | Título | Data de acesso | URL | sha256 (início) |
|---|---|---|---|---|---|
| FNT-000001 | oficial | Câmara dos Deputados, API de dados abertos v2: legislaturas | 2026-09-24 | https://dadosabertos.camara.leg.br/api/v2/legislaturas | 57b9c8f9760f |
| FNT-000002 | oficial | Câmara dos Deputados, API de dados abertos v2: deputados por legislatura | 2026-09-24 | https://dadosabertos.camara.leg.br/api/v2/deputados | 43927fb017dd |
| FNT-000003 | oficial | Câmara dos Deputados, API de dados abertos v2: histórico de partido e situação dos deputados | 2026-09-24 | https://dadosabertos.camara.leg.br/api/v2/deputados/{id}/historico | 531f2b277443 |
| FNT-000004 | oficial | Câmara dos Deputados, API de dados abertos v2: partidos | 2026-09-24 | https://dadosabertos.camara.leg.br/api/v2/partidos/{id} | 2835501674d1 |
| FNT-000005 | oficial | Senado Federal, dados abertos: senadores e mandatos por legislatura | 2026-09-24 | https://legis.senado.leg.br/dadosabertos/senador/lista/legislatura/{n}.json | cd75033610dc |
| FNT-000006 | oficial | Senado Federal, dados abertos: filiações partidárias dos senadores | 2026-09-24 | https://legis.senado.leg.br/dadosabertos/senador/{codigo}/filiacoes.json | 385d65c7339e |
| FNT-000007 | oficial | Tribunal Superior Eleitoral: partidos registrados; fusões, incorporações e mudanças de nome ou sigla | 2026-09-24 | https://www.tse.jus.br/partidos/partidos-registrados-no-tse | fda61af5901f |
| FNT-000008 | base_de_dados | V-Dem Country-Year Full+Others, versão 16 (pacote vdemdata) | 2026-09-24 | https://raw.githubusercontent.com/vdeminstitute/vdemdata/V16/data/vdem.RData | 39b412d39a06 |
| FNT-000009 | base_de_dados | Freedom in the World: Country and Territory Ratings and Statuses, 1973-2024 | 2026-09-24 | https://freedomhouse.org/sites/default/files/2025-02/Country_and_Territory_Ratings_and_Statuses_FIW_1973-2024. | b17283b2b9e9 |
| FNT-000010 | base_de_dados | Freedom in the World 2013-2025 Raw Data | 2026-09-24 | https://freedomhouse.org/sites/default/files/2025-02/All_data_FIW_2013-2024.xlsx | 3dfa43b074ba |
| FNT-000011 | oficial | BNDES, dados abertos: operações de exportação (pós-embarque, serviços de engenharia) | 2026-09-24 | https://dadosabertos.bndes.gov.br/dataset/f27e48cd-653b-4bfa-bc4f-08b637793873/resource/d158033b-f6cb-4609-971 | 65e21b61bb5c |
| FNT-000012 | oficial | BNDES, dados abertos: operações de exportação (pós-embarque, bens) | 2026-09-24 | https://dadosabertos.bndes.gov.br/dataset/f27e48cd-653b-4bfa-bc4f-08b637793873/resource/0cfe4594-44bf-48a8-a79 | 07173999a0f9 |
| FNT-000019 | oficial | OEA, Assembleia Geral, sessão XLIX-O (2019): Actas y Documentos, volume I (declarações e resoluções aprovadas) | 2026-09-24 | http://scm.oas.org/doc_public/SPANISH/HIST_19/AG07996S03.doc | 28cd2343a1a8 |
| FNT-000020 | oficial | OEA, Assembleia Geral, sessão XLIX-O (2019): Atas textuais das sessões plenárias | 2026-09-24 | http://scm.oas.org/pdfs/2020/AC03409T03.docx | 43e49d5f27f2 |
| FNT-000021 | oficial | OEA, Assembleia Geral, sessão XXXIV-O (2004): Actas y Documentos, volume I (declarações e resoluções aprovadas) | 2026-09-24 | http://scm.oas.org/doc_public/SPANISH/HIST_04/AG02528S08.doc | 9eca6e3f1ca3 |
| FNT-000022 | oficial | OEA, Assembleia Geral, sessão XXXIV-O (2004): Atas textuais das sessões plenárias | 2026-09-24 | http://www.oas.org/consejo/GENERAL%20ASSEMBLY/Documents/34.pdf | bd0c3652c924 |
| FNT-000023 | oficial | OEA, Assembleia Geral, sessão XLVIII-O (2018): Actas y Documentos, volume I (declarações e resoluções aprovadas) | 2026-09-24 | http://scm.oas.org/doc_public/SPANISH/HIST_18/AG07745S03.doc | 706ada7aad11 |
| FNT-000024 | oficial | OEA, Assembleia Geral, sessão XLVIII-O (2018): Atas textuais das sessões plenárias | 2026-09-24 | http://scm.oas.org/pdfs/2020/AC03395T03.docx | e1bc0ca70e52 |
| FNT-000025 | oficial | OEA, Assembleia Geral, sessão XLVI-O (2016): Atas textuais das sessões plenárias | 2026-09-24 | http://scm.oas.org/doc_public/SPANISH/HIST_17/AC03216T03.doc | 503368077b16 |
| FNT-000026 | oficial | OEA, Assembleia Geral, sessão LII-O (2022): Atas textuais das sessões plenárias | 2026-09-24 | http://scm.oas.org/doc_public/SPANISH/HIST_23/AG08710T03.docx | a1f3afcd0b62 |
| FNT-000027 | oficial | OEA, Assembleia Geral, sessão LI-O (2021): Actas y Documentos, volume I (declarações e resoluções aprovadas) | 2026-09-24 | http://scm.oas.org/doc_public/SPANISH/HIST_21/AG08489S07.docx | cc40ff257249 |
| FNT-000028 | oficial | OEA, Assembleia Geral, sessão LI-O (2021): Atas textuais das sessões plenárias | 2026-09-24 | http://scm.oas.org/doc_public/SPANISH/HIST_22/AC03908T03.docx | 185c2d741170 |
| FNT-000029 | oficial | OEA, Assembleia Geral, sessão LII-O (2022): Actas y Documentos, volume I (declarações e resoluções aprovadas) | 2026-09-24 | http://scm.oas.org/doc_public/SPANISH/HIST_23/AG08750S08.docx | 3d127fd0b0c2 |
| FNT-000030 | oficial | OEA, Assembleia Geral, sessão L-O (2020): Atas textuais das sessões plenárias | 2026-09-24 | http://scm.oas.org/doc_public/SPANISH/HIST_21/AC03697T03.DOC | 1bc0b4c58309 |
| FNT-000031 | oficial | OEA, Assembleia Geral, sessão LIII-O (2023): Actas y Documentos, volume I (declarações e resoluções aprovadas) | 2026-09-24 | http://scm.oas.org/doc_public/SPANISH/HIST_24/AG08923S12.docx | e090e6793623 |
| FNT-000032 | oficial | OEA, Assembleia Geral, sessão LIII-O (2023): Atas textuais das sessões plenárias | 2026-09-24 | http://scm.oas.org/doc_public/SPANISH/HIST_24/AC04029T03.docx | ebcbac53b028 |
| FNT-000033 | oficial | OEA, Assembleia Geral, sessão LIV-O (2024): Actas y Documentos, volume I (declarações e resoluções aprovadas) | 2026-09-24 | http://scm.oas.org/doc_public/SPANISH/HIST_25/AG09324S06.docx | 604722681e4b |
| FNT-000034 | oficial | OEA, Assembleia Geral, sessão LIV-O (2024): Atas textuais das sessões plenárias | 2026-09-24 | http://scm.oas.org/doc_public/SPANISH/HIST_24/AC04047T05.docx | f2f94c37225c |
| FNT-000035 | oficial | OEA, Assembleia Geral, sessão XLI-O (2011): Actas y Documentos, volume I (declarações e resoluções aprovadas) | 2026-09-24 | http://www.oas.org/consejo/sp/AG/Documentos/AG05485S05.doc | c0cf356287da |
| FNT-000036 | oficial | OEA, Assembleia Geral, sessão XLI-O (2011): Atas textuais das sessões plenárias | 2026-09-24 | http://www.oas.org/consejo/GENERAL%20ASSEMBLY/Documents/AC01733T04.DOC | e5f7c73b13c5 |
| FNT-000037 | oficial | OEA, Assembleia Geral, sessão XLVI-O (2016): Actas y Documentos, volume I (declarações e resoluções aprovadas) | 2026-09-24 | http://scm.oas.org/doc_public/SPANISH/HIST_17/AG07239S03.doc | 52dce0ad5479 |
| FNT-000038 | oficial | OEA, Assembleia Geral, sessão XXXVII-E (2009): Actas y Documentos, volume I (declarações e resoluções aprovadas) | 2026-09-24 | http://www.oas.org/consejo/sp/AG/Documentos/AG04665S04.doc | 26d652c6890a |
| FNT-000039 | oficial | OEA, Assembleia Geral, sessão XXXVII-E (2009): Atas textuais das sessões plenárias | 2026-09-24 | http://www.oas.org/consejo/sp/AG/Documentos/ac01419t04.doc | f9d309053ce8 |
| FNT-000040 | oficial | OEA, Assembleia Geral, sessão XXXVIII-O (2008): Actas y Documentos, volume I (declarações e resoluções aprovadas) | 2026-09-24 | http://www.oas.org/consejo/GENERAL%20ASSEMBLY/Documents/ag04269s07.doc | 4b205a84befe |
| FNT-000041 | oficial | OEA, Assembleia Geral, sessão XXXVIII-O (2008): Atas textuais das sessões plenárias | 2026-09-24 | http://www.oas.org/consejo/GENERAL%20ASSEMBLY/Documents/ac01221t04.doc | b9e17b39856c |
| FNT-000042 | oficial | OEA, Assembleia Geral, sessão XXXIX-O (2009): Actas y Documentos, volume I (declarações e resoluções aprovadas) | 2026-09-24 | http://www.oas.org/consejo/GENERAL%20ASSEMBLY/Documents/AG04688S10.doc | 3663aa577786 |
| FNT-000043 | oficial | OEA, Assembleia Geral, sessão XXXIX-O (2009): Atas textuais das sessões plenárias | 2026-09-24 | http://www.oas.org/consejo/GENERAL%20ASSEMBLY/Documents/AC01413T04.DOC | 41f8481b273a |
| FNT-000044 | oficial | OEA, Assembleia Geral, sessão XL-O (2010): Actas y Documentos, volume I (declarações e resoluções aprovadas) | 2026-09-24 | http://www.oas.org/consejo/sp/AG/Documentos/AG05138S09.doc | 5e482c4b9034 |
| FNT-000045 | oficial | OEA, Assembleia Geral, sessão XL-O (2010): Atas textuais das sessões plenárias | 2026-09-24 | http://www.oas.org/consejo/GENERAL%20ASSEMBLY/Documents/AC01645T04.DOC | a5f00ba24b04 |
| FNT-000046 | oficial | STF, Corte Aberta: decisões em ações penais e inquéritos, 08/01/2003 a 23/09/2026 (exportação do painel) | 2026-09-24 | https://transparencia.stf.jus.br/extensions/decisoes/decisoes.html | 8298383015ad |
| FNT-000047 | oficial | STF, Corte Aberta: acervo de ações penais e inquéritos em tramitação (exportação do painel) | 2026-09-24 | https://transparencia.stf.jus.br/extensions/acervo/acervo.html | e9771ecbe267 |
| FNT-000048 | oficial | Aliança Progressista: página de membros, cópia de 2014-12-10 no Internet Archive | 2026-09-24 | http://progressive-alliance.info/participants/ | a9c971b0096e |
| FNT-000049 | oficial | Aliança Progressista: página de membros, cópia de 2026-07-22 no Internet Archive | 2026-09-24 | https://progressive-alliance.info/network/ | 62aefe29b4bd |
| FNT-000050 | oficial | Aliança Progressista: página de membros, cópia de 2024-03-04 no Internet Archive | 2026-09-24 | http://progressive-alliance.info/network/parties-and-organisations/ | 2b48abe4c303 |
| FNT-000051 | oficial | Conferência Permanente de Partidos Políticos da América Latina e do Caribe: página de membros, cópia de 2003-06-27 no Internet Archive | 2026-09-24 | http://www.copppal.org.mx:80/partidosintegrantes.html | 6b3ab49964f9 |
| FNT-000052 | oficial | Conferência Permanente de Partidos Políticos da América Latina e do Caribe: página de membros, cópia de 2026-07-10 no Internet Archive | 2026-09-24 | https://www.copppal.org/partidos-miembros/ | 96b5c9bc4278 |
| FNT-000053 | oficial | Foro de São Paulo: página de membros, cópia de 2014-08-23 no Internet Archive | 2026-09-24 | http://forodesaopaulo.org:80/partidos/ | c837c6c7b680 |
| FNT-000054 | oficial | Foro de São Paulo: página de membros, cópia de 2024-07-15 no Internet Archive | 2026-09-24 | https://forodesaopaulo.org/partidos/ | 2bbc9e9b1285 |
| FNT-000055 | oficial | Foro de São Paulo: página de membros, cópia de 2019-08-26 no Internet Archive | 2026-09-24 | https://forodesaopaulo.org/partidos/ | 196eca4b6045 |
| FNT-000056 | oficial | Internacional Democrata Centrista: página de membros, cópia de 2003-06-29 no Internet Archive | 2026-09-24 | http://www.idc-cdi.org:80/parties/miembros_idc/Brasil_PSDB.asp | 58745fa0d07f |
| FNT-000057 | oficial | Internacional Democrata Centrista: página de membros, cópia de 2013-07-14 no Internet Archive | 2026-09-24 | http://www.idc-cdi.com:80/partidos.php | c95125b51a4b |
| FNT-000058 | oficial | Internacional Democrata Centrista: página de membros, cópia de 2003-07-02 no Internet Archive | 2026-09-24 | http://idc-cdi.org:80/parties/miembros_idc/Brasil_PFL.asp | 5c2c0d1284c8 |
| FNT-000059 | oficial | International Democrat Union: página de membros, cópia de 2018-06-12 no Internet Archive | 2026-09-24 | https://www.idu.org/members/ | 39bc6644d1d0 |
| FNT-000060 | oficial | International Democrat Union: página de membros, cópia de 2023-07-08 no Internet Archive | 2026-09-24 | https://www.idu.org/members/ | 72c9e44f1723 |
| FNT-000061 | oficial | International Democrat Union: página de membros, cópia de 2024-07-11 no Internet Archive | 2026-09-24 | https://www.idu.org/members/ | 51c79ffdd9a7 |
| FNT-000062 | oficial | International Democrat Union: página de membros, cópia de 2026-07-07 no Internet Archive | 2026-09-24 | https://idu.org/members/ | 54387a332fa0 |
| FNT-000063 | oficial | Internacional Liberal: página de membros, cópia de 2025-10-13 no Internet Archive | 2026-09-24 | https://liberal-international.org/our-members/regions/latin-america/ | c2366b338c25 |
| FNT-000064 | oficial | Internacional Liberal: página de membros, cópia de 2026-07-14 no Internet Archive | 2026-09-24 | https://liberal-international.org/our-members/regions/latin-america/ | 13aa28380183 |
| FNT-000065 | oficial | Internacional Socialista: página de membros, cópia de 2019-07-12 no Internet Archive | 2026-09-24 | https://www.socialistinternational.org/about-us/members/ | d77ffb132771 |
| FNT-000066 | oficial | Internacional Socialista: página de membros, cópia de 2026-07-02 no Internet Archive | 2026-09-24 | https://www.socialistinternational.org/about-us/members/ | cdeb9f054085 |
| FNT-000067 | oficial | Organização Democrata Cristã da América: página de membros, cópia de 2008-07-14 no Internet Archive | 2026-09-24 | http://www.odca.org.mx:80/miembros.html | f1ff19b306d7 |
| FNT-000068 | oficial | Organização Democrata Cristã da América: página de membros, cópia de 2016-03-15 no Internet Archive | 2026-09-24 | http://www.odca.org.mx/partidos2.php | fc12adbba021 |
| FNT-000069 | oficial | Itamaraty, Concórdia (atos internacionais): lista de todos os atos | 2026-09-25 | https://concordia.itamaraty.gov.br/ | 864685be0a38 |
| FNT-000070 | oficial | Itamaraty, Concórdia (atos internacionais): detalhe dos atos bilaterais de 2003 em diante | 2026-09-25 | https://concordia.itamaraty.gov.br/ | 4eb0f207f503 |
| FNT-000071 | oficial | TSE, dados abertos: consulta_cand_2002.zip | 2026-09-25 | https://dadosabertos.tse.jus.br/ | 33876c4d988c |
| FNT-000072 | oficial | TSE, dados abertos: consulta_cand_2006.zip | 2026-09-25 | https://dadosabertos.tse.jus.br/ | 6f5c0cf7ae80 |
| FNT-000073 | oficial | TSE, dados abertos: consulta_cand_2010.zip | 2026-09-25 | https://dadosabertos.tse.jus.br/ | 761c8eb2683b |
| FNT-000074 | oficial | TSE, dados abertos: consulta_cand_2014.zip | 2026-09-25 | https://dadosabertos.tse.jus.br/ | ad31cc36d9a6 |
| FNT-000075 | oficial | TSE, dados abertos: consulta_cand_2018.zip | 2026-09-25 | https://dadosabertos.tse.jus.br/ | 57f6881f1aa0 |
| FNT-000076 | oficial | TSE, dados abertos: consulta_cand_2022.zip | 2026-09-25 | https://dadosabertos.tse.jus.br/ | a7fdbc146f47 |
| FNT-000077 | oficial | TSE, dados abertos: prestacao_contas_2002.zip | 2026-09-25 | https://dadosabertos.tse.jus.br/ | bca94708e30c |
| FNT-000078 | oficial | TSE, dados abertos: prestacao_contas_2006.zip | 2026-09-25 | https://dadosabertos.tse.jus.br/ | 9fb37e8e82d2 |
| FNT-000079 | oficial | TSE, dados abertos: prestacao_contas_2010.zip | 2026-09-25 | https://dadosabertos.tse.jus.br/ | 5c94adac6a9a |
| FNT-000080 | oficial | TSE, dados abertos: prestacao_final_2014.zip | 2026-09-25 | https://dadosabertos.tse.jus.br/ | 9f1686ddfea2 |
| FNT-000081 | oficial | TSE, dados abertos: prestacao_de_contas_eleitorais_candidatos_2018.zip | 2026-09-25 | https://dadosabertos.tse.jus.br/ | 94774bb69183 |
| FNT-000082 | oficial | TSE, dados abertos: prestacao_de_contas_eleitorais_candidatos_2022.zip | 2026-09-25 | https://dadosabertos.tse.jus.br/ | 794cb9efbf0b |
| FNT-000083 | oficial | Nações Unidas, A/64/53 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/64/53&l=en&t=pdf | bdab7dd0d0ca |
| FNT-000084 | oficial | Nações Unidas, A/HRC/RES/20/13 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/20/13&l=en&t=pdf | d9603d2479ee |
| FNT-000085 | oficial | Nações Unidas, A/HRC/RES/20/22 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/20/22&l=en&t=pdf | 280c11b6d440 |
| FNT-000086 | oficial | Nações Unidas, A/HRC/RES/21/26 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/21/26&l=en&t=pdf | 6e46f558ff06 |
| FNT-000087 | oficial | Nações Unidas, A/HRC/RES/22/23 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/22/23&l=en&t=pdf | 5a5435a42de3 |
| FNT-000088 | oficial | Nações Unidas, A/HRC/RES/22/24 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/22/24&l=en&t=pdf | cb6d6646bd76 |
| FNT-000089 | oficial | Nações Unidas, A/HRC/RES/23/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/23/1&l=en&t=pdf | b2bf3ace4f0b |
| FNT-000090 | oficial | Nações Unidas, A/HRC/RES/23/15 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/23/15&l=en&t=pdf | 0f2d1d73e4af |
| FNT-000091 | oficial | Nações Unidas, A/HRC/RES/23/26 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/23/26&l=en&t=pdf | 443e65bb3147 |
| FNT-000092 | oficial | Nações Unidas, A/HRC/RES/25/25 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/25/25&l=en&t=pdf | 443352d52b91 |
| FNT-000093 | oficial | Nações Unidas, A/HRC/RES/28/21 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/28/21&l=en&t=pdf | 71174024b616 |
| FNT-000094 | oficial | Nações Unidas, A/HRC/RES/28/22 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/28/22&l=en&t=pdf | 406cf118622d |
| FNT-000095 | oficial | Nações Unidas, A/HRC/RES/28/27 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/28/27&l=en&t=pdf | 9f4b21b553e9 |
| FNT-000096 | oficial | Nações Unidas, A/HRC/RES/31/17 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/31/17&l=en&t=pdf | 3ddb72057fe9 |
| FNT-000097 | oficial | Nações Unidas, A/HRC/RES/32/25 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/32/25&l=en&t=pdf | 56a0b3c11cc9 |
| FNT-000098 | oficial | Nações Unidas, A/HRC/RES/32/26 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/32/26&l=en&t=pdf | 03cd6dc9d6f5 |
| FNT-000099 | oficial | Nações Unidas, A/HRC/RES/33/23 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/33/23&l=en&t=pdf | 99cffa36f779 |
| FNT-000100 | oficial | Nações Unidas, A/HRC/RES/33/24 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/33/24&l=en&t=pdf | af9a9215428e |
| FNT-000101 | oficial | Nações Unidas, A/HRC/RES/34/23 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/34/23&l=en&t=pdf | da5448af6492 |
| FNT-000102 | oficial | Nações Unidas, A/HRC/RES/34/26 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/34/26&l=en&t=pdf | bea1aed17aed |
| FNT-000103 | oficial | Nações Unidas, A/HRC/RES/34/30 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/34/30&l=en&t=pdf | e9ceb7a133ca |
| FNT-000104 | oficial | Nações Unidas, A/HRC/RES/35/26 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/35/26&l=en&t=pdf | 85dea4f79f5e |
| FNT-000105 | oficial | Nações Unidas, A/HRC/RES/35/27 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/35/27&l=en&t=pdf | 802cb4820f78 |
| FNT-000106 | oficial | Nações Unidas, A/HRC/RES/36/2 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/36/2&l=en&t=pdf | 39799a4bf618 |
| FNT-000107 | oficial | Nações Unidas, A/HRC/RES/36/20 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/36/20&l=en&t=pdf | aa235b291153 |
| FNT-000108 | oficial | Nações Unidas, A/HRC/RES/37/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/37/1&l=en&t=pdf | 7494bc03c82f |
| FNT-000109 | oficial | Nações Unidas, A/HRC/RES/37/29 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/37/29&l=en&t=pdf | cb7f55bd3057 |
| FNT-000110 | oficial | Nações Unidas, A/HRC/RES/37/30 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/37/30&l=en&t=pdf | c6de01b66e39 |
| FNT-000111 | oficial | Nações Unidas, A/HRC/RES/37/32 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/37/32&l=en&t=pdf | 43afcd7b1881 |
| FNT-000112 | oficial | Nações Unidas, A/HRC/RES/38/14 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/38/14&l=en&t=pdf | 81b52e2bd61e |
| FNT-000113 | oficial | Nações Unidas, A/HRC/RES/38/16 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/38/16&l=en&t=pdf | d63577e8542e |
| FNT-000114 | oficial | Nações Unidas, A/HRC/RES/39/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/39/1&l=en&t=pdf | 07747aeaca64 |
| FNT-000115 | oficial | Nações Unidas, A/HRC/RES/39/2 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/39/2&l=en&t=pdf | ba08a36c7d80 |
| FNT-000116 | oficial | Nações Unidas, A/HRC/RES/39/14 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/39/14&l=en&t=pdf | 85bb8ecd9320 |
| FNT-000117 | oficial | Nações Unidas, A/HRC/RES/39/15 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/39/15&l=en&t=pdf | 6bb035613049 |
| FNT-000118 | oficial | Nações Unidas, A/HRC/RES/39/16 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/39/16&l=en&t=pdf | 4870f3b91bed |
| FNT-000119 | oficial | Nações Unidas, A/HRC/RES/40/2 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/40/2&l=en&t=pdf | 825de1d2f48a |
| FNT-000120 | oficial | Nações Unidas, A/HRC/RES/40/17 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/40/17&l=en&t=pdf | 3ade44d3476a |
| FNT-000121 | oficial | Nações Unidas, A/HRC/RES/40/18 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/40/18&l=en&t=pdf | 49aed5006c69 |
| FNT-000122 | oficial | Nações Unidas, A/HRC/RES/40/23 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/40/23&l=en&t=pdf | 917d9ac6ce24 |
| FNT-000123 | oficial | Nações Unidas, A/HRC/RES/40/29 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/40/29&l=en&t=pdf | 90236cb43464 |
| FNT-000124 | oficial | Nações Unidas, A/HRC/RES/41/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/41/1&l=en&t=pdf | e7066fe12dd3 |
| FNT-000125 | oficial | Nações Unidas, A/HRC/RES/41/22 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/41/22&l=en&t=pdf | 97fead67ea30 |
| FNT-000126 | oficial | Nações Unidas, A/HRC/RES/41/23 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/41/23&l=en&t=pdf | dd69a83e86e3 |
| FNT-000127 | oficial | Nações Unidas, A/HRC/RES/42/2 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/42/2&l=en&t=pdf | e05c4b50c53e |
| FNT-000128 | oficial | Nações Unidas, A/HRC/RES/42/3 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/42/3&l=en&t=pdf | cf0d1a540cb0 |
| FNT-000129 | oficial | Nações Unidas, A/HRC/RES/42/4 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/42/4&l=en&t=pdf | 984f62949148 |
| FNT-000130 | oficial | Nações Unidas, A/HRC/RES/42/25 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/42/25&l=en&t=pdf | 61e196efd07f |
| FNT-000131 | oficial | Nações Unidas, A/HRC/RES/42/26 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/42/26&l=en&t=pdf | 1adcc9580e2c |
| FNT-000132 | oficial | Nações Unidas, A/HRC/RES/42/27 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/42/27&l=en&t=pdf | eb1bc1ab12a6 |
| FNT-000133 | oficial | Nações Unidas, A/HRC/RES/43/2 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/43/2&l=en&t=pdf | c52a03ba9c26 |
| FNT-000134 | oficial | Nações Unidas, A/HRC/RES/43/24 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/43/24&l=en&t=pdf | 735275d5eafd |
| FNT-000135 | oficial | Nações Unidas, A/HRC/RES/43/26 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/43/26&l=en&t=pdf | 80a8e1844906 |
| FNT-000136 | oficial | Nações Unidas, A/HRC/RES/43/28 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/43/28&l=en&t=pdf | 4e2e99bef2ce |
| FNT-000137 | oficial | Nações Unidas, A/HRC/RES/44/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/44/1&l=en&t=pdf | 2670f1eb1cd1 |
| FNT-000138 | oficial | Nações Unidas, A/HRC/RES/44/19 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/44/19&l=en&t=pdf | 4f9463a81737 |
| FNT-000139 | oficial | Nações Unidas, A/HRC/RES/44/21 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/44/21&l=en&t=pdf | 9bec7ee17ee5 |
| FNT-000140 | oficial | Nações Unidas, A/HRC/RES/45/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/45/1&l=en&t=pdf | 5ad665276639 |
| FNT-000141 | oficial | Nações Unidas, A/HRC/RES/45/2 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/45/2&l=en&t=pdf | e32bb98e1baa |
| FNT-000142 | oficial | Nações Unidas, A/HRC/RES/45/15 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/45/15&l=en&t=pdf | 061f5223e919 |
| FNT-000143 | oficial | Nações Unidas, A/HRC/RES/45/19 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/45/19&l=en&t=pdf | 5a270b75918a |
| FNT-000144 | oficial | Nações Unidas, A/HRC/RES/45/20 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/45/20&l=en&t=pdf | 792dfd60eb5a |
| FNT-000145 | oficial | Nações Unidas, A/HRC/RES/45/21 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/45/21&l=en&t=pdf | 5e7be90c3b19 |
| FNT-000146 | oficial | Nações Unidas, A/HRC/RES/46/2 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/46/2&l=en&t=pdf | 13a54a34f8c0 |
| FNT-000147 | oficial | Nações Unidas, A/HRC/RES/46/3 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/46/3&l=en&t=pdf | 50ff53e6232e |
| FNT-000148 | oficial | Nações Unidas, A/HRC/RES/46/18 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/46/18&l=en&t=pdf | cf536cf860a6 |
| FNT-000149 | oficial | Nações Unidas, A/HRC/RES/46/23 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/46/23&l=en&t=pdf | 66b7f03241ef |
| FNT-000150 | oficial | Nações Unidas, A/HRC/RES/47/2 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/47/2&l=en&t=pdf | 858079ead48f |
| FNT-000151 | oficial | Nações Unidas, A/HRC/RES/47/13 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/47/13&l=en&t=pdf | 36ef86d6085d |
| FNT-000152 | oficial | Nações Unidas, A/HRC/RES/47/18 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/47/18&l=en&t=pdf | b60e50c5dcc1 |
| FNT-000153 | oficial | Nações Unidas, A/HRC/RES/47/19 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/47/19&l=en&t=pdf | 32a3fe442be6 |
| FNT-000154 | oficial | Nações Unidas, A/HRC/RES/48/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/48/1&l=en&t=pdf | 72f72efa4123 |
| FNT-000155 | oficial | Nações Unidas, A/HRC/RES/48/15 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/48/15&l=en&t=pdf | bb8eca482e3d |
| FNT-000156 | oficial | Nações Unidas, A/HRC/RES/48/16 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/48/16&l=en&t=pdf | 315377e994c5 |
| FNT-000157 | oficial | Nações Unidas, A/HRC/RES/49/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/49/1&l=en&t=pdf | 06bfa6a8783c |
| FNT-000158 | oficial | Nações Unidas, A/HRC/RES/49/3 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/49/3&l=en&t=pdf | 948d55e8f18d |
| FNT-000159 | oficial | Nações Unidas, A/HRC/RES/49/4 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/49/4&l=en&t=pdf | dc8886147522 |
| FNT-000160 | oficial | Nações Unidas, A/HRC/RES/49/24 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/49/24&l=en&t=pdf | 2bb39a9a94f3 |
| FNT-000161 | oficial | Nações Unidas, A/HRC/RES/49/26 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/49/26&l=en&t=pdf | 18456b4bbebd |
| FNT-000162 | oficial | Nações Unidas, A/HRC/RES/49/27 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/49/27&l=en&t=pdf | 9b6e59215d2e |
| FNT-000163 | oficial | Nações Unidas, A/HRC/RES/50/2 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/50/2&l=en&t=pdf | e0ec272efdfd |
| FNT-000164 | oficial | Nações Unidas, A/HRC/RES/50/20 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/50/20&l=en&t=pdf | 2f893155e453 |
| FNT-000165 | oficial | Nações Unidas, A/HRC/RES/51/20 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/51/20&l=en&t=pdf | f05261b4a246 |
| FNT-000166 | oficial | Nações Unidas, A/HRC/RES/51/25 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/51/25&l=en&t=pdf | b20e54ad1972 |
| FNT-000167 | oficial | Nações Unidas, A/HRC/RES/51/26 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/51/26&l=en&t=pdf | a9b1e6d09de5 |
| FNT-000168 | oficial | Nações Unidas, A/HRC/RES/51/27 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/51/27&l=en&t=pdf | ca4a9e4ba039 |
| FNT-000169 | oficial | Nações Unidas, A/HRC/RES/51/28 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/51/28&l=en&t=pdf | 041fe0be3882 |
| FNT-000170 | oficial | Nações Unidas, A/HRC/RES/51/29 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/51/29&l=en&t=pdf | 87ef8a287fb7 |
| FNT-000171 | oficial | Nações Unidas, A/HRC/RES/52/2 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/52/2&l=en&t=pdf | 257453fddcdc |
| FNT-000172 | oficial | Nações Unidas, A/HRC/RES/52/3 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/52/3&l=en&t=pdf | 6cd8b89b0d8e |
| FNT-000173 | oficial | Nações Unidas, A/HRC/RES/52/27 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/52/27&l=en&t=pdf | e3effc7af527 |
| FNT-000174 | oficial | Nações Unidas, A/HRC/RES/52/29 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/52/29&l=en&t=pdf | f03162d41906 |
| FNT-000175 | oficial | Nações Unidas, A/HRC/RES/52/30 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/52/30&l=en&t=pdf | 03046ff6d23c |
| FNT-000176 | oficial | Nações Unidas, A/HRC/RES/52/32 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/52/32&l=en&t=pdf | e2375e99310d |
| FNT-000177 | oficial | Nações Unidas, A/HRC/RES/53/2 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/53/2&l=en&t=pdf | 71edaf785dda |
| FNT-000178 | oficial | Nações Unidas, A/HRC/RES/53/18 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/53/18&l=en&t=pdf | 5af3b3523595 |
| FNT-000179 | oficial | Nações Unidas, A/HRC/RES/53/19 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/53/19&l=en&t=pdf | 64190e51321d |
| FNT-000180 | oficial | Nações Unidas, A/HRC/RES/54/20 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/54/20&l=en&t=pdf | 8b5496deb563 |
| FNT-000181 | oficial | Nações Unidas, A/HRC/RES/54/23 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/54/23&l=en&t=pdf | 1012843c982d |
| FNT-000182 | oficial | Nações Unidas, A/HRC/RES/55/19 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/55/19&l=en&t=pdf | c37a3a681c22 |
| FNT-000183 | oficial | Nações Unidas, A/HRC/RES/55/22 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/55/22&l=en&t=pdf | 6d7ff0e253e1 |
| FNT-000184 | oficial | Nações Unidas, A/HRC/RES/55/23 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/55/23&l=en&t=pdf | b68d5097f1f0 |
| FNT-000185 | oficial | Nações Unidas, A/HRC/RES/56/17 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/56/17&l=en&t=pdf | 1cb6524222d9 |
| FNT-000186 | oficial | Nações Unidas, A/HRC/RES/57/20 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/57/20&l=en&t=pdf | 6df6807de8a5 |
| FNT-000187 | oficial | Nações Unidas, A/HRC/RES/57/21 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/57/21&l=en&t=pdf | b5e6e3a2711b |
| FNT-000188 | oficial | Nações Unidas, A/HRC/RES/57/22 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/57/22&l=en&t=pdf | 52f5a4c3e724 |
| FNT-000189 | oficial | Nações Unidas, A/HRC/RES/57/36 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/57/36&l=en&t=pdf | 1291fed00733 |
| FNT-000190 | oficial | Nações Unidas, A/HRC/RES/58/2 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/58/2&l=en&t=pdf | 91279820f53b |
| FNT-000191 | oficial | Nações Unidas, A/HRC/RES/58/18 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/58/18&l=en&t=pdf | aa07894557d9 |
| FNT-000192 | oficial | Nações Unidas, A/HRC/RES/58/19 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/58/19&l=en&t=pdf | 72427c44909c |
| FNT-000193 | oficial | Nações Unidas, A/HRC/RES/58/21 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/58/21&l=en&t=pdf | 04eddd43ca3d |
| FNT-000194 | oficial | Nações Unidas, A/HRC/RES/58/24 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/58/24&l=en&t=pdf | 438b6ef1ddfc |
| FNT-000195 | oficial | Nações Unidas, A/HRC/RES/59/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/59/1&l=en&t=pdf | dbb429d07e80 |
| FNT-000196 | oficial | Nações Unidas, A/HRC/RES/60/15 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/60/15&l=en&t=pdf | beee2d20f84c |
| FNT-000197 | oficial | Nações Unidas, A/HRC/RES/60/21 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/60/21&l=en&t=pdf | 121a739893db |
| FNT-000198 | oficial | Nações Unidas, A/HRC/RES/61/4 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/61/4&l=en&t=pdf | 7048aa4f39ae |
| FNT-000199 | oficial | Nações Unidas, A/HRC/RES/61/26 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/61/26&l=en&t=pdf | 46fae92ecaf1 |
| FNT-000200 | oficial | Nações Unidas, A/HRC/RES/61/29 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/61/29&l=en&t=pdf | 595932a6f5a0 |
| FNT-000201 | oficial | Nações Unidas, A/HRC/RES/62/2 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/62/2&l=en&t=pdf | 55783e6b0266 |
| FNT-000202 | oficial | Nações Unidas, A/HRC/RES/S-12/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/S-12/1&l=en&t=pdf | a6e12b8a061d |
| FNT-000203 | oficial | Nações Unidas, A/HRC/RES/S-25/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/S-25/1&l=en&t=pdf | 3236c392d48d |
| FNT-000204 | oficial | Nações Unidas, A/HRC/RES/S-27/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/S-27/1&l=en&t=pdf | 7f2ff95e5021 |
| FNT-000205 | oficial | Nações Unidas, A/HRC/RES/S-33/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/S-33/1&l=en&t=pdf | 19023bd9ca13 |
| FNT-000206 | oficial | Nações Unidas, A/HRC/RES/S-34/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/S-34/1&l=en&t=pdf | ad0147d539ac |
| FNT-000207 | oficial | Nações Unidas, A/HRC/RES/S-35/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/S-35/1&l=en&t=pdf | d167a8d2f6d8 |
| FNT-000208 | oficial | Nações Unidas, A/HRC/RES/S-39/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/S-39/1&l=en&t=pdf | e1e914c73033 |
| FNT-000209 | oficial | Nações Unidas, A/63/53 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/63/53&l=en&t=pdf | 7b0894bd77da |
| FNT-000210 | oficial | Nações Unidas, A/HRC/RES/22/28 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/22/28&l=en&t=pdf | a2137fbce1bb |
| FNT-000211 | oficial | Nações Unidas, A/HRC/RES/25/24 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/25/24&l=en&t=pdf | 203013824f27 |
| FNT-000212 | oficial | Nações Unidas, A/HRC/RES/31/19 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/31/19&l=en&t=pdf | e77daa5a0330 |
| FNT-000213 | oficial | Nações Unidas, A/HRC/RES/31/34 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/31/34&l=en&t=pdf | 005dd941b1ae |
| FNT-000214 | oficial | Nações Unidas, A/HRC/RES/53/22 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/53/22&l=en&t=pdf | 35ca1c1938b2 |
| FNT-000215 | oficial | Nações Unidas, A/HRC/RES/55/28 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/55/28&l=en&t=pdf | c441f6343bce |
| FNT-000216 | oficial | Nações Unidas, A/HRC/RES/37/35 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/37/35&l=en&t=pdf | dce21e3f9da8 |
| FNT-000217 | oficial | Nações Unidas, A/HRC/RES/50/19 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/50/19&l=en&t=pdf | d701fc3210d3 |
| FNT-000218 | oficial | Nações Unidas, A/HRC/RES/13/14 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/13/14&l=en&t=pdf | 89b070f33fae |
| FNT-000219 | oficial | Nações Unidas, A/HRC/RES/15/27 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/15/27&l=en&t=pdf | 6c26198092eb |
| FNT-000220 | oficial | Nações Unidas, A/HRC/RES/16/8 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/16/8&l=en&t=pdf | a87f9cd5d804 |
| FNT-000221 | oficial | Nações Unidas, A/HRC/RES/16/9 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/16/9&l=en&t=pdf | 4480e01ec8e9 |
| FNT-000222 | oficial | Nações Unidas, A/HRC/RES/16/29 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/16/29&l=en&t=pdf | f04935151a8a |
| FNT-000223 | oficial | Nações Unidas, A/HRC/RES/17/24 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/17/24&l=en&t=pdf | a6765cc10f77 |
| FNT-000224 | oficial | Nações Unidas, A/HRC/RES/19/12 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/19/12&l=en&t=pdf | 924336faeeb8 |
| FNT-000225 | oficial | Nações Unidas, A/HRC/RES/19/16 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/19/16&l=en&t=pdf | 55b14178608d |
| FNT-000226 | oficial | Nações Unidas, A/HRC/RES/26/25 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/26/25&l=en&t=pdf | a6793a396b35 |
| FNT-000227 | oficial | Nações Unidas, A/HRC/RES/S-16/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/S-16/1&l=en&t=pdf | a21fe7c11bca |
| FNT-000228 | oficial | Nações Unidas, A/HRC/RES/S-18/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/S-18/1&l=en&t=pdf | dfd8aa56dd2d |
| FNT-000229 | oficial | Nações Unidas, A/HRC/RES/S-19/1 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/HRC/RES/S-19/1&l=en&t=pdf | 4c95fa41c6fe |
| FNT-000230 | oficial | Nações Unidas, A/62/53 | 2026-09-25 | https://documents.un.org/api/symbol/access?s=A/62/53&l=en&t=pdf | 797c970b8bf0 |
| FNT-000231 | oficial | STF, Corte Aberta: decisões em petições de ramo penal, 05/02/2003 a 24/09/2026 (exportação do painel) | 2026-09-25 | https://transparencia.stf.jus.br/extensions/decisoes/decisoes.html | b5b6f261cf94 |
| FNT-000232 | oficial | STF, Corte Aberta: acervo de petições criminais em tramitação (exportação do painel) | 2026-09-25 | https://transparencia.stf.jus.br/extensions/acervo/acervo.html | 09ccf6240349 |
| FNT-000233 | judicial | STF, AP 470: página de acompanhamento processual (abas Partes e Andamentos) | 2026-09-25 | https://portal.stf.jus.br/processos/detalhe.asp?incidente=11541 |  |
| FNT-000234 | judicial | STF, AP 470: andamento de 23/10/2012 (Decisão de Julgamento, Tribunal Pleno, formação de quadrilha) | 2026-09-25 | https://portal.stf.jus.br/processos/detalhe.asp?incidente=11541 |  |
| FNT-000235 | judicial | STF, AP 470 EI (embargos infringentes): acórdão de 27/02/2014, julgamento conjunto dos embargos sobre quadrilha | 2026-09-26 | https://jurisprudencia.stf.jus.br/pages/search/sjur273411/false |  |
| FNT-000236 | oficial | STF, Notícias: AP 470: STF fixa penas do núcleo político e inicia análise de dosimetria quanto ao núcleo financeiro | 2026-09-26 | https://noticias.stf.jus.br/postsnoticias/ap-470-stf-fixa-penas-do-nucleo-politico-e-inicia-analise-de-dosimet |  |
| FNT-000237 | oficial | STF, Notícias: Concluída dosimetria das penas de Rogério Tolentino e Vinícius Samarane na AP 470 | 2026-09-26 | https://noticias.stf.jus.br/postsnoticias/concluida-dosimetria-das-penas-de-rogerio-tolentino-e-vinicius-samar |  |
| FNT-000238 | oficial | STF, Notícias: Relator nega provimento a embargos infringentes de condenados por quadrilha na AP 470 (nomeia os oito embargantes) | 2026-09-26 | https://noticias.stf.jus.br/postsnoticias/relator-nega-provimento-a-embargos-infringentes-de-condenados-por-qu |  |
| FNT-000239 | judicial | TJMG, 2ª Câmara Cível, Apelação Cível 1.0604.16.000505-3/001 (acórdão que relata a confirmação, em 22/08/2017, da condenação na ação penal 2378231-34. | 2026-09-26 | https://consulta-jurisprudencia.tjmg.jus.br/inteiro-teor?documentoId=10604160000505001-0&publicacaoData=2017-1 |  |
| FNT-000240 | judicial | TJMG, 1ª Câmara Criminal, Embargos de Declaração-Cr 1.0000.25.033497-6/002 (cita a ementa dos Embargos de Declaração-Cr 1.0024.14.237823-1/006, julgad | 2026-09-26 | https://consulta-jurisprudencia.tjmg.jus.br/inteiro-teor?documentoId=10000250033497002-0&publicacaoData=2025-0 |  |
| FNT-000241 | judicial | TJMG, Órgão Especial, Agravo Interno Cv 1.0024.14.237823-1/012 (agravante Eduardo Brandão Azeredo; negado provimento) | 2026-09-26 | https://consulta-jurisprudencia.tjmg.jus.br/inteiro-teor?documentoId=10024140237823012-0&publicacaoData=2019-0 |  |
| FNT-000242 | judicial | TJMG, Consulta Processual Unificada: ação penal 2378231-34.2014.8.13.0024 (resposta: processo sigiloso, acesso restrito) | 2026-09-26 | https://consulta.tjmg.jus.br/pesquisa?q=%7B%22numeroProcesso%22%3A%5B%222378231-34.2014.8.13.0024%22%5D%7D |  |
| FNT-000243 | oficial | TJMG, Notícias: Juíza interroga três acusados do processo Mensalão mineiro (diz que o réu foi condenado em primeira instância em abril de 2016) | 2026-09-26 | https://www.tjmg.jus.br/portal-tjmg/noticias/juiza-interroga-tres-acusados-do-processo-mensalao-mineiro.htm |  |
| FNT-000244 | oficial | TJMG, Notícias: Juíza interrogará réu do mensalão mineiro (diz que E.B.A. foi condenado em dezembro de 2015) | 2026-09-26 | https://www.tjmg.jus.br/portal-tjmg/noticias/juiza-interrogara-reu-do-mensalao-mineiro.htm |  |
| FNT-000245 | oficial | TRF4, Notícias: Operação Lava Jato: TRF4 confirma condenação do ex-presidente Luiz Inácio Lula da Silva | 2026-09-28 | https://www.trf4.jus.br/trf4/controlador.php?acao=noticia_visualizar&id_noticia=13418 |  |
| FNT-000246 | oficial | STJ, Notícias: Quinta Turma reduz pena do ex-presidente Lula para oito anos e dez meses | 2026-09-28 | https://www.stj.jus.br/sites/portalp/Paginas/Comunicacao/Noticias/Quinta-Turma-reduz-pena-do-ex-presidente-Lul |  |
| FNT-000247 | oficial | STF, Notícias: Fachin anula condenações de Lula e manda ações penais para Justiça Federal do DF | 2026-09-28 | https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo=461870&ori=1 |  |
| FNT-000248 | oficial | STF, Notícias: 2ª Turma reconhece parcialidade de ex-juiz Sérgio Moro na condenação de Lula no caso Triplex | 2026-09-28 | https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo=462854&ori=1 |  |
| FNT-000249 | oficial | STF, Notícias: STF confirma anulação de condenações do ex-presidente Lula na Lava Jato | 2026-09-28 | https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo=464261&ori=1 |  |
| FNT-000250 | oficial | STF, Notícias: Plenário fixa competência da Justiça Federal do DF para julgar processos contra ex-presidente Lula | 2026-09-28 | https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo=464566&ori=1 |  |
| FNT-000251 | oficial | STF, Notícias: STF confirma suspeição de Sergio Moro na ação do triplex do Guarujá | 2026-09-28 | https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo=468086&ori=1 |  |
| FNT-000252 | oficial | STF, Notícias: STF anula todas as provas obtidas em sistemas da Odebrecht em todas as esferas e para todas as ações | 2026-09-28 | https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo=513517&ori=1 |  |
| FNT-000253 | oficial | STF, Notícias: STF anula provas utilizadas em ação contra ex-ministro Paulo Bernardo | 2026-09-28 | https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo=509162&ori=1 |  |
| FNT-000254 | oficial | STF, Notícias: STF anula provas utilizadas em ações penais contra Sérgio Cabral e Gilberto Kassab | 2026-09-28 | https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo=511633&ori=1 |  |
| FNT-000255 | judicial | STF, Pet 15556 e processos relacionados: páginas de acompanhamento processual (abas Partes e Andamentos) | 2026-09-28 | https://portal.stf.jus.br/processos/detalhe.asp?incidente=7514886 |  |
| FNT-000256 | judicial | STF, Pet 15556: andamento de 04/03/2026 (decisão monocrática; prisão preventiva de investigados) | 2026-09-28 | https://portal.stf.jus.br/processos/detalhe.asp?incidente=7514886 |  |
| FNT-000257 | judicial | STF, Pet 15556: andamento de 23/03/2026 (2ª Turma; referendo da liminar) | 2026-09-28 | https://portal.stf.jus.br/processos/detalhe.asp?incidente=7514886 |  |
| FNT-000258 | judicial | STF, Pet 15556: andamento de 03/04/2026 (decisão monocrática sobre convocação à CPI do Crime Organizado) | 2026-09-28 | https://portal.stf.jus.br/processos/detalhe.asp?incidente=7514886 |  |
| FNT-000259 | oficial | TRF4, Notícias: TRF4 confirma condenação do ex-presidente Lula (ação do sítio de Atibaia) | 2026-09-29 | https://www.trf4.jus.br/trf4/controlador.php?acao=noticia_visualizar&id_noticia=14914 |  |
| FNT-000260 | oficial | JFPR (portal do TRF4), Notícias: Operação Lava Jato: julgada ação penal por crimes de lavagem de desvios na Rnest | 2026-09-29 | https://www.trf4.jus.br/trf4/controlador.php?acao=noticia_visualizar&id_noticia=17907 |  |
| FNT-000261 | oficial | STF, Biblioteca: Cezar Peluso - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | dca9ee0634d4 |
| FNT-000262 | oficial | STF: ministros nomeados por Luiz Inácio Lula da Silva | 2026-09-29 | https://portal.stf.jus.br/ostf/ministros/detalhamentos.asp?detalhamento=INDICACOES&entidade=1 | f795f66aef51 |
| FNT-000263 | oficial | STF, Biblioteca: Menezes Direito - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 5b0972e7ee37 |
| FNT-000264 | oficial | STF: biografia de Menezes Direito | 2026-09-29 | https://portal.stf.jus.br/ostf/ministros/verMinistro.asp?periodo=STF&id=43 | f0dca0b72f5a |
| FNT-000265 | oficial | STF, Biblioteca: Ayres Britto - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 95d330364f1a |
| FNT-000266 | oficial | STF, Biblioteca: Cármen Lúcia - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 0412471b2acd |
| FNT-000267 | oficial | STF, Biblioteca: Cristiano Zanin - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | a2c3fe79af00 |
| FNT-000268 | oficial | STF, Biblioteca: Ricardo Lewandowski - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 0607911b6482 |
| FNT-000269 | oficial | STF, Biblioteca: Eros Grau - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 1ae17a1f3a2b |
| FNT-000270 | oficial | STF, Biblioteca: Flávio Dino - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 113350457439 |
| FNT-000271 | oficial | STF: notícia oficial sobre Flávio Dino | 2026-09-29 | https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo=528119&ori=1 | 03587bd2784a |
| FNT-000272 | oficial | STF, Biblioteca: Joaquim Barbosa - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 0fad33ab2a69 |
| FNT-000273 | oficial | STF, Biblioteca: Dias Toffoli - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 8d58ad6b1e3d |
| FNT-000274 | oficial | STF, Biblioteca: Ellen Gracie - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | a7d0026cb900 |
| FNT-000275 | oficial | STF: ministros nomeados por Fernando Henrique Cardoso | 2026-09-29 | https://portal.stf.jus.br/ostf/ministros/detalhamentos.asp?detalhamento=INDICACOES&entidade=2 | b6babc33597a |
| FNT-000276 | oficial | STF, Biblioteca: Gilmar Mendes - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | babb94b574b3 |
| FNT-000277 | oficial | STF, Biblioteca: Nelson Jobim - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 34436d8be68b |
| FNT-000278 | oficial | STF, Biblioteca: Maurício Corrêa - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 535e5a83f267 |
| FNT-000279 | oficial | STF: ministros nomeados por Itamar Augusto Cautiero Franco | 2026-09-29 | https://portal.stf.jus.br/ostf/ministros/detalhamentos.asp?detalhamento=INDICACOES&entidade=3 | 4bc86ce52128 |
| FNT-000280 | oficial | STF: biografia de Maurício Corrêa | 2026-09-29 | https://portal.stf.jus.br/ostf/ministros/verMinistro.asp?periodo=STF&id=33 | d6060e138df3 |
| FNT-000281 | oficial | STF, Biblioteca: Carlos Velloso - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | b601b3fea4ba |
| FNT-000282 | oficial | STF: ministros nomeados por Fernando Affonso Collor de Mello | 2026-09-29 | https://portal.stf.jus.br/ostf/ministros/detalhamentos.asp?detalhamento=INDICACOES&entidade=4 | d188a0044992 |
| FNT-000283 | oficial | STF, Biblioteca: Ilmar Galvão - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | c4a77e835250 |
| FNT-000284 | oficial | STF, Biblioteca: Marco Aurélio - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | ab1680d7f0c8 |
| FNT-000285 | oficial | STF, Biblioteca: Luís Roberto Barroso - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 96d7376a55e5 |
| FNT-000286 | oficial | STF: ministros nomeados por Dilma Rousseff | 2026-09-29 | https://portal.stf.jus.br/ostf/ministros/detalhamentos.asp?detalhamento=INDICACOES&entidade=41 | 8e557b5eff6c |
| FNT-000287 | oficial | STF, Biblioteca: Edson Fachin - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 6a763368d4f7 |
| FNT-000288 | oficial | STF, Biblioteca: Luiz Fux - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 9744f82c2618 |
| FNT-000289 | oficial | STF, Biblioteca: Rosa Weber - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | a31d7253b533 |
| FNT-000290 | oficial | STF, Biblioteca: Teori Zavascki - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | d0bf767243cc |
| FNT-000291 | oficial | STF: notícia oficial sobre Teori Zavascki | 2026-09-29 | https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo=500851&ori=1 | 6beaaef7d0c4 |
| FNT-000292 | oficial | STF, Biblioteca: Celso de Mello - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 82a4f0a0ee62 |
| FNT-000293 | oficial | STF: ministros nomeados por José Sarney | 2026-09-29 | https://portal.stf.jus.br/ostf/ministros/detalhamentos.asp?detalhamento=INDICACOES&entidade=5 | f4923a01c055 |
| FNT-000294 | oficial | STF, Biblioteca: Sepúlveda Pertence - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 9454b6732c30 |
| FNT-000295 | oficial | STF, Biblioteca: Sydney Sanches - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 44f3593ade0b |
| FNT-000296 | oficial | STF: ministros nomeados por João Baptista de Oliveira Figueiredo | 2026-09-29 | https://portal.stf.jus.br/ostf/ministros/detalhamentos.asp?detalhamento=INDICACOES&entidade=6 | 2ebf3035e28b |
| FNT-000297 | oficial | STF, Biblioteca: Alexandre de Moraes - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | d6b1d31eba27 |
| FNT-000298 | oficial | STF: ministros nomeados por Michel Temer | 2026-09-29 | https://portal.stf.jus.br/ostf/ministros/detalhamentos.asp?detalhamento=INDICACOES&entidade=61 | 91b059e55aab |
| FNT-000299 | oficial | STF, Biblioteca: Moreira Alves - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | b4a6f9c955ad |
| FNT-000300 | oficial | STF: ministros nomeados por Ernesto Geisel | 2026-09-29 | https://portal.stf.jus.br/ostf/ministros/detalhamentos.asp?detalhamento=INDICACOES&entidade=7 | d00b6f05064d |
| FNT-000301 | oficial | STF, Biblioteca: André Mendonça - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 2f1006097312 |
| FNT-000302 | oficial | STF: ministros nomeados por Jair Messias Bolsonaro | 2026-09-29 | https://portal.stf.jus.br/ostf/ministros/detalhamentos.asp?detalhamento=INDICACOES&entidade=81 | 06c0b2c2bfda |
| FNT-000303 | oficial | STF, Biblioteca: Nunes Marques - Dados e Datas | 2026-09-29 | https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina= | 1225eb3b204d |
| FNT-000304 | legislativa | Senado: MSF 7/2026 e votação nominal de 2026-04-29 | 2026-09-29 | https://www25.senado.leg.br/web/atividade/materias/-/materia/173452 | 4fad4909ef7b |
| FNT-000305 | base_de_dados | Bolognesi, Ribeiro e Codato (2023). Uma Nova Classificação Ideológica dos Partidos Políticos Brasileiros. Dados 66(2) | 2026-09-29 | https://doi.org/10.1590/dados.2023.66.2.303 | cc91b233d6fe |
| FNT-000306 | oficial | Câmara dos Deputados, dados abertos: tramitações das representações (REP) | 2026-09-29 | https://dadosabertos.camara.leg.br/api/v2/proposicoes/{id}/tramitacoes | d4437eaebaa9 |
| FNT-000307 | oficial | Senado Federal, dados abertos: processos do Conselho de Ética (REP, DEN, PCE) | 2026-09-29 | https://legis.senado.leg.br/dadosabertos/processo/{id} | f1ebd9a6fb96 |
| FNT-000308 | oficial | Senado Federal, dados abertos: Projetos de Resolução do Senado gerados por representações | 2026-09-29 | https://legis.senado.leg.br/dadosabertos/processo/{id} | c3e90c236804 |
| FNT-000309 | oficial | TCU, certidões: responsáveis com contas julgadas irregulares (lista pública) | 2026-09-29 | https://certidoes.apps.tcu.gov.br/api/publico/responsaveis-contas-irregulares/exportar-para-csv?paginaAtual=1& | 30f65ab3fa02 |
| FNT-000310 | oficial | TSE, dados abertos: motivo_cassacao_2018.zip | 2026-09-25 | https://dadosabertos.tse.jus.br/ | 7922156cc5c6 |
| FNT-000311 | oficial | TSE, dados abertos: motivo_cassacao_2022.zip | 2026-09-25 | https://dadosabertos.tse.jus.br/ | 62583ced7c81 |
| FNT-000312 | oficial | STF, AP 1011: decisão monocrática publicada no DJe em 2017-08-23 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=312495372&ext=.pdf | a3015f2cf936 |
| FNT-000313 | oficial | STF, AP 396: decisão monocrática publicada no DJe em 2019-10-18 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=15341501774&ext=.pdf | 3683ea5f4ff6 |
| FNT-000314 | oficial | STF, AP 415: decisão monocrática publicada no DJe em 2013-09-02 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=166278201&ext=.pdf | ec0df6057657 |
| FNT-000315 | oficial | STF, AP 451: decisão monocrática publicada no DJe em 2013-10-03 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=173945413&ext=.pdf | ae300b16867d |
| FNT-000316 | oficial | STF, AP 467: decisão monocrática publicada no DJe em 2013-12-11 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=189869518&ext=.pdf | 4e5c3336eca8 |
| FNT-000317 | oficial | STF, AP 545: decisão monocrática publicada no DJe em 2012-12-19 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=116478450&ext=.pdf | b4c50f645fd7 |
| FNT-000318 | oficial | STF, AP 557: decisão monocrática publicada no DJe em 2014-10-24 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=270950527&ext=.pdf | 25701ce080c7 |
| FNT-000319 | oficial | STF, AP 650: decisão monocrática publicada no DJe em 2014-11-12 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=278113709&ext=.pdf | b51cf9b761ff |
| FNT-000320 | oficial | STF, AP 582: decisão monocrática publicada no DJe em 2014-06-18 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=237513957&ext=.pdf | cfa3beec2eca |
| FNT-000321 | oficial | STF, AP 584: decisão monocrática publicada no DJe em 2014-04-28 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=217186046&ext=.pdf | d071e2d17ed5 |
| FNT-000322 | oficial | STF, AP 593: decisão monocrática publicada no DJe em 2013-10-03 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=174003988&ext=.pdf | 9038da775e65 |
| FNT-000323 | oficial | STF, AP 597: decisão monocrática publicada no DJe em 2014-02-10 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=199527020&ext=.pdf | 401c891e2521 |
| FNT-000324 | oficial | STF, AP 607: decisão monocrática publicada no DJe em 2015-08-06 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=307366999&ext=.pdf | 72586014bb06 |
| FNT-000325 | oficial | STF, AP 615: decisão monocrática publicada no DJe em 2012-12-03 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=113938234&ext=.pdf | b8564b5a2552 |
| FNT-000326 | oficial | STF, AP 624: decisão monocrática publicada no DJe em 2013-03-07 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=127180086&ext=.pdf | 58050c46d57b |
| FNT-000327 | oficial | STF, AP 642: decisão monocrática publicada no DJe em 2013-10-03 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=173972400&ext=.pdf | 368ec62e665c |
| FNT-000328 | oficial | STF, AP 648: decisão monocrática publicada no DJe em 2015-09-04 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=307652156&ext=.pdf | 82d9ab4aa41d |
| FNT-000329 | oficial | STF, AP 673: decisão monocrática publicada no DJe em 2013-09-24 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=171699154&ext=.pdf | 2419e55aed34 |
| FNT-000330 | oficial | STF, AP 675: decisão monocrática publicada no DJe em 2013-12-11 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=189869508&ext=.pdf | 98ec6b2dc594 |
| FNT-000331 | oficial | STF, AP 690: decisão monocrática publicada no DJe em 2013-04-11 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=133172433&ext=.pdf | 144b4be7042a |
| FNT-000332 | oficial | STF, AP 696: decisão monocrática publicada no DJe em 2014-03-06 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=203935668&ext=.pdf | 6053e8689a3d |
| FNT-000333 | oficial | STF, AP 699: decisão monocrática publicada no DJe em 2013-04-23 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=135371353&ext=.pdf | 58da7ea214aa |
| FNT-000334 | oficial | STF, AP 702: decisão monocrática publicada no DJe em 2015-02-24 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=302867141&ext=.pdf | c205eeff6c91 |
| FNT-000335 | oficial | STF, AP 854: decisão monocrática publicada no DJe em 2014-03-13 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=205841398&ext=.pdf | 3c767cde9f90 |
| FNT-000336 | oficial | STF, AP 868: decisão monocrática publicada no DJe em 2014-05-19 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=222186348&ext=.pdf | 7c02a89459e3 |
| FNT-000337 | oficial | STF, AP 939: decisão monocrática publicada no DJe em 2017-05-29 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=311894551&ext=.pdf | 8425f99d26d8 |
| FNT-000338 | oficial | STF, AP 952: decisão monocrática publicada no DJe em 2018-10-11 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=15338828862&ext=.pdf | 9bb2df39c9d0 |
| FNT-000339 | oficial | STF, AP 961: decisão monocrática publicada no DJe em 2018-06-07 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=314532778&ext=.pdf | 16168143fc6b |
| FNT-000340 | oficial | STF, AP 969: decisão monocrática publicada no DJe em 2023-08-31 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=15360649155&ext=.pdf | 4a992f78eec9 |
| FNT-000341 | oficial | STF, AP 983: decisão monocrática publicada no DJe em 2018-03-09 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=313862614&ext=.pdf | 3157070ae75d |
| FNT-000342 | oficial | STF, AP 988: decisão monocrática publicada no DJe em 2017-10-23 (peça do portal) | 2026-09-30 | https://portal.stf.jus.br/processos/downloadPeca.asp?id=313078885&ext=.pdf | 7b80928ff1dd |

## Apêndice B. Tabelas de saída citadas

- `relatorios/tabelas/eixo1_homogeneidade.csv`
- `relatorios/tabelas/eixo1_parlamentares_cobertura.csv`
- `relatorios/tabelas/eixo1_parlamentares_correlacao.csv`
- `relatorios/tabelas/eixo1_parlamentares_governo_periodo.csv`
- `relatorios/tabelas/eixo1_parlamentares_homogeneidade.csv`
- `relatorios/tabelas/eixo1_registros.csv`
- `relatorios/tabelas/eixo1_taxas.csv`
- `relatorios/tabelas/eixo2_acordos_por_governo.csv`
- `relatorios/tabelas/eixo2_bndes_por_governo.csv`
- `relatorios/tabelas/eixo2_comercio_por_governo.csv`
- `relatorios/tabelas/eixo2_redes_partidarias.csv`
- `relatorios/tabelas/eixo2_votos_por_governo.csv`
- `relatorios/tabelas/eixo2_votos_por_resolucao.csv`
- `relatorios/tabelas/eixo3_foro_governo_periodo.csv`
- `relatorios/tabelas/eixo3_foro_taxas.csv`
- `relatorios/tabelas/eixo3_foro_testes.csv`
- `relatorios/tabelas/eixo3_relator_2x2.csv`
- `relatorios/tabelas/eixo3_relator_ministros.csv`
- `relatorios/tabelas/eixo3_relator_presidentes.csv`
- `relatorios/tabelas/etica_correlacao.csv`
- `relatorios/tabelas/etica_desfechos.csv`
- `relatorios/tabelas/etica_governo_periodo.csv`
- `relatorios/tabelas/etica_homogeneidade.csv`
- `relatorios/tabelas/etica_taxas.csv`
- `relatorios/tabelas/ideologia_correlacao.csv`
- `relatorios/tabelas/imprensa_contraste_por_fato.csv`
- `relatorios/tabelas/imprensa_contraste_por_veiculo.csv`
- `relatorios/tabelas/imprensa_navegador_folha_por_coleta.csv`
- `relatorios/tabelas/imprensa_navegador_por_veiculo.csv`
- `relatorios/tabelas/simetria_taxa_bancada.csv`
- `relatorios/tabelas/simetria_taxa_governo_oposicao.csv`
- `relatorios/tabelas/stf_desfechos.csv`
- `relatorios/tabelas/stf_desfechos_cobertura.csv`
- `relatorios/tabelas/stf_desfechos_homogeneidade.csv`
- `relatorios/tabelas/stf_desfechos_taxas.csv`
