"""Parte V, Partidos e coalizões: dispersão, filiação, alinhamento, dinheiro por partido e Conselhos de Ética."""
from __future__ import annotations

import zipfile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from .comum import (C, F_CAMARA, F_ETICA, F_IDEOL, F_ORIENT, F_TSE_CAND, F_TSE_PART, FILIACOES, NOME_ATOR, RAIZ,
                    SIGLA, SUCESSORA, TAB, br, fig, gravar_resultados, ler, nogridx, nogridy, partido_na_data, salvar, tabela)

LEGS = [(52, 2003), (53, 2007), (54, 2011), (55, 2015), (56, 2019), (57, 2023)]


def eleitos_tse(ano: int) -> pd.Series:
    """Deputados federais eleitos por partido no arquivo de candidatos do TSE (verificação de D-073)."""
    z = zipfile.ZipFile(RAIZ / f"data/raw/tse/2026-09-25/consulta_cand_{ano}.zip")
    d = pd.concat([pd.read_csv(z.open(n), sep=";", encoding="latin1", dtype=str,
                               usecols=lambda c: c in ("DS_CARGO", "DS_SIT_TOT_TURNO", "SG_PARTIDO", "SG_UF", "NR_CANDIDATO"))
                   for n in z.namelist() if n.endswith(".csv")])
    d = d[d.DS_CARGO.str.upper() == "DEPUTADO FEDERAL"]
    el = d[d.DS_SIT_TOT_TURNO.str.upper().isin(["ELEITO", "ELEITO POR QP", "ELEITO POR MÉDIA", "MÉDIA"])].drop_duplicates(["SG_UF", "NR_CANDIDATO"])  # SQ_CANDIDATO não é único nos anos antigos
    return el.SG_PARTIDO.value_counts()


def nep(cont: pd.Series) -> float:
    sh = cont / cont.sum()
    return float(1 / (sh ** 2).sum())


