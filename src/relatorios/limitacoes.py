"""Gera a parte automática de docs/limitacoes.md (entre os marcadores INICIO-GERADO e FIM-GERADO):
cobertura da base, buscas registradas, lacunas medidas e avisos do validador. A parte escrita à mão,
acima do marcador, não é alterada.

Uso:
    python -m src.relatorios.limitacoes
"""

import csv
import re
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, ler
from src.esquema import TABELAS
from src.validacao.validar import validar

DOC = RAIZ / "docs" / "limitacoes.md"
CURADORIA = RAIZ / "data" / "curadoria"
INICIO, FIM = "<!-- INICIO-GERADO -->", "<!-- FIM-GERADO -->"


def _n_csv(caminho: Path) -> int:
    return sum(1 for _ in csv.DictReader(caminho.open(encoding="utf-8"))) if caminho.exists() else 0


def _linhas_partidos(base: Path) -> list[str]:
    inst = ler("instituicoes", base)
    partidos = inst[inst["tipo_instituicao"] == "partido"]
    res = CURADORIA / "partidos_resolucao_siglas.csv"
    linhas = [f"- Partidos: {len(partidos)} registros no TSE, com {len(ler('denominacoes_partido', base))} denominações e "
              f"{len(ler('relacoes', base).query('tipo_relacao in [\"fundiu_se_em\", \"incorporado_por\"]'))} fusões ou incorporações "
              "(fonte: página de partidos do TSE, lida no navegador; D-015). A página cobre mudanças a partir da Lei 9.096/1995."]
    if res.exists():
        r = pd.read_csv(res, dtype=str).fillna("")
        soma = {c: int(pd.to_numeric(r[c]).sum()) for c in r.columns if c.startswith("registros_")}
        total = sum(soma.values())
        linhas.append(
            f"- Ligação de siglas das fontes ao partido na data: {soma.get('registros_vigencia', 0)} de {total} na vigência da sigla; "
            f"{soma.get('registros_partido_existente', 0)} com a sigla fora da vigência, mas com um único partido existente na data "
            f"(fontes que gravam a sigla atual em registros antigos); {soma.get('registros_mais_proxima', 0)} pela denominação mais próxima no tempo; "
            f"{soma.get('registros_sem_correspondencia', 0)} sem correspondência. Siglas ligadas pelo nome publicado pela fonte: "
            f"{', '.join(f'{a} ({b})' for a, b in zip(r['sigla_fonte'], r['apelido_para_siglas_tse']) if b) or 'nenhuma'}.")
    return linhas


