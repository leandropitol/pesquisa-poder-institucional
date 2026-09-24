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

    linhas += ["### Validador", "", f"- {len(falhas)} falha(s) e {len(avisos)} aviso(s) na última geração."]
    linhas += [f"- Aviso: {a}" for a in avisos[:20]]
    if len(avisos) > 20:
        linhas.append(f"- … e mais {len(avisos) - 20} avisos.")
    linhas += ["", FIM]
    return "\n".join(linhas)


def run() -> None:
    doc = DOC.read_text(encoding="utf-8")
    antes = doc.split(INICIO)[0]
    DOC.write_text(antes + texto() + "\n", encoding="utf-8")
    print(f"atualizado: {DOC.relative_to(RAIZ).as_posix()}")


if __name__ == "__main__":
    run()
