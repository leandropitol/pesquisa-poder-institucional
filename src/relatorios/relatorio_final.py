"""Relatório final do estudo (fechamento): resultados por eixo, simetria, interpretação separada e apêndice de fontes.

Toda frase de resultado lê um valor de tabela em relatorios/tabelas (ou da base) e traz a citação da tabela, das decisões metodológicas e das fontes;
nenhum número é digitado aqui. A interpretação fica numa seção própria, depois dos resultados. Linguagem descritiva, a mesma para atores de qualquer partido.

Saída: relatorios/relatorio_final.md

Uso:
    python -m src.relatorios.relatorio_final
"""

import re

import numpy as np
import pandas as pd

from src.base import RAIZ, ler
from src.relatorios.util import Fontes, commit, dec, milhar, pct, pv, tabela

SAIDA = RAIZ / "relatorios" / "relatorio_final.md"
F = Fontes()


def rotulos(vocab: str) -> dict:
    d = pd.read_csv(RAIZ / "data" / "vocabularios" / f"{vocab}.csv", dtype=str)
    return dict(zip(d["codigo"], d["rotulo"]))


ROT_STATUS, ROT_CLASSE = rotulos("status_processual"), rotulos("classe_processual")


def cit(*tabs, d=(), p=()):
    return F.cit(tabelas=tuple(f"relatorios/tabelas/{t}.csv" for t in tabs), decisoes=tuple(d), padroes=tuple(p))


# ------------------------------------------------------------------ seções
def secao_escopo() -> list:
    return ["## 1. Escopo e limites", "",
            "O estudo reúne, em forma de registro documental e de 2003 até hoje, processos, decisões e relações entre agentes dos três Poderes, de qualquer partido, em três eixos: "
            "esquemas ilícitos com trâmite formal (eixo 1), relações externas com governos de baixa qualidade democrática (eixo 2) e concentração ou abuso de poder institucional (eixo 3). "
            "A pergunta é aberta e nenhuma análise parte de hipótese sobre um espectro político. *(Fonte: `docs/protocolo.md`, seção 1; `CLAUDE.md`, seção 1)*", "",
            "O estudo não atribui culpa sem decisão judicial, não trata denúncia, colaboração ou reportagem como prova, não trata ausência de evidência como indício nem como inocência, "
            "não infere motivo de coincidência de datas e não classifica governos estrangeiros por critério próprio. *(Fonte: `docs/protocolo.md`, seção 7)*", "",
            "Dados pessoais: sem CPF, endereço ou dados familiares; agente privado só aparece por nome com status formal de réu ou acima. Recomenda-se revisão jurídica antes de qualquer publicação. *(Fonte: `CLAUDE.md`, seção 5)*", ""]


def secao_base() -> list:
    tabs = [("atores", "atores"), ("processos", "processos"), ("status_pessoa_processo", "status formais de pessoa"), ("fases_processo", "fases de processo"),
            ("eventos", "eventos"), ("relacoes", "relações"), ("verificacoes_simetria", "verificações de simetria"), ("verificacao_resultado", "resultados de verificação"),
            ("buscas", "buscas registradas")]
    cont = {t: len(ler(t)) for t, _ in tabs}
    at, pr, st = ler("atores"), ler("processos"), ler("status_pessoa_processo")
    L = ["## 2. A base", "",
         f"A base tem {milhar(cont['atores'])} atores ({milhar((at['tipo_ator'] == 'agente_publico').sum())} agentes públicos e {milhar((at['tipo_ator'] == 'agente_privado').sum())} agentes privados), "
         f"{milhar(cont['processos'])} processos, {milhar(cont['status_pessoa_processo'])} status formais de pessoa, {milhar(cont['fases_processo'])} fases de processo e {milhar(cont['buscas'])} buscas registradas. "
         + cit(p=("STF", "Senado", "Câmara dos Deputados", "TSE", "TCU")), "",
         "Processos por classe: " + "; ".join(f"{ROT_CLASSE.get(c, c)}: {milhar(n)}" for c, n in pr["classe"].value_counts().items()) + ". *(Fonte: `data/base/processos.csv`)*", "",
         "Status formais por tipo: " + "; ".join(f"{ROT_STATUS.get(c, c)}: {milhar(n)}" for c, n in st["status"].value_counts().items()) + ". *(Fonte: `data/base/status_pessoa_processo.csv`)*", ""]
    return L


