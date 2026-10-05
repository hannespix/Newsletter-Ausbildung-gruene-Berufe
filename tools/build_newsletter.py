#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_newsletter.py — baut aus newsletter.html den versandfertigen Newsletter.

Was passiert:
  1. Design-Tokens: jedes var(--bw-*) im HTML wird durch den Wert aus
     bw-theme.css ersetzt. E-Mail-Programme kennen keine CSS-Variablen; das
     Theme bleibt trotzdem die einzige Quelle für Farben und Schriften.
  2. Bilder: lokale <img src="assets/..."> werden für die Browser-Vorschau als
     data:-URLs eingebettet und in der E-Mail als Inline-Anhänge (Content-ID)
     mitgeschickt. Fehlt das Logo, steht eine reine Wortmarke an seiner Stelle
     (das Logo wird nie nachgebaut).
  3. Textfassung: aus dem HTML entsteht die Nur-Text-Alternative der E-Mail.
  4. Varianten: je Datei in varianten/*.json entsteht eine Ausgabe. {{SCHLÜSSEL}}
     werden aus der JSON ersetzt, Blöcke <!--[wenn gaertner]--> … <!--[/wenn]-->
     bleiben nur in der genannten Variante stehen (mehrere: <!--[wenn a,b]-->).
  5. Anhänge je Variante: das Merkblatt aus der JSON (merkblatt/), alle Dateien
     in anhang/alle/ und anhang/<variante>/ (außer README.md).
  6. Prüfung: offene Platzhalter in eckigen Klammern werden gemeldet.

Ausgabe (dist/<variante>/, Dateiname aus „dateiname“ der Varianten-JSON,
z. B. Ausbilder-Info-2026-10-Gartenbau):
  <dateiname>.html  Vorschau im Browser (Bilder eingebettet, Styles aufgelöst)
  <dateiname>.eml   E-Mail zum Öffnen in Outlook oder Thunderbird. Die Kopfzeile
                    „X-Unsent: 1“ lässt das klassische Outlook die Datei direkt
                    als neue, noch nicht gesendete Nachricht öffnen.
  <dateiname>.txt   Nur-Text-Fassung

Aufruf:  python3 tools/build_newsletter.py [--variante gaertner] [--streng] [--antwort-an "…"] [--absender "…"]
Absender: Die .eml trägt absichtlich kein „From“ – Outlook sendet aus dem eigenen
Konto. Antworten gehen per „Reply-To“ an das Funktionspostfach. Soll das
Funktionspostfach selbst Absender sein (--absender), muss das Konto in Exchange
„Senden als“ für dieses Postfach dürfen, sonst: SendAsDenied, nichts geht raus.
Nur Python-Standardbibliothek, keine Abhängigkeiten.
"""
import argparse
import base64
import json
import mimetypes
import re
import sys
import textwrap
from dataclasses import dataclass
from email import policy
from email.message import EmailMessage, MIMEPart
from email.parser import BytesParser
from email.utils import formatdate, make_msgid
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
mimetypes.add_type("image/png", ".png")

ANTWORT_AN = "Ausbildungsberatung Grüne Berufe <abteilung3@rpf.bwl.de>"
CID_DOMAIN = "newsletter.rpf.bwl.de"
GMAIL_GRENZE_KB = 100  # Gmail schneidet Nachrichten über ~102 KB ab


# ------------------------------------------------------------------ Tokens
TOKEN_RE = re.compile(r"--(bw-[\w-]+)\s*:\s*([^;{}]+);")
VAR_RE = re.compile(r"var\(\s*--(bw-[\w-]+)\s*(?:,[^)]*)?\)")


def lade_tokens(theme: Path) -> dict:
    """Liest alle --bw-* Tokens aus bw-theme.css und löst Verweise auf."""
    css = re.sub(r"/\*.*?\*/", "", theme.read_text(encoding="utf-8"), flags=re.S)
    roh = {}
    for m in TOKEN_RE.finditer(css):
        roh.setdefault(m.group(1), m.group(2).strip())  # erste Definition gilt (Desktop)

    def aufloesen(name: str, tiefe: int = 0) -> str:
        if tiefe > 12:
            sys.exit(f"FEHLER: zirkulärer Token-Verweis bei --{name}")
        return VAR_RE.sub(lambda m: aufloesen(m.group(1), tiefe + 1), roh[name])

    tokens = {}
    for name in roh:
        try:
            wert = aufloesen(name)
        except KeyError as e:
            sys.exit(f"FEHLER: Token --{name} verweist auf unbekanntes {e}")
        # Schriftstapel enthalten doppelte Anführungszeichen – innerhalb von
        # style="…" müssen es einfache sein.
        tokens[name] = wert.replace('"', "'")
    return tokens


