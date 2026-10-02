# anhang/ — Dateien, die an der E-Mail hängen

Der Build hängt je Variante an (siehe `varianten/*.json`):

1. das **Merkblatt** der Variante aus `merkblatt/` (liegt im Repo),
2. alles aus **`anhang/alle/`** (geht an beide Varianten),
3. alles aus **`anhang/<variante>/`** (`anhang/gaertner/`, `anhang/gruene-berufe/`).

Die Dateien liegen **im Repo** (privat), damit auch der CI-Build vollständige
Mails liefert. Quelle der Leitfäden bleibt das Repo
`Rechte-und-Pflichten-von-Azubis`: Bei einer neuen Fassung die Datei hier
ersetzen, Dateinamen beibehalten. README-Dateien werden nie angehängt.

Stand Oktober 2026:

```
anhang/alle/Azubi-Info-Rechte-und-Pflichten-2026.pdf        Azubi-Info „Gut durch die Ausbildung“ (Stand 15.09.2026)
anhang/gaertner/Leitfaden-Ausbildung-Gartenbau-2026.pdf     Leitfaden „Klar handeln“, Fassung Gartenbau (02.10.2026)
anhang/gruene-berufe/Leitfaden-Ausbildung-Gruene-Berufe-2026.pdf  Leitfaden, Fassung Grüne Berufe (02.10.2026)
```

Die Dateinamen sind bewusst kurz und ohne Umlaute (manche Mailserver
verstümmeln sonst den Namen).

Wird nur ein Dokument mitgeschickt, die zweite Dokument-Karte in
`newsletter.html` (Abschnitt 2) entfernen.
