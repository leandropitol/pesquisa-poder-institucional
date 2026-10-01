# Parte VII — Núcleo analítico: o que se transformou, quando e com que evidência

As partes II a VI descreveram cada dimensão separadamente. Esta parte faz uma pergunta mais ampla: é possível identificar, nos dados brasileiros de 2003 a 2026, transformações sistêmicas na distribuição de dinheiro, recursos públicos, poder institucional e capacidade de decisão entre partidos, Executivo, Legislativo, Judiciário e demais instituições?

A resposta não foi presumida. Antes de qualquer cálculo novo, as regras de cada teste, os limiares e os critérios de cada veredito foram registrados nas decisões D-074 a D-076. Assim o resultado não pode empurrar a regra. Ao longo da parte, cada afirmação é posta num de três níveis e classificada por uma escala de evidência. Nenhum resultado aqui tem o grau de causalidade demonstrada.

## 34. Como esta parte testa a pergunta

### Três níveis

- **Nível 1, o que aconteceu.** Descrição cronológica de cada série, sem comparação entre elas.
- **Nível 2, o que se moveu junto.** Simultaneidades, mudanças no mesmo sentido e em sentidos opostos, acelerações e reversões. Mover-se junto não significa que uma série tenha provocado a outra.
- **Nível 3, o que pode explicar o movimento.** Hipóteses, cada uma com a evidência disponível, as limitações e uma classificação.

### A escala de evidência

- **Evidência direta.** Um documento oficial estabelece a relação, como o texto de uma lei, de uma emenda constitucional ou de uma decisão judicial que muda a regra observada.
- **Evidência associativa.** Há associação estatística ou temporal medida no livro, mas não demonstração causal.
- **Hipótese.** A relação é plausível, mas não foi medida.
- **Não determinável.** Os dados disponíveis não permitem concluir.

A escala se soma às marcas de grau usadas no restante do livro (● fato, ◐ cálculo, ⇄ correlação, ? hipótese, ◇ interpretação).

### Regras fixadas antes do cálculo

- **Painel.** O painel reúne {{n7_series:d0}} séries anuais em {{n7_dimensoes_painel:d0}} dimensões, todas tiradas das bases já descritas ou derivadas delas (D-074). A décima dimensão, o comércio exterior, só tem dados por mandato e entra apenas na matriz. Série eleitoral só existe em ano de eleição, e nenhum valor é interpolado.
- **Janelas.** As sete janelas de inflexão propostas como hipótese de trabalho (2003–05, 2008–10, 2013–15, 2016–18, 2019–20, 2021–22 e 2023–26) são testadas com uma regra única.
  - A variação de uma série numa janela é a última observação dentro dela menos a última antes dela, dividida pelo desvio-padrão da própria série.
  - A mudança é relevante quando esse valor chega a 1 em módulo.
  - Uma janela indica um ambiente comum quando pelo menos metade das séries observadas nela tem mudança relevante.
- **Matriz.** A matriz sistêmica compara médias de seis períodos. Marca alta ou queda quando a diferença para o período anterior passa de meio desvio-padrão da série.
- **Hipóteses.** As quatro hipóteses têm testes e critérios de veredito escritos antes (D-075). A ligação entre deputados e candidaturas segue D-076.
- **Ajustes depois da primeira execução.** Os controles do modelo de reeleição tiveram de ser trocados, porque a receita de campanha só existe para quem se elegeu (D-078). Uma revisão independente do texto levou a outros ajustes, registrados em D-079: o teste log-rank previsto para o foro passou a ser calculado, o critério da taxa de reeleição foi declarado, e só conta como evidência direta o documento que o projeto leu.

::: nota
Os limiares são relativos à variabilidade de cada série. Uma série quase estável pode ter uma variação pequena em termos absolutos marcada como alta ou queda. O texto aponta esses casos.
Há muitos testes nesta parte, e nenhum é corrigido para comparações múltiplas. Com {{h4_n:d0}} testes de trocas de governo, por exemplo, cerca de um resultado com p < 0,05 seria esperado ao acaso.
Os seis períodos da matriz coincidem com mandatos presidenciais, e o de 2015–18 contém dois governos. Por isso a matriz não separa o tempo do governo.
:::

## 35. Nível 1 — O que aconteceu

O painel mostra cada série padronizada pela própria média e pelo próprio desvio-padrão: vermelho acima da média da série, azul abaixo, cinza sem observação. As linhas tracejadas marcam os anos de troca de governo. A tabela seguinte informa a dimensão, a unidade, a cobertura e a fonte primária de cada série. A tabela anual completa está no Atlas.

[[fig:n30]]

[[tab:t_painel2_fontes]]

**Financiamento eleitoral.** A parcela de empresas no dinheiro dos deputados eleitos caiu ao longo de três eleições: {{pv.emp.2002:d1}}% em 2002, {{pv.emp.2010:d1}}% em 2010 e {{pv.emp.2014:d1}}% em 2014. Em 2018 e em 2022 foi zero. ● Os fundos eleitorais públicos, inexistentes até 2014, responderam por {{pv.fundo.2018:d1}}% em 2018 e {{pv.fundo.2022:d1}}% em 2022. ● Os repasses de partidos subiram até {{pv.part.2014:d1}}% em 2014 e caíram para {{pv.part.2022:d1}}% em 2022. ● Os recursos próprios caíram de {{pv.prop.2002:d1}}% para {{pv.prop.2022:d1}}%. ● O Gini das receitas caiu de {{pv.gini.2014:d3}} em 2014 para {{pv.gini.2022:d3}} em 2022. ◐

