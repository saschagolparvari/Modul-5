"""Starter-Skelett Tagesaufgabe W3/T1: eure erste Pipeline.

Drei Schritte, drei Verträge — ihr füllt die Funktionskörper:

    ingest → clean → store

Jeder Schritt liest genau EINEN definierten Input und schreibt genau
EIN definiertes Artefakt (siehe Konstanten unten). Der Rahmen (main,
Schritt-Auswahl) steht schon — NICHT umbauen, nur die drei TODO-Blöcke füllen.

Aufruf:  python pipeline.py all       (ganze Strecke)
         python pipeline.py ingest    (einzelner Schritt)
         python pipeline.py clean
         python pipeline.py store
"""
from pathlib import Path
import sqlite3
import sys

import pandas as pd

ROHDATEI = Path("bestellungen_april_roh.csv")
ARTEFAKTE = Path("artefakte")
INGEST_ARTEFAKT = ARTEFAKTE / "01_ingest.parquet"
CLEAN_ARTEFAKT = ARTEFAKTE / "02_clean.parquet"
DB_ARTEFAKT = ARTEFAKTE / "shop.db"


def ingest() -> Path:
    """Vertrag: liest ROHDATEI und liefert sie unverändert als INGEST_ARTEFAKT.

    TODO:
      1. CSV laden (sie lädt naiv sauber — die Mängel stecken in den Werten).
      2. ARTEFAKTE-Ordner anlegen (`ARTEFAKTE.mkdir(exist_ok=True)`).
      3. Als Parquet nach INGEST_ARTEFAKT schreiben.
      4. Protokollzeile drucken: Quelle, Ziel, Zeilenzahl.
    """
    ARTEFAKTE.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(ROHDATEI)

    df.to_parquet(INGEST_ARTEFAKT, index=False)

    print(f"Quelle: {ROHDATEI}")
    print(f"Ziel: {INGEST_ARTEFAKT}")
    print(f"Zeilenanzahl: {len(df)}")

    return INGEST_ARTEFAKT


