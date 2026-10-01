// Gera relatorios/livro/livro.docx a partir de relatorios/livro/livro.json (npm: docx).
// Diagramação de livro: 17 x 24 cm, margens espelhadas (interna 3 cm, externa 2,5 cm, 2 cm acima e abaixo),
// texto em Cambria 11 pt justificado com recuo de 1,25 cm, partes em página ímpar, elementos pré-textuais.
// O sumário recebe os números de página de relatorios/livro/paginas.json, calculados por src/livro/diagramar.py.
// Uso, na raiz do repositório: python -m src.livro.diagramar (chama este script, o LibreOffice e a paginação).
const fs = require('fs');
const path = require('path');
const D = require('docx');
const {Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  AlignmentType, HeadingLevel, Footer, PageNumber, LevelFormat, VerticalAlign, PageOrientation, SectionType,
  PositionalTab, PositionalTabAlignment, PositionalTabRelativeTo, PositionalTabLeader} = D;
const RAIZ = path.resolve(__dirname, '../../..');
const L = JSON.parse(fs.readFileSync(path.join(RAIZ, 'relatorios/livro/livro.json'), 'utf8'));
const PAG_PATH = path.join(RAIZ, 'relatorios/livro/paginas.json');
const PAG = fs.existsSync(PAG_PATH) ? JSON.parse(fs.readFileSync(PAG_PATH, 'utf8')) : {};
const NAVY = '0D366B', BLUE = '2A78D6', INK = '1A1A1A', MUTE = '6B6A66';
const SERIF = 'Cambria', SANS = 'Calibri';
const cm = x => Math.round(x * 567);
const PW = cm(17), PH = cm(24), MT = cm(2), MB = cm(2), MIN = cm(3), MOUT = cm(2.5);
const TW = PW - MIN - MOUT, TWL = PH - MIN - MOUT;           // largura útil em retrato e em paisagem
const MARG = {top: MT, bottom: MB, left: MIN, right: MOUT, header: cm(1), footer: cm(1)};
const BODY = 22, LINE = 312, RECUO = cm(1.25);

const run = (t, o = {}) => new TextRun({text: t, bold: o.bold, italics: o.italics, size: o.size || BODY, color: o.color || INK, font: o.font || SERIF});
function runs(s, o = {}) {
  const out = []; String(s).split('**').forEach((p, i) => { if (p) out.push(run(p, {...o, bold: (i % 2 === 1) || o.bold})); });
  return out;
}
const P = (s, o = {}) => new Paragraph({children: runs(s, o), spacing: {after: o.after ?? 0, line: o.line ?? LINE, before: o.before},
  alignment: o.align ?? AlignmentType.JUSTIFIED, keepNext: o.keepNext, indent: o.indent, pageBreakBefore: o.pageBreakBefore,
  shading: o.shade ? {type: ShadingType.CLEAR, fill: o.shade} : undefined, border: o.border});