**Recursos públicos.** A despesa total da União, em reais de agosto de 2026, passou de R$ {{pv.desp.2003:d0}} bilhões em 2003 para R$ {{pv.desp.2014:d0}} bilhões em 2014. Ficou perto desse nível até 2019, saltou para R$ {{pv.desp.2020:d0}} bilhões em 2020 e voltou a R$ {{pv.desp.2021:d0}} bilhões em 2021. Em 2025 foi de R$ {{pv.desp.2025:d0}} bilhões. ◐ O fundo eleitoral pago pelo Tesouro foi de R$ {{pv.fefc.2018:d1}} bilhões em 2018 e de R$ {{pv.fefc.2022:d1}} bilhões em 2022, em valores reais. ◐

**Emendas parlamentares.** O valor pago passou de R$ {{pv.em_real.2017:d1}} bilhões em 2017 para R$ {{pv.em_real.2025:d1}} bilhões em 2025, em valores reais, e de {{p3_pct_despesa_total.2017:d2}}% para {{p3_pct_despesa_total.2025:d2}}% da despesa total. ◐ A parcela sem autor parlamentar individual identificado foi de {{h2_semautor_2019:d1}}% em 2019, {{h2_semautor_2022:d1}}% em 2022 e {{h2_semautor_2025:d1}}% em 2025. ◐ As transferências especiais, criadas em 2019, chegaram a {{h2_te_max:d1}}% do valor pago em {{h2_te_max_ano}}. ◐

**Execução orçamentária.** A despesa discricionária do Executivo era {{pv.disc_pct.2008:d1}}% da despesa total em 2008, primeiro ano da série. Caiu para {{pv.disc_pct.2020:d1}}% em 2020 e ficou em {{pv.disc_pct.2025:d1}}% em 2025. ◐ A execução das emendas, medida como pago sobre empenhado, subiu de {{pv.exec.2017:d1}}% em 2017 para {{pv.exec.2024:d1}}% em 2024. ◐

**Partidos.** O número efetivo de partidos na Câmara subiu de {{pv.nep.2003:d1}} em 2003 para {{pv.nep.2019:d1}} em 2019 e caiu para {{pv.nep.2023:d1}} em 2023. ◐ As mudanças individuais de partido têm picos irregulares. O maior foi em 2022, ano de janela partidária, com {{pv.trocas.2022:d0}}. ● As cadeiras da base do governo foram {{pv.base.2010:d0}}% em 2010 e {{pv.base.2025:d0}}% em 2025. ◐ Entre os deputados que concorreram de novo à Câmara, a reeleição foi de {{h1_reeleicao.2006:d1}}% em 2006, {{h1_reeleicao.2014:d1}}% em 2014, {{h1_reeleicao.2018:d1}}% em 2018 e {{h1_reeleicao.2022:d1}}% em 2022. ◐

**STF.** As ações penais com réu parlamentar em curso na Corte chegaram a {{pv.estoque.max:d0}} no fim de {{pv.estoque.anomax}}. Eram {{pv.estoque.2017:d0}} em 2017, {{pv.estoque.2018:d0}} em 2018 e {{pv.estoque.2022:d0}} em 2022. ◐ Os declínios de competência têm picos nos inícios de legislatura de 2011 e 2015 e em 2018. ●

**Controle administrativo.** As sanções a empresas registradas pela CGU passaram de {{pv.sanc.2015:d0}} em 2015 para {{pv.sanc.2025:d0}} em 2025. Essa série mede também a adesão de órgãos ao cadastro. ● As contas julgadas irregulares pelo TCU envolvendo pessoas da base chegaram ao máximo em {{pv.tcu.anomax}}, com {{pv.tcu.max:d0}} decisões. ● As representações nos Conselhos de Ética têm seu maior número em {{pv.etica.anomax}}, com {{pv.etica.max:d0}}. ●

**Política externa e comércio.** Os atos bilaterais chegaram a {{pv.atos.2010:d0}} em 2010 e caíram para {{pv.atos.2020:d0}} em 2020. ● As exportações para países classificados como Não Livres pela Freedom House passaram de {{h4_comercio.2003–06:d1}}% no mandato de 2003–06 para {{h4_comercio.2023–26:d1}}% no de 2023–26. ◐ A parcela de votos do Brasil a favor de resoluções de escrutínio de direitos humanos varia de ano a ano, conforme os países examinados. ●

**Indicadores democráticos.** O índice de democracia liberal do V-Dem para o Brasil ficou entre {{pv.vdem.2005:d2}} e {{pv.vdem.2014:d2}} de 2005 a 2014. Caiu para {{pv.vdem.2019:d2}} em 2019 e voltou a {{pv.vdem.2025:d2}} em 2025. ● A pontuação da Freedom House caiu de {{pv.fh.2012:d0}} em 2012 para {{pv.fh.2022:d0}} em 2022. ●

