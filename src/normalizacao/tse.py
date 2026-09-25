"""Normalização dos candidatos e das receitas de campanha do TSE (etapa E7, D-043).

Candidatos (eleições gerais ordinárias de 2002 a 2022, `consulta_cand_<ano>`):
- presidente: todos; governador, senador e deputado federal: só os eleitos;
- deputado federal e senador eleitos são ligados ao parlamentar da base (etapa E1) pelo nome de urna ou
  civil, entre os que têm cargo na legislatura seguinte à eleição; sem ligação única, ficam de fora e são
  contados;
- presidente e governador sem correspondência na base entram como ator novo, com a filiação ao partido
  na data da eleição (fonte: o próprio arquivo de candidatos).

Receitas (só dos candidatos acima), somadas por candidato, eleição e tipo de doador:
- pessoa física: um total por candidato (regra de dados pessoais do projeto; D-028);
- pessoa jurídica: uma linha por empresa quando o CNPJ já está na base (BNDES, CGU); as demais somadas;
- partido (inclui comitês e outros candidatos), recursos próprios, fundo público (FEFC e Fundo
  Partidário, 2018 em diante) e outros;
- 2014: o arquivo informa o doador originário dos repasses feitos por partido ou comitê; quando é empresa
  da base, entra uma linha `originario_via_partido`, que já está contida no valor do repasse.

Uso:
    python -m src.normalizacao.tse
"""

import csv
import io
import re
import unicodedata
import zipfile
from collections import defaultdict
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, cnpj_digitos, gravar, ler
from src.normalizacao.partidos import Resolvedor, linhagem, ultima_captura

MANIFESTO = RAIZ / "data" / "manifestos" / "tse.csv"
SAIDA = RAIZ / "data" / "staging" / "tse"
ANOS = [2002, 2006, 2010, 2014, 2018, 2022]
LEGISLATURA = {2002: 52, 2006: 53, 2010: 54, 2014: 55, 2018: 56, 2022: 57}
CARGOS = {"PRESIDENTE", "GOVERNADOR", "SENADOR", "DEPUTADO FEDERAL"}
RE_PARTIDO = re.compile(r"COMIT|PARTIDO|DIRET[OÓ]RIO|DIRETORIO|ELEI[CÇ][OÕ]ES|CANDIDATO")


def norm(s) -> str:
    s = "" if s is None or (isinstance(s, float) and pd.isna(s)) else str(s)
    return " ".join(unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower().split())


def digitos(s) -> str:
    return re.sub(r"\D", "", "" if s is None or (isinstance(s, float) and pd.isna(s)) else str(s))


def valor(s) -> float:
    """Valor em reais; ausente, "#NULO" ou "nan" vale zero (o lançamento continua contado em n_registros)."""
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return 0.0
    s = str(s).strip().replace("R$", "").strip()
    if not s or s.upper().startswith("#NUL") or s.lower() == "nan":
        return 0.0
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        v = float(s)
    except ValueError:
        return 0.0
    return 0.0 if v != v else v


def arquivo(nome: str) -> dict:
    man = [m for m in csv.DictReader(MANIFESTO.open(encoding="utf-8")) if m["arquivo"].endswith("/" + nome)]
    if not man:
        raise FileNotFoundError(nome)
    return max(man, key=lambda m: m["data_acesso"])


def ler_zip(reg: dict, filtro, **kw) -> pd.DataFrame:
    z = zipfile.ZipFile(RAIZ / reg["arquivo"])
    partes = []
    for nm in z.namelist():
        if filtro(nm):
            with z.open(nm) as f:
                d = pd.read_csv(io.TextIOWrapper(f, encoding="latin-1"), sep=";", dtype=str, on_bad_lines="skip", **kw)
            d.columns = [c.strip() for c in d.columns]
            partes.append(d)
    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()


