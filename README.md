# Ausbilder-Info „Grüne Berufe“ — HTML-E-Mail im Landesdesign

E-Mail-Information der **Ausbildungsberatung Grüne Berufe** (Regierungspräsidium
Freiburg, Referat 31) an **alle Ausbildungsbetriebe der Grünen Berufe im
Regierungsbezirk** – Landwirtschaft, Weinbau, Gartenbau, Fischerei und die
weiteren grünen Ausbildungsberufe – als HTML-E-Mail im
Corporate Design des Landes Baden-Württemberg (https://design.landbw.de),
gebaut auf der gemeinsamen Vorlage `Vorlage-Tool-im-Landesdesign`. Inhalte und
Anhänge kommen aus dem Repo `Rechte-und-Pflichten-von-Azubis`.

**Aktuelle Ausgabe:** September 2026 – Start des Ausbildungsjahres (Urlaub im
Abschlussjahr mit Merkblatt, Leitfaden „Rechte und Pflichten“, Save the Date
zum Ausbildertag on tour 2027 im Layout des Flyers) – in **zwei Varianten**:

| Variante | Empfänger | Eigenes | Anhänge |
|----------|-----------|---------|---------|
| `gaertner` | Ausbildungsbetriebe im Gartenbau | Urlaubstabelle mit GaLaBau und Erwerbsgartenbau, Hinweis zur geänderten Eintragungspraxis, Durchwahl der Gartenbau-Beratung | Merkblatt Gartenbau · Leitfaden Gartenbau (`anhang/gaertner/`) |
| `gruene-berufe` | Landwirtschaft, Weinbau, Fischerei und weitere Grüne Berufe | Urlaubstabelle ohne Gartenbau-Tarife (gesetzliches Minimum, tarifgebundene und öffentliche Betriebe), Zentrale als Telefon | Merkblatt Grüne Berufe · Leitfaden Grüne Berufe (`anhang/gruene-berufe/`) |

Eine Vorlage, zwei Ausgaben: `newsletter.html` enthält Blöcke
`<!--[wenn gaertner]--> … <!--[/wenn]-->`, die nur in der genannten Variante
stehen bleiben, und Schlüssel wie `{{EYEBROW}}`, die `varianten/<name>.json`
befüllt. Eine weitere Variante ist eine weitere JSON-Datei.

> In der Mail heißt es bewusst **„Ausbilder-Info“**, nicht „Newsletter“, und es
> gibt keine Ausgabennummer: Es soll keine Erwartung regelmäßiger Post entstehen.
> „Newsletter“ ist nur der interne Name von Repo, Build und Dateien.

- **Design & Technik:** [`CLAUDE.md`](CLAUDE.md)
- **Prozess / Loop:** [`AGENTS.md`](AGENTS.md)
- **Ausgaben:** [`ROADMAP.md`](ROADMAP.md)

---

## In fünf Schritten zum Versand

1. **Inhalt prüfen.** Die drei Termine des Ausbildertags on tour 2027 stehen in
   Abschnitt 3 (aus dem Save-the-Date-Flyer übernommen). Neue Platzhalter in
   eckigen Klammern meldet der Build. Programm, Anmeldeweg und ein
   Anmelde-Button kommen mit der eigentlichen Einladung (siehe `ROADMAP.md`).
2. **Anhänge prüfen.** Leitfaden Gartenbau in `anhang/gaertner/`, Leitfaden
   Grüne Berufe in `anhang/gruene-berufe/` – im Repo, bei neuer Fassung
   ersetzen. `anhang/alle/` bleibt leer, die Azubi-Info geht nicht mit. Das Merkblatt der Variante hängt
   automatisch an – Details in [`anhang/README.md`](anhang/README.md).
3. **Bauen.**
   ```bash
   python3 tools/build_newsletter.py
   ```
   Erzeugt je Variante in `dist/gaertner/` und `dist/gruene-berufe/` drei
   Dateien mit sprechendem Namen aus der Varianten-JSON (`dateiname`), z. B.
   `Ausbilder-Info-2026-10-Gartenbau.eml` (Versand), `.html` (Vorschau im
   Browser) und `.txt` (Nur-Text-Fassung). `--variante gaertner` baut nur
   eine, `--streng` bricht bei offenen Platzhaltern ab.
4. **Prüfen.** Beide `.html`-Vorschauen im Browser ansehen (auch schmal
   ziehen), dann je Variante eine Testmail an die eigene Adresse und an eine
   externe Adresse (z. B. ein Gmail-Konto) schicken.
5. **Versenden.** `Ausbilder-Info-2026-10-Gartenbau.eml` an den
   Gartenbau-Verteiler, `Ausbilder-Info-2026-10-Gruene-Berufe.eml` an die
   übrigen Grünen Berufe – jeweils in Outlook öffnen, Empfänger in **Bcc**,
   Anhänge prüfen, senden. Bei großen Verteilern in mehreren Tranchen
   (Grenzen des Mailservers beachten).

### Ohne Python: Build aus GitHub Actions

Bei jedem Push baut der Workflow **„Newsletter-Check“** beide Varianten und
legt `dist/` als Artefakt ab: *Actions → Lauf öffnen → Artefakt „newsletter“
herunterladen.* Die `.eml`-Dateien darin sind vollständig, inklusive aller
Anhänge.

---

## Versandwege im Detail

**Absender.** Die `.eml` trägt absichtlich keinen Absender: Outlook sendet aus
dem Konto, in dem du sie öffnest. Antworten landen über die Kopfzeile
`Reply-To` trotzdem im Funktionspostfach abteilung3@rpf.bwl.de (in der
geöffneten Nachricht unter *Optionen → Antworten an* sichtbar; falls leer, dort
eintragen). Soll das Funktionspostfach selbst als Absender erscheinen, braucht
dein Konto in Exchange die Berechtigung **„Senden als“** für dieses Postfach
(bei BITBW beantragen); erst dann `--absender "Ausbildungsberatung Grüne
Berufe <abteilung3@rpf.bwl.de>"` setzen. Ohne diese Berechtigung weist der
Server die Nachricht beim Senden ab („Sie besitzen nicht die Berechtigung, die
Nachricht im Auftrag des angegebenen Benutzers zu senden“, SendAsDenied) – dann
ist nichts rausgegangen.

**Outlook (klassisch).** Doppelklick auf die `.eml` öffnet die Datei dank
der Kopfzeile `X-Unsent: 1` direkt als neue, noch nicht gesendete Nachricht –
Empfänger in Bcc, Anhänge prüfen, senden. Erscheint stattdessen ein Lesefenster
(etwa weil das neue Outlook oder Windows Mail für `.eml` zuständig ist): die
Datei per Drag-and-drop in den Ordner **Entwürfe** ziehen und dort öffnen, oder
**Weiterleiten** wählen und den Betreff bereinigen.

**Thunderbird.** *Datei → Öffnen → Gespeicherte Nachricht öffnen*, dann
*Nachricht → Als neu bearbeiten*. Thunderbird sendet das HTML unverändert.

**Newsletter-System.** Quelltext von `dist/newsletter.html` übernehmen, das Logo
im System als Bild hochladen und die beiden eingebetteten `data:`-Bildquellen
durch die Bild-URLs des Systems ersetzen. Die Nur-Text-Fassung liegt in
`dist/newsletter.txt`.

> **Gut zu wissen:** Outlook wandelt HTML beim Senden in sein eigenes Format um
> (Word-Engine). Runde Ecken und die mobilen Umbrüche gehen dabei verloren. Das
> Layout ist deshalb bewusst tabellenbasiert und 600 px breit, damit es auch
> danach in allen gängigen Programmen sauber aussieht. Testmail vor dem
> Versand ist Pflicht.

---

## Aufbau der Ausgabe

| Baustein | Landes-CD |
|----------|-----------|
| Kopf mit RPF-Logo links | CI-Header-Muster (Logo links) |
| Gelbe Titelfläche „Ausbilder-Info …“, Serif-Überschrift mit Punkt | BaWü Gelb als Fläche, Text darauf schwarz |
| Inhaltsübersicht mit gelben Nummern | Karte (`.bw-card`-Optik) |
| Kapitelköpfe: gelbes Nummernquadrat, Serif-Titel, gelbe Linie | wie im Leitfaden „Klar handeln in der Ausbildung“ |
| Tabelle Urlaubsanspruch mit **einem** gelb hervorgehobenen Wert, Dokument-Karte zum Merkblatt | Infografik-Regel: Gelb nur für einen Wert |
| ✓-Liste, Hinweiskasten (grau, schwarzer Balken) | `.bw-hinweis` |
| Zwei Dokument-Karten (halbiert) | `.bw-flaechen.bw-halb` |
| Save-the-Date-Block im Flyer-Layout: 2×2-Fotoraster, schwarzes Band mit Serif-Titel, drei gelben Terminen und rundem Störer (Button erst mit der Einladung) | `.bw-flaeche--schwarz`, `.bw-stoerer` |
| Kontaktkasten, schwarzer Fuß mit Negativ-Logo, Impressum/Datenschutz/Barrierefreiheit | `.bw-footer` |

Farben und Schriften stehen in `newsletter.html` ausschließlich als
`var(--bw-*)` aus `bw-theme.css`. Der Build setzt die festen Werte ein, weil
E-Mail-Programme keine CSS-Variablen verstehen – das Theme bleibt trotzdem die
einzige Quelle.

**Schriften:** Die Landesschriften BaWue Sans/Serif stehen im Schriftstapel an
erster Stelle und greifen überall, wo sie installiert sind (Landesverwaltung).
Sonst gelten die Fallbacks Georgia (Überschriften) und Arial/Systemschrift
(Text). Schriftdateien werden nicht mitgeschickt: E-Mail-Programme laden keine
eingebetteten Fonts, und die Web-Lizenz erlaubt keine Weitergabe an Empfänger.

---

## Lange Inhalte: Kurzfassung in der Mail, Merkblatt im Anhang

Ausführliche Erläuterungen (etwa der Urlaubsanspruch im Abschlussjahr) stehen
nicht komplett in der Mail. Bewährt hat sich: **das Wichtigste kompakt in der
Mail, die vollständige Fassung als Merkblatt-PDF im Landesdesign im Anhang.**
Das bleibt kurz, barrierefrei, druck- und ablagefähig und ist unauffällig für
Spamfilter. Nicht geeignet sind Akkordeons oder aufklappbare Bereiche (Outlook
und Gmail unterstützen sie nicht, versteckter Text gilt als Spam-Signal) und
Bilder mit Text. Ein „Mehr lesen“-Link ist nur sinnvoll, wenn der Text auf
einer Seite des RPF veröffentlicht ist.

Merkblätter liegen als HTML unter `merkblatt/` (Landesdesign über
`bw-theme.css`, Text vom Fachbereich nach juristischer Prüfung, Variantenblöcke
wie im Newsletter) und
werden je Variante mit Chromium als getaggtes A4-PDF gedruckt – mit den
Landesschriften aus `assets/fonts/`:
```bash
npm i -g playwright && npx playwright install chromium   # einmalig
node tools/build_merkblatt.js [variante]                 # -> merkblatt/Merkblatt-…-<Variante>.pdf
```
Das fertige PDF wird mitversioniert, damit der Newsletter-Build es ohne
Node/Playwright anhängen kann.

## Technik: Regeln für HTML-E-Mails (Kurzfassung, Details in `CLAUDE.md`)

- Tabellen-Layout mit `role="presentation"`, 600 px breit, alle Styles inline,
  Farben doppelt (`bgcolor` und `background-color`), Bilder mit `width`/`height`.
- Outlook-Sonderwege: Geistertabelle, `<!--[if mso]>`-Schriftstapel, Störer und
  Button zusätzlich als VML.
- Media Queries nur als Bonus für mobile Clients, nie als Voraussetzung.
- **Nichts wird nachgeladen:** keine externen Bilder, keine Zählpixel, keine
  Web-Fonts. Das Logo geht als Inline-Anhang (Content-ID) mit.
  ```bash
  python3 tools/check_offline.py     # findet externe Lade-Referenzen (läuft im CI)
  ```
- HTML unter 100 KB halten (Gmail kürzt darüber).

---

## Struktur

```
newsletter.html              die aktuelle Ausgabe (Quelle mit --bw-* Tokens und Variantenblöcken)
varianten/                   je Variante eine JSON: Betreff, Eyebrow, Kontakt, Merkblatt-Datei
bw-theme.css                 Design-System, Single Source of Truth (aus der Vorlage)
assets/logo/                 RPF-Logo positiv/negativ — lizenzpflichtig, Repo privat
assets/fotos/                Fotos des Save-the-Date-Flyers, auf 600×432 px zugeschnitten (JPEG)
assets/fonts/                BaWue Sans/Serif (woff2/woff) — nur für Merkblatt-PDFs, lizenzpflichtig
merkblatt/                   Merkblätter: HTML-Quelle im Landesdesign + gedrucktes PDF
tools/build_merkblatt.js     druckt merkblatt/*.html als getaggtes A4-PDF (Chromium)
anhang/alle/ · anhang/<variante>/  Anhänge der E-Mail (versioniert, Repo privat)
tools/build_newsletter.py    Build: Tokens auflösen, Logo einbetten, .eml/.html/.txt
tools/check_offline.py       Offline-/CDN-Prüfung (CI-Gate)
.github/workflows/ci.yml     Offline-Check + Build beider Varianten + Artefakt bei jedem Push/PR
.github/workflows/claude.yml @claude-Loop (Issue/PR → Branch → PR)
.github/ISSUE_TEMPLATE/      Vorlagen für Ausgaben und Aufgaben
CLAUDE.md AGENTS.md ROADMAP.md
```

---

## Recht & Lizenz

- **Repository privat halten.** Das RPF-Logo in `assets/logo/` und die
  Schriften in `assets/fonts/` sind geschützt (`LIZENZ.md` in beiden Ordnern).
  Wird das Repo je öffentlich, beides ausschließen und aus der Historie
  entfernen – der Build setzt dann eine Wortmarke ein. Die Schriften werden nur
  in die Merkblatt-PDFs eingebettet, nie in die E-Mail.
- Die Leitfaden-PDFs in `anhang/` enthalten lizenzierte Schriften und
  Bildmaterial; sie liegen nur hier, weil das Repo privat ist. Quelle und
  Pflege bleiben im Repo `Rechte-und-Pflichten-von-Azubis`.
- **Fotos** (`assets/fotos/`) stammen aus dem Save-the-Date-Flyer des RPF; nur
  Bilder verwenden, deren Nutzungsrechte beim RP Freiburg liegen. Bildnachweise
  gehören unter das Raster oder in den Fuß.
- **Keine Empfängerdaten ins Repo.** Verteiler werden außerhalb gepflegt
  (Outlook-Kontaktgruppe, Fachverfahren). Versand immer per Bcc.
- Rechtsaussagen (z. B. Urlaubsansprüche) stammen vom Fachbereich und werden
  nur dort geändert – siehe `AGENTS.md`, Stop-Bedingungen.