### A matriz sistêmica

A matriz resume cada dimensão por um indicador e seis períodos. Cada célula traz a média do período e o sentido em relação ao período anterior. Das sessenta células, {{n7_matriz_sem_cobertura:d0}} ficam sem cobertura, a maioria por causa das emendas, que só têm dados consistentes desde 2017. As células sem cobertura foram mantidas em branco, e nenhum valor foi estimado para preenchê-las.

[[fig:n33]]

[[tab:t_matriz]]

A versão completa da matriz, com todas as séries, mostra quantas mudam de nível (alta ou queda) em relação ao período anterior. ◐

- 2007–10: {{n7_matriz_pct.2007–10:d0}}% das séries observadas.
- 2011–14: {{n7_matriz_pct.2011–14:d0}}%.
- 2015–18: {{n7_matriz_pct.2015–18:d0}}%.
- 2019–22: {{n7_matriz_pct.2019–22:d0}}%.
- 2023–26: {{n7_matriz_pct.2023–26:d0}}%.

Mudanças de nível são comuns em todos os períodos. A diferença está na proporção, maior a partir de 2015.

[[tab:t_matriz_completa]]

::: permite
- As mudanças de nível mais visíveis no painel estão no financiamento eleitoral (2018), nas emendas (2020, e de novo em 2024), no número de partidos (alta até 2019 e queda em 2023), no conjunto de ações com parlamentar no STF (queda em 2018) e no índice V-Dem (queda até 2019 e recuperação em 2023). ◐
- As exportações para países Não Livres crescem de um mandato ao seguinte até 2019–22 e ficam estáveis em 2023–26. ◐
:::

::: nao_permite
- Comparar a magnitude de séries diferentes pela cor do painel. A cor mostra a posição de cada ano dentro da própria série. ◇
- Atribuir a mudança de um período ao governo do período. Na matriz, período e mandato coincidem. ◇
:::

## 36. Nível 2 — O que se moveu junto

A figura seguinte mostra, para cada série e cada janela, a variação em desvios-padrão. As mudanças relevantes estão marcadas com ▲ (alta) ou ▼ (queda).

[[fig:n31]]

Há {{n7_rel_total:d0}} mudanças relevantes entre os pares de série e janela com observação: {{n7_rel_alta:d0}} altas e {{n7_rel_queda:d0}} quedas. ◐ Pela regra fixada antes, só a janela de {{t_janelas_comuns}} reúne pelo menos metade das séries observadas com mudança relevante ({{n7_janelas.2016–18.rel:d0}} de {{n7_janelas.2016–18.obs:d0}}). ◐ Ela passa no limite, com exatamente metade, e {{n7_1618_eleitorais:d0}} dessas mudanças são de séries eleitorais, que só podem mudar em janelas com eleição. Com um limiar um pouco mais exigente, nenhuma janela passaria. ◇ Em proporção das séries observadas, as janelas seguintes são:

- 2019–20: {{n7_janelas.2019–20.rel:d0}} de {{n7_janelas.2019–20.obs:d0}} séries observadas.
- 2008–10: {{n7_janelas.2008–10.rel:d0}} de {{n7_janelas.2008–10.obs:d0}}.

As de 2003–05 e 2013–15 têm a menor proporção, {{n7_janelas.2003–05.pct:d0}}% e {{n7_janelas.2013–15.pct:d0}}%. ◐

[[fig:n32]]

**Movimentos no mesmo sentido.** Em 2016–18, várias séries mudam juntas ⇄:

- caem a parcela de empresas, a dos repasses de partidos e a concentração das receitas;
- cai o número de ações com parlamentar em curso no STF;
- caem os dois indicadores internacionais de democracia (V-Dem e Freedom House);
- cai a taxa de reeleição.

Em 2019–20 sobem juntos a escala das emendas e a parcela sem autor individual, enquanto cai o peso das despesas discricionárias do Executivo. ⇄

**Movimentos em sentidos opostos.** Alguns pares são o mesmo fenômeno visto por dois lados. A queda das empresas e a alta dos fundos públicos em 2016–18 descrevem uma troca de fonte. ◇ A queda do número de ações no STF e a alta da sua idade mediana descrevem um conjunto que encolhe e envelhece. ◇ Outros pares não têm ligação medida. É o caso da alta da base do governo, em 2016–18, junto com a queda da reeleição. ⇄

**Acelerações e reversões.** A regra marca {{n7_aceleracoes_n:d0}} acelerações e {{n7_reversoes_n:d0}} reversões. ◐ Entre as acelerações estão a queda da parcela de empresas em 2016–18 e a alta da execução das emendas em 2021–22. Entre as reversões estão as mudanças de partido, que alternam altas e quedas com o calendário das janelas partidárias, e a despesa total, que volta em 2021–22 depois do salto de 2020. ●

**Duração.** Das mudanças relevantes, {{n7_dur.persistente:d0}} persistem na janela seguinte e {{n7_dur.revertida:d0}} se revertem. Outras {{n7_dur.sem observação posterior:d0}} ainda não têm observação posterior. ◐

