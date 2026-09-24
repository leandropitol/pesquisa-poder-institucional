# Plano de coleta

Versão 0.1, 2026-09-24. O acesso a cada fonte foi testado nesta data com requisições pequenas (consulta
de catálogo, um registro ou só o cabeçalho HTTP). Nenhum dado foi baixado ainda. Itens marcados
"a confirmar" não foram verificados diretamente.

## 1. Regras comuns a todos os coletores

- **Um módulo por fonte** em `src/coleta/<fonte>.py`, com a mesma interface: `planejar()` lista o que
  seria baixado e o tamanho esperado, sem baixar nada; `coletar()` baixa e registra.
- **Registro obrigatório.** Toda requisição que traz dado grava:
  - o arquivo bruto em `data/raw/<fonte>/<AAAA-MM-DD>/`, sem alteração;
  - uma linha no manifesto `data/manifestos/<fonte>.csv` (URL, caminho, data de acesso, tamanho, sha256);
  - uma linha em `buscas` por consulta lógica (consulta reprodutível, parâmetros, número de resultados,
    sha256 do arquivo bruto; D-012).
    Uma busca com zero resultados também é gravada: é ela que sustenta um "sem evidência".
- **Rede:** sessão HTTP comum (`src/coleta/comum.py`) com tempo limite, novas tentativas com espera
  exponencial, pausa mínima entre requisições e cabeçalho `User-Agent` com o nome do projeto, sem dados
  pessoais.
- **Bloqueios não são contornados.** Se uma fonte recusa cliente automatizado (HTTP 403), o coletor
  para e registra o bloqueio. A alternativa é download manual pelo autor ou espelho público citado, nunca
  trocar identidade, rodar navegador disfarçado ou resolver CAPTCHA.
- **Volume:** o `planejar()` mede o tamanho antes (cabeçalho HTTP). Arquivos acima de 50 MB, ou lotes
  acima de 500 MB, pedem autorização do autor antes de baixar.
- **Chaves de API** só em variável de ambiente: `TRANSPARENCIA_API_KEY` e `DATAJUD_API_KEY` (a chave
  pública divulgada pelo CNJ na documentação do DataJud).
- **Da coleta à base:** `data/raw` → `src/normalizacao/<fonte>.py` → `data/staging/<fonte>/` (Parquet) →
  carga em `data/base/` (CSV). A carga só é aceita com o validador em zero falhas.

## 2. Fontes, acesso verificado e destino

| # | Fonte | Acesso em 2026-09-24 | Formato e volume | Tabelas de destino |
|---|---|---|---|---|
| 1 | Câmara, API v2 (`dadosabertos.camara.leg.br/api/v2`) | OK (deputados, partidos, histórico do deputado, votações) | JSON paginado | `atores`, `filiacoes`, `cargos`, `instituicoes` (partidos), `universo_partidos`, `eventos` (votações), `fonte_legislativa` |
| 2 | Câmara, arquivos anuais (`dadosabertos.camara.leg.br/arquivos/`) | OK | CSV por ano; em 2023: votações 6,7 MB, votos 42,8 MB | votos nominais das votações selecionadas |
| 3 | Senado, dados abertos (`legis.senado.leg.br/dadosabertos`) | OK (senadores por legislatura, filiações com datas) | JSON/XML | `atores`, `filiacoes`, `cargos`, votações nominais |
| 4 | V-Dem, versão 16 (março de 2026) | Página OK; arquivo a medir | CSV country-year (Core ou Full); licença CC BY-SA 4.0 | `qualidade_democratica` (`vdem_row`, `vdem_ldi`), `fonte_base_dados` |
| 5 | Freedom House, Freedom in the World | Planilhas anuais publicadas em `freedomhouse.org/sites/default/files/`; arquivo da edição 2026 a localizar | XLSX pequeno | `qualidade_democratica` (`fh_status`, `fh_total`) |
| 6 | BNDES, dados abertos (CKAN, `operacoes-exportacao`) | OK; atualizado em 2026-09-23 | 3 CSV (pós-embarque serviços de engenharia 0,4 MB; pós-embarque bens 1,0 MB; pré-embarque 3,7 MB) com dicionários em PDF | `operacoes_exportacao_bndes`, `instituicoes` (exportadoras, devedores) |
| 7 | STJ, DataJud (CNJ, `api_publica_stj`) | Documentação OK; STJ incluído, STF não | JSON (Elasticsearch), chave pública no cabeçalho | `processos`, `fases_processo` (movimentos), `fonte_judicial` |
| 8 | STJ, dados abertos (CKAN) | OK: 21 conjuntos, entre eles espelhos de acórdãos por órgão julgador, íntegras de decisões e acervo em tramitação | CSV e JSON | `decisoes_judiciais`, `fases_processo` |
| 9 | STF, portal e Corte Aberta (`transparencia.stf.jus.br`) | **HTTP 403** para cliente automatizado | painéis com exportação CSV e XLSX (dados desde 2000) | `processos`, `decisoes_judiciais`, `fases_processo` |
| 10 | Portal da Transparência, API | OK (documentação; dados exigem chave) | JSON; entre os 80+ serviços: acordos de leniência, CEIS, CNEP, emendas, contratos, convênios | `instituicoes` (empresas sancionadas), `eventos`, `fonte_orcamentaria` |
| 11 | TSE, dados abertos e CDN | **HTTP 403** para cliente automatizado (catálogo e CDN) | ZIP por eleição (candidatos, prestação de contas); volume a medir, provavelmente centenas de MB por ano | `doacoes_campanha` (agregado), `filiacoes` na data da eleição, `cargos` (eleitos) |
| 12 | ONU, votos na Assembleia Geral | UN Digital Library: **HTTP 403**. Alternativa: conjunto Voeten e outros no Harvard Dataverse (CC0, versão 39 de 2026-07-30; a confirmar se inclui os votos nominais além dos pontos ideais) | CSV | `votos_multilaterais` |
| 13 | OEA, Assembleia Geral e Conselho Permanente | Sem base estruturada de votos; muitas resoluções saem por consenso | PDF oficial por resolução | `votos_multilaterais`, por curadoria |
| 14 | Itamaraty, Concórdia (atos internacionais) | Página OK; forma de consulta a confirmar (aplicação web) | a confirmar | `acordos_bilaterais` |
| 15 | Redes partidárias transnacionais | Sites das próprias redes e arquivo da web | HTML, PDF (declarações, listas de membros) | `instituicoes`, `relacoes` (`membro_de`), `eventos` |