def secao_eixo1_stf() -> list:
    b = tabela("simetria_taxa_bancada")
    b = b[(b["legislatura"] == "52-55") & (b["bancada"] >= 100)].copy()
    tot = tabela("simetria_taxa_bancada")
    tot = tot[tot["legislatura"] == "52-55"]
    sobrepoe, pares = 0, 0
    for i, x in b.iterrows():
        for j, y in b.iterrows():
            if i < j:
                pares += 1
                sobrepoe += int(x["ic95_reu_inf"] <= y["ic95_reu_sup"] and y["ic95_reu_inf"] <= x["ic95_reu_sup"])
    alto = b.sort_values("taxa_reu", ascending=False).iloc[0]
    baixo = b.sort_values("taxa_reu").iloc[0]
    go = tabela("simetria_taxa_governo_oposicao")
    go = go[go["periodo"].str.startswith("2003-2019")].set_index("grupo")
    dd = tabela("stf_desfechos")
    dd = dd if "status" in dd else pd.read_csv(RAIZ / "relatorios" / "tabelas" / "stf_desfechos.csv")
    cobertura = tabela("stf_desfechos_cobertura").iloc[0]
    h = tabela("stf_desfechos_homogeneidade")
    tx = tabela("stf_desfechos_taxas")
    tp = tx[tx["grupo_tipo"] == "partido"]
    L = ["### 3.1 Ações penais originárias no STF", "",
         f"Nas legislaturas 52 a 55, {milhar(tot['n_reu'].sum())} de {milhar(tot['bancada'].sum())} parlamentares-legislatura ({pct(tot['n_reu'].sum() / tot['bancada'].sum())}) foram réus em ação penal do STF com assunto do eixo 1, "
         f"e {milhar(tot['n_condenacao'].sum())} tiveram ação com condenação no mérito. " + cit("simetria_taxa_bancada", d=("D-048", "D-049"), p=("STF, Corte Aberta", "STF, portal")), "",
         f"Entre os {len(b)} partidos com bancada de 100 ou mais parlamentares-legislatura, a taxa de réus vai de {pct(baixo['taxa_reu'])} ({baixo['sigla']}) a {pct(alto['taxa_reu'])} ({alto['sigla']}); "
         f"em {sobrepoe} de {pares} pares os intervalos de 95% se sobrepõem. " + cit("simetria_taxa_bancada", d=("D-049",)), "",
         f"Antes da restrição do foro (2003-2019), a taxa de parlamentares-ano réus é {pct(go.loc['governo', 'taxa_reu'], 2)} na base do governo e {pct(go.loc['oposicao', 'taxa_reu'], 2)} na oposição. "
         + cit("simetria_taxa_governo_oposicao", d=("D-050", "D-051")), "",
         f"Desfechos registrados por pessoa: {milhar(len(dd))} status lidos no texto oficial das decisões do STF ({'; '.join(f'{ROT_STATUS.get(k, k)}: {milhar(v)}' for k, v in dd['status'].value_counts().items())}); "
         f"os de mérito são {milhar(dd['status'].isin(['condenado_tribunal_superior', 'absolvido']).sum())}, e os demais encerram a ação sem julgar o mérito (prescrição, extinção da punibilidade, rejeição da denúncia). "
         + cit("stf_desfechos", d=("D-065", "D-066"), p=("Corte Aberta: decisões em ações penais", "decisão monocrática")), "",
         f"Das {milhar(cobertura['acoes_julgadas_no_merito_com_reu_parlamentar'])} ações julgadas no mérito com réu parlamentar, {milhar(cobertura['com_desfecho_na_pessoa'])} têm o desfecho registrado na pessoa ({milhar(cobertura['julgados_pessoa_acao'])} parlamentares x ação). "
         + cit("stf_desfechos_cobertura", d=("D-065",)), "",
         f"Entre os parlamentares julgados no mérito, {pct(tp['condenados'].sum() / tp['n_julgados'].sum())} foram condenados; a proporção não se distingue entre os {milhar(h.iloc[0]['grupos'])} partidos com 5 ou mais julgados ({pv(h.iloc[0]['p_valor'])}) "
         f"nem entre base do governo e oposição ({pv(h.iloc[1]['p_valor'])}). " + cit("stf_desfechos_taxas", "stf_desfechos_homogeneidade", d=("D-065",)), ""]
    return L


def secao_eixo1_etica() -> list:
    d = tabela("etica_desfechos")
    t = tabela("etica_taxas")
    h = tabela("etica_homogeneidade")
    c = tabela("etica_correlacao")
    g = tabela("etica_governo_periodo")
    rep = t[(t["medida"] == "representado") & (t["recorte"] == "2003-2026") & (t["grupo_tipo"] == "partido") & (t["n_unidades"] >= 30)].sort_values("taxa", ascending=False)
    tot = t[(t["medida"] == "representado") & (t["recorte"] == "2003-2026") & (t["grupo_tipo"] == "partido")]
    adv = d["status_final"].isin(["mandato_cassado", "sancao_disciplinar"])
    hr = h[(h["medida"] == "representado")]
    hs = hr[hr["recorte"].str.startswith("2007")].iloc[0]
    gr = g[(g["medida"] == "representado") & (g["periodo"] != "Todo o período")]
    gt = g[(g["medida"] == "representado") & (g["periodo"] == "Todo o período")].iloc[0]
    sig = gr[gr["p_fisher"] < 0.05]
    alto = rep.iloc[0]
    L = ["### 3.2 Conselhos de Ética da Câmara e do Senado", "",
         f"Há {milhar(len(d))} vínculos entre representação por quebra de decoro e parlamentar, em {milhar(d[['casa', 'processo']].drop_duplicates().shape[0])} processos de 2003 a 2026; "
         f"{milhar(d['status_final'].isna().sum())} vínculos não têm desfecho nos campos estruturados das fontes. " + cit("etica_desfechos", d=("D-063",), p=("Conselho de Ética", "tramitações das representações", "Projetos de Resolução")), "",
         f"Desfechos registrados: {'; '.join(f'{ROT_STATUS.get(k, k)}: {milhar(v)}' for k, v in d['status_final'].value_counts().items())}. " + cit("etica_desfechos", d=("D-063",)), "",
         f"Entre os partidos com 30 ou mais parlamentares-legislatura, a parcela de parlamentares alvo de representação vai de {pct(rep['taxa'].min())} ({rep.sort_values('taxa').iloc[0]['sigla']}) a {pct(alto['taxa'])} ({alto['sigla']}, "
         f"{milhar(alto['com_registro'])} de {milhar(alto['n_unidades'])}); as taxas diferem entre partidos ({pv(hs['p_valor'])}, sem a 52ª legislatura) e não se correlacionam com a posição ideológica "
         f"(|rho| de {dec(c['spearman'].abs().min())} a {dec(c['spearman'].abs().max())}; menor {pv(c['p_permutacao'].min())}). " + cit("etica_taxas", "etica_homogeneidade", "etica_correlacao", d=("D-063", "D-062")), "",
         f"No período inteiro, a parcela de parlamentares-ano alvo de representação é {pct(gt['taxa_governo'])} na base do governo e {pct(gt['taxa_oposicao'])} na oposição ({pv(gt['p_fisher'])}); "
         f"{len(sig)} de {len(gr)} períodos presidenciais têm diferença significativa, com sentido diferente entre eles ("
         + "; ".join(f"{r.periodo}: maior {'na base do governo' if r.taxa_governo > r.taxa_oposicao else 'na oposição'}" for r in sig.itertuples()) + "). " + cit("etica_governo_periodo", d=("D-063", "D-050")), "",
         f"Mandato cassado ou sanção disciplinar aprovada: {milhar(adv.sum())} vínculos, número pequeno demais para distinguir partidos ({pv(h[(h['medida'] == 'adverso') & (h['recorte'] == '2003-2026')].iloc[0]['p_valor'])}). "
         + cit("etica_homogeneidade", d=("D-063",)), ""]
    return L