# ------------------------------------------------------------------ candidatos
def candidatos(ano: int) -> pd.DataFrame:
    reg = arquivo(f"consulta_cand_{ano}.zip")
    d = ler_zip(reg, lambda n: n.endswith("_BRASIL.csv"))
    ordinaria = d["NM_TIPO_ELEICAO"].map(norm).str.contains("ordinaria")  # o código muda (2006: "0"; demais anos: "2")
    d = d[ordinaria & d["DS_CARGO"].str.upper().isin(CARGOS)].copy()
    d["NR_TURNO"] = d["NR_TURNO"].astype(int)
    d = d.sort_values("NR_TURNO").drop_duplicates(["SG_UF", "SQ_CANDIDATO"], keep="last")  # resultado final (2º turno, se houve)
    d["cargo"] = d["DS_CARGO"].str.upper()
    sit = d["DS_SIT_TOT_TURNO"].map(norm)
    d["eleito"] = sit.str.startswith("eleito") | (sit == "media")  # 2006 e 2010: "MÉDIA" = eleito pela média
    d = d[(d["cargo"] == "PRESIDENTE") | d["eleito"]]
    d["ano"], d["fonte_arquivo"] = ano, reg["arquivo"]
    return d[["ano", "SG_UF", "SQ_CANDIDATO", "cargo", "eleito", "NM_CANDIDATO", "NM_URNA_CANDIDATO", "SG_PARTIDO", "DT_ELEICAO", "fonte_arquivo"]]


PALAVRAS_VAZIAS = {"de", "da", "do", "das", "dos", "e", "dr", "dr.", "dra", "prof", "delegado", "pastor", "capitao", "coronel", "general"}


def palavras(nome: str) -> set[str]:
    return {p.strip(".") for p in norm(nome).split() if p.strip(".") not in PALAVRAS_VAZIAS}


def mandatos(cargos: pd.DataFrame, nome: dict) -> dict[tuple[str, int], set[str]]:
    """(casa, ano da eleição) -> atores com cargo naquele mandato. Deputado: pela legislatura; senador: pelo
    início do cargo nos oito anos seguintes à eleição (o cargo de senador na base não traz a legislatura)."""
    saida: dict[tuple[str, int], set[str]] = defaultdict(set)
    por_leg = {v: k for k, v in LEGISLATURA.items()}
    for _, c in cargos.iterrows():
        if c["id_ator"] not in nome:
            continue
        m = re.search(r"legislatura (\d+)", c["cargo"])
        if c["cargo"].startswith("Deputado") and m and int(m.group(1)) in por_leg:
            saida[("DEPUTADO FEDERAL", por_leg[int(m.group(1))])].add(c["id_ator"])
        elif c["cargo"].startswith("Senador") and c["data_inicio"][:4].isdigit():
            ini = int(c["data_inicio"][:4])
            for ano in LEGISLATURA:
                if ano < ini <= ano + 8:
                    saida[("SENADOR", ano)].add(c["id_ator"])
    return saida


def ligar_atores(cands: pd.DataFrame, atores: pd.DataFrame, cargos: pd.DataFrame) -> tuple[dict, dict]:
    """(ano, uf, sq) -> id_ator para deputados e senadores eleitos, e o método de cada ligação.

    `nome`: nome normalizado (de urna ou civil) igual ao da base, único entre os que têm mandato na casa;
    `palavras`: todas as palavras do nome da base (pelo menos duas, sem títulos como "Dr." ou "Coronel") estão no
    nome civil ou de urna, com correspondência única."""
    nome = dict(zip(atores["id_ator"], atores["nome_normalizado"]))
    grupos = mandatos(cargos, nome)
    ligados, metodo = {}, {}
    for _, c in cands[cands["cargo"].isin(["SENADOR", "DEPUTADO FEDERAL"])].iterrows():
        grupo = grupos.get((c["cargo"], c["ano"]), set())
        nomes_c = {norm(c["NM_URNA_CANDIDATO"]), norm(c["NM_CANDIDATO"])}
        achados = {a for a in grupo if nome[a] in nomes_c}
        m = "nome"
        if len(achados) != 1:
            pal = palavras(c["NM_URNA_CANDIDATO"]) | palavras(c["NM_CANDIDATO"])
            achados, m = {a for a in grupo if len(palavras(nome[a])) >= 2 and palavras(nome[a]) <= pal}, "palavras"
        if len(achados) == 1:
            chave = (c["ano"], c["SG_UF"], c["SQ_CANDIDATO"])
            ligados[chave], metodo[chave] = achados.pop(), m
    return ligados, metodo


