"""Parte I, Como observar: cobertura das bases, cadeia de custódia, graus de afirmação, testes; esquemas ilustrativos."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from .comum import (BASE, C, FIG, TAB, br, gravar_resultados, ler, registrar, resultados, salvar, tabela, F_STF, F_ETICA, F_TCU, F_IDEOL)

COB = [  # base, início, fim, lacunas, cor
    ("Receitas de campanha (TSE)", 2002, 2022, "só anos de eleição geral", C["blue"]),
    ("Emendas parlamentares (CGU)", 2014, 2026, "2014–16 inconsistentes", C["aqua"]),
    ("Despesa do Governo Central (Tesouro)", 1997, 2025, "", C["aqua"]),
    ("Filiações e mandatos (Câmara, Senado)", 2003, 2026, "", C["violet"]),
    ("Orientações de bancada (Câmara)", 2003, 2026, "", C["violet"]),
    ("Conselhos de Ética (Câmara, Senado)", 2005, 2026, "", C["violet"]),
    ("Ações penais e inquéritos (STF)", 2003, 2026, "", C["orange"]),
    ("Contas irregulares (TCU)", 2003, 2026, "", C["orange"]),
    ("Sanções e leniências (CGU)", 2015, 2026, "", C["orange"]),
    ("Votos em organismos (ONU, OEA)", 2003, 2025, "OEA com atas faltantes", C["green"]),
    ("Atos bilaterais (Itamaraty)", 2003, 2026, "desde 1823 na base", C["green"]),
    ("Crédito à exportação (BNDES)", 1998, 2026, "valor só até 2015", C["green"]),
    ("Exportações (ComexStat)", 2003, 2026, "", C["green"]),
    ("V-Dem", 2000, 2025, "", C["gray"]),
    ("Freedom House", 2000, 2024, "pontuação desde 2012", C["gray"]),
    ("IPCA e população (IBGE)", 2002, 2026, "", C["gray"]),
]


def box(a, x, y, w, h, txt, fc, tc="white", fs=8, bold=False):
    a.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec="none"))
    a.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, color=tc, fontweight="bold" if bold else "normal", linespacing=1.25)


def seta(a, x1, y1, x2, y2):
    a.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11, lw=1.3, color=C["ink2"]))


def canvas(h, w=9.0):
    f, a = plt.subplots(figsize=(w, h)); a.set_xlim(0, 10); a.set_ylim(0, 10 * h / w); a.axis("off"); a.grid(False)
    return f, a, 10 * h / w


def main() -> None:
    R0 = resultados(); R = {}
    # N1 cobertura
    f, a = plt.subplots(figsize=(6.3, 4.2))
    for i, (b, i0, i1, lac, c) in enumerate(COB[::-1]):
        a.barh(i, i1 - i0 + 1, left=i0 - 0.5, color=c, height=0.6)
        if lac:
            a.text(2026.8, i, lac, va="center", fontsize=6.3, color=C["ink2"])
    a.axvline(2002.5, color=C["ink2"], lw=0.7, ls=":")
    a.set_yticks(range(len(COB))); a.set_yticklabels([c[0] for c in COB[::-1]], fontsize=7); a.set_xlim(1996, 2042)
    a.set_xticks(range(1997, 2027, 4)); a.tick_params(axis="x", labelsize=7.5); a.grid(axis="y", visible=False)
    a.set_title("Cobertura temporal das bases usadas no livro")
    salvar(f, "n01", titulo="Cobertura temporal de cada base usada no livro", pergunta="Que anos cada fonte permite observar?",
           periodo="1997–2026", unidade="anos com dado", universo="Bases canônicas do projeto e séries externas (D-070)",
           fonte_primaria="Manifestos de coleta (data/manifestos/) e cobertura medida em docs/limitacoes.md", tratamento="Primeiro e último ano com registro; observações de lacuna",
           derivado="Nenhum", limitacoes="Barra contínua não significa cobertura uniforme dentro do intervalo (ver lacunas à direita e em limitacoes.md)",
           leitura="Só parte das bases cobre os 24 anos do período sem interrupção; as de dinheiro e de emendas têm universos recortados.", codigo="Parte I")
    # N2 cadeia de custódia
    f, a, H = canvas(3.4)
    a.text(0.1, H - 0.35, "Da fonte ao gráfico: o caminho de um número neste livro", fontsize=10, fontweight="bold")
    etapas = [("Fonte primária", "órgão que produziu\no dado (ex.: TSE)", C["navy"]), ("Arquivo bruto", "data/raw/ + sha256\nno manifesto", C["blue"]),
              ("Base canônica", "data/base/*.csv\nfonte por linha", C["blue"]), ("Tratamento do autor", "ligação, filtro,\nsoma, deflação", C["orange"]),
              ("Resultado derivado", "relatorios/livro/\ntabelas e figuras", C["aqua"])]
    for i, (t, d, c) in enumerate(etapas):
        x = 0.1 + i * 1.98
        box(a, x, H - 1.9, 1.75, 0.9, t, c, fs=8, bold=True)
        a.text(x + 0.875, H - 2.1, d, ha="center", va="top", fontsize=7, color=C["ink"])
        if i < 4:
            seta(a, x + 1.75, H - 1.45, x + 1.98, H - 1.45)
    a.text(0.1, 0.35, "Cada gráfico traz, na ficha, as quatro camadas: fonte primária, fonte secundária (quando houver), tratamento do autor e resultado derivado,\n"
           "com o código da análise e a decisão metodológica (D-001 a D-073) que fixou a regra. Repositório: github.com/leandropitol/pesquisa-poder-institucional.", fontsize=6.6, color=C["ink2"])
    salvar(f, "n02", titulo="Cadeia de custódia dos dados, da fonte primária ao resultado derivado", pergunta="Como um número chega ao livro?",
           periodo="—", unidade="—", universo="Todas as bases", fonte_primaria="docs/nota_metodologica.md, seção 3; README do repositório",
           tratamento="Esquema", derivado="—", limitacoes="Parte dos brutos foi capturada no navegador do autor (D-009, D-015, D-037), com sha256 gravado",
           leitura="Nenhum número do livro é digitado à mão: todos saem de scripts (src/livro/).", codigo="Parte I")
    # N3 graus de afirmação
    f, a, H = canvas(2.6)
    a.text(0.1, H - 0.35, "Graus de afirmação usados no texto", fontsize=10, fontweight="bold")
    g = [("●", "Fato observado", "registro com fonte\n(ex.: a data de uma decisão)", C["navy"]), ("◐", "Cálculo derivado", "soma, parcela, mediana,\nfeita pelo autor", C["blue"]),
         ("⇄", "Correlação", "duas séries que variam\njuntas", C["aqua"]), ("?", "Hipótese", "explicação possível,\nainda não testada", C["yellow"]),
         ("◇", "Interpretação", "leitura do autor sobre\no conjunto", C["orange"])]
    for i, (s, t, d, c) in enumerate(g):
        x = 0.1 + i * 1.98
        box(a, x, H - 1.55, 1.75, 0.75, f"{s}  {t}", c, tc="white" if c not in (C["yellow"],) else C["ink"], fs=8, bold=True)
        a.text(x + 0.875, H - 1.75, d, ha="center", va="top", fontsize=7)
    a.text(0.1, 0.2, "Causalidade demonstrada exigiria desenho próprio (experimento, variação exógena); nenhuma afirmação do livro tem esse grau.", fontsize=6.8, color=C["ink2"])
    salvar(f, "n03", titulo="Escala de graus de afirmação", pergunta="Como o leitor distingue fato de interpretação?", periodo="—", unidade="—", universo="Afirmações do livro",
           fonte_primaria="—", tratamento="Convenção do autor (D-071)", derivado="—", limitacoes="—", leitura="Cada afirmação central leva a marca do seu grau.", codigo="Parte I")
    # i1: caminho das ações penais (números de R)
    pm, pdcl, pex = R0.get("p4_pct_merito", 0), R0.get("p4_pct_declinio", 0), R0.get("p4_pct_extincao", 0)
    pout = round(100 - pm - pdcl - pex, 1)
    f, a, H = canvas(5.0)
    a.text(0.1, H - 0.35, "O caminho de 100 ações penais contra parlamentares no STF", fontsize=10, fontweight="bold")
    box(a, 3.4, H - 1.9, 3.2, 0.9, f"100 ações com réu parlamentar\n({R0.get('p4_acoes_parl')} ações autuadas, 2003–2026)", C["navy"], fs=8)
    items = [(pdcl, "Declínio de\ncompetência\n(sai do STF; segue em\noutra instância)", C["orange"]), (pm, "Julgamento\nde mérito\n(absolve ou condena)", C["blue"]),
             (pex, "Extinção da\npunibilidade\n(ex.: prescrição)", C["yellow"]), (pout, "Outro\nencerramento", C["gray"])]
    ys = H - 4.0
    for (n, t, c), x in zip(items, [0.2, 2.7, 5.2, 7.7]):
        seta(a, 5, H - 1.95, x + 1.05, ys + 1.45)
        box(a, x, ys, 2.1, 1.35, f"{br(n,0)} em cada 100", c, tc="white" if c in (C["orange"], C["blue"]) else C["ink"], fs=9, bold=True)
        a.text(x + 1.05, ys - 0.25, t, ha="center", va="top", fontsize=7.5)
    a.text(0.1, 0.15, "Saída do STF não é impunidade nem absolvição: a base não acompanha o processo na instância de destino.", fontsize=6.5, color=C["mute"])
    f.savefig(FIG / "i1.png", dpi=220, facecolor="white", bbox_inches="tight"); plt.close(f)
    registrar("i1", tipo="grafico", arquivo="relatorios/livro/figuras/i1.png", titulo="Esquema: o caminho das ações penais com réu parlamentar no STF",
              pergunta="Para onde vão as ações penais contra parlamentares?", periodo="2003–2026", unidade="ações por 100", universo="Ações penais originárias com réu parlamentar (D-068)",
              fonte_primaria=F_STF, fonte_secundaria="Não há", tratamento="Arredondamento das parcelas do gráfico de desfechos", derivado="Parcela por desfecho",
              limitacoes="O destino após o declínio não é observado", leitura="Esquema dos mesmos números do gráfico de desfechos.", codigo="J1")
    # i2: caminho do dinheiro
    f, a, H = canvas(3.8)
    a.text(0.1, H - 0.3, "O caminho do dinheiro de campanha: antes e depois de 2015", fontsize=10, fontweight="bold")
    a.text(0.1, H - 1.0, "Até 2014", fontsize=9, fontweight="bold", color=C["ink2"])
    box(a, 0.1, H - 2.0, 2.2, 0.8, "Empresas", C["blue"], bold=True); box(a, 3.9, H - 2.0, 2.2, 0.8, "Partido", C["orange"], bold=True); box(a, 7.6, H - 2.0, 2.2, 0.8, "Candidato", C["navy"], bold=True)
    seta(a, 2.3, H - 1.6, 3.9, H - 1.6); seta(a, 6.1, H - 1.6, 7.6, H - 1.6)
    a.annotate("", xy=(7.6, H - 1.3), xytext=(2.3, H - 1.3), arrowprops=dict(arrowstyle="-|>", lw=1.3, color=C["ink2"], connectionstyle="arc3,rad=-0.25"))
    a.text(5.0, H - 0.55, "doação direta; e repasse do partido (até 2010, sem o doador original no registro)", ha="center", fontsize=7)
    a.text(0.1, H - 2.75, "A partir de 2018", fontsize=9, fontweight="bold", color=C["ink2"])
    box(a, 0.1, H - 3.8, 2.2, 0.8, "Tesouro\n(fundo eleitoral)", C["violet"], fs=8, bold=True); box(a, 3.9, H - 3.8, 2.2, 0.8, "Partido", C["orange"], bold=True); box(a, 7.6, H - 3.8, 2.2, 0.8, "Candidato", C["navy"], bold=True)
    seta(a, 2.3, H - 3.4, 3.9, H - 3.4); seta(a, 6.1, H - 3.4, 7.6, H - 3.4)
    mx = R0["p2_mix_pessoa_juridica"]; mf = R0["p2_mix_fundo_publico"]; mp = R0["p2_mix_partido"]
    a.text(0.1, 0.15, f"Deputados federais eleitos: empresas {br(mx['2002'],0)}% do dinheiro em 2002 e {br(mx['2014'],0)}% em 2014; repasses de partido de {br(mp['2002'],0)}% a {br(mp['2014'],0)}%; fundo público {br(mf['2018'],0)}% em 2018 e {br(mf['2022'],0)}% em 2022.", fontsize=6.4, color=C["mute"])
    f.savefig(FIG / "i2.png", dpi=220, facecolor="white", bbox_inches="tight"); plt.close(f)
    registrar("i2", tipo="grafico", arquivo="relatorios/livro/figuras/i2.png", titulo="Esquema: o caminho do dinheiro de campanha antes e depois de 2015",
              pergunta="Por onde o dinheiro chegava aos candidatos?", periodo="2002–2022", unidade="—", universo="Deputados federais eleitos",
              fonte_primaria="TSE, prestação de contas (FNT-000077 a FNT-000082); Lei 13.487/2017", fonte_secundaria="Não há", tratamento="Esquema com os números de c01",
              derivado="—", limitacoes="Esquema simplificado; pessoas físicas e recursos próprios omitidos", leitura="Mesmos números do gráfico de composição.", codigo="D1")
    # i3 modalidades de emendas (números de R)
    f, a, H = canvas(4.4)
    a.text(0.1, H - 0.3, "Cinco modalidades de emenda e o que o arquivo público registra de cada uma", fontsize=10, fontweight="bold")
    cards = [("Individual\n(finalidade definida)", "Autor: parlamentar\nDestino: programa\ninformado", C["blue"], "EC 86/2015"), ("Individual\n(transf. especial)", "Autor: parlamentar\nDestino: ente, sem\nfinalidade definida", C["aqua"], "EC 105/2019"),
             ("Bancada\nestadual", "Autor: a bancada,\nnão o parlamentar", C["orange"], "EC 100/2019"), ("Comissão", "Autor: a comissão", C["violet"], "—"),
             ("Relator", "Autor publicado:\n\"relator geral\" ou\nsem informação", C["red"], "STF, dez/2022\n[a confirmar]")]
    w = 1.82
    for i, (t, d, c, regra) in enumerate(cards):
        x = 0.1 + i * (w + 0.12)
        box(a, x, H - 2.15, w, 1.3, t, c, fs=8, bold=True)
        a.text(x + w / 2, H - 2.4, d, ha="center", va="top", fontsize=7.2)
        a.text(x + w / 2, H - 3.9, "Marco: " + regra, ha="center", va="top", fontsize=7, color=c, fontweight="bold")
    a.text(0.1, 0.2, "Fonte: CGU, arquivo de emendas (FNT-000017); normas no portal da Presidência (lidas em 30/09/2026).", fontsize=6.5, color=C["mute"])
    f.savefig(FIG / "i3.png", dpi=220, facecolor="white", bbox_inches="tight"); plt.close(f)
    registrar("i3", tipo="grafico", arquivo="relatorios/livro/figuras/i3.png", titulo="Esquema: modalidades de emenda parlamentar", pergunta="O que distingue as modalidades?",
              periodo="2014–2026", unidade="—", universo="Arquivo de emendas da CGU", fonte_primaria="CGU (FNT-000017); EC 86/2015, EC 100/2019, EC 105/2019",
              fonte_secundaria="Não há", tratamento="Esquema", derivado="—", limitacoes="A decisão do STF sobre emendas de relator tem referência a confirmar", leitura="—", codigo="M2, M3, M6")
    # i4 status formal
    f, a, H = canvas(3.3)
    a.text(0.1, H - 0.3, "Como ler \"status de pessoa\": o que a base registra e o que não registra", fontsize=10, fontweight="bold")
    st = [("Investigado /\ndenunciado", C["gray"]), ("Réu\n(denúncia recebida)", C["gray"]), ("Absolvido ou\ncondenado na instância", C["blue"]), ("Prescrição /\npunibilidade extinta", C["yellow"]), ("Trânsito em julgado\ne recursos", C["gray"])]
    for i, (t, c) in enumerate(st):
        x = 0.1 + i * 1.98
        box(a, x, H - 2.4, 1.85, 1.2, t, c, tc="white" if c == C["blue"] else C["ink"], fs=6.8, bold=(c == C["blue"]))
        if i < 4:
            seta(a, x + 1.85, H - 1.8, x + 1.98, H - 1.8)
    a.text(0.1, H - 2.8, "Em azul e amarelo: decisões registradas com data e fonte. Em cinza: etapas não acompanhadas de modo sistemático.\n"
           "Processo não é condenação; declínio de competência não é impunidade; prescrição não é absolvição; sanção administrativa não é condenação criminal.",
           fontsize=7, va="top", linespacing=1.5)
    f.savefig(FIG / "i4.png", dpi=220, facecolor="white", bbox_inches="tight"); plt.close(f)
    registrar("i4", tipo="grafico", arquivo="relatorios/livro/figuras/i4.png", titulo="Esquema: categorias formais de status de pessoa", pergunta="O que significa cada registro?",
              periodo="—", unidade="—", universo="status_pessoa_processo", fonte_primaria="Vocabulário fechado do projeto (docs/vocabularios.md)", fonte_secundaria="Não há",
              tratamento="Esquema", derivado="—", limitacoes="—", leitura="—", codigo="Parte I")
    # T1 universos
    t1 = pd.DataFrame([
        ("Receitas de campanha", "Universo recortado", "Presidenciáveis e eleitos a governador, senador e deputado federal; receitas somadas por candidato e tipo", "D-043"),
        ("Emendas parlamentares", "Universo do arquivo", "Todas as linhas publicadas pela CGU de 2014 a 2026, agregadas por emenda, localidade e função", "D-029"),
        ("Ações penais no STF", "Universo por regra", "Ações penais originárias autuadas desde 2003 com tipos penais do protocolo; réus lidos na aba Partes", "D-004, D-048, D-068"),
        ("Status de pessoa", "Registros com fonte", "Status formais com fonte judicial ou oficial; 27 eventos pendentes", "D-046, D-065"),
        ("Contas irregulares (TCU)", "Universo da lista", "Lista pública de responsáveis; ligação aos atores pela candidatura (CPF não guardado)", "D-064"),
        ("Sanções e leniências", "Universo parcial", "CNEP inteiro; CEIS só de empresas já na base; 57 acordos de leniência", "D-027"),
        ("Conselhos de Ética", "Universo das listas oficiais", "Representações e denúncias por quebra de decoro de 2003 a 2026", "D-063"),
        ("Filiações e mandatos", "Universo", "Deputados (legislaturas 52 a 57) e senadores; filiação observada durante o mandato", "D-013, D-016"),
        ("Votos multilaterais", "Seleção temática", "Resoluções de escrutínio sobre países e temas de democracia na ONU e OEA", "D-031, D-044, D-053"),
        ("Atos bilaterais", "Universo", "Atos com um país como outra parte no Concórdia", "D-041"),
        ("Crédito à exportação", "Universo do arquivo", "Pós-embarque de bens e serviços; valor só para serviços", "D-021"),
        ("Réguas de democracia", "Universo", "Todos os países avaliados por V-Dem e Freedom House", "D-003, D-017, D-018"),
    ], columns=["Base", "Tipo de conjunto", "Inclusão (e exclusões principais)", "Decisões"])
    tabela(t1, "t_universos", titulo="Universos, populações e amostras de cada base", unidade="—", periodo="2003–2026", universo="Bases do livro",
           fonte="docs/protocolo.md; docs/decisoes_metodologicas.md; docs/limitacoes.md", notas="\"Seleção temática\" não permite generalizar para toda a política externa.", codigo="Parte I")
    # T3 testes
    ft = pd.read_csv(TAB / "eixo3_foro_testes.csv"); r2 = pd.read_csv(TAB / "eixo3_relator_2x2.csv").set_index("recorte")
    sh = pd.read_csv(TAB / "stf_desfechos_homogeneidade.csv"); eh = pd.read_csv(TAB / "etica_homogeneidade.csv")
    dec_h = ft[(ft.medida == "declinio") & (ft.recorte == "todas as ações") & ft.teste.str.contains("homogeneidade")].iloc[0]
    dec_f = ft[(ft.medida == "declinio") & (ft.recorte == "todas as ações") & ft.teste.str.contains("Fisher")].iloc[0]
    t3 = pd.DataFrame([
        ("Declínio de competência difere entre partidos?", "Pares ação × réu parlamentar", int(dec_h.n), "Qui-quadrado com p exato por simulação", f"p = {br(dec_h.p_valor,3)}", "Sem correção para múltiplos testes; motivo do declínio não medido"),
        ("Declínio difere entre alinhados e oposição?", "Idem", int(dec_f.n), "Fisher bicaudal", f"p = {br(dec_f.p_valor,3)}", "Nenhum período isolado significativo"),
        ("Condenação difere entre partidos (julgados no mérito)?", "Parlamentares julgados no mérito", int(sh.iloc[0].julgados), "Qui-quadrado com simulação", f"p = {br(sh.iloc[0].p_valor,2)}", "Poucos julgados por partido: \"não distingue\""),
        ("Condenação difere por presidente que indicou o relator?", "Julgamentos com relator resolvido", int(r2.loc["total", "julgados_indicados_pt"] + r2.loc["total", "julgados_outros"]), "Fisher bicaudal", f"p = {br(r2.loc['total','p_fisher'],2)}", "Relator por sorteio; decisão colegiada; amostra pequena"),
        ("Representação ética difere entre partidos?", "Parlamentares-legislatura", "—", "Qui-quadrado com simulação", f"p < 0,001 ({int(eh.iloc[0].partidos)} partidos)", "Concentração em poucos episódios"),
        ("Taxas por partido se associam à ideologia?", "Partidos com escore", "15 a 35", "Spearman com permutação", "0 de 20 correlações com p < 0,05", "Poder baixo: só detectaria associações fortes"),
    ], columns=["Pergunta (hipótese nula: não há diferença)", "População", "n", "Método", "Resultado", "Limitação"])
    tabela(t3, "t_testes", titulo="Testes estatísticos citados no livro", unidade="—", periodo="2003–2026", universo="Tabelas de saída do projeto",
           fonte="relatorios/tabelas/eixo3_foro_testes.csv, eixo3_relator_2x2.csv, stf_desfechos_homogeneidade.csv, etica_homogeneidade.csv; relatorio_final.md, seção 7",
           notas="Dos 119 testes do relatório final, 35 têm p < 0,05; ao acaso se esperariam cerca de 6. Testes não independentes.", codigo="Parte I")
    gravar_resultados(R)


if __name__ == "__main__":
    main()
