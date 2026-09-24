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
| `instituicoes` | 1468 |
| `denominacoes_partido` | 67 |
| `processos` | 205 |
| `fases_processo` | 58 |
| `eventos` | 2297 |
| `relacoes` | 2409 |
| `fontes` | 17 |
| `fonte_oficial` | 14 |
| `fonte_base_dados` | 3 |
| `evento_fonte` | 2297 |
| `relacao_fonte` | 2409 |
| `buscas` | 34 |
| `universo_partidos` | 521 |
| `qualidade_democratica` | 16651 |
| `operacoes_exportacao_bndes` | 2996 |
| `emendas_parlamentares` | 92364 |

Tabelas ainda vazias (14): `casos`, `status_pessoa_processo`, `afirmacoes`, `fonte_judicial`, `fonte_legislativa`, `fonte_orcamentaria`, `fonte_jornalistica`, `afirmacao_fonte`, `verificacoes_simetria`, `verificacao_resultado`, `votos_multilaterais`, `acordos_bilaterais`, `decisoes_judiciais`, `doacoes_campanha`.

### Buscas

- 34 buscas registradas; 0 com zero resultados.
- BNDES, dados abertos (CKAN): 7 buscas, coleta de 2026-09-24.
- Câmara, API v2: 9 buscas, coleta de 2026-09-24.
- DataJud (CNJ), API pública, STJ: 3 buscas, coleta de 2026-09-24.
- Freedom House, planilhas históricas: 2 buscas, coleta de 2026-09-24.
- Portal da Transparência (CGU), download de dados: 4 buscas, coleta de 2026-09-24.
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

### Portal da Transparência (etapa E6)

- Acordos de leniência: 57 acordos da CGU. Sanções administrativas na base: 2240 (todas as do CNEP a pessoas jurídicas e, do CEIS, só as de empresas que já estão na base; o CEIS completo fica no dado bruto, D-027). Sanções a pessoas físicas não entram (LGPD).
- Emendas parlamentares: 92364 linhas (agregadas por emenda, localidade e função), de 2014 a 2026; o arquivo da CGU não traz anos anteriores a 2014.
- Emendas individuais: 9554 linhas sem autor na fonte; das 73747 com autor, 97,5% ligadas a um parlamentar da base (nome e mandato no ano). As demais têm grafia diferente (nome civil contra nome parlamentar) ou homônimos com mandato no mesmo ano.
- Emendas de relator: 3537 linhas, com autor publicado só como "RELATOR GERAL" ou sem informação; o arquivo não identifica os parlamentares que indicaram os recursos. Emendas de bancada e de comissão não têm autor individual.
- O arquivo de emendas por favorecido (com nomes de pessoas físicas) e o de convênios ficam só no dado bruto.

### Validador

- 0 falha(s) e 0 aviso(s) na última geração.

<!-- FIM-GERADO -->