def tokens_einsetzen(html: str, tokens: dict) -> str:
    fehlend = set()

    def ersetze(m):
        name = m.group(1)
        if name in tokens:
            return tokens[name]
        fehlend.add("--" + name)
        return m.group(0)

    html = VAR_RE.sub(ersetze, html)
    if fehlend:
        sys.exit(
            "FEHLER: Tokens im Newsletter, die bw-theme.css nicht kennt: "
            + ", ".join(sorted(fehlend))
            + "\n       Fehlende Werte im Theme ergänzen, nicht im Newsletter hart codieren."
        )
    return html


# ------------------------------------------------------------- Kommentare
def kommentare_entfernen(html: str) -> str:
    """Entfernt normale HTML-Kommentare, lässt Outlook-Bedingungen (if mso) stehen."""
    geschuetzt = []

    def schuetzen(m):
        geschuetzt.append(m.group(0))
        return f"\x00{len(geschuetzt) - 1}\x00"

    html = re.sub(r"<!--\[if [^\]]+\]>(?:<!-- -->)?", schuetzen, html)   # Öffner
    html = re.sub(r"<!--<!\[endif\]-->|<!\[endif\]-->", schuetzen, html)   # Schließer
    html = re.sub(r"<!--[\s\S]*?-->", "", html)                             # Rest
    return re.sub(r"\x00(\d+)\x00", lambda m: geschuetzt[int(m.group(1))], html)


# ----------------------------------------------------------------- Bilder
@dataclass
class Bild:
    pfad: Path
    cid: str
    mime: str
    daten: bytes


IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
SRC_RE = re.compile(r'\bsrc\s*=\s*"([^"]+)"', re.I)


def wortmarke(tokens: dict, negativ: bool) -> str:
    """Reine Text-Wortmarke als Ersatz, wenn das (geschützte) Logo fehlt."""
    c1 = tokens["bw-weiss"] if negativ else tokens["bw-schwarz"]
    c2 = tokens["bw-grau-300"] if negativ else tokens["bw-text-leise"]
    return (
        '<table role="presentation" border="0" cellpadding="0" cellspacing="0">'
        f'<tr><td style="font-family:{tokens["bw-font-serif"]};font-size:20px;line-height:24px;'
        f'font-weight:700;color:{c1};">Regierungspräsidium Freiburg</td></tr>'
        f'<tr><td style="font-family:{tokens["bw-font-sans"]};font-size:12px;line-height:18px;'
        f'color:{c2};">Land Baden-Württemberg</td></tr></table>'
    )


def bilder_verarbeiten(html: str, tokens: dict, hinweise: list):
    """Gibt (html_vorschau, html_mail, bilder) zurück."""
    bilder: dict[str, Bild] = {}
    vorschau_teile, mail_teile = [], []
    pos = 0
    for m in IMG_RE.finditer(html):
        tag = m.group(0)
        src_m = SRC_RE.search(tag)
        vorschau_teile.append(html[pos:m.start()])
        mail_teile.append(html[pos:m.start()])
        pos = m.end()
        src = src_m.group(1) if src_m else ""
        if not src or src.startswith(("data:", "cid:", "http:", "https:")):
            vorschau_teile.append(tag)
            mail_teile.append(tag)
            continue
        pfad = (ROOT / src).resolve()
        if not pfad.exists():
            if not src.startswith("assets/logo/"):
                sys.exit(f"FEHLER: Bild fehlt: {src} – Datei nach assets/ legen oder das <img> entfernen.")
            ersatz = wortmarke(tokens, negativ="negativ" in pfad.name.lower())
            hinweise.append(f"Bild fehlt: {src} → Wortmarke eingesetzt (Logo aus der Vorlage nach assets/logo/ kopieren)")
            vorschau_teile.append(ersatz)
            mail_teile.append(ersatz)
            continue
        if src not in bilder:
            mime = mimetypes.guess_type(pfad.name)[0] or "application/octet-stream"
            bilder[src] = Bild(pfad, f"{pfad.stem}@{CID_DOMAIN}", mime, pfad.read_bytes())
        b = bilder[src]
        b64 = base64.b64encode(b.daten).decode("ascii")
        vorschau_teile.append(tag.replace(src_m.group(0), f'src="data:{b.mime};base64,{b64}"'))
        mail_teile.append(tag.replace(src_m.group(0), f'src="cid:{b.cid}"'))
    vorschau_teile.append(html[pos:])
    mail_teile.append(html[pos:])
    return "".join(vorschau_teile), "".join(mail_teile), list(bilder.values())