def texto(base: Path = BASE) -> str:
    falhas, avisos = validar(base)
    contagens = [(t.nome, len(ler(t.nome, base))) for t in TABELAS]
    linhas = [INICIO, "## Parte gerada: cobertura da base", "",
              "Gerada por `python -m src.relatorios.limitacoes`. Não editar à mão.", "",
              "### Registros por tabela", "", "| Tabela | Registros |", "|---|---:|"]
    linhas += [f"| `{n}` | {k} |" for n, k in contagens if k]
    vazias = [n for n, k in contagens if not k]
    linhas += ["", f"Tabelas ainda vazias ({len(vazias)}): {', '.join(f'`{n}`' for n in vazias)}.", ""]

    buscas = ler("buscas", base)
    linhas += ["### Buscas", "", f"- {len(buscas)} buscas registradas; {int((buscas['n_resultados'] == '0').sum())} com zero resultados."]
    fontes = ler("fontes", base)
    for fonte, grupo in buscas.groupby("fonte_dados"):
        linhas.append(f"- {fonte}: {len(grupo)} buscas, coleta de {grupo['data'].max()}.")
    linhas.append("")

    cargos, filiacoes, atores = ler("cargos", base), ler("filiacoes", base), ler("atores", base)
    if len(cargos):
        sup = cargos["cargo"].str.contains("suplente", case=False)
        sem_fil = set(atores["id_ator"]) - set(filiacoes["id_ator"])
        linhas += [
            "### Lacunas medidas na etapa E1 (Câmara e Senado)", "",
            f"- Mandatos de suplente: {int(sup.sum())} de {len(cargos)} cargos. No Senado, o mandato de suplente não indica que houve "
            "exercício; na Câmara, o cargo de suplente só aparece quando há registro no histórico.",
            f"- Atores sem nenhuma filiação registrada: {len(sem_fil)} de {len(atores)}; "
            f"{int(cargos[cargos['id_ator'].isin(sem_fil)].groupby('id_ator')['cargo'].apply(lambda s: s.str.contains('suplente').all()).sum())} "
            "deles só têm mandato de suplente no Senado, e o Senado não publica filiação para quem não exerceu.",
            f"- Filiações da Câmara cobrem só o período de mandato (fonte: histórico do deputado); fora do mandato, a filiação não é observada.",
            f"- Pares Câmara e Senado identificados como a mesma pessoa automaticamente: {_n_csv(CURADORIA / 'equivalencias_atores_automaticas.csv')}; "
            f"pares ambíguos aguardando revisão: {_n_csv(CURADORIA / 'equivalencias_atores_pendentes.csv')} "
            "(`data/curadoria/equivalencias_atores_pendentes.csv`). Até a revisão, cada lado é um ator separado.",
            *_linhas_partidos(base),
            "",
        ]
        uni = ler("universo_partidos", base)
        if len(uni):
            por_ano = uni.groupby("ano").size()
            linhas += [f"- Universo de partidos por ano: de {por_ano.min()} a {por_ano.max()} partidos ({por_ano.index.min()} a {por_ano.index.max()}).", ""]

    q = ler("qualidade_democratica", base)
    if len(q):
        from src.normalizacao.reguas import classificar
        cob = q.groupby("indice").agg(paises=("pais_iso3", "nunique"), ano_min=("ano", "min"), ano_max=("ano", "max"))
        linhas += ["### Réguas externas (etapa E2)", ""]
        linhas += [f"- `{i}`: {r.paises} países, de {r.ano_min} a {r.ano_max}." for i, r in cob.iterrows()]
        par = q[q["indice"].isin(["vdem_row", "fh_status"])].copy()
        par["baixa"] = [classificar(i, v) == "baixa" for i, v in zip(par["indice"], par["valor"])]
        ambos = par.pivot_table(index=["pais_iso3", "ano"], columns="indice", values="baixa", aggfunc="first").dropna()
        so_vdem = set(q.loc[q["indice"] == "vdem_row", "pais_iso3"]) - set(q.loc[q["indice"] == "fh_status", "pais_iso3"])
        so_fh = set(q.loc[q["indice"] == "fh_status", "pais_iso3"]) - set(q.loc[q["indice"] == "vdem_row", "pais_iso3"])
        linhas += [
            f"- Concordância entre as réguas na classificação \"baixa qualidade democrática\" (V-Dem RoW 0 ou 1; Freedom House Não Livre): "
            f"{(ambos['vdem_row'] == ambos['fh_status']).mean() * 100:.1f}%".replace(".", ",") + f" dos {len(ambos)} pares país-ano com as duas réguas. Os relatórios mostram as duas, sem combiná-las.",
            f"- A Freedom House não publicou abertamente a edição 2026 (ano de 2025): os dados passaram a ser atendidos por pedido por e-mail. "
            "O ano de 2025 só tem V-Dem.",
            f"- Países só no V-Dem: {len(so_vdem)} ({', '.join(sorted(so_vdem))}). Países só na Freedom House: {len(so_fh)} "
            "(a maioria microestados que o V-Dem não cobre; inclui Sérvia e Montenegro, SCG, que o V-Dem registra como Sérvia). Códigos de país seguem o V-Dem (ISO 3166-1 alfa-3 quando existe); a ligação dos nomes da "
            "Freedom House está em `data/curadoria/paises_freedom_house.csv`.",
            "- Os valores do V-Dem são estimativas de modelo com incerteza (intervalos publicados pelo V-Dem, não importados); valores próximos ao limiar "
            "entre categorias devem ser lidos com cautela.",
            "",
        ]

    ops = ler("operacoes_exportacao_bndes", base)
    if len(ops):
        g = ops.groupby("linha_de_apoio").agg(linhas=("id_operacao", "size"), operacoes=("numero_operacao", "nunique"),
                                              inicio=("data_contratacao", "min"), fim=("data_contratacao", "max"))
        linhas += ["### BNDES, operações de exportação (etapa E3)", ""]
        linhas += [f"- {i}: {r.linhas} linhas (subcréditos) de {r.operacoes} operações, contratadas de {r.inicio} a {r.fim}." for i, r in g.iterrows()]
        sem_valor = ops[ops["valor"] == ""]
        linhas += [
            f"- O arquivo aberto de pós-embarque de bens não publica valores ({len(sem_valor)} linhas sem valor): para bens, só é possível contar operações.",
            f"- {int((ops['pais_iso3'] == '').sum())} linhas com destino \"diversos\", sem país definido.",
            "- O nome do tomador do financiamento (mutuário) não é publicado; só a categoria (ente público ou privado).",
            "- O arquivo de pré-embarque financia o exportador no Brasil e não informa o país de destino; fica só no dado bruto.",
            "- Valores em moeda da operação, nominais, sem correção; linhas contratadas antes de 2000 não têm régua de qualidade democrática.",
            "- As condições de garantia (seguro de crédito, Fundo de Garantia à Exportação, convênio de créditos recíprocos) aparecem só como texto do BNDES.",
            "",
        ]

    todos = ler("processos", base)
    sigla = dict(zip(ler("instituicoes", base)["id_instituicao"], ler("instituicoes", base)["sigla"]))
    proc = todos[todos["id_tribunal"].map(sigla) == "STJ"]
    if len(proc):
        from src.normalizacao.datajud_stj import no_universo, regras_assuntos
        regras = regras_assuntos()
        proc = proc.copy()
        proc["universo"] = [no_universo([x.split(":")[0] for x in s.split("; ") if x], regras) for s in proc["assuntos_tpu"]]
        proc["ano"] = proc["data_autuacao"].str[:4]
        uni = proc[(proc["universo"] == "sim") & (proc["ano"] >= "2003")]
        ate_2012 = int((uni["ano"] <= "2012").sum())
        linhas += [
            "### STJ pelo DataJud (etapa E4)", "",
            f"- {len(proc)} ações penais e inquéritos do STJ na API pública do DataJud; {len(uni)} no universo do eixo 1 desde 2003 "
            f"(tipos penais do protocolo, pela tabela `data/curadoria/assuntos_tpu_eixo1.csv`); {int((proc['universo'] == 'revisar').sum())} com assuntos "
            "genéricos, a revisar pela fonte primária.",
            f"- Cobertura histórica baixa: só {ate_2012} processos do universo autuados de 2003 a 2012. O DataJud concentra processos com movimentação "
            "recente; processos antigos e baixados podem não estar na base do CNJ. O universo do STJ anterior a 2013 está incompleto.",
            "- A API pública só traz processos sem sigilo; processos sigilosos não aparecem.",
            "- A API não traz nomes de partes, e o termo de uso impede cruzar seus dados com pessoas (D-022). Status de pessoas depende de fonte primária.",
            "- O portal do STJ (consulta processual e jurisprudência) exige verificação de robô; a leitura da fonte primária de cada processo citado "
            "precisa ser feita por uma pessoa. A URL gravada segue o formato do portal e não foi conferida por script.",
            "- Fases processuais: só declínio de competência e arquivamento de procedimento investigatório. O trânsito em julgado não foi usado, porque "
            "no STJ aparece a cada recurso interno encerrado.",
            "",
        ]

    linhas += _linhas_stf(todos[todos["id_tribunal"].map(sigla) == "STF"], base)

    em = ler("emendas_parlamentares", base)
    if len(em):
        ev = ler("eventos", base)
        ind = em[em["tipo_emenda"].str.startswith("Emenda Individual")]
        ident = ind[ind["autor_fonte"] != "Sem informação"]
        rel = em[em["tipo_emenda"] == "Emenda de Relator"]
        linhas += [
            "### Portal da Transparência (etapa E6)", "",
            f"- Acordos de leniência: {int((ev['tipo_evento'] == 'acordo_leniencia').sum())} acordos da CGU. Sanções administrativas na base: "
            f"{int((ev['tipo_evento'] == 'sancao_administrativa').sum())} (todas as do CNEP a pessoas jurídicas e, do CEIS, só as de empresas que já estão "
            "na base; o CEIS completo fica no dado bruto, D-027). Sanções a pessoas físicas não entram (LGPD).",
            f"- Emendas parlamentares: {len(em)} linhas (agregadas por emenda, localidade e função), de {em['ano'].min()} a {em['ano'].max()}; "
            "o arquivo da CGU não traz anos anteriores a 2014.",
            f"- Emendas individuais: {int((ind['autor_fonte'] == 'Sem informação').sum())} linhas sem autor na fonte; das {len(ident)} com autor, "
            f"{(ident['id_ator'] != '').mean() * 100:.1f}%".replace(".", ",") + " ligadas a um parlamentar da base (nome e mandato no ano). "
            "As demais têm grafia diferente (nome civil contra nome parlamentar) ou homônimos com mandato no mesmo ano.",
            f"- Emendas de relator: {len(rel)} linhas, com autor publicado só como \"RELATOR GERAL\" ou sem informação; o arquivo não identifica "
            "os parlamentares que indicaram os recursos. Emendas de bancada e de comissão não têm autor individual.",
            "- O arquivo de emendas por favorecido (com nomes de pessoas físicas) e o de convênios ficam só no dado bruto.",
            "",
        ]

    vm_todos = ler("votos_multilaterais", base)
    siglas = dict(zip(ler("instituicoes", base)["id_instituicao"], ler("instituicoes", base)["sigla"]))
    vm = vm_todos[vm_todos["id_organismo"].map(siglas) == "AGNU"]
    if len(vm):
        res = vm.drop_duplicates("resolucao")
        linhas += [
            "### Votos em organismos multilaterais (etapa E8, bloco A)", "",
            f"- Assembleia Geral da ONU: {len(res)} resoluções adotadas por voto nominal de {res['data'].min()[:4]} a {res['data'].max()[:4]}, "
            f"com o voto de todos os países ({len(vm)} votos); critério em `docs/lista_e8_para_revisao.md`. "
            + "; ".join(f"{k}: {n}" for k, n in res["criterio_inclusao"].value_counts().items()) + ".",
            "- Resoluções adotadas sem votação (por consenso) e votos sobre parágrafos isolados não constam do conjunto da ONU.",
            "- O critério \"cita país da América Latina\" é aplicado ao pé da letra e inclui resoluções de desenvolvimento; a análise separa pelo título.",
            "",
        ]
    linhas += _linhas_cdh(vm_todos[vm_todos["id_organismo"].map(siglas) == "CDH"])
    linhas += _linhas_oea(vm_todos[vm_todos["id_organismo"].map(siglas) == "AG/OEA"])
    linhas += _linhas_redes(base)
    linhas += _linhas_acordos(base)
    linhas += _linhas_tse(base)
    linhas += _linhas_e9(base)
    linhas += _linhas_simetria(base)
    linhas += _linhas_eixo2()
    linhas += _linhas_imprensa()
    linhas += _linhas_eixo1_universos()
    linhas += _linhas_ideologia()
    linhas += _linhas_stf_composicao()

    linhas += ["### Validador", "", f"- {len(falhas)} falha(s) e {len(avisos)} aviso(s) na última geração."]
    linhas += [f"- Aviso: {a}" for a in avisos[:20]]
    if len(avisos) > 20:
        linhas.append(f"- … e mais {len(avisos) - 20} avisos.")
    linhas += ["", FIM]
    return "\n".join(linhas)


