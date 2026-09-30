"""Verificação de simetria por partido para um padrão de status (D-063): a mesma busca, com o mesmo critério, em todos os partidos.

Cada status adverso de ator com filiação recebe uma verificação. Para cada partido do universo do ano do status:
- `encontrado`: há status do mesmo padrão de parlamentar daquele partido (partido = filiação vigente na data do status);
- `sem_evidencia`: não há, e a busca de zero resultados fica registrada em `buscas`.
Todos os status do padrão, de qualquer ator com filiação, entram na contagem por partido.

Uso interno: src.normalizacao.etica (e as demais fontes do eixo 1).
"""

from collections import defaultdict
from pathlib import Path

from src.base import BASE, RegistroIds, ler
from src.normalizacao.simetria_stf import partido_na_data


def verificar(status: list[dict], padrao: str, chave: str, ids: RegistroIds, data: str, script: str, base: Path = BASE):
    """`status`: dicts com id_status, id_ator, data. Devolve (buscas, verificacoes_simetria, verificacao_resultado) novos."""
    fil = ler("filiacoes", base)
    filiados = set(fil["id_ator"])
    universo = ler("universo_partidos", base)
    existentes = set(ler("verificacoes_simetria", base)["id_verificacao"])
    por_partido: dict[str, set[str]] = defaultdict(set)
    for r in status:
        for p in partido_na_data(fil, r["id_ator"], r["data"]):
            por_partido[p].add(r["id_status"])
    buscas, vs, vr, busca_de = [], [], [], {}
    for r in status:
        if r["id_ator"] not in filiados:
            continue
        v = ids.obter("verificacoes_simetria", f"{chave}|{r['id_status']}")
        if v in existentes:
            continue
        ano = r["data"][:4]
        vs.append({"id_verificacao": v, "achado_tabela": "status_pessoa_processo", "achado_id": r["id_status"], "padrao_buscado": padrao,
                   "ano_referencia": ano, "data": data, "script": script})
        for g in sorted(universo.loc[universo["ano"] == ano, "id_partido"]):
            linha = {"id_resultado": ids.obter("verificacao_resultado", f"{v}|{g}"), "id_verificacao": v, "grupo_tipo": "partido", "grupo_id": g}
            achados = sorted(por_partido.get(g, ()))
            if achados:
                linha.update(resultado="encontrado", n_casos=str(len(achados)), ids_encontrados=";".join(achados))
            else:
                if g not in busca_de:
                    busca_de[g] = ids.obter("buscas", f"{script}|{data}|{chave}|partido {g}")
                    buscas.append({"id_busca": busca_de[g], "data": data, "fonte_dados": "Base do projeto (status_pessoa_processo)",
                                   "consulta": f"{chave}: status do padrão em parlamentares com filiação ao partido {g}", "parametros_json": "{}",
                                   "n_resultados": "0", "script": script})
                linha.update(resultado="sem_evidencia", n_casos="0", id_busca=busca_de[g])
            vr.append(linha)
    return buscas, vs, vr
