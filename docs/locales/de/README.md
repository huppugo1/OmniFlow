# OmniFlow

> Windows-Automatisierungs-All-in-One-Tool basierend auf dem MCP (Model Context Protocol) Protokoll

**[English](../en/README.md)** | [中文](../zh-CN/README.md) | [日本語](../ja/README.md) | **Deutsch**

OmniFlow kapselt Windows-Desktop-Automatisierungsfunktionen (Fensteroperationen, Bild-/Farbenerkennung, Texterkennung, Tastatur-/Maus-Simulation, Hintergrundbindung, Speicheroperationen usw.) in einen standardisierten **MCP Server**, sodass jeder AI-Client, der das MCP-Protokoll unterstützt (wie Claude Desktop, VS Code, CodeBuddy, Cursor, Windsurf, Continue, Cline, Cody, Crayfish, Hermes, Trae, Kiro usw.), Windows-Automatisierungsfunktionen direkt aufrufen kann.

---

## ✨ Funktionsmerkmale

### 🎯 Anwendungsszenarien

OmniFlow verwandelt Windows-Desktop-Anwendungen in "von AI aufrufbare Tools". Häufige Anwendungsfälle:

- **🎨 Bildverarbeitungsautomatisierung** — Professionelle Software wie Photoshop / AI für Stapelbildverarbeitung antreiben (Skalierung, Farbkorrektur, Filter, Stapel-Export)
- **📸 Screenshot-Pipeline** — Bildschirmaufnahme → OCR-Textextraktion / PIL-Sekundärverarbeitung / Annotation zurück auf den Bildschirm
- **✏️ Zeichenautomatisierung** — Diagramme mit mspaint zeichnen, Anmerkungen hinzufügen, Flussdiagramme erstellen
- **🎮 Spiel-Assistent** — Hintergrund-Botting, automatischer Kampf, Dungeon-Automatisierung
- **📝 Büroautomatisierung** — Automatisches Ausfüllen von WPS / Office-Dokumenten, Berichterstellung, Stapel-Formatanpassung
- **🎬 Videosteuerung** — Automatische Pause/Fortsetzung des Players, Untertitelerkennung, zeitgesteuerte Aufnahme

### 🖥️ Fensteroperationen
- Fenstersuche und -aufzählung (nach Titel, Klassenname, PID usw.)
- Fensterstatusabfrage (Position, Größe, Sichtbarkeit, Minimierungsstatus usw.)
- Fenster immer im Vordergrund / Vordergrund aufheben / Anzeigen / Ausblenden
- Fensterbindung und -auflösung (Vorbereitung für Hintergrundoperationen)

### 🎯 Bild-/Farbenerkennung
- **Bildsuche**: Bildpositionen in angegebenen Bildschirmbereichen nach Ähnlichkeit suchen, unterstützt Stapelbildsuche für mehrere Bilder
- **Farbsuche**: Einzelpunkt-, Mehrpunkt- und Bereichsfarbsuche mit Farbtoleranz
- **Farbvergleich**: Farben an angegebenen Koordinaten vergleichen
- **Screenshot**: Angegebene Bereiche aufnehmen und speichern / Bilddaten zurückgeben

### 📝 Texterkennung (OCR)
- **Textsuche**: Textkoordinaten auf dem Bildschirm basierend auf vordefinierter Schriftbibliothek suchen
- **Texterkennung**: Textinhalte in angegebenen Bereichen erkennen und zurückgeben
- Unterstützt Standardschriften, Mehrfarbenschriften und Farbverzerrungsschriften
- Unterstützt OCR ohne Schriftbibliothek

### ⌨️🖱️ Tastatur-/Maus-Simulation
- **Vordergrund-Eingabe**: Tastaturtasten, Kombinationen und Zeichenfolgeneingabe simulieren; Mausbewegung / Klick / Scrollen
- **Hintergrund-Eingabe**: Hintergrundnachrichten an gebundene Fenster senden, ohne den Fokus zu stehlen
- Unterstützt Tastenstatussteuerung (halten / loslassen)

