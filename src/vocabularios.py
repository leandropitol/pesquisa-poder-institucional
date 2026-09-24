"""Vocabulários fechados do projeto (fonte de verdade).

Cada vocabulário é uma lista de linhas com `codigo` e `rotulo`; alguns têm colunas extras:

- `nivel_maximo`: teto de confiança que um registro com esse código pode ter (por exemplo,
  citação em colaboração premiada nunca passa de `alegado`);
- `modelo_frase`: frase-modelo usada pelos relatórios, com campos entre chaves.

`python -m src.estrutura` grava cada vocabulário em data/vocabularios/<nome>.csv e o
documenta em docs/vocabularios.md.
"""

NIVEIS = ["alegado", "sob_investigacao", "documentado"]  # ordem crescente


def _v(*linhas: tuple) -> list[dict]:
    return [dict(zip(("codigo", "rotulo"), l[:2]), **(l[2] if len(l) > 2 else {})) for l in linhas]


VOCABULARIOS: dict[str, list[dict]] = {
    "eixo": _v(
        ("esquemas_ilicitos", "Esquemas ilícitos com trâmite formal"),
        ("relacoes_externas", "Relações externas com governos da América Latina"),
        ("poder_institucional", "Concentração ou abuso de poder institucional"),
    ),
    "nivel_confianca": _v(
        ("documentado", "Documentado: decisão judicial publicada, votação nominal oficial, dado orçamentário oficial ou ato publicado"),
        ("sob_investigacao", "Sob investigação: inquérito, denúncia ou processo registrado, sem decisão de mérito"),
        ("alegado", "Alegado: só jornalismo, declarações ou colaboração premiada"),
    ),
    "tipo_fonte": _v(
        ("judicial", "Judicial"), ("legislativa", "Legislativa"), ("orcamentaria", "Orçamentária e financeira"),
        ("jornalistica", "Jornalística"), ("oficial", "Documento oficial (MP, PF, TCU, CGU, Itamaraty, diário oficial)"),
        ("base_de_dados", "Base de dados de pesquisa (V-Dem, Freedom House)"),
    ),
    "classe_jornalistica": _v(
        ("investigativa", "Reportagem investigativa"), ("factual", "Notícia factual"), ("opiniao", "Opinião, editorial ou coluna"),
    ),
    "tipo_ator": _v(("agente_publico", "Agente público"), ("agente_privado", "Agente privado")),
    "tipo_instituicao": _v(
        ("orgao_publico", "Órgão público"), ("tribunal", "Tribunal"), ("ministerio_publico", "Ministério Público"),
        ("policia", "Polícia"), ("casa_legislativa", "Casa legislativa"), ("tribunal_de_contas", "Tribunal de contas"),
        ("empresa_estatal", "Empresa estatal"), ("banco_publico", "Banco público"), ("empresa_privada", "Empresa privada"),
        ("partido", "Partido político"), ("governo_estrangeiro", "Governo estrangeiro"),
        ("organismo_multilateral", "Organismo multilateral"), ("rede_partidaria_transnacional", "Rede partidária transnacional"),
        ("outro", "Outro"),
    ),
    "poder": _v(
        ("executivo", "Executivo"), ("legislativo", "Legislativo"), ("judiciario", "Judiciário"),
        ("ministerio_publico", "Ministério Público"), ("tribunal_de_contas", "Tribunal de contas"), ("nao_se_aplica", "Não se aplica"),
    ),
    "esfera": _v(
        ("federal", "Federal"), ("estadual", "Estadual"), ("municipal", "Municipal"), ("estrangeira", "Estrangeira"),
        ("internacional", "Internacional"), ("nao_se_aplica", "Não se aplica"),
    ),
    "forma_acesso": _v(
        ("eleito", "Eleito"), ("nomeado", "Nomeado"), ("concursado", "Concursado"),
        ("indicado_aprovado", "Indicado e aprovado pelo Senado"), ("outro", "Outro"),
    ),
    "tipo_caso": _v(
        ("operacao_policial", "Operação policial"), ("acao_penal", "Ação penal"), ("inquerito", "Inquérito"),
        ("cpi", "Comissão parlamentar de inquérito"), ("auditoria_tcu", "Auditoria ou tomada de contas do TCU"), ("outro", "Outro"),
    ),
    "classe_processual": _v(
        ("acao_penal", "Ação penal"), ("inquerito", "Inquérito"), ("peticao", "Petição"), ("habeas_corpus", "Habeas corpus"),
        ("adi", "Ação direta de inconstitucionalidade"), ("adpf", "Arguição de descumprimento de preceito fundamental"),
        ("adc", "Ação declaratória de constitucionalidade"), ("mandado_seguranca", "Mandado de segurança"),
        ("reclamacao", "Reclamação"), ("recurso_extraordinario", "Recurso extraordinário"), ("recurso_especial", "Recurso especial"),
        ("acao_civil_publica", "Ação civil pública"), ("acao_improbidade", "Ação de improbidade administrativa"), ("outra", "Outra"),
    ),
    "fase_processual": _v(
        ("instauracao_inquerito", "Instauração de inquérito"), ("arquivamento_inquerito", "Arquivamento de inquérito"),
        ("oferecimento_denuncia", "Oferecimento de denúncia"), ("recebimento_denuncia", "Recebimento de denúncia"),
        ("rejeicao_denuncia", "Rejeição de denúncia"), ("sentenca", "Sentença"), ("acordao_2a_instancia", "Acórdão de segunda instância"),
        ("acordao_tribunal_superior", "Acórdão de tribunal superior"), ("transito_em_julgado", "Trânsito em julgado"),
        ("declinio_competencia", "Declínio de competência"), ("remessa_outra_instancia", "Remessa a outra instância"),
        ("anulacao", "Anulação"), ("prescricao_reconhecida", "Prescrição reconhecida"),
        ("homologacao_colaboracao", "Homologação de colaboração premiada"), ("extincao_punibilidade", "Extinção da punibilidade"),
        ("outra", "Outra"),
    ),
    "status_processual": _v(
        ("investigado", "investigado", {"modelo_frase": "{data}: {ator} passou a investigado em {processo}."}),
        ("denunciado", "denunciado", {"modelo_frase": "{data}: {ator} foi denunciado em {processo}{tipificacao}."}),
        ("reu", "réu", {"modelo_frase": "{data}: {ator} passou a réu em {processo}{tipificacao}."}),
        ("condenado_1a_instancia", "condenado em primeira instância", {"modelo_frase": "{data}: {ator} foi condenado em primeira instância em {processo}{tipificacao}."}),
        ("condenado_2a_instancia", "condenado em segunda instância", {"modelo_frase": "{data}: {ator} foi condenado em segunda instância em {processo}{tipificacao}."}),
        ("condenado_tribunal_superior", "condenado por tribunal superior", {"modelo_frase": "{data}: {ator} foi condenado por tribunal superior em {processo}{tipificacao}."}),
        ("condenado_transito_em_julgado", "condenado com trânsito em julgado", {"modelo_frase": "{data}: a condenação de {ator} em {processo} transitou em julgado{tipificacao}."}),
        ("absolvido", "absolvido", {"modelo_frase": "{data}: {ator} foi absolvido em {processo}."}),
        ("denuncia_rejeitada", "denúncia rejeitada", {"modelo_frase": "{data}: a denúncia contra {ator} em {processo} foi rejeitada."}),
        ("arquivado", "arquivado", {"modelo_frase": "{data}: a investigação sobre {ator} em {processo} foi arquivada."}),
        ("prescrito", "prescrição reconhecida", {"modelo_frase": "{data}: foi reconhecida a prescrição em relação a {ator} em {processo}."}),
        ("punibilidade_extinta", "punibilidade extinta", {"modelo_frase": "{data}: foi declarada extinta a punibilidade de {ator} em {processo}."}),
        ("condenacao_anulada", "condenação anulada", {"modelo_frase": "{data}: a condenação de {ator} em {processo} foi anulada."}),
        ("processo_anulado", "processo anulado", {"modelo_frase": "{data}: o processo {processo} foi anulado em relação a {ator}."}),
        ("colaborador", "colaborador", {"modelo_frase": "{data}: {ator} firmou colaboração premiada homologada em {processo}."}),
    ),
    "tipo_evento": _v(
        ("decisao_judicial", "Decisão judicial"), ("votacao_nominal", "Votação nominal"), ("operacao_policial", "Operação policial"),
        ("oferecimento_denuncia", "Oferecimento de denúncia"), ("contrato_publico", "Contrato público"), ("financiamento", "Financiamento"),
        ("acordo_bilateral", "Acordo bilateral"), ("voto_multilateral", "Voto em organismo multilateral"), ("nomeacao", "Nomeação"),
        ("exoneracao", "Exoneração"), ("eleicao", "Eleição"), ("cpi_instalada", "Instalação de CPI"),
        ("cpi_relatorio_final", "Relatório final de CPI"), ("reuniao_rede_partidaria", "Reunião de rede partidária transnacional"),
        ("outro", "Outro"),
    ),
    "precisao_data": _v(("dia", "Dia (AAAA-MM-DD)"), ("mes", "Mês (AAAA-MM)"), ("ano", "Ano (AAAA)")),
    "tipo_entidade": _v(
        ("ator", "Ator (tabela atores)"), ("instituicao", "Instituição"), ("caso", "Caso"), ("processo", "Processo"), ("evento", "Evento"),
    ),
    "tipo_relacao": _v(
        ("membro_de", "é membro de"), ("parte_em_contrato", "é parte em contrato com"), ("financiou", "financiou"),
        ("controla", "controla"), ("subsidiaria_de", "é subsidiária de"), ("participou_de", "participou de"),
        ("representou_brasil_em", "representou o Brasil em"), ("indicou", "indicou"), ("relator_de", "foi relator de"),
        ("citado_em_colaboracao", "foi citado em colaboração premiada de", {"nivel_maximo": "alegado"}),
        ("citado_em_reportagem", "foi citado em reportagem sobre", {"nivel_maximo": "alegado"}),
    ),
    "predicado_afirmacao": _v(
        ("recebeu_valor", "recebeu valor de", {"modelo_frase": "{data}: {sujeito} recebeu valor de {objeto}{valor}."}),
        ("pagou_valor", "pagou valor a", {"modelo_frase": "{data}: {sujeito} pagou valor a {objeto}{valor}."}),
        ("autorizou", "autorizou", {"modelo_frase": "{data}: {sujeito} autorizou {objeto}."}),
        ("indicou_para_cargo", "indicou para cargo", {"modelo_frase": "{data}: {sujeito} indicou {objeto} para cargo."}),
        ("interveio_em", "interveio em", {"modelo_frase": "{data}: {sujeito} interveio em {objeto}."}),
        ("declarou", "declarou sobre", {"modelo_frase": "{data}: {sujeito} declarou sobre {objeto}.", "nivel_maximo": "alegado"}),
        ("negou", "negou", {"modelo_frase": "{data}: {sujeito} negou {objeto}."}),
        ("outro", "outro", {"modelo_frase": "{data}: {sujeito}, {objeto}."}),
    ),
    "resultado_verificacao": _v(
        ("encontrado", "Casos equivalentes encontrados"),
        ("sem_evidencia", "Busca registrada sem resultados"),
        ("nao_verificado", "Não verificado"),
    ),
    "grupo_verificacao": _v(("partido", "Partido"), ("governo", "Base do governo na época"), ("oposicao", "Oposição na época")),
    "casa_legislativa": _v(
        ("camara_deputados", "Câmara dos Deputados"), ("senado_federal", "Senado Federal"),
        ("congresso_nacional", "Congresso Nacional"), ("outra", "Outra"),
    ),
    "tipo_decisao": _v(("monocratica", "Monocrática"), ("colegiada", "Colegiada")),
    "voto_multilateral": _v(("sim", "Sim"), ("nao", "Não"), ("abstencao", "Abstenção"), ("ausente", "Ausente")),
    "indice_democracia": _v(
        ("vdem_row", "V-Dem Regimes of the World (0 a 3)"),
        ("vdem_ldi", "V-Dem Liberal Democracy Index (0 a 1)"),
        ("fh_status", "Freedom House, status (F, PF, NF)"),
        ("fh_total", "Freedom House, pontuação total (0 a 100)"),
    ),
    "doador_tipo": _v(
        ("pessoa_juridica", "Pessoa jurídica"), ("pessoa_fisica_agregado", "Pessoas físicas, agregado"),
        ("partido", "Partido"), ("recursos_proprios", "Recursos próprios"), ("fundo_publico", "Fundo público (FEFC ou Fundo Partidário)"),
        ("outro", "Outro"),
    ),
    "moeda": _v(("BRL", "Real"), ("USD", "Dólar americano"), ("EUR", "Euro"), ("outra", "Outra")),
}


def codigos(nome: str) -> set[str]:
    return {l["codigo"] for l in VOCABULARIOS[nome]}


def teto(nome: str, codigo: str) -> str | None:
    for l in VOCABULARIOS[nome]:
        if l["codigo"] == codigo:
            return l.get("nivel_maximo")
    return None
