# OmniFlow AI Integrationsleitfaden

> Praktischer Leitfaden für AI-Clients (Claude Desktop / Cursor / Windsurf / Hermes / Claude Code) zur korrekten Nutzung von OmniFlow.

---

## 1. MCP Client Konfiguration

OmniFlow kommuniziert mit MCP-Clients über das **stdio-Protokoll**. Die Konfiguration sagt im Wesentlichen "dem Client, wie er den OmniFlow-Server startet".

### 1.1 Universelle Konfigurationsvorlage

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

| Feld | Beschreibung |
|---|---|
| `command` | Absoluter Pfad zu `python.exe` in der venv (**nicht** das System-`python` — das omniflow-Paket wird nicht gefunden) |
| `args` | `["-m", "omniflow"]` (als Modul ausführen, `pip install -e .` muss **zuvor** ausgeführt werden) |
| `cwd` | Stammverzeichnis des OmniFlow-Repositorys (einige Clients unterstützen es, z.B. Hermes) |

### 1.2 Konfigurationsdatei-Standorte je Client

| Client | Konfigurationsdatei-Standort |
|---|---|
| **Hermes** | `~/.hermes/config.yaml` im Abschnitt `mcp.servers.omniflow` (verwaltet über `hermes mcp add omniflow ...` Befehl) |
| **Claude Desktop** | Windows: `%APPDATA%\Claude\claude_desktop_config.json`<br>macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Cursor** | Settings → MCP → Add new global MCP server |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` |
| **VS Code + Continue** | `.continue/config.json` im Abschnitt `experimental.mcpServers` |
| **Cline** | VS Code Einstellungen → Cline → MCP Servers |

### 1.3 Hermes Empfohlene Konfiguration

```bash
# Mit hermes mcp add registrieren (stabilsten)
hermes mcp add omniflow \
  --command "F:/woker/OmniFlow/.venv-omniflow/Scripts/python.exe" \
  --args "-m" "omniflow"
```

Oder **manuell bearbeiten** `~/.hermes/config.yaml`:
```yaml
mcp:
  servers:
    omniflow:
      command: "F:/woker/OmniFlow/.venv-omniflow/Scripts/python.exe"
      args: ["-m", "omniflow"]