### 🧠 Hintergrundbindung
- Mehrere Bildbindungsmodi: `gdi`, `dx`, `dx2`, `opengl` usw.
- Mehrere Tastatur-/Maus-Bindungsmodi: `windows`, `normal` usw.
- Geeignet für Spiel-Hintergrund-Botting und Multi-Fenster-Parallelautomatisierung

#### 4 display_mode Optionen

| Modus | Prinzip | Vorteile | Nachteile | Wann AI wählen sollte |
|------|------|------|------|----------------------|
| `gdi` | GDI API Screenshot | Stabil, gute Kompatibilität | Fenster kann nicht minimiert werden | **Standard-Erstwahl**, normale Desktop-Software (WPS / Paint / PS) |
| `dx` | DirectX Hook | Kann minimiert werden, hohe Leistung | Einige Spiele nicht unterstützt | Wenn Benutzer explizit **DirectX-Engine** Spiel sagt |
| `dx2` | DirectX Enhanced | Bessere Kompatibilität | Etwas höherer Ressourcenverbrauch | Ausprobieren, wenn `dx` Modus fehlschlägt |
| `opengl` | OpenGL Hook | Unterstützt OpenGL-Spiele | Etwas instabil | Wenn Benutzer explizit **OpenGL-Engine** Spiel sagt |

**Tastatur-/Maus-Modus**: `normal` (Vordergrund, Fenster muss im Vordergrund sein) / `windows` (Windows-Nachrichten-Hintergrund, **empfohlen**)

**Automatische Modusauswahl (Zukunft)**: Plan zur Hinzufügung von `detect_bind_mode(hwnd)` Tool, automatisches Ausprobieren von `gdi → dx → dx2 → opengl` und Rückgabe einer Empfehlung.

### 🧬 Speicheroperationen
- Lesen / Schreiben von Prozessspeicher
- Speichersuche und Signatur-Scanning
- Basisadresse des Prozessmoduls abrufen

### 📁 Datei und System
- Datei-Lese-/Schreiboperationen
- Systeminformationen abrufen (CPU-Auslastung, Speicher, Bildschirmauflösung usw.)
- Prozessaufzählung und -verwaltung

### 🔧 Multi-Threading-Sicherheit
- Unterstützt Multi-Threading-Parallelaufrufe
- Pro Thread unabhängige Fensterbindung, gegenseitige Störungen vermeiden

### 🔄 Workflow
- Visuelle / skriptbasierte Orchestrierung von Automatisierungsaufgaben
- Unterstützt Bedingungen, Schleifen, Verzögerungen, Unterabläufe und andere Kontrollstrukturen
- Aufgabenkettenausführung, Ausgabe des vorherigen Schritts als Eingabe des nächsten Schritts
- Unterstützt Speichern, Laden und Wiederverwenden von Workflows

### 🧩 Plugin-System
- Plugin-Hotloading zur Erweiterung der OmniFlow-Fähigkeiten
- Unterstützt benutzerdefinierte Tools und benutzerdefinierte Workflow-Knoten
- Community-Plugin-Ökosystem zum Teilen und Wiederverwenden von Automatisierungsfähigkeiten

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
│          Windows Systemebene            │
│     GDI / DX / Win32 API               │
└─────────────────────────────────────────┘
```

---

## 📥 Installation

### Voraussetzungen
- Windows-Betriebssystem
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

# 3. Abhängigkeiten installieren (wichtig: `pip install -e .` ist erforderlich, damit omniflow-Paket von `python -m omniflow` importiert werden kann)

# Methode 1: requirements.txt + editable install (empfohlen)
pip install -r requirements.txt
pip install -e .

# Methode 2: Einzeiler
pip install -r requirements.txt && pip install -e .
```

---

## 🚀 Schnellstart

### MCP-Client konfigurieren

Fügen Sie OmniFlow zur Konfigurationsdatei Ihres MCP-Clients hinzu:

```json
{
  "mcpServers": {
    "omniflow": {
      "command": "<venv-python>",
      "args": ["-m", "omniflow"],
      "cwd": "<lokaler OmniFlow-Repository-Pfad>"
    }
  }
}
```

