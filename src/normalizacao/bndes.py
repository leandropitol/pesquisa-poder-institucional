"""Normalização das operações de exportação do BNDES (etapa E3) para `operacoes_exportacao_bndes`.

Entram os dois arquivos com país de destino: pós-embarque de serviços de engenharia (obras no
exterior, com valores) e pós-embarque de bens (o arquivo aberto não publica valores). O arquivo de
pré-embarque financia o exportador no Brasil, sem país de destino, e fica só no bruto.

Cada linha do arquivo (subcrédito) vira uma linha da base, com o valor como publicado. Exportadoras
entram como instituições de tipo `empresa` (CNPJ e nome publicados pelo BNDES). Países de destino
ligados ao código ISO por data/curadoria/paises_bndes.csv.

Uso:
    python -m src.normalizacao.bndes
"""

import csv
import hashlib
from collections import Counter
from pathlib import Path

import pandas as pd

from src.base import BASE, RAIZ, RegistroIds, gravar, ler

MANIFESTO = RAIZ / "data" / "manifestos" / "bndes.csv"
CURADORIA = RAIZ / "data" / "curadoria"
ARQUIVOS = {
    "operacoes-exportacao-operacoes-de-exportacao-pos-embarque-servicos-de-engenharia.csv": "Pós-embarque, serviços de engenharia",
    "operacoes-exportacao-operacoes-de-exportacao-pos-embarque-bens.csv": "Pós-embarque, bens",
}
MOEDAS = {"US$ COMPRA": "USD", "EUR C": "EUR"}


def numero_br(v: str) -> str:
    """'64400000,0' -> '64400000.0'; vazio continua vazio. Mantém a precisão publicada."""
    v = (v or "").strip()
    if not v:
        return ""
    v = v.replace(".", "").replace(",", ".") if "," in v else v
    float(v)  # falha se não for número
    return v


def chave_linha(linha: dict, ocorrencia: int) -> str:
    conteudo = "|".join(f"{k}={(linha[k] or '').strip()}" for k in sorted(linha))
    return hashlib.sha1(conteudo.encode("utf-8")).hexdigest()[:16] + f"#{ocorrencia}"


def ler_csv(caminho: Path) -> pd.DataFrame:
    return pd.read_csv(caminho, sep=";", dtype=str, encoding="latin-1", keep_default_na=False)