def secao_eixo1_tcu_tse() -> list:
    r = tabela("eixo1_registros")
    cob = tabela("eixo1_parlamentares_cobertura")
    h = tabela("eixo1_parlamentares_homogeneidade")
    c = tabela("eixo1_parlamentares_correlacao")
    g = tabela("eixo1_parlamentares_governo_periodo")
    gt = g[(g["medida"] == "tcu_acumulado") & (g["periodo"] == "Todo o período")].iloc[0]
    ha = h[(h["medida"] == "tcu_acumulado") & (h["recorte"] == "2003-2026")].iloc[0]
    e1h = tabela("eixo1_homogeneidade")
    el = e1h[(e1h["universo"] == "eleitos") & (e1h["anos"] == "todos")].set_index("medida")
    e1 = tabela("eixo1_taxas")
    eg = e1[(e1["grupo_tipo"] == "governo_oposicao") & (e1["universo"] == "eleitos") & (e1["anos"] == "todos") & (e1["medida"] == "tcu_ate_eleicao")].set_index("grupo")
    ind_eleitos = e1[(e1["grupo_tipo"] == "governo_oposicao") & (e1["universo"] == "eleitos") & (e1["anos"] == "todos") & (e1["medida"] == "tse_indeferimento")]
    ca = e1h[(e1h["universo"] == "candidatos") & (e1h["anos"] == "todos")].set_index("medida")
    alta = e1[(e1["grupo_tipo"] == "partido") & (e1["universo"] == "candidatos") & (e1["anos"] == "todos") & (e1["medida"] == "tse_indeferimento") & (e1["n"] >= 200)].sort_values("taxa", ascending=False).head(3)
    alta_tcu = e1[(e1["grupo_tipo"] == "partido") & (e1["universo"] == "candidatos") & (e1["anos"] == "todos") & (e1["medida"] == "tcu_ate_eleicao") & (e1["n"] >= 200)].sort_values("taxa", ascending=False).head(3)

    def lista(x):
        return "; ".join(f"{r.sigla} {pct(r.taxa, 2)} ({milhar(r.com_registro)} de {milhar(r.n)})" for r in x.itertuples())
    L = ["### 3.3 Contas julgadas irregulares (TCU) e candidaturas indeferidas (TSE)", "",
         f"A base registra {milhar((r['registro'] == 'TCU').sum())} status de contas julgadas irregulares (trânsito em julgado de 2003 em diante) em {milhar(r[r['registro'] == 'TCU']['id_ator'].nunique())} atores "
         f"e {milhar((r['registro'] == 'TSE').sum())} de candidatura indeferida por motivo do eixo 1 (2018 e 2022) em {milhar(r[r['registro'] == 'TSE']['id_ator'].nunique())} atores; "
         "a ligação entre lista pública e ator usa o CPF e o nome civil da candidatura, e o CPF não entra na base. " + cit("eixo1_registros", d=("D-064",), p=("TCU, certidões", "consulta_cand", "motivo_cassacao")), "",
         f"A ligação cobre {pct(cob['ligados'].sum() / cob['parlamentar_legislatura'].sum())} das unidades parlamentar-legislatura. " + cit("eixo1_parlamentares_cobertura", d=("D-064",)), "",
         f"Entre os parlamentares com candidatura ligada, a parcela com contas irregulares já transitadas até o fim da legislatura não difere entre partidos ({pv(ha['p_valor'])}), "
         f"não se correlaciona com o escore ideológico (|rho| de {dec(c['spearman'].abs().min())} a {dec(c['spearman'].abs().max())}) e é {pct(gt['taxa_governo'], 2)} na base do governo e {pct(gt['taxa_oposicao'], 2)} na oposição ({pv(gt['p_fisher'])}). "
         + cit("eixo1_parlamentares_homogeneidade", "eixo1_parlamentares_correlacao", "eixo1_parlamentares_governo_periodo", d=("D-064",)), "",
         f"No universo dos candidatos eleitos de 2010 a 2022, a parcela com contas irregulares até a eleição é {pct(eg.loc['governo', 'taxa'], 2)} entre partidos da base do governo e {pct(eg.loc['oposicao', 'taxa'], 2)} na oposição, "
         f"com intervalos de 95% que se sobrepõem; a diferença entre partidos dessa parcela tem {pv(el.loc['tcu_ate_eleicao', 'p_valor'])} e a de candidaturas indeferidas por motivo do eixo 1, {pv(el.loc['tse_indeferimento', 'p_valor'])}, com apenas {milhar(ind_eleitos['com_registro'].sum())} candidaturas indeferidas entre {milhar(ind_eleitos['n'].sum())} eleitos. "
         + cit("eixo1_taxas", "eixo1_homogeneidade", d=("D-060", "D-061")), "",
         f"No universo de todos os candidatos às eleições gerais de 2010 a 2022, a parcela com contas irregulares até a eleição difere entre partidos ({pv(ca.loc['tcu_ate_eleicao', 'p_valor'])}) e a de candidaturas indeferidas por motivo do eixo 1 também ({pv(ca.loc['tse_indeferimento', 'p_valor'])}); "
         f"entre os partidos com 200 ou mais candidatos, as maiores parcelas de contas irregulares são {lista(alta_tcu)} e as de candidaturas indeferidas, {lista(alta)}. "
         "Essas taxas dependem também do número e do perfil dos candidatos de cada partido e não medem a conduta do partido; em 2022, a cassação por fraude à cota de gênero atinge a lista inteira e é tratada à parte em D-061. "
         + cit("eixo1_taxas", "eixo1_homogeneidade", d=("D-060", "D-061")), ""]
    return L


