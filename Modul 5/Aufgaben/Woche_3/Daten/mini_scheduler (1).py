"""Mini-Scheduler — Übungsgerüst zu Tag 13 (Trigger & Scheduling).

Ein Scheduler in 30 Zeilen: eine Endlosschleife, die eure Pipeline
regelmäßig startet und jeden Lauf protokolliert.

ACHTUNG — nur zum Lernen: Dieses Skript zeigt, WAS ein Scheduler tut.
Im echten Betrieb übernimmt cron (oder ein Orchestrator) das Timing —
warum, steht in der Vorlesung (die vier Fallen).

Aufgabe: die vier TODOs vervollständigen, dann starten mit
    python3 mini_scheduler.py
und nach mindestens 3 Läufen mit Strg+C stoppen.
"""

import time
from datetime import datetime
from pathlib import Path

INTERVALL_SEKUNDEN = 10          # didaktisch kurz — cron kann frühestens 1×/Minute
PROTOKOLL = Path("mini_protokoll.csv")


def pipeline_lauf() -> int:
    """Simulierter Pipeline-Lauf (gestern: der Ingest aus der Mock-API).

    Gibt die Zahl der 'geholten Zeilen' zurück.
    """
    # TODO 1: Simuliert hier einen Lauf — z. B. 2 Sekunden "Arbeit"
    #         (time.sleep) und ein fester Rückgabewert genügt.
    ...


def protokolliere(start: datetime, ende: datetime, zeilen: int) -> None:
    """Hängt eine Zeile an das Lauf-Protokoll an."""
    # TODO 2: Zeile "start;ende;zeilen" an PROTOKOLL anhängen.
    #         Falls die Datei noch nicht existiert: erst die Header-Zeile
    #         "start;ende;zeilen" schreiben.
    ...


def main() -> None:
    print("Mini-Scheduler gestartet — Stoppen mit Strg+C")
    while True:
        start = datetime.now()
        # TODO 3: Lauf ausführen, Ende-Zeitpunkt nehmen, protokollieren
        #         und eine Statuszeile drucken, z. B.:
        #         [07:32:10] Lauf ok — 42 Zeilen (2 s)
        ...

        # TODO 4: Bis zum nächsten Lauf warten.
        #         Bonus-Frage für die Reflexion in der Tagesaufgabe:
        #         Warum verschiebt sich der Startzeitpunkt mit
        #         time.sleep(INTERVALL_SEKUNDEN) langsam nach hinten —
        #         und warum passiert cron das nicht?
        time.sleep(INTERVALL_SEKUNDEN)


if __name__ == "__main__":
    main()
