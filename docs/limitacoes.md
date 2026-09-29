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
| `atores` | 2861 |
| `filiacoes` | 6553 |
| `cargos` | 4657 |
| `instituicoes` | 1487 |
| `denominacoes_partido` | 67 |
| `casos` | 4 |
| `processos` | 10077 |
| `fases_processo` | 6639 |
| `status_pessoa_processo` | 88 |
| `eventos` | 2298 |
| `relacoes` | 2459 |
| `fontes` | 304 |
| `fonte_judicial` | 11 |
| `fonte_legislativa` | 1 |
| `fonte_oficial` | 289 |
| `fonte_base_dados` | 3 |
| `evento_fonte` | 2298 |
| `relacao_fonte` | 2509 |
| `buscas` | 795 |
| `verificacoes_simetria` | 94 |
| `verificacao_resultado` | 2017 |
| `universo_partidos` | 521 |
| `qualidade_democratica` | 16651 |
| `operacoes_exportacao_bndes` | 2996 |
| `votos_multilaterais` | 26696 |
| `acordos_bilaterais` | 7720 |
| `emendas_parlamentares` | 92364 |
| `doacoes_campanha` | 12613 |

Tabelas ainda vazias (5): `afirmacoes`, `fonte_orcamentaria`, `fonte_jornalistica`, `afirmacao_fonte`, `decisoes_judiciais`.

### Buscas

- 795 buscas registradas; 204 com zero resultados.
- BNDES, dados abertos (CKAN): 7 buscas, coleta de 2026-09-24.
- Base do projeto (relações 'indicou' da D-058): 33 buscas, coleta de 2026-09-29.
- Buscador web do ChatGPT (site:), relatado pelo agente: 60 buscas, coleta de 2026-09-29.
- ComexStat (MDIC), API pública e tabelas auxiliares: 3 buscas, coleta de 2026-09-28.
- Câmara dos Deputados, dados abertos: 2 buscas, coleta de 2026-09-29.
- Câmara dos Deputados, dados abertos (arquivos anuais): 48 buscas, coleta de 2026-09-28.
- Câmara, API v2: 9 buscas, coleta de 2026-09-24.
- DataJud (CNJ), API pública, STJ: 3 buscas, coleta de 2026-09-24.
- Ferramenta de busca na web do assistente (restrita ao domínio do veículo): 131 buscas, coleta de 2026-09-29.
- Freedom House, planilhas históricas: 2 buscas, coleta de 2026-09-24.
- Google (site:), via Claude in Chrome no navegador do autor, sem login: 60 buscas, coleta de 2026-09-29.
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
- Portal do STF (navegador embutido, mesma origem): 75 buscas, coleta de 2026-09-29.
- STF, Corte Aberta (exportação feita pelo autor no navegador, D-037): 24 buscas, coleta de 2026-09-29.
- STF, portal (aba Partes) e Corte Aberta (decisões): 74 buscas, coleta de 2026-09-28.
- STF, portal (aba Partes) e Corte Aberta (decisões); Câmara, orientações de bancada (D-050/D-051): 4 buscas, coleta de 2026-09-28.
- Senado, dados abertos: 12 buscas, coleta de 2026-09-29.
- TCU, Plataforma de Certidões (API pública): 4 buscas, coleta de 2026-09-29.
- TSE, portal de dados abertos (download feito pelo autor no navegador, D-042): 34 buscas, coleta de 2026-09-25.
- TSE, página de partidos registrados (leitura no navegador, D-015): 1 buscas, coleta de 2026-09-24.
- V-Dem Institute, pacote vdemdata (GitHub, tag V16): 1 buscas, coleta de 2026-09-24.

### Lacunas medidas na etapa E1 (Câmara e Senado)

- Mandatos de suplente: 1132 de 4657 cargos. No Senado, o mandato de suplente não indica que houve exercício; na Câmara, o cargo de suplente só aparece quando há registro no histórico.
- Atores sem nenhuma filiação registrada: 281 de 2861; 209 deles só têm mandato de suplente no Senado, e o Senado não publica filiação para quem não exerceu.
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