def _linhas_cdh(vm: pd.DataFrame) -> list[str]:
    """Bloco A2: Conselho de Direitos Humanos da ONU (D-044)."""
    if not len(vm):
        return []
    res = RAIZ / "data" / "staging" / "conselho_dh" / "resolucoes.csv"
    r = pd.read_csv(res, dtype=str, keep_default_na=False) if res.exists() else pd.DataFrame(columns=["criterio", "estado", "confere"])
    sel = r[r["criterio"] != ""]
    nao_confere = sel[(sel["estado"] == "votacao") & (sel["confere"] != "True")]
    bra = vm[vm["pais_iso3"] == "BRA"]
    return [
        f"- Conselho de Direitos Humanos: {vm['resolucao'].nunique()} resoluções adotadas por votação registrada de {vm['data'].min()[:4]} a "
        f"{vm['data'].max()[:4]}, com o voto de todos os membros ({len(vm)} votos); o Brasil votou em {bra['resolucao'].nunique()} (nos demais anos "
        "não era membro). Mesmo critério da Assembleia Geral; voto de cada país conferido com o placar escrito na resolução (D-044).",
        f"- Das {len(sel)} resoluções selecionadas, {int((sel['estado'] == 'sem_votacao').sum())} foram adotadas sem votação e não geram voto por país; "
        f"{int((sel['estado'] == 'sem_registro_de_adocao').sum())} não trazem o registro de adoção no texto lido; "
        f"{len(nao_confere)} com lista de votos que não bate com o placar do próprio documento ficam fora (" + ", ".join(nao_confere["simbolo"]) + ").",
        "- Lacunas de fonte: o relatório da 1ª sessão (2006, A/61/53) e as resoluções das sessões especiais S-13 e S-17 não estão no repositório "
        "de documentos da ONU; as sessões especiais S-1 a S-11 só entram quando estão nos relatórios anuais.",
        "",
    ]


def _linhas_oea(vm: pd.DataFrame) -> list[str]:
    """Bloco A3: Assembleia Geral da OEA (D-036)."""
    if not len(vm):
        return []
    stg = RAIZ / "data" / "staging" / "oea"
    cur = pd.read_csv(CURADORIA / "oea_resolucoes_ag_curadoria.csv", dtype=str, keep_default_na=False)
    vot = pd.read_csv(stg / "votacoes_resumo.csv", dtype=str, keep_default_na=False) if (stg / "votacoes_resumo.csv").exists() else pd.DataFrame()
    sem_ata = pd.read_csv(stg / "resolucoes_sem_ata.csv", dtype=str, keep_default_na=False) if (stg / "resolucoes_sem_ata.csv").exists() else pd.DataFrame()
    reg = vm[vm["modalidade"] == "votacao_registrada"]
    cons = vm[vm["modalidade"] == "sem_votacao"]
    linhas = [
        "- Assembleia Geral da OEA: " + f"{vm['resolucao'].nunique()} resoluções ou votações na base ({reg['resolucao'].nunique()} por votação registrada, "
        f"{cons['resolucao'].nunique()} sem votação no plenário), de {vm['data'].min()[:4]} a {vm['data'].max()[:4]}; curadoria item a item "
        f"(`data/curadoria/oea_resolucoes_ag_curadoria.csv`): {int((cur['decisao_final'] == 'inclui').sum())} incluídas, "
        f"{int((cur['decisao_final'] == 'exclui').sum())} excluídas e {int((cur['decisao_final'] == '').sum())} aguardando decisão do autor (fora da base).",
    ]
    if len(vot):
        vot = vot[vot["decisao"] == "inclui"]
        nominais = vot[vot["lidos_sim"].astype(int) + vot["lidos_nao"].astype(int) + vot["lidos_abstencao"].astype(int) > 0]
        nao = nominais[nominais["confere"] != "True"]
        linhas.append(
            f"- Votações incluídas, localizadas nas atas: {len(vot)} (`data/curadoria/oea_votacoes.csv`); em {int((nominais['confere'] == 'True').sum())} das "
            f"{len(nominais)} chamadas nominais a contagem das respostas bate com o placar oficial e entra o voto de cada país. "
            + ("Não bate em: " + "; ".join(f"{r.data} ({r.simbolo or r.descricao[:60]}: placar {r.placar_sim}/{r.placar_nao}/{r.placar_abstencao}, "
                                           f"lidos {r.lidos_sim}/{r.lidos_nao}/{r.lidos_abstencao})" for r in nao.itertuples())
               + "; nesses casos só entra o voto do Brasil, lido na fala da delegação. " if len(nao) else "")
            + "A votação de mão erguida da AG/RES. 2 (XXXVII-E/09) (suspensão de Honduras, 4 de julho de 2009, 33 votos afirmativos) não individualiza os votos e não gera linha por país.")
    linhas += [
        "- Resolução sem chamada nominal na ata da sessão é registrada como adotada sem votação: `consenso` para o Brasil ou `consenso_com_nota` "
        "quando há nota de rodapé do país no texto certificado; os demais países só aparecem quando registraram nota. Votações na Comissão Geral "
        "(antes do plenário) não constam das atas lidas.",
        "- A autoria da nota é o primeiro Estado membro citado no início dela; notas \"Ídem\" e \"Véase nota N\" herdam o autor. No volume de 2010 "
        "o leitor não traz as chamadas de nota, e a nota é ligada à resolução que cita o mesmo Estado no título.",
        f"- Notas de rodapé do Brasil nas resoluções incluídas: {int((cons['pais_iso3'].eq('BRA') & cons['voto'].eq('consenso_com_nota')).sum())}.",
    ]
    if len(sem_ata):
        linhas.append("- Sem ata da sessão (download recusado pelo servidor da OEA: 2005, 2007, 2013, 2014 e 2015), não dá para dizer se houve votação; "
                      "estas resoluções incluídas ficam fora da base: " + ", ".join(sem_ata["simbolo"]) + ".")
    linhas += ["- Volumes de resoluções de 2003, 2005 e 2006 não foram obtidos (erro do servidor da OEA); o segundo arquivo da sessão extraordinária de 2009 veio do repositório de documentos da OEA, porque o link do índice recusa o acesso; "
               "resoluções do Conselho Permanente ainda não foram indexadas.", ""]
    return linhas