**O que fica fora das janelas.** Em {{n7_fora_janelas_n:d0}} séries, a maior variação anual cai em anos que as janelas não cobrem: {{t_fora_janelas}}. ◐ As janelas captam a maior parte das grandes mudanças, mas não todas.

### O que não se moveu

Ao lado das mudanças, há regularidades que atravessam todo o período. ●

- Parte dos partidos permaneceu no grupo alinhado ao governo sob presidentes de partidos diferentes (capítulo 24).
- A saída das ações penais do STF acompanha o fim dos mandatos em todos os inícios de legislatura observados (capítulo 18).
- A saúde foi o principal destino das emendas em todos os anos observados, entre {{h2_saude_min:d0}}% e {{h2_saude_max:d0}}% do valor pago (capítulo 14).
- O Brasil se absteve na maioria das votações sobre o Irã em todos os períodos presidenciais (capítulo 29).
- Pessoas físicas responderam, em todas as eleições, por uma parcela entre um décimo e um quinto do dinheiro dos eleitos (capítulo 6).

::: permite
- Identificar 2016–18 como a única janela em que pelo menos metade das séries observadas muda de modo relevante, pela regra fixada antes do cálculo. ◐
- Afirmar que há mudanças relevantes em todas as janelas com dados e que as séries não mudam todas no mesmo ano. ◐
:::

::: nao_permite
- Concluir que as séries que mudam juntas responderam a uma mesma causa. ◇
- Tratar o limiar de um desvio-padrão como fronteira natural entre mudança e estabilidade. Ele é uma convenção declarada. ◇
:::

## 37. Pontos de inflexão

As janelas foram propostas como hipótese. O teste mostra que elas não têm o mesmo peso. ◐

- **2016–18.** Única janela que passa no critério de ambiente comum, no limite. As mudanças abrangem financiamento, partidos, STF, controle administrativo, política externa e indicadores democráticos.
- **2008–10 e 2019–20.** Inflexões parciais, com {{n7_janelas.2008–10.pct:d0}}% e {{n7_janelas.2019–20.pct:d0}}% das séries observadas em mudança relevante. Em 2008–10 elas estão sobretudo no financiamento e nos partidos; em 2019–20, no orçamento e no STF.
- **2003–05.** Não se sustenta como inflexão ampla. Poucas séries estão observadas, e só uma muda.
- **2013–15.** Também não se sustenta como inflexão ampla. As mudanças estão sobretudo no sistema partidário e nos declínios do STF, que seguem o calendário dos mandatos, além da queda das operações do BNDES.
- **2021–22 e 2023–26.** Têm mudanças setoriais: a janela partidária, o fundo eleitoral, a execução das emendas, a reconcentração partidária, a ausência de emendas de relator no arquivo a partir de 2023 e a alta das sanções.

A tabela de inflexões, em página horizontal, reúne para cada janela a mudança observada, os indicadores, as fontes, a magnitude, a duração, as possíveis explicações, a evidência e as limitações. A mudança observada, a magnitude e a duração saem da regra de D-074. As explicações e a classificação da evidência foram redigidas depois do cálculo, com a escala de D-075. A lista completa das mudanças relevantes, série por série, está no Atlas.

[[paisagem]]

[[tab:t_inflexoes]]

[[retrato]]

Boa parte das explicações com evidência direta remete a normas datadas. A linha do tempo abaixo mostra as que tratam de financiamento, orçamento, partidos e controle. Dos {{p7_marcos_n:d0}} marcos, {{p7_marcos_2015_2019:d0}} estão entre 2015 e 2019, o mesmo intervalo da única janela de ambiente comum e da inflexão parcial seguinte. ●

[[fig:n21]]

[[tab:t_marcos]]

::: permite
- Tratar 2016–18 como o principal ponto de inflexão do período pela regra adotada, com 2008–10 e 2019–20 como inflexões parciais. ◐
- Associar várias inflexões a normas datadas que mudaram a regra medida. ⇄
:::

::: nao_permite
- Tratar as janelas como ciclos. Os intervalos entre as inflexões não se repetem com regularidade, e cada inflexão envolve séries diferentes. ◇
- Afirmar que as normas foram a única causa das mudanças que as seguem. ◇
:::

## 38. Hipótese 1 — Do financiamento privado aos mecanismos públicos?

**Hipótese testada:** à medida que determinadas fontes privadas de financiamento eleitoral perderam espaço, mecanismos públicos e institucionais de distribuição de recursos ganharam importância na competição política. A frase foi tratada como hipótese, não como conclusão.

A regra de D-075 tem três passos.

1. A hipótese só pode valer se a parcela de empresas cair e a de fundos públicos subir.
2. Se isso acontecer, ela é testada também na competição: pela taxa de reeleição (alta em 2018 e em 2022 frente a 2014, critério declarado em D-079) e pela associação entre emendas recebidas e reeleição.
3. Ela só é sustentada como associação se todos os testes apontarem no mesmo sentido.

[[tab:t_h1]]

A primeira parte da hipótese se confirma. O dinheiro dos deputados eleitos deixou de vir de empresas e passou a vir sobretudo de fundos públicos. A troca de fonte segue normas datadas e lidas pelo projeto: a Lei 13.165/2015 revogou o artigo da Lei 9.504/1997 que tratava das doações de pessoas jurídicas, e a Lei 13.487/2017 criou o fundo eleitoral. ● A decisão do STF de 2015 sobre o mesmo tema está com a referência a confirmar. As receitas também ficaram menos concentradas, e o total real caiu. ◐

