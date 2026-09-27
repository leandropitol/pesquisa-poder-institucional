# Limitações metodológicas

Documento mantido junto de todo relatório. A primeira parte é escrita e revisada à mão; a segunda é
gerada a partir da base (cobertura, lacunas e registros sem verificação) e não deve ser editada.

## Parte escrita: vieses e lacunas conhecidos

### Fontes judiciais

1. **Sigilo.** Processos e peças sob sigilo não aparecem. Ausência na base não significa ausência de
   processo.
2. **Jurisprudência do STF sem API oficial.** A coleta depende do Corte Aberta e de consulta ao portal,
   com limite de requisições; pode haver lacunas, registradas em `buscas`.
3. **Número de processos antigo.** Processos anteriores à numeração única do CNJ (2010) exigem
   conciliação manual de números.
4. **Foro e instância mudam.** A restrição do foro por prerrogativa (STF, AP 937, 2018) mudou o universo
   de processos originários: comparações antes e depois de 2018 não medem só conduta.

### Esforço investigativo e cobertura

5. **Exposição desigual.** O número de processos depende do esforço de investigação, da força-tarefa, do
   período e de quem controla o Executivo. Diferença de contagem entre partidos não mede, sozinha,
   diferença de conduta. Por isso a verificação de simetria separa também governo e oposição na época.
6. **Cobertura jornalística desigual** por veículo, região e período. Registros só jornalísticos ficam
   como `alegado`.
7. **Colaboração premiada.** Delações citam terceiros sem prova autônoma; várias foram revistas ou
   anuladas. Conteúdo de delação nunca passa de `alegado` quanto a terceiros.
8. **Anulações.** Condenações anuladas (por exemplo, as da Lava Jato anuladas pelo STF) continuam na
   linha do tempo como fatos históricos e aparecem como anuladas no status vigente.

### Dados administrativos

9. **TSE.** O formato da prestação de contas muda entre eleições; séries anteriores a 2006 são menos
   completas. Doações empresariais foram proibidas a partir de 2015, o que muda a comparação.
10. **BNDES.** Os dados abertos cobrem as operações divulgadas; condições contratuais e garantias
    (seguro de crédito, FGE) podem estar em outras bases.
11. **Portal da Transparência.** Cobertura e formato variam por ano e por programa.

### Réguas externas

12. **V-Dem e Freedom House** são avaliações de especialistas com metodologias próprias; revisam séries
    passadas entre versões. A versão usada fica registrada em `fonte_base_dados`.

### Desenho do projeto

13. **Universo da fase 1** restrito a processos originários no STF e no STJ: deixa de fora casos que
    nunca subiram de instância, enquanto a fase 2 não for feita.
14. **Coincidência temporal não é motivo.** Indicadores como "nomeação durante investigação" medem datas,
    não intenção.
15. **Dados pessoais.** A minimização (sem CPF, doações de pessoa física agregadas) limita o
    cruzamento de homônimos; a deduplicação usa identificadores oficiais quando existem.

<!-- INICIO-GERADO -->
## Parte gerada: cobertura da base

Gerada por `python -m src.relatorios.limitacoes`. Não editar à mão.

### Registros por tabela

| Tabela | Registros |
|---|---:|
| `atores` | 2815 |
| `filiacoes` | 6553 |
| `cargos` | 4628 |
| `instituicoes` | 1485 |
| `denominacoes_partido` | 67 |
| `casos` | 2 |
| `processos` | 10068 |
| `fases_processo` | 6615 |
| `status_pessoa_processo` | 66 |
| `eventos` | 2297 |
| `relacoes` | 2429 |
| `fontes` | 244 |
| `fonte_judicial` | 7 |
| `fonte_oficial` | 234 |
| `fonte_base_dados` | 3 |
| `evento_fonte` | 2297 |
| `relacao_fonte` | 2449 |
| `buscas` | 286 |
| `universo_partidos` | 521 |
| `qualidade_democratica` | 16651 |
| `operacoes_exportacao_bndes` | 2996 |
| `votos_multilaterais` | 26696 |
| `acordos_bilaterais` | 7720 |
| `emendas_parlamentares` | 92364 |
| `doacoes_campanha` | 12613 |

Tabelas ainda vazias (8): `afirmacoes`, `fonte_legislativa`, `fonte_orcamentaria`, `fonte_jornalistica`, `afirmacao_fonte`, `verificacoes_simetria`, `verificacao_resultado`, `decisoes_judiciais`.

### Buscas