def _linhas_stf(proc: pd.DataFrame, base: Path) -> list[str]:
    """Etapa E5: STF pelo Corte Aberta (D-037, D-038)."""
    if not len(proc):
        return []
    from src.normalizacao.stf import CUR_ASSUNTOS, universo
    cur = pd.read_csv(CUR_ASSUNTOS, dtype=str, keep_default_na=False)
    u = universo(proc, dict(zip(cur["caminho_stf"], cur["decisao"])))
    tri = RAIZ / "data" / "staging" / "stf" / "universo_stf.csv"
    t = pd.read_csv(tri, dtype=str, keep_default_na=False) if tri.exists() else pd.DataFrame(columns=["triagem"])
    fases = ler("fases_processo", base)
    fases = fases[fases["id_processo"].isin(proc["id_processo"])]
    sim = proc[u == "sim"]
    return [
        "### STF pelo Corte Aberta (etapa E5)", "",
        f"- {len(proc)} processos ({', '.join(f'{k}: {n}' for k, n in proc['classe'].value_counts().items())}): ações penais e inquéritos com "
        "decisão de 08/01/2003 a 23/09/2026, petições de ramo penal com decisão de 05/02/2003 a 24/09/2026, e os em tramitação nas datas das "
        f"exportações (D-037, D-045). No universo do eixo 1: {len(sim)} (tipos do protocolo pelo assunto); {int((u == 'revisar').sum())} a revisar; "
        f"{int((u == 'nao').sum())} fora; {int((u == 'antes_de_2003').sum())} autuados antes de 2003.",
        "- O Corte Aberta traz um só assunto por processo. Em 1.774 ações penais o assunto é o genérico \"Direito Processual Penal | Ação Penal\", "
        "e o tipo penal só aparece na fonte primária. Triagem pelo texto das decisões (não decide nada): "
        + "; ".join(f"{k}: {n}" for k, n in t["triagem"].replace("", pd.NA).dropna().value_counts().items()) + ". Os indícios de fora do protocolo "
        "vêm sobretudo das ações penais de 2023 a 2026 sobre crimes contra o Estado Democrático de Direito (CP, Título XII).",
        "- Regra de assuntos em `data/curadoria/assuntos_stf_eixo1.csv` (D-038): capítulos do Título XI do Código Penal entram inteiros, como "
        "diz o protocolo (inclusive desobediência, desacato e sonegação de contribuição previdenciária); crimes eleitorais só entram como "
        "conexos (art. 350); crimes de responsabilidade de prefeitos (Decreto-Lei 201/1967) entram por emenda ao protocolo (D-039), também no STJ.",
        f"- Fases: {len(fases)} registros de decisões com correspondência inequívoca ("
        + "; ".join(f"{k}: {n}" for k, n in fases["fase"].value_counts().items()) + "). O julgamento de mérito da ação penal "
        "(procedente ou improcedente) é registrado sem distinguir réus; o status de cada pessoa depende da fonte primária.",
        "- Petições criminais: o assunto costuma ser processual (investigação, prisão, busca e apreensão, quebra de sigilo) e não diz o crime; "
        "por isso a maioria fica a revisar. O arquivamento de petição investigativa é registrado com a fase de arquivamento de procedimento "
        "investigatório (vocabulário: arquivamento de inquérito).",
        "- Decisões em segredo de justiça aparecem só como \"Decisão (segredo de justiça)\" e não geram fase. O campo de sigilo do processo não vem na exportação.",
        "- A página de dados abertos do STF (bases de processos recebidos e baixados, com todos os assuntos de cada processo) corta as "
        "exportações em 5 milhões de células: os arquivos de cinco anos (2006 a 2025) chegam incompletos, em ordem alfabética de classe, "
        "sem inquéritos. Só os de 2026 estão completos e foram registrados; neles, 22 de 140 AP e Inq trazem mais de um assunto.",
        "- Número único CNJ só para os processos em tramitação (planilha do acervo). A URL gravada é a consulta por classe e número do portal, "
        "conferida no navegador para a AP 470.",
        "",
    ]


def _linhas_redes(base: Path) -> list[str]:
    """Bloco D: filiação de partidos brasileiros a redes transnacionais (D-040)."""
    rel = ler("relacoes", base)
    rel = rel[rel["tipo_relacao"].isin(["membro_de", "observador_de"])]
    if not len(rel):
        return []
    inst = ler("instituicoes", base)
    redes = inst[inst["tipo_instituicao"].isin(["rede_partidaria_transnacional", "forum_politico_nao_partidario"])]
    com = set(rel["destino_id"])
    sem = redes[~redes["id_instituicao"].isin(com)]
    return [
        "### Redes partidárias transnacionais (etapa E8, bloco D)", "",
        f"- {len(rel)} períodos de filiação ou observação de partidos brasileiros em {len(com)} redes, lidos nas listas de membros publicadas "
        "pelas próprias redes, em cópias anuais do Internet Archive (D-040). As datas são a primeira e a última observação no arquivo, não "
        "as datas de filiação ou de saída; data final vazia quer dizer que o partido está na cópia de 2026.",
        "- Cobertura desigual: o arquivo não tem lista de membros utilizável do Foro de São Paulo antes de 2014, da Internacional Socialista "
        "de 2003 a 2018 (as páginas antigas não trazem a lista no texto), da International Democrat Union de 2007 a 2017 (lista carregada por script, "
        "fora da cópia), da Aliança Progressista antes de 2014, da UPLA depois de 2003, nem da ODCA e da Internacional Democrata Centrista "
        "depois de 2016 e de 2013. Ausência de cópia não é ausência de filiação.",
        "- Listas desatualizadas pela própria rede são registradas como estão (por exemplo, \"PPS\" no Foro de São Paulo depois da mudança "
        "para Cidadania; \"Democratas\" na International Democrat Union depois da fusão no União Brasil); a sigla é ligada ao partido do "
        "registro no TSE.",
        "- Sem partido brasileiro nas listas lidas: " + (", ".join(sorted(sem["nome"])) if len(sem) else "nenhuma rede") + ". O Grupo de "
        "Puebla e o Foro de Madri reúnem pessoas; a participação de pessoas fica para etapa própria.",
        "- Filiação a rede é relação política pública; o relatório não a liga a registros dos eixos 1 e 3.",
        "",
    ]


def _linhas_acordos(base: Path) -> list[str]:
    """Bloco B: atos bilaterais do Concórdia (D-041)."""
    a = ler("acordos_bilaterais", base)
    if not len(a):
        return []
    from src.normalizacao.concordia import montar
    from src.base import RegistroIds
    c = montar(RegistroIds())["contagem"]
    desde = a[a["data_assinatura"] >= "2003"]
    return [
        "### Atos bilaterais do Brasil (etapa E8, bloco B)", "",
        f"- {len(a)} atos bilaterais com um país como outra parte, de {a['data_assinatura'].min()[:4]} a {a['data_assinatura'].max()[:4]}, "
        f"com {a['pais_iso3'].nunique()} países; {len(desde)} celebrados de 2003 em diante (Concórdia, D-041).",
        f"- Fora da tabela: {c['organismo']} atos bilaterais com organismos internacionais, {c['sem_parte']} sem outra parte informada e "
        f"{c['nao_bilateral']} atos trilaterais ou multilaterais.",
        f"- Data de entrada em vigor: {int((desde['data_vigencia'] != '').sum())} dos {len(desde)} atos de 2003 em diante (do detalhe de cada ato); "
        "atos anteriores a 2003 não tiveram o detalhe coletado. Ato sem data de vigência pode estar em tramitação, sem vigência "
        "registrada ou sem o campo preenchido no Concórdia.",
        "- O Concórdia registra atos de naturezas diferentes (tratados, acordos, memorandos, ajustes complementares, troca de notas); a base "
        "guarda o título como publicado e não classifica relevância. Contagem de atos não mede intensidade de relação.",
        "- Estados extintos entram com o código de antigo Estado (Iugoslávia, Alemanha Oriental). Nomes de signatários ficam só no dado bruto.",
        "",
    ]


