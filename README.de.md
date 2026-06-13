# OmniFlow

> Windows-Automatisierungswerkzeugkit basierend auf dem MCP (Model Context Protocol)

[English](README.en.md) | [中文](README.md) | [日本語](README.ja.md) | **Deutsch**

OmniFlow kapselt Windows-Desktop-Automatisierungsfunktionen (Fensteroperationen, Bild/Farberkennung, OCR, Tastatur-/Maussimulation, Hintergrundbindung, Speicheroperationen usw.) als standardmäßigen **MCP Server**. Jede AI-Client-Software, die das MCP-Protokoll unterstützt (z. B. Claude Desktop, VS Code, CodeBuddy, Cursor, Windsurf, Continue, Cline, Cody, Crayfish, Hermes, Trae, Kiro usw.), kann direkt auf Windows-Automatisierungsfunktionen zugreifen.

---

## ✨ Funktionen

### 🎯 Anwendungsfälle

OmniFlow verwandelt Windows-Desktop-Anwendungen in „von AI aufrufbare Tools“. Häufige Anwendungsfälle:

- **🎨 Bildverarbeitungsautomatisierung** — Steuerung von Photoshop/AI für Batch-Bildverarbeitung (Größenanpassung, Farbkorrektur, Filter, Batch-Export)
- **📸 Screenshot-Pipeline** — Bildschirmaufnahme → OCR-Textextraktion / PIL-Weiterverarbeitung / Anmerkungen zurück auf den Bildschirm
- **✏️ Zeichnungsautomatisierung** — Erstellung von Diagrammen, Anmerkungen, Flussdiagrammen mit mspaint
- **🎮 Spieleautomatisierung** — Hintergrund-AFK, Autokampf, Dungeon-Aufzeichnung und -Wiedergabe
- **📝 Büroautomatisierung** — WPS/Office-Dokumente automatisch ausfüllen, Berichte generieren, Batch-Formatierung
- **🎬 Videosteuerung** — Player automatisch pausieren/fortsetzen, Untertiterkennung, geplanter Rekord

### 🖥️ Fensteroperationen
- Fenster suchen und auflisten (nach Titel, Klassenname, PID usw.)
- Fensterstatus abrufen (Position, Größe, Sichtbarkeit, minimiert usw.)
- Fenster immer im Vordergrund / Vordergrund aufheben / anzeigen / ausblenden
- Fenster binden und lösen (Vorbereitung für Hintergrundoperationen)

### 🎯 Bild- & Farberkennung
- **Bild suchen**: Bildposition nach Ähnlichkeit in einem angegebenen Bildschirmbereich suchen, Batch-Suche unterstützt
- **Farbe suchen**: Einpunkt-Farbsuche, Mehrpunkt-Farbsuche, Bereichsfarbsuche, Farbtoleranz unterstützt
- **Farbe vergleichen**: Farbe an einer angegebenen Koordinate vergleichen
- **Screenshot**: Angegebenen Bereich erfassen und speichern / Bilddaten zurückgeben

### 📝 OCR (Optische Zeichenerkennung)
- **Text suchen**: Textkoordinaten auf dem Bildschirm basierend auf einem voreingestellten Wörterbuch suchen
- **Text erkennen**: Textinhalt in einem angegebenen Bereich erkennen und zurückgeben
- Unterstützt Standardzeichen, mehrfarbige Zeichen, farbverschobene Zeichen
- Unterstützt wörterbuchfreie OCR-Erkennung

### ⌨️🖱️ Tastatur- & Maussimulation
- **Vordergrundeingabe**: Tastaturtasten, Tastenkombinationen, Zeichenketten-Eingabe simulieren; Maus bewegen / klicken / scrollen
- **Hintergrundeingabe**: Hintergrundnachrichten an gebundene Fenster senden, ohne Fokus zu stehlen
- Unterstützt Tastenstatussteuerung (drücken / loslassen)

