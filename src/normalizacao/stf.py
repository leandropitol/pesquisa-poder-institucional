"""Normalização das exportações do Corte Aberta do STF (etapa E5) para `processos` e `fases_processo`.

Entradas (D-037): decisões em AP e Inq de 2003 em diante e acervo de AP e Inq em tramitação.

- `processos`: todas as AP e Inq das duas planilhas. O Corte Aberta traz um único assunto por processo,
  como caminho da classificação do STF ("DIREITO PENAL | CRIMES PRATICADOS POR FUNCIONÁRIOS PÚBLICOS
  CONTRA A ADMINISTRAÇÃO EM GERAL | PECULATO"), gravado com o prefixo "STF:".
- Assuntos: regra por caminho em data/curadoria/assuntos_stf_eixo1.csv (inclui, conexo, exclui,
  indeterminado), gerada por `regra_caminho` e revisável; decisões já registradas não mudam.
- Universo do eixo 1 (calculado, não gravado): `sim` para assunto `inclui`; `revisar` para
  `indeterminado` e `conexo` (com um só assunto por processo não dá para ver a conexão); `nao` para
  `exclui`. Processos com assunto genérico ganham uma segunda leitura pelo texto das decisões
  (`indicios_no_texto`), que só orienta a revisão e não põe ninguém no universo.
- `fases_processo`: andamentos de decisão com correspondência inequívoca no vocabulário (MAPA_FASES).

Uso:
    python -m src.normalizacao.stf
"""

import csv
import re
import unicodedata
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, acrescentar, gravar, ler

MANIFESTO = RAIZ / "data" / "manifestos" / "stf.csv"
CURADORIA = RAIZ / "data" / "curadoria"
CUR_ASSUNTOS = CURADORIA / "assuntos_stf_eixo1.csv"
SAIDA = RAIZ / "data" / "staging" / "stf"
URL_PROCESSO = "https://portal.stf.jus.br/processos/listarProcessos.asp?classe={classe}&numeroProcesso={numero}"
CLASSES = {"AP": "acao_penal", "Inq": "inquerito"}

# Capítulos do Título XI do Código Penal (protocolo: arts. 312 a 359-H), como aparecem na classificação do STF
TITULO_XI = {
    "CRIMES PRATICADOS POR FUNCIONARIOS PUBLICOS CONTRA A ADMINISTRACAO EM GERAL": "Capítulo I",
    "CRIMES PRATICADOS POR PARTICULAR CONTRA A ADMINISTRACAO EM GERAL": "Capítulo II",
    "CRIMES PRATICADOS POR PARTICULAR CONTRA A ADMINISTRACAO PUBLICA ESTRANGEIRA": "Capítulo II-A",
    "CRIMES CONTRA A ADMINISTRACAO DA JUSTICA": "Capítulo III",
    "CRIMES CONTRA AS FINANCAS PUBLICAS": "Capítulo IV",
    "CRIMES CONTRA A ADMINISTRACAO PUBLICA": "Título XI",
}
GENERICOS = {"*NI*", "DIREITO PENAL", "DIREITO PROCESSUAL PENAL", "ACAO PENAL", "INVESTIGACAO PENAL", "JURISDICAO E COMPETENCIA",
             "COMPETENCIA POR PRERROGATIVA DE FUNCAO", "DENUNCIA/QUEIXA", "CRIMES PREVISTOS NA LEGISLACAO EXTRAVAGANTE", "INQUERITO",
             "INQUERITO POLICIAL", "PROVAS", "PRISAO PREVENTIVA", "ACAO PENAL ORIGINARIA"}
RE_TIPOS = re.compile(r"PECULATO|CONCUSSAO|CORRUPCAO (?:PASSIVA|ATIVA)|PREVARICACAO|ADVOCACIA ADMINISTRATIVA|TRAFICO DE INFLUENCIA|"
                      r"LAVAGEM|OCULTACAO DE BENS|LICITAC|ORGANIZACAO CRIMINOSA|EMPREGO IRREGULAR DE VERBAS|EXPLORACAO DE PRESTIGIO")