def _linhas_tse(base: Path) -> list[str]:
    """Etapa E7: candidatos e receitas de campanha (D-042, D-043)."""
    d = ler("doacoes_campanha", base)
    if not len(d):
        return []
    res = RAIZ / "data" / "staging" / "tse" / "resumo.csv"
    r = pd.read_csv(res, dtype=str, keep_default_na=False) if res.exists() else pd.DataFrame()
    sem = ", ".join(f"{x.ano}: {x.sem_ligacao}" for x in r.itertuples()) if len(r) else "n/d"
    emp = d[d["id_doador"] != ""]
    return [
        "### TSE: candidatos e receitas de campanha (etapa E7)", "",
        f"- {len(d)} linhas de receita, somadas por candidato, eleição e tipo de doador, de {d['ano_eleicao'].min()} a {d['ano_eleicao'].max()} "
        "(eleições gerais ordinárias; presidente, governador eleito, senador eleito e deputado federal eleito; D-043).",
        f"- Deputados e senadores eleitos sem ligação única com o parlamentar da base, e por isso sem receitas na base, por eleição: {sem}. "
        "A ligação é por nome, sem CPF; nomes de urna muito diferentes do nome parlamentar ficam de fora.",
        "- Candidatos não eleitos a governador, senador e deputado federal, e todos os candidatos a cargos estaduais e municipais, ficam fora.",
        f"- Empresas: linha própria só para as {emp['id_doador'].nunique()} empresas já presentes na base (BNDES, CGU); as demais aparecem somadas "
        "por candidato. Pessoas físicas só em total por candidato. Doações de empresas foram proibidas a partir de 2015 (STF, ADI 4650).",
        "- 2002: o arquivo não traz o tipo de receita; o tipo é deduzido do documento do doador (CPF ou CNPJ) e do nome (partido, comitê, "
        "próprio candidato). Até 2010, repasses de comitês e de outros candidatos aparecem como \"partido\", sem o doador originário.",
        "- 2014: linhas `originario_via_partido` identificam o doador originário de recursos repassados por partido ou comitê; o valor já está "
        "contado na linha do repasse e não deve ser somado de novo.",
        "- Receitas registradas são doações legais declaradas à Justiça Eleitoral; o registro não indica irregularidade.",
        "",
    ]


def _linhas_e9(base: Path) -> list[str]:
    """Casos-teste da E9 (D-046)."""
    st = ler("status_pessoa_processo", base)
    casos = ler("casos", base)
    if not len(st):
        return []
    return [
        "### Casos-teste (etapa E9)", "",
        f"- Casos: {', '.join(casos['nome'])}. Status formais registrados: {len(st)} "
        f"({'; '.join(f'{k}: {n}' for k, n in st['status'].value_counts().items())}), com fonte judicial ou oficial (STF, STJ, TRF4, TJMG; D-046).",
        "- Lava Jato (D-052): os processos-âncora ficam fora do universo coletado (primeira instância federal não foi coletada; HC e Rcl não "
        "entram na E5) e entram pela E9. Carregados: a ação do triplex (5046512-94.2016.4.04.7000), com os status de Luiz Inácio Lula da Silva "
        "de condenação (primeira e segunda instâncias e STJ) seguidos da condenação anulada (HC 193726, 08/03/2021) e do processo anulado "
        "(HC 164493, 23/03/2021); a ação do sítio de Atibaia com a condenação em primeira instância (fevereiro de 2019, dia não informado), "
        "a confirmação no TRF4 (27/11/2019) e a condenação anulada (08/03/2021); as duas ações do Instituto Lula só com a anulação e a "
        "remessa à Justiça Federal do DF (sem sentença lida); a ação 5026212-82.2014.4.04.7000 (Refinaria Abreu e Lima) com oito condenados e "
        "dois absolvidos em 22/04/2015 (réus sem mandato na base); a Rcl 43007 com a decisão de 06/09/2023 sobre as provas da Odebrecht. "
        "O desfecho na Justiça Federal do DF depois de abril de 2021 não foi localizado. Fontes: notícias oficiais do TRF4, da JFPR, do STJ e "
        "do STF. A consulta processual não pôde ser usada: em 29/09/2026 o eproc da JFPR e o do TRF4 exibiam \"A consulta pública está "
        "desativada.\", a consulta unificada do TRF4 pedia CAPTCHA (não resolvido) e o PJe público do TRF1 contava resultados sem exibi-los "
        "(relatório no bruto). Ficaram sem leitura as ações 5083401-18.2014 e 5083258-29.2014 e o inquérito 5049557-14.2013. A data do "
        "julgamento do Plenário de 15/04/2021 diverge no próprio texto da notícia (\"quinta-feira (14)\").",
        "- A anulação de provas da Rcl 43007 foi estendida a pessoas de partidos diferentes (Paulo Bernardo, 19/06/2023; Sérgio Cabral e "
        "Gilberto Kassab, 02/08/2023; fontes registradas); as ações penais dessas pessoas não foram carregadas. A Lava Jato que correu "
        "no próprio STF está no universo da E5 (por exemplo, AP 996 e AP 1003) e entrou na verificação de simetria.",
        "- Banco Master (D-052): Inq 5026 e processos distribuídos por prevenção estão no universo do STF, com assunto processual (\"revisar\" "
        "no eixo 1); no Inq 5026 os investigados não aparecem na aba Partes. Entraram como investigados os quatro nomes da decisão de "
        "04/03/2026 que decretou prisões preventivas (pessoas sem cargo público na base). A decisão de 03/04/2026 sobre Ibaneis Rocha Barros "
        "Júnior trata da condição de investigado atribuída pela CPI do Crime Organizado e não informa inclusão no inquérito do STF: entrou "
        "como fase do processo, não como status. Decisões sigilosas e petições sem partes não foram lidas.",
        "- AP 470: o texto da decisão de 17/12/2012 vem cortado no portal, e o resultado por réu e por crime está espalhado em andamentos de "
        "agosto a dezembro de 2012, em trechos também cortados. Entraram só as condenações nomeadas em decisão do Tribunal (23/10/2012, "
        "quadrilha) ou em notícia oficial da fixação das penas (12 e 21/11/2012), e as absolvições por quadrilha nos embargos infringentes de "
        "27/02/2014. Os demais resultados de 2012 ficam pendentes de leitura da fonte primária completa.",
        "- Pendências conhecidas: condenação por quadrilha de Marcos Valério e José Roberto Salgado (a absolvição de 2014 está registrada, a "
        "condenação de 2012 não tem trecho com data); embargos infringentes sobre lavagem de 13/03/2014 (duas absolvições e uma rejeição) sem "
        "fonte oficial que nomeie cada embargante; extinção de punibilidade de 16/09/2010 sem o nome do réu; trânsitos em julgado por réu.",
        "- AP 536 (Mensalão mineiro): o STF declinou da competência em 27/03/2014 e enviou o processo à Justiça estadual de Belo Horizonte "
        "sem julgamento de mérito. O recebimento da denúncia não aparece nos andamentos do STF.",
        "- AP 536 no TJMG (ação penal 2378231-34.2014.8.13.0024, 9ª Vara Criminal de Belo Horizonte): o processo é sigiloso na consulta "
        "processual (\"Processo sigiloso — acesso restrito\"); as fases vêm de acórdãos públicos de outros processos que o citam e do agravo "
        "interno de 2019, que nomeia o réu. Duas notícias oficiais do TJMG divergem sobre a data da sentença de primeira instância "
        "(dezembro de 2015 na notícia de 01/08/2017; abril de 2016 na de 07/04/2017); por isso a condenação em primeira instância não tem "
        "status próprio, e o primeiro status registrado é a confirmação em segunda instância (22/08/2017). Os embargos infringentes citados "
        "no agravo interno não têm número nem data nas páginas lidas. Trânsito em julgado, execução da pena e fatos após 10/07/2019 não "
        "aparecem nas páginas públicas do TJMG; a pesquisa antiga de jurisprudência pede CAPTCHA, que não foi resolvido.",
        "- Os processos da AP 536 dos demais réus, desmembrados no TJMG, não foram levantados.",
        "- Réus sem correspondência única com a base entram como ator novo, com tipo provisório; a ligação do réu Carlos Alberto Rodrigues Pinto "
        "ao deputado Carlos Rodrigues é decisão manual a conferir.",
        "- Status de pessoas filiadas ainda sem verificação de simetria: aparecem como aviso do validador e não vão a relatório (D-007).",
        "",
    ]