A segunda parte não se confirma com estes dados.

- **Reeleição.** A taxa entre os deputados que concorreram de novo à Câmara não subiu depois da mudança. Foi de {{h1_reeleicao.2014:d1}}% em 2014, {{h1_reeleicao.2018:d1}}% em 2018 e {{h1_reeleicao.2022:d1}}% em 2022. ◐
- **Emendas e reeleição.** A associação muda de sinal entre as eleições. Em 2018, quem recebeu mais emendas pagas em 2017–18 se reelegeu menos, com coeficiente de Spearman de {{h1_modelo.2018.rho:d2}} e p = {{h1_modelo.2018.p_spearman:d3}}. Em 2022, quem recebeu mais em 2019–22 se reelegeu mais, com coeficiente de {{h1_modelo.2022.rho:d2}} e p = {{h1_modelo.2022.p_spearman:d3}}. ⇄
- **Controle pela base do governo.** Quando se controla se o deputado estava na base, a associação perde significância nas duas eleições. Em 2022, a razão de chances é {{h1_modelo.2022.or_em:d2}} e p = {{h1_modelo.2022.p_em:d2}}. ⇄

[[fig:n34]]

[[tab:t_h1_quartis]]

[[tab:t_h1_modelo]]

A escala ajuda a situar a pergunta, mas não a responde. Em 2019–22 foram pagos R$ {{h1_emendas_leg56_bi:d1}} bilhões em emendas, em valores reais. Isso é cerca de {{h1_razao_emendas_campanha:d0}} vezes o dinheiro de campanha de todos os deputados eleitos em 2022. ◐ A escala mostra quanto passa pelo mecanismo, e não se esse dinheiro é usado na competição eleitoral.

**Veredito pela regra de D-075: {{h1_veredito}}.** Os dados sustentam a troca de fonte do financiamento. Não sustentam a afirmação de que mecanismos públicos tenham ganhado importância na competição política, pelo menos na medida usada aqui, que é a reeleição para a Câmara. ◇

::: nota
O teste de reeleição cobre os deputados que puderam ser ligados à candidatura pelo nome: {{h1_lig_pct.2018:d0}}% dos que estavam em exercício em 2018 e {{h1_lig_pct.2022:d0}}% em 2022. Quem disputou outro cargo fica fora.
O valor pago de emendas individuais depende da execução e de quem exerceu o mandato. A base não registra licenças nem o tempo efetivo de exercício.
As emendas de relator e de comissão não têm autor individual e não entram no teste.
:::

::: permite
- Afirmar que as empresas saíram do financiamento dos deputados eleitos e que os fundos públicos passaram a responder pela maior parte dele, por regra formal. ●
- Afirmar que a taxa de reeleição não subiu depois da mudança e que a associação entre emendas e reeleição não é estável entre 2018 e 2022. ◐
:::

::: nao_permite
- Afirmar que emendas garantem reeleição ou que deixaram de influenciar eleições. ◇
- Afirmar que o dinheiro dos partidos antes de 2018 era público. A origem desses repasses não é separável. ◇
:::

## 39. Hipótese 2 — Emendas: mais dinheiro ou outro instrumento?

**Hipótese testada:** o aumento das emendas parlamentares representa apenas crescimento quantitativo do orçamento parlamentar ou também uma transformação qualitativa da capacidade do Legislativo de direcionar recursos públicos?

Pela regra de D-075, houve mudança de natureza se pelo menos duas dimensões além da escala mudaram de forma documentada. Cada dimensão foi comparada em três triênios (2017–19, 2020–22 e 2023–25), com o critério de meio desvio-padrão.

[[fig:n35]]

[[tab:t_h2]]

**Escala.** O valor pago passou de R$ {{pv.em_real.2017:d1}} bilhões em 2017 para R$ {{pv.em_real.2024:d1}} bilhões em 2024 e R$ {{pv.em_real.2025:d1}} bilhões em 2025, em valores reais. A razão entre emendas pagas e despesas discricionárias do Executivo foi de {{p3_razao_discricionarias.2017:d1}}% em 2017 e {{p3_razao_discricionarias.2025:d1}}% em 2025. ◐

As demais dimensões mudaram assim:

- **Modalidades.** Há três mudanças de composição. As emendas de relator foram {{h2_relator_2020:d1}}% do pago em 2020 e desapareceram a partir de 2023. As transferências especiais existem desde 2020. As emendas de comissão foram {{h2_comissao_2024:d1}}% em 2024. ●
- **Autoria.** A parcela sem autor individual acompanha o peso das emendas de relator: alta em 2017 e de 2020 a 2022, baixa em 2018–2019 e a partir de 2023. Foi de {{h2_semautor_2022:d1}}% em 2022 e {{h2_semautor_2023:d1}}% em 2023. ◐
- **Rastreabilidade.** A parcela sem UF de destino foi de {{h2_semuf_2019:d1}}% em 2019, {{h2_semuf_2022:d1}}% em 2022 e {{h2_semuf_2023:d1}}% em 2023. ◐
- **Execução.** A relação entre pago e empenhado subiu de {{h2_exec_2017:d1}}% em 2017 para {{h2_exec_2024:d1}}% em 2024. Para as emendas individuais e de bancada, a execução se tornou obrigatória pelas Emendas Constitucionais 86/2015 e 100/2019. ●
- **Destino.** A saúde perdeu peso relativo, sem deixar de ser o principal destino. ◐
- **Território.** A desigualdade per capita entre UF, medida pelo Gini, foi de {{pv.em_giniuf.2017:d2}} em 2017, caiu para {{pv.em_giniuf.2022:d2}} em 2022 e ficou em {{pv.em_giniuf.2025:d2}} em 2025. ◐
- **Partido do autor.** A média de emendas individuais pagas a autores da base ficou entre {{h2_razao_min:d2}} e {{h2_razao_max:d2}} vezes a dos autores de fora da base. ◐ A regra marca essa série como variável, mas a diferença absoluta entre os triênios é pequena. Ela só aparece porque a série quase não varia. ◇

**Veredito pela regra de D-075: {{h2_veredito}}.** A mudança de natureza tem evidência direta em dois pontos: a execução obrigatória (EC 86/2015 e EC 100/2019) e a criação das transferências especiais (EC 105/2019). ● A mudança de modalidades e a parcela paga sem autor individual identificado entre 2020 e 2022 são fatos observados no arquivo da CGU. ●

O que os dados não determinam é quem decidiu o destino dessas emendas sem autor. Também não determinam se a mudança representa mais poder do Legislativo ou outra forma de negociação entre Legislativo e Executivo. As duas leituras são hipóteses. ?

::: permite
- Afirmar que as emendas cresceram e também mudaram de forma: modalidades, autoria registrada, rastreabilidade do destino e obrigatoriedade de execução. ●
- Afirmar que a diferença entre autores da base e de fora dela, nas emendas individuais, é pequena em todos os anos. ◐
:::

::: nao_permite
- Atribuir as emendas sem autor a parlamentares ou partidos determinados. ◇
- Medir, com estes dados, a capacidade do Legislativo de decidir o destino final do recurso. ◇
:::

## 40. Hipótese 3 — Foro e permanência na Corte

**Hipótese testada:** a transformação do foro e da competência do STF alterou a composição e a duração do conjunto de processos que permanecem na Corte?

O teste só usa o que os dados permitem. Para isso, conta quantas ações com réu parlamentar estão em curso ao fim de cada ano, de onde elas vieram, que idade têm e quanto tempo duram, por coorte de autuação (D-075).

[[fig:n36]]

[[tab:t_h3]]

**Tamanho.** O conjunto de ações em curso caiu de {{pv.estoque.2017:d0}} no fim de 2017 para {{pv.estoque.2018:d0}} no fim de 2018, o ano em que o STF restringiu o foro [REFERÊNCIA A CONFIRMAR: acórdão da AP 937]. ◐ A entrada de ações novas também caiu: foram {{h3_autuadas_2011_2017:d0}} autuadas em 2011–2017 e {{h3_autuadas_2019_2025:d0}} em 2019–2025. ◐

**Composição.** As ações autuadas no próprio STF eram {{h3_pct_stf_2017:d0}}% do conjunto em curso em 2017 e passaram a {{h3_pct_stf_2019:d0}}% em 2019. ◐

**Idade.** A idade mediana do conjunto subiu de {{h3_idade_2017:d1}} anos em 2017 para {{h3_idade_2020:d1}} anos em 2020. ◐

**Duração.** A duração mediana foi de {{h3_med_pre:d2}} anos na coorte autuada até 02/05/2018, com {{h3_n_pre:d0}} ações, e de {{h3_med_pos:d2}} anos na coorte autuada depois, com {{h3_n_pos:d0}} ações. O teste log-rank previsto em D-075 aponta duração menor na coorte nova (p {{h3_logrank_txt}}), e a proporção encerrada em até dois anos não difere de modo significativo (Fisher, p = {{h3_fisher_p:d3}}). ⇄ O resultado do log-rank não pode ser lido como diferença real. A coorte nova, autuada a partir de 2018, só pode ter ações de até oito anos, enquanto a antiga inclui ações que duraram mais de dez; além disso, o universo deixa de fora ações sem nenhuma decisão até a exportação. Os dois cortes encurtam a duração da coorte nova por construção. ◇

**Leitura.** D-075 não fixou regra de veredito para esta hipótese. O tamanho e a composição do conjunto que permanece no STF mudaram depois de 2018. A mudança coincide com a decisão do STF que restringiu o foro, cuja referência ainda está a confirmar; por isso a relação é classificada como evidência associativa. A duração não é determinável: a coorte nova tem só {{h3_n_pos:d0}} ações, e o tempo de observação das duas coortes é diferente. ◇

::: permite
- Afirmar que, depois de 2018, ficaram menos ações com réu parlamentar no STF, em maior proporção originadas na própria Corte e mais antigas. ◐
:::

::: nao_permite
- Afirmar que as ações passaram a durar menos ou mais. ◇
- Tratar a saída das ações do STF como encerramento dos casos. Elas seguem em outras instâncias, que este estudo não acompanha. ●
:::

