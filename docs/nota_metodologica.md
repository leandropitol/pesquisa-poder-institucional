# Nota metodológica

Gerada por `python -m src.relatorios.nota_metodologica` (commit 788057b). Descreve o que o estudo mede, como, com que fontes e com que limites. Resultados estão em `relatorios/relatorio_final.md`; a linha do tempo em `relatorios/linha_do_tempo.md`; os vieses conhecidos e a cobertura medida em `docs/limitacoes.md`.

## 1. Pergunta e escopo

Quais fatores institucionais e relações entre agentes do Executivo, do Legislativo e do Judiciário brasileiros, de qualquer partido, de 2003 até hoje, aparecem associados, em registro documental, a três fenômenos: (eixo 1) esquemas ilícitos com trâmite formal, (eixo 2) apoio a governos de baixa qualidade democrática no exterior e (eixo 3) concentração ou abuso de poder institucional. A pergunta é aberta: nenhuma análise parte de hipótese sobre um espectro político, e toda medição que envolve partido é repetida para todos os partidos do universo do ano, para governo e oposição e para a posição ideológica.

O estudo não atribui culpa sem decisão judicial, não trata denúncia, colaboração ou reportagem como prova, não trata ausência de evidência como indício nem como inocência, não infere motivo de coincidência de datas e não classifica governos estrangeiros por critério próprio.

## 2. Unidade de registro e definições

- **Processo** é a unidade de registro. `casos` agrupam processos e não são unidade de contagem.
- **Status de pessoa** vem de vocabulário fechado (investigado, denunciado, réu, condenado por instância, absolvido, arquivado, prescrito, punibilidade extinta, condenação anulada, contas julgadas irregulares, candidatura indeferida, representado, sanção disciplinar, mandato cassado e outros), com fonte judicial ou oficial. O status vigente é o de data mais recente; uma mudança é uma linha nova.
- **Nível de confiança:** `documentado` (fonte judicial, legislativa, orçamentária, oficial ou base de dados de pesquisa), `sob_investigacao` (fonte judicial ou oficial sobre procedimento sem decisão de mérito) e `alegado` (só jornalismo, declarações ou colaboração premiada).
- **Partido** é a filiação do ator na data do fato (nunca a atual). Fusões, incorporações e mudanças de nome seguem o registro no TSE.
- **Governo e oposição** (D-050, D-051): o partido é classificado na data do fato pela concordância com as orientações do governo nas votações nominais do Plenário da Câmara (base: 2/3 ou mais; oposição: abaixo de 1/2). Mede alinhamento em votação, não participação formal na coalizão.
- **Posição ideológica** (D-062): escore médio de Bolognesi, Ribeiro e Codato (2023), survey de 2018 com cientistas políticos, com os cortes dos autores; vale o mesmo escore para todo o período.
- **Baixa qualidade democrática** (eixo 2, D-053): país Não Livre na Freedom House ou autocracia (fechada ou eleitoral) no V-Dem Regimes of the World, no ano do fato; as duas réguas ficam lado a lado e nenhuma é combinada em índice próprio.

## 3. Fontes e base

A base tem 2.861 atores, 10.782 processos, 1.296 status de pessoa, 7.526 fases de processo, 2.298 eventos, 2.459 relações e 341 fontes citáveis (oficiais, judiciais, legislativas e bases de dados de pesquisa). Jornalismo entra só no contraste com a imprensa, como verificação de cobertura, nunca como sustentação de fato. Cada consulta de coleta fica em `buscas` (1.017 registros), que é o registro formal de ausência. Fontes do DataJud não são citadas (termo de uso, D-022).

| Família de fontes | Fontes registradas |
|---|---|
| STF (Corte Aberta, portal, composição, decisões em PDF) | 107 |
| Câmara dos Deputados | 5 |
| Senado Federal | 5 |
| TSE (candidaturas, motivos de indeferimento, partidos) | 15 |
| TCU | 1 |
| Portal da Transparência (CGU) | 4 |
| BNDES e ComexStat | 2 |
| Itamaraty (atos bilaterais) | 2 |
| Nações Unidas e OEA (votos) | 176 |
| Freedom House e V-Dem (réguas) | 3 |
| Redes partidárias transnacionais | 21 |
| Tribunais de outras instâncias (TJMG, TRF4, JFPR, STJ) | 10 |
| Posição ideológica dos partidos | 1 |

