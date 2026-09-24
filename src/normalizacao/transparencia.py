"""Normalização do Portal da Transparência (etapa E6).

- Acordos de leniência (CGU, Lei 12.846/2013): um evento `acordo_leniencia` por acordo, com as empresas
  ligadas por `signataria_de`. Nível `documentado` (registro oficial da CGU).
- CNEP (Cadastro Nacional de Empresas Punidas): um evento `sancao_administrativa` por sanção a pessoa
  jurídica, com a empresa ligada por `sancionada_em`. Sanções a pessoas físicas ficam só no bruto (LGPD).
- CEIS (Cadastro de Empresas Inidôneas e Suspensas): só sanções de empresas que já estão na base
  (exportadoras do BNDES, signatárias de acordos, empresas do CNEP); o cadastro inteiro fica no bruto e
  é contado nas limitações (D-027).
- Emendas parlamentares: tabela `emendas_parlamentares`, agregada por emenda, localidade e função; o
  autor é ligado a um parlamentar da base quando o nome normalizado e o mandato no ano apontam para uma
  só pessoa. O arquivo por favorecido (com nomes de pessoas físicas) fica só no bruto.

As frases de `eventos.descricao` saem de modelos fixos, com os campos publicados pela CGU.

Uso:
    python -m src.normalizacao.transparencia
"""

import csv
import datetime as dt
import zipfile
from collections import defaultdict
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, cnpj_digitos, gravar, id_empresa, ler
from src.normalizacao.legislativo import normalizar_nome

MANIFESTO = RAIZ / "data" / "manifestos" / "transparencia.csv"
LICENCA = "Dados abertos (Lei 12.527/2011)"


def data_br(v: str) -> str:
    v = (v or "").strip()
    if not v:
        return ""
    try:
        return dt.datetime.strptime(v, "%d/%m/%Y").date().isoformat()
    except ValueError:
        return ""


def valor_br(v: str) -> str:
    v = (v or "").strip()
    if not v:
        return ""
    v = v.replace(".", "").replace(",", ".")
    float(v)
    return v


def ler_zip(caminho: Path, nome_parcial: str) -> pd.DataFrame:
    with zipfile.ZipFile(caminho) as z:
        nome = next(n for n in z.namelist() if nome_parcial in n)
        with z.open(nome) as f:
            return pd.read_csv(f, sep=";", dtype=str, encoding="latin-1", keep_default_na=False)


def _col(df: pd.DataFrame, inicio: str) -> str:
    """Nome da coluna que começa com `inicio` (os cabeçalhos da CGU trazem caracteres variáveis)."""
    return next(c for c in df.columns if c.upper().startswith(inicio.upper()))


def chave_nome(nome: str) -> str:
    """Nome normalizado só com letras e espaços: "Chico D'Angelo" e "CHICO DANGELO" coincidem."""
    return " ".join("".join(c for c in normalizar_nome(nome) if c.isalnum() or c == " ").split())


def parlamentar_por_nome(atores: pd.DataFrame, cargos: pd.DataFrame) -> "callable":
    por_nome = defaultdict(set)
    for a, n in zip(atores["id_ator"], atores["nome"]):
        por_nome[chave_nome(n)].add(a)
    periodos = defaultdict(list)
    for a, i, f in zip(cargos["id_ator"], cargos["data_inicio"], cargos["data_fim"]):
        periodos[a].append((i, f or "9999"))

    def achar(nome: str, ano: str) -> str:
        cands = por_nome.get(chave_nome(nome), set())
        ativos = {a for a in cands if any(i[:4] <= ano <= f[:4] for i, f in periodos[a])}
        return next(iter(ativos)) if len(ativos) == 1 else ""
    return achar