def secao_eixo1_ideologia_imprensa() -> list:
    c = tabela("ideologia_correlacao")
    pvec = tabela("imprensa_contraste_por_veiculo")
    pf = tabela("imprensa_contraste_por_fato")
    nav = tabela("imprensa_navegador_por_veiculo")
    menor = c.sort_values("p_permutacao").iloc[0]
    tot = pvec[["concorda", "diverge", "mencao_sem_resultado", "sem_resultado"]].sum()
    n_bus = int(tot.sum())
    cheios = pf[pf["com_materia"] == pf["veiculos_em_uso"]]["id_fato"].tolist()
    vazios = pf.sort_values("com_materia").head(2)
    L = ["### 3.4 Posição ideológica dos partidos", "",
         f"Das {len(c)} correlações entre o escore ideológico e as taxas por partido (STF, TCU e TSE), {int((c['p_permutacao'] < 0.05).sum())} têm p abaixo de 0,05; a de menor p ({menor['fonte']}, {menor['medida']}, {menor['universo']}) "
         f"tem rho = {dec(menor['spearman'])} ({pv(menor['p_permutacao'])}). " + cit("ideologia_correlacao", d=("D-062",), p=("Bolognesi",)), "",
         "### 3.5 Contraste com a imprensa", "",
         f"Para {len(pf)} fatos oficiais já na base, buscou-se cobertura em {milhar(pvec['veiculo'].nunique())} veículos (busca em ferramenta de pesquisa): em {milhar(tot['concorda'])} de {milhar(n_bus)} buscas havia matéria que concorda com o fato oficial, "
         f"em {milhar(tot['diverge'])} matéria que diverge, em {milhar(tot['mencao_sem_resultado'])} menção sem o resultado e em {milhar(tot['sem_resultado'])} nenhum resultado; \"sem resultado\" mede também a ferramenta de busca. "
         + cit("imprensa_contraste_por_veiculo", "imprensa_contraste_por_fato", d=("D-055", "D-056"), p=("imprensa",)), "",
         f"Os fatos {', '.join(cheios)} têm matéria em todos os veículos em uso; {vazios.iloc[0]['id_fato']} ({vazios.iloc[0]['caso']}) e {vazios.iloc[1]['id_fato']} ({vazios.iloc[1]['caso']}) têm matéria em {milhar(vazios.iloc[0]['com_materia'])} e {milhar(vazios.iloc[1]['com_materia'])} dos {milhar(vazios.iloc[0]['veiculos_em_uso'])} veículos. "
         + cit("imprensa_contraste_por_fato", d=("D-055",)), "",
         f"Uma segunda coleta, no navegador, registrou {milhar(nav['concorda'].sum())} buscas com matéria concordante, {milhar(nav['diverge'].sum())} divergente e {milhar(nav['sem_resultado'].sum())} sem resultado em {milhar(nav['veiculo'].nunique())} veículos; "
         "as coletas divergem entre si para a Folha em vários fatos, o que mostra o efeito da ferramenta. " + cit("imprensa_navegador_por_veiculo", "imprensa_navegador_folha_por_coleta", d=("D-056",)), ""]
    return L


def md_tabela(df: pd.DataFrame) -> list:
    cab = "| " + " | ".join(df.columns) + " |"
    return [cab, "|" + "---|" * len(df.columns)] + ["| " + " | ".join(str(x) for x in r) + " |" for r in df.itertuples(index=False)]


