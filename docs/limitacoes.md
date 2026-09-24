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
| `instituicoes` | 55 |
| `fontes` | 6 |
| `fonte_oficial` | 6 |
| `buscas` | 16 |
| `universo_partidos` | 521 |

Tabelas ainda vazias (23): `casos`, `processos`, `fases_processo`, `status_pessoa_processo`, `eventos`, `relacoes`, `afirmacoes`, `fonte_judicial`, `fonte_legislativa`, `fonte_orcamentaria`, `fonte_jornalistica`, `fonte_base_dados`, `evento_fonte`, `relacao_fonte`, `afirmacao_fonte`, `verificacoes_simetria`, `verificacao_resultado`, `qualidade_democratica`, `operacoes_exportacao_bndes`, `votos_multilaterais`, `acordos_bilaterais`, `decisoes_judiciais`, `doacoes_campanha`.

### Buscas

- 16 buscas registradas; 0 com zero resultados.
- Câmara, API v2: 9 buscas, coleta de 2026-09-24.
- Senado, dados abertos: 7 buscas, coleta de 2026-09-24.

### Lacunas medidas na etapa E1 (Câmara e Senado)

- Mandatos de suplente: 1132 de 4628 cargos. No Senado, o mandato de suplente não indica que houve exercício; na Câmara, o cargo de suplente só aparece quando há registro no histórico.
- Atores sem nenhuma filiação registrada: 210 de 2703; 209 deles só têm mandato de suplente no Senado, e o Senado não publica filiação para quem não exerceu.
- Filiações da Câmara cobrem só o período de mandato (fonte: histórico do deputado); fora do mandato, a filiação não é observada.
- Pares Câmara e Senado identificados como a mesma pessoa automaticamente: 115; pares ambíguos aguardando revisão: 0 (`data/curadoria/equivalencias_atores_pendentes.csv`). Até a revisão, cada lado é um ator separado.
- Partidos identificados por sigla: 53. Fusões, mudanças de nome e reutilização de sigla (por exemplo, a mesma sigla usada por partidos diferentes em épocas diferentes) ainda não foram revisadas.

- Universo de partidos por ano: de 15 a 30 partidos (2003 a 2026).

### Validador

- 0 falha(s) e 0 aviso(s) na última geração.

<!-- FIM-GERADO -->
