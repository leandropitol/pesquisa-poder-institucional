# Relatório — Consulta pública eproc (JFPR/TRF4) e TRF1: ações da Lava Jato

**Observação metodológica prévia (leia antes das seções por processo):** antes de tentar cada um dos 8 processos individualmente, foram testadas as três vias de acesso público exigidas pela tarefa (eproc da JFPR, eproc do TRF4/Consulta Processual Unificada, e PJe público do TRF1). As três apresentaram bloqueio ao acesso somente-leitura, sem login e sem resolução de CAPTCHA, conforme detalhado abaixo. Como o bloqueio ocorre no nível do próprio serviço de consulta (antes de qualquer resultado específico de processo), e foi confirmado tanto de forma genérica quanto testando o número do Processo 1, o mesmo bloqueio se aplica igualmente aos demais processos que dependem da mesma via — o que é registrado, de forma literal, em cada seção abaixo, em vez de repetir 8 vezes a mesma tentativa infrutífera contra o mesmo endpoint.

- **eproc da JFPR** — URL testada: `https://eproc.jfpr.jus.br/eprocV2/externo_controlador.php?acao=processo_consulta_publica` (com e sem `&num_processo=<número>`). Resultado: página carrega, mas o corpo inteiro contém apenas a mensagem literal **"A consulta pública está desativada."** Não há formulário de busca disponível. (A URL raiz `https://eproc.jfpr.jus.br` redireciona para login SSO — `eproc-sso.trf4.jus.br` —, também não utilizável sob a regra de não fazer login.)
- **eproc do TRF4** (para eventuais apelações/ACr) — URL testada: `https://eproc.trf4.jus.br/eproc2trf4/externo_controlador.php?acao=processo_consulta_publica`. Resultado: mesma mensagem literal **"A consulta pública está desativada."**
- **Consulta Processual Unificada (TRF4/JFRS/JFSC/JFPR)** — via `https://www.trf4.jus.br` → formulário "Consulta Processual Judicial", origem "JFPR", busca pelo nº do processo (testado com 5046512-94.2016.4.04.7000). Resultado: a busca redireciona para `https://consulta.trf4.jus.br/trf4/controlador.php` e exibe a página "Consulta Processual Unificada" com um desafio **Cloudflare — "Confirme que é humano"** (checkbox de verificação humana) antes de mostrar qualquer resultado. Por se tratar de um CAPTCHA, a consulta foi interrompida neste ponto, sem resolvê-lo, conforme instrução da tarefa.
- **PJe público do TRF1 (JFDF)** — `https://pje1g-consultapublica.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam`. Diferentemente das duas vias acima, este sistema **não exige login nem CAPTCHA** e o formulário de busca pública funciona. Testado com o número de destino do Processo 2 (1032252-24.2021.4.01.3400, campo "Numeração única"): a busca foi concluída (após um erro transitório de servidor — "IJ000655: No managed connections available within configured blocking timeout" — corrigido com uma nova tentativa, conforme permitido) e retornou o texto **"3 resultados encontrados"**, mas a tabela de resultados não exibiu nenhuma linha/processo (nem número, nem link, nem movimentação), mesmo após novo carregamento e espera adicional. Não foi possível extrair réus, classe, vara ou movimentações a partir desta tela, pois nenhum dado de processo foi efetivamente renderizado — apenas a contagem, sem conteúdo. Isso não é um bloqueio por login/CAPTCHA, mas a consulta não produziu informação utilizável.

---

## Processo 1 — 5046512-94.2016.4.04.7000 (JFPR, ação do triplex do Guarujá)
- Classe / vara / autuação / sigilo: não informado
- Réus (literal): não informado
- Marcos:

| Data | Órgão | Marco (recebimento, sentença, apelação, anulação, remessa, trânsito…) | Réu | Resultado para o réu (literal) | Trecho literal | URL |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