- 286 buscas registradas; 45 com zero resultados.
- BNDES, dados abertos (CKAN): 7 buscas, coleta de 2026-09-24.
- Câmara, API v2: 9 buscas, coleta de 2026-09-24.
- DataJud (CNJ), API pública, STJ: 3 buscas, coleta de 2026-09-24.
- Freedom House, planilhas históricas: 2 buscas, coleta de 2026-09-24.
- Internet Archive (Wayback Machine): Aliança Progressista: 3 buscas, coleta de 2026-09-24.
- Internet Archive (Wayback Machine): Conferência Permanente de Partidos Políticos da América Latina e do Caribe: 8 buscas, coleta de 2026-09-24.
- Internet Archive (Wayback Machine): Foro de Madri: 2 buscas, coleta de 2026-09-24.
- Internet Archive (Wayback Machine): Foro de São Paulo: 2 buscas, coleta de 2026-09-24.
- Internet Archive (Wayback Machine): Grupo de Puebla: 1 buscas, coleta de 2026-09-24.
- Internet Archive (Wayback Machine): Internacional Democrata Centrista: 2 buscas, coleta de 2026-09-24.
- Internet Archive (Wayback Machine): Internacional Liberal: 4 buscas, coleta de 2026-09-24.
- Internet Archive (Wayback Machine): Internacional Socialista: 4 buscas, coleta de 2026-09-24.
- Internet Archive (Wayback Machine): International Democrat Union: 6 buscas, coleta de 2026-09-24.
- Internet Archive (Wayback Machine): Organização Democrata Cristã da América: 4 buscas, coleta de 2026-09-24.
- Internet Archive (Wayback Machine): União de Partidos Latino-Americanos: 3 buscas, coleta de 2026-09-24.
- Itamaraty, Concórdia (atos internacionais), interface pública do site: 3 buscas, coleta de 2026-09-25.
- Nações Unidas, repositório oficial de documentos (resoluções do Conselho de Direitos Humanos): 109 buscas, coleta de 2026-09-25.
- OEA, atas das sessões plenárias da Assembleia Geral: 22 buscas, coleta de 2026-09-24.
- OEA, volumes de resoluções da Assembleia Geral: 25 buscas, coleta de 2026-09-24.
- OEA, volumes de resoluções da Assembleia Geral (download manual do autor, D-034): 5 buscas, coleta de 2026-09-24.
- ONU, UN Digital Library (download manual do autor, D-032): 1 buscas, coleta de 2026-09-24.
- Portal da Transparência (CGU), download de dados: 4 buscas, coleta de 2026-09-24.
- STF, Corte Aberta (exportação feita pelo autor no navegador, D-037): 14 buscas, coleta de 2026-09-26.
- Senado, dados abertos: 7 buscas, coleta de 2026-09-24.
- TSE, portal de dados abertos (download feito pelo autor no navegador, D-042): 34 buscas, coleta de 2026-09-25.
- TSE, página de partidos registrados (leitura no navegador, D-015): 1 buscas, coleta de 2026-09-24.
- V-Dem Institute, pacote vdemdata (GitHub, tag V16): 1 buscas, coleta de 2026-09-24.

### Lacunas medidas na etapa E1 (Câmara e Senado)

- Mandatos de suplente: 1132 de 4628 cargos. No Senado, o mandato de suplente não indica que houve exercício; na Câmara, o cargo de suplente só aparece quando há registro no histórico.
- Atores sem nenhuma filiação registrada: 235 de 2815; 209 deles só têm mandato de suplente no Senado, e o Senado não publica filiação para quem não exerceu.
- Filiações da Câmara cobrem só o período de mandato (fonte: histórico do deputado); fora do mandato, a filiação não é observada.
- Pares Câmara e Senado identificados como a mesma pessoa automaticamente: 115; pares ambíguos aguardando revisão: 0 (`data/curadoria/equivalencias_atores_pendentes.csv`). Até a revisão, cada lado é um ator separado.
- Partidos: 47 registros no TSE, com 67 denominações e 17 fusões ou incorporações (fonte: página de partidos do TSE, lida no navegador; D-015). A página cobre mudanças a partir da Lei 9.096/1995.
- Ligação de siglas das fontes ao partido na data: 6539 de 6850 na vigência da sigla; 299 com a sigla fora da vigência, mas com um único partido existente na data (fontes que gravam a sigla atual em registros antigos); 12 pela denominação mais próxima no tempo; 0 sem correspondência. Siglas ligadas pelo nome publicado pela fonte: SDD (SD SOLIDARIEDADE).