def secao_eixo2() -> list:
    v = tabela("eixo2_votos_por_governo")
    fh = v[v["recorte"] == "escrutínio, alvo BQD (FH)"]
    vd = v[v["recorte"] == "escrutínio, alvo BQD (V-Dem)"]
    bn = tabela("eixo2_bndes_por_governo")
    cm = tabela("eixo2_comercio_por_governo")
    ac = tabela("eixo2_acordos_por_governo")
    rd = tabela("eixo2_redes_partidarias")

    def linhas_voto(x):
        return pd.DataFrame({"Governo": x["governo"], "Resoluções": x["n_resolucoes"], "Brasil, parcela de sim": x["parcela_sim_brasil"].map(pct),
                             "Democracias, média de sim": x["media_sim_democracias"].map(pct), "América Latina, média de sim": x["media_sim_america_latina"].map(pct)})
    bn2 = bn[~bn["governo"].str.startswith("antes")]
    L = ["## 4. Eixo 2: relações externas e qualidade democrática", "",
         "Um país é de baixa qualidade democrática (BQD) quando é Não Livre na Freedom House ou autocracia (fechada ou eleitoral) no V-Dem Regimes of the World, no ano do fato; as duas réguas são apresentadas lado a lado e não são combinadas. "
         + cit(d=("D-053",), p=("Freedom in the World", "V-Dem")), "",
         "### 4.1 Votos em resoluções de escrutínio sobre países (ONU e OEA)", "",
         f"Em resoluções de escrutínio cujo alvo é BQD pela Freedom House, a parcela de votos favoráveis do Brasil vai de {pct(fh['parcela_sim_brasil'].min())} ({fh.sort_values('parcela_sim_brasil').iloc[0]['governo']}) "
         f"a {pct(fh['parcela_sim_brasil'].max())} ({fh.sort_values('parcela_sim_brasil').iloc[-1]['governo']}); a média de democracias nas mesmas resoluções vai de {pct(fh['media_sim_democracias'].min())} a {pct(fh['media_sim_democracias'].max())}. "
         + cit("eixo2_votos_por_governo", "eixo2_votos_por_resolucao", d=("D-053",), p=("Nações Unidas", "OEA")), ""]
    L += md_tabela(linhas_voto(fh)) + ["", "Régua V-Dem (mesmas resoluções, alvo BQD pelo V-Dem):", ""] + md_tabela(linhas_voto(vd)) + [""]
    L += ["### 4.2 Apoio à exportação (BNDES)", "",
          f"A parcela das operações de apoio à exportação do BNDES com destino BQD pela Freedom House vai de {pct(bn2['parcela_operacoes_bqd_fh'].min())} a {pct(bn2['parcela_operacoes_bqd_fh'].max())} entre os governos; "
          f"a parcela do valor de serviços de engenharia com destino BQD só existe nos governos com esse tipo de operação ({', '.join(bn2[bn2['parcela_valor_servicos_bqd_fh'].notna()]['governo'])}) e chega a {pct(bn2['parcela_valor_servicos_bqd_fh'].max())} em {', '.join(bn2[bn2['parcela_valor_servicos_bqd_fh'] == bn2['parcela_valor_servicos_bqd_fh'].max()]['governo'])}. "
          + cit("eixo2_bndes_por_governo", d=("D-053",), p=("BNDES",)), ""]
    L += md_tabela(pd.DataFrame({"Governo": bn2["governo"], "Operações": bn2["n_operacoes"], "Parcela BQD (FH)": bn2["parcela_operacoes_bqd_fh"].map(pct),
                                 "Parcela BQD (V-Dem)": bn2["parcela_operacoes_bqd_vdem"].map(pct)})) + [""]
    L += ["### 4.3 Comércio exterior (exportações, ComexStat)", "",
          f"A parcela das exportações brasileiras com destino BQD pela Freedom House vai de {pct(cm['parcela_exportacoes_bqd_fh'].min())} a {pct(cm['parcela_exportacoes_bqd_fh'].max())} entre os governos, "
          f"com a China como primeiro destino BQD {'em todos os governos' if cm['principais_destinos_bqd_fh'].str.startswith('CHN').all() else 'em parte dos governos'} ({cm['principais_destinos_bqd_fh'].iloc[-1].split(';')[0].replace('CHN ', 'China, ').replace('.', ',')} das exportações no governo mais recente). "
          f"A parcela de exportações para países sem classificação na Freedom House é {pct(cm['parcela_exportacoes_sem_classificacao_fh'].iloc[-1])} no governo mais recente, contra no máximo {pct(cm['parcela_exportacoes_sem_classificacao_fh'].iloc[:-1].max())} nos anteriores, "
          "o que limita a comparação desse governo. " + cit("eixo2_comercio_por_governo", d=("D-054",), p=("ComexStat",)), ""]
    L += md_tabela(pd.DataFrame({"Governo": cm["governo"], "Meses": cm["meses"], "Parcela BQD (FH)": cm["parcela_exportacoes_bqd_fh"].map(pct), "Parcela BQD (V-Dem)": cm["parcela_exportacoes_bqd_vdem"].map(pct),
                                 "Sem classificação (FH)": cm["parcela_exportacoes_sem_classificacao_fh"].map(pct)})) + [""]
    ac = ac.sort_values("parcela_atos_bqd_fh")
    L += ["### 4.4 Atos bilaterais (Itamaraty)", "",
          f"Nos atos bilaterais registrados, a parcela com país BQD pela Freedom House vai de {pct(ac['parcela_atos_bqd_fh'].min())} ({ac.iloc[0]['governo']}) a {pct(ac['parcela_atos_bqd_fh'].max())} ({ac.iloc[-1]['governo']}); "
          f"a parcela de países BQD no mundo no mesmo período vai de {pct(ac['parcela_paises_bqd_no_mundo_fh'].min())} a {pct(ac['parcela_paises_bqd_no_mundo_fh'].max())}. " + cit("eixo2_acordos_por_governo", d=("D-053",), p=("Itamaraty",)), "",
          "### 4.5 Redes partidárias transnacionais", "",
          f"Foram registradas {milhar(len(rd))} participações de partidos brasileiros em {milhar(rd['rede'].nunique())} redes partidárias transnacionais de várias orientações (por exemplo, "
          + "; ".join(f"{r}: {milhar(n)} partido(s)" for r, n in rd.groupby('rede')['partido'].nunique().sort_values(ascending=False).head(3).items()) + "); participação em rede é relação, não indício de ilícito. "
          + cit("eixo2_redes_partidarias", d=("D-053",), p=("Foro de São Paulo", "Internacional", "Aliança Progressista", "Conferência Permanente", "Democrat", "Democrata")), ""]
    return L