# ------------------------------------------------------------ Textfassung
class TextFassung(HTMLParser):
    """Erzeugt aus dem E-Mail-HTML eine lesbare Nur-Text-Fassung.

    Layout-Tabellen mit width-Attribut gelten als Blöcke (jede Zeile eine
    Textzeile), Tabellen ohne width (Nummern-Badges, Störer, Button) als
    Inline-Elemente. Datentabellen (role="table") bekommen „|“ als Spalten-
    trenner. Verborgene Elemente (display:none) und <style> werden übersprungen.
    """

    ABSATZ = {"p", "ul", "ol", "blockquote"}
    UEBERSCHRIFT = {"h1", "h2", "h3", "h4"}
    IGNORIEREN = {"style", "script", "title", "head", "xml"}
    LEER = {"br", "img", "meta", "link", "hr", "input", "col"}
    TRENNER = "\x01"   # Platzhalter für den Zellen-Abstand in Layout-Tabellen

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.zeilen: list[str] = []
        self.aktuell: list[str] = []
        self.stapel: list[tuple[str, bool]] = []      # (Tag, ist verborgen?)
        self.verborgen = 0
        self.links: list[tuple[str, int]] = []
        self.tabellen: list[tuple[bool, bool]] = []   # (inline?, Datentabelle?)

    # -- Hilfen
    def _tab(self) -> tuple[bool, bool]:
        return self.tabellen[-1] if self.tabellen else (False, False)

    def _text(self) -> str:
        t = re.sub(r"\s+", " ", "".join(self.aktuell)).replace("\xa0", " ").replace("\xad", "")
        t = re.sub(r"\s*" + self.TRENNER + r"\s*", "  ", t)
        return t.strip()

    def _flush(self):
        t = self._text()
        if t:
            self.zeilen.append(t)
        self.aktuell = []

    def _leerzeile(self):
        if self.zeilen and self.zeilen[-1] != "":
            self.zeilen.append("")

    def _trenner(self, daten: bool):
        if not self._text():
            return
        if daten:
            self.aktuell.append(" | ")
        elif not (self.aktuell and self.aktuell[-1] == self.TRENNER):
            self.aktuell.append(self.TRENNER)

    def _in_zelle(self) -> bool:
        return any(t in ("td", "th") for t, _ in self.stapel)

    # -- Parser
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        style = (a.get("style") or "").replace(" ", "").lower()
        verborgen = "display:none" in style or tag in self.IGNORIEREN
        if tag not in self.LEER:
            self.stapel.append((tag, verborgen))
            if verborgen:
                self.verborgen += 1
        if self.verborgen:
            return
        inline, daten = self._tab()
        if tag == "table":
            neu_inline = "width" not in a
            if not neu_inline:
                self._flush()
            self.tabellen.append((neu_inline, (a.get("role") or "") == "table"))
        elif tag == "tr":
            if not inline:
                self._flush()
        elif tag in ("td", "th"):
            if not inline:
                self._trenner(daten)
        elif tag == "br":
            if inline:
                self.aktuell.append(" ")
            elif daten and self._in_zelle():
                self.aktuell.append(" – ")
            else:
                self._flush()
        elif tag in self.UEBERSCHRIFT:
            if self._text():
                self._trenner(False)      # Nummern-Badge vor der Überschrift
            else:
                self._flush()
        elif tag in self.ABSATZ or tag in ("div", "li"):
            self._flush()
        elif tag == "a" and a.get("href"):
            self.links.append((a["href"], len(self.aktuell)))

    def handle_endtag(self, tag):
        if tag in self.LEER:
            return
        while self.stapel:                # bis zum passenden Start-Tag zurückrollen
            t, v = self.stapel.pop()
            if v:
                self.verborgen -= 1
            if t == tag:
                break
        if self.verborgen:
            return
        if tag == "a" and self.links:
            href, start = self.links.pop()
            linktext = "".join(self.aktuell[start:]).strip().lower()
            if href.startswith("mailto:"):
                adresse = href[7:].split("?", 1)[0]
                if adresse.lower() not in linktext:
                    self.aktuell.append(f" ({adresse})")
            elif href.startswith(("http://", "https://")):
                kurz = re.sub(r"^https?://", "", href).rstrip("/").lower()
                if kurz not in linktext:
                    self.aktuell.append(f" ({href})")
        elif tag in self.UEBERSCHRIFT:
            self._flush()
            if self.zeilen and tag in ("h1", "h2"):
                self.zeilen.append(("=" if tag == "h1" else "-") * min(len(self.zeilen[-1]), 78))
            self._leerzeile()
        elif tag == "table":
            inline, _ = self.tabellen.pop() if self.tabellen else (False, False)
            if not inline:
                self._flush()
                self._leerzeile()
        elif tag == "tr":
            if not self._tab()[0]:
                self._flush()
        elif tag in self.ABSATZ:
            self._flush()
            self._leerzeile()
        elif tag in ("div", "li"):
            self._flush()

    def handle_data(self, data):
        if self.verborgen:
            return
        self.aktuell.append(data)

    def ergebnis(self) -> str:
        self._flush()
        text = "\n".join(self.zeilen)
        text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
        zeilen = []
        for z in text.split("\n"):
            if len(z) > 78 and not re.fullmatch(r"[=-]+", z):
                zeilen.extend(textwrap.wrap(z, 78, break_long_words=False, break_on_hyphens=False))
            else:
                zeilen.append(z)
        return "\n".join(zeilen) + "\n"


