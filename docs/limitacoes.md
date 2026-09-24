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
| `atores` | 2703 |
| `filiacoes` | 6329 |
| `cargos` | 4628 |
| `instituicoes` | 1471 |
| `denominacoes_partido` | 67 |
| `processos` | 5250 |
| `fases_processo` | 5256 |
| `eventos` | 2297 |
| `relacoes` | 2409 |
| `fontes` | 47 |
| `fonte_oficial` | 44 |
| `fonte_base_dados` | 3 |
| `evento_fonte` | 2297 |
| `relacao_fonte` | 2409 |
| `buscas` | 90 |
| `universo_partidos` | 521 |
| `qualidade_democratica` | 16651 |
| `operacoes_exportacao_bndes` | 2996 |
| `votos_multilaterais` | 19746 |
| `emendas_parlamentares` | 92364 |

Tabelas ainda vazias (13): `casos`, `status_pessoa_processo`, `afirmacoes`, `fonte_judicial`, `fonte_legislativa`, `fonte_orcamentaria`, `fonte_jornalistica`, `afirmacao_fonte`, `verificacoes_simetria`, `verificacao_resultado`, `acordos_bilaterais`, `decisoes_judiciais`, `doacoes_campanha`.

### Buscas

- 90 buscas registradas; 14 com zero resultados.
- BNDES, dados abertos (CKAN): 7 buscas, coleta de 2026-09-24.
- Câmara, API v2: 9 buscas, coleta de 2026-09-24.
- DataJud (CNJ), API pública, STJ: 3 buscas, coleta de 2026-09-24.
- Freedom House, planilhas históricas: 2 buscas, coleta de 2026-09-24.
- OEA, atas das sessões plenárias da Assembleia Geral: 22 buscas, coleta de 2026-09-24.
- OEA, volumes de resoluções da Assembleia Geral: 25 buscas, coleta de 2026-09-24.
- OEA, volumes de resoluções da Assembleia Geral (download manual do autor, D-034): 5 buscas, coleta de 2026-09-24.
- ONU, UN Digital Library (download manual do autor, D-032): 1 buscas, coleta de 2026-09-24.
- Portal da Transparência (CGU), download de dados: 4 buscas, coleta de 2026-09-24.
- STF, Corte Aberta (exportação feita pelo autor no navegador, D-037): 3 buscas, coleta de 2026-09-24.
- Senado, dados abertos: 7 buscas, coleta de 2026-09-24.
- TSE, página de partidos registrados (leitura no navegador, D-015): 1 buscas, coleta de 2026-09-24.
- V-Dem Institute, pacote vdemdata (GitHub, tag V16): 1 buscas, coleta de 2026-09-24.

### Lacunas medidas na etapa E1 (Câmara e Senado)

- Mandatos de suplente: 1132 de 4628 cargos. No Senado, o mandato de suplente não indica que houve exercício; na Câmara, o cargo de suplente só aparece quando há registro no histórico.
- Atores sem nenhuma filiação registrada: 210 de 2703; 209 deles só têm mandato de suplente no Senado, e o Senado não publica filiação para quem não exerceu.
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

- 205 ações penais e inquéritos do STJ na API pública do DataJud; 124 no universo do eixo 1 desde 2003 (tipos penais do protocolo, pela tabela `data/curadoria/assuntos_tpu_eixo1.csv`); 21 com assuntos genéricos, a revisar pela fonte primária.
- Cobertura histórica baixa: só 14 processos do universo autuados de 2003 a 2012. O DataJud concentra processos com movimentação recente; processos antigos e baixados podem não estar na base do CNJ. O universo do STJ anterior a 2013 está incompleto.
- A API pública só traz processos sem sigilo; processos sigilosos não aparecem.
- A API não traz nomes de partes, e o termo de uso impede cruzar seus dados com pessoas (D-022). Status de pessoas depende de fonte primária.
- O portal do STJ (consulta processual e jurisprudência) exige verificação de robô; a leitura da fonte primária de cada processo citado precisa ser feita por uma pessoa. A URL gravada segue o formato do portal e não foi conferida por script.
- Fases processuais: só declínio de competência e arquivamento de procedimento investigatório. O trânsito em julgado não foi usado, porque no STJ aparece a cada recurso interno encerrado.

### STF pelo Corte Aberta (etapa E5)