- 9866 processos (peticao: 4817, inquerito: 2598, acao_penal: 2447, habeas_corpus: 2, reclamacao: 2): ações penais e inquéritos com decisão de 08/01/2003 a 23/09/2026, petições de ramo penal com decisão de 05/02/2003 a 24/09/2026, e os em tramitação nas datas das exportações (D-037, D-045). No universo do eixo 1: 1441 (tipos do protocolo pelo assunto); 6047 a revisar; 2328 fora; 50 autuados antes de 2003.
- O Corte Aberta traz um só assunto por processo. Em 1.774 ações penais o assunto é o genérico "Direito Processual Penal | Ação Penal", e o tipo penal só aparece na fonte primária. Triagem pelo texto das decisões (não decide nada): sem_indicio: 4625; indicio_fora_do_protocolo: 1071; indicio_do_protocolo: 347. Os indícios de fora do protocolo vêm sobretudo das ações penais de 2023 a 2026 sobre crimes contra o Estado Democrático de Direito (CP, Título XII).
- Regra de assuntos em `data/curadoria/assuntos_stf_eixo1.csv` (D-038): capítulos do Título XI do Código Penal entram inteiros, como diz o protocolo (inclusive desobediência, desacato e sonegação de contribuição previdenciária); crimes eleitorais só entram como conexos (art. 350); crimes de responsabilidade de prefeitos (Decreto-Lei 201/1967) entram por emenda ao protocolo (D-039), também no STJ.
- Fases: 6562 registros de decisões com correspondência inequívoca (recebimento_denuncia: 2030; declinio_competencia: 1329; arquivamento_inquerito: 1286; acordao_tribunal_superior: 1073; extincao_punibilidade: 745; rejeicao_denuncia: 91; outra: 7; anulacao: 1). O julgamento de mérito da ação penal (procedente ou improcedente) é registrado sem distinguir réus; o status de cada pessoa depende da fonte primária.
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

