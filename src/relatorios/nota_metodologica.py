"""Nota metodológica (fechamento do estudo): definições, fontes, regras, métodos estatísticos e índice das decisões D-001 em diante.

Texto fixo só onde descreve método; contagens saem da base e o índice das decisões sai de docs/decisoes_metodologicas.md.

Saída: docs/nota_metodologica.md

Uso:
    python -m src.relatorios.nota_metodologica
"""

import re

import pandas as pd

from src.base import RAIZ, ler
from src.relatorios.util import commit, milhar

DECISOES = RAIZ / "docs" / "decisoes_metodologicas.md"
SAIDA = RAIZ / "docs" / "nota_metodologica.md"
FAMILIAS = [("STF (Corte Aberta, portal, composição, decisões em PDF)", ("STF",)), ("Câmara dos Deputados", ("Câmara dos Deputados",)), ("Senado Federal", ("Senado",)),
            ("TSE (candidaturas, motivos de indeferimento, partidos)", ("TSE", "Tribunal Superior Eleitoral")), ("TCU", ("TCU",)), ("Portal da Transparência (CGU)", ("Portal da Transparência",)),
            ("BNDES e ComexStat", ("BNDES", "ComexStat")), ("Itamaraty (atos bilaterais)", ("Itamaraty",)), ("Nações Unidas e OEA (votos)", ("Nações Unidas", "OEA", "UN Dag")),
            ("Freedom House e V-Dem (réguas)", ("Freedom in the World", "V-Dem")), ("Redes partidárias transnacionais", ("Internacional", "Foro de São Paulo", "Aliança Progressista", "Conferência Permanente", "Democrat", "Democrata")),
            ("Tribunais de outras instâncias (TJMG, TRF4, JFPR, STJ)", ("TJMG", "TRF4", "JFPR", "STJ")), ("Posição ideológica dos partidos", ("Bolognesi",))]


def decisoes() -> list:
    saida = []
    for linha in DECISOES.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| (D-\d{3}) \| (\d{4}-\d{2}-\d{2}) \| (.*)$", linha)
        if not m:
            continue
        corpo = m.group(3).rstrip()
        corpo = corpo[:-1].rstrip() if corpo.endswith("|") else corpo
        decisao = corpo.rsplit(" | ", 1)[0] if " | " in corpo else corpo
        resumo = re.sub(r"\s+", " ", decisao).strip()
        saida.append((m.group(1), m.group(2), resumo[:300] + ("…" if len(resumo) > 300 else "")))
    return saida