def secao_eixo3() -> list:
    cob = tabela("eixo3_cobertura").iloc[0]
    t2 = tabela("eixo3_relator_2x2").set_index("recorte")
    te = tabela("eixo3_foro_testes")
    gp = tabela("eixo3_foro_governo_periodo")
    gp = gp[(gp["medida"] == "declinio") & gp["p_fisher"].notna()]
    g = te[(te["medida"] == "declinio") & (te["recorte"] == "todas as ações")].set_index("teste")
    ft = tabela("eixo3_foro_taxas")
    go = ft[(ft["medida"] == "declinio") & (ft["recorte"] == "todas as ações") & (ft["grupo_tipo"] == "governo_oposicao")].set_index("grupo")
    tot = t2.loc["total"]
    L = ["## 5. Eixo 3: poder institucional", "",
         "Entraram as partes que os dados em mãos permitem calcular. Ficam fora a nomeação para cargo com foro durante status de investigado ou denunciado (a base não tem cargos de ministro de Estado) e a decisão monocrática de alto impacto "
         "(a exportação do Corte Aberta cobre só ação penal, inquérito e petição penal); a tabela `decisoes_judiciais` está vazia. " + cit(d=("D-067",)), "",
         "### 5.1 Relator e presidente que indicou", "",
         f"Dos {milhar(cob['julgados_resolvidos'])} julgamentos de parlamentares no mérito, {pct(tot['taxa_indicados_pt'])} ({milhar(tot['condenados_indicados_pt'])} de {milhar(tot['julgados_indicados_pt'])}) dos decididos por ministro indicado por presidente do PT "
         f"terminaram em condenação, contra {pct(tot['taxa_outros'])} ({milhar(tot['condenados_outros'])} de {milhar(tot['julgados_outros'])}) dos decididos por ministro indicado por outro presidente ({pv(tot['p_fisher'])}). "
         + cit("eixo3_relator_2x2", "eixo3_relator_ministros", "eixo3_relator_presidentes", d=("D-067", "D-065"), p=("Corte Aberta: decisões em ações penais", "composição")), "",
         "### 5.2 Uso do foro", "",
         f"Em {milhar(cob['acoes_x_reu_no_foro'])} pares ação penal x réu parlamentar com vínculo confirmado, {milhar(cob['com_declinio'])} têm decisão de declínio de competência, {milhar(cob['declinio_com_reu_em_mandato'])} delas com o réu ainda em mandato na data. "
         f"A parcela com declínio é {pct(go.loc['governo', 'taxa'])} entre réus de partidos da base do governo e {pct(go.loc['oposicao', 'taxa'])} entre os da oposição ({pv(g.loc['governo x oposição (Fisher)', 'p_valor'])}) e difere entre partidos "
         f"({pv(g.loc['homogeneidade entre partidos', 'p_valor'])}); dentro de cada um dos {len(gp)} períodos presidenciais com os dois grupos a taxa é maior na oposição em {int((gp['taxa_oposicao'] > gp['taxa_governo']).sum())}, sem diferença significativa em nenhum período isolado. "
         + cit("eixo3_foro_taxas", "eixo3_foro_testes", "eixo3_foro_governo_periodo", d=("D-067",)), ""]
    return L