- Universo de partidos por ano: de 15 a 30 partidos (2003 a 2026).

### Réguas externas (etapa E2)

- `fh_status`: 196 países, de 2000 a 2024.
- `fh_total`: 195 países, de 2012 a 2024.
- `vdem_ldi`: 179 países, de 2000 a 2025.
- `vdem_row`: 179 países, de 2000 a 2025.
- Concordância entre as réguas na classificação "baixa qualidade democrática" (V-Dem RoW 0 ou 1; Freedom House Não Livre): 80,7% dos 4318 pares país-ano com as duas réguas. Os relatórios mostram as duas, sem combiná-las.
- A Freedom House não publicou abertamente a edição 2026 (ano de 2025): os dados passaram a ser atendidos por pedido por e-mail. O ano de 2025 só tem V-Dem.
- Países só no V-Dem: 5 (HKG, PSE, PSG, SML, ZZB). Países só na Freedom House: 22 (a maioria microestados que o V-Dem não cobre; inclui Sérvia e Montenegro, SCG, que o V-Dem registra como Sérvia). Códigos de país seguem o V-Dem (ISO 3166-1 alfa-3 quando existe); a ligação dos nomes da Freedom House está em `data/curadoria/paises_freedom_house.csv`.
- Os valores do V-Dem são estimativas de modelo com incerteza (intervalos publicados pelo V-Dem, não importados); valores próximos ao limiar entre categorias devem ser lidos com cautela.

### BNDES, operações de exportação (etapa E3)

- Pós-embarque, bens: 2344 linhas (subcréditos) de 1912 operações, contratadas de 2002-01-04 a 2026-07-31.
- Pós-embarque, serviços de engenharia: 652 linhas (subcréditos) de 146 operações, contratadas de 1998-07-24 a 2015-04-28.
- O arquivo aberto de pós-embarque de bens não publica valores (2344 linhas sem valor): para bens, só é possível contar operações.
- 82 linhas com destino "diversos", sem país definido.
- O nome do tomador do financiamento (mutuário) não é publicado; só a categoria (ente público ou privado).
- O arquivo de pré-embarque financia o exportador no Brasil e não informa o país de destino; fica só no dado bruto.
- Valores em moeda da operação, nominais, sem correção; linhas contratadas antes de 2000 não têm régua de qualidade democrática.
- As condições de garantia (seguro de crédito, Fundo de Garantia à Exportação, convênio de créditos recíprocos) aparecem só como texto do BNDES.

### STJ pelo DataJud (etapa E4)

- 205 ações penais e inquéritos do STJ na API pública do DataJud; 127 no universo do eixo 1 desde 2003 (tipos penais do protocolo, pela tabela `data/curadoria/assuntos_tpu_eixo1.csv`); 21 com assuntos genéricos, a revisar pela fonte primária.
- Cobertura histórica baixa: só 14 processos do universo autuados de 2003 a 2012. O DataJud concentra processos com movimentação recente; processos antigos e baixados podem não estar na base do CNJ. O universo do STJ anterior a 2013 está incompleto.
- A API pública só traz processos sem sigilo; processos sigilosos não aparecem.
- A API não traz nomes de partes, e o termo de uso impede cruzar seus dados com pessoas (D-022). Status de pessoas depende de fonte primária.
- O portal do STJ (consulta processual e jurisprudência) exige verificação de robô; a leitura da fonte primária de cada processo citado precisa ser feita por uma pessoa. A URL gravada segue o formato do portal e não foi conferida por script.
- Fases processuais: só declínio de competência e arquivamento de procedimento investigatório. O trânsito em julgado não foi usado, porque no STJ aparece a cada recurso interno encerrado.

### STF pelo Corte Aberta (etapa E5)