def textfassung(html: str) -> str:
    p = TextFassung()
    p.feed(html)
    p.close()
    return p.ergebnis()


# ------------------------------------------------------------------ E-Mail
def eml_bauen(html_mail: str, text: str, bilder: list, anhaenge: list, betreff: str,
              absender: str | None, antwort_an: str | None) -> bytes:
    """Baut die .eml so auf, wie Outlook selbst HTML-Mails mit eingebetteten
    Bildern aufbaut. Nur in dieser Struktur zeigt Outlook die Bilder sicher im
    Text und nicht zusätzlich als Anhang (auch beim Öffnen als Entwurf):

        multipart/mixed                                 (nur mit Anhängen)
        ├─ multipart/related; type="multipart/alternative"   (nur mit Bildern)
        │  ├─ multipart/alternative
        │  │  ├─ text/plain
        │  │  └─ text/html            (verweist per cid: auf die Bilder)
        │  └─ image/…                 (Content-Disposition: inline, Content-ID)
        └─ application/pdf …          (Content-Disposition: attachment)

    Die Teile sind MIMEPart (keine MIME-Version je Teil). Die Message-ID ist
    nötig, damit aktuelles Outlook den Entwurf speichern und senden kann.
    """
    def teil() -> MIMEPart:
        return MIMEPart(policy=policy.SMTP)

    alternative = teil()
    alternative.set_content(text, subtype="plain", charset="utf-8", cte="quoted-printable")
    alternative.add_alternative(html_mail, subtype="html", charset="utf-8", cte="quoted-printable")

    inhalt = alternative
    if bilder:
        inhalt = teil()
        inhalt["Content-Type"] = 'multipart/related; type="multipart/alternative"'
        inhalt.attach(alternative)
        for b in bilder:
            maintype, subtype = b.mime.split("/", 1)
            bild = teil()
            bild.set_content(b.daten, maintype=maintype, subtype=subtype, cte="base64",
                             disposition="inline", filename=b.pfad.name,
                             cid=f"<{b.cid}>", params={"name": b.pfad.name})
            inhalt.attach(bild)

    msg = EmailMessage(policy=policy.SMTP)
    # Kein From: Outlook sendet dann aus dem eigenen Konto. Ein fremder Absender
    # (Funktionspostfach) braucht in Exchange die Berechtigung „Senden als“,
    # sonst weist der Server die Nachricht beim Senden ab (SendAsDenied).
    if absender:
        msg["From"] = absender
    if antwort_an:
        msg["Reply-To"] = antwort_an
    msg["Subject"] = betreff
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=CID_DOMAIN)
    msg["X-Unsent"] = "1"          # klassisches Outlook: als neue Nachricht öffnen
    msg["X-Priority"] = "3"
    msg["MIME-Version"] = "1.0"
    if anhaenge:
        msg["Content-Type"] = "multipart/mixed"
        msg.attach(inhalt)
        for a in anhaenge:
            typ = mimetypes.guess_type(a.name)[0] or "application/octet-stream"
            maintype, subtype = typ.split("/", 1)
            anhang = teil()
            anhang.set_content(a.read_bytes(), maintype=maintype, subtype=subtype, cte="base64",
                               disposition="attachment", filename=a.name, params={"name": a.name})
            msg.attach(anhang)
    else:
        msg["Content-Type"] = str(inhalt["Content-Type"])
        for p in inhalt.iter_parts():
            msg.attach(p)
    return msg.as_bytes(policy=policy.SMTP)


