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

    proc = ler("processos", base)
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
            + "A votação de mão erguida (suspensão de Honduras, 4 de julho de 2009, 33 votos afirmativos) não individualiza os votos e não gera linha por país.")
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
    linhas += ["- Volumes de resoluções de 2003, 2005 e 2006 e o segundo arquivo da sessão extraordinária de 2009 não foram obtidos; "
               "resoluções do Conselho Permanente ainda não foram indexadas.", ""]
    return linhas


def run() -> None:
    doc = DOC.read_text(encoding="utf-8")
    antes = doc.split(INICIO)[0]
    DOC.write_text(antes + texto() + "\n", encoding="utf-8")
    print(f"atualizado: {DOC.relative_to(RAIZ).as_posix()}")


if __name__ == "__main__":
    run()