> Hinweise:
> - `command` zeigt auf `python.exe` in der venv (z.B. `D:/OmniFlow/.venv/Scripts/python.exe`)
> - `cwd` zeigt auf das Stammverzeichnis des OmniFlow-Repositorys
> - Einige MCP-Clients **unterstützen** das Feld `cwd` (z.B. Hermes); für diejenigen, die es nicht unterstützen, verwenden Sie stattdessen `env.PYTHONPATH`

### Beispiel: Lassen Sie AI automatisch ein Bild finden und klicken

> Durch natürliche Sprachbeschreibung im AI-Client ruft OmniFlow automatisch das entsprechende MCP Tool auf:

1. Bildschirm aufnehmen → `screenshot`
2. Bild im Screenshot suchen → `find_image`
3. Maus bewegen und klicken → `mouse_click`

Der AI-Client orchestriert diese MCP Tool-Aufrufe automatisch.

---

## 📖 MCP Tools Referenz

### Fenster-Tools

| Tool | Beschreibung |
|------|-------------|
| `window_find` | Fenster nach Titel / Klassenname suchen |
| `window_enum` | Alle Top-Level-Fenster aufzählen |
| `window_get_info` | Detaillierte Fensterinformationen abrufen |
| `window_set_top` | Fenster immer im Vordergrund |
| `window_show` | Fenster anzeigen / ausblenden |
| `window_activate` | Fenster in den Vordergrund bringen |
| `window_close` | Fenster schließen (WM_CLOSE-Nachricht senden, gleichbedeutend mit X-Klick) |

### Bindungs-Tools

| Tool | Beschreibung |
|------|-------------|
| `bind_window` | Fenster im Hintergrund binden, Tastatur-/Maus-Steuerung ohne Benutzerwahrnehmung (Bild-/Tastatur-/Maus-Modus angeben) |
| `unbind_window` | Fenster auflösen, Vordergrundoperation wiederherstellen |

### Bild-/Farb-Tools

| Tool | Beschreibung |
|------|-------------|
| `screenshot` | Angegebenen Bereich aufnehmen, Base64-Bild zurückgeben |
| `find_image` | Bild im angegebenen Bereich suchen, Koordinaten zurückgeben |
| `find_color` | Angegebene Farbe suchen, Koordinaten zurückgeben |
| `compare_color` | Farbe an angegebenen Koordinaten vergleichen |
| `get_color` | Farbwert an angegebenen Koordinaten abrufen |

### Text-Tools

| Tool | Beschreibung |
|------|-------------|
| `ocr` | Text im angegebenen Bereich erkennen |
| `find_text` | Textposition auf dem Bildschirm suchen |
| `set_ocr_dict` | OCR-Schriftbibliotheksdateipfad festlegen |

### Tastatur-/Maus-Tools

| Tool | Beschreibung |
|------|-------------|
| `key_press` | Tastaturtaste drücken |
| `key_down` | Tastaturtaste halten |
| `key_up` | Tastaturtaste loslassen |
| `key_type` | Zeichenfolge eingeben |
| `hotkey` | Kombinationstasten senden, z.B. Strg+C |
| `mouse_move` | Maus bewegen |
| `mouse_click` | Mausklick (links / rechts / mittlere Taste) |
| `mouse_scroll` | Mausscrollen |
| `mouse_get_pos` | Aktuelle Mausposition abrufen |

### Speicher-Tools

| Tool | Beschreibung |
|------|-------------|
| `mem_read` | Prozessspeicher lesen |
| `mem_write` | Prozessspeicher schreiben |
| `get_module_base` | Basisadresse des Prozessmoduls abrufen |

### System-Tools

| Tool | Beschreibung |
|------|-------------|
| `get_system_info` | Systeminformationen wie CPU, Speicher abrufen |
| `get_screen_size` | Bildschirmauflösung abrufen |
| `enum_process` | Laufende Prozesse aufzählen |
| `run_program` | Externes Programm starten (unterstützt PATH-Suche und .lnk-Verknüpfungen) |

### Workflow-Tools