- Casos: Ação Penal 470 (caso conhecido como Mensalão), Ação Penal 536 (caso conhecido como Mensalão mineiro), Operação Lava Jato: ação do triplex (5046512-94.2016.4.04.7000) e anulações no STF (HC 193726, HC 164493, Rcl 43007), Banco Master: apurações no STF (Inq 5026 e processos distribuídos por prevenção). Status formais registrados: 88 (reu: 40; condenado_tribunal_superior: 18; absolvido: 10; condenado_1a_instancia: 10; investigado: 4; condenado_2a_instancia: 3; condenacao_anulada: 2; processo_anulado: 1), com fonte judicial ou oficial (STF, STJ, TRF4, TJMG; D-046).
- Lava Jato (D-052): os processos-âncora ficam fora do universo coletado (primeira instância federal não foi coletada; HC e Rcl não entram na E5) e entram pela E9. Carregados: a ação do triplex (5046512-94.2016.4.04.7000), com os status de Luiz Inácio Lula da Silva de condenação (primeira e segunda instâncias e STJ) seguidos da condenação anulada (HC 193726, 08/03/2021) e do processo anulado (HC 164493, 23/03/2021); a ação do sítio de Atibaia com a condenação em primeira instância (fevereiro de 2019, dia não informado), a confirmação no TRF4 (27/11/2019) e a condenação anulada (08/03/2021); as duas ações do Instituto Lula só com a anulação e a remessa à Justiça Federal do DF (sem sentença lida); a ação 5026212-82.2014.4.04.7000 (Refinaria Abreu e Lima) com oito condenados e dois absolvidos em 22/04/2015 (réus sem mandato na base); a Rcl 43007 com a decisão de 06/09/2023 sobre as provas da Odebrecht. O desfecho na Justiça Federal do DF depois de abril de 2021 não foi localizado. Fontes: notícias oficiais do TRF4, da JFPR, do STJ e do STF. A consulta processual não pôde ser usada: em 29/09/2026 o eproc da JFPR e o do TRF4 exibiam "A consulta pública está desativada.", a consulta unificada do TRF4 pedia CAPTCHA (não resolvido) e o PJe público do TRF1 contava resultados sem exibi-los (relatório no bruto). Ficaram sem leitura as ações 5083401-18.2014 e 5083258-29.2014 e o inquérito 5049557-14.2013. A data do julgamento do Plenário de 15/04/2021 diverge no próprio texto da notícia ("quinta-feira (14)").
- A anulação de provas da Rcl 43007 foi estendida a pessoas de partidos diferentes (Paulo Bernardo, 19/06/2023; Sérgio Cabral e Gilberto Kassab, 02/08/2023; fontes registradas); as ações penais dessas pessoas não foram carregadas. A Lava Jato que correu no próprio STF está no universo da E5 (por exemplo, AP 996 e AP 1003) e entrou na verificação de simetria.
- Banco Master (D-052): Inq 5026 e processos distribuídos por prevenção estão no universo do STF, com assunto processual ("revisar" no eixo 1); no Inq 5026 os investigados não aparecem na aba Partes. Entraram como investigados os quatro nomes da decisão de 04/03/2026 que decretou prisões preventivas (pessoas sem cargo público na base). A decisão de 03/04/2026 sobre Ibaneis Rocha Barros Júnior trata da condição de investigado atribuída pela CPI do Crime Organizado e não informa inclusão no inquérito do STF: entrou como fase do processo, não como status. Decisões sigilosas e petições sem partes não foram lidas.
- AP 470: o texto da decisão de 17/12/2012 vem cortado no portal, e o resultado por réu e por crime está espalhado em andamentos de agosto a dezembro de 2012, em trechos também cortados. Entraram só as condenações nomeadas em decisão do Tribunal (23/10/2012, quadrilha) ou em notícia oficial da fixação das penas (12 e 21/11/2012), e as absolvições por quadrilha nos embargos infringentes de 27/02/2014. Os demais resultados de 2012 ficam pendentes de leitura da fonte primária completa.
- Pendências conhecidas: condenação por quadrilha de Marcos Valério e José Roberto Salgado (a absolvição de 2014 está registrada, a condenação de 2012 não tem trecho com data); embargos infringentes sobre lavagem de 13/03/2014 (duas absolvições e uma rejeição) sem fonte oficial que nomeie cada embargante; extinção de punibilidade de 16/09/2010 sem o nome do réu; trânsitos em julgado por réu.
- AP 536 (Mensalão mineiro): o STF declinou da competência em 27/03/2014 e enviou o processo à Justiça estadual de Belo Horizonte sem julgamento de mérito. O recebimento da denúncia não aparece nos andamentos do STF.
- AP 536 no TJMG (ação penal 2378231-34.2014.8.13.0024, 9ª Vara Criminal de Belo Horizonte): o processo é sigiloso na consulta processual ("Processo sigiloso — acesso restrito"); as fases vêm de acórdãos públicos de outros processos que o citam e do agravo interno de 2019, que nomeia o réu. Duas notícias oficiais do TJMG divergem sobre a data da sentença de primeira instância (dezembro de 2015 na notícia de 01/08/2017; abril de 2016 na de 07/04/2017); por isso a condenação em primeira instância não tem status próprio, e o primeiro status registrado é a confirmação em segunda instância (22/08/2017). Os embargos infringentes citados no agravo interno não têm número nem data nas páginas lidas. Trânsito em julgado, execução da pena e fatos após 10/07/2019 não aparecem nas páginas públicas do TJMG; a pesquisa antiga de jurisprudência pede CAPTCHA, que não foi resolvido.
- Os processos da AP 536 dos demais réus, desmembrados no TJMG, não foram levantados.
- Réus sem correspondência única com a base entram como ator novo, com tipo provisório; a ligação do réu Carlos Alberto Rodrigues Pinto ao deputado Carlos Rodrigues é decisão manual a conferir.
- Status de pessoas filiadas ainda sem verificação de simetria: aparecem como aviso do validador e não vão a relatório (D-007).

### Verificação de simetria dos status da E9