### 🧠 Hintergrundbindung
- Mehrere Bild/Farb-Bindemodi: `gdi`, `dx`, `dx2`, `opengl` usw.
- Mehrere Tastatur/Maus-Bindemodi: `windows`, `normal` usw.
- Geeignet für Spiele-Hintergrund-AFK, Multi-Fenster-Parallelautomatisierung

### 🧬 Speicheroperationen
- Prozessspeicher lesen / schreiben
- Speichersuche und Mustererkennung
- Modulbasisadresse eines Prozesses abrufen

### 📁 Datei & System
- Datei-Lese-/Schreiboperationen
- Systeminformationen abrufen (CPU-Auslastung, Arbeitsspeicher, Bildschirmauflösung usw.)
- Prozesse auflisten und verwalten

### 🔧 Thread-Sicherheit
- Unterstützt multithreaded-parallele Aufrufe
- Jeder Thread hat eine unabhängige Fensterbindung, keine gegenseitige干扰

### 🔄 Workflow
- Visuelle / Skript-basierte Automatisierungs-Task-Orchestrierung
- Unterstützt Steuerstrukturen wie Bedingungen, Schleifen, Verzögerungswartezeiten, Subflows
- Task-Kettenausführung, Ausgabe des vorherigen Schritts als Eingabe für den nächsten Schritt
- Unterstützt Workflow-Speichern, -Laden und -Wiederverwendung

### 🧩 Plugin-System
- Plugin-Hotloading zur Erweiterung von OmniFlow-Funktionen
- Unterstützt benutzerdefinierte Tools, benutzerdefinierte Workflow-Knoten
- Community-Plugin-Ökosystem zum Teilen und Wiederverwenden von Automatisierungsfunktionen

---

## 🏗️ Architektur

```
┌────────────────────────────────────────┐
│           AI Client (MCP Host)          │
│  Claude Desktop / CodeBuddy / VS Code   │
│  Cursor / Windsurf / Continue / Cline   │
│  Crayfish / Hermes / Trae / Kiro ...     │
└──────────────┬─────────────────────────┘
               │  MCP Protocol (stdio)
┌──────────────▼─────────────────────────┐
│           OmniFlow MCP Server           │
│  ┌───────────────────────────────────┐  │
│  │         MCP Tools Layer           │  │
│  │  window / image / text / input    │  │
│  │  / binding / memory / system ...  │  │
│  └──────────────┬────────────────────┘  │
│  ┌──────────────▼────────────────────┐  │
│  │        Automation Engine          │  │
│  │     Win32 API / COM / ctypes      │  │
│  └──────────────┬────────────────────┘  │
└─────────────────┼───────────────────────┘
┌─────────────────▼───────────────────────┐
│          Windows System Layer           │
│     GDI / DX / Win32 API               │
└────────────────────────────────────────┘
```

---

## 📥 Installation

### Voraussetzungen
- Windows OS
- Python 3.10+

### Installationsschritte

```bash
# 1. Repository klonen
git clone <this-repo-url>
cd OmniFlow

# 2. Virtuelle Umgebung erstellen
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac (einige Funktionen nicht unterstützt)

# 3. Abhängigkeiten installieren (Wichtig: muss `pip install -e .` verwenden, damit das omniflow-Paket über `python -m omniflow` importierbar ist)

# Methode 1: requirements.txt + editable install (Empfohlen)
pip install -r requirements.txt
pip install -e .

# Methode 2: Einzeiler
pip install -r requirements.txt && pip install -e .
```

---

## 🚀 Schnellstart

### MCP-Client konfigurieren

OmniFlow zur MCP-Client-Konfigurationsdatei hinzufügen:

```json
{
  "mcpServers": {
    "omniflow": {
      "command": "<venv-python>",
      "args": ["-m", "omniflow"],
      "cwd": "<local OmniFlow repo path>"
    }
  }
}
```