## 3. Ordem das etapas

Cada etapa termina com: validador em zero falhas, testes passando, parte gerada de
`docs/limitacoes.md` atualizada e, com o seu OK, um commit local.

| Etapa | Conteúdo | Por que nesta ordem | Depende de você |
|---|---|---|---|
| E1 | Câmara e Senado: deputados e senadores desde 2003 (legislaturas 52 a 57), filiações com datas, mandatos, partidos com fusões e mudanças de nome, `universo_partidos` por ano | A simetria não funciona sem o universo de partidos por ano | Não (volume pequeno, só API) |
| E2 | V-Dem e Freedom House | Independente e pequeno; fixa as réguas antes de olhar o eixo 2 | Autorizar o CSV do V-Dem se passar de 50 MB |
| E3 | BNDES, operações de exportação (todos os países) | Três arquivos pequenos; fecha o denominador do eixo 2 | Não |
| E4 | STJ: ações penais e inquéritos originários desde 2003 pelos tipos penais do protocolo (DataJud mais os dados abertos do STJ) | Primeiro universo do eixo 1 com acesso automatizado | Não |
| E5 | STF: lista de ações penais e inquéritos originários e decisões monocráticas (Corte Aberta) | O portal bloqueia cliente automatizado | Exportar os CSV do Corte Aberta pelo navegador, ou autorizar outro caminho (espelho da Base dos Dados, que pede conta Google) |
| E6 | Portal da Transparência: acordos de leniência, CEIS e CNEP; emendas parlamentares (eixo 3) | Liga empresas dos processos a sanções administrativas | Cadastrar a chave da API e defini-la em `TRANSPARENCIA_API_KEY` |
| E7 | TSE: candidatos (partido e resultado por eleição) e receitas de campanha agregadas, 2002 a 2024 | Grande e bloqueado a cliente automatizado | Baixar os ZIP pelo navegador ou autorizar outro caminho; autorizar o volume |
| E8 | Eixo 2 por curadoria: acordos (Concórdia), votos na ONU e na OEA, redes partidárias de todas as orientações | Exige leitura de documentos | Revisar a lista de resoluções e redes antes da coleta |
| E9 | Casos de teste: Mensalão (AP 470), Lava Jato e processos conexos, Banco Master | Conferir se aparecem porque pertencem ao universo; se algum não aparecer, a lacuna vai para `docs/limitacoes.md`, e o caso não é forçado para dentro | Não |

## 4. Detalhes por etapa

### E1, Câmara e Senado

- Câmara: `/deputados?idLegislatura=52..57`, `/deputados/{id}/historico` (mudanças de partido e de
  situação com data), `/partidos`. Senado: `/senador/lista/legislatura/{n}` e `/senador/{codigo}/filiacoes`
  (filiação e desfiliação com data).
- `universo_partidos` do ano X: partidos com ao menos um deputado em exercício em 2 de fevereiro de X (D-013),
  calculado do histórico. O critério fica na coluna `criterio`.
- Votações: só as nominais de proposições ligadas aos eixos (foro por prerrogativa, CPIs, emendas de
  relator, BNDES, aprovação de acordos internacionais por decreto legislativo, anistias). A lista de
  temas é fixada antes, no protocolo, para não selecionar votações pelo resultado.

### E4 e E5, tribunais superiores

- Filtro por classe (ação penal, inquérito, petição criminal) e por assunto da Tabela Processual
  Unificada do CNJ correspondente aos tipos penais do protocolo. A tabela de correspondência entre assunto
  e tipo penal fica versionada em `data/curadoria/`.
- Status de pessoas: só a partir de decisão com fonte judicial. Nomes de partes em processos criminais
  podem vir anonimizados ou por iniciais; nesse caso o registro fica no processo, sem ator, e a lacuna é
  contada nas limitações.
- DataJud cobre metadados e movimentos, não o texto das decisões. Texto, quando necessário, vem dos
  dados abertos do STJ ou da página pública do processo.

### E7, TSE

- Pessoas físicas doadoras ficam agregadas por candidato e eleição (regra de LGPD do projeto). Pessoas
  jurídicas doadoras (até 2014) entram por CNPJ.

## 5. Riscos de coleta já identificados

1. STF, TSE e UN Digital Library recusaram cliente automatizado em 2026-09-24. Os três dependem de
   download manual ou de espelho, o que torna a atualização menos frequente.
2. DataJud não inclui o STF.
3. A cobertura histórica do DataJud para processos antigos e baixados precisa ser medida na E4; o
   resultado entra em `docs/limitacoes.md`.
4. Votos na OEA quase nunca são nominais; o eixo 2 pode ter pouca informação de voto nessa organização,
   o que será registrado como lacuna.
5. A Freedom House publica planilhas com endereço diferente a cada edição; o coletor precisa localizar o
   arquivo, e o arquivo usado fica no manifesto.