def eml_pruefen(daten: bytes, bilder: list, anhaenge: list) -> list[str]:
    """Liest die fertige .eml zurück und prüft die Struktur, die Outlook braucht.
    Gibt eine Liste von Fehlern zurück (leer = in Ordnung)."""
    fehler: list[str] = []
    msg = BytesParser(policy=policy.default).parsebytes(daten)
    ebene1 = msg
    if anhaenge:
        if msg.get_content_type() != "multipart/mixed":
            fehler.append(f"oberste Ebene ist {msg.get_content_type()}, erwartet multipart/mixed")
            return fehler
        teile = list(msg.iter_parts())
        ebene1 = teile[0] if teile else msg
        gefunden = {t.get_filename(): len(t.get_payload(decode=True) or b"")
                    for t in teile[1:] if t.get_content_disposition() == "attachment"}
        for a in anhaenge:
            if gefunden.get(a.name) != a.stat().st_size:
                fehler.append(f"Anhang fehlt oder ist unvollständig: {a.name}")
        if len(teile) - 1 != len(anhaenge):
            fehler.append(f"{len(teile) - 1} Anhangsteile, erwartet {len(anhaenge)}")
    if bilder:
        if ebene1.get_content_type() != "multipart/related" \
                or ebene1.get_param("type") != "multipart/alternative":
            fehler.append("Bilder liegen nicht in multipart/related; type=\"multipart/alternative\"")
            return fehler
        teile = list(ebene1.iter_parts())
        alternative = teile[0] if teile else ebene1
        bildteile = teile[1:]
    else:
        alternative, bildteile = ebene1, []
    if alternative.get_content_type() != "multipart/alternative":
        fehler.append(f"Textteil ist {alternative.get_content_type()}, erwartet multipart/alternative")
        return fehler
    typen = [t.get_content_type() for t in alternative.iter_parts()]
    if typen != ["text/plain", "text/html"]:
        fehler.append(f"multipart/alternative enthält {typen}, erwartet text/plain + text/html")
        return fehler
    html = list(alternative.iter_parts())[1].get_content()
    ohne_kommentare = re.sub(r"<!--[\s\S]*?-->", "", html)   # Outlook zählt Verweise in Kommentaren nicht
    verweise = set(re.findall(r'src="cid:([^"]+)"', ohne_kommentare))
    for t in bildteile:
        cid = (t.get("Content-ID") or "").strip("<>")
        if t.get_content_disposition() != "inline":
            fehler.append(f"Bild {t.get_filename()} ist nicht inline")
        if cid not in verweise:
            fehler.append(f"Bild {t.get_filename()} wird im HTML nicht verwendet → erschiene als Anhang")
        verweise.discard(cid)
    for cid in sorted(verweise):
        fehler.append(f"HTML verweist auf fehlendes Bild cid:{cid}")
    if "Message-ID" not in msg or msg.get("X-Unsent") != "1":
        fehler.append("Message-ID oder X-Unsent fehlt (Outlook öffnet die Datei sonst nicht als Entwurf)")
    return fehler


# --------------------------------------------------------------- Varianten
BLOCK_RE = re.compile(r"<!--\[wenn ([\w,\- ]+)\]-->([\s\S]*?)<!--\[/wenn\]-->")
SCHLUESSEL_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def lade_varianten(ordner: Path, auswahl: str | None) -> list[dict]:
    dateien = sorted(ordner.glob("*.json")) if ordner.exists() else []
    if not dateien:
        sys.exit("FEHLER: keine Varianten gefunden – varianten/<name>.json anlegen (siehe README).")
    varianten = []
    for d in dateien:
        v = json.loads(d.read_text(encoding="utf-8"))
        v.setdefault("ausgabe", d.stem)
        varianten.append(v)
    if auswahl:
        varianten = [v for v in varianten if v["ausgabe"] == auswahl]
        if not varianten:
            sys.exit(f"FEHLER: Variante {auswahl!r} nicht gefunden. Vorhanden: "
                     + ", ".join(d.stem for d in dateien))
    return varianten