| Tool | Beschreibung |
|------|-------------|
| `workflow_run` | Angegebenen Workflow ausführen |
| `workflow_list` | Alle gespeicherten Workflows auflisten |
| `workflow_save` | Aktuellen orchestrierten Workflow speichern |
| `workflow_delete` | Workflow löschen |
| `workflow_pause` | Workflow-Ausführung pausieren |
| `workflow_resume` | Workflow-Ausführung fortsetzen |

### Kombi-Tools (3) ⭐AI-freundlich

| Tool | Beschreibung |
|------|-------------|
| `click_image` | Bild suchen und klicken (kombiniert find_image + mouse_move + mouse_click) |
| `wait_and_click` | Polling bis Bild erscheint, dann klicken |
| `ocr_and_click` | OCR-Textsuche, dann Bereichsmittelpunkt klicken |

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
├── .gitignore               # Git Ignore-Konfiguration
├── README.md                # Projektdokumentation
├── OmniFlow 使用示例.md      # Nutzungsbeispiele (nach Szenario organisiert: PS / Screenshot / Zeichnung)
├── requirements.txt         # Python-Abhängigkeiten
├── pyproject.toml          # Projekt-Metadaten
├── scripts/                 # Hilfsskripte
├── docs/
│   ├── AI_INTEGRATION_GUIDE.md   # AI-Integrationsleitfaden (Konfiguration / Prompt / Debugging)
│   ├── MCP_TOOLS_REFERENCE.md    # 43 Tools vollständige Referenz (mit Fehlercodes)
│   └── OPTIMIZATION_PLAN.md      # Optimierungsplan
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
│           ├── window.py     # Fensterbezogene Tools (inkl. window_close)
│           ├── binding.py    # Bindungsbezogene Tools
│           ├── image.py      # Bild-/Farbenerkennung Tools
│           ├── ocr.py        # Texterkennung Tools
│           ├── input.py      # Tastatur-/Maus-Simulation Tools
│           ├── memory.py     # Speicheroperation Tools
│           ├── system.py     # Systembezogene Tools (inkl. run_program)
│           ├── workflow.py   # Workflow Tools (v2 Engine: IF / WAIT_FOR_WINDOW / Variablensystem)
│           └── plugin.py     # Plugin-System Tools
├── examples/
│   ├── open_photoshop.py    # Photoshop-Automatisierungsbeispiel
│   ├── ai_prompts/          # AI Prompt Beispiele (4 Szenarien)
│   │   ├── game_automation.md
│   │   ├── office_automation.md
│   │   ├── image_processing.md
│   │   └── web_control.md
│   └── workflows/
│       └── infinite_fish_auto_sell.json   # v2 Engine vollständiges Workflow-Beispiel (selbstenthalten)
└── tests/
    ├── __init__.py
    ├── test_tools.py        # Tool-Basistests
    └── test_workflow_v2.py  # Workflow v2 Engine Regressionstests (8 Fälle)
```

> Hinweis: OmniFlow Engine v2 Verbesserungen (Variablensystem / IF-Knoten / WAIT_FOR_WINDOW / Sichere condition / Echte MCP-Aufrufe) siehe `docs/workflows/translation-notes.md` und `known-integrations.md` Einträge für OmniFlow 0.2.0.

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

**MIT Lizenz**

OmniFlow verwendet die MIT-Lizenz, eine sehr permissive Open-Source-Lizenz:

- ✅ Freie Nutzung, Kopie, Modifikation und Verteilung des Codes erlaubt
- ✅ Für kommerzielle Projekte verwendbar
- ✅ Abgeleitete Werke können als Closed Source veröffentlicht werden
- ⚠️ Nur die ursprüngliche Urheberrechtshinweis und Lizenztext müssen beibehalten werden

Für spezifische Bedingungen siehe die LICENSE-Datei im Projekt.

---

## ⚠️ Haftungsausschluss

Dieses Tool ist nur für legale Zwecke (wie automatisiertes Testen, Büroautomatisierung usw.) vorgesehen. Verwenden Sie es nicht für Szenarien, die gegen die Nutzungsbedingungen von Spielen verstoßen, die Rechte anderer verletzen oder für illegale Aktivitäten. Benutzer tragen die eigene Verantwortung.