def _linhas_eixo2() -> list[str]:
    """Métricas do eixo 2 por governo (D-053)."""
    if not (RAIZ / "relatorios" / "tabelas" / "eixo2_votos_por_governo.csv").exists():
        return []
    return [
        "### Eixo 2: métricas por governo (D-053)", "",
        "- Votos: o Brasil só vota no Conselho de Direitos Humanos quando é membro, e o número de resoluções por governo varia com isso e "
        "com a agenda de cada ano. O país-alvo sai do título por regra; nas resoluções sobre território ocupado, o alvo é a potência "
        "ocupante ou agressora (Rússia na Ucrânia, Israel no Território Palestino Ocupado). A comparação com democracias e com a América "
        "Latina é a média do voto desses países nas mesmas resoluções. Voto em organismo multilateral é posição do Estado (Poder "
        "Executivo), não de partido.",
        "- Baixa qualidade democrática: Freedom House até 2024 e V-Dem até 2025; atos e operações de 2025-2026 ficam sem classificação "
        "pela Freedom House (136 dos 314 acordos do governo iniciado em 2023).",
        "- BNDES: o arquivo aberto não publica valor nas operações de exportação de bens (2.344); só as de serviços de engenharia (652, "
        "em dólar) têm valor, e não há operação desse tipo depois de 2015. A comparação por valor cobre só os governos de 2003 a 2016; "
        "a comparação entre todos os governos usa a contagem de operações. Parte das operações antigas não tem país de destino "
        "identificado.",
        "- Linha de base comercial (D-054): exportações do ComexStat por país e mês (cada mês no governo em exercício no dia 15). A parcela "
        "exportada para países BQD é dominada pela China (de 6% a 30% das exportações), e a tendência reflete sobretudo o crescimento desse "
        "comércio; no governo iniciado em 2023, 47% do valor exportado fica sem classificação porque a Freedom House vai só até 2024. A "
        "comparação com o BNDES é de parcelas, não de valores: o BNDES financia uma fração pequena e específica das exportações.",
        "- Redes partidárias: as datas são as da primeira e da última cópia arquivada da página de cada rede (Wayback, D-040), não as "
        "datas de filiação; filiações anteriores à primeira cópia (por exemplo, fundadores de uma rede) aparecem com a data da cópia.",
        "",
    ]


def _linhas_ideologia() -> list[str]:
    """Simetria por posição ideológica (D-062)."""
    arq = RAIZ / "relatorios" / "tabelas" / "ideologia_correlacao.csv"
    if not arq.exists():
        return []
    c = pd.read_csv(arq)
    esc = pd.read_csv(RAIZ / "data" / "base" / "posicao_ideologica.csv", dtype=str)
    return [
        "### Posição ideológica dos partidos (D-062)", "",
        f"- Escala: Bolognesi, Ribeiro e Codato (2023), survey de 2018 com cientistas políticos; {len(esc)} partidos com escore. O mesmo "
        "escore vale para 2003-2026: partidos que mudaram de posição no período ficam com a posição de 2018. Partidos criados por fusão "
        "depois de 2018 (União, PRD) ficam sem escore.",
        f"- Nenhuma das {len(c)} correlações entre escore e taxa por partido tem p abaixo de 0,05 (menor p: {c['p_permutacao'].min():.3f}). "
        "A faixa \"direita\" reúne 16 partidos, entre eles MDB, PSDB e PSD, pelos cortes do artigo; a comparação entre faixas é mais "
        "informativa que o rótulo de cada uma.",
        "- Partidos de extrema-esquerda têm poucos eleitos e poucos candidatos que foram gestores: taxa perto de zero reflete também exposição.",
        "",
    ]


def _linhas_eixo1_universos() -> list[str]:
    """Eixo 1 ampliado: TSE e TCU em universos de candidatos (D-060, D-061)."""
    arq = RAIZ / "relatorios" / "tabelas" / "eixo1_taxas.csv"
    if not arq.exists():
        return []
    t = pd.read_csv(arq)
    def total(medida, universo="candidatos"):
        x = t[(t["medida"] == medida) & (t["anos"] == "todos") & (t["universo"] == universo) & (t["grupo_tipo"] == "partido")]
        return int(x["com_registro"].sum()), int(x["n"].sum())
    ind, n_ind = total("tse_indeferimento")
    ind_l, _ = total("tse_indeferimento_inclui_lista")
    tcu_e, n_tcu = total("tcu_ate_eleicao")
    tcu_q, _ = total("tcu_qualquer_data")
    return [
        "### Eixo 1 ampliado: candidatos, TSE e TCU (D-060, D-061)", "",
        f"- Universo: {n_tcu} candidaturas das eleições gerais de 2010 a 2022 (um registro por sequencial do TSE); eleições municipais fora.",
        f"- TSE: {ind} de {n_ind} candidaturas de 2018 e 2022 indeferidas ou cassadas por motivo do eixo 1; {ind_l} sem a exclusão dos casos "
        "de lista (D-061: em 2022, quase todo \"abuso de poder político\" acompanha fraude à cota de gênero no DRAP, que atinge a lista). O TSE "
        "não publica o arquivo de motivos de 2010, e o de 2014 tem 10 linhas: a medida não cobre esses anos. O arquivo não traz a data da "
        "decisão; usa-se a do primeiro turno.",
        f"- TCU: {tcu_e} candidaturas com conta julgada irregular (trânsito em julgado) até o primeiro turno; {tcu_q} em qualquer data. A "
        "lista do TCU concentra gestores de recursos federais, sobretudo ex-prefeitos: partidos com mais candidatos que já foram gestores "
        "têm mais exposição, e a taxa não separa exposição de conduta. Ligação só por CPF igual no TSE e no TCU; CPF ausente no TSE deixa "
        "o candidato sem ligação.",
        "- Governo/oposição: grupo do partido na data da eleição pela regra de D-050 (orientação de bancada na Câmara); partidos sem "
        "votações suficientes ficam sem classificação.",
        "- Homogeneidade entre partidos: estatística qui-quadrado com p exato por simulação (válido com contagens pequenas), só partidos "
        "com pelo menos 30 candidaturas no recorte.",
        "",
    ]