def main() -> None:
    R = {}
    cg = ler("cargos")
    dep = cg[cg.cargo.str.startswith("Deputado federal (titular)")].copy()
    dep["leg"] = dep.cargo.str.extract(r"legislatura (\d+)")[0].astype(int)
    rows = []
    for leg, y in LEGS:
        ids = dep[dep.leg == leg].id_ator.unique()
        for rot, d in (("inicio", f"{y}-02-02"), ("fim", f"{y+3}-12-31" if y < 2023 else "2026-09-01")):
            s = pd.Series(ids).map(partido_na_data(d)).map(SIGLA).dropna().value_counts()
            rows.append(dict(legislatura=leg, momento=rot, data=d, deputados_com_partido=int(s.sum()), partidos=int(len(s)),
                             nep=round(nep(s), 2), maior=s.index[0], maior_pct=round(float(s.iloc[0] / s.sum() * 100), 1)))
        try:
            t = eleitos_tse(y - 1)
            rows.append(dict(legislatura=leg, momento="tse_eleitos", data=f"{y-1}-10", deputados_com_partido=int(t.sum()), partidos=int(len(t)),
                             nep=round(nep(t), 2), maior=t.index[0], maior_pct=round(float(t.iloc[0] / t.sum() * 100), 1)))
        except FileNotFoundError:
            pass
    N = pd.DataFrame(rows)
    R["p5_nep"] = N.to_dict(orient="records")
    tt = N[N.momento == "tse_eleitos"]
    R["nep_tse"] = {d[:4]: v for d, v in zip(tt.data, tt.nep)}; R["maior_tse"] = {d[:4]: v for d, v in zip(tt.data, tt.maior_pct)}
    ini = N[N.momento == "inicio"].set_index("legislatura"); tse = N[N.momento == "tse_eleitos"].set_index("legislatura")
    f, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 3.0))
    xs = [str(y) for _, y in LEGS]
    a1.plot(xs, ini.nep, color=C["blue"], lw=2, marker="o", label="Base: titulares em 2 de fevereiro")
    if len(tse):
        a1.plot(xs, tse.nep.reindex(ini.index), color=C["orange"], lw=1.4, ls="--", marker="s", ms=4, label="TSE: eleitos por partido")
    for i, v in enumerate(ini.nep):
        a1.text(i, v + 0.5, br(v, 1), ha="center", fontsize=7.5, color=C["blue"])
    a1.set_ylim(0, 20); a1.set_title("Número efetivo de partidos", fontsize=8.5); a1.legend(fontsize=6.5, loc="lower right"); nogridx(a1)
    a2.bar(xs, ini.maior_pct, color=C["violet"], width=0.6)
    for i, (v, s_) in enumerate(zip(ini.maior_pct, ini.maior)):
        a2.text(i, v + 0.4, f"{s_}\n{br(v,1)}%", ha="center", fontsize=6.8)
    a2.set_ylim(0, 25); a2.set_title("Maior bancada (% das cadeiras)", fontsize=8.5); nogridx(a2)
    for a in (a1, a2):
        a.tick_params(labelsize=7.5); a.set_xlabel("início da legislatura", fontsize=7.5)
    salvar(f, "n13", titulo="Número efetivo de partidos na Câmara e parcela da maior bancada, por legislatura (2003–2023)",
           pergunta="O sistema partidário na Câmara se dispersou ou se concentrou?", periodo="Legislaturas 52 a 57 (início em 2003 a 2023)",
           unidade="número efetivo de partidos (Laakso-Taagepera); % das cadeiras",
           universo="Deputados federais titulares de cada legislatura (base) e eleitos por partido no arquivo de candidatos do TSE (verificação)",
           fonte_primaria=F_CAMARA + "; " + F_TSE_CAND, tratamento="Partido pela filiação na data (D-016); índice de D-073",
           derivado="Número efetivo de partidos; parcela da maior bancada",
           limitacoes="Filiação observada só durante o mandato; a base e o TSE diferem por mudanças de partido entre a eleição e a posse",
           leitura=f"Na base, o número efetivo vai de {br(ini.nep.iloc[0],1)} (2003) a {br(ini.nep.max(),1)} ({ini.nep.idxmax() and xs[list(ini.index).index(ini.nep.idxmax())]}) e {br(ini.nep.iloc[-1],1)} (2023); pelo TSE, de {br(tse.nep.iloc[0],1) if len(tse) else '—'} a {br(tse.nep.max(),1) if len(tse) else '—'} e {br(tse.nep.iloc[-1],1) if len(tse) else '—'}.",
           codigo="P (novo)")
    tabela(N.rename(columns={"legislatura": "Legislatura", "momento": "Momento", "data": "Data", "deputados_com_partido": "Deputados com partido",
                             "partidos": "Partidos", "nep": "Número efetivo", "maior": "Maior bancada", "maior_pct": "Maior bancada (%)"}),
           "t_p_nep", titulo="Número efetivo de partidos na Câmara por legislatura", unidade="índice e %", periodo="2003–2026",
           universo="Deputados titulares (base) e eleitos (TSE)", fonte=F_CAMARA + "; " + F_TSE_CAND, notas="D-073; o TSE usa a sigla da eleição.", codigo="P (novo)")
    # mudanças de filiação, separando fusões (D-072)
    fl = FILIACOES.sort_values(["id_ator", "data_inicio"]).copy()
    fl["ant"] = fl.groupby("id_ator").id_partido.shift()
    tr = fl[fl.ant.notna() & (fl.ant != fl.id_partido)].copy()
    tr["institucional"] = [SUCESSORA.get(a) == b for a, b in zip(tr.ant, tr.id_partido)]
    tr["ano"] = tr.data_inicio.dt.year
    ty = tr.groupby(["ano", "institucional"]).size().unstack(fill_value=0).reindex(range(2003, 2027), fill_value=0)
    ty.columns = ["individual" if not c else "institucional" for c in ty.columns]
    R["p5_trocas_total"] = int(len(tr)); R["p5_trocas_institucionais"] = int(tr.institucional.sum())
    R["p5_trocas_individuais_ano"] = {int(k): int(v) for k, v in ty["individual"].items()}
    R["trocas_top"] = [int(y) for y in ty["individual"].sort_values(ascending=False).head(3).index]
    R["p5_trocas_inst_ano"] = {int(k): int(v) for k, v in ty.get("institucional", pd.Series(dtype=int)).items()}
    npart = fl.groupby("id_ator").id_partido.nunique()
    R["p5_parl_2mais"] = int((npart >= 2).sum()); R["p5_parl_total"] = int(len(npart))
    f, a = fig(3.0)
    a.bar(ty.index, ty["individual"], color=C["blue"], width=0.75, label="Mudança individual")
    if "institucional" in ty:
        a.bar(ty.index, ty["institucional"], bottom=ty["individual"], color=C["gray"], width=0.75, label="Por fusão ou incorporação (D-072)")
    for y in ty["individual"].sort_values(ascending=False).head(4).index:
        a.text(y, ty.loc[y].sum() + 4, str(int(ty.loc[y, "individual"])), ha="center", fontsize=7.5, fontweight="bold", color=C["blue"])
    a.set_ylabel("mudanças de partido"); nogridx(a); a.set_xticks(range(2003, 2027, 3)); a.legend(fontsize=7.5, loc="upper left")
    a.set_title("Mudanças de partido de parlamentares, por ano")
    salvar(f, "c37", titulo="Mudanças de filiação partidária de deputados e senadores, individuais e por fusão, por ano",
           pergunta="Quantos parlamentares mudaram de partido por decisão própria, separando as mudanças causadas por fusão?",
           periodo="2003–2026 (2026 parcial)", unidade="número de mudanças", universo=f"{len(npart)} parlamentares com filiação registrada",
           fonte_primaria=F_CAMARA + "; " + F_TSE_PART, tratamento="Mudanças entre filiações consecutivas; classificação de D-072 pela sucessora registrada no TSE",
           derivado="Contagem anual", limitacoes="Filiação observada só durante o mandato; mudanças fora do mandato não aparecem",
           leitura=f"{len(tr)} mudanças, das quais {int(tr.institucional.sum())} por fusão ou incorporação; maiores anos de mudança individual: {', '.join(str(int(y)) for y in ty['individual'].sort_values(ascending=False).head(3).index)}.",
           codigo="P1")
    tri = tr[~tr.institucional].copy(); tri["o"] = tri.ant.map(SIGLA); tri["d"] = tri.id_partido.map(SIGLA)
    fx = tri.groupby(["o", "d"]).size().sort_values(ascending=False).head(12)
    f, a = fig(3.0)
    labs = [f"{o} → {d}" for o, d in fx.index][::-1]
    a.barh(labs, fx.values[::-1], color=C["violet"], height=0.64)
    for i, v in enumerate(fx.values[::-1]):
        a.text(v + 0.5, i, str(v), va="center", fontsize=8)
    nogridy(a); a.set_xlabel("mudanças individuais, 2003–2026"); a.set_title("Trajetos de mudança individual mais frequentes")
    salvar(f, "c37b", titulo="Trajetos mais frequentes de mudança individual de partido (sem fusões), 2003–2026",
           pergunta="Entre quais partidos ocorrem as mudanças individuais?", periodo="2003–2026", unidade="número de mudanças",
           universo="Mudanças individuais (D-072)", fonte_primaria=F_CAMARA + "; " + F_TSE_PART, tratamento="Sigla do partido na data da mudança",
           derivado="Contagem por par origem–destino", limitacoes="Mesmas da série anual", leitura=f"Trajeto mais frequente: {fx.index[0][0]} → {fx.index[0][1]} ({fx.iloc[0]}).", codigo="P1")
    tabela(pd.DataFrame({"De": [o for o, _ in fx.index], "Para": [d for _, d in fx.index], "Mudanças": fx.values}), "t_p1_trajetos",
           titulo="Trajetos de mudança individual mais frequentes", unidade="número", periodo="2003–2026", universo="Mudanças individuais (D-072)",
           fonte=F_CAMARA + "; " + F_TSE_PART, notas="Fusões e incorporações excluídas.", codigo="P1")
    # fusões: linha do tempo (tabela)
    ins = ler("instituicoes"); pp = ins[(ins.tipo_instituicao == "partido") & ins.id_sucessora.notna()].copy()
    pp["data"] = pp.observacao.str.extract(r"encerrado em (\d{4}-\d{2}-\d{2})")[0]
    pp = pp[pp.data >= "2003-01-01"].sort_values("data")
    tabela(pd.DataFrame({"Data": pp.data, "Partido encerrado": pp.sigla, "Sucessor": pp.id_sucessora.map(SIGLA)}), "t_p_fusoes",
           titulo="Fusões e incorporações de partidos registradas no TSE desde 2003", unidade="datas", periodo="2003–2026",
           universo="Partidos registrados no TSE", fonte=F_TSE_PART, notas="Mudança de nome mantém o partido e não aparece aqui (D-016).", codigo="P (novo)")
    R["p5_fusoes_desde_2003"] = int(len(pp))
    # c38 alinhamento
    g = pd.read_csv(TAB / "governo_oposicao_partidos.csv")
    g["gov"] = g.presidente.map({"Luiz Inácio Lula da Silva": "Lula", "Dilma Rousseff": "Dilma", "Michel Temer": "Temer", "Jair Messias Bolsonaro": "Bolsonaro"})
    g["per"] = g.inicio.str[:4] + ("" if True else "")
    g.loc[(g.gov == "Temer") & (g.inicio == "2016-05-12"), "per"] = "2016T"
    per = list(dict.fromkeys(g.sort_values("inicio").per))
    ps = [s for s in ["PT", "PSB", "PDT", "PCdoB", "PSOL", "MDB", "PSD", "PSDB", "PP", "PL", "PTB", "DEM", "UNIÃO", "REPUBLICANOS", "PODE", "PSL", "NOVO"] if s in set(g.sigla)]
    mx = g.groupby(["sigla", "per"]).concordancia.mean().unstack().reindex(index=ps, columns=per)
    R["_vb"] = 0
    R["p5_vezes_base"] = {s: [int((g[g.sigla == s].grupo == "governo").sum()), int(len(g[g.sigla == s])), int((g[g.sigla == s].grupo == "oposicao").sum())] for s in ["PP", "MDB", "PSD", "PL", "PT", "PSDB", "PTB"] if s in set(g.sigla)}
    for k_, v_ in R["p5_vezes_base"].items():
        R[f"base_{k_}"] = v_
    f, a = fig(4.2)
    cm = LinearSegmentedColormap.from_list("s", ["#f3f7fd", "#2a78d6", "#0b2e66"])
    a.imshow(mx.values, cmap=cm, vmin=0, vmax=1, aspect="auto")
    for i in range(mx.shape[0]):
        for j in range(mx.shape[1]):
            v = mx.values[i, j]
            if pd.notna(v):
                a.text(j, i, f"{int(round(v*100))}", ha="center", va="center", fontsize=6.3, color="white" if v > 0.55 else C["ink"])
    a.set_xticks(range(len(per))); a.set_xticklabels([p.replace("2016T", "2016*") for p in per], rotation=60, fontsize=6.5)
    a.set_yticks(range(len(ps))); a.set_yticklabels(ps, fontsize=7.5); a.grid(False); [s.set_visible(False) for s in a.spines.values()]
    a.set_title("% de votações em que o partido seguiu a orientação do governo")
    salvar(f, "c38", titulo="Concordância de cada partido com a orientação do governo em votações nominais da Câmara, por ano, 2003–2026",
           pergunta="Quais partidos acompanham o governo, em cada período?", periodo="2003–2026 (* 2016 a partir da posse de Michel Temer)",
           unidade="% das votações com orientação do governo em que o partido orientou igual",
           universo="Votações nominais do Plenário da Câmara com orientação do governo e do partido (D-050, D-051)", fonte_primaria=F_ORIENT,
           tratamento="Concordância por partido e ano; partidos que orientaram só em bloco recebem a orientação do bloco (D-051)",
           derivado="Taxa de concordância; grupo (base: 2/3 ou mais; oposição: abaixo de 1/2)",
           limitacoes="Orientação de liderança, não voto de cada deputado; blocos grandes a partir de 2023 juntam partidos de posições diferentes; só a Câmara",
           leitura="PP: grupo de base em {0} de {1} períodos de medição; PT: {2} de {3}.".format(*R["p5_vezes_base"].get("PP", [0, 0, 0])[:2], *R["p5_vezes_base"].get("PT", [0, 0, 0])[:2]),
           codigo="P2")
    t = (mx * 100).round(0).reset_index().rename(columns={"sigla": "Partido"})
    tabela(t, "t_p2_matriz", titulo="Concordância com a orientação do governo por partido e ano", unidade="%", periodo="2003–2026",
           universo="Votações nominais da Câmara", fonte=F_ORIENT, notas="D-050, D-051.", codigo="P2")
    # cadeiras por grupo no início de cada ano
    rows = []
    for (presid, inicio), gg in g.groupby(["presidente", "inicio"]):
        pa = partido_na_data(pd.Timestamp(inicio) + pd.Timedelta(days=40))
        deps = dep[(pd.to_datetime(dep.data_inicio, errors="coerce") <= pd.Timestamp(inicio) + pd.Timedelta(days=40)) &
                   (pd.to_datetime(dep.data_fim, errors="coerce").fillna(pd.Timestamp("2027-02-01")) >= pd.Timestamp(inicio) + pd.Timedelta(days=40))].id_ator.unique()
        cont = pd.Series(deps).map(pa).value_counts()
        grp = gg.set_index("id_partido").grupo
        s = cont.groupby(lambda p: grp.get(p, "sem_classificacao")).sum()
        rows.append(dict(inicio=inicio, **{k: int(s.get(k, 0)) for k in ["governo", "oposicao", "nenhum", "sem_classificacao"]}))
    Gp = pd.DataFrame(rows).sort_values("inicio")
    tot = Gp[["governo", "oposicao", "nenhum", "sem_classificacao"]].sum(axis=1)
    R["p5_pct_cadeiras_base"] = {r.inicio[:4] + ("T" if r.inicio == "2016-05-12" else ""): round(float(r.governo / t_ * 100), 0) for r, t_ in zip(Gp.itertuples(), tot)}
    f, a = fig(3.0)
    xs = [i[:4] + ("*" if i == "2016-05-12" else "") for i in Gp.inicio]
    bot = np.zeros(len(Gp))
    for k, lab, c in [("governo", "Alinhados ao governo", C["blue"]), ("nenhum", "Entre os limiares", C["gray"]), ("oposicao", "Oposição", C["orange"]), ("sem_classificacao", "Sem classificação", "#e7e6e2")]:
        v = Gp[k].values / tot.values * 100
        a.bar(xs, v, bottom=bot, color=c, label=lab, width=0.75, edgecolor="white", linewidth=0.5); bot += v
    a.set_ylim(0, 100); a.set_ylabel("% dos deputados em exercício"); nogridx(a); a.tick_params(axis="x", labelsize=6.3, rotation=60)
    a.legend(ncol=4, fontsize=6.8, loc="upper center", bbox_to_anchor=(0.5, -0.22)); a.set_title("Cadeiras da Câmara por alinhamento do partido ao governo")
    salvar(f, "n15", titulo="Parcela das cadeiras da Câmara em partidos alinhados, de oposição e intermediários, por ano, 2003–2026",
           pergunta="Que parcela da Câmara pertence a partidos que votam com o governo?", periodo="2003–2026",
           unidade="% dos deputados titulares em exercício cerca de 40 dias após o início do período", universo="Deputados titulares em exercício",
           fonte_primaria=F_ORIENT + "; " + F_CAMARA, tratamento="Grupo do partido no período (D-050, D-051) aplicado à bancada na data",
           derivado="Parcela das cadeiras por grupo", limitacoes="Alinhamento medido em votações nominais; bancada em uma data do ano",
           leitura="Os partidos classificados como alinhados ao governo reúnem a maior parte das cadeiras na maioria dos anos.", codigo="P2")
    # Conselhos de Ética
    e = pd.read_csv(TAB / "etica_desfechos.csv")
    n = len(e); vc = e.status_final.value_counts()
    R["p5_etica"] = dict(vinculos=n, com_desfecho=int(vc.sum()), arquivado=int(vc.get("arquivado", 0)), improcedente=int(vc.get("representacao_improcedente", 0)),
                         cassado=int(vc.get("mandato_cassado", 0)), sancao=int(vc.get("sancao_disciplinar", 0)), cd=int((e.casa == "CD").sum()), sf=int((e.casa == "SF").sum()),
                         parlamentares=int(e.id_ator.nunique()), processos=int(e.processo.nunique()))
    nd = R["p5_etica"]["com_desfecho"]
    f, a = fig(2.7)
    vals = [n, nd, vc.get("arquivado", 0) + vc.get("representacao_improcedente", 0), vc.get("sancao_disciplinar", 0) + vc.get("mandato_cassado", 0), vc.get("mandato_cassado", 0)]
    labs = ["Vínculos representação × parlamentar", "Com desfecho registrado", "Arquivados ou improcedentes", "Sanção disciplinar ou cassação", "Mandato cassado"]
    cl = [C["blue"], C["blue"], C["gray"], C["orange"], C["red"]]
    yy = np.arange(5)[::-1]
    a.barh(yy, vals, color=cl, height=0.62)
    for y_, v, i in zip(yy, vals, range(5)):
        a.text(v + 6, y_, f"{v}" if i < 2 else f"{v} ({br(v/nd*100,1)}% dos com desfecho)", va="center", fontsize=8.5, fontweight="bold")
    a.set_yticks(yy); a.set_yticklabels(labs); a.set_xlim(0, n * 1.6); nogridy(a); a.set_title("Desfechos nos Conselhos de Ética")
    salvar(f, "c39", titulo="Representações por quebra de decoro e seus desfechos, Câmara e Senado, 2005–2026",
           pergunta="O que acontece com as representações por quebra de decoro?", periodo="2005–2026", unidade="vínculos representação × parlamentar e %",
           universo=f"{n} vínculos em {R['p5_etica']['processos']} processos, {R['p5_etica']['parlamentares']} parlamentares (D-063)",
           fonte_primaria=F_ETICA, tratamento="Ligação por nome parlamentar na ementa, subsequência e curadoria (D-063); desfecho dos campos estruturados",
           derivado="Contagem e parcela por desfecho", limitacoes=f"{n - nd} vínculos sem desfecho nos campos estruturados (não é o mesmo que \"em andamento\"); sanção aprovada no Conselho pode ter sido modificada no Plenário",
           leitura=f"Dos {nd} vínculos com desfecho, {vals[2]} foram arquivados ou julgados improcedentes, {vals[3]} tiveram sanção ou cassação e {vals[4]} terminaram em cassação.",
           codigo="P3")
    e["ap"] = pd.to_datetime(e.apresentacao, errors="coerce"); e["fi"] = pd.to_datetime(e.data_final, errors="coerce"); e["dias"] = (e.fi - e.ap).dt.days
    d = e[e.dias.notna() & (e.dias >= 0)]
    med = d.groupby("status_final").dias.median()
    R["p5_etica_mediana_dias"] = {k: int(v) for k, v in med.items()}; R["p5_etica_max_dias"] = int(d.dias.max())
    order = ["representacao_improcedente", "arquivado", "sancao_disciplinar", "mandato_cassado"]
    nm = {"representacao_improcedente": "Improcedente", "arquivado": "Arquivado", "sancao_disciplinar": "Sanção disciplinar", "mandato_cassado": "Mandato cassado"}
    f, a = fig(2.6)
    data = [d[d.status_final == k].dias.values for k in order]
    bp = a.boxplot(data, vert=False, tick_labels=[f"{nm[k]} (n={len(x)})" for k, x in zip(order, data)], patch_artist=True, widths=0.5,
                   flierprops=dict(marker="o", ms=3, mfc=C["gray"], mec="none"), medianprops=dict(color="white", lw=2))
    for p_, c in zip(bp["boxes"], [C["gray"], C["gray"], C["orange"], C["red"]]):
        p_.set_facecolor(c); p_.set_edgecolor(c)
    a.set_xlim(-30, 1750)
    for i, k in enumerate(order):
        a.text(1740, i + 1, f"mediana {int(med[k])} dias", ha="right", va="center", fontsize=7.5)
    a.invert_yaxis(); a.set_xlabel("dias entre a apresentação e o desfecho (eixo cortado em 1.750)"); nogridy(a); a.set_title("Tempo até o desfecho")
    salvar(f, "c40", titulo="Dias entre a apresentação da representação e o desfecho, por tipo de desfecho",
           pergunta="Quanto tempo leva cada tipo de desfecho?", periodo="2005–2026", unidade="dias", universo="Vínculos com datas de apresentação e desfecho",
           fonte_primaria=F_ETICA, tratamento="Diferença de datas", derivado="Mediana e distribuição",
           limitacoes=f"Alguns arquivamentos passam de 1.750 dias (máximo: {int(d.dias.max())}) e ficam fora do eixo",
           leitura=f"Medianas: cassação {int(med['mandato_cassado'])} dias; arquivamento {int(med['arquivado'])} dias.", codigo="P4")
    ey = e.groupby([e.ap.dt.year, "casa"]).size().unstack(fill_value=0).reindex(range(2005, 2027), fill_value=0)
    R["p5_etica_ano"] = {int(k): int(v) for k, v in ey.sum(axis=1).items()}
    R["etica_ano_max"] = int(ey.sum(axis=1).idxmax())
    f, a = fig(2.9)
    a.bar(ey.index, ey.get("CD", 0), color=C["blue"], label="Câmara", width=0.75); a.bar(ey.index, ey.get("SF", 0), bottom=ey.get("CD", 0), color=C["orange"], label="Senado", width=0.75)
    a.legend(ncol=2, loc="upper right"); a.set_ylabel("vínculos (ano da apresentação)"); nogridx(a); a.set_xticks(range(2005, 2027, 3)); a.set_title("Representações por ano")
    salvar(f, "c41", titulo="Vínculos representação × parlamentar por ano de apresentação, Câmara e Senado", pergunta="Em que anos o instrumento foi mais usado?",
           periodo="2005–2026 (2026 parcial)", unidade="número de vínculos", universo="D-063", fonte_primaria=F_ETICA, tratamento="Ano da apresentação",
           derivado="Contagem anual", limitacoes="Uma representação pode atingir vários parlamentares", leitura=f"Ano com mais vínculos: {int(ey.sum(axis=1).idxmax())} ({int(ey.sum(axis=1).max())}).", codigo="P5")
    # c42 por faixa ideológica com e sem 52ª
    t = pd.read_csv(TAB / "etica_taxas.csv")
    ordf = ["extrema_esquerda", "esquerda", "centro_esquerda", "centro", "centro_direita", "direita", "extrema_direita"]
    nmf = ["Extrema esquerda", "Esquerda", "Centro-esquerda", "Centro", "Centro-direita", "Direita", "Extrema direita"]
    f, a = fig(3.0)
    yy = np.arange(7)[::-1]
    for k, (rec, c, off, lab) in enumerate([("2003-2026", C["blue"], 0.18, "2003–2026"), ("2007-2026 (sem a 52ª legislatura)", C["orange"], -0.18, "Sem a 52ª legislatura (2003–2007)")]):
        tt = t[(t.medida == "representado") & (t.recorte == rec) & (t.grupo_tipo == "faixa_ideologica")].set_index("grupo").reindex(ordf)
        a.errorbar(tt.taxa * 100, yy + off, xerr=[(tt.taxa - tt.ic95_inf) * 100, (tt.ic95_sup - tt.taxa) * 100], fmt="o", color=c, ms=4, capsize=2, lw=1, label=lab)
    a.set_yticks(yy); a.set_yticklabels(nmf); a.set_xlabel("% de parlamentares-legislatura com representação (intervalo de 95%)"); nogridy(a); a.legend(fontsize=7, loc="lower right")
    a.set_title("Representações por faixa ideológica do partido")
    corr = pd.read_csv(TAB / "etica_correlacao.csv")
    salvar(f, "c42", titulo="Parcela de parlamentares alvo de representação, por faixa ideológica do partido, com e sem a 52ª legislatura",
           pergunta="A frequência de representações varia com a posição ideológica do partido?", periodo="2003–2026", unidade="% e intervalo de Wilson",
           universo="Pares parlamentar × legislatura (D-049, D-063)", fonte_primaria=F_ETICA + "; " + F_IDEOL,
           tratamento="Faixa pelo escore do partido (survey de 2018, D-062)", derivado="Taxa por faixa; Spearman entre escore e taxa por partido",
           limitacoes="Faixas pequenas (extrema esquerda: 42 unidades) têm intervalos largos; a diferença vem de poucos episódios; o escore é de 2018 para todo o período",
           leitura="Nenhuma correlação entre escore ideológico e taxa tem p abaixo de 0,05; a extrema esquerda tem a maior taxa e o maior intervalo.", codigo="P7")
    tt = t[(t.medida == "representado") & (t.recorte == "2003-2026") & (t.grupo_tipo == "faixa_ideologica")].set_index("grupo").reindex(ordf)
    tabela(pd.DataFrame({"Faixa": nmf, "Parlamentares-legislatura": tt.n_unidades.astype(int).values, "Com representação": tt.com_registro.astype(int).values,
                         "%": (tt.taxa * 100).round(1).values, "IC 95%": [f"{br(a_*100,1)}–{br(b_*100,1)}" for a_, b_ in zip(tt.ic95_inf, tt.ic95_sup)]}),
           "t_p7_faixa", titulo="Representações por faixa ideológica do partido", unidade="unidades e %", periodo="2003–2026", universo="D-063",
           fonte=F_ETICA + "; " + F_IDEOL, notas="Intervalo de Wilson; sem correlação significativa com o escore (D-063).", codigo="P7")
    # Atlas: cassações
    ca = e[e.status_final == "mandato_cassado"].sort_values("data_final")
    tabela(pd.DataFrame({"Casa": ca.casa.map({"CD": "Câmara", "SF": "Senado"}), "Processo": ca.processo,
                         "Parlamentar": [str(NOME_ATOR.get(i, i)).title() for i in ca.id_ator], "Apresentação": ca.apresentacao, "Desfecho": ca.data_final,
                         "Natureza do registro": ca.tipificacao}), "atlas_cassacoes",
           titulo="Mandatos cassados após representação por quebra de decoro", unidade="registros", periodo="2005–2026", universo="D-063",
           fonte=F_ETICA, notas="Decisão do Plenário da Casa; registro formal, sem juízo sobre os fatos.", codigo="P3")
    # reincidência agregada
    rc = e.groupby("id_ator").size()
    R["p5_etica_3mais"] = int((rc >= 3).sum())
    # redes partidárias
    rd = pd.read_csv(TAB / "eixo2_redes_partidarias.csv")
    R["p5_redes_periodos"] = int(len(rd)); R["p5_redes_n"] = int(rd.rede.nunique())
    tabela(rd.rename(columns={"partido": "Partido", "rede": "Rede", "tipo": "Relação", "inicio_observado": "Primeira observação", "fim_observado": "Última observação"}).fillna({"Última observação": "na cópia de 2026"}),
           "t_p_redes", titulo="Partidos brasileiros em redes partidárias transnacionais", unidade="datas de observação", periodo="2003–2026",
           universo="Listas de membros publicadas pelas redes, em cópias do Internet Archive (D-040)", fonte="Páginas de membros das redes no Internet Archive (FNT-000048 a FNT-000068)",
           notas="Datas de observação, não de filiação; ausência de cópia não é ausência de filiação.", codigo="P (novo)")
    gravar_resultados(R)
    print(N.to_string()); print(R["p5_trocas_total"], R["p5_trocas_institucionais"], R["p5_vezes_base"])


if __name__ == "__main__":
    main()