- 94 verificações, 2017 resultados por grupo (nao_verificado: 714; sem_evidencia: 675; encontrado: 628).
- Universo lido: lotes 1, 2, 3, 4, 5, 6, 7 de D-048 (660 de 660 ações penais do STF, fora 8 de janeiro; o lote 1 reúne as 99 julgadas no mérito); os réus vêm da aba Partes lida no navegador. Linhas que não são nome de pessoa (órgão do Ministério Público no campo de réu, "OS MESMOS"), empresas (LTDA, ME, EPP), entes públicos (município) e nomes só com iniciais ficam fora. Ação sem réu rotulado (queixa-crime, com querelante e querelado) não entra na lista de réus. Com todos os lotes lidos, os status de réu têm verificação própria (padrão de réu, abaixo).
- Padrão de condenação: contam só ações com assunto do eixo 1 pela regra da E5 e com condenação de ao menos um réu (Procedente ou Procedente em parte), partido na data do primeiro julgamento de mérito. Padrão de réu: todas as ações do eixo 1 em que o parlamentar é réu, partido na data de autuação da ação; ação penal no STF não mostra quando cada pessoa passou a réu. O status de denunciado não tem padrão lido (denúncia oferecida fica no inquérito, fora da lista de ações penais). O resultado por réu não foi lido: em ação com mais de um réu, o parlamentar pode ter sido absolvido. Ações com assunto classificado como crime contra o sistema financeiro, falsidade ou crime eleitoral ficam fora ou em "revisar", conforme a regra da E5; partido só com ações em "revisar" fica `nao_verificado`, com a lista das ações.
- Ligação réu -> parlamentar pelo nome e pelo mandato no período da ação. A Câmara só publica o nome civil em arquivos que também trazem CPF, que o projeto não guarda (D-011); por isso a ligação usa o nome parlamentar, com decisões manuais e motivo em `data/curadoria/simetria_stf_ap_ligacoes.csv`. Ligação que se apoia só no prenome, ou no prenome e num nome do meio, entra como `aceita_a_conferir` quando nenhum outro parlamentar da base tem esse nome; prenome compartilhado é rejeitado; nome comum em ação com muitos réus fica `pendente`.
- Partido é contado pela instituição exata da filiação na data; fusões e incorporações (por exemplo, PL antigo e PL atual) não são somadas.
- Governo e oposição (D-050, D-051): na primeira versão das verificações ficaram `nao_verificado`; a segunda versão, datada, classifica o partido do réu na data do caso pelas orientações de bancada no Plenário da Câmara (concordância com o Governo de 2/3 ou mais: base; abaixo de 1/2: oposição). A classificação mede alinhamento em votação, não participação formal na coalizão (ministérios); orientação de liderança não é o voto de cada deputado; o Senado não entra. Blocos são decompostos pelo nome (D-051), o que amplia a cobertura mas atribui a orientação do bloco a cada membro; a partir de 2023 blocos grandes juntam partidos de posições diferentes. A regra sem blocos fica em coluna própria para comparação.
- Taxa por bancada (D-049, `relatorios/tabelas/simetria_taxa_bancada.csv`): suplentes de senador ficam fora do denominador e do numerador, porque a base só os lista, sem o período em que exerceram o mandato; parlamentares ligados a réus que só aparecem como suplentes de senador não entram na taxa. A queda da taxa a partir da legislatura 56 acompanha a restrição do foro por prerrogativa de função no STF (maio de 2018), não uma mudança medida de conduta; a comparação entre partidos usa as legislaturas 52 a 55. Os intervalos de 95% se sobrepõem para a maior parte dos partidos: diferenças pequenas entre taxas não são distinguíveis com esses números. O intervalo supõe pares independentes, o que não vale quando o mesmo parlamentar aparece em várias legislaturas.
- O status de Eduardo Azeredo no TJMG fica `nao_verificado` em todos os grupos: não há universo lido de ações penais estaduais.

### Eixo 2: métricas por governo (D-053)