- 9862 processos (peticao: 4817, inquerito: 2598, acao_penal: 2447): ações penais e inquéritos com decisão de 08/01/2003 a 23/09/2026, petições de ramo penal com decisão de 05/02/2003 a 24/09/2026, e os em tramitação nas datas das exportações (D-037, D-045). No universo do eixo 1: 1441 (tipos do protocolo pelo assunto); 6043 a revisar; 2328 fora; 50 autuados antes de 2003.
- O Corte Aberta traz um só assunto por processo. Em 1.774 ações penais o assunto é o genérico "Direito Processual Penal | Ação Penal", e o tipo penal só aparece na fonte primária. Triagem pelo texto das decisões (não decide nada): sem_indicio: 4625; indicio_fora_do_protocolo: 1071; indicio_do_protocolo: 347. Os indícios de fora do protocolo vêm sobretudo das ações penais de 2023 a 2026 sobre crimes contra o Estado Democrático de Direito (CP, Título XII).
- Regra de assuntos em `data/curadoria/assuntos_stf_eixo1.csv` (D-038): capítulos do Título XI do Código Penal entram inteiros, como diz o protocolo (inclusive desobediência, desacato e sonegação de contribuição previdenciária); crimes eleitorais só entram como conexos (art. 350); crimes de responsabilidade de prefeitos (Decreto-Lei 201/1967) entram por emenda ao protocolo (D-039), também no STJ.
- Fases: 6554 registros de decisões com correspondência inequívoca (recebimento_denuncia: 2030; declinio_competencia: 1329; arquivamento_inquerito: 1286; acordao_tribunal_superior: 1073; extincao_punibilidade: 745; rejeicao_denuncia: 91). O julgamento de mérito da ação penal (procedente ou improcedente) é registrado sem distinguir réus; o status de cada pessoa depende da fonte primária.
- Petições criminais: o assunto costuma ser processual (investigação, prisão, busca e apreensão, quebra de sigilo) e não diz o crime; por isso a maioria fica a revisar. O arquivamento de petição investigativa é registrado com a fase de arquivamento de procedimento investigatório (vocabulário: arquivamento de inquérito).
- Decisões em segredo de justiça aparecem só como "Decisão (segredo de justiça)" e não geram fase. O campo de sigilo do processo não vem na exportação.
- A página de dados abertos do STF (bases de processos recebidos e baixados, com todos os assuntos de cada processo) corta as exportações em 5 milhões de células: os arquivos de cinco anos (2006 a 2025) chegam incompletos, em ordem alfabética de classe, sem inquéritos. Só os de 2026 estão completos e foram registrados; neles, 22 de 140 AP e Inq trazem mais de um assunto.
- Número único CNJ só para os processos em tramitação (planilha do acervo). A URL gravada é a consulta por classe e número do portal, conferida no navegador para a AP 470.

### Portal da Transparência (etapa E6)

- Acordos de leniência: 57 acordos da CGU. Sanções administrativas na base: 2240 (todas as do CNEP a pessoas jurídicas e, do CEIS, só as de empresas que já estão na base; o CEIS completo fica no dado bruto, D-027). Sanções a pessoas físicas não entram (LGPD).
- Emendas parlamentares: 92364 linhas (agregadas por emenda, localidade e função), de 2014 a 2026; o arquivo da CGU não traz anos anteriores a 2014.
- Emendas individuais: 9554 linhas sem autor na fonte; das 73747 com autor, 97,5% ligadas a um parlamentar da base (nome e mandato no ano). As demais têm grafia diferente (nome civil contra nome parlamentar) ou homônimos com mandato no mesmo ano.
- Emendas de relator: 3537 linhas, com autor publicado só como "RELATOR GERAL" ou sem informação; o arquivo não identifica os parlamentares que indicaram os recursos. Emendas de bancada e de comissão não têm autor individual.
- O arquivo de emendas por favorecido (com nomes de pessoas físicas) e o de convênios ficam só no dado bruto.

### Votos em organismos multilaterais (etapa E8, bloco A)

- Assembleia Geral da ONU: 101 resoluções adotadas por voto nominal de 2003 a 2025, com o voto de todos os países (19442 votos); critério em `docs/lista_e8_para_revisao.md`. direitos_humanos_pais: 77; cita_america_latina: 24.
- Resoluções adotadas sem votação (por consenso) e votos sobre parágrafos isolados não constam do conjunto da ONU.
- O critério "cita país da América Latina" é aplicado ao pé da letra e inclui resoluções de desenvolvimento; a análise separa pelo título.

- Conselho de Direitos Humanos: 149 resoluções adotadas por votação registrada de 2006 a 2026, com o voto de todos os membros (6950 votos); o Brasil votou em 122 (nos demais anos não era membro). Mesmo critério da Assembleia Geral; voto de cada país conferido com o placar escrito na resolução (D-044).
- Das 269 resoluções selecionadas, 111 foram adotadas sem votação e não geram voto por país; 8 não trazem o registro de adoção no texto lido; 1 com lista de votos que não bate com o placar do próprio documento ficam fora (A/HRC/RES/19/22).
- Lacunas de fonte: o relatório da 1ª sessão (2006, A/61/53) e as resoluções das sessões especiais S-13 e S-17 não estão no repositório de documentos da ONU; as sessões especiais S-1 a S-11 só entram quando estão nos relatórios anuais.

