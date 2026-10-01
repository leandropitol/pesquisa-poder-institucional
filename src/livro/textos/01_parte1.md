# Parte I — Como observar a transformação

Antes de descrever qualquer mudança é preciso dizer o que foi observado, com que regra e com que limite. Esta parte trata do objeto do estudo, dos universos de cada base, do caminho de um número desde a fonte até o gráfico, das definições usadas e dos cuidados estatísticos.

## 1. Objeto, pergunta e período

O estudo examina as relações entre agentes do Executivo, do Legislativo e do Judiciário brasileiros, de qualquer partido, e o modo como recursos públicos e privados circulam entre eles, de 2003 até a data da coleta, setembro de 2026. Os anos de 2000 a 2002 entram apenas como contexto, nas séries que os têm.

O protocolo do projeto, fixado em 24 de setembro de 2026 antes da coleta, estabelece o que o estudo não faz: não atribui culpa sem decisão judicial; não trata denúncia, colaboração premiada ou reportagem como prova; não trata ausência de evidência como indício nem como inocência demonstrada; não infere motivo a partir de coincidência de datas; e não classifica governos estrangeiros por critério próprio, usando as réguas do V-Dem e da Freedom House lado a lado.

A unidade de registro nos dados judiciais é o processo, e não uma narrativa sobre ele. O partido de uma pessoa é sempre a filiação na data do fato, e nunca a atual. Toda medida que envolve partidos é repetida para todos os partidos do universo daquele ano, e não apenas para os que aparecem num caso.

## 2. Universos, populações e amostras

As bases do livro não têm a mesma natureza. Algumas cobrem o universo completo do que pretendem medir; outras cobrem um universo recortado por regra; outras são seleções temáticas. Essa diferença decide o que cada número pode dizer.

[[tab:t_universos]]

Três consequências atravessam o livro. As receitas de campanha cobrem apenas quem foi eleito (e os candidatos a presidente), e por isso não dizem nada sobre o custo de perder uma eleição. As votações em organismos multilaterais são uma seleção de resoluções sobre países e temas de democracia, e não toda a política externa. E as ações penais cobrem os processos originários no Supremo: o que acontece depois que uma ação deixa o tribunal não é observado.

[[fig:n01]]

### Critérios de inclusão e exclusão

Os critérios foram registrados como decisão metodológica antes do cálculo de cada medida. Quando um esclarecimento foi feito depois de ver os dados, a própria decisão o declara (por exemplo, D-051, D-061 e D-067). Para a primeira versão do livro foram fixadas cinco decisões novas: a publicação do repositório (D-069), as séries externas e a regra de deflação (D-070), a estrutura do livro e o tratamento de nomes (D-071), a separação entre mudanças de partido individuais e por fusão (D-072) e o índice de número efetivo de partidos (D-073). O núcleo analítico da Parte VII acrescentou mais cinco, fixadas antes do cálculo, com um ajuste declarado: as regras do painel, das janelas e da matriz (D-074), as hipóteses e a escala de evidência (D-075), a ligação entre deputados e candidaturas (D-076), a extensão do IPCA de junho a 2002 (D-077) e os controles do teste de reeleição, definidos depois da primeira execução (D-078).

## 3. Da fonte ao gráfico

Cada número do livro passa por cinco etapas: a fonte primária, isto é, o órgão que produziu o dado; o arquivo bruto, guardado como foi baixado, com seu sha256 registrado num manifesto; a base canônica em CSV, em que cada linha aponta para a fonte; o tratamento do autor (ligação entre arquivos, filtros, somas, deflação); e o resultado derivado, que é o indicador que aparece no gráfico.

[[fig:n02]]

As fichas distinguem quatro camadas. A **fonte primária** é o órgão que originalmente produziu o dado. A **fonte secundária** é uma base ou publicação que o reorganizou, quando houver. O **tratamento do autor** é a limpeza, agregação, filtragem, cruzamento ou cálculo feito para este estudo. O **resultado derivado** é o indicador calculado. Um cálculo próprio nunca é apresentado como dado produzido pela instituição original.