# Termos procurados no texto das decisões dos processos com assunto genérico (só orientam a revisão)
RE_INDICIO = re.compile(r"PECULATO|CONCUSSAO|CORRUPCAO PASSIVA|CORRUPCAO ATIVA|PREVARICACAO|ADVOCACIA ADMINISTRATIVA|TRAFICO DE INFLUENCIA|"
                        r"LAVAGEM DE (?:DINHEIRO|CAPITAIS|BENS)|LEI N?[º°O.]*\s*9\.?613|LEI N?[º°O.]*\s*8\.?666|LEI N?[º°O.]*\s*12\.?850|"
                        r"ORGANIZACAO CRIMINOSA|ARTS?\.?\s*(?:312|313|316|317|319|321|332|333)\b|DISPENSA (?:INDEVIDA )?DE LICITACAO|FRAUDE A LICITACAO")
# Tipos fora do protocolo citados no texto (Título XII do CP, crimes contra o Estado Democrático de Direito, entre outros)
RE_FORA = re.compile(r"ESTADO DEMOCRATICO DE DIREITO|ARTS?\.?\s*359-[L-R]|GOLPE DE ESTADO|DANO QUALIFICADO|DETERIORACAO DE PATRIMONIO TOMBADO")
MAPA_FASES = {
    "RECEBIDA DENUNCIA": "recebimento_denuncia", "RECEBIDA DENUNCIA EM PARTE": "recebimento_denuncia",
    "JULG. DO PLENO - RECEBIDA A DENUNCIA": "recebimento_denuncia",
    "REJEITADA A DENUNCIA": "rejeicao_denuncia", "JULGAMENTO DO PLENO - REJEITADA DENUNCIA": "rejeicao_denuncia",
    "DECLINADA A COMPETENCIA": "declinio_competencia", "DECISAO DO(A) RELATOR(A) - DECLINANDO DA COMPETENCIA": "declinio_competencia",
    "DECLARADA A EXTINCAO DA PUNIBILIDADE": "extincao_punibilidade", "DECISAO DO(A) RELATOR(A) - EXTINCAO DA PUNIBILIDADE": "extincao_punibilidade",
    "JULG. POR DESP.-EXTINCAO DA PUNIBILIDADE": "extincao_punibilidade",
}
MAPA_FASES_INQ = {  # arquivamento só é fase de inquérito
    "DETERMINADO ARQUIVAMENTO": "arquivamento_inquerito", "DECISAO DO(A) RELATOR(A) - ARQUIVADO": "arquivamento_inquerito",
    "JULGAMENTO DO PLENO - ARQUIVADO": "arquivamento_inquerito", "DECISAO DA PRESIDENCIA - ARQUIVADO": "arquivamento_inquerito",
}
MAPA_FASES_AP = {  # julgamento de mérito da ação penal originária (decisão final)
    "PROCEDENTE": "acordao_tribunal_superior", "PROCEDENTE EM PARTE": "acordao_tribunal_superior",
    "IMPROCEDENTE": "acordao_tribunal_superior", "JULGAMENTO DO PLENO - IMPROCEDENTE": "acordao_tribunal_superior",
}