- Assembleia Geral da OEA: 31 resoluções ou votações na base (9 por votação registrada, 22 sem votação no plenário), de 2004 a 2024; curadoria item a item (`data/curadoria/oea_resolucoes_ag_curadoria.csv`): 33 incluídas, 34 excluídas e 0 aguardando decisão do autor (fora da base).
- Votações incluídas, localizadas nas atas: 10 (`data/curadoria/oea_votacoes.csv`); em 8 das 9 chamadas nominais a contagem das respostas bate com o placar oficial e entra o voto de cada país. Não bate em: 2018-06-05 (AG/RES. 2929 (XLVIII-O/18): placar 19/4/11, lidos 20/3/11); nesses casos só entra o voto do Brasil, lido na fala da delegação. A votação de mão erguida da AG/RES. 2 (XXXVII-E/09) (suspensão de Honduras, 4 de julho de 2009, 33 votos afirmativos) não individualiza os votos e não gera linha por país.
- Resolução sem chamada nominal na ata da sessão é registrada como adotada sem votação: `consenso` para o Brasil ou `consenso_com_nota` quando há nota de rodapé do país no texto certificado; os demais países só aparecem quando registraram nota. Votações na Comissão Geral (antes do plenário) não constam das atas lidas.
- A autoria da nota é o primeiro Estado membro citado no início dela; notas "Ídem" e "Véase nota N" herdam o autor. No volume de 2010 o leitor não traz as chamadas de nota, e a nota é ligada à resolução que cita o mesmo Estado no título.
- Notas de rodapé do Brasil nas resoluções incluídas: 0.
- Sem ata da sessão (download recusado pelo servidor da OEA: 2005, 2007, 2013, 2014 e 2015), não dá para dizer se houve votação; estas resoluções incluídas ficam fora da base: AG/DEC. 54 (XXXVII-O/07), AG/RES. 2306 (XXXVII-O/07), AG/RES. 2856 (XLIV-O/14), AG/RES. 2877 (XLV-O/15).
- Volumes de resoluções de 2003, 2005 e 2006 não foram obtidos (erro do servidor da OEA); o segundo arquivo da sessão extraordinária de 2009 veio do repositório de documentos da OEA, porque o link do índice recusa o acesso; resoluções do Conselho Permanente ainda não foram indexadas.

### Redes partidárias transnacionais (etapa E8, bloco D)

- 20 períodos de filiação ou observação de partidos brasileiros em 8 redes, lidos nas listas de membros publicadas pelas próprias redes, em cópias anuais do Internet Archive (D-040). As datas são a primeira e a última observação no arquivo, não as datas de filiação ou de saída; data final vazia quer dizer que o partido está na cópia de 2026.
- Cobertura desigual: o arquivo não tem lista de membros utilizável do Foro de São Paulo antes de 2014, da Internacional Socialista de 2003 a 2018 (as páginas antigas não trazem a lista no texto), da International Democrat Union de 2007 a 2017 (lista carregada por script, fora da cópia), da Aliança Progressista antes de 2014, da UPLA depois de 2003, nem da ODCA e da Internacional Democrata Centrista depois de 2016 e de 2013. Ausência de cópia não é ausência de filiação.
- Listas desatualizadas pela própria rede são registradas como estão (por exemplo, "PPS" no Foro de São Paulo depois da mudança para Cidadania; "Democratas" na International Democrat Union depois da fusão no União Brasil); a sigla é ligada ao partido do registro no TSE.
- Sem partido brasileiro nas listas lidas: Foro de Madri, Grupo de Puebla, União de Partidos Latino-Americanos. O Grupo de Puebla e o Foro de Madri reúnem pessoas; a participação de pessoas fica para etapa própria.
- Filiação a rede é relação política pública; o relatório não a liga a registros dos eixos 1 e 3.

### Atos bilaterais do Brasil (etapa E8, bloco B)

