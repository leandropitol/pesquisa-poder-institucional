"""Gera a parte automática de docs/limitacoes.md (entre os marcadores INICIO-GERADO e FIM-GERADO):
cobertura da base, buscas registradas, lacunas medidas e avisos do validador. A parte escrita à mão,
acima do marcador, não é alterada.

Uso:
    python -m src.relatorios.limitacoes
"""

import csv
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
            "- Resoluções sobre países da América Latina no Conselho de Direitos Humanos (bloco A2) ainda não entraram.",
            "",
        ]
    linhas += _linhas_oea(vm_todos[vm_todos["id_organismo"].map(siglas) == "AG/OEA"])
    linhas += _linhas_redes(base)
    linhas += _linhas_acordos(base)
    linhas += _linhas_tse(base)

    linhas += ["### Validador", "", f"- {len(falhas)} falha(s) e {len(avisos)} aviso(s) na última geração."]
    linhas += [f"- Aviso: {a}" for a in avisos[:20]]
    if len(avisos) > 20:
        linhas.append(f"- … e mais {len(avisos) - 20} avisos.")
    linhas += ["", FIM]
    return "\n".join(linhas)


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
        f"- {len(proc)} ações penais e inquéritos: os que tiveram decisão de 08/01/2003 a 23/09/2026 e os em tramitação na data da exportação "
        f"(D-037). No universo do eixo 1: {len(sim)} (tipos do protocolo pelo assunto); {int((u == 'revisar').sum())} a revisar; "
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


def run() -> None:
    doc = DOC.read_text(encoding="utf-8")
    antes = doc.split(INICIO)[0]
    DOC.write_text(antes + texto() + "\n", encoding="utf-8")
    print(f"atualizado: {DOC.relative_to(RAIZ).as_posix()}")


if __name__ == "__main__":
    run()
