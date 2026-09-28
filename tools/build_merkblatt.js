#!/usr/bin/env node
// build_merkblatt.js — druckt merkblatt/*.html mit Chromium (Playwright) als
// A4-PDF im Landesdesign, inklusive der lokal liegenden BaWue-Schriften und
// PDF-Tagging (Strukturbaum für Screenreader).
//
// Aufruf:  node tools/build_merkblatt.js            (Playwright muss installiert sein,
//          z. B. global: npm i -g playwright && npx playwright install chromium)
// Ausgabe: merkblatt/<Name>.pdf — wird mitversioniert, damit der Newsletter-Build
//          das PDF ohne Node/Playwright anhängen kann.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const DIR = path.join(ROOT, 'merkblatt');
const BLAETTER = {
  'urlaub-abschlussjahr.html': 'Merkblatt-Urlaub-letztes-Ausbildungsjahr.pdf',
};

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const [quelle, ziel] of Object.entries(BLAETTER)) {
    const src = path.join(DIR, quelle);
    if (!fs.existsSync(src)) { console.error('fehlt:', src); process.exitCode = 1; continue; }
    await page.goto('file://' + src, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    const fonts = await page.evaluate(() => Array.from(document.fonts).filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight));
    const out = path.join(DIR, ziel);
    await page.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true, tagged: true, displayHeaderFooter: false });
    const pdf = fs.readFileSync(out);
    const seiten = (pdf.toString('latin1').match(/\/Type\s*\/Page(?![s])/g) || []).length;
    console.log(`OK  -> merkblatt/${ziel}  (${Math.round(pdf.length / 1024)} KB, ${seiten} Seite(n))`);
    console.log('    Schriften geladen:', fonts.length ? fonts.join(', ') : 'keine (Fallback)');
  }
  await browser.close();
})();