```

### 1.4 Konfiguration überprüfen

Nach dem Start des Clients **Verbindungstest mit `mcp__omniflow__get_screen_size()`** — Rückgabe von `{"width": 1920, "height": 1080}` bedeutet OK.

---

## 2. Prompt Best Practices

### 2.1 AI zur richtigen Tool-Auswahl führen

**❌ Schlechter Prompt**:
> "Bedienen Sie den Computer für mich"

AI weiß nicht, mit welchem Tool sie beginnen soll.

**✅ Guter Prompt**:
> "Klicken Sie auf eine Schaltfläche in der unteren rechten Ecke des Bildschirms (Koordinaten 1800, 1000). Die Schaltfläche ist ein blaues abgerundetes Rechteck mit weißem Hintergrund"

AI weiß, dass sie `screenshot` für den Bildschirm + `find_image` für die Schaltfläche + `mouse_click` für den Klick verwenden soll.

### 2.2 AI aktiv `recovery_suggestions` prüfen lassen

**❌ Schlechter Prompt**:
> "Finden Sie die 'OK'-Schaltfläche"

Wenn die Schaltfläche nicht gefunden wird, wird die AI **wiederholt dasselbe Tool** versuchen und Zeit verschwenden.

**✅ Guter Prompt**:
> "Finden Sie die 'OK'-Schaltfläche. Wenn nicht gefunden, passen Sie zuerst den similarity-Schwellenwert gemäß `recovery_suggestions` an; wenn immer noch nicht gefunden, machen Sie einen Screenshot und zeigen Sie ihn mir"

Die AI wird **aktiv** das `recovery_suggestions`-Feld prüfen und die Strategie gemäß den Vorschlägen anpassen.

### 2.3 Klare Grenzen definieren

**❌ Gefährlicher Prompt**:
> "Ändern Sie die Spiel-HP auf 0"

Kann die AI dazu verleiten, **Speichermodifikationen** vorzunehmen (rechtliches Risiko).

**✅ Sicherer Prompt**:
> "Verwenden Sie Screenshot + find_image, um die HP-Leiste zu finden, und drücken Sie automatisch die Taste, um einen Trank zu trinken, wenn HP < 30%. **Verwenden Sie keine `mem_*`-Tools**"

Sagen Sie der AI explizit, den GUI-Automatisierungspfad zu verwenden, **keine** Speichermodifikation.

### 2.4 AI bereits registrierte Tools wiederverwenden lassen, anstatt neue zu erfinden

Wenn der Benutzer-Prompt vage ist, könnte die AI vorschlagen, neue Tools zu installieren. **Führen Sie die AI dazu, vorhandene Tools zu priorisieren**:

> "Verwenden Sie die vorhandenen Tools von OmniFlow, um diese Aufgabe zu erledigen. **Schlagen Sie nicht die Installation neuer Software vor**"

### 2.5 AI Kombi-Tools anstelle von atomaren Tools verwenden lassen

**❌ Schlechter Prompt**:
> "Finden Sie die 'OK'-Schaltfläche, bewegen Sie dann die Maus und klicken Sie"

Die AI wird `find_image` + `mouse_move` + `mouse_click` in drei Schritten verwenden.

**✅ Guter Prompt**:
> "Klicken Sie auf die 'OK'-Schaltfläche"

Die AI erkennt das `click_image` Kombi-Tool und priorisiert es (Ein-Schritt-Abschluss).

---

## 3. Typische Aufgabenabläufe (Wie AI Tools orchestrieren sollte)

### 3.1 Aufgabe: Automatisch auf eine Schaltfläche klicken

```
✅ Empfohlener Ablauf:
1. click_image(image_path="templates/btn.png", similarity=0.9)
2. Wenn clicked=False, wait_and_click aufrufen, um es erneut zu versuchen (längeres timeout)
3. Wenn immer noch fehlgeschlagen, similarity gemäß recovery_suggestions anpassen oder dem Benutzer einen Screenshot zeigen

❌ Nicht so machen:
1. find_image → Koordinaten holen → mouse_move → mouse_click (4 Schritte, nicht so gut wie click_image in 1 Schritt)
```

### 3.2 Aufgabe: Auf das Erscheinen einer Oberfläche warten

```
✅ Empfohlen:
1. wait_and_click(image_path="templates/loaded.png", timeout=30, poll_interval=1)
   (klicken, wenn Bild erscheint; nach timeout "Oberfläche ist nicht erschienen" melden)

Oder Workflow-Knoten verwenden (stabiler):
1. wait_for_window(class_name="MainForm", timeout=30)
```

### 3.3 Aufgabe: In Desktop-App einloggen

```
✅ Empfohlen:
1. window_find(title="Login Window") um hwnd zu erhalten
2. window_activate(hwnd=...) um in den Vordergrund zu bringen
3. key_type(text="username", interval=0.05)  # für IME
4. key_press(key="tab")
5. key_type(text="password", interval=0.05)
6. key_press(key="enter")
7. Überprüfung: Einige Sekunden warten → window_find(title="Main") um zu prüfen, ob Hauptoberfläche erreicht
```

### 3.4 Aufgabe: Spiel-Auto-Kampf-Schleife

```
✅ Empfohlen (Workflow-Engine):
1. Mit workflow_save einen Workflow speichern:
   - Monster-Icon suchen (find_image)
   - Bei Fund klicken (mouse_click)
   - 1s warten
   - Schleife
2. Mit hermes cron planen: Alle 60s ausführen

Oder in einer einzelnen Session:
1. bind_window(display_mode="dx", mouse_mode="windows", keyboard_mode="windows")
2. Schleife (manuelle loop_until "Benutzer bricht ab"):
   - find_image(image_path="monster.png")
   - Bei Fund klicken
   - "Aufheben"-Schaltfläche suchen → klicken
   - "Erfahrungsleiste voll"-Schaltfläche suchen → klicken
   - sleep(1)