# ------------------------------------------------------------------ receitas
def receitas(ano: int) -> pd.DataFrame:
    """Colunas padronizadas: uf, sq, cargo, doc, nome_doador, valor, tipo, fonte, doc_orig."""
    if ano in (2002, 2006):
        reg = arquivo(f"prestacao_contas_{ano}.zip")
        d = ler_zip(reg, lambda n: n.endswith("Candidato/Receita/ReceitaCandidato.csv"))
        if ano == 2002:
            p = pd.DataFrame({"uf": d["SG_UF"], "sq": d["SEQUENCIAL_CANDIDATO"], "cargo": d["DS_CARGO"], "doc": d["CD_CPF_CGC"],
                              "nome_doador": d["NO_DOADOR"], "nome_cand": d["NO_CAND"], "valor": d["VR_RECEITA"], "tipo": "", "fonte": ""})
        else:
            p = pd.DataFrame({"uf": d["UNIDADE_ELEITORAL_CANDIDATO"], "sq": d["SEQUENCIAL_CANDIDATO"], "cargo": d["DESCRICAO_CARGO"],
                              "doc": d["NUMERO_CPF_CGC_DOADOR"], "nome_doador": d["NOME_DOADOR"], "nome_cand": d["NOME_CANDIDATO"],
                              "valor": d["VALOR_RECEITA"], "tipo": d["TIPO_RECEITA"], "fonte": ""})
        p["doc_orig"] = ""
    elif ano == 2010:
        reg = arquivo("prestacao_contas_2010.zip")
        d = ler_zip(reg, lambda n: n.startswith("candidato/") and n.endswith("ReceitasCandidatos.txt"))
        p = pd.DataFrame({"uf": d["UF"], "sq": d["Sequencial Candidato"], "cargo": d["Cargo"], "doc": d["CPF/CNPJ do doador"],
                          "nome_doador": d["Nome do doador"], "nome_cand": d["Nome candidato"], "valor": d["Valor receita"],
                          "tipo": d["Tipo receita"], "fonte": "", "doc_orig": ""})
    elif ano == 2014:
        reg = arquivo("prestacao_final_2014.zip")
        d = ler_zip(reg, lambda n: n == "receitas_candidatos_2014_brasil.txt")
        p = pd.DataFrame({"uf": d["UF"], "sq": d["Sequencial Candidato"], "cargo": d["Cargo"], "doc": d["CPF/CNPJ do doador"],
                          "nome_doador": d["Nome do doador"], "nome_cand": d["Nome candidato"], "valor": d["Valor receita"],
                          "tipo": d["Tipo receita"], "fonte": "", "doc_orig": d["CPF/CNPJ do doador originário"]})
    else:
        reg = arquivo(f"prestacao_de_contas_eleitorais_candidatos_{ano}.zip")
        d = ler_zip(reg, lambda n: n.lower() == f"receitas_candidatos_{ano}_brasil.csv")
        # a prestação final já contém as parciais e o relatório financeiro; cada receita conta uma vez (1º e 2º turno repetem)
        tipo_p = d["TP_PRESTACAO_CONTAS"].map(norm)
        d = d[tipo_p.isin(["final", "regularizacao da omissao"])].drop_duplicates("SQ_RECEITA")
        p = pd.DataFrame({"uf": d["SG_UF"], "sq": d["SQ_CANDIDATO"], "cargo": d["DS_CARGO"], "doc": d["NR_CPF_CNPJ_DOADOR"],
                          "nome_doador": d["NM_DOADOR"], "nome_cand": d["NM_CANDIDATO"], "valor": d["VR_RECEITA"],
                          "tipo": d["DS_ORIGEM_RECEITA"], "fonte": d["DS_FONTE_RECEITA"], "doc_orig": ""})
    p["cargo"] = p["cargo"].str.upper().str.strip()
    p["ano"], p["fonte_arquivo"] = ano, reg["arquivo"]
    return p[p["cargo"].isin(CARGOS)].copy()


