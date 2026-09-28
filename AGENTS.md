# AGENTS.md — Agentisches Arbeiten im Loop

Diese Datei beschreibt **wie** in diesem Repository gearbeitet wird (Prozess).
Das **was** (Design, Technik, CI-Regeln) steht in `CLAUDE.md`, die Ausgaben in
`ROADMAP.md` und den GitHub Issues. `@claude` und alle Beteiligten lesen vor
jeder Aufgabe `CLAUDE.md` **und** `AGENTS.md`.

> Sprache durchgehend Deutsch. Sicherheit und CI-Treue gehen vor Tempo.

---

## 1. Rollen

- **Mensch (Hannes / Fachbereich):** legt Inhalte und Versandtermine fest,
  eröffnet Issues, prüft Pull Requests, merged, **versendet**. Trifft alle
  Entscheidungen mit Rechts-, Datenschutz- oder Fachbezug — jede Rechtsaussage
  im Newsletter stammt vom Fachbereich.
- **`@claude` (GitHub Action):** plant, setzt Ausgaben und Änderungen um, öffnet
  Pull Requests, reagiert auf Review-Kommentare. Arbeitet **nur** auf Branches
  und über PRs, niemals direkt auf `main`. Versendet nie selbst.

---

## 2. Der Loop

Ein Durchlauf bearbeitet **genau ein** Issue (eine Ausgabe oder eine Aufgabe):

```
   ┌────────────────────────────────────────────────────────────┐
   │ 1. AUFGABE   Issue mit Inhalt, Termin, Definition of Done   │
   │ 2. PLAN      @claude antwortet mit kurzem Umsetzungsplan     │
   │ 3. BUILD     Branch anlegen, umsetzen, Build + Selbstcheck   │
   │ 4. PR        Pull Request öffnen, Bezug zum Issue            │
   │ 5. PRÜFUNG   CI (Offline-Check, Build) + menschliches Review │
   │ 6. NACHBESSERN bei Änderungswünschen: @claude im PR          │
   │ 7. MERGE     Mensch merged, baut, testet, versendet          │
   └────────────────────────────────────────────────────────────┘
```

**Auslösen:** `@claude` in einem Issue oder PR-Kommentar erwähnen, mit klarer
Anweisung. Beispiele:

- `@claude setze die Ausgabe Dezember 2026 aus dem Issue um und öffne einen PR.`
- `@claude die Tabelle zum Urlaubsanspruch braucht eine Zeile für Minderjährige. Bitte umsetzen.`
- `@claude warum schlägt der CI-Check fehl?` (mit aktivem `actions: read`)

---

## 3. Ausgaben statt Milestones

Jede Newsletter-Ausgabe ist ein Issue (Vorlage „Ausgabe“) und ein PR. Sie ist:

- **vollständig** am Ende (alle Abschnitte, Betreff, Vorschautext, Anhänge
  benannt) — offene Platzhalter nur für Angaben, die der Mensch liefert
  (Termine, Orte), und im PR ausdrücklich genannt,
- **lauffähig**: Build und Offline-Check grün, Vorschau geprüft,
- mit einer **Definition of Done** versehen.

Nach dem Versand archiviert der Mensch (oder `@claude` per Aufgabe) den Stand
unter `ausgaben/JJJJ-MM-titel.html`; `newsletter.html` ist dann frei für die
nächste Ausgabe. Größere Umbauten am Gerüst (neue Bausteine, Build) laufen als
eigene Aufgabe, nicht versteckt in einer Ausgabe.

---

## 4. Definition of Done (für jeden PR)

Vor „fertig“ prüft `@claude` selbst und hakt im PR-Text ab:

- [ ] Erfüllt das Issue-Ziel vollständig, nichts Unfertiges zurückgelassen.
- [ ] **CI-Treue** nach `CLAUDE.md` (nur `--bw-*`-Tokens, Gelb-Budget
      eingehalten, keine Schatten/Verläufe, Gelb nie als Text auf Weiß,
      hoher Weißanteil, Bausteine aus 3.1).