- Votos: o Brasil só vota no Conselho de Direitos Humanos quando é membro, e o número de resoluções por governo varia com isso e com a agenda de cada ano. O país-alvo sai do título por regra; nas resoluções sobre território ocupado, o alvo é a potência ocupante ou agressora (Rússia na Ucrânia, Israel no Território Palestino Ocupado). A comparação com democracias e com a América Latina é a média do voto desses países nas mesmas resoluções. Voto em organismo multilateral é posição do Estado (Poder Executivo), não de partido.
- Baixa qualidade democrática: Freedom House até 2024 e V-Dem até 2025; atos e operações de 2025-2026 ficam sem classificação pela Freedom House (136 dos 314 acordos do governo iniciado em 2023).
- BNDES: o arquivo aberto não publica valor nas operações de exportação de bens (2.344); só as de serviços de engenharia (652, em dólar) têm valor, e não há operação desse tipo depois de 2015. A comparação por valor cobre só os governos de 2003 a 2016; a comparação entre todos os governos usa a contagem de operações. Parte das operações antigas não tem país de destino identificado.
- Linha de base comercial (D-054): exportações do ComexStat por país e mês (cada mês no governo em exercício no dia 15). A parcela exportada para países BQD é dominada pela China (de 6% a 30% das exportações), e a tendência reflete sobretudo o crescimento desse comércio; no governo iniciado em 2023, 47% do valor exportado fica sem classificação porque a Freedom House vai só até 2024. A comparação com o BNDES é de parcelas, não de valores: o BNDES financia uma fração pequena e específica das exportações.
- Redes partidárias: as datas são as da primeira e da última cópia arquivada da página de cada rede (Wayback, D-040), não as datas de filiação; filiações anteriores à primeira cópia (por exemplo, fundadores de uma rede) aparecem com a data da cópia.

### Contraste com a imprensa (D-055, D-056)

- Painel: 10 veículos em uso. Sem acesso pela ferramenta de busca: Folha de S.Paulo, O Estado de S. Paulo, O Globo, Valor Econômico, BBC News Brasil; só uma reserva (Revista Oeste) tinha acesso. O painel não é uma amostra da imprensa brasileira, e a ausência de jornais impressos de circulação nacional é a maior lacuna.
- A unidade é o título devolvido pela ferramenta de busca restrita ao domínio (até 10 links por consulta fixa). `sem_resultado` quer dizer que a matéria não apareceu nesses links, não que o veículo não a publicou: a ordem e o índice são da ferramenta, não do arquivo do veículo, e o critério de ordenação da ferramenta não é conhecido.
- CNN Brasil e Revista Oeste não têm matéria sobre nenhum dos 7 fatos anteriores a 2020 nos resultados; comparações entre fatos de épocas diferentes devem excluir esses veículos.
- Assimetria de cobertura observada: TJMG confirma a condenação de Eduardo Azeredo (F03, 2017) aparece em 1 de 10 veículos em uso (1 de 8 sem os veículos acima); TRF4 confirma a condenação de Lula no triplex (F05, 2018), em 7 de 10 (7 de 8). Vários veículos devolveram títulos sobre fases posteriores do caso Azeredo (ordem de prisão, STJ, embargos). O desenho não separa as causas possíveis (termos da consulta, ordem da ferramenta, projeção nacional do réu, tribunal estadual ou federal) e não permite atribuir a diferença a linha editorial.
- Divergências: 1 (F10 Poder360). O critério é o título; matéria cujo título não informa o desfecho conta como `mencao_sem_resultado`, mesmo que o texto o informe.
- Os esclarecimentos da régua em D-056 foram feitos durante a classificação, depois de ver os títulos, e valem para todas as linhas.

#### Principais sem acesso: relatórios de navegação (D-057)

- Coletas usadas: Google pelo Claude in Chrome (chrome_google) e buscador do ChatGPT (chatgpt_busca). Buscas bloqueadas: chatgpt_busca BBC News Brasil: 12; chatgpt_busca O Estado de S. Paulo: 12; chatgpt_busca O Globo: 12; chatgpt_busca Valor Econômico: 12; chrome_google BBC News Brasil: 12; chrome_google Valor Econômico: 5. A BBC News Brasil ficou sem nenhuma busca concluída. O relatório do Gemini está no bruto e fora da classificação.
- O buscador muda o resultado. Na Folha, a única coberta pelas duas coletas, elas divergem sobre haver matéria da decisão em 7 dos 12 fatos (F01, F02, F03, F06, F07, F11, F12). Em F03 (Azeredo, TJMG) o Google não devolveu nenhum resultado e o outro buscador pôs a matéria da decisão em primeiro. `sem_resultado` mede o buscador tanto quanto o veículo, e a assimetria F03 × F05 do painel principal não deve ser lida como diferença de cobertura dos veículos.
- Pelo Google, nos 4 jornais com acesso, F03 tem matéria em 0 de 4 e F05 em 2 de 4.
- Estadão: a regra de D-055 exclui URL de blog, e a cobertura judicial do jornal está sob /blog-do-fausto-macedo/. Há matéria em 5 de 12 fatos pela regra e em 7 incluindo blogs.
- O Google às vezes mostra um título diferente do título da página (reescrita do buscador). A unidade continua sendo o título devolvido; quando o corte do buscador escondia o desfecho, valeu o título completo lido no navegador.