def montar() -> str:
    tabelas = ["atores", "processos", "status_pessoa_processo", "fases_processo", "fontes", "eventos", "relacoes", "verificacoes_simetria", "verificacao_resultado", "buscas",
               "votos_multilaterais", "operacoes_exportacao_bndes", "acordos_bilaterais", "emendas_parlamentares", "doacoes_campanha", "decisoes_judiciais"]
    cont = {t: len(ler(t)) for t in tabelas}
    fo = ler("fontes").fillna("")
    fo = fo[~fo["licenca"].str.contains("DataJud", case=False)]
    L = ["# Nota metodológica", "",
         f"Gerada por `python -m src.relatorios.nota_metodologica` (commit {commit()}). Descreve o que o estudo mede, como, com que fontes e com que limites. "
         "Resultados estão em `relatorios/relatorio_final.md`; a linha do tempo em `relatorios/linha_do_tempo.md`; os vieses conhecidos e a cobertura medida em `docs/limitacoes.md`.", "",
         "## 1. Pergunta e escopo", "",
         "Quais fatores institucionais e relações entre agentes do Executivo, do Legislativo e do Judiciário brasileiros, de qualquer partido, de 2003 até hoje, aparecem associados, em registro documental, a três fenômenos: "
         "(eixo 1) esquemas ilícitos com trâmite formal, (eixo 2) apoio a governos de baixa qualidade democrática no exterior e (eixo 3) concentração ou abuso de poder institucional. "
         "A pergunta é aberta: nenhuma análise parte de hipótese sobre um espectro político, e toda medição que envolve partido é repetida para todos os partidos do universo do ano, para governo e oposição e para a posição ideológica.", "",
         "O estudo não atribui culpa sem decisão judicial, não trata denúncia, colaboração ou reportagem como prova, não trata ausência de evidência como indício nem como inocência, não infere motivo de coincidência de datas e não classifica governos estrangeiros por critério próprio.", "",
         "## 2. Unidade de registro e definições", "",
         "- **Processo** é a unidade de registro. `casos` agrupam processos e não são unidade de contagem.",
         "- **Status de pessoa** vem de vocabulário fechado (investigado, denunciado, réu, condenado por instância, absolvido, arquivado, prescrito, punibilidade extinta, condenação anulada, contas julgadas irregulares, candidatura indeferida, representado, sanção disciplinar, mandato cassado e outros), com fonte judicial ou oficial. O status vigente é o de data mais recente; uma mudança é uma linha nova.",
         "- **Nível de confiança:** `documentado` (fonte judicial, legislativa, orçamentária, oficial ou base de dados de pesquisa), `sob_investigacao` (fonte judicial ou oficial sobre procedimento sem decisão de mérito) e `alegado` (só jornalismo, declarações ou colaboração premiada).",
         "- **Partido** é a filiação do ator na data do fato (nunca a atual). Fusões, incorporações e mudanças de nome seguem o registro no TSE.",
         "- **Governo e oposição** (D-050, D-051): o partido é classificado na data do fato pela concordância com as orientações do governo nas votações nominais do Plenário da Câmara (base: 2/3 ou mais; oposição: abaixo de 1/2). Mede alinhamento em votação, não participação formal na coalizão.",
         "- **Posição ideológica** (D-062): escore médio de Bolognesi, Ribeiro e Codato (2023), survey de 2018 com cientistas políticos, com os cortes dos autores; vale o mesmo escore para todo o período.",
         "- **Baixa qualidade democrática** (eixo 2, D-053): país Não Livre na Freedom House ou autocracia (fechada ou eleitoral) no V-Dem Regimes of the World, no ano do fato; as duas réguas ficam lado a lado e nenhuma é combinada em índice próprio.", "",
         "## 3. Fontes e base", "",
         f"A base tem {milhar(cont['atores'])} atores, {milhar(cont['processos'])} processos, {milhar(cont['status_pessoa_processo'])} status de pessoa, {milhar(cont['fases_processo'])} fases de processo, {milhar(cont['eventos'])} eventos, {milhar(cont['relacoes'])} relações "
         f"e {milhar(len(fo))} fontes citáveis (oficiais, judiciais, legislativas e bases de dados de pesquisa). Jornalismo entra só no contraste com a imprensa, como verificação de cobertura, nunca como sustentação de fato. "
         f"Cada consulta de coleta fica em `buscas` ({milhar(cont['buscas'])} registros), que é o registro formal de ausência. Fontes do DataJud não são citadas (termo de uso, D-022).", "",
         "| Família de fontes | Fontes registradas |", "|---|---|"]
    for nome, pads in FAMILIAS:
        n = int(fo.apply(lambda r: any(p.lower() in (r["titulo"] + " " + r["caminho_raw"]).lower() for p in pads), axis=1).sum())
        L.append(f"| {nome} | {milhar(n)} |")
    L += ["", "Os dados brutos ficam em `data/raw/` (imutáveis, com sha256 em `data/manifestos/`); as tabelas canônicas em `data/base/` (CSV) são a única fonte de verdade; todo número de relatório sai de script.", "",
          "## 4. Regras que valem para todo o estudo", "",
          "1. **Simetria ativa.** Todo achado que envolve ator com filiação gera uma verificação por partido, por governo e oposição na época do fato. Relatório nenhum sai com achado sem verificação; o validador checa.",
          "2. **Ausência é registrada, nunca inferida.** `sem_evidencia` só existe quando uma busca registrada devolveu zero resultados; sem busca, o resultado é `nao_verificado`.",
          "3. **Histórico só cresce.** Fases, status, fontes, buscas e verificações só recebem linhas novas; correções de linhas já gravadas ficam em `data/curadoria/correcoes_historico.csv`. Versões novas de verificações (por exemplo, v3 e v4 da simetria do STF) não apagam as anteriores.",
          "4. **Pessoas: só status formal.** Agente privado só aparece por nome com status de réu ou acima. Sem CPF, endereço ou dados familiares; o CPF só serve de chave de ligação entre arquivos públicos e nunca entra na base nem nos relatórios (D-064).",
          "5. **Linguagem descritiva,** sem adjetivos valorativos, a mesma formulação para atores de qualquer partido; o status formal no lugar de qualificações.",
          "6. **Regra antes do cálculo.** Universos, medidas e testes são registrados como decisão metodológica antes de calcular; esclarecimentos feitos depois de ver resultados são declarados como tais na própria decisão (por exemplo, D-061, D-067).", "",
          "## 5. Métodos estatísticos", "",
          "- **Proporções** têm intervalo de confiança de 95% de Wilson. Intervalos que se sobrepõem não permitem distinguir as taxas.",
          "- **Homogeneidade entre partidos:** estatística qui-quadrado de grupos por resultado, com p exato por simulação (hipergeométrica multivariada, 20.000 repetições, semente 20260929), válida com contagens pequenas; só entram partidos com o mínimo de unidades declarado em cada decisão.",
          "- **Governo contra oposição e 2x2:** teste exato de Fisher, bicaudal.",
          "- **Ideologia:** correlação de Spearman entre o escore do partido e a taxa, com p por permutação.",
          "- **Comparações múltiplas:** as tabelas trazem muitos testes e não há correção; o relatório informa quantos têm p abaixo de 0,05 e quantos se esperariam ao acaso. Teste sem poder (poucos casos) é apresentado como “não distingue”, nunca como igualdade.", "",
          "## 6. Decisões metodológicas", "",
          "O registro completo, com justificativas, está em `docs/decisoes_metodologicas.md`. Índice (resumo do início de cada decisão):", "",
          "| Decisão | Data | Resumo |", "|---|---|---|"]
    for i, d, r in decisoes():
        L.append(f"| {i} | {d} | {r.replace('|', '/')} |")
    L += ["", "## 7. Reprodução", "",
          "Com o ambiente Python do projeto, nesta ordem: `python -m src.estrutura`, `python -m src.validacao.validar`, `python -m pytest -q`, os módulos de `src/analise/` e `src/simetria/` (cada um grava em `relatorios/tabelas/`), "
          "`python -m src.relatorios.limitacoes`, `python -m src.relatorios.linha_do_tempo`, `python -m src.relatorios.relatorio_final` e `python -m src.relatorios.nota_metodologica`. "
          "As coletas (`src/coleta/`) repetem downloads dos dados públicos; parte dos brutos vem de captura feita no navegador, guardada em `data/raw/` com sha256, porque alguns portais recusam clientes automatizados.", "",
          "## 8. Limitações e revisão", "",
          "As limitações conhecidas estão em `docs/limitacoes.md` (parte gerada com a cobertura medida). Antes de qualquer publicação, recomenda-se revisão jurídica: o material nomeia agentes públicos com status formal de processos, e o autor responde pelo uso.", ""]
    return "\n".join(L)


def run() -> None:
    SAIDA.write_text(montar(), encoding="utf-8")
    print(f"escrito: {SAIDA.relative_to(RAIZ).as_posix()} ({len(decisoes())} decisões)")


if __name__ == "__main__":
    run()
