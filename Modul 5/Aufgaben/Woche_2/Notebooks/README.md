# Woche 2 – Tag 4: Reproduzierbare Datenpipeline

## Ziel
Automatische Bereinigung der April-Bestellungen.

## Bereinigungsschritte
1. Rohdaten einlesen: 80 Zeilen
2. Vollständige Duplikate entfernen: 6 Zeilen
3. Datumsformate vereinheitlichen
4. Preise bereinigen
5. Rabattwerte bereinigen
6. Ländernamen vereinheitlichen
7. März-Bestellungen ausschließen: 3 Zeilen
8. Daten sortieren und exportieren

## Ergebnis
71 bereinigte April-Bestellungen.

## Projektdateien
- clean_bestellungen.py: Python-Skript
- requirements.txt: Pandas-Version
- raw/: Unveränderte Eingangsdaten
- clean/: Bereinigte Ergebnisse

## Ausführung
1. Abhängigkeiten installieren: python -m pip install -r requirements.txt
2. Pipeline starten: python clean_bestellungen.py

## Reproduzierbarkeit
Zwei Durchläufe erzeugten denselben SHA-256-Hash:

44b8afcc667c74a6da5b765b7732ae34d1c518982b5bd8c0a11f5b1d705862f9

## Datenschutz
Die CSV-Dateien enthalten personenbezogene Daten.
Sie dürfen nicht in ein öffentliches GitHub-Repository hochgeladen werden.


## Test im frischen Verzeichnis

Die Pipeline wurde in einem neu erstellten temporären
Projektverzeichnis zweimal ausgeführt.

Beide Durchläufe waren erfolgreich.

SHA-256 Durchlauf 1:
44b8afcc667c74a6da5b765b7732ae34d1c518982b5bd8c0a11f5b1d705862f9

SHA-256 Durchlauf 2:
44b8afcc667c74a6da5b765b7732ae34d1c518982b5bd8c0a11f5b1d705862f9

Ergebnis: Beide Ausgabedateien sind bytegenau identisch.

Hinweis: Der Test verwendete die bereits installierte
Python-Umgebung.
