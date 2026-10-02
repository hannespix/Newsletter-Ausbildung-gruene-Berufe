# ROADMAP — Ausgaben

> Zweck: Ausbilder-Info der Ausbildungsberatung Grüne Berufe (RP Freiburg,
> Referat 31) an die Ausbildungsbetriebe – als HTML-E-Mail im Landesdesign.
> In der Mail nie „Newsletter“: keine Erwartung regelmäßiger Post schüren.
> Zielgruppe: Ausbilderinnen und Ausbilder im Regierungsbezirk Freiburg.
> Versand: aus Outlook (Bcc) über `dist/newsletter.eml`, siehe README.

Jede Ausgabe ist ein Issue und ein Pull Request (siehe `AGENTS.md`). Vor dem
Versand wird der Stand als Ausgabe archiviert (`ausgaben/JJJJ-MM-titel.html`),
damit `newsletter.html` für die nächste Ausgabe frei ist.

---

## A1 — September 2026: Start des Ausbildungsjahres (zwei Varianten)
**Varianten:** `gaertner` (Gartenbau) und `gruene-berufe` (Landwirtschaft, Weinbau,
Fischerei und weitere) – je eigene Urlaubstabelle, eigenes Merkblatt, eigene
Leitfaden-Fassung. Die Leitfäden „Klar handeln in der Ausbildung“ (Gartenbau /
Grüne Berufe) werden nachgereicht, sobald sie fertig sind.
**Inhalt:** Urlaub im Abschlussjahr (Kurzfassung + Merkblatt-PDF, Text nach der
juristischen Prüfung vom 1. Oktober 2026 – Mindesturlaub/Mehrurlaub, Zeilen für
Landwirtschaft/Weinbau und Minderjährige) · Leitfaden „Rechte und Pflichten“,
Fassung Grüne Berufe (Anhang) ·
Save the Date „Ausbildertag on tour 2027“ mit den drei Terminen aus dem Flyer
(21.01., 26.01., 28.01.2027), noch keine Anmeldung.
**Done:** Build läuft ohne Fehler, Offline-Check grün, keine Platzhalter,
Testmail in Outlook und an eine externe Adresse geprüft, Anhänge dabei.
**Status:** Inhalt vollständig, Versand nach Testmail möglich.

## A2 — Einladung zum Ausbildertag
**Inhalt:** Programm, Anmeldeweg und Frist, Anmelde-Button (Baustein liegt in
der Git-Historie von A1: gelber Button mit `mailto:`, alternativ Formular-Link).
Laut Flyer folgt die offizielle Einladung mit Anmeldelink im November 2026.
**Done:** eigene Aussendung, sobald Programm und Anmeldung feststehen.

## Ideen für weitere Ausgaben
- **Foto oder Illustration** in der Titelfläche – nur mit Nutzungsrechten des RPF
  (Bilder als Content-ID einbetten, nie extern laden).
- **Wiederkehrende Rubriken:** Termine (Prüfungen, Ausbildertag), Neues aus
  dem Recht (mit Fundstelle), Praxisfrage des Monats aus der Beratung.
- **Versandweg:** Newsletter-System statt Outlook, damit Media Queries und
  Abmelde-Link automatisch funktionieren.
- **Archiv:** Ordner `ausgaben/` mit allen versendeten Fassungen.
