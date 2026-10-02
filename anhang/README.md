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
anhang/gaertner/Leitfaden-Ausbildung-Gartenbau-2026.pdf          Leitfaden „Klar handeln“, Fassung Gartenbau (02.10.2026, komprimiert)
anhang/gruene-berufe/Leitfaden-Ausbildung-Gruene-Berufe-2026.pdf  Leitfaden, Fassung Grüne Berufe (02.10.2026, komprimiert)
```

`anhang/alle/` ist derzeit leer: Die Azubi-Info „Gut durch die Ausbildung“ geht
bewusst nicht mit – die Ausbilder-Info richtet sich an die Betriebe.

Die Dateinamen sind bewusst kurz und ohne Umlaute (manche Mailserver
verstümmeln sonst den Namen).

Kommt ein weiteres Dokument dazu, in `newsletter.html` (Abschnitt 2) eine
zweite Dokument-Karte ergänzen – halbiert nebeneinander, wie in `CLAUDE.md` 3.1.