def _linhas_stf_composicao() -> list[str]:
    """Composição do STF (D-058)."""
    arq = RAIZ / "relatorios" / "tabelas" / "stf_composicao.csv"
    if not arq.exists():
        return []
    t = pd.read_csv(arq, dtype=str, keep_default_na=False)
    c = pd.read_csv(RAIZ / "relatorios" / "tabelas" / "stf_composicao_correcoes.csv", dtype=str, keep_default_na=False)
    div = t[t["vaga_divergente"] == "True"]
    return [
        "### Composição do STF (D-058)", "",
        f"- {len(t)} ministros em exercício em algum dia desde 2003, das páginas \"Dados e Datas\" da Biblioteca do STF. As páginas têm erros: "
        + "; ".join(f"{r.nome_guerra}, {r.campo}: lido {r.lido or '(vazio)'}, usado {r.valor} ({r.arquivo})" for r in c.itertuples()) + ".",
        "- Vaga citada no decreto de nomeação diferente da citada na mensagem de indicação: "
        + "; ".join(f"{r.nome_guerra} (mensagem: {r.vaga_de}; decreto: {r.vaga_no_decreto})" for r in div.itertuples())
        + ". A tabela usa a mensagem; nenhuma data depende disso.",
        "- Datas de fim: aposentadoria = data de início do decreto (\"a partir de\") ou, sem ela, a data do decreto; falecimento = biografia "
        "ou notícia oficial. As relações `indicou` usam a data da mensagem de indicação. A indicação rejeitada de 2026 usa a data de "
        "apresentação no Senado, porque a mensagem presidencial não traz o dia nas fontes coletadas.",
        "- Partido do presidente (D-059): partido do registro de candidatura no TSE para o mandato em curso, não a filiação no dia. Jair "
        "Bolsonaro foi eleito pelo PSL (2018) e aparece como PSL em todo o mandato 2019-2022, inclusive nas indicações de 2020 e 2021; "
        "a filiação no dia, se usada, exige fonte própria.",
        "",
    ]


def _linhas_imprensa() -> list[str]:
    """Contraste com a imprensa (D-055, D-056)."""
    arq = RAIZ / "relatorios" / "tabelas" / "imprensa_contraste.csv"
    if not arq.exists():
        return []
    det = pd.read_csv(arq, dtype=str, keep_default_na=False)
    veic = pd.read_csv(CURADORIA / "imprensa_veiculos.csv", dtype=str)
    uso = det[det["resultado"].isin(["concorda", "diverge", "mencao_sem_resultado", "sem_resultado"])].copy()
    uso["com_materia"] = uso["resultado"] != "sem_resultado"
    fora = veic[(veic["papel"] == "principal") & (veic["situacao_acesso"] != "ok")]["veiculo"].tolist()
    antes = uso[uso["data_fato"] < "2020-01-01"]
    sem_antes = sorted(v for v, g in antes.groupby("veiculo") if not g["com_materia"].any())
    ok_antes = uso[~uso["veiculo"].isin(sem_antes)]

    def cobertura(f: str, tab: pd.DataFrame) -> str:
        g = tab[tab["id_fato"] == f]
        return f"{int(g['com_materia'].sum())} de {len(g)}"

    div = uso[uso["resultado"] == "diverge"]
    return [
        "### Contraste com a imprensa (D-055, D-056)", "",
        f"- Painel: {uso['veiculo'].nunique()} veículos em uso. Sem acesso pela ferramenta de busca: {', '.join(fora)}; só uma reserva "
        "(Revista Oeste) tinha acesso. O painel não é uma amostra da imprensa brasileira, e a ausência de jornais impressos de "
        "circulação nacional é a maior lacuna.",
        "- A unidade é o título devolvido pela ferramenta de busca restrita ao domínio (até 10 links por consulta fixa). "
        "`sem_resultado` quer dizer que a matéria não apareceu nesses links, não que o veículo não a publicou: a ordem e o índice "
        "são da ferramenta, não do arquivo do veículo, e o critério de ordenação da ferramenta não é conhecido.",
        f"- {' e '.join(sem_antes)} não têm matéria sobre nenhum dos {antes['id_fato'].nunique()} fatos anteriores a 2020 nos "
        "resultados; comparações entre fatos de épocas diferentes devem excluir esses veículos.",
        f"- Assimetria de cobertura observada: TJMG confirma a condenação de Eduardo Azeredo (F03, 2017) aparece em {cobertura('F03', uso)} "
        f"veículos em uso ({cobertura('F03', ok_antes)} sem os veículos acima); TRF4 confirma a condenação de Lula no triplex (F05, 2018), "
        f"em {cobertura('F05', uso)} ({cobertura('F05', ok_antes)}). Vários veículos devolveram títulos sobre fases posteriores do caso "
        "Azeredo (ordem de prisão, STJ, embargos). O desenho não separa as causas possíveis (termos da consulta, ordem da ferramenta, "
        "projeção nacional do réu, tribunal estadual ou federal) e não permite atribuir a diferença a linha editorial.",
        f"- Divergências: {len(div)} ({'; '.join(f'{r.id_fato} {r.veiculo}' for r in div.itertuples())}). O critério é o título; "
        "matéria cujo título não informa o desfecho conta como `mencao_sem_resultado`, mesmo que o texto o informe.",
        "- Os esclarecimentos da régua em D-056 foram feitos durante a classificação, depois de ver os títulos, e valem para todas as linhas.",
        "",
    ] + _linhas_imprensa_navegador()


