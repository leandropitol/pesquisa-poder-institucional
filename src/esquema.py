"""Esquema de dados do projeto (fonte de verdade).

Cada tabela vira um CSV em data/base/<nome>.csv. `python -m src.estrutura` cria os CSVs
vazios (só cabeçalho, sem sobrescrever dados) e gera docs/esquema_dados.md;
`python -m src.validacao.validar` confere os dados contra este esquema.

Tipos de coluna:
  id       chave no formato PREFIXO-000001 (o prefixo é o da tabela de origem)
  ref      referência a outra tabela (campo `fk`, "tabela.coluna")
  texto    texto livre curto
  data     data ISO parcial: AAAA, AAAA-MM ou AAAA-MM-DD
  inteiro, decimal, bool (true/false), url, iso3 (país), sha256, ano (AAAA)
  vocab    valor de vocabulário fechado (campo `vocab`, ver src/vocabularios.py)
  lista    identificadores separados por ";"
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Coluna:
    nome: str
    tipo: str
    obrigatoria: bool = False
    descricao: str = ""
    vocab: str | None = None
    fk: str | None = None


@dataclass(frozen=True)
class Tabela:
    nome: str
    grupo: str
    descricao: str
    chave: tuple[str, ...]
    colunas: tuple[Coluna, ...]
    prefixo: str | None = None
    so_cresce: bool = False  # histórico: linhas nunca são apagadas nem alteradas
    polimorficas: tuple[tuple[str, str], ...] = field(default_factory=tuple)  # (coluna_tipo, coluna_id)

    @property
    def nomes(self) -> list[str]:
        return [c.nome for c in self.colunas]


def C(nome, tipo, obrigatoria=False, descricao="", vocab=None, fk=None) -> Coluna:
    return Coluna(nome, tipo, obrigatoria, descricao, vocab, fk)


FONTE = C("id_fonte", "ref", True, "Fonte que sustenta o registro", fk="fontes.id_fonte")

TABELAS: list[Tabela] = [
    # ------------------------------------------------------------------ entidades
    Tabela("atores", "entidades", "Pessoas físicas: agentes públicos e privados. Sem CPF, endereço ou familiares.", ("id_ator",), (
        C("id_ator", "id", True),
        C("nome", "texto", True, "Nome como aparece em fonte oficial"),
        C("nome_normalizado", "texto", True, "Minúsculas, sem acento, para busca e deduplicação"),
        C("tipo_ator", "vocab", True, vocab="tipo_ator"),
        C("id_camara", "texto", False, "Identificador na API de dados abertos da Câmara"),
        C("id_senado", "texto", False, "Código do parlamentar no Senado"),
        C("observacao", "texto"),
    ), prefixo="ATR"),
    Tabela("filiacoes", "entidades", "Filiação partidária no tempo. A análise usa a filiação na data do fato.", ("id_filiacao",), (
        C("id_filiacao", "id", True),
        C("id_ator", "ref", True, fk="atores.id_ator"),
        C("id_partido", "ref", True, "Instituição de tipo partido", fk="instituicoes.id_instituicao"),
        C("data_inicio", "data", True), C("data_fim", "data"), FONTE,
    ), prefixo="FIL"),
    Tabela("cargos", "entidades", "Cargos ocupados no tempo.", ("id_cargo",), (
        C("id_cargo", "id", True),
        C("id_ator", "ref", True, fk="atores.id_ator"),
        C("id_instituicao", "ref", True, fk="instituicoes.id_instituicao"),
        C("cargo", "texto", True), C("forma_acesso", "vocab", True, vocab="forma_acesso"),
        C("data_inicio", "data", True), C("data_fim", "data"), FONTE,
    ), prefixo="CRG"),
    Tabela("instituicoes", "entidades", "Órgãos, tribunais, empresas, partidos, governos estrangeiros, organismos e redes partidárias.", ("id_instituicao",), (
        C("id_instituicao", "id", True),
        C("nome", "texto", True), C("sigla", "texto"),
        C("tipo_instituicao", "vocab", True, vocab="tipo_instituicao"),
        C("poder", "vocab", True, vocab="poder"), C("esfera", "vocab", True, vocab="esfera"),
        C("pais_iso3", "iso3", False, "País sede (BRA para instituições brasileiras); vazio quando a fonte não informa (por exemplo, empresa estrangeira identificada só por código da CGU)"),
        C("cnpj", "texto", False, "Só para pessoa jurídica brasileira"),
        C("id_sucessora", "ref", False, "Instituição que a sucedeu (fusão ou mudança de nome de partido)", fk="instituicoes.id_instituicao"),
        C("observacao", "texto"),
    ), prefixo="INS"),
    Tabela("denominacoes_partido", "entidades", "Siglas e nomes de cada partido (registro no TSE) ao longo do tempo. Mudança de nome ou sigla não cria partido novo.", ("id_denominacao",), (
        C("id_denominacao", "id", True),
        C("id_partido", "ref", True, "Instituição de tipo partido", fk="instituicoes.id_instituicao"),
        C("sigla", "texto", True), C("nome", "texto", True),
        C("data_inicio", "data", False, "Vazia quando anterior aos registros consultados"),
        C("data_fim", "data", False, "Data da decisão que mudou o nome, fundiu ou incorporou o partido"), FONTE,
    ), prefixo="DNP"),
    Tabela("casos", "entidades", "Agrupamento de processos (operação, ação penal, CPI). Não é unidade de registro.", ("id_caso",), (
        C("id_caso", "id", True), C("nome", "texto", True),
        C("tipo_caso", "vocab", True, vocab="tipo_caso"), C("eixo", "vocab", True, vocab="eixo"),
        C("data_inicio", "data", True),
        C("criterio_inclusao", "texto", True, "Por que o caso entrou no universo (ver docs/protocolo.md)"), FONTE,
    ), prefixo="CAS"),
    Tabela("processos", "entidades", "Processos judiciais e procedimentos formais. Unidade de registro do eixo 1.", ("id_processo",), (
        C("id_processo", "id", True),
        C("numero_cnj", "texto", False, "Numeração única CNJ, quando existir"),
        C("numero_originario", "texto", False, "Ex.: AP 470, Inq 4.130 (quando a fonte informa)"),
        C("classe", "vocab", True, vocab="classe_processual"),
        C("id_tribunal", "ref", True, fk="instituicoes.id_instituicao"),
        C("id_relator_atual", "ref", False, fk="atores.id_ator"),
        C("data_autuacao", "data", False, "Vazia quando a fonte não informa (registros de candidatura do TSE e processos de contas do TCU, D-064)"),
        C("id_caso", "ref", False, fk="casos.id_caso"),
        C("assuntos_tpu", "texto", False, "Assuntos da Tabela Processual Unificada do CNJ, 'código:nome' separados por ';'; no STF, o assunto do Corte Aberta com prefixo 'STF:'"),
        C("sigilo", "bool", False, "Vazio quando a fonte não informa"), C("url", "url", True), FONTE,
    ), prefixo="PRC"),
    Tabela("fases_processo", "entidades", "Histórico de fases de cada processo.", ("id_fase",), (
        C("id_fase", "id", True),
        C("id_processo", "ref", True, fk="processos.id_processo"),
        C("data", "data", True), C("fase", "vocab", True, vocab="fase_processual"),
        C("id_orgao_julgador", "ref", False, fk="instituicoes.id_instituicao"),
        C("resumo", "texto", False, "Resumo factual curto do dispositivo"), FONTE,
    ), prefixo="FAS", so_cresce=True),
    Tabela("status_pessoa_processo", "entidades", "Histórico do status formal de cada pessoa em cada processo. O vigente é o de data mais recente.", ("id_status",), (
        C("id_status", "id", True),
        C("id_ator", "ref", True, fk="atores.id_ator"),
        C("id_processo", "ref", True, fk="processos.id_processo"),
        C("data", "data", True), C("status", "vocab", True, vocab="status_processual"),
        C("tipificacao", "texto", False, "Crime ou ato imputado como consta da peça, com artigo"),
        C("id_fonte", "ref", True, "Fonte judicial ou oficial", fk="fontes.id_fonte"),
    ), prefixo="STA", so_cresce=True),
    Tabela("eventos", "entidades", "Fatos datados que alimentam a linha do tempo.", ("id_evento",), (
        C("id_evento", "id", True),
        C("data", "data", True), C("precisao_data", "vocab", True, vocab="precisao_data"),
        C("tipo_evento", "vocab", True, vocab="tipo_evento"), C("eixo", "vocab", True, vocab="eixo"),
        C("descricao", "texto", True, "Frase factual curta, sem adjetivos"),
        C("pais_iso3", "iso3", True), C("valor", "decimal"), C("moeda", "vocab", vocab="moeda"),
        C("id_processo", "ref", False, fk="processos.id_processo"),
        C("nivel_confianca", "vocab", True, vocab="nivel_confianca"),
    ), prefixo="EVT"),
    Tabela("relacoes", "entidades", "Relações entre entidades (membro de, financiou, controla…).", ("id_relacao",), (
        C("id_relacao", "id", True),
        C("origem_tipo", "vocab", True, vocab="tipo_entidade"), C("origem_id", "texto", True),
        C("tipo_relacao", "vocab", True, vocab="tipo_relacao"),
        C("destino_tipo", "vocab", True, vocab="tipo_entidade"), C("destino_id", "texto", True),
        C("data_inicio", "data", True), C("data_fim", "data"),
        C("eixo", "vocab", False, "Vazio em relações estruturais (por exemplo, fusão de partidos)", vocab="eixo"),
        C("nivel_confianca", "vocab", True, vocab="nivel_confianca"),
    ), prefixo="REL", polimorficas=(("origem_tipo", "origem_id"), ("destino_tipo", "destino_id"))),
    Tabela("afirmacoes", "entidades", "Afirmações que os relatórios podem fazer, em forma sujeito-predicado-objeto.", ("id_afirmacao",), (
        C("id_afirmacao", "id", True),
        C("sujeito_tipo", "vocab", True, vocab="tipo_entidade"), C("sujeito_id", "texto", True),
        C("predicado", "vocab", True, vocab="predicado_afirmacao"),
        C("objeto_tipo", "vocab", True, vocab="tipo_entidade"), C("objeto_id", "texto", True),
        C("data", "data", True), C("valor", "decimal"), C("moeda", "vocab", vocab="moeda"),
        C("eixo", "vocab", True, vocab="eixo"),
        C("nivel_confianca", "vocab", True, vocab="nivel_confianca"),
        C("observacao_interna", "texto", False, "Nunca vai para relatório"),
    ), prefixo="AFI", polimorficas=(("sujeito_tipo", "sujeito_id"), ("objeto_tipo", "objeto_id"))),

    # ------------------------------------------------------------------ fontes
    Tabela("fontes", "fontes", "Registro comum de toda fonte. Cada fonte tem uma linha na tabela do seu tipo.", ("id_fonte",), (
        C("id_fonte", "id", True), C("tipo_fonte", "vocab", True, vocab="tipo_fonte"),
        C("titulo", "texto", True), C("data_publicacao", "data", True),
        C("url", "url", True), C("url_arquivada", "url", False, "Cópia em arquivo da web (Wayback, archive.today)"),
        C("data_acesso", "data", True), C("sha256", "sha256", False, "Do arquivo bruto em data/raw, quando baixado"),
        C("caminho_raw", "texto"), C("licenca", "texto"), C("observacao", "texto"),
    ), prefixo="FNT", so_cresce=True),
    Tabela("fonte_judicial", "fontes", "Campos obrigatórios da fonte judicial.", ("id_fonte",), (
        C("id_fonte", "ref", True, fk="fontes.id_fonte"),
        C("numero_processo", "texto", True), C("id_orgao", "ref", True, fk="instituicoes.id_instituicao"),
        C("data_documento", "data", True), C("fase_processual", "vocab", True, vocab="fase_processual"),
        C("tipo_documento", "texto", True, "Decisão, acórdão, denúncia, despacho…"), C("link_publico", "url", True),
    )),
    Tabela("fonte_legislativa", "fontes", "Campos obrigatórios da fonte legislativa.", ("id_fonte",), (
        C("id_fonte", "ref", True, fk="fontes.id_fonte"),
        C("casa", "vocab", True, vocab="casa_legislativa"), C("proposicao", "texto", True),
        C("id_votacao", "texto", False, "Identificador da votação nominal no portal da Casa"),
        C("data", "data", True), C("link_portal", "url", True),
    )),
    Tabela("fonte_orcamentaria", "fontes", "Campos obrigatórios da fonte orçamentária e financeira.", ("id_fonte",), (
        C("id_fonte", "ref", True, fk="fontes.id_fonte"),
        C("id_orgao", "ref", True, fk="instituicoes.id_instituicao"),
        C("valor", "decimal", True), C("moeda", "vocab", True, vocab="moeda"), C("ano", "ano", True),
        C("conjunto_dados", "texto", True), C("link_dado_aberto", "url", True),
    )),
    Tabela("fonte_jornalistica", "fontes", "Campos obrigatórios da fonte jornalística.", ("id_fonte",), (
        C("id_fonte", "ref", True, fk="fontes.id_fonte"),
        C("veiculo", "texto", True), C("classe_jornalistica", "vocab", True, vocab="classe_jornalistica"),
    )),
    Tabela("fonte_oficial", "fontes", "Documento oficial não judicial (MP, PF, TCU, CGU, Itamaraty, diário oficial).", ("id_fonte",), (
        C("id_fonte", "ref", True, fk="fontes.id_fonte"),
        C("id_orgao", "ref", True, fk="instituicoes.id_instituicao"),
        C("tipo_documento", "texto", True), C("data_documento", "data", True), C("link", "url", True),
    )),
    Tabela("fonte_base_dados", "fontes", "Base de dados de pesquisa (V-Dem, Freedom House).", ("id_fonte",), (
        C("id_fonte", "ref", True, fk="fontes.id_fonte"),
        C("organizacao", "texto", True), C("conjunto", "texto", True), C("versao", "texto", True),
        C("variavel", "texto", False), C("link", "url", True),
    )),
    Tabela("evento_fonte", "fontes", "Fontes de cada evento.", ("id_evento", "id_fonte"), (
        C("id_evento", "ref", True, fk="eventos.id_evento"), FONTE,
        C("localizador", "texto", False, "Página, parágrafo ou item na fonte"),
    )),
    Tabela("relacao_fonte", "fontes", "Fontes de cada relação.", ("id_relacao", "id_fonte"), (
        C("id_relacao", "ref", True, fk="relacoes.id_relacao"), FONTE, C("localizador", "texto"),
    )),
    Tabela("afirmacao_fonte", "fontes", "Fontes de cada afirmação.", ("id_afirmacao", "id_fonte"), (
        C("id_afirmacao", "ref", True, fk="afirmacoes.id_afirmacao"), FONTE, C("localizador", "texto"),
    )),

    # ------------------------------------------------------------------ rastreabilidade
    Tabela("buscas", "rastreabilidade", "Toda consulta de coleta. É o registro formal de ausência (n_resultados = 0).", ("id_busca",), (
        C("id_busca", "id", True), C("data", "data", True),
        C("fonte_dados", "texto", True, "API ou portal consultado"),
        C("consulta", "texto", True, "Descrição reprodutível da consulta"),
        C("parametros_json", "texto", False), C("n_resultados", "inteiro", True),
        C("sha256_resposta", "sha256", False), C("caminho_raw", "texto"), C("script", "texto", True),
    ), prefixo="BSC", so_cresce=True),
    Tabela("verificacoes_simetria", "rastreabilidade", "Verificação de casos equivalentes em outros partidos para um achado.", ("id_verificacao",), (
        C("id_verificacao", "id", True),
        C("achado_tabela", "texto", True, "afirmacoes, relacoes ou status_pessoa_processo"),
        C("achado_id", "texto", True),
        C("padrao_buscado", "texto", True, "Padrão descrito de forma reprodutível"),
        C("ano_referencia", "ano", True, "Ano do fato, que define o universo de partidos"),
        C("data", "data", True), C("script", "texto", True),
    ), prefixo="VSM", so_cresce=True),
    Tabela("verificacao_resultado", "rastreabilidade", "Resultado por partido, e por governo e oposição, de cada verificação.", ("id_resultado",), (
        C("id_resultado", "id", True),
        C("id_verificacao", "ref", True, fk="verificacoes_simetria.id_verificacao"),
        C("grupo_tipo", "vocab", True, vocab="grupo_verificacao"),
        C("grupo_id", "texto", True, "id_instituicao do partido, ou 'governo' / 'oposicao'"),
        C("resultado", "vocab", True, vocab="resultado_verificacao"),
        C("n_casos", "inteiro", False), C("ids_encontrados", "lista", False),
        C("id_busca", "ref", False, fk="buscas.id_busca"),
        C("justificativa", "texto", False, "Obrigatória quando não verificado"),
    ), prefixo="VRS", so_cresce=True),
    Tabela("universo_partidos", "rastreabilidade", "Partidos que toda verificação de um ano deve cobrir.", ("ano", "id_partido"), (
        C("ano", "ano", True), C("id_partido", "ref", True, fk="instituicoes.id_instituicao"),
        C("criterio", "texto", True, "Ex.: bancada na Câmara no início do ano"), FONTE,
    )),

    Tabela("posicao_ideologica", "rastreabilidade", "Posição ideológica medida do partido, por escala publicada (D-062). Partido novo por fusão não herda.", ("id_partido", "escala"), (
        C("id_partido", "ref", True, fk="instituicoes.id_instituicao"), C("escala", "vocab", True, vocab="escala_ideologica"),
        C("ano_referencia", "ano", True, "Ano da medição"), C("rotulo_fonte", "texto", True, "Sigla ou nome como aparece na fonte"),
        C("media", "decimal", True), C("mediana", "decimal", False), C("moda", "decimal", False), C("desvio_padrao", "decimal", False),
        C("n", "inteiro", False, "Número de respondentes"), C("faixa", "vocab", True, vocab="faixa_ideologica"), FONTE,
    )),

    # ------------------------------------------------------------------ eixo 2
    Tabela("qualidade_democratica", "eixo_relacoes_externas", "Valores brutos das réguas externas, por país e ano. A classificação é calculada por código.", ("pais_iso3", "ano", "indice"), (
        C("pais_iso3", "iso3", True), C("ano", "ano", True),
        C("indice", "vocab", True, vocab="indice_democracia"), C("valor", "texto", True), FONTE,
    )),
    Tabela("operacoes_exportacao_bndes", "eixo_relacoes_externas", "Linhas (subcréditos) das operações de apoio à exportação do BNDES com país de destino, como publicadas. Linhas com o mesmo número somam a operação.", ("id_operacao",), (
        C("id_operacao", "id", True),
        C("numero_operacao", "texto", True, "Número da operação no BNDES"),
        C("linha_de_apoio", "texto", True, "Arquivo de origem: pós-embarque de serviços de engenharia ou pós-embarque de bens"),
        C("data_contratacao", "data", True),
        C("pais_destino_fonte", "texto", True, "País de destino como publicado pelo BNDES"),
        C("pais_iso3", "iso3", False, "Vazio quando o BNDES informa destinos diversos"),
        C("id_exportadora", "ref", True, fk="instituicoes.id_instituicao"),
        C("tipo_mutuario", "texto", False, "Ente público ou ente privado, como publicado (o nome do tomador não é publicado)"),
        C("descricao_projeto", "texto", True), C("modalidade", "texto", False, "Modalidade operacional (buyer, supplier)"),
        C("valor", "decimal", False, "Valor da linha na moeda da operação; o arquivo de bens não publica valores"),
        C("valor_desembolsado", "decimal", False),
        C("moeda", "vocab", True, vocab="moeda"),
        C("tipo_garantia", "texto", False), C("situacao", "texto", False, "Situação informada pelo BNDES (ativa, liquidada)"), FONTE,
    ), prefixo="BND"),
    Tabela("votos_multilaterais", "eixo_relacoes_externas", "Voto de cada país em resoluções selecionadas de organismos multilaterais (Brasil e demais países).", ("id_voto",), (
        C("id_voto", "id", True), C("id_organismo", "ref", True, fk="instituicoes.id_instituicao"),
        C("resolucao", "texto", True), C("titulo", "texto", True), C("tema", "texto", False, "Item de agenda, como publicado"),
        C("criterio_inclusao", "texto", True, "Regra de seleção que incluiu a resolução (docs/lista_e8_para_revisao.md)"),
        C("data", "data", True), C("pais_iso3", "iso3", True), C("voto", "vocab", True, vocab="voto_multilateral"),
        C("link", "url", False, "Registro da votação na fonte"),
        C("modalidade", "vocab", False, vocab="modalidade_votacao"),
        C("trecho", "texto", False, "Trecho literal da fonte que registra o voto ou a nota do país (atas e volumes da OEA)"), FONTE,
    ), prefixo="VOT"),
    Tabela("acordos_bilaterais", "eixo_relacoes_externas", "Acordos bilaterais do Brasil (todos os países, para ter denominador).", ("id_acordo",), (
        C("id_acordo", "id", True), C("pais_iso3", "iso3", True), C("titulo", "texto", True), C("tema", "texto", True),
        C("data_assinatura", "data", True), C("data_vigencia", "data", False),
        C("situacao", "texto", False, "Situação no Concórdia (em vigor, expirado, em tramitação etc.)"),
        C("id_concordia", "texto", False, "Identificador do ato no Concórdia (Itamaraty)"), C("link", "url", False), FONTE,
    ), prefixo="ACO"),

    # ------------------------------------------------------------------ eixo 3
    Tabela("decisoes_judiciais", "eixo_poder_institucional", "Decisões (universo do Corte Aberta e equivalentes), com atributos para o critério de alto impacto.", ("id_decisao",), (
        C("id_decisao", "id", True), C("id_processo", "ref", True, fk="processos.id_processo"),
        C("data", "data", True), C("tipo_decisao", "vocab", True, vocab="tipo_decisao"),
        C("id_relator", "ref", False, fk="atores.id_ator"), C("resultado", "texto", True),
        C("suspende_ato_normativo", "bool", True), C("atinge_ato_de_outro_poder", "bool", True),
        C("data_referendo", "data", False, "Data em que o colegiado apreciou a decisão monocrática"), FONTE,
    ), prefixo="DEC"),

    Tabela("emendas_parlamentares", "eixo_poder_institucional", "Execução de emendas parlamentares (Portal da Transparência), agregada por emenda, localidade e função.", ("id_emenda_linha",), (
        C("id_emenda_linha", "id", True),
        C("ano", "ano", True), C("tipo_emenda", "texto", True, "Como publicado: individual, bancada, comissão, relator"),
        C("codigo_emenda", "texto", False), C("numero_emenda", "texto", False),
        C("codigo_autor_fonte", "texto", False), C("autor_fonte", "texto", True, "Nome do autor como publicado (inclui 'RELATOR GERAL' e 'Sem informação')"),
        C("id_ator", "ref", False, "Parlamentar ligado ao autor por nome e mandato no ano, quando a ligação é única", fk="atores.id_ator"),
        C("localidade", "texto", False), C("uf", "texto", False), C("funcao", "texto", False),
        C("valor_empenhado", "decimal", True), C("valor_liquidado", "decimal", True), C("valor_pago", "decimal", True), FONTE,
    ), prefixo="EMD"),

    # ------------------------------------------------------------------ financiamento de campanha
    Tabela("doacoes_campanha", "financiamento", "Receitas de campanha (TSE). Pessoas físicas só em agregado.", ("id_doacao",), (
        C("id_doacao", "id", True), C("ano_eleicao", "ano", True),
        C("id_ator", "ref", True, "Candidato", fk="atores.id_ator"),
        C("doador_tipo", "vocab", True, vocab="doador_tipo"),
        C("id_doador", "ref", False, "Só para pessoa jurídica ou partido", fk="instituicoes.id_instituicao"),
        C("valor", "decimal", True),
        C("via", "vocab", True, vocab="via_doacao"),
        C("n_registros", "inteiro", False, "Quantidade de lançamentos somados na linha"), FONTE,
    ), prefixo="DOA"),
]

POR_NOME = {t.nome: t for t in TABELAS}
PREFIXOS = {t.prefixo: t.nome for t in TABELAS if t.prefixo}
TABELA_DA_ENTIDADE = {"ator": "atores", "instituicao": "instituicoes", "caso": "casos", "processo": "processos", "evento": "eventos"}
SUBTABELA_DA_FONTE = {
    "judicial": "fonte_judicial", "legislativa": "fonte_legislativa", "orcamentaria": "fonte_orcamentaria",
    "jornalistica": "fonte_jornalistica", "oficial": "fonte_oficial", "base_de_dados": "fonte_base_dados",
}