## 41. Hipótese 4 — Política externa: sincronia ou dinâmica própria?

**Hipótese testada:** a política externa brasileira apresenta movimentos sincronizados com os ciclos políticos domésticos, ou tem dinâmica parcialmente autônoma?

O teste de D-075 compara, para cada série anual, a variação nos anos de troca de governo (2003, 2011, 2016, 2019 e 2023) com a variação nos demais anos. A mesma regra foi aplicada às séries domésticas, para que houvesse termo de comparação.

[[fig:n37]]

[[tab:t_h4_trocas]]

**Séries externas.** Nenhuma das {{h4_ext_n:d0}} séries externas varia mais nos anos de troca de governo com p < 0,05. ◐ Com dois a cinco anos de troca por série, isso é ausência de evidência de sincronia, e não prova de autonomia. ◇

**Séries domésticas.** Entre as {{h4_dom_n:d0}} séries domésticas (o grupo inclui os índices do V-Dem e da Freedom House, que medem o Brasil), {{h4_sig_n:d0}} variam mais nos anos de troca: {{t_h4_sig}}. ◐ Para duas delas há uma explicação de calendário. Os anos de 2003, 2011, 2019 e 2023 são também inícios de legislatura, quando mudam a composição da Câmara e o conjunto de ações no STF. ◇ A terceira é o índice do V-Dem. O livro não testa por que ele varia mais nos anos de troca. ?

[[tab:t_h4]]

A comparação por governo reforça o resultado. Os votos a favor de resoluções de escrutínio não seguem a orientação partidária de modo regular: foram mais altos sob Dilma 1 ({{h4_votos_gov.Dilma 1:d0}}%) e Bolsonaro ({{h4_votos_gov.Bolsonaro:d0}}%) e mais baixos sob Lula 2 ({{h4_votos_gov.Lula 2:d0}}%) e Lula 3 ({{h4_votos_gov.Lula 3:d0}}%). ◐ As exportações para países Não Livres sobem de um mandato ao seguinte até 2019–22, sob governos de orientações diferentes, e ficam estáveis em 2023–26; sem a China, também sobem. ◐ Os atos bilaterais começam a cair em 2011, dentro de uma sequência de governos do mesmo partido. ●

**Leitura.** D-075 só define o que conta como sincronia, e ela não aparece nas séries externas. A leitura de uma dinâmica parcialmente autônoma é uma interpretação: as séries externas não mudam mais nas trocas de governo, e as que crescem o fazem sob governos de orientações diferentes. ◇ Quanto à autonomia em si, a classe de evidência é não determinável.

O que explica a ausência de sincronia observada não é determinável com estes dados. A demanda externa, a composição dos países examinados em cada ano e a burocracia diplomática são hipóteses que o livro não mede. ?

::: permite
- Afirmar que as séries externas do livro não mostram variação maior nos anos de troca de governo. ◐
- Afirmar que a parcela das exportações para países Não Livres cresceu sob governos de orientações diferentes entre 2003 e 2022. ◐
:::

::: nao_permite
- Afirmar que a política externa é independente dos governos. Votos e atos dependem de decisões de governo, e o teste só mede o momento das mudanças. ◇
- Explicar o crescimento do comércio com países Não Livres por afinidade política. ◇
:::

## 42. Um modelo provisório da transformação institucional brasileira

O ponto de partida foi uma cadeia linear: dinheiro, competição política, partidos, orçamento, distribuição de recursos, instituições de controle, Justiça e política externa. Antes de desenhar qualquer modelo, cada elo dessa cadeia foi classificado pela evidência disponível.

[[tab:t_cadeia]]

Nenhum elo da cadeia tem evidência direta, e {{cadeia_nd:d0}} dos sete não são determináveis com os dados do livro. A sequência linear não descreve bem o que os dados mostram. ◇

O modelo abaixo substitui a cadeia por uma rede, e cada relação traz a sua classe de evidência. Há um nó que a cadeia não tinha: as normas, isto é, as decisões do Congresso e do STF que mudam as regras.

[[fig:n38]]

[[tab:t_modelo]]

**Leitura do modelo.**

- **Relações a partir das normas.** As {{modelo_classes.Evidência direta:d0}} relações com evidência direta partem todas das normas, e cada uma atinge um mecanismo diferente: o dinheiro eleitoral, o orçamento e os partidos. ● A restrição do foro também parte das normas, mas fica como associativa até a confirmação do acórdão. ◇
- **Relações entre mecanismos.** São associativas, como o destino territorial e por função das emendas; hipotéticas, como as relações entre as receitas dos eleitos e a competição, entre competição e partidos e entre a Justiça e o controle administrativo; ou não determináveis, como as relações entre emendas e reeleição, entre partidos e emendas, entre controle e emendas e entre os ciclos domésticos e a política externa. ◇
- **O que o modelo descreve.** Um sistema em que várias regras mudaram num intervalo curto, cada uma sobre um mecanismo. As séries correspondentes mudam depois dessas regras, mas as ligações entre os mecanismos ainda não foram medidas. ◇

O modelo é provisório por três razões.

