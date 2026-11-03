# pipeline.py -- BITTE NICHT ANFASSEN, LÄUFT!!! (Stand: irgendwann März)
# von Alex (Praktikum), Fragen an mich (bin ab 20.03. weg)
# TODO: aufräumen (irgendwann)

import pandas as pd

API_KEY = "sk-live-4711-shop-geheim-XK9"  # für den API-Abruf von Dienstag (falls wir den wieder brauchen)

print("Pipeline startet...")

# ---------------------------------------------------------------
# Tag 1 einlesen und sauber machen
# ---------------------------------------------------------------
df1 = pd.read_csv("bestellungen_2026-03-16.csv")
print("Tag 1 gelesen:", len(df1))
# Stornos will keiner im Report haben (hat Frau Sommer am 17.03. gesagt)
df1 = df1[df1["status"] != "storniert"]
# Preis kommt als Text mit Komma (deutsches Format, wie immer)
df1["preis_eur"] = df1["preis_eur"].str.replace(",", ".", regex=False)
df1["preis_eur"] = df1["preis_eur"].astype(float)
df1["datum"] = pd.to_datetime(df1["datum"])
# Brutto ausrechnen (19% MwSt)
df1["umsatz_brutto"] = df1["menge"] * df1["preis_eur"] * (1 + 0.19)

# ---------------------------------------------------------------
# Tag 2 einlesen und sauber machen (kopiert von oben, geht ja schnell)
# ---------------------------------------------------------------
data2 = pd.read_csv("bestellungen_2026-03-17.csv")
print("Tag 2 gelesen:", len(data2))
# Stornos raus, siehe oben
data2 = data2[data2["status"] != "storniert"]
data2["preis_eur"] = data2["preis_eur"].str.replace(",", ".", regex=False)
data2["preis_eur"] = data2["preis_eur"].astype(float)
data2["datum"] = pd.to_datetime(data2["datum"])
data2["umsatz_brutto"] = data2["menge"] * data2["preis_eur"] * (1 + 0.19)

# ---------------------------------------------------------------
# Tag 3 (auch kopiert, diesmal von Tag 2)
# ---------------------------------------------------------------
import pandas as pd  # sicher ist sicher

tabelle3 = pd.read_csv("bestellungen_2026-03-18.csv")
print("Tag 3 gelesen:", len(tabelle3))
tabelle3 = tabelle3[tabelle3["status"] != "storniert"]
tabelle3["preis_eur"] = tabelle3["preis_eur"].str.replace(",", ".", regex=False)
tabelle3["preis_eur"] = tabelle3["preis_eur"].astype(float)
tabelle3["datum"] = pd.to_datetime(tabelle3["datum"])
tabelle3["umsatz_brutto"] = tabelle3["menge"] * tabelle3["preis_eur"] * (1 + 0.19)

# ---------------------------------------------------------------
# hier war mal der API-Abruf von Dienstag, geht gerade nicht,
# aber NICHT löschen, vielleicht brauchen wir das nochmal:
# ---------------------------------------------------------------
# import requests
# antwort = requests.get(
#     "https://shop.example.com/api/bestellungen",
#     headers={"Authorization": "Bearer " + API_KEY},
#     timeout=10,
# )
# df_api = pd.DataFrame(antwort.json()["bestellungen"])
# df_api.to_csv("/Users/alex/Desktop/shop_projekt/api_dump_NEU_final2.csv")

# ---------------------------------------------------------------
# alles zusammenwerfen
# ---------------------------------------------------------------
alles = pd.concat([df1, data2, tabelle3], ignore_index=True)
print("zusammen:", len(alles))

# Die Export-Fenster überlappen sich (kam Mittwoch raus), deshalb
# tauchen manche Bestellungen doppelt auf -> Duplikate raus.
# (Donnerstag gelernt: sonst zählt der Report Umsatz doppelt!)
final_df = alles.drop_duplicates(subset=["bestell_id"], keep="first")
final_df = final_df.sort_values("bestell_id").reset_index(drop=True)
print("nach Duplikat-Check:", len(final_df))

# ---------------------------------------------------------------
# Ergebnis speichern
# ---------------------------------------------------------------
final_df.to_parquet("bestellungen_woche.parquet")

# Zusammenfassung für Frau Sommer (die öffnet nur Excel)
zusammenfassung = final_df.groupby("land", as_index=False)["umsatz_brutto"].sum()
zusammenfassung["umsatz_brutto"] = zusammenfassung["umsatz_brutto"].round(2)
zusammenfassung.to_csv("zusammenfassung.csv", index=False)

# ---------------------------------------------------------------
# Tagesumsätze fürs Daily (Wunsch von Herrn Brandt, 18.03.)
# ---------------------------------------------------------------
t1 = final_df[final_df["datum"] == "2026-03-16"]
print("Umsatz 16.03.:", round(t1["umsatz_brutto"].sum(), 2), "EUR")
t2 = final_df[final_df["datum"] == "2026-03-17"]
print("Umsatz 17.03.:", round(t2["umsatz_brutto"].sum(), 2), "EUR")
t3 = final_df[final_df["datum"] == "2026-03-18"]
print("Umsatz 18.03.:", round(t3["umsatz_brutto"].sum(), 2), "EUR")

# ---------------------------------------------------------------
# Top-Produkte für DE (wollte Marketing am 18.03. haben)
# ---------------------------------------------------------------
nur_de = final_df[final_df["land"] == "DE"]
top_de = nur_de.groupby("produkt", as_index=False)["umsatz_brutto"].sum()
top_de = top_de.sort_values("umsatz_brutto", ascending=False)
top_de["umsatz_brutto"] = top_de["umsatz_brutto"].round(2)
top_de.to_csv("top_produkte_DE.csv", index=False)
print("Top-Produkt DE:", top_de.iloc[0]["produkt"])

# ---------------------------------------------------------------
# Top-Produkte für AT (kopiert vom DE-Block, nur Land getauscht)
# ---------------------------------------------------------------
nur_at = final_df[final_df["land"] == "AT"]
top_at = nur_at.groupby("produkt", as_index=False)["umsatz_brutto"].sum()
top_at = top_at.sort_values("umsatz_brutto", ascending=False)
top_at["umsatz_brutto"] = top_at["umsatz_brutto"].round(2)
top_at.to_csv("top_produkte_AT.csv", index=False)
print("Top-Produkt AT:", top_at.iloc[0]["produkt"])

# ---------------------------------------------------------------
# Abschluss-Zahlen (die will Frau Sommer montags als Erstes sehen)
# ---------------------------------------------------------------
ergebnis = final_df["umsatz_brutto"].sum()
print("Umsatz brutto gesamt:", round(ergebnis, 2), "EUR")
# nochmal netto, falls jemand fragt (Netto = ohne die 19%)
print("Umsatz netto gesamt:", round(ergebnis / (1 + 0.19), 2), "EUR")

print("Fertig! Dateien: bestellungen_woche.parquet, zusammenfassung.csv, top_produkte_DE.csv, top_produkte_AT.csv")