- Não encontrado / bloqueios (mensagem literal): eproc JFPR — "A consulta pública está desativada." (`https://eproc.jfpr.jus.br/eprocV2/externo_controlador.php?acao=processo_consulta_publica&num_processo=5046512-94.2016.4.04.7000`). Consulta Processual Unificada TRF4/JFPR — bloqueada por desafio Cloudflare "Confirme que é humano" antes de exibir resultado (`https://consulta.trf4.jus.br/trf4/controlador.php`, origem JFPR, busca por nº do processo). Processo não é apontado como enviado a outro tribunal, então TRF1 não se aplica.

## Processo 2 — 5021365-32.2017.4.04.7000 (JFPR, sítio de Atibaia) — destino no DF: 1032252-24.2021.4.01.3400
- Classe / vara / autuação / sigilo: não informado
- Réus (literal): não informado
- Marcos:

| Data | Órgão | Marco (recebimento, sentença, apelação, anulação, remessa, trânsito…) | Réu | Resultado para o réu (literal) | Trecho literal | URL |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

- Não encontrado / bloqueios (mensagem literal): eproc JFPR — "A consulta pública está desativada." (mesma URL/mensagem do Processo 1, serviço indisponível de forma geral). Consulta Processual Unificada TRF4/JFPR — mesmo bloqueio por Cloudflare "Confirme que é humano". Processo de destino no DF (1032252-24.2021.4.01.3400) pesquisado no PJe público do TRF1 (`https://pje1g-consultapublica.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam`, campo "Numeração única"): retornou "3 resultados encontrados" sem nenhuma linha de processo exibida na tabela — nenhum dado (réus, movimentações, datas) pôde ser lido.

## Processo 3 — 5063130-17.2018.4.04.7000 (JFPR, sede do Instituto Lula)
- Classe / vara / autuação / sigilo: não informado
- Réus (literal): não informado
- Marcos:

| Data | Órgão | Marco (recebimento, sentença, apelação, anulação, remessa, trânsito…) | Réu | Resultado para o réu (literal) | Trecho literal | URL |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

- Não encontrado / bloqueios (mensagem literal): eproc JFPR — "A consulta pública está desativada." Consulta Processual Unificada TRF4/JFPR — bloqueada por Cloudflare "Confirme que é humano" (mesmo bloqueio de acesso, aplicável a qualquer nº de processo de origem JFPR nesta via). Não há indicação de remessa à JF do DF para este processo.

## Processo 4 — 5044305-83.2020.4.04.7000 (JFPR, doações ao Instituto Lula)
- Classe / vara / autuação / sigilo: não informado
- Réus (literal): não informado
- Marcos:

| Data | Órgão | Marco (recebimento, sentença, apelação, anulação, remessa, trânsito…) | Réu | Resultado para o réu (literal) | Trecho literal | URL |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

- Não encontrado / bloqueios (mensagem literal): eproc JFPR — "A consulta pública está desativada." Consulta Processual Unificada TRF4/JFPR — bloqueada por Cloudflare "Confirme que é humano". Não há indicação de remessa à JF do DF para este processo.

## Processo 5 — 5026212-82.2014.4.04.7000 (JFPR)
- Classe / vara / autuação / sigilo: não informado
- Réus (literal): não informado
- Marcos:

| Data | Órgão | Marco (recebimento, sentença, apelação, anulação, remessa, trânsito…) | Réu | Resultado para o réu (literal) | Trecho literal | URL |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

- Não encontrado / bloqueios (mensagem literal): eproc JFPR — "A consulta pública está desativada." Consulta Processual Unificada TRF4/JFPR — bloqueada por Cloudflare "Confirme que é humano". Não há indicação de remessa à JF do DF para este processo.

## Processo 6 — 5083401-18.2014.4.04.7000 (JFPR)
- Classe / vara / autuação / sigilo: não informado
- Réus (literal): não informado
- Marcos:

| Data | Órgão | Marco (recebimento, sentença, apelação, anulação, remessa, trânsito…) | Réu | Resultado para o réu (literal) | Trecho literal | URL |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