Os dados brutos ficam em `data/raw/` (imutáveis, com sha256 em `data/manifestos/`); as tabelas canônicas em `data/base/` (CSV) são a única fonte de verdade; todo número de relatório sai de script.

## 4. Regras que valem para todo o estudo

1. **Simetria ativa.** Todo achado que envolve ator com filiação gera uma verificação por partido, por governo e oposição na época do fato. Relatório nenhum sai com achado sem verificação; o validador checa.
2. **Ausência é registrada, nunca inferida.** `sem_evidencia` só existe quando uma busca registrada devolveu zero resultados; sem busca, o resultado é `nao_verificado`.
3. **Histórico só cresce.** Fases, status, fontes, buscas e verificações só recebem linhas novas; correções de linhas já gravadas ficam em `data/curadoria/correcoes_historico.csv`. Versões novas de verificações (por exemplo, v3 e v4 da simetria do STF) não apagam as anteriores.
4. **Pessoas: só status formal.** Agente privado só aparece por nome com status de réu ou acima. Sem CPF, endereço ou dados familiares; o CPF só serve de chave de ligação entre arquivos públicos e nunca entra na base nem nos relatórios (D-064).
5. **Linguagem descritiva,** sem adjetivos valorativos, a mesma formulação para atores de qualquer partido; o status formal no lugar de qualificações.
6. **Regra antes do cálculo.** Universos, medidas e testes são registrados como decisão metodológica antes de calcular; esclarecimentos feitos depois de ver resultados são declarados como tais na própria decisão (por exemplo, D-061, D-067).

## 5. Métodos estatísticos

- **Proporções** têm intervalo de confiança de 95% de Wilson. Intervalos que se sobrepõem não permitem distinguir as taxas.
- **Homogeneidade entre partidos:** estatística qui-quadrado de grupos por resultado, com p exato por simulação (hipergeométrica multivariada, 20.000 repetições, semente 20260929), válida com contagens pequenas; só entram partidos com o mínimo de unidades declarado em cada decisão.
- **Governo contra oposição e 2x2:** teste exato de Fisher, bicaudal.
- **Ideologia:** correlação de Spearman entre o escore do partido e a taxa, com p por permutação.
- **Comparações múltiplas:** as tabelas trazem muitos testes e não há correção; o relatório informa quantos têm p abaixo de 0,05 e quantos se esperariam ao acaso. Teste sem poder (poucos casos) é apresentado como “não distingue”, nunca como igualdade.

## 6. Decisões metodológicas

O registro completo, com justificativas, está em `docs/decisoes_metodologicas.md`. Índice (resumo do início de cada decisão):