def secao_simetria() -> list:
    vs, vr, st, fil = ler("verificacoes_simetria"), ler("verificacao_resultado"), ler("status_pessoa_processo"), ler("filiacoes")
    filiados = set(fil["id_ator"])
    com = set(vs["achado_id"])
    from src.validacao.validar import STATUS_COM_SIMETRIA
    alvo = st[st["id_ator"].isin(filiados) & st["status"].isin(STATUS_COM_SIMETRIA)]
    cont = vr["resultado"].value_counts()
    L = ["## 6. Simetria", "",
         f"Dos {milhar(len(alvo))} status de atores com filiação que exigem verificação de simetria (denúncia, réu, condenação, candidatura indeferida, contas irregulares, cassação e sanção), {milhar(alvo['id_status'].isin(com).sum())} têm a verificação registrada; "
         f"as {milhar(len(vs))} verificações têm {milhar(len(vr))} resultados por partido, governo ou oposição: {'; '.join(f'{k}: {milhar(v)}' for k, v in cont.items())}. "
         "`sem_evidencia` só existe com busca registrada de zero resultados; `nao_verificado` indica grupo sem universo lido ou sem busca. "
         + cit(d=("D-007", "D-048", "D-065"), p=("STF", "Senado", "Câmara dos Deputados")) + " *(Fonte: `data/base/verificacoes_simetria.csv`, `data/base/verificacao_resultado.csv`)*", ""]
    return L


P_FONTES = [("etica_homogeneidade", "p_valor"), ("etica_correlacao", "p_permutacao"), ("etica_governo_periodo", "p_fisher"), ("eixo1_homogeneidade", "p_valor"),
            ("ideologia_correlacao", "p_permutacao"), ("eixo1_parlamentares_homogeneidade", "p_valor"), ("eixo1_parlamentares_correlacao", "p_permutacao"),
            ("eixo1_parlamentares_governo_periodo", "p_fisher"), ("stf_desfechos_homogeneidade", "p_valor"), ("eixo3_relator_2x2", "p_fisher"), ("eixo3_foro_testes", "p_valor"),
            ("eixo3_foro_governo_periodo", "p_fisher")]


def testes() -> pd.DataFrame:
    linhas = []
    for nome, col in P_FONTES:
        d = tabela(nome)
        d = d[d[col].notna()]
        for r in d.itertuples():
            linhas.append({"tabela": nome, "p": getattr(r, col)})
    return pd.DataFrame(linhas)


def secao_interpretacao() -> list:
    t = testes()
    n, k = len(t), int((t["p"] < 0.05).sum())
    por_tab = t.groupby("tabela")["p"].agg(lambda x: f"{int((x < 0.05).sum())} de {len(x)}")
    corr = pd.concat([tabela("etica_correlacao")[["partidos", "p_permutacao"]], tabela("eixo1_parlamentares_correlacao")[["partidos", "p_permutacao"]], tabela("ideologia_correlacao")[["partidos", "p_permutacao"]]])
    gp = tabela("eixo3_foro_governo_periodo")
    gp = gp[(gp["medida"] == "declinio") & gp["p_fisher"].notna()]
    eg = tabela("etica_governo_periodo")
    eg = eg[(eg["medida"] == "representado") & (eg["periodo"] != "Todo o período") & (eg["p_fisher"] < 0.05)]
    sdh = tabela("stf_desfechos_homogeneidade")
    t2 = tabela("eixo3_relator_2x2").set_index("recorte").loc["total"]
    gpe = tabela("eixo1_parlamentares_governo_periodo")
    gpe = gpe[(gpe["medida"] == "tcu_acumulado") & (gpe["periodo"] == "Todo o período")].iloc[0]
    cm = tabela("eixo2_comercio_por_governo")
    crescente = bool((cm["parcela_exportacoes_bqd_fh"].diff().dropna() > 0).all())
    L = ["## 7. Interpretação (separada dos resultados)", "",
         "Esta seção lê os resultados acima; não produz registro novo e pode ser lida separadamente. Cada leitura indica de onde vem.", "",
         f"1. **Muitos testes, poucos casos.** As tabelas trazem {milhar(n)} testes (homogeneidade, correlação, Fisher), dos quais {milhar(k)} ({pct(k / n)}) têm p abaixo de 0,05; ao acaso, sem correção, se esperariam cerca de {pct(0.05)}. "
         f"Os testes não são independentes (os mesmos partidos entram em recortes vizinhos). A maior parte vem das comparações entre partidos no universo de todos os candidatos (seção 3.3), com dezenas de milhares de candidaturas, em que o teste detecta diferenças pequenas de taxa e a composição de candidatos de cada partido pesa; "
         "esses testes descrevem que as taxas diferem, não por quê. "
         f"Distribuição dos com p < 0,05 por tabela: {'; '.join(f'{nome} ({v})' for nome, v in por_tab.items() if not v.startswith('0 '))}. "
         "Diferenças isoladas não sustentam conclusão; importam as que se repetem em recortes diferentes.", "",
         f"2. **Posição ideológica.** Nas {len(corr)} correlações entre o escore ideológico do partido e uma taxa (STF, ética, TCU, TSE), {int((corr['p_permutacao'] < 0.05).sum())} têm p abaixo de 0,05. "
         f"Com o número de partidos disponível ({milhar(corr['partidos'].min())} a {milhar(corr['partidos'].max())}), o teste só distinguiria associações fortes; o resultado diz que nenhuma associação forte aparece, não que não exista nenhuma.", "",
         "3. **Onde há diferença entre partidos, ela se concentra.** A diferença entre partidos na parcela alvo de representação nos Conselhos de Ética vem de poucos casos: o PSOL, com poucos parlamentares e muitas representações, "
         "e o antigo PL e o PRONA na 52ª legislatura (episódio das ambulâncias, 2005-2006), conforme a sensibilidade sem a 52ª legislatura em D-063. "
         f"A diferença no declínio de competência tem o mesmo sentido (maior na oposição) em {int((gp['taxa_oposicao'] > gp['taxa_governo']).sum())} dos {len(gp)} períodos presidenciais com os dois grupos, mas nenhum período isolado a confirma; a medida não distingue o motivo do declínio.", "",
         f"4. **Governo e oposição.** Na ética, dos períodos presidenciais com diferença significativa na parcela alvo de representação, {len(eg)} têm sentidos diferentes ("
         + "; ".join(f"{r.periodo}: maior {'na base do governo' if r.taxa_governo > r.taxa_oposicao else 'na oposição'}" for r in eg.itertuples())
         + f"), o que não indica padrão estável. No STF, a proporção de condenados entre julgados no mérito não difere entre base do governo e oposição ({pv(sdh.iloc[1]['p_valor'])}), nem as contas irregulares do TCU ({pv(gpe['p_fisher'])}).", "",
         f"5. **Desfechos de processo.** Entre os parlamentares julgados no mérito no STF, a proporção de condenados não difere entre partidos ({pv(sdh.iloc[0]['p_valor'])}) nem entre relatores indicados por presidentes do PT e de outros partidos ({pv(t2['p_fisher'])}); "
         "com dezenas de julgamentos por recorte, o teste não tem poder para diferenças moderadas.", "",
         f"6. **Eixo 2.** As parcelas de votos, operações de crédito, exportações e atos bilaterais com países BQD variam entre governos, em sentidos diferentes conforme o indicador e a régua (Freedom House ou V-Dem). "
         f"A parcela de exportações para países BQD {'cresce a cada governo' if crescente else 'varia entre governos'} ({pct(cm['parcela_exportacoes_bqd_fh'].iloc[0])} a {pct(cm['parcela_exportacoes_bqd_fh'].iloc[-1])}), "
         f"enquanto a parcela das exportações para a China passa de {cm['principais_destinos_bqd_fh'].iloc[0].split(';')[0].replace('CHN ', '').replace('.', ',')} a {cm['principais_destinos_bqd_fh'].iloc[-1].split(';')[0].replace('CHN ', '').replace('.', ',')} no mesmo intervalo; "
         "o estudo não atribui essa variação a decisão de governo.", "",
         "7. **O que os dados não sustentam.** Não há, nestes dados, base para afirmar que um partido, espectro ou governo concentre esquemas ilícitos, apoio a países BQD ou abuso de poder institucional. "
         "Também não sustentam o contrário: as coberturas são parciais (por exemplo, inquéritos sem lista de réus, primeira instância e tribunais estaduais sem universo lido, sanções administrativas só de pessoas jurídicas) e ausência de registro não é evidência de ausência. "
         "As limitações completas estão em `docs/limitacoes.md`.", ""]
    return L