def montar(ids: RegistroIds, base: Path = BASE) -> dict:
    man = list(csv.DictReader(MANIFESTO.open(encoding="utf-8")))
    data = max(m["data_acesso"] for m in man)
    regs = {Path(m["arquivo"]).name.split("_")[0]: m for m in man if m["data_acesso"] == data}
    cgu = ids.obter("instituicoes", "orgao:CGU")
    instituicoes = {cgu: {"id_instituicao": cgu, "nome": "Controladoria-Geral da União", "sigla": "CGU", "tipo_instituicao": "orgao_publico",
                          "poder": "executivo", "esfera": "federal", "pais_iso3": "BRA"}}
    fontes, oficiais, fonte_de = [], [], {}
    titulos = {"acordos-leniencia": "acordos de leniência", "cnep": "Cadastro Nacional de Empresas Punidas (CNEP)",
               "ceis": "Cadastro de Empresas Inidôneas e Suspensas (CEIS)", "emendas-parlamentares": "emendas parlamentares"}
    for chave, reg in regs.items():
        f = ids.obter("fontes", f"raw:{reg['arquivo']}")
        fonte_de[chave] = f
        fontes.append({"id_fonte": f, "tipo_fonte": "oficial", "titulo": f"Portal da Transparência (CGU): {titulos[chave]}", "data_publicacao": reg["data_acesso"],
                       "url": reg["url_base"], "data_acesso": reg["data_acesso"], "sha256": reg["sha256"], "caminho_raw": reg["arquivo"], "licenca": LICENCA})
        oficiais.append({"id_fonte": f, "id_orgao": cgu, "tipo_documento": "Arquivo de download de dados (CSV compactado)", "data_documento": reg["data_acesso"], "link": reg["url_base"]})

    def empresa(cnpj: str, nome: str, obs: str) -> str:
        i = id_empresa(ids, cnpj)
        instituicoes.setdefault(i, {"id_instituicao": i, "nome": nome, "tipo_instituicao": "empresa", "poder": "nao_se_aplica", "esfera": "nao_se_aplica",
                                    "pais_iso3": "BRA" if len(cnpj_digitos(cnpj)) == 14 else "", "cnpj": cnpj if len(cnpj_digitos(cnpj)) == 14 else "",
                                    "observacao": obs})
        return i

    eventos, ev_fonte, relacoes, rel_fonte = [], [], [], []

    def ligar(empresa_id: str, evento_id: str, tipo: str, data: str, fonte: str) -> None:
        r = ids.obter("relacoes", f"{empresa_id}>{tipo}>{evento_id}")
        relacoes.append({"id_relacao": r, "origem_tipo": "instituicao", "origem_id": empresa_id, "tipo_relacao": tipo, "destino_tipo": "evento",
                         "destino_id": evento_id, "data_inicio": data, "eixo": "esquemas_ilicitos", "nivel_confianca": "documentado"})
        rel_fonte.append({"id_relacao": r, "id_fonte": fonte})

    # acordos de leniência
    a = ler_zip(RAIZ / regs["acordos-leniencia"]["arquivo"], "Acordos")
    c_cnpj, c_razao, c_ini = _col(a, "CNPJ"), _col(a, "RAZÃO SOCIAL"), _col(a, "DATA DE INÍCIO")
    c_sit, c_proc = _col(a, "SITUAÇÃO"), _col(a, "NÚMERO DO PROCESSO")
    for acordo, g in a.groupby("ID DO ACORDO"):
        r0 = g.iloc[0]
        data = data_br(r0[c_ini])
        e = ids.obter("eventos", f"cgu:acordo:{acordo}")
        eventos.append({"id_evento": e, "data": data, "precisao_data": "dia", "tipo_evento": "acordo_leniencia", "eixo": "esquemas_ilicitos",
                        "descricao": f"Acordo de leniência (Lei 12.846/2013) registrado pela CGU, processo {r0[c_proc]}; situação informada: {r0[c_sit]}",
                        "pais_iso3": "BRA", "nivel_confianca": "documentado"})
        ev_fonte.append({"id_evento": e, "id_fonte": fonte_de["acordos-leniencia"], "localizador": f"ID DO ACORDO {acordo}"})
        for _, r in g.iterrows():
            ligar(empresa(r[c_cnpj], r[c_razao], "Signatária de acordo de leniência (CGU)"), e, "signataria_de", data, fonte_de["acordos-leniencia"])

    def sancoes(df: pd.DataFrame, origem: str, filtro_empresas: set | None) -> int:
        n = 0
        c_tipo, c_doc, c_nome = _col(df, "TIPO DE PESSOA"), _col(df, "CPF OU CNPJ"), _col(df, "NOME DO SANCIONADO")
        c_cat, c_ini, c_org = _col(df, "CATEGORIA DA SANÇÃO"), _col(df, "DATA INÍCIO SANÇÃO"), _col(df, "ÓRGÃO SANCIONADOR")
        c_esf, c_proc, c_cod = _col(df, "ESFERA ÓRGÃO"), _col(df, "NÚMERO DO PROCESSO"), _col(df, "CÓDIGO DA SANÇÃO")
        c_multa = next((c for c in df.columns if c.upper().startswith("VALOR DA MULTA")), None)
        for _, r in df[df[c_tipo] == "J"].iterrows():
            doc = r[c_doc]
            if filtro_empresas is not None and cnpj_digitos(doc) not in filtro_empresas:
                continue
            data = data_br(r[c_ini])
            if not data:
                continue
            e = ids.obter("eventos", f"cgu:{origem}:{r[c_cod]}")
            multa = valor_br(r[c_multa]) if c_multa else ""
            eventos.append({"id_evento": e, "data": data, "precisao_data": "dia", "tipo_evento": "sancao_administrativa", "eixo": "esquemas_ilicitos",
                            "descricao": f"Sanção registrada no {origem.upper()}: {r[c_cat]}; órgão sancionador: {r[c_org]} ({r[c_esf].lower()}); processo {r[c_proc]}",
                            "pais_iso3": "BRA", "valor": multa if multa and float(multa) > 0 else "", "moeda": "BRL" if multa and float(multa) > 0 else "",
                            "nivel_confianca": "documentado"})
            ev_fonte.append({"id_evento": e, "id_fonte": fonte_de[origem], "localizador": f"CÓDIGO DA SANÇÃO {r[c_cod]}"})
            ligar(empresa(doc, r[c_nome], f"Empresa com sanção no {origem.upper()}"), e, "sancionada_em", data, fonte_de[origem])
            n += 1
        return n

    cnep = ler_zip(RAIZ / regs["cnep"]["arquivo"], "CNEP")
    n_cnep = sancoes(cnep, "cnep", None)
    ja_na_base = {cnpj_digitos(c) for c in ler("instituicoes", base)["cnpj"]} | {cnpj_digitos(i.get("cnpj", "")) for i in instituicoes.values()}
    ja_na_base.discard("")
    ceis = ler_zip(RAIZ / regs["ceis"]["arquivo"], "CEIS")
    n_ceis = sancoes(ceis, "ceis", ja_na_base)

    # emendas parlamentares
    em = ler_zip(RAIZ / regs["emendas-parlamentares"]["arquivo"], "EmendasParlamentares.csv")
    chaves = ["Ano da Emenda", "Tipo de Emenda", "Código da Emenda", "Número da emenda", "Código do Autor da Emenda", "Nome do Autor da Emenda",
              "Localidade de aplicação do recurso", "UF", "Nome Função"]
    for c in ("Valor Empenhado", "Valor Liquidado", "Valor Pago"):
        em[c] = em[c].map(valor_br).astype(float)
    ag = em.groupby(chaves, as_index=False)[["Valor Empenhado", "Valor Liquidado", "Valor Pago"]].sum()
    achar = parlamentar_por_nome(ler("atores", base), ler("cargos", base))
    emendas = []
    for _, r in ag.iterrows():
        k = "|".join(str(r[c]) for c in chaves)
        autor = r["Nome do Autor da Emenda"]
        emendas.append({"id_emenda_linha": ids.obter("emendas_parlamentares", f"emenda:{k}"), "ano": r["Ano da Emenda"], "tipo_emenda": r["Tipo de Emenda"],
                        "codigo_emenda": r["Código da Emenda"], "numero_emenda": r["Número da emenda"], "codigo_autor_fonte": r["Código do Autor da Emenda"],
                        "autor_fonte": autor, "id_ator": achar(autor, r["Ano da Emenda"]) if autor not in ("Sem informação", "RELATOR GERAL") else "",
                        "localidade": r["Localidade de aplicação do recurso"], "uf": r["UF"], "funcao": r["Nome Função"],
                        "valor_empenhado": f"{r['Valor Empenhado']:.2f}", "valor_liquidado": f"{r['Valor Liquidado']:.2f}", "valor_pago": f"{r['Valor Pago']:.2f}",
                        "id_fonte": fonte_de["emendas-parlamentares"]})
    return {"instituicoes": list(instituicoes.values()), "fontes": fontes, "fonte_oficial": oficiais, "eventos": eventos, "evento_fonte": ev_fonte,
            "relacoes": relacoes, "relacao_fonte": rel_fonte, "emendas_parlamentares": emendas,
            "contagens": {"acordos": a["ID DO ACORDO"].nunique(), "cnep_pj": n_cnep, "ceis_total": len(ceis), "ceis_pj": int((ceis[_col(ceis, 'TIPO DE PESSOA')] == 'J').sum()),
                          "ceis_na_base": n_ceis, "emendas_linhas_fonte": len(em)}}