def variante_anwenden(html: str, v: dict) -> str:
    """Behält nur die Blöcke der Variante und setzt {{SCHLÜSSEL}} aus der JSON ein."""
    kennung = v["ausgabe"]

    def block(m):
        namen = {n.strip() for n in m.group(1).split(",")}
        return m.group(2) if kennung in namen else ""

    html = BLOCK_RE.sub(block, html)
    fehlend = set()

    def ersetze(m):
        k = m.group(1)
        wert = v.get(k, v.get(k.lower()))
        if isinstance(wert, str):
            return wert
        fehlend.add(k)
        return m.group(0)

    html = SCHLUESSEL_RE.sub(ersetze, html)
    if fehlend:
        sys.exit(f"FEHLER: Variante {kennung}: in varianten/{kennung}.json fehlen die Werte "
                 + ", ".join(sorted(fehlend)))
    return html


def anhaenge_sammeln(v: dict, anhang_dir: Path, hinweise: list) -> list:
    """Merkblatt der Variante + anhang/alle/ + anhang/<variante>/ (+ lose Dateien in anhang/)."""
    liste = []
    if v.get("merkblatt"):
        mb = ROOT / "merkblatt" / v["merkblatt"]
        if mb.exists():
            liste.append(mb)
        else:
            hinweise.append(f"{v['ausgabe']}: Merkblatt fehlt ({mb.name}) – node tools/build_merkblatt.js ausführen.")
    for ordner in (anhang_dir / "alle", anhang_dir / v["ausgabe"], anhang_dir):
        if ordner.exists():
            liste += sorted(p for p in ordner.iterdir()
                            if p.is_file() and p.name.lower() != "readme.md" and not p.name.startswith("."))
    return liste