- Não encontrado / bloqueios (mensagem literal): eproc JFPR — "A consulta pública está desativada." Consulta Processual Unificada TRF4/JFPR — bloqueada por Cloudflare "Confirme que é humano". Não há indicação de remessa à JF do DF para este processo.

## Processo 7 — 5083258-29.2014.4.04.7000 (JFPR)
- Classe / vara / autuação / sigilo: não informado
- Réus (literal): não informado
- Marcos:

| Data | Órgão | Marco (recebimento, sentença, apelação, anulação, remessa, trânsito…) | Réu | Resultado para o réu (literal) | Trecho literal | URL |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

- Não encontrado / bloqueios (mensagem literal): eproc JFPR — "A consulta pública está desativada." Consulta Processual Unificada TRF4/JFPR — bloqueada por Cloudflare "Confirme que é humano". Não há indicação de remessa à JF do DF para este processo.

## Processo 8 — 5049557-14.2013.4.04.7000 (JFPR, inquérito policial apontado como origem da operação)
- Classe / vara / autuação / sigilo: não informado
- Réus (literal): não informado
- Marcos:

| Data | Órgão | Marco (recebimento, sentença, apelação, anulação, remessa, trânsito…) | Réu | Resultado para o réu (literal) | Trecho literal | URL |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

- Não encontrado / bloqueios (mensagem literal): eproc JFPR — "A consulta pública está desativada." Consulta Processual Unificada TRF4/JFPR — bloqueada por Cloudflare "Confirme que é humano". Não há indicação de remessa à JF do DF para este processo.

## Conferência final
- Dos 8 processos solicitados, **nenhum** pôde ser efetivamente lido (réus, classe, vara, marcos/sentenças) nos sistemas públicos indicados, porque as três vias de acesso permitidas ficaram bloqueadas antes de chegar a qualquer conteúdo de processo específico:
  - eproc da JFPR (`eproc.jfpr.jus.br`): consulta pública desativada pelo próprio sistema ("A consulta pública está desativada."), afetando os Processos 1, 2, 3, 4, 5, 6, 7 e 8.
  - eproc do TRF4 (`eproc.trf4.jus.br`), verificado como via alternativa para eventuais apelações (ACr): mesma mensagem de consulta pública desativada.
  - Consulta Processual Unificada (`consulta.trf4.jus.br`, acessível a partir de `www.trf4.jus.br`, que também cobre JFPR): exige resolver um CAPTCHA (Cloudflare "Confirme que é humano") antes de exibir qualquer resultado; a tarefa proíbe resolver CAPTCHA, então a consulta foi interrompida nesse ponto para todos os 8 processos.
- Processo de destino no DF encontrado: sim — o Processo 2 (sítio de Atibaia, segunda pista) tem destino informado pelo usuário como 1032252-24.2021.4.01.3400, na JF do DF. Este número foi pesquisado no PJe público do TRF1 (`https://pje1g-consultapublica.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam`), que é a única das três vias que não exigiu login nem CAPTCHA. A busca foi concluída (após um erro transitório de servidor, resolvido com nova tentativa) e indicou "3 resultados encontrados", mas a tabela de resultados não exibiu nenhuma linha de processo, número, parte ou movimentação — não foi possível ler nenhum dado substantivo a partir dela. Nenhum outro processo de destino no DF foi identificado para os demais 7 processos (nenhum deles foi apontado pelo usuário como remetido à JF do DF).
- Em resumo: o levantamento não pôde ser completado com dados de mérito para nenhum dos 8 processos, devido a bloqueios de acesso público (serviço desativado ou CAPTCHA) nos sistemas eproc da JFPR e do TRF4, e a uma consulta sem resultado utilizável no PJe do TRF1 para o único processo de destino no DF identificado.

## Data e hora da leitura
29/09/2026, 09:41 (horário de Brasília)