function larguras(cols, rows, total) {
  const n = cols.length; const len = cols.map((c, j) => Math.max(String(c).length * 0.8, ...rows.slice(0, 80).map(r => Math.min(String(r[j] ?? '').length, 90))));
  const sq = len.map(x => Math.sqrt(Math.max(x, 3))); const s = sq.reduce((a, b) => a + b, 0);
  const mn = Math.min(500, Math.floor(total / n * 0.6)); let w = sq.map(x => Math.max(mn, Math.round(total * x / s))); const d = total - w.reduce((a, b) => a + b, 0); w[w.indexOf(Math.max(...w))] += d; return w;
}
function tabela(b, total) {
  const ncol = b.cols.length; const fs_ = ncol >= 9 ? 11 : ncol >= 7 ? 12 : ncol >= 5 ? 13 : 15;
  const w = larguras(b.cols, b.rows, total);
  const bd = {style: BorderStyle.SINGLE, size: 4, color: 'D6D5D0'}; const borders = {top: bd, bottom: bd, left: bd, right: bd};
  const num = v => /^-?[\d.,]+%?$/.test(String(v).trim());
  const cel = (t, j, head, zebra) => new TableCell({width: {size: w[j], type: WidthType.DXA}, borders, verticalAlign: VerticalAlign.CENTER,
    shading: {type: ShadingType.CLEAR, fill: head ? NAVY : (zebra ? 'F4F6FA' : 'FFFFFF')}, margins: {top: 30, bottom: 30, left: 55, right: 55},
    children: [new Paragraph({alignment: (!head && num(t)) ? AlignmentType.RIGHT : AlignmentType.LEFT, spacing: {line: 230},
      children: [new TextRun({text: String(t), bold: head, size: fs_, color: head ? 'FFFFFF' : INK, font: SANS})]})]});
  const rows = [new TableRow({tableHeader: true, cantSplit: true, children: b.cols.map((c, j) => cel(c, j, true, false))})];
  b.rows.forEach((r, k) => rows.push(new TableRow({cantSplit: true, children: r.map((c, j) => cel(c, j, false, k % 2 === 1))})));
  return [P(`Tabela ${b.num}. ${b.titulo}`, {bold: true, size: 18, color: NAVY, after: 60, before: 160, keepNext: true, align: AlignmentType.LEFT, line: 260}),
          new Table({width: {size: total, type: WidthType.DXA}, columnWidths: w, rows}),
          P(b.nota, {size: 15, color: MUTE, after: 220, before: 40, line: 230, align: AlignmentType.LEFT})];
}
const CAIXA = {permite: ['O que os dados permitem afirmar', 'E8F4EE', '1BAF7A'], nao_permite: ['O que os dados não permitem afirmar', 'FFF4E0', 'EDA100'], nota: ['Nota metodológica', 'F2F1EE', '8A8983']};

function render(blocos, total) {
  const k = []; let prev = null;
  for (const b of blocos) {
    switch (b.t) {
      case 'part': k.push(new Paragraph({heading: HeadingLevel.HEADING_1, spacing: {before: cm(4), after: cm(1.2)}, children: [new TextRun({text: b.x, font: SERIF})]})); break;
      case 'h1': k.push(new Paragraph({heading: HeadingLevel.HEADING_2, keepNext: true, children: [new TextRun({text: b.x, font: SERIF})]})); break;
      case 'h2': k.push(new Paragraph({heading: HeadingLevel.HEADING_3, keepNext: true, children: [new TextRun({text: b.x, font: SERIF})]})); break;
      case 'h3': k.push(P(b.x, {bold: true, size: 20, color: NAVY, before: 200, after: 60, keepNext: true, align: AlignmentType.LEFT})); break;
      case 'p': k.push(P(b.x, {indent: prev === 'p' ? {firstLine: RECUO} : undefined})); break;  // primeiro parágrafo após título sem recuo
      case 'bul': k.push(new Paragraph({numbering: {reference: 'bul', level: 0}, children: runs(b.x), alignment: AlignmentType.JUSTIFIED,
        spacing: {before: prev === 'bul' ? 0 : 80, after: 40, line: 290}})); break;
      case 'ref': k.push(P(b.x, {size: 16, after: 40, line: 240, indent: {left: 300, hanging: 300}, align: AlignmentType.LEFT})); break;
      case 'fig': {
        const W = Math.round(total / 1440 * 96); const H = Math.round(W * b.ar);
        k.push(P(`Figura ${b.num}. ${b.titulo}`, {bold: true, size: 17, color: NAVY, keepNext: true, before: 200, after: 60, align: AlignmentType.LEFT, line: 250}));
        k.push(new Paragraph({alignment: AlignmentType.CENTER, keepNext: true, spacing: {after: 40},
          children: [new ImageRun({type: 'png', data: fs.readFileSync(b.path), transformation: {width: W, height: H}, altText: {title: b.titulo, description: b.titulo, name: b.id}})]}));
        k.push(P(b.ficha + (b.codigo ? ` · Análise ${b.codigo}. Ficha completa no Atlas.` : ''), {size: 14, color: MUTE, after: 220, line: 220, align: AlignmentType.LEFT}));
        break; }
      case 'table': k.push(...tabela(b, total)); break;
      case 'box': {
        const [tit, fill, cor] = CAIXA[b.tipo] || ['Nota', 'F2F1EE', '8A8983'];
        const brd = {left: {style: BorderStyle.SINGLE, size: 18, color: cor, space: 6}};
        k.push(P(tit, {bold: true, size: 19, shade: fill, border: brd, keepNext: true, after: 40, before: 200, indent: {left: 140}, align: AlignmentType.LEFT, line: 270}));
        b.itens.forEach((it, i) => k.push(P((b.tipo === 'nota' ? '' : '• ') + it, {size: 19, shade: fill, border: brd, after: i === b.itens.length - 1 ? 220 : 30, indent: {left: 140}, line: 270})));
        break; }
      case 'ficha': {
        const nomes = {titulo: 'Título', pergunta: 'Pergunta', periodo: 'Período', unidade: 'Unidade', universo: 'Universo', fonte_primaria: 'Fonte primária', fonte_secundaria: 'Fonte secundária',
          tratamento: 'Tratamento do autor', derivado: 'Resultado derivado', limitacoes: 'Limitações', leitura: 'Leitura descritiva', codigo: 'Código da análise', arquivo: 'Arquivo'};
        k.push(P(`Figura ${b.num} (${b.id})`, {bold: true, size: 17, color: NAVY, keepNext: true, before: 140, after: 30, align: AlignmentType.LEFT}));
        b.campos.forEach(([c, v]) => k.push(P(`**${nomes[c]}:** ${v || '—'}`, {size: 15, after: 10, line: 230, align: AlignmentType.LEFT})));
        break; }
    }
    prev = b.t;
  }
  return k;
}