- [ ] **E-Mail-Technik** nach `CLAUDE.md` 2.1: Tabellen-Layout, Styles inline,
      Outlook-Sonderwege, HTML < 100 KB, Media Queries nur als Bonus.
- [ ] **Zero-Trust:** keine externen Bilder/Fonts/Skripte;
      `python3 tools/check_offline.py` läuft fehlerfrei durch.
- [ ] **Build:** `python3 tools/build_newsletter.py` ohne Fehler; Vorschau
      breit und schmal geprüft; Nur-Text-Fassung lesbar.
- [ ] **Barrierefrei:** `lang`, `role="presentation"`, `alt`-Texte,
      Überschriftenhierarchie, Kontrast ≥ 4,5:1.
- [ ] **Texte:** Deutsch, aktive Verben, Sentence-Case, Zahlen de-DE;
      Rechtsaussagen unverändert aus dem Issue bzw. den Leitfäden übernommen.
- [ ] Offene Platzhalter im PR benannt; Anhänge benannt.
- [ ] Kurzer, klarer PR-Text: Was, Warum, Wie getestet. Bezug `Closes #<Nr>`.
- [ ] Keine Geheimnisse, keine Empfänger- oder personenbezogenen Echtdaten.

---

## 5. Leitplanken (verbindlich)

**`@claude` darf:**
- Branches anlegen, Dateien ändern, PRs öffnen, auf Reviews reagieren.
- Innerhalb des Repos refactoren und Prüfungen ergänzen.

**`@claude` darf nicht:**
- Nicht auf `main` pushen, keine PRs selbst mergen, nie versenden.
- Keine externen Abhängigkeiten, Bild-Hosts, Tracker oder Kurzlinks einführen.
- Keine Secrets, Tokens, Verteiler oder personenbezogenen Echtdaten committen.
- **Rechtsaussagen nicht eigenmächtig ändern oder ergänzen** (Fristen,
  Ansprüche, Paragrafen). Umformulieren nur redaktionell, inhaltsgleich.
- Den Scope eines Issues nicht eigenmächtig erweitern. Unklarheiten →
  **nachfragen statt raten** (Kommentar im Issue/PR), dann stoppen.

**Stop-Bedingungen** (Loop anhalten, Mensch einbeziehen):
- Aufgabe berührt Recht, Datenschutz oder eine Fachentscheidung.
- Definition of Done nicht erreichbar ohne Scope-Erweiterung.
- Wiederholt fehlschlagende CI ohne klare Ursache.

---

## 6. Selbstreview vor dem PR

`@claude` führt vor dem Öffnen des PR einen kurzen Eigen-Review durch und
notiert das Ergebnis im PR:

1. Diff gegen die Definition of Done (Abschnitt 4) prüfen.
2. CI-Checkliste aus `CLAUDE.md` durchgehen, Build-Hinweise lesen.
3. Offene Punkte/Annahmen explizit benennen, nicht verschweigen.

---

## 7. Commit- & PR-Konventionen

- Branch: `ausgabe/<jjjj-mm>`, `feat/<kurz>`, `fix/<kurz>`, `chore/<kurz>`.
- Commits klein und sprechend, Imperativ, Deutsch:
  `Ausbildertag: Termin und Ort eintragen`.
- PR-Titel = Ziel in einem Satz. PR-Body: Kontext, Vorgehen, Test, `Closes #<Nr>`.
- Ein PR = eine Ausgabe oder eine Aufgabe.

---

## 8. Einstieg für einen neuen Loop (Vorlage)

> **Issue-Titel:** Ausgabe Dezember 2026: Prüfungen und Jahreswechsel
> **Anlass:** Versand in KW 49. Inhalte: Prüfungstermine, Berichtsheft vor der
> Prüfung, Rückblick Ausbildertag.
> **Definition of Done:** Build und Offline-Check grün, Platzhalter benannt,
> Anhänge benannt, CI-treu, barrierefrei, Rechtsaussagen unverändert.
> **Auslöser:** `@claude setze diese Ausgabe um und öffne einen PR.`
