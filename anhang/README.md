# anhang/ — Dateien, die an der E-Mail hängen

Alles, was hier liegt (außer dieser README), hängt der Build automatisch an
`dist/newsletter.eml` an. Die Dateien werden **nicht** versioniert
(`.gitignore`) – sie liegen im Repo `Rechte-und-Pflichten-von-Azubis` unter
`pdf/` und werden von dort kopiert, damit nichts auseinanderläuft.

Für die Ausgabe September 2026:

```
pdf/20260915 Leitfaden Ausbildung (Grüne Berufe).pdf     → anhang/
pdf/20260915 Azubi-Info Rechte und Pflichten.pdf         → anhang/
```

Die Ausbilder-Info geht an **alle** Ausbildungsbetriebe der Grünen Berufe im
Regierungsbezirk, deshalb die Fassung „Grüne Berufe“ des Leitfadens (breitere
Berufsliste, Ausfüllfelder), nicht die Gartenbau-Fassung. Das Merkblatt
„Urlaub im letzten Ausbildungsjahr“ liegt unter `merkblatt/` im Repo und
hängt automatisch an.

Tipp: kurze, sprechende Dateinamen ohne Umlaute vermeiden Ärger bei manchen
Mailservern, z. B. `Leitfaden-Ausbildung-Gartenbau-2026.pdf` und
`Azubi-Info-Rechte-und-Pflichten-2026.pdf`.

Wird nur ein Dokument mitgeschickt, die zweite Dokument-Karte in
`newsletter.html` (Abschnitt 2) entfernen.