def clean() -> Path:
    """Vertrag: liest INGEST_ARTEFAKT, wendet eure Bereinigungsregeln an
    und liefert den sauberen Stand als CLEAN_ARTEFAKT.

    TODO — die Regeln kennt ihr aus Woche 1/2:
      1. Exakte Dubletten entfernen (erst zählen!).
      2. Gemischte Datumsformate explizit parsen (kein stiller Dreher!).
      3. Preise mit Dezimalkomma → float.
      4. Land-Schreibweisen per Mapping-Tabelle normalisieren.
      5. Fehlende E-Mails: Entscheidung treffen + im Protokoll dokumentieren.
      6. Vertrag prüfen (asserts: kein NaT, nur April, kein unbekanntes Land),
         DANN als Parquet nach CLEAN_ARTEFAKT schreiben + Protokollzeile drucken.
    """
    df = pd.read_parquet(INGEST_ARTEFAKT)

    zeilen_vorher = len(df)

    df = df.drop_duplicates().copy()

    print("=== DUPLIKATBEREINIGUNG ===")
    print("Vorher:", zeilen_vorher)
    print("Nachher:", len(df))
    print("Entfernt:", zeilen_vorher - len(df))
    # Gemischte Datumsformate erkennen
    iso = df["datum"].str.fullmatch(r"\d{4}-\d{2}-\d{2}")
    de = df["datum"].str.fullmatch(r"\d{2}\.\d{2}\.\d{4}")

    # Neue Datumsspalte vorbereiten
    datum_neu = pd.Series(
        pd.NaT, index=df.index, dtype="datetime64[ns]"
    )

    # ISO-Format verarbeiten
    datum_neu.loc[iso] = pd.to_datetime(
        df.loc[iso, "datum"],
        format="%Y-%m-%d"
    )

    # Deutsches Format verarbeiten
    datum_neu.loc[de] = pd.to_datetime(
        df.loc[de, "datum"],
        format="%d.%m.%Y"
    )

    # Bereinigte Datumswerte übernehmen
    df["datum"] = datum_neu 

    print("Fehlerhafte Datumswerte:", df["datum"].isna().sum())
    print("Frühestes Datum:", df["datum"].min())
    print("Spätestes Datum:", df["datum"].max())
    # Preise von Text in Dezimalzahlen umwandeln
    df["preis_eur"] = (
        df["preis_eur"]
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    print("=== PREISBEREINIGUNG ===")
    print("Datentyp:", df["preis_eur"].dtype)
    print("Fehlende Preise:", df["preis_eur"].isna().sum())
    # Länderbezeichnungen vereinheitlichen
    land_mapping = {
        "DE": "DE",
        "de": "DE",
        "Deutschland": "DE",
        "AT": "AT",
        "at": "AT",
        "Österreich": "AT"
    }

    df["land"] = df["land"].map(land_mapping)

    print("=== LÄNDERBEREINIGUNG ===")
    print(df["land"].value_counts())
    print("Unbekannte Länder:", df["land"].isna().sum())
    # Fehlende E-Mail-Adressen bewusst beibehalten
    # Begründung: Die Bestellungen sind ansonsten vollständig.
    # Keine erfundenen E-Mail-Adressen und kein Datenverlust.

    fehlende_emails = df["kunde_email"].isna().sum()

    print("=== E-MAIL-PRÜFUNG ===")
    print("Fehlende E-Mail-Adressen:", fehlende_emails)
    print("Entscheidung: Bestellungen bleiben erhalten.")
    # Abschließende Qualitätsprüfungen
    assert df["datum"].notna().all(), \
        "Fehler: Ungültige Datumswerte vorhanden!"

    assert df["datum"].between(
        pd.Timestamp("2026-04-01"),
        pd.Timestamp("2026-04-30")
    ).all(), "Fehler: Bestellung außerhalb April 2026!"

    assert df["land"].isin(["DE", "AT"]).all(), \
        "Fehler: Unbekannter Ländercode vorhanden!"

    print("=== QUALITÄTSPRÜFUNG ===")
    print("Alle drei Prüfungen bestanden!")
    # Bereinigte Bestellungen als Parquet speichern
    df.to_parquet(CLEAN_ARTEFAKT, index=False)

    print("=== CLEAN ABGESCHLOSSEN ===")
    print("Gespeicherte Bestellungen:", len(df))
    print("Zieldatei:", CLEAN_ARTEFAKT)

    return CLEAN_ARTEFAKT


def store() -> Path:
    """Vertrag: liest CLEAN_ARTEFAKT und schreibt die Tabelle `bestellungen`
    in die SQLite-Datenbank DB_ARTEFAKT.

    TODO:
      1. Clean-Artefakt laden.
      2. Mit `sqlite3.connect(DB_ARTEFAKT)` verbinden und per
         `df.to_sql("bestellungen", con, if_exists="replace", index=False)` schreiben.
      3. Kontrollabfrage: `SELECT COUNT(*) FROM bestellungen` — stimmt die Zeilenzahl?
      4. Protokollzeile drucken, Verbindung schließen.
    """
        # Bereinigte Daten laden
    df = pd.read_parquet(CLEAN_ARTEFAKT)

    # Verbindung zur SQLite-Datenbank herstellen
    con = sqlite3.connect(DB_ARTEFAKT)

    try:
        # Daten in die Tabelle "bestellungen" schreiben
        df.to_sql(
            "bestellungen",
            con,
            if_exists="replace",
            index=False
        )

        # Gespeicherte Zeilen in SQLite überprüfen
        anzahl_db = con.execute(
            "SELECT COUNT(*) FROM bestellungen"
        ).fetchone()[0]

        assert anzahl_db == len(df), \
            "Fehler: Zeilenanzahl in SQLite stimmt nicht!"

    finally:
        # Datenbankverbindung schließen
        con.close()

    print("=== STORE ABGESCHLOSSEN ===")
    print("Quelle:", CLEAN_ARTEFAKT)
    print("Datenbank:", DB_ARTEFAKT)
    print("Gespeicherte Bestellungen:", anzahl_db)

    return DB_ARTEFAKT


SCHRITTE = {"ingest": ingest, "clean": clean, "store": store}


def main() -> None:
    auswahl = sys.argv[1] if len(sys.argv) > 1 else "all"

    if auswahl == "all":
        for schritt in SCHRITTE.values():
            schritt()
        print(f"[lauf] ok - alle Artefakte in {ARTEFAKTE}/")

    elif auswahl in SCHRITTE:
        SCHRITTE[auswahl]()

    else:
        sys.exit(f"Unbekannter Schritt: {auswahl!r}")


if __name__ == "__main__":
    main()