- 7720 atos bilaterais com um país como outra parte, de 1823 a 2026, com 190 países; 3101 celebrados de 2003 em diante (Concórdia, D-041).
- Fora da tabela: 576 atos bilaterais com organismos internacionais, 4 sem outra parte informada e 4191 atos trilaterais ou multilaterais.
- Data de entrada em vigor: 2575 dos 3101 atos de 2003 em diante (do detalhe de cada ato); atos anteriores a 2003 não tiveram o detalhe coletado. Ato sem data de vigência pode estar em tramitação, sem vigência registrada ou sem o campo preenchido no Concórdia.
- O Concórdia registra atos de naturezas diferentes (tratados, acordos, memorandos, ajustes complementares, troca de notas); a base guarda o título como publicado e não classifica relevância. Contagem de atos não mede intensidade de relação.
- Estados extintos entram com o código de antigo Estado (Iugoslávia, Alemanha Oriental). Nomes de signatários ficam só no dado bruto.

### TSE: candidatos e receitas de campanha (etapa E7)

- 12613 linhas de receita, somadas por candidato, eleição e tipo de doador, de 2002 a 2022 (eleições gerais ordinárias; presidente, governador eleito, senador eleito e deputado federal eleito; D-043).
- Deputados e senadores eleitos sem ligação única com o parlamentar da base, e por isso sem receitas na base, por eleição: 2002: 11, 2006: 10, 2010: 15, 2014: 11, 2018: 22, 2022: 10. A ligação é por nome, sem CPF; nomes de urna muito diferentes do nome parlamentar ficam de fora.
- Candidatos não eleitos a governador, senador e deputado federal, e todos os candidatos a cargos estaduais e municipais, ficam fora.
- Empresas: linha própria só para as 128 empresas já presentes na base (BNDES, CGU); as demais aparecem somadas por candidato. Pessoas físicas só em total por candidato. Doações de empresas foram proibidas a partir de 2015 (STF, ADI 4650).
- 2002: o arquivo não traz o tipo de receita; o tipo é deduzido do documento do doador (CPF ou CNPJ) e do nome (partido, comitê, próprio candidato). Até 2010, repasses de comitês e de outros candidatos aparecem como "partido", sem o doador originário.
- 2014: linhas `originario_via_partido` identificam o doador originário de recursos repassados por partido ou comitê; o valor já está contado na linha do repasse e não deve ser somado de novo.
- Receitas registradas são doações legais declaradas à Justiça Eleitoral; o registro não indica irregularidade.

### Casos-teste (etapa E9)

- Casos: Ação Penal 470 (caso conhecido como Mensalão), Ação Penal 536 (caso conhecido como Mensalão mineiro). Status formais registrados: 66 (reu: 40; condenado_tribunal_superior: 17; absolvido: 8; condenado_2a_instancia: 1), com fonte judicial ou oficial do STF (D-046).
- AP 470: o texto da decisão de 17/12/2012 vem cortado no portal, e o resultado por réu e por crime está espalhado em andamentos de agosto a dezembro de 2012, em trechos também cortados. Entraram só as condenações nomeadas em decisão do Tribunal (23/10/2012, quadrilha) ou em notícia oficial da fixação das penas (12 e 21/11/2012), e as absolvições por quadrilha nos embargos infringentes de 27/02/2014. Os demais resultados de 2012 ficam pendentes de leitura da fonte primária completa.
- Pendências conhecidas: condenação por quadrilha de Marcos Valério e José Roberto Salgado (a absolvição de 2014 está registrada, a condenação de 2012 não tem trecho com data); embargos infringentes sobre lavagem de 13/03/2014 (duas absolvições e uma rejeição) sem fonte oficial que nomeie cada embargante; extinção de punibilidade de 16/09/2010 sem o nome do réu; trânsitos em julgado por réu.
- AP 536 (Mensalão mineiro): o STF declinou da competência em 27/03/2014 e enviou o processo à Justiça estadual de Belo Horizonte sem julgamento de mérito; o desfecho está no TJMG e ainda não foi lido. O recebimento da denúncia não aparece nos andamentos do STF.
- Réus sem correspondência única com a base entram como ator novo, com tipo provisório; a ligação do réu Carlos Alberto Rodrigues Pinto ao deputado Carlos Rodrigues é decisão manual a conferir.
- Status de pessoas filiadas ainda sem verificação de simetria: aparecem como aviso do validador e não vão a relatório (D-007).

### Validador

- 0 falha(s) e 20 aviso(s) na última geração.
- Aviso: status_pessoa_processo: STA-000001 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000002 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000015 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000017 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000018 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000023 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000026 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000027 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000029 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000030 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000031 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000033 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000034 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000035 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000040 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000041 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000043 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000048 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000049 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)
- Aviso: status_pessoa_processo: STA-000066 envolve ator filiado e não tem verificação de simetria (bloqueia relatório)

<!-- FIM-GERADO -->