| Decisão | Data | Resumo |
|---|---|---|
| D-001 | 2026-09-24 | Projeto em `Documents/pesquisa-poder-institucional`, separado de outros estudos |
| D-002 | 2026-09-24 | Git só local; remoto privado e commits quando grande parte estiver pronta e o autor pedir |
| D-003 | 2026-09-24 | Qualidade democrática por V-Dem (Regimes of the World) e Freedom House (status), lado a lado, sem índice combinado; limiares na seção 4 do protocolo |
| D-004 | 2026-09-24 | Universo do eixo 1, fase 1: ações penais e inquéritos originários no STF e no STJ desde 2003, com os tipos penais da seção 3 do protocolo |
| D-005 | 2026-09-24 | CSV em `data/base/` é a fonte de verdade; Parquet e DuckDB são derivados. DuckDB fica para quando houver consultas analíticas (não está instalado) |
| D-006 | 2026-09-24 | Tabelas de histórico só crescem; o validador compara com o último commit |
| D-007 | 2026-09-24 | Achado sem verificação de simetria é aviso na base e bloqueio no relatório |
| D-008 | 2026-09-24 | Redes partidárias transnacionais de todas as orientações entram no eixo 2 |
| D-009 | 2026-09-24 | Fontes que recusam cliente automatizado (STF, TSE, UN Digital Library em 2026-09-24) não são contornadas; entram por download manual do autor ou espelho público citado |
| D-010 | 2026-09-24 | Votações nominais da Câmara e do Senado entram por lista de temas fixada antes (ver `docs/plano_coleta.md`, E1), não pelo resultado |
| D-011 | 2026-09-24 | A coleta da Câmara não usa o endpoint de detalhe do deputado (`/deputados/{id}`), que devolve CPF; nome e UF vêm da lista por legislatura e do histórico |
| D-012 | 2026-09-24 | Uma busca é uma consulta lógica (por exemplo, "histórico dos deputados das legislaturas 52 a 57"), não cada requisição; cada requisição fica no arquivo bruto JSONL com URL, horário e status |
| D-013 | 2026-09-24 | Universo de partidos do ano X: partidos com ao menos um deputado federal em exercício em 2 de fevereiro de X, pelo histórico da Câmara |
| D-014 | 2026-09-24 | Deputado e senador são a mesma pessoa só quando nome parlamentar normalizado e UF coincidem de forma única; casos ambíguos ficam separados até revisão manual |
| D-015 | 2026-09-24 | Página pública bloqueada a cliente automatizado pode ser lida no navegador do aplicativo, uma página por vez, à vista do autor; as tabelas são extraídas do DOM por trecho JavaScript registrado no código, e o sha256 calculado no navegador é conferido com o do arquivo gravado |
| D-016 | 2026-09-24 | Partido é o registro no TSE, com denominações (sigla e nome) datadas; mudança de nome mantém o partido, fusão cria partido novo, incorporação encerra o incorporado. Siglas das fontes são ligadas ao partido vigente na data |
| D-017 | 2026-09-24 | V-Dem v16 obtido pelo pacote oficial `vdemdata` (GitHub, tag V16), sem o formulário do site; leitura do `.RData` com o R já instalado, que só seleciona colunas e anos |
| D-018 | 2026-09-24 | Freedom House: planilhas históricas públicas mais recentes (fevereiro de 2025, até o ano de 2024). Ano = ano sob avaliação (status) e edição menos um (pontuação total). A edição 2026 fica como lacuna enquanto não houver pedido por e-mail |
| D-019 | 2026-09-24 | Código de país: `country_text_id` do V-Dem (ISO 3166-1 alfa-3 quando existe); nomes da Freedom House ligados por nome normalizado ou pela tabela de curadoria com justificativa |
| D-020 | 2026-09-24 | As réguas entram de 2000 em diante (três anos antes do período, para contexto) |
| D-021 | 2026-09-24 | BNDES: entram as linhas (subcréditos) dos arquivos de pós-embarque de serviços de engenharia e de bens, como publicadas; o pré-embarque fica só no bruto (sem país de destino). Exportadoras entram como `empresa`, sem classificar a natureza |
| D-022 | 2026-09-24 | Termo de uso da API pública do DataJud (CNJ, v1.2) aceito com autorização expressa do autor, com uso restrito: o DataJud serve só para descobrir o universo de processos (número, classe, assunto, datas, movimentos); nenhum dado dele é cruzado com pessoas (cláusulas 3.11 e 4.2); relatórios e bases pub… |
| D-023 | 2026-09-24 | A chave pública do DataJud é lida a cada execução na página de acesso do CNJ, que a publica para uso geral e avisa que ela pode mudar; a chave nunca é gravada em código, dado bruto ou log |
| D-024 | 2026-09-24 | Crimes de licitação entram no universo do eixo 1: estavam na Lei 8.666/1993 e, desde a Lei 14.133/2021, estão no Título XI do Código Penal (arts. 337-E a 337-P) |
| D-025 | 2026-09-24 | Tipos penais do protocolo aplicados pelos códigos de assunto da Tabela Processual Unificada do CNJ (`data/curadoria/assuntos_tpu_eixo1.csv`): `inclui`, `conexo` (só entra com um `inclui`), `exclui`, `qualificador`, `indeterminado` (vai para revisão) |
| D-026 | 2026-09-24 | O portal do STJ exige verificação de robô; o projeto não resolve esse tipo de desafio. A conferência da fonte primária de processos do STJ fica para leitura humana, na etapa de relatórios |
| D-027 | 2026-09-24 | Portal da Transparência pelo download em lote (sem chave de API). CNEP entra inteiro (pessoas jurídicas); do CEIS só entram sanções de empresas já presentes na base; o cadastro completo fica no bruto, com contagens nas limitações |
| D-028 | 2026-09-24 | Sanções e favorecidos que são pessoas físicas não entram na base (ficam só no bruto) |
| D-029 | 2026-09-24 | Emendas parlamentares agregadas por emenda, localidade e função; autor ligado a parlamentar só quando nome (sem pontuação) e mandato no ano apontam para uma pessoa |
| D-030 | 2026-09-24 | Empresas identificadas pelo CNPJ só com dígitos, para ligar a mesma empresa entre BNDES, CGU e CEIS; identificadores estrangeiros da CGU ficam como estão, sem país |
| D-031 | 2026-09-24 | E8 aprovada pelo autor com as sugestões de `docs/lista_e8_para_revisao.md`: votos da ONU por conjunto aberto (Harvard Dataverse ou `unvotes`) com conferência por amostra na UN Digital Library; bloco C (dívidas, garantias, pagamentos a governos) fica para depois; fóruns não partidários entram como ca… |
| D-032 | 2026-09-24 | Votos da Assembleia Geral da ONU: conjunto oficial da UN Digital Library (versão 5, fevereiro de 2026, 364 MB) baixado manualmente pelo autor, porque o servidor não entrega a cliente automatizado; o arquivo fica fora do Git, com sha256 no manifesto |
| D-033 | 2026-09-24 | OEA (bloco A3): índice de volumes das sessões ordinárias de 2003 a 2024 e extraordinárias de 2009 em `data/curadoria/oea_volumes.csv`; resoluções extraídas dos volumes oficiais; seleção em duas etapas (título cita Estado membro + triagem de tema) com curadoria item a item em `data/curadoria/oea_reso… |
| D-034 | 2026-09-24 | Volumes da OEA de 2008 a 2011 e da sessão extraordinária de junho de 2009 (Honduras) baixados manualmente pelo autor, porque o site recusa o coletor (HTTP 406); registrados no manifesto com sha256. Propostas de curadoria aceitas pelo autor viram decisão final; casos parecidos seguem a mesma regra (d… |
| D-035 | 2026-09-24 | Correção documentada em tabela de histórico: a linha antiga fica listada em `data/curadoria/correcoes_historico.csv` (sha1 da linha, identificador novo, motivo, decisão), e o validador aceita só essas alterações. Primeira correção (C-001, script `src/correcoes/c001_buscas_oea.py`): chaves repetidas … |
| D-036 | 2026-09-24 | OEA, votos (bloco A3): (1) cada votação localizada na leitura das atas entra em `data/curadoria/oea_votacoes.csv` com o trecho literal do placar; o script confere que o trecho existe na ata e que o placar digitado aparece nele; (2) o voto de cada país sai da resposta da delegação na chamada e só ent… |
| D-037 | 2026-09-24 | STF (E5): o autor abriu o Corte Aberta no próprio navegador, com o Claude in Chrome, e exportou pelo botão dos painéis as decisões em AP e Inq de 08/01/2003 a 23/09/2026 (17.202) e o acervo em tramitação de AP e Inq (1.331). O número de linhas das planilhas é conferido com o total mostrado no painel… |
| D-038 | 2026-09-24 | STF, assuntos (E5): o Corte Aberta traz um só assunto por processo, como caminho da classificação do STF. Regra por caminho em `data/curadoria/assuntos_stf_eixo1.csv`: capítulos do Título XI do Código Penal entram inteiros (texto do protocolo); nomes iguais aos da tabela do STJ herdam a decisão de D… |
| D-039 | 2026-09-24 | Emenda ao protocolo, por decisão do autor: crimes de responsabilidade de prefeitos e vereadores (Decreto-Lei 201/1967) entram no eixo 1, no STJ e no STF. O art. 1º do decreto pune a apropriação e o desvio de bens e rendas públicas, conduta equivalente ao peculato |
| D-040 | 2026-09-24 | Redes partidárias (E8, bloco D): filiação lida nas listas de membros publicadas pelas próprias redes, em cópias anuais do Internet Archive (uma por ano e endereço, a mais próxima de 1º de julho, desde 2003; `data/curadoria/redes_fontes.csv`). A detecção por nome e sigla só propõe; cada par (rede, pa… |
| D-041 | 2026-09-25 | Atos bilaterais (E8, bloco B): Concórdia do Itamaraty pela interface pública que o próprio site usa (aplicacao.itamaraty.gov.br/ApiConcordia), sem chave. Entram todos os atos bilaterais com um país como outra parte, de todos os anos, para dar denominador; o país vem da lista de países do Concórdia (… |
| D-042 | 2026-09-25 | TSE (E7): arquivos do portal de dados abertos baixados pelo autor no navegador (D-009) e registrados por `src/coleta/tse.py` com sha256. Só os conjuntos usados entram no registro (candidatos, coligações, vagas, cassações, prestação de contas de candidatos e partidos, fundo eleitoral); bens declarado… |
| D-043 | 2026-09-25 | TSE, candidatos e receitas (E7): eleições gerais ordinárias de 2002 a 2022; entram todos os candidatos a presidente e os eleitos a governador, senador e deputado federal. Deputados e senadores são ligados ao parlamentar da base pelo nome (de urna ou civil) igual, ou por todas as palavras do nome da … |
| D-044 | 2026-09-25 | Conselho de Direitos Humanos (E8, bloco A2): resoluções do repositório oficial de documentos da ONU (o site do Alto Comissariado recusa cliente automatizado); da 12ª sessão em diante, uma a uma; das sessões 2 a 11, pelos relatórios anuais do Conselho à Assembleia Geral. Voto de cada país lido na lis… |
| D-045 | 2026-09-25 | STF, petições criminais (E5): entram as petições (Pet) de ramo penal com decisão desde 2003 e as petições criminais em tramitação, exportadas pelo autor do Corte Aberta (o protocolo prevê petições criminais conexas; o caso Master corre sobretudo em petições). Assunto processual sem tipo penal (inves… |
| D-046 | 2026-09-26 | Casos-teste (E9), status das pessoas: só entra status com fonte judicial ou oficial que nomeia a pessoa e diz o resultado; voto de um ministro não é resultado; trechos cortados no portal não sustentam status. Réus ligados a parlamentares da base pelo nome (igual ou por palavras, com correspondência … |
| D-047 | 2026-09-26 | Contraste com a imprensa: lista fechada de veículos definida antes de qualquer busca (`data/curadoria/imprensa_veiculos.csv`): 14 principais (Folha, Estadão, O Globo, Valor, Agência Brasil, BBC News Brasil, CNN Brasil, Poder360, Metrópoles, Gazeta do Povo, CartaCapital, Conjur, JOTA, Migalhas) e 3 d… |
| D-048 | 2026-09-26 | Simetria dos status da E9 (D-007): o padrão é "parlamentar federal réu, condenado ou absolvido em ação penal originária no STF", buscado para todos os partidos do universo do ano. Como a exportação do Corte Aberta não traz partes e o portal recusa cliente automatizado (HTTP 403), os réus de cada açã… |
| D-049 | 2026-09-28 | Normalização pela bancada (`src/simetria/taxa_bancada.py`): a unidade é o par parlamentar x legislatura (deputado titular ou suplente com exercício; senador titular em cada legislatura que o mandato cobre; suplente de senador fica fora porque a base não tem o período de exercício). Partido = filiaçã… |
| D-050 | 2026-09-28 | Governo e oposição por data (grupos da verificação de simetria, D-007), regra fixada antes de calcular: fonte = orientações de bancada nas votações nominais do Plenário da Câmara (arquivos anuais de dados abertos, `src/coleta/camara_orientacoes.py`), com a orientação do Governo ("GOV." ou "Governo")… |
| D-051 | 2026-09-28 | Emenda a D-050, feita depois do primeiro cálculo por lacuna de cobertura (não pelo resultado): na regra original, partidos que orientaram só em bloco ficaram sem classificação em períodos longos (MDB em 2007-2010 e 2015-2016; PP em 2014-2019). O nome do bloco é decomposto nos partidos listados ("PpM… |
| D-052 | 2026-09-28 | E9, Lava Jato e Banco Master: primeiro se confere se o processo está no universo coletado; o que está fora entra pela E9 só com fonte judicial ou oficial e fica registrado como fora do universo (primeira instância federal; HC e Rcl no STF). Notícia oficial de tribunal (TRF4, STJ, STF) que nomeia a p… |
| D-053 | 2026-09-28 | Eixo 2 (relações externas), regras fixadas antes do cálculo. (1) Baixa qualidade democrática (BQD): país com status "Não Livre" (NF) na Freedom House no ano do fato; sensibilidade: regime "autocracia fechada" ou "autocracia eleitoral" no V-Dem (Regimes of the World 0 ou 1); ano sem índice fica sem c… |
| D-054 | 2026-09-28 | Linha de base comercial do eixo 2, regra fixada antes do cálculo: exportações brasileiras (valor FOB em dólar, ComexStat/MDIC, API pública, dados mensais por país; tabela oficial de países com código ISO) de 2003 até o último mês disponível; cada mês vai ao governo em exercício no dia 15. Métrica: p… |
| D-055 | 2026-09-29 | Contraste com a imprensa (execução de D-047), desenho fixado antes das buscas: lista fechada de 12 fatos oficiais já na base (`data/curadoria/imprensa_fatos.csv`, cobrindo Mensalão, Mensalão mineiro, Lava Jato e Banco Master, com condenações, absolvições e anulações); para cada fato, a mesma consult… |
| D-056 | 2026-09-29 | Execução de D-055. (1) Acesso: a busca restrita ao domínio não devolve nenhum link em Folha de S.Paulo, O Globo e Valor Econômico (consulta de controle "Lula" e F05); Estadão e BBC News Brasil recusam a ferramenta (F05); as reservas g1 e UOL também não devolvem link; a Revista Oeste (reserva 3) tem … |
| D-057 | 2026-09-29 | Principais sem acesso (D-056) buscados por agentes no navegador do autor, com as 12 consultas fixas. Três relatórios entregues, guardados no bruto sem alteração (`data/raw/imprensa/2026-09-29/navegador_*.md`, sha256 no manifesto): (a) Claude in Chrome pelo Google (`site:`), sem login: Folha, Estadão… |
| D-058 | 2026-09-29 | Composição do STF de 2003 em diante. Fonte primária: portal do STF, lido no navegador embutido com os bytes gravados no bruto e conferidos pelo sha256 (`data/raw/stf_ministros/`): detalhamento das indicações por presidente, páginas "Dados e Datas" da Biblioteca do STF (mensagem de indicação, decreto… |
| D-059 | 2026-09-29 | Partido do presidente = partido do registro de candidatura no TSE (consulta_cand, já no bruto) na eleição que deu o mandato em curso; para o vice que assumiu, o do registro como vice (Michel Temer, PMDB, 2014). Tabela gerada: `relatorios/tabelas/presidencias_partido.csv` (PT 2003-2016 e 2023-, PMDB … |
| D-060 | 2026-09-29 | Eixo 1 ampliado de casos escolhidos para universos definidos por regra, fixada antes do cálculo e aprovada pelo autor. (1) Universo de pessoas: candidatos das eleições gerais de 2010 a 2022 (TSE, consulta_cand) e parlamentares federais da base; eleições municipais fora. (2) Registros formais: (a) TS… |
| D-061 | 2026-09-29 | Execução de D-060, esclarecimentos feitos depois de ver a distribuição dos motivos do TSE e as contagens por ano, antes de ver taxa por partido: (1) o arquivo de motivos repete cada motivo por candidato; conta-se o candidato, não a linha; (2) 257 dos 259 candidatos com "abuso de poder político" em 2… |
| D-062 | 2026-09-29 | Posição ideológica dos partidos como recorte adicional de simetria, fixado antes do cálculo. Fonte: Bolognesi, Ribeiro e Codato (2023), Dados 66(2), doi 10.1590/dados.2023.66.2.303 (survey com cerca de 510 cientistas políticos em 2018, escala 0 a 10), página do artigo e errata no bruto (a errata cor… |
| D-063 | 2026-09-30 | Conselhos de Ética da Câmara e do Senado no eixo 1, regras fixadas antes do cálculo das taxas. Universo: representações e denúncias por quebra de decoro parlamentar de 2003 a 2026, das listas oficiais (Câmara: REP, tramitações em dadosabertos; Senado: REP, DEN e PCE por ano, mais os PRS de perda de … |
| D-064 | 2026-09-30 | Registros individuais do TCU e do TSE para parlamentares e eleitos da base, com regras fixadas antes do cálculo das taxas. (1) Ligação: candidaturas às eleições gerais de 2002 a 2022 (TSE, consulta_cand, com CPF; deputados federais e senadores eleitos ou suplentes, governadores eleitos, candidatos a… |
| D-065 | 2026-09-30 | Desfechos das ações penais originárias do STF para parlamentares da base, com regras fixadas antes do cálculo das taxas. (1) Fonte: texto oficial das decisões das ações penais na exportação do Corte Aberta (data/raw/stf/2026-09-24). Eventos: Procedente e Procedente em parte = `condenado_tribunal_sup… |
| D-066 | 2026-09-30 | Causa das extinções de punibilidade do STF lida na decisão publicada. Os andamentos do Corte Aberta e as abas do portal trazem só "Declarada a extinção da punibilidade, EM dd/mm/aaaa"; a causa e o nome do acusado estão na decisão monocrática publicada no DJe. Com autorização expressa do autor (30/09… |
| D-067 | 2026-09-30 | Eixo 3 (poder institucional), primeira parte, regras fixadas antes do cálculo. Escopo: o que os dados em mãos permitem. Ficam de fora, por falta de dado, (a) a nomeação para cargo com foro durante status de investigado ou denunciado (a base não tem cargos de ministro de Estado ou equivalentes) e (b)… |
| D-068 | 2026-09-30 | Estudo do foro por prerrogativa de função: o que acontece com as ações penais contra parlamentares no STF, regras fixadas antes do cálculo. (1) Universo: ações penais originárias do STF da lista de D-048 (lotes 1 a 7; fora 8 de janeiro), autuadas no STF de 2003-01-01 em diante. Grupo principal: ação… |

## 7. Reprodução

Com o ambiente Python do projeto, nesta ordem: `python -m src.estrutura`, `python -m src.validacao.validar`, `python -m pytest -q`, os módulos de `src/analise/` e `src/simetria/` (cada um grava em `relatorios/tabelas/`), `python -m src.relatorios.limitacoes`, `python -m src.relatorios.linha_do_tempo`, `python -m src.relatorios.relatorio_final` e `python -m src.relatorios.nota_metodologica`. As coletas (`src/coleta/`) repetem downloads dos dados públicos; parte dos brutos vem de captura feita no navegador, guardada em `data/raw/` com sha256, porque alguns portais recusam clientes automatizados.

## 8. Limitações e revisão

As limitações conhecidas estão em `docs/limitacoes.md` (parte gerada com a cobertura medida). Antes de qualquer publicação, recomenda-se revisão jurídica: o material nomeia agentes públicos com status formal de processos, e o autor responde pelo uso.
