// Gera relatorios/livro/livro.docx a partir de relatorios/livro/livro.json (npm: docx).
// Uso, na raiz do repositório: node src/livro/docx/montar_docx.js
const fs = require('fs');
const path = require('path');
const D = require('docx');
const {Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  AlignmentType, HeadingLevel, PageBreak, Footer, PageNumber, LevelFormat, VerticalAlign, PageOrientation} = D;
const RAIZ = path.resolve(__dirname, '../../..');
const L = JSON.parse(fs.readFileSync(path.join(RAIZ, 'relatorios/livro/livro.json'), 'utf8'));
const NAVY = '0D366B', BLUE = '2A78D6', INK = '1A1A1A', MUTE = '6B6A66', FONT = 'Calibri';
const PW = 11906, PH = 16838, MAR = 1134;
const run = (t, o = {}) => new TextRun({text: t, bold: o.bold, italics: o.italics, size: o.size || 21, color: o.color || INK, font: FONT});
function runs(s, o = {}) {
  const out = []; String(s).split('**').forEach((p, i) => { if (p) out.push(run(p, {...o, bold: (i % 2 === 1) || o.bold})); });
  return out;
}
const P = (s, o = {}) => new Paragraph({children: runs(s, o), spacing: {after: o.after ?? 110, line: o.line ?? 290, before: o.before},
  alignment: o.align, keepNext: o.keepNext, indent: o.indent, shading: o.shade ? {type: ShadingType.CLEAR, fill: o.shade} : undefined, border: o.border});
