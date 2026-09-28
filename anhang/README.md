# anhang/ — Dateien, die an der E-Mail hängen

Alles, was hier liegt (außer dieser README), hängt der Build automatisch an
`dist/newsletter.eml` an. Die Dateien werden **nicht** versioniert
(`.gitignore`) – sie liegen im Repo `Rechte-und-Pflichten-von-Azubis` unter
`pdf/` und werden von dort kopiert, damit nichts auseinanderläuft.

Für die Ausgabe September 2026:

```
pdf/20260915 Leitfaden Ausbildung (Gartenbau).pdf        → anhang/
pdf/20260915 Azubi-Info Rechte und Pflichten.pdf         → anhang/
```

Tipp: kurze, sprechende Dateinamen ohne Umlaute vermeiden Ärger bei manchen
Mailservern, z. B. `Leitfaden-Ausbildung-Gartenbau-2026.pdf` und
`Azubi-Info-Rechte-und-Pflichten-2026.pdf`.

Wird nur ein Dokument mitgeschickt, die zweite Dokument-Karte in
`newsletter.html` (Abschnitt 2) entfernen.
