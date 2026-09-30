"""Nota técnica do estudo do foro (D-068): o que acontece com as ações penais contra parlamentares no STF, 2003 a 2026.

Gerada de relatorios/tabelas/foro_*.csv, sem número digitado à mão; gráficos em relatorios/graficos. Resultados separados da interpretação.

Saídas: relatorios/nota_tecnica_foro.md e relatorios/graficos/foro_*.png

Uso:
    python -m src.relatorios.nota_foro
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.analise.foro import ORDEM, ROTULO, incidencia  # noqa: E402
from src.base import RAIZ  # noqa: E402
from src.relatorios.util import Fontes, commit, dec, milhar, pct, pv, tabela  # noqa: E402

SAIDA = RAIZ / "relatorios" / "nota_tecnica_foro.md"
GRAF = RAIZ / "relatorios" / "graficos"
F = Fontes()
ROT_STATUS = dict(zip(pd.read_csv(RAIZ / "data" / "vocabularios" / "status_processual.csv", dtype=str)["codigo"], pd.read_csv(RAIZ / "data" / "vocabularios" / "status_processual.csv", dtype=str)["rotulo"]))
CORES = {"merito": "#1f77b4", "declinio": "#ff7f0e", "extincao": "#7f7f7f", "outro": "#bcbd22", "acordo": "#9467bd", "em_tramitacao": "#d9d9d9"}
PARL = "com réu parlamentar"


def cit(*tabs, d=(), p=()):
    return F.cit(tabelas=tuple(f"relatorios/tabelas/{t}.csv" for t in tabs), decisoes=tuple(d), padroes=tuple(p))


def graficos(a: pd.DataFrame) -> None:
    GRAF.mkdir(parents=True, exist_ok=True)
    parl = a[a["grupo"] == PARL]
    # 1. desfechos por grupo
    fig, ax = plt.subplots(figsize=(8, 2.6))
    rotulados = set()
    for i, (g, x) in enumerate(a.groupby("grupo")):
        esq = 0.0
        for cat in ORDEM:
            v = (x["categoria"] == cat).mean()
            if v:
                ax.barh(i, v, left=esq, color=CORES[cat], label=None if cat in rotulados else ROTULO[cat])
                rotulados.add(cat)
                esq += v
    ax.set_yticks(range(a["grupo"].nunique()), sorted(a["grupo"].unique()))
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.legend(ncol=3, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.25), frameon=False)
    ax.set_title("Como terminam as ações penais no STF (autuadas de 2003 a 2026)", fontsize=9)
    fig.tight_layout()
    fig.savefig(GRAF / "foro_desfechos.png", dpi=150)
    plt.close(fig)
    # 2. incidência acumulada, ações com réu parlamentar
    t, e = parl["anos"].to_numpy(float), parl["evento"].to_numpy(int)
    causa = np.where(e == 1, parl["categoria"].to_numpy(str), "")
    grade = np.linspace(0, 12, 121)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    base = np.zeros_like(grade)
    for cat in ["merito", "declinio", "extincao", "outro"]:
        y = np.array([incidencia(t, causa, cat, h) for h in grade])
        ax.fill_between(grade, base, base + y, color=CORES[cat], label=ROTULO[cat], step="post", alpha=0.9)
        base = base + y
    ax.set_xlabel("anos desde a autuação no STF")
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_title("Ações com réu parlamentar: incidência acumulada de cada desfecho", fontsize=9)
    ax.legend(fontsize=7, loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(GRAF / "foro_incidencia.png", dpi=150)
    plt.close(fig)
    # 3. série anual
    s = tabela("foro_serie_anual").set_index("ano")
    fig, ax = plt.subplots(figsize=(8, 3))
    base = np.zeros(len(s))
    for cat in ["merito", "declinio", "extincao", "outro"]:
        col = ROTULO[cat]
        if col in s:
            ax.bar(s.index.astype(str), s[col], bottom=base, color=CORES[cat], label=col)
            base = base + s[col].to_numpy()
    ax.set_title("Ações com réu parlamentar: desfechos por ano", fontsize=9)
    ax.tick_params(axis="x", labelrotation=90, labelsize=7)
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(GRAF / "foro_serie_anual.png", dpi=150)
    plt.close(fig)


INICIO_LEGISLATURA = {"2003", "2007", "2011", "2015", "2019", "2023"}


def rotulo_ano(ano) -> str:
    ano = str(ano)
    if ano in INICIO_LEGISLATURA:
        return ", início de legislatura"
    return ", ano da restrição do foro" if ano == "2018" else ""


def montar() -> str:
    a = tabela("foro_acoes")
    parl = a[a["grupo"] == PARL]
    graficos(a)
    cob = tabela("foro_cobertura").iloc[0]
    tp = tabela("foro_tempos")
    tg = tp[tp["recorte"] == "grupo"].set_index("grupo")
    tpar = tg.loc[PARL]
    tcont = tg.loc["sem réu parlamentar ligado"]
    to = tp[tp["recorte"] == "origem"].set_index("origem")
    tc = tp[tp["recorte"] == "coorte"].set_index("coorte")
    rec = tabela("foro_desfechos_recortes")
    od = tabela("foro_outro_detalhe")
    pes = tabela("foro_pessoas")
    sim = tabela("foro_simetria")
    te = tabela("foro_simetria_testes").set_index("teste")
    serie = tabela("foro_serie_anual").set_index("ano")
    n = len(parl)
    k = parl["categoria"].value_counts()
    sem_merito = n - k.get("merito", 0) - k.get("em_tramitacao", 0)
    pes_st = dict(zip(pes["status"], pes["parlamentar_x_acao"]))
    cond, abs_ = pes_st.get("condenado_tribunal_superior", 0), pes_st.get("absolvido", 0)
    gov = sim[sim["grupo_tipo"] == "governo_oposicao"].set_index("grupo")
    decl_ano = serie[ROTULO["declinio"]] if ROTULO["declinio"] in serie else pd.Series(dtype=float)
    ano_pico = str(decl_ano.idxmax()) if len(decl_ano) else ""
    origem_outra = rec[(rec["recorte"] == "origem") & (rec["origem"] == "vinda de outra instância")].set_index("desfecho")
    origem_stf = rec[(rec["recorte"] == "origem") & (rec["origem"] == "autuada no STF")].set_index("desfecho")
    fontes_stf = ("Corte Aberta: decisões em ações penais", "decisão monocrática publicada no DJe", "STF, AP 470")

    L = ["# O que acontece com as ações penais contra parlamentares no STF (2003-2026)", "",
         f"Nota técnica gerada por código a partir da base auditável (commit {commit()}; `python -m src.relatorios.nota_foro`). Resultados (seções 2 a 4) separados da interpretação (seção 5). "
         "Status de pessoa é status formal, nunca culpa. Recomenda-se revisão jurídica antes de qualquer publicação.", "",
         "## Resumo", "",
         f"- {milhar(n)} ações penais com réu parlamentar federal foram autuadas no STF de 2003 a 2026; {milhar(k.get('merito', 0))} ({pct(k.get('merito', 0) / n)}) terminaram com julgamento de mérito e {milhar(sem_merito)} ({pct(sem_merito / n)}) deixaram o STF sem julgamento de mérito. "
         + cit("foro_acoes", "foro_desfechos", d=("D-068",), p=fontes_stf),
         f"- O desfecho mais frequente foi o declínio de competência: {milhar(k.get('declinio', 0))} ações ({pct(k.get('declinio', 0) / n)}) saíram do STF para outra instância sem julgamento. "
         + cit("foro_desfechos", d=("D-068",)),
         f"- Metade das ações deixa o STF em até {dec(tpar['mediana_anos'], 1)} anos da autuação (mediana; intervalo de 95% de {dec(tpar['mediana_ic95_inf'], 1)} a {dec(tpar['mediana_ic95_sup'], 1)} anos). "
         + cit("foro_tempos", d=("D-068",)),
         f"- Quando o parlamentar é julgado no mérito, o último status registrado é de absolvição em {milhar(abs_)} casos e de condenação em {milhar(cond)}; outros {milhar(pes_st.get('prescrito', 0))} terminaram em prescrição. "
         + cit("foro_pessoas", d=("D-065", "D-066")),
         f"- A diferença entre partidos na proporção de ações julgadas no mérito não se distingue do acaso ({pv(te.loc['homogeneidade entre partidos', 'p_valor'])}), e a proporção não acompanha a posição ideológica ({pv(te.loc['Spearman com escore ideológico', 'p_valor'])}); "
         f"é maior entre réus de partidos da base do governo ({pct(gov.loc['governo', 'taxa'])}) do que da oposição ({pct(gov.loc['oposicao', 'taxa'])}; {pv(te.loc['governo x oposição (Fisher)', 'p_valor'])}), na direção oposta à do declínio (D-067). "
         + cit("foro_simetria", "foro_simetria_testes", d=("D-068", "D-050", "D-062")), "",
         "## 1. Pergunta, dados e método", "",
         "Pergunta: o que acontece, e em quanto tempo, com as ações penais contra deputados federais e senadores no Supremo Tribunal Federal, onde tramitam por causa do foro por prerrogativa de função. A mesma medição vale para réus de qualquer partido. "
         + cit(d=("D-068",)), "",
         f"Universo: {milhar(cob['acoes_no_universo'])} ações penais originárias do STF da lista lida (autuadas de 2003 em diante; {milhar(cob['autuadas_antes_de_2003'])} anteriores ficam fora), das quais {milhar(cob['com_reu_parlamentar'])} têm réu parlamentar federal ligado por nome civil "
         f"ou ligação curada ({milhar(cob['pares_parlamentar_acao'])} pares parlamentar x ação). Os réus de cada ação vêm da leitura da aba Partes do portal do STF (relatórios em `data/raw/stf/*/stf_relatorio_navegacao_partes_ap_lote*.md`, registrados em `buscas` como registro auxiliar). As demais ({milhar(cob['acoes_no_universo'] - cob['com_reu_parlamentar'])}) servem de contraste descritivo. " + cit("foro_cobertura", d=("D-048", "D-065"), p=fontes_stf), "",
         "Desfecho, um por ação, pela hierarquia: julgamento de mérito > declínio de competência > em tramitação > extinção da punibilidade sem mérito > acordo homologado > outro encerramento. O tempo vai da autuação no STF até a primeira decisão do desfecho; "
         f"ações em tramitação são censuradas em 23/09/2026 ({milhar(cob['com_reu_parlamentar_ainda_no_acervo_apos_desfecho'])} ações com réu parlamentar seguem no acervo do STF depois do desfecho, em recurso ou execução). "
         " A mediana vem da curva de Kaplan-Meier e a incidência de cada desfecho do estimador de Aalen-Johansen (riscos competitivos). " + cit(d=("D-068",)), "",
         "## 2. Como as ações terminam", "",
         "![Desfechos](graficos/foro_desfechos.png)", "",
         "| Desfecho | Ações com réu parlamentar | % | Demais ações | % |", "|---|---|---|---|---|"]
    cont = a[a["grupo"] != PARL]
    for cat in ORDEM:
        x, y = int((parl["categoria"] == cat).sum()), int((cont["categoria"] == cat).sum())
        L.append(f"| {ROTULO[cat]} | {milhar(x)} | {pct(x / n)} | {milhar(y)} | {pct(y / len(cont))} |")
    L += ["", cit("foro_desfechos", d=("D-068",)), "",
          f"\"Outro encerramento\" reúne ações baixadas sem decisão registrada de mérito, declínio, extinção ou acordo. Pelo texto da última decisão final (sensibilidade, sem mudar a categoria): "
          + "; ".join(f"{r.detalhe_outro}: {milhar(r.acoes)}" for r in od.itertuples()) + ". " + cit("foro_outro_detalhe", d=("D-068",)), "",
          "## 3. Quanto tempo", "",
          "![Incidência acumulada](graficos/foro_incidencia.png)", "",
          f"Nas ações com réu parlamentar, a mediana até a saída do STF é {dec(tpar['mediana_anos'], 1)} anos; nas demais ações, {dec(tcont['mediana_anos'], 2)} anos. " + cit("foro_tempos", d=("D-068",)), "",
          "| Até | Julgamento de mérito | Declínio | Extinção sem mérito | Outro encerramento |", "|---|---|---|---|---|"]
    for h in (2, 4, 8):
        L.append(f"| {h} anos | {pct(tpar[f'merito_ate_{h}_anos'])} | {pct(tpar[f'declinio_ate_{h}_anos'])} | {pct(tpar[f'extincao_ate_{h}_anos'])} | {pct(tpar[f'outro_ate_{h}_anos'])} |")
    L += ["", "Incidência acumulada com riscos competitivos: parcela das ações com réu parlamentar que já teve cada desfecho até o prazo. " + cit("foro_tempos", d=("D-068",)), "",
          "## 4. Recortes", "",
          "### 4.1 Origem da ação", "",
          f"{milhar(to.loc['vinda de outra instância', 'acoes'])} ações com réu parlamentar chegaram ao STF vindas de outra instância (por exemplo, com a diplomação do réu) e {milhar(to.loc['autuada no STF', 'acoes'])} foram autuadas no próprio STF. "
          f"Das vindas de outra instância, {pct(origem_outra.loc[ROTULO['declinio'], 'parcela'])} voltaram por declínio, contra {pct(origem_stf.loc[ROTULO['declinio'], 'parcela'])} das autuadas no STF; "
          f"o julgamento de mérito alcança {pct(origem_outra.loc[ROTULO['merito'], 'parcela'])} e {pct(origem_stf.loc[ROTULO['merito'], 'parcela'])}, respectivamente. " + cit("foro_desfechos_recortes", d=("D-068",)), "",
          "### 4.2 Antes e depois da restrição do foro (maio de 2018)", "",
          f"Só {milhar(tc.loc['a partir de 2018-05-03', 'acoes'])} ações com réu parlamentar foram autuadas depois da restrição, contra {milhar(tc.loc['até 2018-05-02', 'acoes'])} antes; a comparação de desfechos entre as coortes não tem casos suficientes. "
          f"Na série anual, os anos com mais declínios são {'; '.join(f'{ano} ({milhar(v)} ações{rotulo_ano(ano)})' for ano, v in decl_ano.sort_values(ascending=False).head(3).items())}. "
          "No início de cada legislatura, parlamentares que não se reelegeram perdem o foro, e a ação volta à instância de origem. " + cit("foro_desfechos_recortes", "foro_serie_anual", d=("D-068",)), "",
          "![Série anual](graficos/foro_serie_anual.png)", "",
          "### 4.3 Pessoas", "",
          "| Último status registrado (parlamentar x ação) | Quantidade |", "|---|---|"]
    for r in pes.itertuples():
        L.append(f"| {ROT_STATUS.get(r.status, r.status)} | {milhar(r.parlamentar_x_acao)} |")
    L += ["", cit("foro_pessoas", d=("D-065", "D-066")), "",
          "### 4.4 Simetria", "",
          f"Proporção de ações encerradas com julgamento de mérito, por grupo do partido do réu na data da autuação: base do governo {pct(gov.loc['governo', 'taxa'])} ({milhar(gov.loc['governo', 'com_registro'])} de {milhar(gov.loc['governo', 'n_unidades'])}), "
          f"oposição {pct(gov.loc['oposicao', 'taxa'])} ({milhar(gov.loc['oposicao', 'com_registro'])} de {milhar(gov.loc['oposicao', 'n_unidades'])}); {pv(te.loc['governo x oposição (Fisher)', 'p_valor'])}. "
          f"Entre partidos com 10 ou mais ações, {pv(te.loc['homogeneidade entre partidos', 'p_valor'])}; correlação com o escore ideológico, rho = {dec(te.loc['Spearman com escore ideológico', 'estatistica'])} ({pv(te.loc['Spearman com escore ideológico', 'p_valor'])}). "
          + cit("foro_simetria", "foro_simetria_testes", d=("D-068", "D-050", "D-062")), "",
          "| Partido na autuação | Ações encerradas | Com mérito | % |", "|---|---|---|---|"]
    inst = pd.read_csv(RAIZ / "data" / "base" / "instituicoes.csv", dtype=str).fillna("")
    sucedido = set(inst.loc[inst["id_sucessora"] != "", "id_instituicao"])
    for r in sim[(sim["grupo_tipo"] == "partido") & (sim["n_unidades"] >= 10)].sort_values("n_unidades", ascending=False).itertuples():
        rot = f"{r.sigla} (registro encerrado, {r.grupo})" if r.grupo in sucedido else r.sigla
        L.append(f"| {rot} | {milhar(r.n_unidades)} | {milhar(r.com_registro)} | {pct(r.taxa)} |")
    L += ["", cit("foro_simetria", d=("D-068",)), "",
          "## 5. Interpretação (separada dos resultados)", "",
          f"1. **O foro funciona mais como etapa de passagem do que como instância de julgamento.** Cerca de {pct(k.get('merito', 0) / n, 0)} das ações com réu parlamentar chegam a julgamento de mérito no STF; as demais saem por declínio, extinção da punibilidade ou outro encerramento. "
          "Isso descreve o que acontece no STF; o que acontece depois do declínio, em outra instância, não está nesta base.",
          f"2. **O tempo pesa.** Com metade das ações saindo em cerca de {dec(tpar['mediana_anos'], 1)} anos e a maior parte das saídas sem mérito, a prescrição e o fim do mandato (que leva ao declínio) competem com o julgamento. Os dados mostram a competição; não medem a intenção de ninguém.",
          f"3. **Quando há julgamento, a absolvição é mais frequente que a condenação** ({milhar(abs_)} contra {milhar(cond)} no último status de pessoa), o que não permite ler o foro como proteção automática nem como condenação garantida.",
          "4. **Partido.** A diferença entre partidos não se distingue do acaso e não há associação com a posição ideológica; com dezenas de ações por partido, só diferenças grandes seriam detectadas. A diferença entre base do governo e oposição tem sentido estável com a do declínio (D-067): réus da oposição saem mais por declínio e, por isso, chegam menos ao mérito. "
          "Os dados não dizem o motivo; hipóteses como reeleição, renúncia ou perda de mandato por outras vias exigiriam dados de mandato por data.",
          "5. **O que a nota não sustenta.** Ela não mede crimes cometidos, não mede inquéritos (sem lista de réus lida) e não acompanha a ação depois que sai do STF. A comparação antes e depois de 2018 não tem casos suficientes.", "",
          "## 6. Limitações", "",
          "- Unidade de tempo começa na autuação da ação penal no STF, não na denúncia nem nos fatos; ações que vieram de outra instância já tinham tempo decorrido antes.",
          "- A categoria do desfecho vem do tipo de decisão registrado no Corte Aberta; \"outro encerramento\" é heterogêneo (ver seção 2) e parte dele poderia ser declínio ou extinção pelo texto.",
          "- A lista de réus do portal pode estar incompleta; o vínculo réu-parlamentar exige nome civil ou curadoria (D-065), o que deixa de fora ligações não confirmadas.",
          "- Os testes por partido têm poucos casos por grupo; o limite completo do projeto está em `docs/limitacoes.md`.", "",
          "## 7. Reprodução", "",
          "`python -m src.analise.foro` e `python -m src.relatorios.nota_foro`; regras em D-068 (`docs/decisoes_metodologicas.md`); método geral em `docs/nota_metodologica.md`.", "",
          "## Apêndice. Fontes citadas", ""] + F.apendice() + [""]
    return "\n".join(L)


def run() -> None:
    SAIDA.write_text(montar(), encoding="utf-8")
    print(f"escrito: {SAIDA.relative_to(RAIZ).as_posix()}; fontes: {len(F.citadas)}")


if __name__ == "__main__":
    run()
