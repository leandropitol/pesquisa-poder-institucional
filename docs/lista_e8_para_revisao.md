# Etapa E8: lista para revisão antes da coleta

Versão 0.1, 2026-09-24. Proposta do que entra no eixo 2 (relações externas), fixada **antes** de olhar
resultados. Nada aqui entra na base sem ser encontrado na fonte oficial indicada. Exemplos entre
parênteses só ilustram o critério e estão marcados "a confirmar".

Regras que valem para todos os blocos:

- **Universo por critério, não por lista de casos.** Cada bloco tem um critério que se aplica igualmente
  a qualquer país e a qualquer governo brasileiro do período.
- **Denominador.** Sempre que possível, o bloco inclui também o comportamento do Brasil em relação a
  países de qualquer orientação política, para comparação.
- **Governo da época.** Cada registro traz a data, para ser analisado por período de governo
  (2003–2010, 2011–2016, 2016–2018, 2019–2022, 2023 em diante), sem juízo sobre intenção.
- **Réguas.** A classificação do país-alvo vem das réguas da E2 (V-Dem e Freedom House), no ano do fato.

---

## Bloco A. Votos em organismos multilaterais

### A1. Assembleia Geral da ONU

- **Critério:** todas as votações nominais (*recorded votes*) de 2003 em diante sobre:
  1. situação de direitos humanos em um país específico, de qualquer região (por exemplo, resoluções
     sobre Irã, Mianmar, Coreia do Norte, Síria, Crimeia; a confirmar);
  2. temas que citem nominalmente um país da América Latina e do Caribe (por exemplo, a resolução
     anual sobre o embargo a Cuba; a confirmar).
- **Por que assim:** o item 1 dá o denominador (como o Brasil vota em resoluções de direitos humanos
  sobre países de qualquer orientação); o item 2 cobre a América Latina.
- **Fonte:** UN Digital Library, coleção de dados de votação (recusa cliente automatizado; ver E8-D1).
  Alternativas: conjunto de votos da Assembleia Geral no Harvard Dataverse (CC0) ou pacote `unvotes`.
- **Registro:** voto de todos os países em cada resolução, em `votos_multilaterais`.

### A2. Conselho de Direitos Humanos da ONU

- **Critério:** todas as votações nominais sobre situação de país específico nos anos em que o Brasil foi
  membro votante (anos de mandato a confirmar na fonte), incluindo resoluções sobre países da América
  Latina (por exemplo, Venezuela e Nicarágua; a confirmar) e de outras regiões.
- **Fonte:** documentos oficiais do Conselho (relatórios de sessão com os votos registrados).

### A3. Organização dos Estados Americanos

- **Critério:** todas as resoluções e declarações da Assembleia Geral e do Conselho Permanente de 2003 em
  diante que (a) invoquem a Carta Democrática Interamericana ou (b) tratem da situação política, eleitoral
  ou de direitos humanos de um Estado membro específico, qualquer que seja o país.
- **Registro:** texto aprovado, votação (quando nominal) e posição do Brasil (a favor, contra, abstenção,
  ausente, consenso, nota de rodapé ou declaração de voto).
- **Limite conhecido:** muitas resoluções saem por consenso; a posição do Brasil nesses casos é
  "participou do consenso", salvo nota de rodapé. Isso será contado nas limitações.
- **Fonte:** atas e documentos oficiais da OEA (PDF), leitura por curadoria.

---

## Bloco B. Acordos e atos bilaterais

- **Critério:** todos os atos bilaterais assinados pelo Brasil de 2003 em diante, com **todos** os países
  (denominador), a partir da base Concórdia do Itamaraty.
- **Campos:** país, título, tema, data de assinatura, entrada em vigor e, quando houver, o decreto
  legislativo de aprovação no Congresso (liga à votação da E1).
- **Classificação de tema** (fixada antes): cooperação técnica; financiamento e crédito; comércio e
  investimento; energia e infraestrutura; defesa e segurança; saúde; educação e cultura; outros.
- **Fonte:** Concórdia (forma de consulta a confirmar; se bloquear cliente automatizado, leitura no
  navegador pela regra D-015).

---

## Bloco C. Financiamento, crédito e garantias do Estado brasileiro no exterior

Além das operações do BNDES (E3), proposta de três fontes, todas por critério geral e para todos os
países:

- **C1. Renegociação e perdão de dívidas soberanas com o Brasil:** resoluções do Senado que autorizam
  renegociação ou perdão de créditos da União com outros países, de 2003 em diante (fonte: Senado,
  dados abertos da E1; a confirmar a forma de busca).
- **C2. Indenizações do seguro de crédito à exportação (Fundo de Garantia à Exportação):** pagamentos da
  União por inadimplência de devedores estrangeiros, por país e ano (fonte: publicações do Tesouro
  Nacional e da Câmara de Comércio Exterior; a confirmar disponibilidade em dado aberto).
- **C3. Pagamentos da União a governos estrangeiros por programas de cooperação** (por exemplo, programas
  executados por meio de organismo internacional com contrapartida a governo estrangeiro; a confirmar):
  critério geral, para qualquer país; fonte a definir (Portal da Transparência ou relatórios do TCU).

**Pergunta para você:** C1 a C3 ampliam o eixo 2 além do que foi pedido (BNDES, votos, acordos, redes).
Entram agora, ficam para depois ou saem?

---

## Bloco D. Redes partidárias e fóruns políticos transnacionais

- **Critério:** redes ou fóruns permanentes de partidos políticos, com participação de ao menos um partido
  brasileiro com registro no TSE, de qualquer orientação. Registro de **filiação** (partido → rede, com
  período) e de **encontros** (data, local, partidos brasileiros presentes segundo a documentação da
  própria rede).
- **Lista inicial** (ordem alfabética; a participação de partidos brasileiros e as datas serão confirmadas
  nas fontes de cada rede):

| Rede ou fórum | Tipo | A confirmar |
|---|---|---|
| Aliança Progressista | rede internacional de partidos | membros brasileiros e período |
| COPPPAL (Conferência Permanente de Partidos Políticos da América Latina e do Caribe) | rede regional de partidos | membros brasileiros e período |
| Foro de Madri | fórum criado em 2020 | se há partido brasileiro como signatário ou só parlamentares individuais |
| Foro de São Paulo | rede regional de partidos, desde 1990 | membros brasileiros e período |
| International Democrat Union | rede internacional de partidos | membros brasileiros e período |
| Internacional Democrata Centrista e ODCA (Organização Democrata Cristã da América) | rede internacional e regional | membros brasileiros e período |
| Internacional Liberal e RELIAL (Rede Liberal da América Latina) | rede internacional e regional | membros brasileiros e período |
| Internacional Socialista | rede internacional de partidos | membros brasileiros e período |
| UPLA (União de Partidos Latino-Americanos) | rede regional de partidos | membros brasileiros e período |

- **Ficam fora** (proposta): fóruns de pessoas e não de partidos (por exemplo, Grupo de Puebla),
  conferências abertas sem filiação formal (por exemplo, edições nacionais da CPAC), fundações e
  institutos (por exemplo, redes de *think tanks*) e o Parlamento do Mercosul (órgão institucional, não
  partidário). **Pergunta para você:** concorda com a exclusão, ou algum desses entra como categoria
  separada, "fórum político não partidário", com o mesmo critério para todas as orientações?
- **Fontes:** sites oficiais das redes (listas de membros e declarações finais de encontros), com cópia
  datada no arquivo da web (Wayback Machine) para cada ano; documentos dos próprios partidos brasileiros.
- **Nível de confiança:** filiação registrada na lista oficial da rede = `documentado`; presença em
  encontro citada só em reportagem = `alegado`.
- **Regra de leitura:** participação em rede é relação política pública, não indício de ilícito; o
  relatório nunca liga filiação a rede com os eixos 1 e 3 sem registro próprio.

---

## Decisões que preciso de você

| ID | Pergunta | Minha sugestão |
|---|---|---|
| E8-D1 | Votos da ONU: a UN Digital Library recusa o coletor. Uso o conjunto do Harvard Dataverse (CC0) ou o pacote `unvotes`, se trouxerem os votos nominais, e confiro uma amostra pela Digital Library no navegador? | Sim |
| E8-D2 | Blocos C1 a C3 (dívidas, garantias, pagamentos a governos): entram agora, depois ou saem? | Depois; primeiro A, B e D |
| E8-D3 | Fóruns não partidários (Grupo de Puebla, CPAC etc.): ficam fora ou entram como categoria separada? | Categoria separada, mesmo critério para todos |
| E8-D4 | Conselho de Direitos Humanos (A2): entra junto com a Assembleia Geral? | Sim |
| E8-D5 | Ordem de coleta | A1, A3, D, B, A2 |
