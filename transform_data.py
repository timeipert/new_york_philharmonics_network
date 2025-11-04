import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import json
    import pandas as pd
    import glob
    from typing import List, Dict, Any, Union


    return json, pd


@app.cell
def _(mo):
    mo.md(r"""
    ## Laden

    * Dieser Prozess ist dafür verantwortlich, die Rohdaten aus den externen Dateien in den Arbeitsspeicher zu bringen.
    * Das Ziel ist, Zugriff auf alle Programminformationen erhalten. Jede gefundene JSON-Datei wird einzeln mit der json-Bibliothek eingelesen und in ein Python-Dictionary umgewandelt.
    * Das Ergebnis ist eine einzige, große Liste von Objekten, wobei jedes Objekt ein Konzertprogramm ("program") repräsentiert.
    """)
    return


@app.cell
def _(mo):
    file_picker = mo.ui.file(multiple=False
    )

    marimo_file = file_picker
    file_picker
    return file_picker, marimo_file


@app.cell
def _():
    return


@app.cell
def _(file_picker, json, marimo_file):
    if file_picker.value:
        mo_file = marimo_file.value[0]
        print(mo_file)
    
    
        all_programs = []
    
        try:
            file_content = mo_file.contents.decode('utf-8')
            data = json.loads(file_content)
    
            if 'programs' in data:
                all_programs.extend(data['programs'])
            else:
                all_programs.extend(data)
            
        except json.JSONDecodeError:
            print(f"Fehler: Ungültiges JSON-Format in der Datei .")
        except Exception as e:
            print(f"Fehler beim Verarbeiten der Datei {e}")
            
        print(all_programs)
    return (all_programs,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Extraktion
    ### Definition der Akteure (Knoten):

    * Alle Solisten (soloistName) werden als potenzielle Kollaborationspartner identifiziert.

    ### Definition der Kanten (Kollaboration):

    * Für jedes Werk in einem Programm werden alle beteiligten Akteure in eine temporäre Liste (all_artists) zusammengefasst.

    * Es wird angenommen, dass jeder Akteur mit jedem anderen Akteur in dieser Liste kollaboriert hat.

    * Es werden Kanten zwischen allen Paaren (Source und Target) in dieser Gruppe generiert, wobei eine temporale Komponente (Date des Konzerts) hinzugefügt wird.

    Ergebnis: Eine lange, unbereinigte Kantenliste (Source, Target, Date, WorkID).
    """)
    return


@app.cell
def _(all_programs, pd):
    """
    Extrahiert Kollaborationen (Kanten) zwischen Dirigenten und Solisten pro Werk.

    Args:
        programs: Eine Liste von Programm-Dictionaries aus den NYP-Daten.
    
    Returns:
        Ein Pandas DataFrame, das die Kantenliste (Source, Target, Date) darstellt.
    """

    edges = []

    for program in all_programs:
        concert_date = None
        if program.get('concerts') and program['concerts'][0].get('Date'):
            concert_date = program['concerts'][0]['Date'].split('T')[0]

        for work in program.get('works', []):
            if work.get('interval') == "Intermission" or not concert_date:
                continue

            soloists = [s['soloistName'] for s in work.get('soloists', []) if s.get('soloistName')]
            for i in range(len(soloists)):
                source = soloists[i].strip()
                for j in range(i + 1, len(soloists)):
                    target = soloists[j].strip()
                
                    if source and target and source != target:
                        edges.append({
                            'Source': source,
                            'Target': target,
                            'Date': concert_date,
                            'WorkID': work.get('ID', 'N/A')
                        })
                    
    df = pd.DataFrame(edges)
    df




    return (df,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Aggregation
    Der letzte Schritt berechnet die Stärke der Kollaborationen, indem die einzelnen Kanten gezählt werden.

    * Ziel: Die Häufigkeit der gemeinsamen Auftritte als Kantengewicht (Weight) zu bestimmen.

    * Methode: Gruppierung des DataFrames nach den Spalten Source und Target (den beiden Kollaborationspartnern).

    * Aktion: Die Anzahl der Zeilen innerhalb jeder Gruppe wird gezählt (mit groupby().size()).

    * Ergebnis: Die finale Kantenliste als Pandas DataFrame im Format: Source | Target | Weight.

    Dieses Format ist fertig für die Visualisierung und Analyse in Tools wie Gephi oder NetworkX.
    """)
    return


@app.cell
def _(df):
    # 3. Aggregation (Zählen der Häufigkeit pro Kollaboration/Kante)
    # Da wir eine temporale Analyse machen wollen, lassen wir das Datum zunächst drin,
    # aber wir können die Gesamtanzahl als "Weight" hinzufügen.
    # Für die Darstellung der Häufigkeit ("wie häufig eine Erwähnung haben")
    df_agg = df.groupby(['Source', 'Target']).size().reset_index(name='Weight')
    df_agg
    return (df_agg,)


@app.cell
def _(df_agg):
    """
    Speichert das DataFrame der Kantenliste in eine CSV-Datei.
    """
    df_agg.to_csv("nyp_collaboration_network.csv", index=False)
    print(f"Kantenliste erfolgreich gespeichert unter: nyp_collaboration_network.csv")

    return


@app.cell
def _(df_agg, mo):
    download_txt = mo.download(
        data=df_agg.to_csv(),
        filename="nyp_network.csv",
        mimetype="text/csv",
    )
    mo.md(f"{download_txt}")
    return


if __name__ == "__main__":
    app.run()