### Eixo 1 ampliado: candidatos, TSE e TCU (D-060, D-061)

- Universo: 107113 candidaturas das eleições gerais de 2010 a 2022 (um registro por sequencial do TSE); eleições municipais fora.
- TSE: 448 de 58415 candidaturas de 2018 e 2022 indeferidas ou cassadas por motivo do eixo 1; 705 sem a exclusão dos casos de lista (D-061: em 2022, quase todo "abuso de poder político" acompanha fraude à cota de gênero no DRAP, que atinge a lista). O TSE não publica o arquivo de motivos de 2010, e o de 2014 tem 10 linhas: a medida não cobre esses anos. O arquivo não traz a data da decisão; usa-se a do primeiro turno.
- TCU: 568 candidaturas com conta julgada irregular (trânsito em julgado) até o primeiro turno; 1284 em qualquer data. A lista do TCU concentra gestores de recursos federais, sobretudo ex-prefeitos: partidos com mais candidatos que já foram gestores têm mais exposição, e a taxa não separa exposição de conduta. Ligação só por CPF igual no TSE e no TCU; CPF ausente no TSE deixa o candidato sem ligação.
- Governo/oposição: grupo do partido na data da eleição pela regra de D-050 (orientação de bancada na Câmara); partidos sem votações suficientes ficam sem classificação.
- Homogeneidade entre partidos: estatística qui-quadrado com p exato por simulação (válido com contagens pequenas), só partidos com pelo menos 30 candidaturas no recorte.

### Composição do STF (D-058)

- 29 ministros em exercício em algum dia desde 2003, das páginas "Dados e Datas" da Biblioteca do STF. As páginas têm erros: Flávio Dino, data_posse: lido 2011-03-03, usado 2024-02-22 (noticia_stf_528119.html); Maurício Corrêa, data_decreto_nomeacao: lido 2004-10-27, usado 1994-10-27 (biografia_33.html); Teori Zavascki, data_fim: lido (vazio), usado 2017-01-19 (noticia_stf_500851.html); Teori Zavascki, motivo_fim: lido (vazio), usado falecimento (noticia_stf_500851.html).
- Vaga citada no decreto de nomeação diferente da citada na mensagem de indicação: Luís Roberto Barroso (mensagem: Carlos Augusto Ayres de Freitas Britto; decreto: Antonio Cezar Peluso); André Mendonça (mensagem: Marco Aurélio Mendes de Farias Mello; decreto: Aurélio Mendes de Farias Mello). A tabela usa a mensagem; nenhuma data depende disso.
- Datas de fim: aposentadoria = data de início do decreto ("a partir de") ou, sem ela, a data do decreto; falecimento = biografia ou notícia oficial. As relações `indicou` usam a data da mensagem de indicação. A indicação rejeitada de 2026 usa a data de apresentação no Senado, porque a mensagem presidencial não traz o dia nas fontes coletadas.
- Partido do presidente (D-059): partido do registro de candidatura no TSE para o mandato em curso, não a filiação no dia. Jair Bolsonaro foi eleito pelo PSL (2018) e aparece como PSL em todo o mandato 2019-2022, inclusive nas indicações de 2020 e 2021; a filiação no dia, se usada, exige fonte própria.

### Validador

- 0 falha(s) e 0 aviso(s) na última geração.

<!-- FIM-GERADO -->