Parte dos arquivos brutos não pôde ser obtida por programa, porque alguns portais recusam clientes automatizados. Nesses casos o autor baixou ou exportou os arquivos no próprio navegador, e o sha256 foi gravado no manifesto (D-009, D-015, D-037). As séries do IBGE usadas no livro foram lidas na resposta da interface pública do instituto por uma ferramenta de leitura web, pela mesma razão, e estão marcadas para conferência por download direto (D-070).

## 4. Definições e réguas

**Status de pessoa.** É a situação processual formal de uma pessoa em um processo, num vocabulário fechado: investigado, denunciado, réu, absolvido, condenado em determinada instância, prescrição reconhecida, punibilidade extinta, condenação anulada, contas julgadas irregulares, representado, mandato cassado e outros. O status vigente é o de data mais recente. Cada mudança é uma linha nova, com fonte judicial ou oficial.

**Nível de confiança.** Um registro é "documentado" quando há fonte judicial, legislativa, orçamentária, oficial ou base de dados de pesquisa; "sob investigação" quando a fonte trata de procedimento sem decisão de mérito; e "alegado" quando só há jornalismo, declarações ou colaboração premiada. Este livro usa apenas registros documentados.

**Partido, governo e oposição.** O partido é a filiação na data do fato, com fusões, incorporações e mudanças de nome segundo o registro no TSE (D-016). Um partido é classificado como alinhado ao governo quando concordou com a orientação do governo em dois terços ou mais das votações nominais do Plenário da Câmara no período, e como de oposição quando concordou em menos da metade (D-050, D-051). A medida é de alinhamento em votação, não de participação formal na coalizão.

**Baixa qualidade democrática.** Um país é classificado assim quando a Freedom House o considera "Não Livre" ou o V-Dem o classifica como autocracia fechada ou eleitoral, no ano do fato. As duas réguas são mostradas lado a lado e nunca combinadas (D-003, D-053).

**Valores nominais e reais.** Os valores das fontes são nominais. Quando o livro compara anos distantes, mostra também valores em reais de agosto de 2026, corrigidos pelo IPCA: receitas de campanha pelo índice de outubro do ano da eleição e fluxos anuais pelo índice de junho do ano (D-070). Os valores nominais continuam visíveis ao lado. Valores em dólar (BNDES) não são corrigidos.

## 5. Estatística sem falsa precisão

O projeto usa poucos métodos, todos simples. Proporções têm intervalo de confiança de 95% de Wilson; quando os intervalos se sobrepõem, as taxas não podem ser distinguidas. A homogeneidade entre partidos é testada por qui-quadrado com valor p exato por simulação, válido com contagens pequenas. Comparações entre dois grupos usam o teste exato de Fisher. A associação com a posição ideológica usa a correlação de Spearman com valor p por permutação.

O relatório final do projeto traz 119 testes, dos quais 35 têm p abaixo de 0,05; ao acaso, sem correção, se esperariam cerca de seis. Os testes não são independentes, porque os mesmos partidos entram em recortes vizinhos. Por isso o livro só valoriza diferenças que se repetem em recortes diferentes, e trata a ausência de diferença em amostras pequenas como "os dados não distinguem", nunca como igualdade.

[[tab:t_testes]]

Duas análises do material anterior foram trazidas para cá como exemplos de falsa precisão. A primeira compara a taxa de condenação por ministro relator no STF: são de 2 a 12 julgamentos por ministro, e os intervalos de 95% cobrem quase toda a escala. A segunda compara a arrecadação de campanha de eleitos que depois tiveram ação penal no STF com a dos demais: o resultado não tem direção estável entre eleições e o grupo inclui absolvidos. Nenhuma das duas sustenta conclusão.

[[fig:c19]]

::: permite
- Dizer o que cada base cobre, com a regra que definiu o universo e a data em que foi fixada. ●
- Reproduzir cada número a partir dos arquivos e scripts do repositório. ●
:::

::: nao_permite
- Tratar ausência de registro como ausência de fato: sigilo, lacunas de fonte e universos recortados limitam o que aparece. ●
- Comparar ministros, partidos ou governos com amostras de poucas dezenas de casos como se a diferença fosse estável. ◐
:::