def montar(ids: RegistroIds) -> dict:
    man = list(csv.DictReader(MANIFESTO.open(encoding="utf-8")))
    data = max(m["data_acesso"] for m in man)
    regs = {Path(m["arquivo"]).name: m for m in man if m["data_acesso"] == data}
    paises = {l["pais_destino_bndes"]: l["pais_iso3"] for l in csv.DictReader((CURADORIA / "paises_bndes.csv").open(encoding="utf-8"))}

    bndes = ids.obter("instituicoes", "orgao:BNDES")
    instituicoes = {bndes: {"id_instituicao": bndes, "nome": "Banco Nacional de Desenvolvimento Econômico e Social", "sigla": "BNDES",
                            "tipo_instituicao": "banco_publico", "poder": "executivo", "esfera": "federal", "pais_iso3": "BRA"}}
    fontes, oficiais, linhas, sem_pais = [], [], [], Counter()
    for arquivo, linha_apoio in ARQUIVOS.items():
        reg = regs[arquivo]
        f = ids.obter("fontes", f"raw:{reg['arquivo']}")
        fontes.append({"id_fonte": f, "tipo_fonte": "oficial", "titulo": f"BNDES, dados abertos: operações de exportação ({linha_apoio.lower()})",
                       "data_publicacao": reg["data_acesso"], "url": reg["url_base"], "data_acesso": reg["data_acesso"], "sha256": reg["sha256"],
                       "caminho_raw": reg["arquivo"], "licenca": "Dados abertos (Lei 12.527/2011)"})
        oficiais.append({"id_fonte": f, "id_orgao": bndes, "tipo_documento": "Conjunto de dados abertos (CSV)", "data_documento": reg["data_acesso"], "link": reg["url_base"]})
        d = ler_csv(RAIZ / reg["arquivo"])
        vistos: Counter = Counter()
        for _, r in d.iterrows():
            r = {k: (v or "").strip() for k, v in r.items()}
            base_chave = chave_linha(r, 0)[:16]
            vistos[base_chave] += 1
            cnpj = r["cnpj_do_exportador"]
            exp = ids.obter("instituicoes", f"cnpj:{cnpj}")
            instituicoes.setdefault(exp, {"id_instituicao": exp, "nome": r["exportador"], "tipo_instituicao": "empresa", "poder": "nao_se_aplica",
                                          "esfera": "nao_se_aplica", "pais_iso3": "BRA", "cnpj": cnpj,
                                          "observacao": "Exportadora com operação de apoio à exportação no BNDES"})
            destino = r["pais_destino_das_exportacoes"]
            if destino not in paises:
                raise SystemExit(f"país sem código em data/curadoria/paises_bndes.csv: {destino!r}")
            if not paises[destino]:
                sem_pais[destino] += 1
            linhas.append({
                "id_operacao": ids.obter("operacoes_exportacao_bndes", f"bndes:{arquivo}:{base_chave}#{vistos[base_chave]}"),
                "numero_operacao": r["numero_da_operacao"], "linha_de_apoio": linha_apoio, "data_contratacao": r["data_da_contratacao"],
                "pais_destino_fonte": destino, "pais_iso3": paises[destino], "id_exportadora": exp, "tipo_mutuario": r.get("mutuario", ""),
                "descricao_projeto": r["descricao_da_operacao"], "modalidade": r.get("modalidade_operacional", ""),
                "valor": numero_br(r.get("valor_da_operacao_em_um", "")), "valor_desembolsado": numero_br(r.get("valor_desembolsado_em_um", "")),
                "moeda": MOEDAS.get(r["moeda_sigla"], "outra"), "tipo_garantia": r.get("tipo_de_garantia", ""), "situacao": r.get("situacao_da_operacao", ""),
                "id_fonte": f,
            })
    return {"instituicoes": list(instituicoes.values()), "fontes": fontes, "fonte_oficial": oficiais, "operacoes_exportacao_bndes": linhas, "sem_pais": sem_pais}


def gravar_resultado(r: dict, ids: RegistroIds, base: Path = BASE) -> None:
    for nome in ("fontes", "fonte_oficial"):
        atual = ler(nome, base)
        novas = [l for l in r[nome] if l["id_fonte"] not in set(atual["id_fonte"])]
        gravar(nome, pd.concat([atual, pd.DataFrame(novas, dtype=str)], ignore_index=True), base)
    atual = ler("instituicoes", base)
    novas = pd.DataFrame(r["instituicoes"], dtype=str)
    gravar("instituicoes", pd.concat([atual[~atual["id_instituicao"].isin(novas["id_instituicao"])], novas], ignore_index=True), base)
    gravar("operacoes_exportacao_bndes", pd.DataFrame(r["operacoes_exportacao_bndes"], dtype=str), base)
    ids.salvar()


def run() -> None:
    ids = RegistroIds()
    r = montar(ids)
    gravar_resultado(r, ids)
    d = pd.DataFrame(r["operacoes_exportacao_bndes"])
    resumo = d.groupby("linha_de_apoio").agg(linhas=("id_operacao", "size"), operacoes=("numero_operacao", "nunique"),
                                             paises=("pais_iso3", lambda s: s[s != ""].nunique()), inicio=("data_contratacao", "min"), fim=("data_contratacao", "max"))
    print(resumo.to_string())
    print(f"exportadoras: {sum(1 for i in r['instituicoes'] if i['tipo_instituicao'] == 'empresa')}; linhas sem país definido: {dict(r['sem_pais'])}")


if __name__ == "__main__":
    run()
