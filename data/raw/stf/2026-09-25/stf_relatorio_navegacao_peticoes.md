# Relatório — Exportação de dados públicos do painel Corte Aberta (STF)

## 1. URLs abertas

- Portal STF: https://portal.stf.jus.br
- Painéis estatísticos — Corte Aberta: https://transparencia.stf.jus.br/extensions/corte_aberta/corte_aberta.html
- Painel de Decisões: https://transparencia.stf.jus.br/extensions/decisoes/decisoes.html
- Painel de Acervo: https://transparencia.stf.jus.br/extensions/acervo/acervo.html
- Aba "Acervo histórico" (dentro do painel de Acervo, mesma URL acima)

## 2. Exportações realizadas

### 2.1 Painel de Decisões

- **Filtros aplicados exatamente como ficaram na tela:**
  - Filtro padrão "Ano decisão: 2026" removido
  - Classe Processo: **Pet**
  - Ramo do Direito: **DIREITO PENAL, DIREITO PENAL MILITAR, DIREITO PROCESSUAL PENAL** (chip exibia "3 de 293")
  - Data decisão: digitei 01/01/2003–25/09/2026; o seletor do painel ajustou (clamp) automaticamente para **05/02/2003–24/09/2026** — repeti a digitação 3 vezes e o resultado foi sempre o mesmo, indicando que essa é a menor/maior data com decisão existente nesse subconjunto de filtros (não há decisões Pet + Penal/Processual Penal/Penal Militar fora desse intervalo)
- **Período:** 05/02/2003 a 24/09/2026 (efetivamente equivalente a "01/01/2003 até hoje", pois não há dados fora desse intervalo)
- **Total mostrado pelo painel:** 10.994 decisões (Decisões em Originários: 10.994; Decisões em Recursais: 0)
- **Exportação:** botão "Decisões" (topo direito), formato XLSX
- **Observação:** por cliques duplicados meus durante a verificação, a exportação foi disparada **3 vezes** (11:41:15, 11:41:25 e 11:41:39, todas "Exportação concluída com sucesso" no console). O conteúdo das 3 é idêntico (mesmos filtros). É provável que 3 arquivos XLSX tenham sido baixados na pasta de downloads do usuário (nomes prováveis: "Decisões.xlsx" e variações com sufixo numérico, conforme o padrão do navegador). Recomendo conferir e apagar as duplicatas.

### 2.2 Painel de Acervo — aba "Acervo"

- **Filtros aplicados exatamente como ficaram na tela:**
  - Classe Processo: **Pet**
  - Processo criminal: o filtro existe, mas os valores disponíveis são **"Cível" / "Criminal"** (não "Sim/Não" como mencionado na tarefa) — selecionei **"Criminal"**
- **Total mostrado pelo painel:** 719 processos (Originários: 719)
- **Exportação:** botão "Processos" (topo direito), formato XLSX — disparada 1 vez (11:45:00, "Exportação concluída com sucesso")

### 2.3 Painel de Acervo — aba "Acervo histórico"

- Aba existe e foi aberta
- Os filtros Classe Processo=Pet e Processo criminal=Criminal permaneceram selecionados (visíveis nos chips), **mas o próprio painel exibe o aviso: "Os filtros do aplicativo não funcionam para esse gráfico, isto é, os dados aqui são estáticos, sendo atualizados somente a cada ano."**
- Ou seja, os dados exportados desta aba **não refletem os filtros Pet/Criminal** — são o total geral (não filtrado) do acervo do STF por ano, de 2006 a 2025
- **Colunas disponíveis na "Tabela de dados":** Ano, Originários, Recursais, Total
- **Totais de referência:** 2006 = 150.001; última linha (2025) = 21.976 (esse valor bate exatamente com o total geral não filtrado observado ao abrir a aba "Acervo" antes de qualquer filtro, confirmando que a série é estática/não filtrada)
- KPIs exibidos: "Redução desde 2006: 85,35%"; "Redução últimos 05 anos: 8,75%"; "Aumento no acervo em 2026: 5,94%"
- **Exportação:** botão "Processos", formato XLSX — confirmada pelo usuário mesmo sabendo que os dados não são filtrados; disparada 1 vez (11:45:14, "Exportação concluída com sucesso")

## 3. Filtros que não existiam ou não funcionaram, e o que foi feito no lugar

- **Painel de Decisões — "Ramo direito":** existe como filtro próprio (não foi necessário usar "Assunto" como alternativa). Havia também a opção "DIREITO PROCESSUAL PENAL MILITAR" na lista, que não foi selecionada por não ter sido pedida explicitamente.
- **Painel de Decisões — filtro de Data decisão:** aceitava digitação livre, mas sempre "clampava" (ajustava) para o intervalo com dados reais (05/02/2003–24/09/2026) ao invés de manter exatamente 01/01/2003–25/09/2026 digitado.
- **Painel de Acervo — "Processo criminal":** existe, mas com valores "Cível"/"Criminal" em vez de "Sim"/"Não". Usei "Criminal" como equivalente.
- **Aba "Acervo histórico":** os filtros da aplicação (Classe/Processo criminal) não têm efeito nessa tabela específica — informação dada pelo próprio painel, não uma limitação da automação.

## 4. Erros (texto literal)

- Ao abrir o painel de Acervo pela primeira vez, a página travou na mensagem **"🔍 Carregando filtros essenciais... (0/4)"** por mais de 15 segundos sem progresso. Segui a regra definida: recarreguei a página (https://transparencia.stf.jus.br/extensions/acervo/acervo.html) e, na segunda tentativa, carregou normalmente em poucos segundos. Não foram necessárias mais tentativas.
- Nenhum bloqueio, CAPTCHA, erro 403 ou "acesso negado" foi encontrado em nenhuma etapa.

## 5. Data e hora

- Relatório gerado em: **25/09/2026, 11:46 (horário de Brasília, UTC-3)**
- As exportações ocorreram entre 11:41 e 11:45 (horário de Brasília) do mesmo dia.
- O rodapé do painel de Acervo indicava: "Informações atualizadas em 25/09/2026, às 06:15:18".