> Hinweise:
> - `command` zeigt auf python.exe in der venv (z. B. `D:/OmniFlow/.venv/Scripts/python.exe`)
> - `cwd` zeigt auf das OmniFlow-Repository-Stammverzeichnis
> - Einige MCP-Clients **unterstützen** das `cwd`-Feld (z. B. Hermes); bei Nichtunterstützung stattdessen `env.PYTHONPATH` verwenden

### Beispiel: AI ein Bild finden und klicken lassen

> Durch natürliche Sprachbeschreibung im AI-Client ruft OmniFlow automatisch die entsprechenden MCP-Tools auf:

1. Bildschirm erfassen → `screenshot`
2. Bild in Screenshot suchen → `find_image`
3. Maus bewegen und klicken → `mouse_click`

AI-Clients orchestrieren diese MCP-Tool-Aufrufe automatisch.

---

## 📖 MCP Tools Referenz

### Fenster-Tools

| Tool | Beschreibung |
|------|-------------|
| `window_find` | Fenster nach Titel / Klassenname suchen |
| `window_enum` | Alle Top-Level-Fenster auflisten |
| `window_get_info` | Detaillierte Fensterinformationen abrufen |
| `window_set_top` | Fenster immer im Vordergrund anzeigen |
| `window_show` | Fenster anzeigen / ausblenden |
| `window_activate` | Fenster in den Vordergrund bringen |
| `window_close` | Fenster schließen (sendet WM_CLOSE-Nachricht, entspricht dem Klicken auf X) |

### Bindung-Tools

| Tool | Beschreibung |
|------|-------------|
| `bind_window` | Fenster für Hintergrundoperation binden, Tastatur/Maus-Steuerung ist für den Benutzer transparent (Bild/Farbe und Eingabemodi angeben) |
| `unbind_window` | Fensterbindung aufheben, Vordergrundoperation wiederherstellen |

### Bild-Tools

| Tool | Beschreibung |
|------|-------------|
| `screenshot` | Angegebenen Bereich erfassen, Base64-Bild zurückgeben |
| `find_image` | Bild in angegebenem Bereich suchen, Koordinaten zurückgeben |
| `find_color` | Angegebene Farbe suchen, Koordinaten zurückgeben |
| `compare_color` | Farbe an angegebener Koordinate vergleichen |
| `get_color` | Farbwert an angegebener Koordinate abrufen |

### Text-Tools

| Tool | Beschreibung |
|------|-------------|
| `ocr` | Text in angegebenem Bereich erkennen |
| `find_text` | Textposition auf dem Bildschirm suchen |
| `set_ocr_dict` | OCR-Wörterbuchdateipfad festlegen |

### Eingabe-Tools

| Tool | Beschreibung |
|------|-------------|
| `key_press` | Tastaturtaste drücken und loslassen |
| `key_down` | Tastaturtaste gedrückt halten |
| `key_up` | Tastaturtaste loslassen |
| `key_type` | Zeichenkette eingeben |
| `hotkey` | Tastenkombination senden, z. B. Ctrl+C |
| `mouse_move` | Maus bewegen |
| `mouse_click` | Mausklick (links / rechts / mitte) |
| `mouse_scroll` | Mausrad scrollen |
| `mouse_get_pos` | Aktuelle Mausposition abrufen |

### Speicher-Tools

| Tool | Beschreibung |
|------|-------------|
| `mem_read` | Prozessspeicher lesen |
| `mem_write` | Prozessspeicher schreiben |
| `get_module_base` | Modulbasisadresse abrufen |

### System-Tools

| Tool | Beschreibung |
|------|-------------|
| `get_system_info` | CPU, Arbeitsspeicher und andere Systeminformationen abrufen |
| `get_screen_size` | Bildschirmauflösung abrufen |
| `enum_process` | Laufende Prozesse auflisten |
| `run_program` | Externes Programm starten (unterstützt PATH-Suche und .lnk-Verknüpfungen) |

### Workflow-Tools