function larguras(cols, rows, total) {
  const n = cols.length; const len = cols.map((c, j) => Math.max(String(c).length * 0.8, ...rows.slice(0, 80).map(r => Math.min(String(r[j] ?? '').length, 90))));
  const sq = len.map(x => Math.sqrt(Math.max(x, 3))); const s = sq.reduce((a, b) => a + b, 0);
  const mn = Math.min(550, Math.floor(total / n * 0.6)); let w = sq.map(x => Math.max(mn, Math.round(total * x / s))); const d = total - w.reduce((a, b) => a + b, 0); w[w.indexOf(Math.max(...w))] += d; return w;
}
function tabela(b, total) {
  const ncol = b.cols.length; const fs = ncol >= 9 ? 12 : ncol >= 7 ? 13 : 15;
  const w = larguras(b.cols, b.rows, total);
  const bd = {style: BorderStyle.SINGLE, size: 4, color: 'D6D5D0'}; const borders = {top: bd, bottom: bd, left: bd, right: bd};
  const num = v => /^-?[\d.,]+%?$/.test(String(v).trim());
  const cel = (t, j, head, zebra) => new TableCell({width: {size: w[j], type: WidthType.DXA}, borders, verticalAlign: VerticalAlign.CENTER,
    shading: {type: ShadingType.CLEAR, fill: head ? NAVY : (zebra ? 'F4F6FA' : 'FFFFFF')}, margins: {top: 40, bottom: 40, left: 70, right: 70},
    children: [new Paragraph({alignment: (!head && num(t)) ? AlignmentType.RIGHT : AlignmentType.LEFT, children: [new TextRun({text: String(t), bold: head, size: fs, color: head ? 'FFFFFF' : INK, font: FONT})]})]});
  const rows = [new TableRow({tableHeader: true, cantSplit: true, children: b.cols.map((c, j) => cel(c, j, true, false))})];
  b.rows.forEach((r, k) => rows.push(new TableRow({cantSplit: true, children: r.map((c, j) => cel(c, j, false, k % 2 === 1))})));
  return [P(`Tabela ${b.num}. ${b.titulo}`, {bold: true, size: 19, color: NAVY, after: 60, keepNext: true}),
          new Table({width: {size: total, type: WidthType.DXA}, columnWidths: w, rows}),
          P(b.nota, {size: 15, color: MUTE, after: 220, before: 40})];
}
const CAIXA = {permite: ['O que os dados permitem afirmar', 'E8F4EE', '1BAF7A'], nao_permite: ['O que os dados não permitem afirmar', 'FFF4E0', 'EDA100'], nota: ['Nota metodológica', 'F2F1EE', '8A8983']};
function render(blocos, total) {
  const k = [];
  for (const b of blocos) {
    switch (b.t) {
      case 'part': k.push(new Paragraph({heading: HeadingLevel.HEADING_1, pageBreakBefore: true, spacing: {before: 2400, after: 400}, children: [new TextRun({text: b.x, font: FONT})]})); break;
      case 'h1': k.push(new Paragraph({heading: HeadingLevel.HEADING_2, pageBreakBefore: false, keepNext: true, children: [new TextRun({text: b.x, font: FONT})]})); break;
      case 'h2': k.push(new Paragraph({heading: HeadingLevel.HEADING_3, keepNext: true, children: [new TextRun({text: b.x, font: FONT})]})); break;
      case 'h3': k.push(P(b.x, {bold: true, size: 20, color: NAVY, before: 200, after: 60, keepNext: true})); break;
      case 'p': k.push(P(b.x)); break;
      case 'bul': k.push(new Paragraph({numbering: {reference: 'bul', level: 0}, children: runs(b.x), spacing: {after: 70, line: 280}})); break;
      case 'ref': k.push(P(b.x, {size: 15, after: 30, line: 240, indent: {left: 300, hanging: 300}})); break;
      case 'fig': {
        const W = total > 11000 ? 760 : 600; const H = Math.round(W * b.ar);
        k.push(P(`Figura ${b.num}. ${b.titulo}`, {bold: true, size: 18, color: NAVY, keepNext: true, before: 120, after: 40}));
        k.push(new Paragraph({alignment: AlignmentType.CENTER, keepNext: true, spacing: {after: 40},
          children: [new ImageRun({type: 'png', data: fs.readFileSync(b.path), transformation: {width: W, height: H}, altText: {title: b.titulo, description: b.titulo, name: b.id}})]}));
        k.push(P(b.ficha + (b.codigo ? ` · Análise ${b.codigo}. Ficha completa no Atlas.` : ''), {size: 15, color: MUTE, after: 200}));
        break; }
      case 'table': k.push(...tabela(b, total)); break;
      case 'box': {
        const [tit, fill, cor] = CAIXA[b.tipo] || ['Nota', 'F2F1EE', '8A8983'];
        const brd = {left: {style: BorderStyle.SINGLE, size: 18, color: cor, space: 6}};
        k.push(P(tit, {bold: true, size: 19, shade: fill, border: brd, keepNext: true, after: 40, before: 120, indent: {left: 140}}));
        b.itens.forEach((it, i) => k.push(P((b.tipo === 'nota' ? '' : '• ') + it, {size: 19, shade: fill, border: brd, after: i === b.itens.length - 1 ? 220 : 30, indent: {left: 140}, line: 270})));
        break; }
      case 'ficha': {
        const nomes = {titulo: 'Título', pergunta: 'Pergunta', periodo: 'Período', unidade: 'Unidade', universo: 'Universo', fonte_primaria: 'Fonte primária', fonte_secundaria: 'Fonte secundária',
          tratamento: 'Tratamento do autor', derivado: 'Resultado derivado', limitacoes: 'Limitações', leitura: 'Leitura descritiva', codigo: 'Código da análise', arquivo: 'Arquivo'};
        k.push(P(`Figura ${b.num} (${b.id})`, {bold: true, size: 17, color: NAVY, keepNext: true, before: 120, after: 30}));
        b.campos.forEach(([c, v]) => k.push(P(`**${nomes[c]}:** ${v || '—'}`, {size: 15, after: 10, line: 230})));
        break; }
    }
  }
  return k;
}
// capa e sumário
const capa = [new Paragraph({spacing: {before: 2600}, children: []}),
  P('DINHEIRO, JUSTIÇA E PODER', {bold: true, size: 56, color: NAVY, align: AlignmentType.CENTER, after: 200}),
  P('Transformações das relações entre dinheiro, Estado, partidos, Justiça e política externa no Brasil, 2003–2026', {size: 28, align: AlignmentType.CENTER, after: 600}),
  P('Um estudo baseado em dados públicos auditáveis', {size: 22, color: MUTE, align: AlignmentType.CENTER, after: 120}),
  P(`Segunda edição, outubro de 2026 · repositório ${L.meta.repo}`, {size: 18, color: MUTE, align: AlignmentType.CENTER}),
  P(`Gerada a partir do commit ${L.meta.commit}`, {size: 16, color: MUTE, align: AlignmentType.CENTER})];