def norm(s) -> str:
    s = "" if s is None or (isinstance(s, float) and pd.isna(s)) else str(s)
    return " ".join(unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").upper().split())


def segmentos(caminho: str) -> list[str]:
    return [p.strip() for p in norm(caminho).split("|") if p.strip()]


def numero_cnj(digitos: str) -> str:
    d = re.sub(r"\D", "", str(digitos or ""))
    return f"{d[:7]}-{d[7:9]}.{d[9:13]}.{d[13]}.{d[14:16]}.{d[16:20]}" if len(d) == 20 else ""


def regras_tpu() -> dict[str, tuple[str, str]]:
    """Nome normalizado -> (decisão, fundamento), da curadoria já aprovada para o STJ (D-025)."""
    return {norm(l["nome_tpu"]): (l["decisao"], l["fundamento"]) for l in csv.DictReader((CURADORIA / "assuntos_tpu_eixo1.csv").open(encoding="utf-8"))
            if l["nome_tpu"]}


def regra_caminho(caminho: str, tpu: dict) -> tuple[str, str, str]:
    """(decisão, fundamento, origem da regra) para um caminho de assunto do STF."""
    seg = segmentos(caminho)
    if not seg or all(s in GENERICOS for s in seg):
        return "indeterminado", "assunto genérico (o Corte Aberta traz um só assunto por processo): revisar pela fonte primária", "generico"
    for s in seg:
        if s in TITULO_XI:
            return "inclui", f"CP Título XI, {TITULO_XI[s]} (protocolo: arts. 312 a 359-H)", "titulo_xi"
    folha = seg[-1]
    if "CRIMES ELEITORAIS" in seg or "CRIME ELEITORAL" in seg:
        if folha in ("CRIMES ELEITORAIS", "CRIME ELEITORAL") or "FALSIDADE IDEOLOGICA" in folha or "FALSO ELEITORAL" in folha:
            return "conexo", "Código Eleitoral; o protocolo inclui o art. 350 conexo aos demais tipos", "eleitoral"
        return "exclui", "tipo eleitoral fora do protocolo (só o art. 350 entra, conexo)", "eleitoral"
    if folha in tpu:
        d, f = tpu[folha]
        return d, f, "tpu_nome"
    if seg[0].startswith("DIREITO ADMINISTRATIVO"):
        return "indeterminado", "assunto de direito administrativo em ação penal ou inquérito: revisar pela fonte primária", "administrativo"
    if RE_TIPOS.search(folha):
        return "inclui", "tipo do protocolo citado no assunto", "palavra_chave"
    if folha in GENERICOS:
        return "indeterminado", "assunto genérico: revisar pela fonte primária", "generico"
    for s in reversed(seg[:-1]):
        if s in tpu and tpu[s][0] == "exclui" and s not in GENERICOS:
            return "exclui", f"categoria fora dos tipos do protocolo ({s.title()})", "categoria_tpu"
    return "exclui", "fora dos tipos do protocolo", "residual"


def atualizar_curadoria(contagem: pd.Series) -> pd.DataFrame:
    """Acrescenta caminhos novos com a regra; linhas existentes (e a decisão registrada nelas) não mudam."""
    tpu = regras_tpu()
    atual = pd.read_csv(CUR_ASSUNTOS, dtype=str, keep_default_na=False) if CUR_ASSUNTOS.exists() else pd.DataFrame(
        columns=["caminho_stf", "n_processos", "decisao", "fundamento", "origem_regra"])
    atual["n_processos"] = atual["caminho_stf"].map(contagem).fillna(0).astype(int).astype(str)
    novos = [{"caminho_stf": c, "n_processos": str(n), **dict(zip(("decisao", "fundamento", "origem_regra"), regra_caminho(c, tpu)))}
             for c, n in contagem.items() if c not in set(atual["caminho_stf"])]
    saida = pd.concat([atual, pd.DataFrame(novos, columns=atual.columns)], ignore_index=True)
    saida = saida.sort_values(["decisao", "n_processos"], key=lambda s: s.astype(int) if s.name == "n_processos" else s, ascending=[True, False])
    saida.to_csv(CUR_ASSUNTOS, index=False, encoding="utf-8", lineterminator="\n")
    return saida


def ler_exportacoes() -> tuple[dict, pd.DataFrame, dict, pd.DataFrame]:
    man = list(csv.DictReader(MANIFESTO.open(encoding="utf-8")))
    reg_dec = max((m for m in man if "decisoes" in m["arquivo"]), key=lambda m: m["data_acesso"])
    reg_ace = max((m for m in man if "acervo" in m["arquivo"]), key=lambda m: m["data_acesso"])
    dec = pd.read_excel(RAIZ / reg_dec["arquivo"], dtype=str).fillna("")
    ace = pd.read_excel(RAIZ / reg_ace["arquivo"], dtype=str).fillna("")
    return reg_dec, dec, reg_ace, ace


def indicios_no_texto(dec: pd.DataFrame, regex: re.Pattern = RE_INDICIO) -> dict[str, str]:
    """Processo -> termos citados no texto das decisões (orienta a revisão; não decide)."""
    saida = {}
    for proc, textos in dec.groupby("Processo")["Observação do andamento"]:
        achados = sorted({m.group(0) for t in textos for m in regex.finditer(norm(t))})
        if achados:
            saida[proc] = "; ".join(achados)
    return saida


def montar(ids: RegistroIds) -> dict:
    reg_dec, dec, reg_ace, ace = ler_exportacoes()
    stf = ids.obter("instituicoes", "orgao:STF")
    inst = [{"id_instituicao": stf, "nome": "Supremo Tribunal Federal", "sigla": "STF", "tipo_instituicao": "tribunal", "poder": "judiciario",
             "esfera": "federal", "pais_iso3": "BRA"}]
    fontes, oficiais, f_de = [], [], {}
    for reg, titulo in ((reg_dec, "decisões em ações penais e inquéritos, 08/01/2003 a 23/09/2026"), (reg_ace, "acervo de ações penais e inquéritos em tramitação")):
        f = ids.obter("fontes", f"raw:{reg['arquivo']}")
        f_de[reg["arquivo"]] = f
        fontes.append({"id_fonte": f, "tipo_fonte": "oficial", "titulo": f"STF, Corte Aberta: {titulo} (exportação do painel)", "data_publicacao": reg["data_acesso"],
                       "url": reg["url_base"], "data_acesso": reg["data_acesso"], "sha256": reg["sha256"], "caminho_raw": reg["arquivo"],
                       "licenca": "Dados públicos do STF; licença não informada no painel", "observacao": "Exportação feita pelo autor no navegador (D-037)"})
        oficiais.append({"id_fonte": f, "id_orgao": stf, "tipo_documento": "Exportação de painel estatístico (XLSX)", "data_documento": reg["data_acesso"],
                         "link": reg["url_base"]})
    f_dec, f_ace = f_de[reg_dec["arquivo"]], f_de[reg_ace["arquivo"]]

    por_proc = {}
    for _, r in dec.drop_duplicates("Processo").iterrows():
        por_proc[r["Processo"]] = {"assunto": r["Assuntos do processo"], "autuacao": r["Data de autuação"][:10], "cnj": "", "fonte": f_dec}
    for _, r in ace.iterrows():
        base = por_proc.setdefault(r["Processo"], {"assunto": r["Assuntos"], "autuacao": r["Data autuação"][:10], "cnj": "", "fonte": f_ace})
        base["cnj"] = numero_cnj(r["Número único"])
    processos, id_de = [], {}
    for proc, x in sorted(por_proc.items()):
        classe, numero = proc.split(" ", 1)
        p = ids.obter("processos", f"stf:{proc}")
        id_de[proc] = p
        processos.append({"id_processo": p, "numero_cnj": x["cnj"], "numero_originario": proc, "classe": CLASSES[classe], "id_tribunal": stf,
                          "data_autuacao": x["autuacao"], "assuntos_tpu": f"STF:{x['assunto']}", "sigilo": "",
                          "url": URL_PROCESSO.format(classe=classe, numero=numero), "id_fonte": x["fonte"]})
    fases = []
    for _, r in dec.iterrows():
        classe = r["Processo"].split(" ", 1)[0]
        andamento = norm(r["Andamento decisão"])
        fase = MAPA_FASES.get(andamento) or (MAPA_FASES_INQ.get(andamento) if classe == "Inq" else None) \
            or (MAPA_FASES_AP.get(andamento) if classe == "AP" and r["Tipo decisão"] == "Decisão Final" else None)
        if not fase:
            continue
        fases.append({"id_fase": ids.obter("fases_processo", f"stf:decisao:{r['idFatoDecisao']}"), "id_processo": id_de[r["Processo"]],
                      "data": r["Data da decisão"][:10], "fase": fase, "id_orgao_julgador": stf,
                      "resumo": f"{r['Andamento decisão']} ({r['Órgão julgador'].lower()})", "id_fonte": f_dec})
    return {"instituicoes": inst, "fontes": fontes, "fonte_oficial": oficiais, "processos": processos, "fases_processo": fases, "decisoes": dec}


def universo(processos: pd.DataFrame, regras: dict[str, str]) -> pd.Series:
    d = processos["assuntos_tpu"].str.removeprefix("STF:").map(regras).fillna("indeterminado")
    u = d.map({"inclui": "sim", "exclui": "nao", "qualificador": "revisar"}).fillna("revisar")
    return u.where(processos["data_autuacao"] >= "2003", u.replace({"sim": "antes_de_2003"}))


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    for nome in ("fontes", "fonte_oficial"):
        atual = ler(nome, base)
        novas = [l for l in r[nome] if l["id_fonte"] not in set(atual["id_fonte"])]
        gravar(nome, pd.concat([atual, pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    atual = ler("instituicoes", base)
    novas = pd.DataFrame(r["instituicoes"], dtype=str)
    gravar("instituicoes", pd.concat([atual[~atual["id_instituicao"].isin(novas["id_instituicao"])], novas], ignore_index=True), base)
    atual = ler("processos", base)
    novos = pd.DataFrame(r["processos"], dtype=str)
    gravar("processos", pd.concat([atual[~atual["id_processo"].isin(novos["id_processo"])], novos], ignore_index=True), base)
    existentes = set(ler("fases_processo", base)["id_fase"])
    acrescentar("fases_processo", [x for x in r["fases_processo"] if x["id_fase"] not in existentes], base)  # histórico só cresce
    ids.salvar()


def run() -> None:
    ids = RegistroIds()
    r = montar(ids)
    p = pd.DataFrame(r["processos"])
    cur = atualizar_curadoria(p["assuntos_tpu"].str.removeprefix("STF:").value_counts())
    gravar_resultado(r, ids)
    p["universo"] = universo(p, dict(zip(cur["caminho_stf"], cur["decisao"])))
    p["indicios_texto"] = p["numero_originario"].map(indicios_no_texto(r["decisoes"])).fillna("")
    p["indicios_fora"] = p["numero_originario"].map(indicios_no_texto(r["decisoes"], RE_FORA)).fillna("")
    p["triagem"] = ""
    rev = p["universo"] == "revisar"
    p.loc[rev, "triagem"] = "sem_indicio"
    p.loc[rev & (p["indicios_fora"] != ""), "triagem"] = "indicio_fora_do_protocolo"
    p.loc[rev & (p["indicios_texto"] != ""), "triagem"] = "indicio_do_protocolo"
    SAIDA.mkdir(parents=True, exist_ok=True)
    p[["id_processo", "numero_originario", "data_autuacao", "assuntos_tpu", "universo", "triagem", "indicios_texto", "indicios_fora"]].to_csv(
        SAIDA / "universo_stf.csv", index=False, encoding="utf-8")
    print(p.groupby(["classe", "universo"]).size().to_string())
    print("triagem de revisar:", p.loc[rev, "triagem"].value_counts().to_dict())
    print(f"fases: {pd.Series([f['fase'] for f in r['fases_processo']]).value_counts().to_dict()}")
    print(f"curadoria de assuntos: {cur['decisao'].value_counts().to_dict()} caminhos")


if __name__ == "__main__":
    run()
