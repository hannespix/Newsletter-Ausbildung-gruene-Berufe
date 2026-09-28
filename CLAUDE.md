# CLAUDE.md — Grundanweisung für den Newsletter (RP Freiburg)

Steuert, **wie** dieser Newsletter gebaut wird (Design + Technik). Den
**Prozess** (Loop, PRs, Ausgaben) regelt `AGENTS.md`. Vor jeder Aufgabe beide
lesen. Ziel: der Newsletter sieht **wie aus einem Guss** mit den Browsertools
des RPF aus — aktuelles Landes-CD Baden-Württemberg (https://design.landbw.de)
— und kommt in jedem gängigen E-Mail-Programm sauber an.

> Antworten und Texte immer auf **Deutsch**.

---

## 0. Wichtigste Regel
Aussehen wird nicht pro Ausgabe neu erfunden. Verbindlich ist `bw-theme.css`
(Single Source of Truth, identisch mit der Vorlage). **Keine Farb- oder
Schriftwerte hart codieren** — in `newsletter.html` stehen ausschließlich
`var(--bw-*)`-Verweise; `tools/build_newsletter.py` setzt die Werte ein, weil
E-Mail-Programme keine CSS-Variablen kennen. Fehlt ein Wert, ergänze ihn im
Theme, nicht im Newsletter.

---

## 1. Projektstruktur
```
newsletter.html              ← die aktuelle Ausgabe (Quelle, nur --bw-* Tokens)
bw-theme.css                 ← Design-System, Single Source of Truth
assets/logo/                 ← RPF-Logo (rpf-logo.png, -negativ.png) — lizenzpflichtig
anhang/                      ← Anhänge der E-Mail (nicht versioniert)
tools/build_newsletter.py    ← Build: Tokens, Logo (Content-ID), .eml/.html/.txt
tools/check_offline.py       ← findet externe Lade-Referenzen (CI-Gate)
dist/                        ← Build-Ausgabe (nicht versioniert)
CLAUDE.md · AGENTS.md · ROADMAP.md · README.md
```

---

## 2. Kernvorgabe: nichts nachladen
Eine E-Mail darf beim Öffnen **nichts aus dem Netz holen** (Zero-Trust, kein
Tracking):
- **Keine externen Bilder, Zählpixel, Web-Fonts, Stylesheets.** Skripte
  funktionieren in E-Mails ohnehin nicht und haben nichts darin zu suchen.
- **Bilder liegen in `assets/`** und werden vom Build eingebettet: als
  Content-ID-Anhang in der `.eml`, als `data:`-URL in der Browser-Vorschau.
- **Links** (`<a href="https://…">`) sind erlaubt — auf Seiten des Landes/RPF
  oder `mailto:`. Keine Kurzlinks, keine Tracking-Parameter.
- **Prüfung:** `python3 tools/check_offline.py` (läuft im CI bei jedem PR).

## 2.1 Technik HTML-E-Mail (verbindlich)
- **Tabellen-Layout** mit `role="presentation"`, Container 600 px, Outlook-
  Geistertabelle (`<!--[if mso]>`), alle Styles **inline**; Farben doppelt
  (`bgcolor` + `background-color`), Bilder mit `width`/`height`-Attributen.
- **Outlook (Word-Engine)** kennt weder `border-radius`, `max-width` noch Media
  Queries. Runder Störer und Button zusätzlich als **VML** (`v:oval`,
  `v:roundrect`); Schriftstapel per `<!--[if mso]>` auf Arial/Georgia gesetzt,
  sonst fällt Outlook auf Times New Roman zurück.
- **Mobil:** Media Queries (`.container`, `.pad`, `.stack`, `.h1`) sind ein
  Bonus für Apple Mail, Gmail & Co. — das Layout muss auch ohne funktionieren.
- **Schriften:** nur der Theme-Stapel (`--bw-font-serif`/`--bw-font-sans`,
  BaWue zuerst, dann Fallbacks). Keine `@font-face`, keine Schriftdateien in
  der Mail (Lizenz, keine Client-Unterstützung).
- **Größe:** HTML der Mail unter 100 KB (Gmail-Clipping). Logo-PNGs schlank.
- **Platzhalter** stehen in eckigen Klammern `[…]`; der Build meldet sie,
  `--streng` bricht ab. Nie mit Platzhaltern versenden.
- **Nur-Text-Alternative** erzeugt der Build aus dem HTML — Struktur so halten,
  dass die Textfassung lesbar bleibt (Überschriften, Absätze, Tabellenzeilen).
- **Betreff** = `<title>`; **Vorschautext** = verborgener Preheader am Anfang.
- **Absender** ist das Funktionspostfach `abteilung3@rpf.bwl.de`; Empfänger nur
  per **Bcc**; Abmeldehinweis und Impressum/Datenschutz im Fuß sind Pflicht.

---

## 3. Design-System (Details in `bw-theme.css`)
- **Hauptfarben:** `--bw-gelb`, `--bw-schwarz` (warm), Weiß. Funktionale
  Grautöne (`--bw-grau-*`) gliedern, ersetzen die Hauptfarben nie.
- **Gelb-Regel:** Flächen-/Hervorhebungsfarbe, **nie Textfarbe auf Weiß**; Text
  auf Gelb ist Schwarz; gelbe Elemente auf Weiß brauchen dunkle Outline
  (Button: 2 px `--bw-schwarz`).
- **Gelb-Budget je Ausgabe:** Titelfläche, Kapitelnummern und -linien,
  Nummern-Badges, **ein** hervorgehobener Tabellenwert, Störer, Button. Mehr
  nicht — hoher Weißanteil.
- **Schriften:** Überschriften `--bw-font-serif`, Text/UI `--bw-font-sans`.
  Überschriften enden mit Punkt (Landes-CD: „Der Punkt“).
- **Flächen:** Kopf (weiß) · Titelfläche (gelb) · Inhalt (weiß) · Einladung
  (schwarz) · Fuß (schwarz). Keine weiteren Vollflächen, keine Verläufe,
  keine Schatten, keine schiefen Teilungen. Halbierte Karten statt 75/25.

## 3.1 Bausteine (in dieser Reihenfolge, nicht neu erfinden)
Kopf mit Logo links · gelbe Titelfläche (Eyebrow, Serif-Titel, Unterzeile) ·
Anrede · Inhaltsübersicht (Karte mit gelben Nummern) · **Kapitelkopf** (gelbes
Quadrat mit Serif-Nummer, Serif-Titel, 2 px gelbe Linie — wie im Leitfaden) ·
Fließtext 16/25 px · **Tabelle** (schwarzer Kopf, Zebra `--bw-grau-50`, ein
gelber Wert) · **✓-Liste** (gelber Kreis, in Outlook Quadrat) · **Hinweis**
(`--bw-grau-50`, 4 px schwarzer Balken links) · **Karten halbiert** (1 px
`--bw-linie`) · **schwarze Fläche** mit gelbem Eyebrow, Störer rund, gelbem
Button · Schluss/Gruß · **Kontaktkasten** · **Fuß** schwarz mit Negativ-Logo,
Impressum · Datenschutz · Barrierefreiheit · Abmelden.

## 3.2 Zahlen, Termine, Texte
- Zahlen in **de-DE** (Tausenderpunkt, Dezimalkomma), geschützte Leerzeichen
  zwischen Zahl und Einheit (`20&#160;Arbeitstage`, `30.&#160;Juni`).
- Texte: aktive Verben, Sentence-Case, keine Füllwörter; Anrede „Sehr geehrte
  Ausbilderinnen und Ausbilder, sehr geehrte Damen und Herren“.
- **Rechtsaussagen** (Urlaub, Vergütung, Fristen) kommen vom Fachbereich und
  werden im Wortlaut übernommen — umstrukturieren ja (Tabelle, Liste), Inhalt
  ändern nein (siehe `AGENTS.md`, Stop-Bedingungen).

---

## 4. CI-Checkliste
**Do:** nur Markenfarben; aufgeräumt; hoher Weißanteil; klare gerade Flächen;
Störer rund/kontrastierend; ausreichender Kontrast; Logo unverändert.
**Don't:** keine Schatten/Verläufe/Konturlinien als Deko; keine freie
Farbigkeit; nicht überladen; Gelb nie als Text auf Weiß; Logo nicht
einfärben/verzerren/abschatten; keine Emojis.

---

## 5. Barrierefreiheit (Pflicht)
`lang="de"` auf `<html>` und dem Artikel-Container; Layout-Tabellen mit
`role="presentation"`, Datentabellen mit `<th scope="col">`; sinnvolle
Überschriftenhierarchie (`h1` Titel, `h2` Kapitel, `h3` Unterpunkte);
`alt`-Text an jedem Bild (Logo: „Baden-Württemberg – Regierungspräsidium
Freiburg“); Kontrast ≥ 4,5:1 (Grau `--bw-text-leise` nur auf Weiß/Grau-50,
`--bw-grau-300` nur auf Schwarz); Links unterstrichen; Nur-Text-Alternative
in jeder Mail; Schriftgröße ≥ 12 px, Fließtext 16 px.

---

## 6. Logo & Recht
- RPF-Logo aus `assets/logo/` (nicht nachbauen/einfärben/verzerren). Kopf:
  `rpf-logo.png`; schwarzer Fuß: `rpf-logo-negativ.png`. Fehlt das Logo, setzt
  der Build eine reine Wortmarke ein.
- Logo und Schriften sind geschützt (`assets/logo/LIZENZ.md`). **Repository
  privat halten.** Schriftdateien liegen nicht im Repo und gehören nicht in die
  Mail.
- Keine Empfängerdaten, keine Verteiler, keine personenbezogenen Echtdaten
  ins Repo. Kontaktangaben nur dienstlich (Funktionspostfach, Durchwahl der
  Ausbildungsberatung wie im Leitfaden).

---

## 7. Arbeitsweise
1. Erst prüfen, ob die vorhandenen Bausteine (3.1) reichen.
2. `python3 tools/build_newsletter.py` laufen lassen, `dist/newsletter.html`
   im Browser (breit und schmal) prüfen, Textfassung lesen.
3. `python3 tools/check_offline.py` grün; CI-Checkliste (4) und
   Barrierefreiheit (5) vor jedem Commit durchgehen.
4. Vor dem Versand: Platzhalter weg, Anhänge da, Testmail in Outlook und an
   eine externe Adresse.
5. Prozess (Branch/PR/Ausgaben): `AGENTS.md`.
