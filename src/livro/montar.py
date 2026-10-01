"""Monta relatorios/livro/livro.json (estrutura do livro) a partir dos textos, resultados, figuras, tabelas e fichas.

Os textos em src/livro/textos/ usam marcadores {{chave.subchave:dN}} preenchidos com resultados.json, e
[[fig:id]], [[tab:id]], [[fichas]], [[referencias]], [[matriz]] para inserir material gerado.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pandas as pd
from PIL import Image

from .comum import BASE, FIG, RAIZ, REPO, SAIDA, TABS, br, resultados
from .matriz import COLS as MCOLS, M as MATRIZ

TXT = Path(__file__).parent / "textos"


def commit() -> str:
    try:
        h = subprocess.check_output(["git", "-C", str(RAIZ), "rev-parse", "--short", "HEAD"], text=True).strip()
        sujo = subprocess.check_output(["git", "-C", str(RAIZ), "status", "--porcelain", "--", "src", "docs", "data/curadoria", "data/manifestos"], text=True).strip()
        return h + (" com alterações locais ainda não versionadas (src/livro, data/curadoria, data/manifestos, docs)" if sujo else "")
    except Exception:
        return "[sem commit]"


def preencher(texto: str, R: dict) -> str:
    def rep(m):
        expr = m.group(1).strip()
        if expr == "REPO":
            return REPO
        if expr == "COMMIT":
            return R.get("_commit", "")
        chave, _, fmt = expr.partition(":")
        partes = chave.split(".")
        v = R
        for p_ in partes:
            if isinstance(v, list):
                v = v[int(p_)]
            else:
                if p_ not in v:
                    raise KeyError(f"marcador sem valor: {expr}")
                v = v[p_]
        if fmt.startswith("d") and isinstance(v, (int, float)):
            return br(float(v), int(fmt[1:]))
        return str(v)
    return re.sub(r"\{\{([^}]+)\}\}", rep, texto)


def ficha_curta(f: dict) -> str:
    partes = [f"Pergunta: {f.get('pergunta','')}", f"Período: {f.get('periodo','')}", f"Unidade: {f.get('unidade','')}",
              f"Fonte primária: {f.get('fonte_primaria','')}", f"Tratamento do autor: {f.get('tratamento','')}"]
    return " · ".join(p for p in partes if not p.endswith(": "))


def tabela_bloco(tid: str, fichas: dict, num: int) -> dict:
    df = pd.read_csv(TABS / f"{tid}.csv", dtype=str).fillna("")
    f = fichas.get(tid, {})
    if tid == "atlas_condenacoes":
        df = df.drop(columns=[c for c in ["Natureza do registro", "Situação processual na data de corte"] if c in df])
        df["Fonte"] = df["Fonte"].str.extract(r"\((FNT-\d+)\)")[0].fillna("FNT-000046")
        f = dict(f); f["notas"] = ("Natureza do registro em todas as linhas: condenação em ação penal originária no STF (procedente ou procedente em parte). "
                                   "Situação na data de corte: último status registrado na base para a pessoa na ação; recursos, trânsito em julgado e revisões posteriores não foram lidos (D-065). ") + f.get("notas", "")
    for c in df.columns:  # números com vírgula decimal
        df[c] = df[c].map(lambda x: x.replace(".", ",") if re.fullmatch(r"-?\d+\.\d+", x) else x)
    return dict(t="table", id=tid, num=num, titulo=f.get("titulo", tid), cols=list(df.columns), rows=df.values.tolist(),
                nota=f"Unidade: {f.get('unidade','')}. Período: {f.get('periodo','')}. Universo: {f.get('universo','')}. Fonte: {f.get('fonte','')}. "
                     f"Notas: {f.get('notas','')} Código: {f.get('codigo','')}. Arquivo: relatorios/livro/tabelas/{tid}.csv.")


INST = [("dadosabertos.tse.jus.br", "Tribunal Superior Eleitoral"), ("www.tse.jus.br", "Tribunal Superior Eleitoral"),
        ("dadosabertos.camara.leg.br", "Câmara dos Deputados"), ("legis.senado.leg.br", "Senado Federal"), ("senado.leg.br", "Senado Federal"),
        ("dadosabertos-download.cgu.gov.br", "Controladoria-Geral da União (Portal da Transparência)"),
        ("stf.jus.br", "Supremo Tribunal Federal"), ("certidoes.apps.tcu.gov.br", "Tribunal de Contas da União"),
        ("dadosabertos.bndes.gov.br", "BNDES"), ("concordia.itamaraty.gov.br", "Ministério das Relações Exteriores (Itamaraty)"),
        ("documents.un.org", "Nações Unidas"), ("digitallibrary.un.org", "Nações Unidas"), ("oas.org", "Organização dos Estados Americanos"),
        ("githubusercontent.com", "V-Dem Institute"), ("freedomhouse.org", "Freedom House"), ("doi.org", "Bases acadêmicas"),
        ("tjmg.jus.br", "Tribunais de outras instâncias"), ("trf4.jus.br", "Tribunais de outras instâncias"), ("stj.jus.br", "Tribunais de outras instâncias"),
        ("datajud.cnj.jus.br", "CNJ (DataJud)")]


def referencias() -> list[dict]:
    f = pd.read_csv(BASE / "fontes.csv")
    f["dom"] = f.url.str.extract(r"https?://([^/]+)")[0].fillna("")
    def inst(d):
        for k, v in INST:
            if k in d:
                return v
        return "Redes partidárias transnacionais (cópias do Internet Archive)"
    f["inst"] = f.dom.map(inst)
    f = f[f.inst != "CNJ (DataJud)"]  # termo de uso: não citar (D-022)
    out = []
    ordem = ["Tribunal Superior Eleitoral", "Câmara dos Deputados", "Senado Federal", "Controladoria-Geral da União (Portal da Transparência)",
             "Supremo Tribunal Federal", "Tribunal de Contas da União", "BNDES", "Ministério das Relações Exteriores (Itamaraty)", "Nações Unidas",
             "Organização dos Estados Americanos", "V-Dem Institute", "Freedom House", "Tribunais de outras instâncias", "Bases acadêmicas",
             "Redes partidárias transnacionais (cópias do Internet Archive)"]
    for ins in ordem:
        g = f[f.inst == ins].sort_values("id_fonte")
        if len(g) == 0:
            continue
        out.append(dict(t="h3", x=f"{ins} ({len(g)})"))
        for r in g.itertuples():
            sha = str(r.sha256)[:12] if isinstance(r.sha256, str) else "—"
            out.append(dict(t="ref", x=f"{r.id_fonte}. {r.titulo}. {r.url}. Acesso em {r.data_acesso}. sha256 {sha}."))
    extra = [
        ("Instituto Brasileiro de Geografia e Estatística (IBGE)", [
            "IPCA, número-índice (dez/1993 = 100), tabela 1737 do SIDRA, variável 2266. https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/<períodos>. Acesso em 2026-09-30. Valores em data/curadoria/ibge_ipca_numero_indice.csv (D-070); conferir por download direto.",
            "Estimativas da população residente por UF, tabela 6579 do SIDRA, variável 9324, anos 2021, 2024 e 2025. https://apisidra.ibge.gov.br/values/t/6579/n3/all/v/9324/p/2021,2024,2025. Acesso em 2026-09-30. Valores em data/curadoria/ibge_populacao_uf.csv (D-070)."]),
        ("Tesouro Nacional", ["Resultado do Tesouro Nacional, dezembro de 2025, série histórica (serie_historica_dez25.xlsx), Tabela 2.1. https://thot-arquivos.tesouro.gov.br/publicacao-anexo/27550. Baixado pelo autor em 2026-09-30; sha256 2a82626c9e8f (data/manifestos/tesouro.csv)."]),
        ("Ministério do Desenvolvimento, Indústria, Comércio e Serviços (ComexStat)", ["API pública do ComexStat, exportações e importações por país e mês. https://api-comexstat.mdic.gov.br/general. Acesso em 2026-09-28 (data/manifestos/comexstat.csv). [REFERÊNCIA A CONFIRMAR: registrar a fonte em data/base/fontes.csv]."]),
        ("Câmara dos Deputados (orientações de bancada)", ["Arquivos anuais de votações e orientações de bancada do Plenário (data/manifestos/camara_orientacoes.csv), acesso em 2026-09-28. [REFERÊNCIA A CONFIRMAR: registrar a fonte em data/base/fontes.csv]."]),
        ("Legislação (Presidência da República, textos oficiais lidos em 2026-09-30 e 2026-10-01)", [
            "Lei 12.846, de 1º de agosto de 2013. https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/lei/l12846.htm",
            "Emenda Constitucional 86, de 17 de março de 2015. https://www.planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc86.htm",
            "Lei 13.165, de 29 de setembro de 2015 (art. 15 revoga o art. 81 da Lei 9.504/1997). https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13165.htm",
            "Emenda Constitucional 97, de 4 de outubro de 2017. https://www.planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc97.htm",
            "Lei 13.487, de 6 de outubro de 2017. https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2017/lei/l13487.htm",
            "Emenda Constitucional 100, de 26 de junho de 2019. https://www.planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc100.htm",
            "Emenda Constitucional 105, de 12 de dezembro de 2019. https://www.planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc105.htm",
            "Lei 13.878, de 3 de outubro de 2019 (art. 23, § 2º-A, da Lei 9.504/1997: recursos próprios até 10% do limite de gastos). https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2019/lei/L13878.htm. Lida em 2026-10-01."]),
        ("Jurisprudência (Supremo Tribunal Federal)", [
            "ADI 4650, doações de pessoas jurídicas a campanhas eleitorais, 2015. [REFERÊNCIA A CONFIRMAR: data do julgamento e acórdão; a página do STF não pôde ser lida pela ferramenta de leitura]",
            "AP 937, questão de ordem, restrição do foro por prerrogativa de função, maio de 2018 (data de corte de D-068). [REFERÊNCIA A CONFIRMAR: acórdão]",
            "ADPF 850, 851, 854 e 1014, emendas de relator, dezembro de 2022. [REFERÊNCIA A CONFIRMAR: data e acórdão]"]),
        ("Banco Central do Brasil e IPEA", ["Não utilizados nesta edição."]),
        ("Repositório do projeto", [f"Pesquisa documental: poder institucional no Brasil, 2003 até hoje. {REPO}. Edição gerada a partir do commit indicado na Apresentação; scripts do livro em src/livro/; dicionário de dados em docs/esquema_dados.md; decisões em docs/decisoes_metodologicas.md; limitações em docs/limitacoes.md."]),
    ]
    for ins, itens in extra:
        out.append(dict(t="h3", x=ins))
        out += [dict(t="ref", x=i) for i in itens]
    out.append(dict(t="p", x="A fonte FNT-000013 (DataJud, CNJ) foi usada só para descobrir o universo de processos do STJ e, pelo termo de uso aceito (D-022), não é citada."))
    return out


def main() -> None:
    R = resultados(); R["_commit"] = commit()
    fichas = json.loads((SAIDA / "fichas.json").read_text(encoding="utf-8"))
    blocos, nfig, ntab, usadas = [], 0, 0, []
    for arq in sorted(TXT.glob("*.md")):
        txt = preencher(arq.read_text(encoding="utf-8"), R)
        caixa = None
        for linha in txt.split("\n"):
            s = linha.rstrip()
            if caixa is not None:
                if s == ":::":
                    blocos.append(caixa); caixa = None
                elif s.startswith("- "):
                    caixa["itens"].append(s[2:])
                elif s:
                    caixa["itens"].append(s)
                continue
            if not s:
                continue
            if s.startswith("::: "):
                caixa = dict(t="box", tipo=s[4:].strip(), itens=[]); continue
            m = re.fullmatch(r"\[\[(fig|tab):([\w]+)\]\]", s)
            if m:
                k, i = m.groups()
                if k == "fig":
                    nfig += 1; f = fichas[i]; usadas.append((nfig, i))
                    im = Image.open(RAIZ / f["arquivo"])
                    blocos.append(dict(t="fig", id=i, num=nfig, path=str(RAIZ / f["arquivo"]), ar=im.height / im.width,
                                       titulo=f["titulo"], ficha=ficha_curta(f), codigo=f.get("codigo", "")))
                else:
                    ntab += 1; blocos.append(tabela_bloco(i, fichas, ntab))
                continue
            if s == "[[fichas]]":
                for n, i in usadas:
                    f = fichas[i]
                    blocos.append(dict(t="ficha", num=n, id=i, campos=[(k, f.get(k, "")) for k in
                        ["titulo", "pergunta", "periodo", "unidade", "universo", "fonte_primaria", "fonte_secundaria", "tratamento", "derivado", "limitacoes", "leitura", "codigo", "arquivo"]]))
                continue
            if s in ("[[paisagem]]", "[[retrato]]"):
                blocos.append(dict(t="orient", o="L" if s == "[[paisagem]]" else "P")); continue
            if s == "[[referencias]]":
                blocos += referencias(); continue
            if s == "[[matriz]]":
                ntab += 1
                blocos.append(dict(t="table", id="matriz", num=ntab, titulo="Matriz de transformação: análises do catálogo anterior e capítulos deste livro",
                                   cols=MCOLS, rows=[list(r) for r in MATRIZ], nota="Arquivo: src/livro/matriz.py. Capítulos numerados como neste livro; \"Atlas\" refere-se à Parte VIII."))
                continue
            if s.startswith("# "):
                blocos.append(dict(t="part", x=s[2:])); continue
            if s.startswith("## "):
                blocos.append(dict(t="h1", x=s[3:])); continue
            if s.startswith("### "):
                blocos.append(dict(t="h2", x=s[4:])); continue
            if s.startswith("- "):
                blocos.append(dict(t="bul", x=s[2:])); continue
            blocos.append(dict(t="p", x=s))
    pend = re.findall(r"\{\{[^}]+\}\}", json.dumps(blocos, ensure_ascii=False))
    assert not pend, pend
    meta = dict(commit=R["_commit"], repo=REPO, nfig=nfig, ntab=ntab)
    (SAIDA / "livro.json").write_text(json.dumps(dict(meta=meta, blocos=blocos), ensure_ascii=False), encoding="utf-8")
    print(meta, len(blocos))


if __name__ == "__main__":
    main()