// ---------- elementos pré-textuais ----------
const C = AlignmentType.CENTER;
const rosto = [P('DINHEIRO, JUSTIÇA E PODER', {bold: true, size: 40, color: NAVY, align: C, before: cm(6)})];   // falsa folha de rosto
const folha = [
  P('Leandro Marques Pitol', {size: 24, align: C, before: cm(2), after: cm(3)}),
  P('DINHEIRO, JUSTIÇA E PODER', {bold: true, size: 44, color: NAVY, align: C, after: 300, line: 360}),
  P('Transformações das relações entre dinheiro, Estado, partidos, Justiça e política externa no Brasil, 2003–2026', {size: 26, align: C, after: cm(1), line: 340}),
  P('Um estudo baseado em dados públicos auditáveis', {size: 21, italics: true, color: MUTE, align: C, after: cm(6)}),
  P('Segunda edição · 2026', {size: 20, color: MUTE, align: C})];
const creditos = [
  P(`© 2026 Leandro Marques Pitol`, {size: 17, before: cm(9), after: 160, align: AlignmentType.LEFT}),
  P('Primeira edição: setembro de 2026. Segunda edição: outubro de 2026.', {size: 17, after: 160, align: AlignmentType.LEFT}),
  P(`Dados, código, decisões metodológicas e esta edição: ${L.meta.repo}`, {size: 17, after: 160, align: AlignmentType.LEFT}),
  P(`Edição gerada a partir do commit ${L.meta.commit}. Nenhum número do texto foi digitado à mão: todos saem dos scripts do repositório.`, {size: 17, after: 160, align: AlignmentType.LEFT}),
  P('Diagramação gerada por script (src/livro/docx/montar_docx.js). Formato 17 × 24 cm. Texto em Cambria 11 pt.', {size: 17, after: 160, align: AlignmentType.LEFT}),
  P('Recomenda-se revisão jurídica antes da reprodução dos registros nominais do Atlas documental.', {size: 17, align: AlignmentType.LEFT})];