def _linhas_imprensa_navegador() -> list[str]:
    """Relatórios de navegação para os principais sem acesso (D-057)."""
    arq = RAIZ / "relatorios" / "tabelas" / "imprensa_navegador.csv"
    if not arq.exists():
        return []
    det = pd.read_csv(arq, dtype=str, keep_default_na=False)
    pv = pd.read_csv(RAIZ / "relatorios" / "tabelas" / "imprensa_navegador_por_veiculo.csv")
    folha = pd.read_csv(RAIZ / "relatorios" / "tabelas" / "imprensa_navegador_folha_por_coleta.csv", dtype=str)
    achou = folha[["chrome_google", "chatgpt_busca"]].ne("sem_resultado")
    difere = folha[achou["chrome_google"] != achou["chatgpt_busca"]]["id_fato"].tolist()
    bloq = det[det["resultado"] == "bloqueado"].groupby(["coleta", "veiculo"]).size()
    est = pv[(pv["coleta"] == "chrome_google") & (pv["veiculo"] == "O Estado de S. Paulo")].iloc[0]
    g = det[(det["coleta"] == "chrome_google") & det["resultado"].isin(["concorda", "diverge", "mencao_sem_resultado", "sem_resultado"])]

    def cobertura(f: str) -> str:
        x = g[g["id_fato"] == f]
        return f"{int((x['resultado'] != 'sem_resultado').sum())} de {len(x)}"

    return [
        "#### Principais sem acesso: relatórios de navegação (D-057)", "",
        f"- Coletas usadas: Google pelo Claude in Chrome (chrome_google) e buscador do ChatGPT (chatgpt_busca). Buscas bloqueadas: "
        f"{'; '.join(f'{c} {v}: {n}' for (c, v), n in bloq.items())}. A BBC News Brasil ficou sem nenhuma busca concluída. O relatório do Gemini "
        "está no bruto e fora da classificação.",
        f"- O buscador muda o resultado. Na Folha, a única coberta pelas duas coletas, elas divergem sobre haver matéria da decisão em "
        f"{len(difere)} dos {len(folha)} fatos ({', '.join(difere)}). Em F03 (Azeredo, TJMG) o Google não devolveu nenhum resultado e o "
        "outro buscador pôs a matéria da decisão em primeiro. `sem_resultado` mede o buscador tanto quanto o veículo, e a assimetria "
        "F03 × F05 do painel principal não deve ser lida como diferença de cobertura dos veículos.",
        f"- Pelo Google, nos 4 jornais com acesso, F03 tem matéria em {cobertura('F03')} e F05 em {cobertura('F05')}.",
        f"- Estadão: a regra de D-055 exclui URL de blog, e a cobertura judicial do jornal está sob /blog-do-fausto-macedo/. Há matéria "
        f"em {int(est['com_materia'])} de {int(est['buscas_com_acesso'])} fatos pela regra e em {int(est['com_materia_incluindo_blogs'])} incluindo blogs.",
        "- O Google às vezes mostra um título diferente do título da página (reescrita do buscador). A unidade continua sendo o título "
        "devolvido; quando o corte do buscador escondia o desfecho, valeu o título completo lido no navegador.",
        "",
    ]


def _linhas_simetria(base: Path) -> list[str]:
    """Verificação de simetria dos status da E9 (D-048)."""
    vs, vr = ler("verificacoes_simetria", base), ler("verificacao_resultado", base)
    if not len(vs):
        return []
    cont = vr["resultado"].value_counts().to_dict()
    lotes = sorted({re.search(r"lote(\d+)", f.name).group(1) for f in (RAIZ / "data" / "raw" / "stf").glob("*/stf_relatorio_navegacao_partes_ap_lote*.md")})
    lista = pd.read_csv(RAIZ / "data" / "curadoria" / "simetria_stf_ap_lista.csv", dtype=str)
    n_lidas = int(lista["lote"].isin(lotes).sum())
    return [
        "### Verificação de simetria dos status da E9", "",
        f"- {len(vs)} verificações, {len(vr)} resultados por grupo ({'; '.join(f'{k}: {n}' for k, n in cont.items())}).",
        f"- Universo lido: lotes {', '.join(lotes)} de D-048 ({n_lidas} de {len(lista)} ações penais do STF, fora 8 de janeiro; o lote 1 "
        "reúne as 99 julgadas no mérito); os réus vêm da aba Partes lida no navegador. Linhas que não são nome de pessoa (órgão do "
        "Ministério Público no campo de réu, \"OS MESMOS\"), empresas (LTDA, ME, EPP), entes públicos (município) e nomes só com iniciais ficam "
        "fora. Ação sem réu rotulado (queixa-crime, com querelante e querelado) não entra na lista de réus. "
        + ("Com todos os lotes lidos, os status de réu têm verificação própria (padrão de réu, abaixo)." if n_lidas == len(lista) else
           "Enquanto houver lote não lido, os status de réu e de denunciado não têm verificação e seguem como aviso do validador."),
        "- Padrão de condenação: contam só ações com assunto do eixo 1 pela regra da E5 e com condenação de ao menos um réu (Procedente ou "
        "Procedente em parte), partido na data do primeiro julgamento de mérito. Padrão de réu: todas as ações do eixo 1 em que o "
        "parlamentar é réu, partido na data de autuação da ação; ação penal no STF não mostra quando cada pessoa passou a réu. O status "
        "de denunciado não tem padrão lido (denúncia oferecida fica no inquérito, fora da lista de ações penais). "
        "O resultado por réu não foi lido: em ação com mais de um réu, o parlamentar pode ter sido absolvido. Ações com assunto "
        "classificado como crime contra o sistema financeiro, falsidade ou crime eleitoral ficam fora ou em \"revisar\", conforme a regra "
        "da E5; partido só com ações em \"revisar\" fica `nao_verificado`, com a lista das ações.",
        "- Ligação réu -> parlamentar pelo nome e pelo mandato no período da ação. A Câmara só publica o nome civil em arquivos que "
        "também trazem CPF, que o projeto não guarda (D-011); por isso a ligação usa o nome parlamentar, com decisões manuais e motivo em "
        "`data/curadoria/simetria_stf_ap_ligacoes.csv`. Ligação que se apoia só no prenome, ou no prenome e num nome do meio, entra "
        "como `aceita_a_conferir` quando nenhum outro parlamentar da base tem esse nome; prenome compartilhado é rejeitado; nome comum em "
        "ação com muitos réus fica `pendente`.",
        "- Partido é contado pela instituição exata da filiação na data; fusões e incorporações (por "
        "exemplo, PL antigo e PL atual) não são somadas.",
        "- Governo e oposição (D-050, D-051): na primeira versão das verificações ficaram `nao_verificado`; a segunda versão, datada, "
        "classifica o partido do réu na data do caso pelas orientações de bancada no Plenário da Câmara (concordância com o Governo "
        "de 2/3 ou mais: base; abaixo de 1/2: oposição). A classificação mede alinhamento em votação, não participação formal na "
        "coalizão (ministérios); orientação de liderança não é o voto de cada deputado; o Senado não entra. Blocos são decompostos "
        "pelo nome (D-051), o que amplia a cobertura mas atribui a orientação do bloco a cada membro; a partir de 2023 blocos "
        "grandes juntam partidos de posições diferentes. A regra sem blocos fica em coluna própria para comparação.",
        "- Taxa por bancada (D-049, `relatorios/tabelas/simetria_taxa_bancada.csv`): suplentes de senador ficam fora do denominador e do "
        "numerador, porque a base só os lista, sem o período em que exerceram o mandato; parlamentares ligados a réus que só aparecem como "
        "suplentes de senador não entram na taxa. A queda da taxa a partir da legislatura 56 acompanha a restrição do foro por prerrogativa "
        "de função no STF (maio de 2018), não uma mudança medida de conduta; a comparação entre partidos usa as legislaturas 52 a 55. Os "
        "intervalos de 95% se sobrepõem para a maior parte dos partidos: diferenças pequenas entre taxas não são distinguíveis com esses "
        "números. O intervalo supõe pares independentes, o que não vale quando o mesmo parlamentar aparece em várias legislaturas.",
        "- O status de Eduardo Azeredo no TJMG fica `nao_verificado` em todos os grupos: não há universo lido de ações penais estaduais.",
        "",
    ]


def run() -> None:
    doc = DOC.read_text(encoding="utf-8")
    antes = doc.split(INICIO)[0]
    DOC.write_text(antes + texto() + "\n", encoding="utf-8")
    print(f"atualizado: {DOC.relative_to(RAIZ).as_posix()}")


if __name__ == "__main__":
    run()
