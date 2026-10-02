# anhang/ — Dateien, die an der E-Mail hängen

Der Build hängt je Variante an (siehe `varianten/*.json`):

1. das **Merkblatt** der Variante aus `merkblatt/` (liegt im Repo),
2. alles aus **`anhang/alle/`** (geht an beide Varianten),
3. alles aus **`anhang/<variante>/`** (`anhang/gaertner/`, `anhang/gruene-berufe/`).

Die Dateien hier werden **nicht** versioniert (`.gitignore`) – sie liegen im
Repo `Rechte-und-Pflichten-von-Azubis` unter `pdf/` und werden von dort kopiert,
damit nichts auseinanderläuft. README-Dateien werden nie angehängt.

Für die Ausgabe September 2026 (sobald die Leitfäden fertig sind):

```
pdf/… Azubi-Info Rechte und Pflichten.pdf           → anhang/alle/
pdf/… Leitfaden Ausbildung (Gartenbau).pdf          → anhang/gaertner/
pdf/… Leitfaden Ausbildung (Grüne Berufe).pdf       → anhang/gruene-berufe/
```

Tipp: kurze, sprechende Dateinamen ohne Umlaute vermeiden Ärger bei manchen
Mailservern, z. B. `Leitfaden-Ausbildung-Gartenbau-2026.pdf`.

Wird nur ein Dokument mitgeschickt, die zweite Dokument-Karte in
`newsletter.html` (Abschnitt 2) entfernen.