def secao_limitacoes() -> list:
    txt = (RAIZ / "docs" / "limitacoes.md").read_text(encoding="utf-8")
    cab = [m for m in re.findall(r"^### (.+)$", txt, flags=re.M) if "datajud" not in m.lower()]  # DataJud nunca é citado em relatório (CLAUDE.md, seção 6)
    return ["## 8. Limitações", "",
            "As limitações conhecidas (vieses) e a cobertura medida na base estão em `docs/limitacoes.md`, que acompanha este relatório. Seções da parte gerada: " + "; ".join(cab) + ".", ""]


def secao_reproducao() -> list:
    return ["## 9. Reprodução", "",
            f"Este relatório é gerado por `python -m src.relatorios.relatorio_final` a partir de `data/base` e de `relatorios/tabelas` (commit {commit()}). A ordem completa de geração está em `docs/nota_metodologica.md`, seção 7. "
            "Os números mudam se a base mudar; o commit identifica a versão.", ""]


def montar() -> str:
    cab = ["# Relatório final: fatores institucionais e relações entre agentes dos Poderes, Brasil, 2003 a 2026", "",
           f"Gerado por código a partir da base auditável (commit {commit()}). Linguagem descritiva e a mesma para atores de qualquer partido; status formal de pessoa nunca é culpa. "
           "Resultados (seções 2 a 6) ficam separados da interpretação (seção 7). Recomenda-se revisão jurídica antes de qualquer publicação. "
           "Documentos que acompanham: `docs/nota_metodologica.md`, `docs/limitacoes.md` e `relatorios/linha_do_tempo.md`.", ""]
    corpo = secao_escopo() + secao_base() + ["## 3. Eixo 1: esquemas ilícitos com trâmite formal", ""] + secao_eixo1_stf() + secao_eixo1_etica() + secao_eixo1_tcu_tse() + secao_eixo1_ideologia_imprensa()
    corpo += secao_eixo2() + secao_eixo3() + secao_simetria() + secao_interpretacao() + secao_limitacoes() + secao_reproducao()
    ap_a = ["## Apêndice A. Fontes citadas", ""] + F.apendice() + [""]
    ap_b = ["## Apêndice B. Tabelas de saída citadas", ""] + [f"- `{t}`" for t in sorted(F.tabelas)] + [""]
    return "\n".join(cab + corpo + ap_a + ap_b)


def run() -> None:
    SAIDA.write_text(montar(), encoding="utf-8")
    print(f"escrito: {SAIDA.relative_to(RAIZ).as_posix()}; fontes citadas: {len(F.citadas)}; tabelas: {len(F.tabelas)}")


if __name__ == "__main__":
    run()
