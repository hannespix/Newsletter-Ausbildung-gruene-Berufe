# ROADMAP — Ausgaben

> Zweck: Newsletter der Ausbildungsberatung Grüne Berufe (RP Freiburg, Referat 31)
> an die Ausbildungsbetriebe – als HTML-E-Mail im Landesdesign.
> Zielgruppe: Ausbilderinnen und Ausbilder im Regierungsbezirk Freiburg.
> Versand: aus Outlook (Bcc) über `dist/newsletter.eml`, siehe README.

Jede Ausgabe ist ein Issue und ein Pull Request (siehe `AGENTS.md`). Vor dem
Versand wird der Stand als Ausgabe archiviert (`ausgaben/JJJJ-MM-titel.html`),
damit `newsletter.html` für die nächste Ausgabe frei ist.

---

## A1 — September 2026: Start des Ausbildungsjahres
**Inhalt:** Urlaub im Abschlussjahr · Leitfaden „Rechte und Pflichten“ (Anhang) ·
Einladung zum Ausbildertag.
**Done:** Build läuft ohne Fehler, Offline-Check grün, Platzhalter zum
Ausbildertag ausgefüllt, Testmail in Outlook und an eine externe Adresse
geprüft, Anhänge dabei. **Status:** Gerüst und Inhalt stehen, Platzhalter offen.

## Ideen für weitere Ausgaben
- **Foto oder Illustration** in der Titelfläche – nur mit Nutzungsrechten des RPF
  (Bilder als Content-ID einbetten, nie extern laden).
- **Wiederkehrende Rubriken:** Termine (Prüfungen, Ausbildertag), Neues aus
  dem Recht (mit Fundstelle), Praxisfrage des Monats aus der Beratung.
- **Versandweg:** Newsletter-System statt Outlook, damit Media Queries und
  Abmelde-Link automatisch funktionieren.
- **Archiv:** Ordner `ausgaben/` mit allen versendeten Fassungen.
