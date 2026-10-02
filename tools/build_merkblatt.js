#!/usr/bin/env node
// build_merkblatt.js — druckt merkblatt/urlaub-abschlussjahr.html je Variante
// (varianten/*.json) mit Chromium (Playwright) als A4-PDF im Landesdesign,
// inklusive der lokal liegenden BaWue-Schriften und PDF-Tagging (Strukturbaum
// für Screenreader).
//
// Varianten: Blöcke <!--[wenn gaertner]--> … <!--[/wenn]--> bleiben nur in der
// genannten Variante stehen (mehrere: <!--[wenn a,b]-->), {{SCHLÜSSEL}} werden
// aus der JSON-Datei ersetzt. Dieselbe Logik nutzt tools/build_newsletter.py.
//
// Aufruf:  node tools/build_merkblatt.js [variante]
//          (Playwright muss installiert sein, z. B. global:
//           npm i -g playwright && npx playwright install chromium)
// Ausgabe: merkblatt/<merkblatt aus der JSON>.pdf — wird mitversioniert, damit
//          der Newsletter-Build die PDFs ohne Node/Playwright anhängen kann.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const QUELLE = path.join(ROOT, 'merkblatt', 'urlaub-abschlussjahr.html');
const BLOCK = /<!--\[wenn ([\w,\- ]+)\]-->([\s\S]*?)<!--\[\/wenn\]-->/g;

function varianteAnwenden(html, v) {
  html = html.replace(BLOCK, (_, namen, inhalt) => namen.split(',').map(s => s.trim()).includes(v.ausgabe) ? inhalt : '');
  return html.replace(/\{\{([A-Z0-9_]+)\}\}/g, (m, k) => { const w = v[k] ?? v[k.toLowerCase()]; return typeof w === 'string' ? w : m; });
}

(async () => {
  const auswahl = process.argv[2];
  const varianten = fs.readdirSync(path.join(ROOT, 'varianten')).filter(f => f.endsWith('.json')).sort()
    .map(f => JSON.parse(fs.readFileSync(path.join(ROOT, 'varianten', f), 'utf8')))
    .filter(v => !auswahl || v.ausgabe === auswahl);
  if (!varianten.length) { console.error('keine Variante gefunden'); process.exit(1); }
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const v of varianten) {
    if (!v.merkblatt) { console.log(`${v.ausgabe}: kein Merkblatt vorgesehen`); continue; }
    const html = varianteAnwenden(fs.readFileSync(QUELLE, 'utf8'), v);
    const tmp = path.join(ROOT, 'merkblatt', `.build-${v.ausgabe}.html`);
    fs.writeFileSync(tmp, html);
    try {
      await page.goto('file://' + tmp, { waitUntil: 'load' });
      await page.evaluate(() => document.fonts.ready);
      const fonts = await page.evaluate(() => Array.from(document.fonts).filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight));
      const out = path.join(ROOT, 'merkblatt', v.merkblatt);
      await page.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true, tagged: true, displayHeaderFooter: false });
      const pdf = fs.readFileSync(out);
      const seiten = (pdf.toString('latin1').match(/\/Type\s*\/Page(?![s])/g) || []).length;
      console.log(`OK  -> merkblatt/${v.merkblatt}  (${Math.round(pdf.length / 1024)} KB, ${seiten} Seite(n))  Variante ${v.ausgabe}`);
      console.log('    Schriften geladen:', fonts.length ? fonts.join(', ') : 'keine (Fallback)');
    } finally {
      fs.unlinkSync(tmp);
    }
  }
  await browser.close();
})();