- 5045 ações penais e inquéritos: os que tiveram decisão de 08/01/2003 a 23/09/2026 e os em tramitação na data da exportação (D-037). No universo do eixo 1: 912 (tipos do protocolo pelo assunto); 2556 a revisar; 1533 fora; 44 autuados antes de 2003.
- O Corte Aberta traz um só assunto por processo. Em 1.774 ações penais o assunto é o genérico "Direito Processual Penal | Ação Penal", e o tipo penal só aparece na fonte primária. Triagem pelo texto das decisões (não decide nada): sem_indicio: 1358; indicio_fora_do_protocolo: 910; indicio_do_protocolo: 288. Os indícios de fora do protocolo vêm sobretudo das ações penais de 2023 a 2026 sobre crimes contra o Estado Democrático de Direito (CP, Título XII).
- Regra de assuntos em `data/curadoria/assuntos_stf_eixo1.csv` (D-038): capítulos do Título XI do Código Penal entram inteiros, como diz o protocolo (inclusive desobediência, desacato e sonegação de contribuição previdenciária); crimes eleitorais só entram como conexos (art. 350); crimes de responsabilidade (Decreto-Lei 201/1967) ficam fora, como no STJ.
- Fases: 5198 registros de decisões com correspondência inequívoca (recebimento_denuncia: 1630; acordao_tribunal_superior: 1073; declinio_competencia: 1052; extincao_punibilidade: 699; arquivamento_inquerito: 653; rejeicao_denuncia: 91). O julgamento de mérito da ação penal (procedente ou improcedente) é registrado sem distinguir réus; o status de cada pessoa depende da fonte primária.
- Decisões em segredo de justiça aparecem só como "Decisão (segredo de justiça)" e não geram fase. O campo de sigilo do processo não vem na exportação.
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
- Resoluções sobre países da América Latina no Conselho de Direitos Humanos (bloco A2) ainda não entraram.

- Assembleia Geral da OEA: 31 resoluções ou votações na base (9 por votação registrada, 22 sem votação no plenário), de 2004 a 2024; curadoria item a item (`data/curadoria/oea_resolucoes_ag_curadoria.csv`): 33 incluídas, 34 excluídas e 0 aguardando decisão do autor (fora da base).
- Votações incluídas, localizadas nas atas: 10 (`data/curadoria/oea_votacoes.csv`); em 8 das 9 chamadas nominais a contagem das respostas bate com o placar oficial e entra o voto de cada país. Não bate em: 2018-06-05 (AG/RES. 2929 (XLVIII-O/18): placar 19/4/11, lidos 20/3/11); nesses casos só entra o voto do Brasil, lido na fala da delegação. A votação de mão erguida da AG/RES. 2 (XXXVII-E/09) (suspensão de Honduras, 4 de julho de 2009, 33 votos afirmativos) não individualiza os votos e não gera linha por país.
- Resolução sem chamada nominal na ata da sessão é registrada como adotada sem votação: `consenso` para o Brasil ou `consenso_com_nota` quando há nota de rodapé do país no texto certificado; os demais países só aparecem quando registraram nota. Votações na Comissão Geral (antes do plenário) não constam das atas lidas.
- A autoria da nota é o primeiro Estado membro citado no início dela; notas "Ídem" e "Véase nota N" herdam o autor. No volume de 2010 o leitor não traz as chamadas de nota, e a nota é ligada à resolução que cita o mesmo Estado no título.
- Notas de rodapé do Brasil nas resoluções incluídas: 0.
- Sem ata da sessão (download recusado pelo servidor da OEA: 2005, 2007, 2013, 2014 e 2015), não dá para dizer se houve votação; estas resoluções incluídas ficam fora da base: AG/DEC. 54 (XXXVII-O/07), AG/RES. 2306 (XXXVII-O/07), AG/RES. 2856 (XLIV-O/14), AG/RES. 2877 (XLV-O/15).
- Volumes de resoluções de 2003, 2005 e 2006 não foram obtidos (erro do servidor da OEA); o segundo arquivo da sessão extraordinária de 2009 veio do repositório de documentos da OEA, porque o link do índice recusa o acesso; resoluções do Conselho Permanente ainda não foram indexadas.

### Validador

- 0 falha(s) e 0 aviso(s) na última geração.

<!-- FIM-GERADO -->