// ---------- sumário com página (paginas.json) ----------
const tab = new PositionalTab({alignment: PositionalTabAlignment.RIGHT, relativeTo: PositionalTabRelativeTo.MARGIN, leader: PositionalTabLeader.DOT});
const entrada = (x, o) => new Paragraph({spacing: {before: o.before ?? 0, after: o.after ?? 30, line: 260}, indent: o.indent, keepNext: o.keepNext,
  children: [run(x, {size: o.size, bold: o.bold, color: o.color}), new TextRun({children: [tab, String(PAG[x] ?? '—')], size: o.size, font: SERIF, color: o.color || INK, bold: o.bold})]});
const sumario = [P('Sumário', {bold: true, size: 36, color: NAVY, after: 300, align: AlignmentType.LEFT})];
for (const b of L.blocos) {
  if (b.t === 'part') sumario.push(entrada(b.x, {bold: true, color: NAVY, before: 160, after: 40, size: 20, keepNext: true}));
  if (b.t === 'h1' && (/^\d+\./.test(b.x) || /^[A-H]\. /.test(b.x))) sumario.push(entrada(b.x, {size: 18, indent: {left: 300, right: 400}}));
}

// ---------- seções: cada parte em página ímpar; [[paisagem]]/[[retrato]] mudam a orientação ----------
const rodape = new Footer({children: [new Paragraph({alignment: C, children: [new TextRun({children: [PageNumber.CURRENT], size: 18, color: MUTE, font: SERIF})]})]});
function secoes(bl) {
  const seg = []; let cur = null;
  for (const b of bl) {
    if (b.t === 'part') { cur = {o: b.x.startsWith('Parte VIII') ? 'L' : 'P', tipo: SectionType.ODD_PAGE, b: [b]}; seg.push(cur); continue; }
    if (b.t === 'orient') { cur = {o: b.o, tipo: SectionType.NEXT_PAGE, b: []}; seg.push(cur); continue; }
    cur.b.push(b);
  }
  return seg.filter(s => s.b.length).map((sg, i) => ({
    properties: {type: sg.tipo, page: {size: sg.o === 'L' ? {width: PW, height: PH, orientation: PageOrientation.LANDSCAPE} : {width: PW, height: PH},
      margin: MARG, ...(i === 0 ? {pageNumbers: {start: 1}} : {})}},
    footers: {default: rodape}, children: render(sg.b, sg.o === 'L' ? TWL : TW)}));
}
const pre = (children, tipo) => ({properties: {type: tipo, page: {size: {width: PW, height: PH}, margin: MARG}}, children});

const doc = new Document({
  creator: 'Leandro Marques Pitol', title: 'Dinheiro, Justiça e Poder', description: 'Estudo sobre transformações institucionais no Brasil, 2003–2026',
  styles: {default: {document: {run: {font: SERIF, size: BODY}}}, paragraphStyles: [
    {id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: {size: 40, bold: true, color: NAVY, font: SERIF}, paragraph: {spacing: {line: 440}, outlineLevel: 0}},
    {id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: {size: 28, bold: true, color: INK, font: SERIF}, paragraph: {spacing: {before: 480, after: 180, line: 320}, outlineLevel: 1}},
    {id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: {size: 23, bold: true, color: BLUE, font: SERIF}, paragraph: {spacing: {before: 300, after: 100, line: 300}, outlineLevel: 2}}]},
  numbering: {config: [{reference: 'bul', levels: [{level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: {paragraph: {indent: {left: 500, hanging: 260}}}}]}]},
  sections: [pre(rosto, SectionType.NEXT_PAGE), pre(folha, SectionType.ODD_PAGE), pre(creditos, SectionType.NEXT_PAGE), pre(sumario, SectionType.ODD_PAGE), ...secoes(L.blocos)]
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(path.join(RAIZ, 'relatorios/livro/livro.docx'), b); console.log('ok', b.length); });