def tipo_doador(r) -> str:
    t, f = norm(r["tipo"]), norm(r["fonte"])
    if "fundo especial" in f or "fundo partidario" in f:
        return "fundo_publico"
    if t:
        if "propri" in t:
            return "recursos_proprios"
        if "juridic" in t:
            return "pessoa_juridica"
        if "partido" in t or "outros candidatos" in t or "comite" in t:
            return "partido"
        if "fisica" in t or "internet" in t or "financiamento coletivo" in t:
            return "pessoa_fisica_agregado"
        return "outro"
    doc = digitos(r["doc"])  # 2002: sem tipo de receita; decide pelo documento e pelo nome
    if norm(r["nome_doador"]) and norm(r["nome_doador"]) == norm(r["nome_cand"]):
        return "recursos_proprios"
    if len(doc) == 14:
        return "partido" if RE_PARTIDO.search(str(r["nome_doador"]).upper()) else "pessoa_juridica"
    if len(doc) == 11:
        return "pessoa_fisica_agregado"
    return "outro"


# ------------------------------------------------------------------ montagem
def montar(ids: RegistroIds, anos: list[int] = ANOS) -> dict:
    atores, cargos = ler("atores"), ler("cargos")
    inst = ler("instituicoes")
    empresa_de = {cnpj_digitos(c): i for i, c in zip(inst["id_instituicao"], inst["cnpj"]) if c}
    _, tabelas = ultima_captura()
    resolver = Resolvedor(linhagem(tabelas))
    por_nome = defaultdict(set)
    for i, n in zip(atores["id_ator"], atores["nome_normalizado"]):
        por_nome[n].add(i)
    tse = ids.obter("instituicoes", "orgao:TSE")
    fontes, oficiais, f_de = [], [], {}

    def fonte(arq: str) -> str:
        if arq not in f_de:
            reg = next(m for m in csv.DictReader(MANIFESTO.open(encoding="utf-8")) if m["arquivo"] == arq)
            f = ids.obter("fontes", f"raw:{arq}")
            nome = Path(arq).name
            fontes.append({"id_fonte": f, "tipo_fonte": "oficial", "titulo": f"TSE, dados abertos: {nome}", "data_publicacao": reg["data_acesso"],
                           "url": reg["url_base"], "data_acesso": reg["data_acesso"], "sha256": reg["sha256"], "caminho_raw": arq,
                           "licenca": "Dados públicos (Lei 12.527/2011)", "observacao": "Download feito pelo autor no navegador (D-042)"})
            oficiais.append({"id_fonte": f, "id_orgao": tse, "tipo_documento": "Conjunto de dados abertos (ZIP)", "data_documento": reg["data_acesso"],
                             "link": reg["url_base"]})
            f_de[arq] = f
        return f_de[arq]

    novos_atores, filiacoes, doacoes = {}, [], {}
    resumo = []
    for ano in anos:
        cands = candidatos(ano)
        ligados, metodo = ligar_atores(cands, atores, cargos)
        mapa = {}
        for _, c in cands.iterrows():
            chave = (c["ano"], c["SG_UF"], c["SQ_CANDIDATO"])
            if chave in ligados:
                mapa[chave] = ligados[chave]
                continue
            if c["cargo"] not in ("PRESIDENTE", "GOVERNADOR"):
                continue  # deputado ou senador eleito sem ligação única com a base: contado no resumo
            n_civil = norm(c["NM_CANDIDATO"])
            existentes = por_nome.get(n_civil, set()) | por_nome.get(norm(c["NM_URNA_CANDIDATO"]), set())
            if len(existentes) == 1:
                a = next(iter(existentes))
            else:
                a = ids.obter("atores", f"tse_nome:{n_civil}")
                publico = c["eleito"] or novos_atores.get(a, {}).get("tipo_ator") == "agente_publico"
                novos_atores[a] = {"id_ator": a, "nome": c["NM_CANDIDATO"].strip(), "nome_normalizado": n_civil,
                                   "tipo_ator": "agente_publico" if publico else "agente_privado",
                                   "observacao": "Candidato em eleição geral (TSE); entrou na etapa E7"}
                por_nome[n_civil].add(a)
            mapa[chave] = a
            data = "-".join(reversed(c["DT_ELEICAO"].split("/")))
            p, _ = resolver(c["SG_PARTIDO"], data)
            if p is not None:
                filiacoes.append({"id_filiacao": ids.obter("filiacoes", f"tse:{ano}:{c['SG_UF']}:{c['SQ_CANDIDATO']}"), "id_ator": a,
                                  "id_partido": ids.obter("instituicoes", p.chave), "data_inicio": data, "data_fim": data,
                                  "id_fonte": fonte(c["fonte_arquivo"])})
        sem = cands[[(r.ano, r.SG_UF, r.SQ_CANDIDATO) not in mapa for r in cands.itertuples()]]
        rec = receitas(ano)
        rec["chave"] = list(zip(rec["ano"], rec["uf"], rec["sq"]))
        if ano >= 2018:  # sequencial único no país: a UF do arquivo de receitas pode ser BR para presidente
            por_sq = {k[2]: v for k, v in mapa.items()}
            rec["id_ator"] = rec["sq"].map(por_sq)
        else:
            rec["id_ator"] = rec["chave"].map(mapa)
        rec = rec[rec["id_ator"].notna()].copy()
        rec["tipo_doador"] = rec.apply(tipo_doador, axis=1)
        rec["v"] = rec["valor"].map(valor)
        rec["doc_d"] = rec["doc"].map(digitos)
        for r in rec.itertuples():
            emp = empresa_de.get(r.doc_d) if r.tipo_doador == "pessoa_juridica" else None
            linhas = [(r.tipo_doador, emp or "", "direta")]
            orig = digitos(r.doc_orig)
            if r.tipo_doador == "partido" and orig in empresa_de:
                linhas.append(("pessoa_juridica", empresa_de[orig], "originario_via_partido"))
            for tipo, doador, via in linhas:
                k = (ano, r.id_ator, tipo, doador, via, r.fonte_arquivo)
                e = doacoes.setdefault(k, [0.0, 0])
                e[0] += r.v
                e[1] += 1
        resumo.append({"ano": ano, "candidatos_alvo": len(cands), "ligados_por": pd.Series(list(metodo.values()), dtype=str).value_counts().to_dict(),
                       "sem_ligacao": len(sem), "sem_ligacao_cargos": sem["cargo"].value_counts().to_dict(),
                       "receitas_lidas": len(rec)})
        print(resumo[-1])
    linhas = []
    for (ano, a, tipo, doador, via, arq), (v, n) in doacoes.items():
        linhas.append({"id_doacao": ids.obter("doacoes_campanha", f"tse:{ano}:{a}:{tipo}:{doador}:{via}"), "ano_eleicao": str(ano), "id_ator": a,
                       "doador_tipo": tipo, "id_doador": doador, "valor": f"{v:.2f}", "via": via, "n_registros": str(n), "id_fonte": fonte(arq)})
    return {"atores": list(novos_atores.values()), "filiacoes": filiacoes, "doacoes_campanha": linhas, "fontes": fontes, "fonte_oficial": oficiais,
            "resumo": resumo}


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    for nome in ("fontes", "fonte_oficial"):
        atual = ler(nome, base)
        novas = [l for l in r[nome] if l["id_fonte"] not in set(atual["id_fonte"])]
        gravar(nome, pd.concat([atual, pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    for nome, chave in (("atores", "id_ator"), ("filiacoes", "id_filiacao"), ("doacoes_campanha", "id_doacao")):
        atual = ler(nome, base)
        novos = pd.DataFrame(r[nome], dtype=str)
        if nome == "doacoes_campanha":
            atual = atual.iloc[0:0]  # a tabela inteira sai do TSE; é refeita a cada execução
        gravar(nome, pd.concat([atual[~atual[chave].isin(novos[chave])] if len(novos) else atual, novos], ignore_index=True), base)
    ids.salvar()
    SAIDA.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(r["resumo"]).to_csv(SAIDA / "resumo.csv", index=False, encoding="utf-8")


def run() -> None:
    ids = RegistroIds()
    r = montar(ids)
    gravar_resultado(r, ids)
    d = pd.DataFrame(r["doacoes_campanha"])
    d["valor"] = d["valor"].astype(float)
    print(f"atores novos: {len(r['atores'])}; filiações: {len(r['filiacoes'])}; linhas de doação: {len(d)}")
    print(d.groupby(["ano_eleicao", "doador_tipo"])["valor"].sum().div(1e6).round(1).unstack(fill_value=0).to_string())


if __name__ == "__main__":
    run()
