from pathlib import Path
import pandas as pd

# Projektverzeichnis automatisch ermitteln
BASE_DIR = Path(__file__).resolve().parent

# Eingabe- und Ausgabedateien
RAW_DATEI = BASE_DIR / "raw" / "bestellungen_april_roh.csv"
CLEAN_DATEI = BASE_DIR / "clean" / "bestellungen_april_clean.csv"

# Fester Berichtszeitraum
STARTDATUM = pd.Timestamp("2026-04-01")
ENDDATUM = pd.Timestamp("2026-05-01")


def main():
    print("Starte Bereinigung der April-Bestellungen ...")

    # Rohdaten einlesen
    df = pd.read_csv(RAW_DATEI)

    print(f"Eingelesene Bestellungen: {len(df)}")

    # Vollständig identische Bestellungen entfernen
    df = df.drop_duplicates().copy()

    print(f"Bestellungen nach Duplikatbereinigung: {len(df)}")

    # Unterschiedliche Datumsformate vereinheitlichen
    datum_iso = pd.to_datetime(
        df["datum"], format="%Y-%m-%d", errors="coerce"
    )

    datum_de = pd.to_datetime(
        df["datum"], format="%d.%m.%Y", errors="coerce"
    )

    df["datum_parsed"] = datum_iso.fillna(datum_de)

    # Ungültige Datumswerte erkennen
    assert df["datum_parsed"].notna().all(), "Ungültige Datumswerte!"

    print(f"Erfolgreich erkannte Datumswerte: {df['datum_parsed'].notna().sum()}")

    # Preisformate vereinheitlichen
    df["preis_eur"] = pd.to_numeric(
        df["preis_eur"]
        .astype("string")
        .str.replace(",", ".", regex=False),
        errors="raise"
    )

    # Qualitätskontrolle
    assert df["preis_eur"].notna().all(), "Fehlende Preise!"

    print(f"Erfolgreich bereinigte Preise: {df['preis_eur'].notna().sum()}")

    # Rabattwerte vereinheitlichen
    df["rabatt_pct"] = pd.to_numeric(
        df["rabatt_pct"]
        .astype("string")
        .str.replace("%", "", regex=False)
        .str.strip(),
        errors="raise"
    )

    # Qualitätskontrolle
    assert df["rabatt_pct"].notna().all(), "Fehlende Rabatte!"
    assert df["rabatt_pct"].between(0, 100).all(), "Ungültige Rabatte!"

    print(f"Erfolgreich bereinigte Rabatte: {df['rabatt_pct'].notna().sum()}")

    # Ländernamen vereinheitlichen
    laender_mapping = {
        "DE": "DE",
        "de": "DE",
        "Deutschland": "DE",
        "AT": "AT",
        "Österreich": "AT"
    }

    df["land"] = df["land"].map(laender_mapping)

    # Qualitätskontrolle
    assert df["land"].notna().all(), "Unbekannte Länderwerte!"
    assert df["land"].isin(["DE", "AT"]).all(), "Ungültige Ländercodes!"

    print(f"Erfolgreich bereinigte Länder: {df['land'].notna().sum()}")

    # Festen April-Zeitraum anwenden
    vorher = len(df)

    df = df[
        (df["datum_parsed"] >= STARTDATUM) &
        (df["datum_parsed"] < ENDDATUM)
    ].copy()

    print(f"Bestellungen außerhalb April: {vorher - len(df)}")
    print(f"Bereinigte April-Bestellungen: {len(df)}")

    # Qualitätskontrolle
    assert len(df) == 71, "Unerwartete Anzahl an April-Bestellungen!"
    assert df["datum_parsed"].between(
        STARTDATUM, ENDDATUM, inclusive="left"
    ).all(), "Bestellungen außerhalb des Berichtszeitraums!"

    # Feste Sortierung für reproduzierbaren Export
    df = df.sort_values("bestell_id").reset_index(drop=True)

    # Datum einheitlich als YYYY-MM-DD speichern
    df["datum"] = df["datum_parsed"].dt.strftime("%Y-%m-%d")
    df = df.drop(columns=["datum_parsed"])

    # Bereinigte CSV speichern
    CLEAN_DATEI.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(
        CLEAN_DATEI,
        index=False,
        encoding="utf-8",
        float_format="%.2f",
        lineterminator="\n"
    )

    print(f"CSV erfolgreich gespeichert: {CLEAN_DATEI}")
    print(f"Exportierte Bestellungen: {len(df)}")









if __name__ == "__main__":
    main()