```

### 3.5 Aufgabe: Alle Pop-ups leeren (Workflow am Laufen halten)

```
✅ Empfohlen (Workflow-Engine):
1. "Hinweis"-Fenster suchen → Bei Fund key_press(enter)
2. "Fehler"-Fenster suchen → Bei Fund window_close
3. Geöffnete Unterfenster suchen → Bei Fund schließen
4. Diese drei Schritte sind **idempotent** (überspringen, wenn nicht gefunden), können als Anfangssegment eines Workflows verwendet werden

Oder als wiederverwendbarer "Cleanup-Subflow":
- Workflow mit verschachtelter Subflow-Referenz
- Vor jeder Aufgabe Cleanup ausführen
```

### 3.6 Aufgabe: Text aus Screenshot extrahieren

```
✅ Empfohlen:
1. screenshot(Bereich) aufnehmen
2. ocr(Bereich) erkennen
3. LLM den Textinhalt analysieren lassen (regex / LLM)

⚠️ Hinweis: omni ocr gibt keine Koordinaten für jedes Wort zurück. Für Koordinaten find_image mit Text-Screenshot-Vorlage verwenden
```

---

## 4. Debugging-Tipps

### 4.1 Wenn Tool-Aufruf fehlschlägt

1. **`error_code` prüfen** — identifiziert die Problemkategorie (E1001 = Fenster nicht gefunden, E2001 = Bild nicht gefunden, usw.)
2. **`recovery_suggestions` prüfen** — listet spezifische Vorschläge für "was als Nächstes zu tun ist"
3. **Wenn Vorschläge unklar sind**, **`screenshot()` aufrufen, um den aktuellen Zustand zu sehen** —> 90% der "Fenster/Schaltfläche nicht gefunden"-Probleme sind auf einem Screenshot sofort ersichtlich

### 4.2 Wenn Aufgabe hängen bleibt

**Fragen Sie die AI selbst**:
> "Was sind Ihre letzten 5 Tool-Aufrufe? Welchen `error_code` haben sie zurückgegeben?"

Lassen Sie die AI ihren Aufrufverlauf melden und **selbst** das Problem identifizieren.

**Ausführliche Protokollierung aktivieren**:
```bash
hermes chat --verbose
# Oder beim Start von server.py:
LOG_LEVEL=DEBUG
```

### 4.3 Überprüfen, ob Workflow sinnvoll ist

`validate_workflow` Tool verwenden (P3-Plan, noch nicht implementiert; aktuell JSON mit Python parsen, dann dry-run):

```python
# Nach dem Parsen von JSON prüfen:
# 1. Sind alle Schritt-IDs eindeutig?
# 2. Stimmen Feldnamen im outputs schema mit downstream {var}-Referenzen überein?
# 3. Sind Bedingungsausdrücke gültig?
```

### 4.4 Test-Tools

`tests/test_workflow_v2.py` enthält 8 Workflow-Engine-Unit-Tests + Integrationstests. **Vor der Änderung der Workflow-Engine ausführen**.

`tests/test_p0_wrap.py` überprüft die `_wrap_result` Wrapper-Logik (einheitliches Rückgabeformat).

`tests/test_p1_composite.py` überprüft Fehlerpfade von 3 Kombi-Tools.

---

## 5. Leistung und Best Practices

### 5.1 Hochfrequente Aufruf-Optimierung

- `screenshot` ist synchron blockierend (50-200ms), **nicht** in 60fps-Echtzeit-Schleifen verwenden
- Für hochfrequente Screenshots (>5/Sek) `mss`-Bibliothek verwenden
- Vorlagenbildladen ist zwischengespeichert — `find_image` mit demselben Bild mehrmals ist schneller als verschiedene Bilder

### 5.2 Langzeit-Aufgaben-Planung

**Einzelne Session**: Geeignet für schnelle Aufgaben < 5 Minuten.

**Cross-Session** (`hermes cron`): Geeignet für geplante Aufgaben (stündliches Leeren von Pop-ups, alle 10 Minuten Daten speichern).

**Workflow-Engine**: Geeignet für zusammengesetzte Abläufe wie "Cleanup + Hauptaufgabe", als Workflow speichern und wiederverwenden.

### 5.3 Sicherheits-Leitplanken

1. **Vor Schreiboperationen bestätigen** — `mem_write` / `key_type` / `mouse_click` haben alle **Nebenwirkungen**
2. **Vor Hintergrundoperationen `bind_window`** — verhindern, dass Tastatur/Maus von anderen Fenstern gestohlen wird
3. **Vor Screenshot `mouse_move(0, 0)`** um Cursor in die Ecke zu verschieben — vermeiden, dass Cursor auf dem Screenshot erscheint
4. **Fehlermeldungen enthalten `recovery_suggestions`** — bei Fehlern **zuerst hier prüfen**, **nicht** blind versuchen

---

## 6. Dokumentation Querverweise

- Vollständige 43 Tool-Beschreibungen + Szenarien + Fehlercodes: `docs/MCP_TOOLS_REFERENCE.md`
- Nach Szenario organisierte Nutzungsbeispiele: `OmniFlow 使用示例.md`
- v2 Engine Workflow-Beispiel: `examples/workflows/infinite_fish_auto_sell.json`
- Vollständige Fehlercode-Liste: `src/omniflow/tools/errors.py`
- Skills (für AI-Selbstlernen): `~/.hermes/skills/autonomous-ai-agents/omniflow-windows-automation/SKILL.md`

---

## 7. Häufig gestellte Fragen (FAQ)

**Q: AI hat ein Tool aufgerufen, aber es schlägt immer fehl, was tun?**
A: Lassen Sie die AI einen Screenshot machen, um den aktuellen Zustand zu zeigen. 90% der "X nicht gefunden"-Probleme sind auf einem Screenshot direkt ersichtlich (Fenster versteckt, Schaltfläche verdeckt, Koordinatenversatz usw.).

**Q: Tool kann keinen geeigneten Workflow-Engine-Knoten finden?**
A: Workflow v2 Engine unterstützte Knoten: tool_call / condition / if / loop / delay / subflow / wait_for_window. **`wait_for_window_close`** (Warten bis Fenster verschwindet) und andere seltene Knoten werden **nicht** unterstützt. Umgehung: `loop_until` + `window_get_info` verwenden, um Fensterexistenz zu pollen.

**Q: Wie bringt man AI bei, OmniFlow-Nutzungsmuster zu lernen?**
A: Laden Sie den Skill unter `~/.hermes/skills/autonomous-ai-agents/omniflow-windows-automation/`. Dieser Skill enthält bereits 6 große Szenarien, 5 Muster, Fehlerwiederherstellung und Designprinzipien.

**Q: AI hat versehentlich `mem_write` verwendet, was tun?**
A: Sofort rückgängig machen! `mem_write` an falsche Adresse kann den Zielprozess abstürzen lassen. **Prävention** > **Behandlung**: Lassen Sie die AI niemals automatisch `mem_write` verwenden — explizit "Screenshot + find_image verwenden, Speicher nicht modifizieren" verlangen.

**Q: Workflow-Engine läuft langsam?**
A: Workflow v2 Engine ist Single-Threaded-sequentielle Ausführung (v1 ähnlich), ohne Parallelisierung. Wenn ein Workflow 100 Schritte hat, jeder 100ms, insgesamt 10s. Optimierung: Schritte zusammenfassen, `wait_for_window` Polling-Intervall reduzieren, `hermes cron` verwenden, um große Aufgaben in mehrere kleine aufzuteilen.

**Q: Unterschiedliche LLM OmniFlow-Nutzungsgewohnheiten?**
A:
- **Claude Opus / Sonnet**: Am besten bei Kombi-Tools, hochsensibel für Fehlercodes + Wiederherstellungsvorschläge
- **GPT-4 / GPT-4o**: Ähnlich wie Claude
- **Lokale kleine Modelle (z.B. llama3 7B)**: Könnten bei Mehrschritt-Orchestrierung scheitern, **empfohlen** `click_image` und andere Kombi-Tools zu verwenden, um Orchestrierungskomplexität zu reduzieren