# -------------------------------------------------------------------- Main
def main() -> int:
    ap = argparse.ArgumentParser(description="Newsletter je Variante bauen (Vorschau, .eml, .txt)")
    ap.add_argument("--quelle", default="newsletter.html", help="Quelldatei (Standard: newsletter.html)")
    ap.add_argument("--theme", default="bw-theme.css", help="Design-System (Standard: bw-theme.css)")
    ap.add_argument("--varianten", default="varianten", help="Ordner mit Varianten-JSON (Standard: varianten/)")
    ap.add_argument("--variante", help="nur diese Variante bauen (Standard: alle)")
    ap.add_argument("--anhang", default="anhang", help="Ordner mit Anhängen (Standard: anhang/)")
    ap.add_argument("--out", default="dist", help="Zielordner (Standard: dist/, je Variante ein Unterordner)")
    ap.add_argument("--betreff", help="Betreff für alle Varianten (Standard: betreff aus der JSON, sonst <title>)")
    ap.add_argument("--absender", default=None,
                    help="Absender eintragen (Standard: keiner – Outlook nimmt das eigene Konto; "
                         "ein Funktionspostfach braucht die Exchange-Berechtigung „Senden als“)")
    ap.add_argument("--antwort-an", default=ANTWORT_AN,
                    help="Reply-To, damit Antworten am Funktionspostfach landen (Standard: Ausbildungsberatung)")
    ap.add_argument("--streng", action="store_true",
                    help="Abbruch mit Fehler bei offenen Platzhaltern oder fehlendem Logo")
    args = ap.parse_args()

    quelle = ROOT / args.quelle
    theme = ROOT / args.theme
    if not quelle.exists():
        sys.exit(f"FEHLER: {args.quelle} nicht gefunden.")
    if not theme.exists():
        sys.exit(f"FEHLER: {args.theme} nicht gefunden.")

    tokens = lade_tokens(theme)
    vorlage = quelle.read_text(encoding="utf-8")
    varianten = lade_varianten(ROOT / args.varianten, args.variante)
    print(f"Absender: {args.absender or 'eigenes Outlook-Konto (kein From in der .eml)'}")
    print(f"Antworten an: {args.antwort_an or '–'}")
    ernst = False

    for v in varianten:
        hinweise: list[str] = []
        html = variante_anwenden(vorlage, v)
        html = tokens_einsetzen(html, tokens)
        html = kommentare_entfernen(html)
        if re.search(r"var\(\s*--", html):
            sys.exit("FEHLER: Es sind noch var(--…)-Verweise übrig.")
        if re.search(r'<img\b[^>]*\bsrc\s*=\s*"https?://', html, re.I):
            sys.exit("FEHLER: externes Bild im Newsletter – Bilder gehören nach assets/ und werden eingebettet.")

        html_vorschau, html_mail, bilder = bilder_verarbeiten(html, tokens, hinweise)
        text = textfassung(html_mail)
        platzhalter = sorted(set(re.findall(r"\[[^\[\]\n]{2,90}\]", text)))
        if platzhalter:
            hinweise.append("Offene Platzhalter (vor dem Versand ersetzen): " + ", ".join(platzhalter))

        betreff = args.betreff or v.get("betreff")
        if not betreff:
            m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
            betreff = re.sub(r"\s+", " ", m.group(1)).strip() if m else "Ausbilder-Info Grüne Berufe"
        anhaenge = anhaenge_sammeln(v, ROOT / args.anhang, hinweise)

        out = ROOT / args.out / v["ausgabe"]
        out.mkdir(parents=True, exist_ok=True)
        name = re.sub(r"[^\w.-]+", "-", v.get("dateiname") or f"ausbilder-info-{v['ausgabe']}")
        for alt in out.glob("*"):          # alte Ausgaben der Variante wegräumen
            if alt.is_file() and alt.suffix in (".eml", ".html", ".txt"):
                alt.unlink()
        (out / f"{name}.html").write_text(html_vorschau, encoding="utf-8")
        (out / f"{name}.txt").write_text(text, encoding="utf-8")
        eml = eml_bauen(html_mail, text, bilder, anhaenge, betreff, args.absender, args.antwort_an)
        probleme = eml_pruefen(eml, bilder, anhaenge)
        if probleme:
            sys.exit(f"FEHLER: {name}.eml hat nicht die Struktur, die Outlook braucht:\n  - "
                     + "\n  - ".join(probleme))
        (out / f"{name}.eml").write_bytes(eml)

        kb = lambda p: (out / p).stat().st_size / 1024
        rel = out.relative_to(ROOT)
        print(f"\n== Variante {v['ausgabe']}: {v.get('name', '')}")
        print(f"Betreff : {betreff}")
        print(f"OK  -> {rel}/{name}.html  ({kb(name + '.html'):.0f} KB)  Vorschau im Browser")
        print(f"OK  -> {rel}/{name}.eml   ({kb(name + '.eml'):.0f} KB)  "
              f"{len(bilder)} Bild(er) eingebettet ({sum(len(b.daten) for b in bilder) / 1024:.0f} KB), "
              f"{len(anhaenge)} Anhang/Anhänge")
        for a in anhaenge:
            print(f"         + {a.name} ({a.stat().st_size / 1024:.0f} KB)")
        print(f"OK  -> {rel}/{name}.txt   Nur-Text-Fassung")
        mail_kb = len(html_mail.encode("utf-8")) / 1024
        if mail_kb > GMAIL_GRENZE_KB:
            hinweise.append(f"HTML der E-Mail ist {mail_kb:.0f} KB – Gmail kürzt Nachrichten über ~102 KB.")
        bild_kb = sum(len(b.daten) for b in bilder) / 1024
        if bild_kb > 1024:
            hinweise.append(f"Eingebettete Bilder: {bild_kb:.0f} KB – Fotos kleiner zuschneiden oder stärker komprimieren.")
        if not any(a.parent.name in ("alle", v["ausgabe"]) for a in anhaenge):
            hinweise.append(f"Keine Dateien in anhang/alle/ oder anhang/{v['ausgabe']}/ – Leitfaden und Azubi-Info dort ablegen.")
        if hinweise:
            print("Hinweise:")
            for h in hinweise:
                print("  • " + h)
        ernst = ernst or bool(platzhalter) or any(h.startswith("Bild fehlt") for h in hinweise)

    if args.streng and ernst:
        print("\nAbbruch (--streng): Platzhalter ersetzen bzw. Logo ablegen und erneut bauen.")
        return 1
    print("\nVersand: die .eml der Variante in Outlook öffnen, Empfänger in Bcc eintragen, senden (siehe README).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