const sumario = [new Paragraph({children: [new PageBreak()]}), P('Sumário', {bold: true, size: 36, color: NAVY, after: 200})];
for (const b of L.blocos) {
  if (b.t === 'part') sumario.push(P(b.x, {bold: true, color: NAVY, after: 40, before: 120}));
  if (b.t === 'h1' && /^\d+\./.test(b.x)) sumario.push(P(b.x, {size: 19, after: 10, indent: {left: 360}}));
  if (b.t === 'h1' && /^[A-H]\. /.test(b.x)) sumario.push(P(b.x, {size: 19, after: 10, indent: {left: 360}}));
}
const iA = L.blocos.findIndex(b => b.t === 'part' && b.x.startsWith('Parte VIII'));
const corpo = L.blocos.slice(0, iA), atlas = L.blocos.slice(iA);
// o corpo pode alternar retrato e paisagem com os marcadores [[paisagem]] e [[retrato]]
function segmentos(bl) {
  const seg = [{o: 'P', b: []}];
  for (const b of bl) { if (b.t === 'orient') seg.push({o: b.o, b: []}); else seg[seg.length - 1].b.push(b); }
  return seg.filter((s, i) => i === 0 || s.b.length);
}
const rodape = new Footer({children: [new Paragraph({alignment: AlignmentType.CENTER, children: [run('Dinheiro, Justiça e Poder · ', {size: 15, color: MUTE}), new TextRun({children: [PageNumber.CURRENT], size: 15, color: MUTE, font: FONT})]})]});
const secoesCorpo = segmentos(corpo).map((sg, i) => ({
  properties: {page: {size: sg.o === 'L' ? {width: PW, height: PH, orientation: PageOrientation.LANDSCAPE} : {width: PW, height: PH},
    margin: {top: MAR, bottom: MAR, left: MAR, right: MAR}, ...(i === 0 ? {pageNumbers: {start: 1}} : {})}}, footers: {default: rodape},
  children: i === 0 ? [...sumario, ...render(sg.b, PW - 2 * MAR)] : render(sg.b, sg.o === 'L' ? PH - 2 * MAR : PW - 2 * MAR)}));
const doc = new Document({
  creator: 'Pesquisa poder institucional', title: 'Dinheiro, Justiça e Poder', description: 'Estudo sobre transformações institucionais no Brasil, 2003–2026',
  styles: {default: {document: {run: {font: FONT, size: 21}}}, paragraphStyles: [
    {id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: {size: 44, bold: true, color: NAVY, font: FONT}, paragraph: {spacing: {before: 240, after: 240}, outlineLevel: 0}},
    {id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: {size: 30, bold: true, color: INK, font: FONT}, paragraph: {spacing: {before: 420, after: 140}, outlineLevel: 1}},
    {id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: {size: 23, bold: true, color: BLUE, font: FONT}, paragraph: {spacing: {before: 240, after: 80}, outlineLevel: 2}}]},
  numbering: {config: [{reference: 'bul', levels: [{level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: {paragraph: {indent: {left: 540, hanging: 270}}}}]}]},
  sections: [
    {properties: {page: {size: {width: PW, height: PH}, margin: {top: MAR, bottom: MAR, left: MAR, right: MAR}}}, children: capa},
    ...secoesCorpo,
    {properties: {page: {size: {width: PW, height: PH, orientation: PageOrientation.LANDSCAPE}, margin: {top: MAR, bottom: MAR, left: MAR, right: MAR}}}, footers: {default: rodape},
     children: render(atlas, PH - 2 * MAR)}]
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(path.join(RAIZ, 'relatorios/livro/livro.docx'), b); console.log('ok', b.length); });