1. **As normas não são explicadas.** O livro não explica por que essas normas foram aprovadas naquele intervalo. Elas são produto de um processo político que os dados não medem. ?
2. **Ausência de seta não é ausência de relação.** Uma relação sem seta pode existir. O que falta é o dado que a teste. ◇
3. **O modelo pode mudar.** Ele pode ser revisto à medida que os dados da agenda do Atlas forem processados, como as despesas de campanha, os fornecedores de partidos e os doadores completos.

::: permite
- Representar as relações entre os mecanismos como uma rede com as normas no centro, e não como uma cadeia. ◇
- Distinguir as relações documentadas das associativas, das hipotéticas e das não determináveis. ●
:::

::: nao_permite
- Ler o diagrama como modelo causal estimado. ◇
- Inferir, da posição central das normas, quem as promoveu ou com que intenção. ◇
:::

## 43. Balanço: o que mudou, o que não mudou e o que continua sem explicação

**O que mudou.** Mudaram quatro coisas.

- A fonte do dinheiro dos deputados eleitos, de empresas para fundos públicos.
- A escala e a forma das emendas parlamentares.
- O número de partidos relevantes na Câmara, que subiu e depois voltou a cair.
- O conjunto de ações penais com parlamentares que permanece no STF.

Mudaram também a parcela das exportações para países Não Livres, que cresceu até 2019–22, o registro de sanções administrativas e as avaliações internacionais sobre a democracia brasileira. O índice do V-Dem caiu até 2019 e se recuperou em parte desde 2023; a pontuação da Freedom House caiu até 2022 e não se recuperou até 2024. ◐

**O que não mudou.** Ficaram estáveis:

- a faixa de participação das pessoas físicas no dinheiro dos eleitos, entre um décimo e um quinto;
- a saúde como principal destino das emendas;
- a presença dos mesmos partidos na base de governos diferentes;
- a saída das ações do STF no fim dos mandatos. ●

A taxa de reeleição para a Câmara oscila entre {{pv.reel.min:d0}}% e {{pv.reel.max:d0}}%, com altas e quedas relevantes entre eleições, mas sem tendência de longo prazo. ◐

**Quando mudou.** A única janela com mudança ampla, pela regra fixada antes, foi 2016–18. As de 2008–10 e 2019–20 tiveram mudanças parciais. As demais foram setoriais. ◐

**Em que direção.** O financiamento dos eleitos passou do privado ao público e ficou menos concentrado. As emendas cresceram e mudaram de forma. O sistema partidário se dispersou até 2019 e voltou a se concentrar em 2023. O conjunto de ações no STF encolheu e envelheceu. ◐

**Quais instituições estiveram envolvidas.** O Congresso Nacional, por emendas constitucionais e leis eleitorais. O STF, por decisões sobre financiamento, foro e emendas de relator, estas com referências a confirmar. O TSE, que registra partidos, fusões e contas. O Tesouro e a CGU, que registram despesas e sanções. ●

**Quais dados sustentam a observação.** Os do TSE, do Tesouro, da CGU, do STF, do TCU, da Câmara e do Senado, do Itamaraty, das Nações Unidas e da OEA, do BNDES, do ComexStat, do V-Dem e da Freedom House. A deflação usa o IPCA do IBGE. Todos estão listados na tabela de fontes do painel e nas referências do Atlas. ●

**O que pode ser interpretado.** As principais mudanças seguem normas datadas e concentradas num intervalo curto. O Brasil de 2026 distribui recursos eleitorais e orçamentários por regras diferentes das de 2003. ◇

**O que continua sem explicação.** Ficam em aberto seis perguntas.

- Por que as normas foram aprovadas naquele intervalo.
- Quem decidiu o destino das emendas sem autor individual.
- Se a mudança das emendas ampliou o poder do Legislativo ou mudou a forma de negociação com o Executivo.
- Por que a reeleição não subiu depois da troca do financiamento.
- O que explica a ausência de sincronia observada entre a política externa e as trocas de governo.
- Quanto da queda e da recuperação das avaliações externas de democracia corresponde às séries institucionais deste livro.

?

**A resposta à pergunta da Parte VII.** Sim, é possível identificar transformações sistêmicas no sentido mais restrito do termo: várias dimensões mudaram no mesmo intervalo, em vários casos depois de mudanças de regra documentadas. ◐ Não é possível, com estes dados, afirmar que essas transformações formem um único processo com causa comum, nem que uma tenha provocado a outra. ◇ O que os dados mostram é um conjunto de mecanismos que mudaram de regra quase ao mesmo tempo e que, depois disso, passaram a operar de outra forma. ◇

::: permite
- Afirmar que entre 2015 e 2019 mudaram, por lei e emenda constitucional, as regras de financiamento eleitoral, de execução das emendas e de organização partidária, e que as séries correspondentes mudaram em seguida. ● A restrição do foro pelo STF no mesmo período está com a referência a confirmar.
- Afirmar que a janela de 2016–18 é a única com mudança ampla pela regra fixada, e que as séries externas não mostram sincronia com as trocas de governo. ◐
:::

::: nao_permite
- Afirmar que o Brasil viveu um ciclo, ou que as mudanças tenham causa comum demonstrada. ◇
- Atribuir as transformações a um presidente, partido ou governo. ◇
:::