def _substituir(nome: str, novas: list[dict], chave: str, remover, base: Path) -> None:
    atual = ler(nome, base)
    atual = atual[~remover(atual)]
    novo = pd.DataFrame(novas, dtype=str)
    if len(novo):
        atual = atual[~atual[chave].isin(novo[chave])]
    gravar(nome, pd.concat([atual, novo], ignore_index=True), base)


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    for nome in ("fontes", "fonte_oficial"):
        atual = ler(nome, base)
        novas = [l for l in r[nome] if l["id_fonte"] not in set(atual["id_fonte"])]
        gravar(nome, pd.concat([atual, pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    _substituir("instituicoes", r["instituicoes"], "id_instituicao", lambda df: df["id_instituicao"] == "", base)
    tipos = {"acordo_leniencia", "sancao_administrativa"}
    ev_antigos = set(ler("eventos", base).query("tipo_evento in @tipos")["id_evento"])
    _substituir("eventos", r["eventos"], "id_evento", lambda df: df["tipo_evento"].isin(tipos), base)
    _substituir("evento_fonte", r["evento_fonte"], "id_evento", lambda df: df["id_evento"].isin(ev_antigos), base)
    rel_antigas = set(ler("relacoes", base).query("tipo_relacao in ['signataria_de', 'sancionada_em']")["id_relacao"])
    _substituir("relacoes", r["relacoes"], "id_relacao", lambda df: df["tipo_relacao"].isin({"signataria_de", "sancionada_em"}), base)
    _substituir("relacao_fonte", r["relacao_fonte"], "id_relacao", lambda df: df["id_relacao"].isin(rel_antigas), base)
    gravar("emendas_parlamentares", pd.DataFrame(r["emendas_parlamentares"], dtype=str), base)
    ids.salvar()


def run() -> None:
    ids = RegistroIds()
    r = montar(ids)
    gravar_resultado(r, ids)
    print(r["contagens"])
    e = pd.DataFrame(r["emendas_parlamentares"])
    individuais = e[e["tipo_emenda"].str.startswith("Emenda Individual")]
    identificados = individuais[individuais["autor_fonte"] != "Sem informação"]
    print(f"linhas de emendas na base: {len(e)}; individuais com autor identificado na fonte: {len(identificados)}, "
          f"ligadas a parlamentar: {(identificados['id_ator'] != '').mean():.1%}")
    print(e.groupby("tipo_emenda").agg(linhas=("ano", "size"), com_ator=("id_ator", lambda s: (s != "").sum())).to_string())


if __name__ == "__main__":
    run()