| Tool | Beschreibung |
|------|-------------|
| `workflow_run` | Angegebenen Workflow ausführen |
| `workflow_list` | Alle gespeicherten Workflows auflisten |
| `workflow_save` | Aktuell orchestrierten Workflow speichern |
| `workflow_delete` | Workflow löschen |
| `workflow_pause` | Workflow-Ausführung anhalten |
| `workflow_resume` | Workflow-Ausführung fortsetzen |

### Plugin-Tools

| Tool | Beschreibung |
|------|-------------|
| `plugin_list` | Installierte Plugins auflisten |
| `plugin_install` | Plugin installieren |
| `plugin_uninstall` | Plugin deinstallieren |
| `plugin_enable` | Plugin aktivieren |
| `plugin_disable` | Plugin deaktivieren |

---

## 📁 Projektstruktur

```
OmniFlow/
├── .gitignore               # Git-Ignore-Konfiguration
├── README.md                # Projektdokumentation (Chinesisch)
├── README.en.md             # Projektdokumentation (Englisch)
├── README.ja.md             # Projektdokumentation (Japanisch)
├── README.de.md             # Projektdokumentation (Deutsch)
├── OmniFlow 使用示例.md      # Anwendungsbeispiele (nach Szenario: PS / Screenshot / Zeichnen)
├── requirements.txt         # Python-Abhängigkeiten
├── pyproject.toml          # Projektmetadaten
├── scripts/                 # Hilfsskripte
├── src/
│   └── omniflow/
│       ├── __init__.py
│       ├── __main__.py       # Einstiegspunkt (python -m omniflow)
│       ├── server.py         # MCP Server Hauptlogik
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── com.py        # COM / Win32 API Wrapper
│       │   └── types.py      # Typdefinitionen
│       └── tools/
│           ├── __init__.py
│           ├── window.py     # Fenster-Tools (einschließlich window_close)
│           ├── binding.py    # Bindung-Tools
│           ├── image.py      # Bild/Farberkennung-Tools
│           ├── ocr.py        # OCR-Tools
│           ├── input.py      # Tastatur/Maus-Simulation-Tools
│           ├── memory.py     # Speicheroperations-Tools
│           ├── system.py     # System-Tools (einschließlich run_program)
│           ├── workflow.py   # Workflow-Tools (v2-Engine: IF / WAIT_FOR_WINDOW / Variablenystem)
│           └── plugin.py     # Plugin-System-Tools
├── examples/
│   ├── open_photoshop.py    # Photoshop-Automatisierungsbeispiel
│   └── workflows/
│       └── infinite_fish_auto_sell.json   # Komplettes v2-Engine-Workflow-Beispiel (selbstständig)
└── tests/
    ├── __init__.py
    ├── test_tools.py        # Basistool-Tests
    └── test_workflow_v2.py  # Workflow v2-Engine-Regressionstests (8 Fälle)
```

> Hinweis: OmniFlow-Engine v2-Verbesserungen (Variablenystem / IF-Knoten / WAIT_FOR_WINDOW / sichere Bedingung / echte MCP-Aufrufe) finden Sie in `docs/workflows/translation-notes.md` und im OmniFlow 0.2.0-Eintrag in `known-integrations.md`.

---

## 🛠️ Entwicklung

```bash
# Entwicklungsabhängigkeiten installieren
pip install -e ".[dev]"

# Tests ausführen
pytest

# Code-Formatierung
ruff format src/
ruff check src/
```

---

## 📄 Lizenz

MIT License

---

## ⚠️ Haftungsausschluss

Dieses Tool darf nur für rechtmäßige Zwecke verwendet werden (z. B. Automatisierungstests, Büroautomatisierung usw.). Verwenden Sie es nicht für Szenarien, die gegen Spielbedingungen verstoßen, die Rechte anderer verletzen oder illegale Aktivitäten darstellen. Die Nutzer tragen die Verantwortung für ihre eigenen Handlungen.