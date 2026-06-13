# OmniFlow MCP Tools Referenz

> Vollständige 43 MCP Tools Anwendungsszenarien, Parameter, Rückgabewerte, Fehlercodes und gängige Kombinationen.

---

## 1. Einheitliches Rückgabeformat

Alle Tool-Aufrufe geben JSON im **einheitlichen Format** zurück:

```json
{
  "success": true,
  "data": { ... },                  // Original Tool-Rückgabe (Felder beibehalten)
  "message": "ok",                  // Menschenlesbar
  "error_code": null,               // Fehlercode (null bei Erfolg)
  "recovery_suggestions": []       // Bei Fehler mit Wiederherstellungsvorschlägen gefüllt
}
```

### 1.1 Vollständiger Fehlercode

OmniFlow verwendet ein **modulare Segmentierung** Fehlercodesystem:

| Modul | Code-Bereich | Modul-Beschreibung |
|------|------|------|
| System | E0000-E0999 | Systemweite Fehler, gängige Validierungsfehler |
| Fenster | E1000-E1999 | Fensteroperationen (Suche, Aufzählung, Status) |
| Bindung | E2000-E2999 | Fensterbindung, Bild-/Tastatur-/Maus-Modus |
| Bild | E3000-E3999 | Bild-/Farbenerkennung (find_image, find_color, compare_color, screenshot) |
| Text (OCR) | E4000-E4999 | Texterkennung (ocr, find_text, set_ocr_dict) |
| Eingabe | E5000-E5999 | Tastatur-/Maus-Simulation (key_press, mouse_click usw.) |
| Speicher | E6000-E6999 | Speicheroperationen (mem_read, mem_write) |
| System | E7000-E7999 | Systembezogene Tools (get_system_info, get_screen_size, enum_process) |
| Workflow | E8000-E8999 | Workflow-Engine (workflow_run, workflow_save, subflow usw.) |

Häufige Fehlercodes:

| Code | Fehlertyp | Bedeutung |
|------|------|------|
| E0001 | Validierungsfehler | Eingabeparameter-Validierung fehlgeschlagen (z.B. Pfad existiert nicht, Koordinaten negativ, Farbe hat falsches Format) |
| E0002 | Nicht initialisiert | Engine hat kein vollständiges OMNI-Objekt |
| E1001 | Fenster nicht gefunden | window_find Titel/ClassName nicht gefunden |
| E1002 | Fensterstatusfehler | window_get_info hwnd ungültig oder Fenster bereits zerstört |
| E2001 | Bild nicht gefunden | find_image Suchergebnis ist leer (Similarity zu gering / Bild überdeckt / Bild nicht aufgenommen) |
| E2002 | Farbe nicht gefunden | find_color Suchergebnis ist leer |
| E2003 | Bindungsfehler | bind_window Modus nicht unterstützt (z.B. DirectX-Fenster mit GDI-Modus) |
| E2004 | Bindung fehlgeschlagen | bind_window hwnd nicht gefunden oder Fenster ist Desktop |
| E3001 | Farbvergleich fehlgeschlagen | compare_color Koordinaten sind schwarzer Bereich / Hintergrund |
| E4001 | OCR-Schriftbibliothek nicht gesetzt | Vor ocr / find_text muss set_ocr_dict aufgerufen werden |
| E4002 | OCR-Erkennung fehlgeschlagen | Zu kleiner Bereich / Text verschwommen / Schriftbibliothek nicht passend |
| E4003 | Text nicht gefunden | find_text Suchergebnis ist leer |
| E5001 | Tastenname ungültig | key_press "shift" + "a" hat falsches Format (nicht "shift+a") |
| E5002 | Eingabesperre | AI hat innerhalb von 500ms nach mouse_click eine andere mouse_click an derselben Stelle ausgeführt |
| E6001 | Speicherzugriff verweigert | Speicher nicht lesbar / Adresse außerhalb des Prozesses |
| E6002 | Speicherformatfehler | mem_write Hex-Daten-Länge ist keine gerade Anzahl |
| E7001 | Prozess nicht gefunden | enum_process PID nicht vorhanden |
| E8001 | Workflow nicht gefunden | workflow_run ID nicht vorhanden |
| E8002 | Workflow-Knotenfehler | Workflow-Knoten-Typ ungültig / Schritt-ID dupliziert / Bedingungsausdruck Syntaxfehler |

Für vollständige Fehlercode-Liste siehe `src/omniflow/tools/errors.py`.

### 1.2 Wiederherstellungsvorschläge `recovery_suggestions`

Bei Fehlern gibt `recovery_suggestions` eine geordnete Liste der Lösungsvorschläge zurück, z.B.:

```json
{
  "success": false,
  "error_code": "E2001",
  "message": "Bild nicht gefunden: btn.png",
  "recovery_suggestions": [
    "Bereich vergrößern, um mehr Bildschirm zu abdecken",
    "Similarity-Schwellenwert reduzieren (0.9 → 0.7 → 0.5)",
    "Screenshots vergleichen, um zu prüfen, ob Schaltfläche durch anderes Fenster verdeckt ist"
  ]
}
```

AI sollte **diese Vorschläge priorisieren**, nicht blind wiederholen.

---

## 2. Tool-Schnellreferenz (Schnelles Nachschlagen)

### 2.1 Tool-Liste und Anwendungsszenarien

#### 🔧 System-Tools (7)

| Tool | Anwendungsszenario | Häufigkeit |
|------|------|------|
| `screenshot` | Beliebige visuelle Aufgabe, Debug-Zustand | ⭐⭐⭐⭐⭐ |
| `get_screen_size` | Vor dem ersten Aufruf Verbindungstest | ⭐⭐⭐⭐ |
| `get_system_info` | Prozessressourcen-Überwachung | ⭐⭐ |
| `enum_process` | Zielprozess-PID finden | ⭐⭐⭐ |
| `get_color` | Farbvergleich, Status-Lichtprüfung | ⭐⭐ |
| `find_color` | Schnelle Farbpositionierung | ⭐⭐⭐ |
| `compare_color` | Status-Lichtfarbe prüfen (z.B. Verbindungsstatus-LED) | ⭐⭐ |

#### 🖥️ Fensteroperationen (7)

| Tool | Anwendungsszenario | Häufigkeit |
|------|------|------|
| `window_find` | Zielfenster-Handle (hwnd) finden | ⭐⭐⭐⭐⭐ |
| `window_enum` | Alle geöffneten Fenster auflisten | ⭐⭐ |
| `window_get_info` | Fensterstatus prüfen (Größe / Position / Sichtbarkeit) | ⭐⭐⭐ |
| `window_activate` | Fenster in den Vordergrund bringen | ⭐⭐⭐⭐ |
| `window_set_top` | Fenster fixieren (nicht von anderen überdeckt) | ⭐⭐ |
| `window_show` | Fenster anzeigen / ausblenden | ⭐⭐ |
| `window_close` | Fenster schließen (nach Abschluss der Aufgabe bereinigen) | ⭐⭐ |

#### 🔗 Bindungsoperationen (2)

| Tool | Anwendungsszenario | Häufigkeit |
|------|------|------|
| `bind_window` | Spiel-Hintergrund-Botting, Multi-Fenster-Automatisierung | ⭐⭐⭐⭐ |
| `unbind_window` | Nach Aufgabenende bindung auflösen, Ressourcen freigeben | ⭐⭐⭐ |

#### 🎯 Bildoperationen (3)

| Tool | Anwendungsszenario | Häufigkeit |
|------|------|------|
| `find_image` | Schaltflächen / Symbole / Checkboxen / Elemente finden | ⭐⭐⭐⭐⭐ |
| `find_image` Batch | Mehrere Schaltflächen gleichzeitig finden (z.B. "Aufheben" / "Schließen" / "OK") | ⭐⭐⭐ |
| `click_image` | ⭐ AI-freundlich: Bild suchen + Maus bewegen + klicken in einem Schritt | ⭐⭐⭐⭐⭐ |
| `wait_and_click` | ⭐ AI-freundlich: Polling bis Bild erscheint, dann klicken | ⭐⭐⭐⭐ |

#### 📝 Textoperationen (3)

| Tool | Anwendungsszenario | Häufigkeit |
|------|------|------|
| `ocr` | Text im Spiel / in der Software extrahieren (HP / Gold / Level) | ⭐⭐⭐⭐ |
| `find_text` | "OK"-Text auf dem Bildschirm finden und klicken | ⭐⭐⭐ |
| `ocr_and_click` | ⭐ AI-freundlich: OCR-Textsuche + Bereichsmittelpunkt-Klick | ⭐⭐⭐ |

#### ⌨️🖱️ Eingabeoperationen (10)

| Tool | Anwendungsszenario | Häufigkeit |
|------|------|------|
| `key_press` | Einzeltasten (Enter / Tab / Esc / F1) | ⭐⭐⭐⭐ |
| `key_type` | Benutzername / Passwort / Suchbegriff eingeben | ⭐⭐⭐⭐⭐ |
| `key_down` / `key_up` | Tastenkombination halten (Shift+Klick) | ⭐⭐ |
| `hotkey` | Tastenkombinationen senden (Ctrl+C / Ctrl+V / Alt+F4) | ⭐⭐⭐⭐ |
| `mouse_move` | Maus an Koordinaten bewegen (z.B. vor Screenshot) | ⭐⭐⭐ |
| `mouse_click` | Mausklick auf Koordinaten (links / rechts / mittlere Taste) | ⭐⭐⭐⭐⭐ |
| `mouse_scroll` | Scrollen in Listen / Webseiten | ⭐⭐⭐ |
| `mouse_get_pos` | Aktuelle Mausposition erhalten | ⭐⭐ |

#### 🧠 Speicheroperationen (3)

| Tool | Anwendungsszenario | Häufigkeit |
|------|------|------|
| `mem_read` | Spiel-Daten lesen (nicht empfohlen, Rechtsrisiko) | ⭐ |
| `mem_write` | Spiel-Daten modifizieren (nicht empfohlen, Rechtsrisiko) | ⭐ |
| `get_module_base` | Modulbasisadresse für Adressberechnung | ⭐ |

#### 🔄 Workflow-Tools (6)

| Tool | Anwendungsszenario | Häufigkeit |
|------|------|------|
| `workflow_run` | Gespeicherten Workflow ausführen | ⭐⭐⭐⭐ |
| `workflow_list` | Verfügbare Workflows anzeigen | ⭐⭐ |
| `workflow_save` | Aktuellen Workflow speichern | ⭐⭐⭐ |
| `workflow_delete` | Veralteten Workflow löschen | ⭐ |
| `workflow_pause` | Langläufigen Workflow pausieren | ⭐ |
| `workflow_resume` | Pausierten Workflow fortsetzen | ⭐ |

#### 🧩 Plugin-Tools (5)

| Tool | Anwendungsszenario | Häufigkeit |
|------|------|------|
| `plugin_list` | Installierte Plugins anzeigen | ⭐⭐ |
| `plugin_install` | Neues Plugin installieren | ⭐ |
| `plugin_uninstall` | Plugin entfernen | ⭐ |
| `plugin_enable` | Plugin aktivieren | ⭐⭐ |
| `plugin_disable` | Plugin deaktivieren | ⭐⭐ |

### 2.2 Gängige Kombinationen

#### 3-Tool-Kette: Screenshot → find_image → click
```
1. screenshot(top=0, left=0, right=1920, bottom=1080)  # Gesamter Bildschirm
2. find_image(image_path="templates/btn.png", similarity=0.9)  # -> {"found": true, "x": 500, "y": 300}
3. mouse_click(x=500, y=300, button="left", clicks=1)
```

#### 2-Tool-Kette: window_find → window_activate
```
1. window_find(title="Spiel")  # -> {"hwnd": 123456, ...}
2. window_activate(hwnd=123456)  # Fenster in den Vordergrund bringen
```

#### 4-Tool-Kette: bind_window → find_image → mouse_click → unbind_window
```
1. bind_window(hwnd=123456, display_mode="gdi", mouse_mode="windows", keyboard_mode="windows")
2. find_image(image_path="templates/monster.png")
3. mouse_click(x=..., y=...)
4. unbind_window(hwnd=123456)  # Nach Abschluss auflösen
```

#### 2-Tool-Kette: screenshot → ocr (Textextraktion)
```
1. screenshot(top=100, left=100, right=300, bottom=200)  # Bereich aufnehmen
2. ocr(top=100, left=100, right=300, bottom=200)  # -> {"text": "Level: 42"}
```

#### Ein-Schritt-Kombi: click_image
```
1. click_image(image_path="templates/btn.png", similarity=0.9, button="left")
   # -> {"clicked": true, "x": 500, "y": 300}
```

---

## 3. Details aller Tools

### 3.1 System-Tools

#### `screenshot`

Bereich aufnehmen, Base64-Bild zurückgeben.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `top` | int | Nein | 0 | Bereich obere Koordinate |
| `left` | int | Nein | 0 | Bereich linke Koordinate |
| `right` | int | Nein | Bildschirmbreite | Bereich rechte Koordinate |
| `bottom` | int | Nein | Bildschirmhöhe | Bereich untere Koordinate |
| `save_path` | str | Nein | - | Speicherpfad (png/jpg), weglassen, um nur Base64 zurückzugeben |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "image": "base64_string_here...",
    "width": 1920,
    "height": 1080
  }
}
```

**Häufige Fehlercodes**: E3001 (Bereich außerhalb des Bildschirms)

**Anwendungsszenarien**:
- **Debug-Zustand**: Wenn ein Tool fehlschlägt, screenshot aufrufen, um dem Benutzer den aktuellen Zustand zu zeigen
- **Vorlagenaufnahme**: Schaltflächen / Symbole aufnehmen und als find_image-Vorlage speichern
- **OCR-Vorverarbeitung**: Bereich aufnehmen und ocr übergeben

**Hinweise**:
- screenshot ist synchron blockierend (50-200ms), nicht in 60fps-Echtzeit-Schleifen verwenden
- Vor dem Aufnehmen mouse_move(0, 0) aufrufen, um Cursor in die Ecke zu verschieben (vermeiden, dass Cursor auf dem Bild erscheint)

---

#### `get_screen_size`

Bildschirmauflösung abrufen.

| Parameter | Erforderlich | Beschreibung |
|---|---|---|
| Keine | - | - |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "width": 1920,
    "height": 1080
  }
}
```

**Anwendungsszenarien**: Verbindungstest (nach MCP-Client-Konfiguration mit diesem Tool testen, ob OmniFlow läuft)

---

#### `get_system_info`

Systeminformationen abrufen.

| Parameter | Erforderlich | Beschreibung |
|---|---|---|
| Keine | - | - |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "cpu_percent": 15.2,
    "memory_percent": 45.3,
    "platform": "Windows-10-10.0.19045-SP0"
  }
}
```

---

#### `enum_process`

Laufende Prozesse aufzählen.

| Parameter | Erforderlich | Beschreibung |
|---|---|---|
| Keine | - | - |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "processes": [
      {"pid": 1234, "name": "chrome.exe"},
      {"pid": 5678, "name": "game.exe"}
    ]
  }
}
```

**Häufige Fehlercodes**: E7001 (Prozess nicht gefunden — bei Abfrage nach bestimmter PID)

---

#### `get_color`

Farbwert an angegebenen Koordinaten abrufen.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `x` | int | Ja | X-Koordinate |
| `y` | int | Ja | Y-Koordinate |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "color": "FF5733"
  }
}
```

---

#### `find_color`

Angegebene Farbe suchen.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `color` | str | Ja | - | Farbwert, wie "FF5733" |
| `tolerance` | int | Nein | 20 | Farbtoleranz 0-255 |
| `top` | int | Nein | 0 | Bereich obere Koordinate |
| `left` | int | Nein | 0 | Bereich linke Koordinate |
| `right` | int | Nein | Bildschirmbreite | Bereich rechte Koordinate |
| `bottom` | int | Nein | Bildschirmhöhe | Bereich untere Koordinate |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "found": true,
    "x": 500,
    "y": 300
  }
}
```

**Häufige Fehlercodes**: E2002 (Farbe nicht gefunden)

---

#### `compare_color`

Farbe an angegebenen Koordinaten vergleichen.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `x` | int | Ja | - | X-Koordinate |
| `y` | int | Ja | - | Y-Koordinate |
| `color` | str | Ja | - | Erwartete Farbe, wie "FF5733" |
| `tolerance` | int | Nein | 20 | Farbtoleranz 0-255 |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "matched": true,
    "actual_color": "FF5733"
  }
}
```

**Häufige Fehlercodes**: E3001 (Farbvergleich fehlgeschlagen — Koordinaten sind schwarzer Bereich / Hintergrund)

**Anwendungsszenarien**: Status-Licht prüfen (z.B. Netzwerkverbindung grüne LED / rote LED)

---

### 3.2 Fenster-Tools

#### `window_find`

Fenster nach Titel / Klassenname suchen.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `title` | str | Nein | Fenstertitel (Teilstring oder vollständiger Titel) |
| `class_name` | str | Nein | Fensterklassenname |

**Hinweise**: Mindestens eines von `title` oder `class_name` angeben.

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "hwnd": 123456,
    "title": "Spiel",
    "class_name": "UnityWndClass",
    "pid": 7890
  }
}
```

**Häufige Fehlercodes**: E1001 (Fenster nicht gefunden)

**Anwendungsszenarien**:
- **Vor dem Spiel-Botting**: window_find("Spiel") um hwnd zu erhalten, dann bind_window
- **Fensterstatus prüfen**: window_find("Login") um zu prüfen, ob Login-Fenster noch vorhanden ist

---

#### `window_enum`

Alle Top-Level-Fenster aufzählen.

| Parameter | Erforderlich | Beschreibung |
|---|---|---|
| Keine | - | - |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "windows": [
      {"hwnd": 123456, "title": "Spiel", "class_name": "UnityWndClass", "visible": true},
      {"hwnd": 789012, "title": "Editor", "class_name": "Notepad", "visible": false}
    ]
  }
}
```

**Anwendungsszenarien**: Auflisten aller geöffneten Fenster, um Zielfenster zu finden (besonders nützlich, wenn Fenstertitel dynamisch ist)

---

#### `window_get_info`

Detaillierte Fensterinformationen abrufen.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `hwnd` | int | Ja | Fenster-Handle |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "hwnd": 123456,
    "title": "Spiel",
    "class_name": "UnityWndClass",
    "rect": {"left": 100, "top": 100, "right": 1100, "bottom": 700},
    "width": 1000,
    "height": 600,
    "visible": true,
    "minimized": false,
    "pid": 7890
  }
}
```

**Häufige Fehlercodes**: E1002 (Fensterstatusfehler — hwnd ungültig oder Fenster bereits zerstört)

---

#### `window_activate`

Fenster in den Vordergrund bringen.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `hwnd` | int | Ja | Fenster-Handle |

**Rückgabe**: `{"activated": true}`

**Anwendungsszenarien**: Vor key_type / mouse_click sicherstellen, dass Zielfenster im Vordergrund ist

---

#### `window_set_top`

Fenster immer im Vordergrund / Vordergrund aufheben.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `hwnd` | int | Ja | - | Fenster-Handle |
| `on_top` | bool | Nein | true | true = Immer im Vordergrund, false = Aufheben |

**Rückgabe**: `{"set": true}`

---

#### `window_show`

Fenster anzeigen / ausblenden.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `hwnd` | int | Ja | - | Fenster-Handle |
| `show` | bool | Nein | true | true = Anzeigen, false = Ausblenden |

**Rückgabe**: `{"shown": true}`

---

#### `window_close`

Fenster schließen (WM_CLOSE-Nachricht senden, gleichbedeutend mit X-Klick).

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `hwnd` | int | Ja | Fenster-Handle |

**Rückgabe**: `{"closed": true}`

**Hinweise**: Einige Anwendungen zeigen "Speichern?"-Dialog, in diesem Fall ist closed true, aber Anwendung nicht beendet. Notwendig, Dialog zu bestätigen.

---

### 3.3 Bindungs-Tools

#### `bind_window`

Fenster im Hintergrund binden.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `hwnd` | int | Ja | - | Fenster-Handle |
| `display_mode` | str | Nein | "gdi" | Bildmodus: gdi / dx / dx2 / opengl |
| `mouse_mode` | str | Nein | "windows" | Mausmodus: normal / windows |
| `keyboard_mode` | str | Nein | "windows" | Tastaturmodus: normal / windows |

**Rückgabe**: `{"bound": true}`

**Häufige Fehlercodes**:
- E2003 (Bindungsfehler — Modus nicht unterstützt, z.B. DirectX-Fenster mit GDI-Modus)
- E2004 (Bindung fehlgeschlagen — hwnd nicht gefunden oder Fenster ist Desktop)

**Anwendungsszenarien**:
- **Spiel-Hintergrund-Botting**: bind_window + Hintergrund-Maus-/Tastatureingabe, Benutzer kann gleichzeitig anderes tun
- **Multi-Fenster-Automatisierung**: Mehrere Fenster binden, nacheinander Operationen ausführen

**Hinweise**:
- Hintergrund-Bindung ist Tastatur-/Maus-Steuerung ohne Benutzerwahrnehmung, Benutzer kann weiter normal arbeiten
- Nach Aufgabenende unbind_window aufrufen, um Ressourcen freizugeben

---

#### `unbind_window`

Fenster auflösen.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `hwnd` | int | Ja | Fenster-Handle |

**Rückgabe**: `{"unbound": true}`

**Anwendungsszenarien**: Nach Aufgabenende aufrufen, um Ressourcen freizugeben, Rückkehr zur Vordergrundoperation

---

### 3.4 Bild-Tools

#### `find_image`

Bild im angegebenen Bereich suchen.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `image_path` | str | Ja | - | Vorlagenbildpfad (png/jpg/bmp) |
| `similarity` | float | Nein | 0.9 | Ähnlichkeitsschwellenwert 0.0-1.0 |
| `top` | int | Nein | 0 | Bereich obere Koordinate |
| `left` | int | Nein | 0 | Bereich linke Koordinate |
| `right` | int | Nein | Bildschirmbreite | Bereich rechte Koordinate |
| `bottom` | int | Nein | Bildschirmhöhe | Bereich untere Koordinate |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "found": true,
    "x": 500,
    "y": 300,
    "similarity": 0.95
  }
}
```

**Häufige Fehlercodes**: E2001 (Bild nicht gefunden)

**Wiederherstellungsvorschläge** (bei E2001):
1. Bereich vergrößern (z.B. gesamten Bildschirm)
2. similarity reduzieren (0.9 → 0.7 → 0.5)
3. Screenshots vergleichen, um zu prüfen, ob Schaltfläche durch anderes Fenster verdeckt ist

**Anwendungsszenarien**:
- **Schaltfläche finden**: Schaltflächen-Screenshot als Vorlage speichern, dann find_image
- **Batch-Suche**: Mehrere Schaltflächen gleichzeitig finden (z.B. "Aufheben" / "Schließen" / "OK")
- **Status prüfen**: Spiel-UI-Element (z.B. "Auto"-Status-Icon) finden, um Zustand zu bestimmen

**Hinweise**:
- Vorlagenbild sollte klar sein (nur Zielschaltfläche, ohne umgebende Elemente)
- Empfohlene similarity: 0.9 (zu hoch ist nicht gefunden, zu niedrig ist falsch erkannt)
- Nach ersten Aufruf Vorlagenbild zwischengespeichert, mehrmalige Suche schneller

---

#### `click_image`

Bild suchen und klicken (kombiniert find_image + mouse_move + mouse_click).

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `image_path` | str | Ja | - | Vorlagenbildpfad |
| `similarity` | float | Nein | 0.9 | Ähnlichkeitsschwellenwert |
| `button` | str | Nein | "left" | Maustaste: left / right / middle |
| `clicks` | int | Nein | 1 | Klickanzahl |
| `top` | int | Nein | 0 | Bereich obere Koordinate |
| `left` | int | Nein | 0 | Bereich linke Koordinate |
| `right` | int | Nein | Bildschirmbreite | Bereich rechte Koordinate |
| `bottom` | int | Nein | Bildschirmhöhe | Bereich untere Koordinate |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "clicked": true,
    "x": 500,
    "y": 300,
    "similarity": 0.95
  }
}
```

**Häufige Fehlercodes**: E2001 (Bild nicht gefunden → clicked=false)

**Anwendungsszenarien**: ⭐ AI-freundlich: Schaltfläche in einem Schritt finden und klicken, 3 atomare Operationen in 1 reduziert

---

#### `wait_and_click`

Polling bis Bild erscheint, dann klicken.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `image_path` | str | Ja | - | Vorlagenbildpfad |
| `similarity` | float | Nein | 0.9 | Ähnlichkeitsschwellenwert |
| `timeout` | float | Nein | 10 | Timeout (Sekunden) |
| `poll_interval` | float | Nein | 0.5 | Polling-Intervall (Sekunden) |
| `button` | str | Nein | "left" | Maustaste |
| `clicks` | int | Nein | 1 | Klickanzahl |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "clicked": true,
    "x": 500,
    "y": 300,
    "wait_time": 2.5
  }
}
```

**Häufige Fehlercodes**: E2001 (Timeout erreicht, Bild nicht erschienen)

**Anwendungsszenarien**:
- **Auf Oberfläche warten**: "Laden"-Bildschirm, dann auf "Start"-Schaltfläche klicken
- **Pop-up bestätigen**: "Möchten Sie speichern?"-Dialog, auf "Ja" warten und klicken
- **Spiel-Zustandsübergang**: "Kampf beendet"-Bild, dann auf "Aufheben" klicken

---

### 3.5 Text-Tools (OCR)

#### `set_ocr_dict`

OCR-Schriftbibliotheksdateipfad festlegen.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `dict_path` | str | Ja | Schriftbibliotheksdateipfad (omni-spezifisches Format) |

**Rückgabe**: `{"set": true}`

**Hinweise**: Vor ocr / find_text muss set_ocr_dict aufgerufen werden, sonst E4001-Fehler.

---

#### `ocr`

Text im angegebenen Bereich erkennen.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `top` | int | Nein | 0 | Bereich obere Koordinate |
| `left` | int | Nein | 0 | Bereich linke Koordinate |
| `right` | int | Nein | Bildschirmbreite | Bereich rechte Koordinate |
| `bottom` | int | Nein | Bildschirmhöhe | Bereich untere Koordinate |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "text": "Level: 42\nHP: 100/100"
  }
}
```

**Häufige Fehlercodes**:
- E4001 (Schriftbibliothek nicht gesetzt — set_ocr_dict zuerst aufrufen)
- E4002 (Erkennung fehlgeschlagen — Bereich zu klein / Text verschwommen)

**Anwendungsszenarien**:
- **Spiel-Daten lesen**: HP / Gold / Level-Text aus Spiel-UI extrahieren
- **Formularausfüllung**: Formularfeld-Text erkennen, um zu bestimmen, welches Feld ausgefüllt werden muss
- **Fehlermeldung**: Pop-up-Fehlermeldungstext erkennen

**Hinweise**: ocr gibt nur Text ohne Koordinaten zurück. Für Koordinaten find_image mit Text-Screenshot-Vorlage verwenden.

---

#### `find_text`

Text auf dem Bildschirm suchen.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `text` | str | Ja | - | Zu suchender Text |
| `top` | int | Nein | 0 | Bereich obere Koordinate |
| `left` | int | Nein | 0 | Bereich linke Koordinate |
| `right` | int | Nein | Bildschirmbreite | Bereich rechte Koordinate |
| `bottom` | int | Nein | Bildschirmhöhe | Bereich untere Koordinate |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "found": true,
    "x": 500,
    "y": 300
  }
}
```

**Häufige Fehlercodes**:
- E4001 (Schriftbibliothek nicht gesetzt)
- E4003 (Text nicht gefunden)

---

#### `ocr_and_click`

OCR-Textsuche, dann Bereichsmittelpunkt klicken.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `text` | str | Ja | - | Zu suchender Text |
| `button` | str | Nein | "left" | Maustaste |
| `clicks` | int | Nein | 1 | Klickanzahl |
| `top` | int | Nein | 0 | Bereich obere Koordinate |
| `left` | int | Nein | 0 | Bereich linke Koordinate |
| `right` | int | Nein | Bildschirmbreite | Bereich rechte Koordinate |
| `bottom` | int | Nein | Bildschirmhöhe | Bereich untere Koordinate |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "clicked": true,
    "x": 500,
    "y": 300,
    "text": "OK"
  }
}
```

**Anwendungsszenarien**: ⭐ AI-freundlich: "OK"-Text suchen und klicken, geeignet für dynamische Schaltflächen (Text ändert sich, Position unveränderlich)

---

### 3.6 Tastatur-/Maus-Tools

#### `key_press`

Tastaturtaste drücken und loslassen.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `key` | str | Ja | Tastenname, wie "enter", "tab", "f1", "a", "1" |

**Rückgabe**: `{"pressed": true}`

**Häufige Fehlercodes**: E5001 (Tastenname ungültig — z.B. "shift" + "a" hat falsches Format, nicht "shift+a")

**Anwendungsszenarien**:
- **Bestätigen**: key_press("enter") oder key_press("space")
- **Navigieren**: key_press("tab") Formularfeld wechseln
- **Funktionstasten**: key_press("f5") Seite aktualisieren

**Hinweise**: Kombinationen verwenden hotkey, nicht key_press.

---

#### `key_down` / `key_up`

Tastaturtaste halten / loslassen.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `key` | str | Ja | Tastenname |

**Rückgabe**: `{"down": true}` / `{"up": true}`

**Anwendungsszenarien**: Tastenkombination halten (z.B. Shift gedrückt halten, mehrere Dateien auswählen)

---

#### `key_type`

Zeichenfolge eingeben.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `text` | str | Ja | - | Eingabetext |
| `interval` | float | Nein | 0.01 | Tastenanschlagintervall (Sekunden) |

**Rückgabe**: `{"typed": true, "length": 12}`

**Anwendungsszenarien**:
- **Formularausfüllung**: Benutzername / Passwort / Suchbegriff eingeben
- **IME-Unterstützung**: interval=0.05 für chinesische Eingabe (Pinyin-Konvertierung braucht Zeit)

**Hinweise**: interval bei schneller Eingabe auf 0.01 setzen, bei chinesischer Eingabe auf 0.05 setzen

---

#### `hotkey`

Kombinationstasten senden.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `keys` | list | Ja | Tastenliste, wie ["ctrl", "c"] |

**Rückgabe**: `{"sent": true}`

**Gängige Kombinationen**:
- `hotkey(keys=["ctrl", "c"])` — Kopieren
- `hotkey(keys=["ctrl", "v"])` — Einfügen
- `hotkey(keys=["alt", "f4"])` — Fenster schließen
- `hotkey(keys=["ctrl", "shift", "esc"])` — Task-Manager öffnen

**Hinweise**: Tastenreihenfolge ist wichtig, Modifikatoren zuerst (ctrl / alt / shift), dann Buchstaben.

---

#### `mouse_move`

Maus bewegen.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `x` | int | Ja | - | Ziel-X-Koordinate |
| `y` | int | Ja | - | Ziel-Y-Koordinate |
| `duration` | float | Nein | 0.0 | Bewegungsdauer (Sekunden), 0 = sofort |

**Rückgabe**: `{"moved": true}`

**Anwendungsszenarien**:
- **Vor Screenshot**: mouse_move(0, 0) Cursor in die Ecke verschieben (vermeiden, dass Cursor auf dem Bild erscheint)
- **Tooltip auslösen**: Maus über Element bewegen, um Tooltip anzuzeigen
- **Drag-Vorbereitung**: Maus an Startposition bewegen

---

#### `mouse_click`

Maustaste klicken.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `x` | int | Nein | Aktuelle Position | Klick-X-Koordinate |
| `y` | int | Nein | Aktuelle Position | Klick-Y-Koordinate |
| `button` | str | Nein | "left" | Maustaste: left / right / middle |
| `clicks` | int | Nein | 1 | Klickanzahl |

**Rückgabe**: `{"clicked": true}`

**Häufige Fehlercodes**: E5002 (Eingabesperre — innerhalb von 500ms nach derselben Stelle erneut geklickt)

**Anwendungsszenarien**:
- **Schaltfläche klicken**: mouse_click(x=500, y=300)
- **Rechtsklick-Menü**: mouse_click(x=500, y=300, button="right")
- **Doppelklick**: mouse_click(x=500, y=300, clicks=2)

---

#### `mouse_scroll`

Mausrad scrollen.

| Parameter | Typ | Erforderlich | Standard | Beschreibung |
|---|---|---|---|---|
| `clicks` | int | Ja | - | Scrollmenge, positiv = nach oben, negativ = nach unten |

**Rückgabe**: `{"scrolled": true}`

**Anwendungsszenarien**: In Listen / Webseiten scrollen, um Elemente außerhalb des Sichtbereichs anzuzeigen

---

#### `mouse_get_pos`

Aktuelle Mausposition abrufen.

| Parameter | Erforderlich | Beschreibung |
|---|---|---|
| Keine | - | - |

**Rückgabe**: `{"x": 500, "y": 300}`

---

### 3.7 Speicher-Tools

#### `mem_read`

Prozessspeicher lesen.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `pid` | int | Ja | Zielprozess-PID |
| `address` | int/str | Ja | Speicheradresse (dezimal oder hexadezimal, wie "0x12345678") |
| `size` | int | Nein | 4 | Lesegröße (Bytes) |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "hex": "2A000000",
    "int": 42
  }
}
```

**Häufige Fehlercodes**: E6001 (Speicherzugriff verweigert — Speicher nicht lesbar / Adresse außerhalb des Prozesses)

**Hinweise**: Speicheroperationen sind riskant, können Spiel abstürzen lassen oder verboten sein. **Nicht empfohlen**.

---

#### `mem_write`

Prozessspeicher schreiben.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `pid` | int | Ja | Zielprozess-PID |
| `address` | int/str | Ja | Speicheradresse |
| `data_hex` | str | Ja | Hexadezimale Datencode, wie "2A000000" |

**Rückgabe**: `{"written": true}`

**Häufige Fehlercodes**: E6002 (Formatfehler — Hex-Daten-Länge ist keine gerade Anzahl)

**Hinweise**: **Nicht empfohlen** — falscher Adress-Schreiben kann Spiel abstürzen lassen oder verboten sein.

---

#### `get_module_base`

Basisadresse des Prozessmoduls abrufen.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `pid` | int | Ja | Zielprozess-PID |
| `module_name` | str | Nein | - | Modulname, wie "game.exe" |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "base_address": "0x00400000"
  }
}
```

**Anwendungsszenarien**: Für Speicher-Adressberechnung (meist mit mem_read / mem_write zusammen verwendet)

---

### 3.8 Workflow-Tools

#### `workflow_run`

Gespeicherten Workflow ausführen.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `workflow_id` | str | Ja | Workflow-ID oder Name |
| `variables` | dict | Nein | {} | Initiale Variablenwerte |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "status": "completed",
    "steps_executed": 10,
    "results": { ... }
  }
}
```

**Häufige Fehlercodes**:
- E8001 (Workflow nicht gefunden)
- E8002 (Workflow-Knotenfehler — Knotentyp ungültig / Schritt-ID dupliziert / Bedingungsausdruck Syntaxfehler)

---

#### `workflow_list`

Alle gespeicherten Workflows auflisten.

| Parameter | Erforderlich | Beschreibung |
|---|---|---|
| Keine | - | - |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "workflows": [
      {"id": "auto_login", "name": "Auto Login", "steps": 5},
      {"id": "daily_task", "name": "Daily Task", "steps": 12}
    ]
  }
}
```

---

#### `workflow_save`

Workflow speichern.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `name` | str | Ja | Workflow-Name |
| `steps` | list | Ja | Workflow-Schritte-Liste |

**Rückgabe**: `{"saved": true, "workflow_id": "auto_login"}`

**Schrittformat** (v2 Engine unterstützte Knoten):

```json
{
  "id": "step1",
  "type": "tool_call",
  "tool": "window_find",
  "inputs": {
    "title": "Login Window"
  },
  "outputs": {
    "hwnd": "login_hwnd"
  }
}
```

**Unterstützte Knotentypen**: `tool_call`, `condition`, `if`, `loop`, `delay`, `subflow`, `wait_for_window`

---

#### `workflow_delete`

Workflow löschen.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `workflow_id` | str | Ja | Workflow-ID oder Name |

**Rückgabe**: `{"deleted": true}`

---

#### `workflow_pause`

Workflow-Ausführung pausieren.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `workflow_id` | str | Ja | Workflow-ID |

**Rückgabe**: `{"paused": true}`

---

#### `workflow_resume`

Workflow-Ausführung fortsetzen.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `workflow_id` | str | Ja | Workflow-ID |

**Rückgabe**: `{"resumed": true}`

---

### 3.9 Plugin-Tools

#### `plugin_list`

Installierte Plugins auflisten.

| Parameter | Erforderlich | Beschreibung |
|---|---|---|
| Keine | - | - |

**Rückgabe**:
```json
{
  "success": true,
  "data": {
    "plugins": [
      {"name": "web_automation", "version": "1.0.0", "enabled": true},
      {"name": "database_connector", "version": "0.5.0", "enabled": false}
    ]
  }
}
```

---

#### `plugin_install`

Plugin installieren.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `source` | str | Ja | Plugin-Quelle (URL oder lokaler Pfad) |

**Rückgabe**: `{"installed": true, "plugin_name": "web_automation"}`

---

#### `plugin_uninstall`

Plugin deinstallieren.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `plugin_name` | str | Ja | Plugin-Name |

**Rückgabe**: `{"uninstalled": true}`

---

#### `plugin_enable`

Plugin aktivieren.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `plugin_name` | str | Ja | Plugin-Name |

**Rückgabe**: `{"enabled": true}`

---

#### `plugin_disable`

Plugin deaktivieren.

| Parameter | Typ | Erforderlich | Beschreibung |
|---|---|---|---|
| `plugin_name` | str | Ja | Plugin-Name |

**Rückgabe**: `{"disabled": true}`

---

## 4. Designprinzipien

### 4.1 Sicherheit zuerst

- **Speicheroperationen nicht empfohlen**: `mem_read` / `mem_write` können Spiel abstürzen lassen oder verboten sein
- **Vor Schreiboperationen bestätigen**: `mem_write` / `key_type` / `mouse_click` haben Nebenwirkungen
- **Vor Hintergrundoperationen bind_window**: verhindern, dass Tastatur/Maus von anderen Fenstern gestohlen wird

### 4.2 Fehlertoleranz

- **Fehlermeldungen enthalten recovery_suggestions**: bei Fehlern zuerst hier prüfen
- **AI aktiv recovery_suggestions prüfen lassen**: nicht blind wiederholen
- **Kombi-Tools verwenden**: click_image / wait_and_click reduzieren Fehlerwahrscheinlichkeit

### 4.3 Effizienz

- **Kombi-Tools priorisieren**: click_image statt find_image + mouse_move + mouse_click
- **Workflow-Engine für wiederholbare Aufgaben**: Speichern und Wiederverwenden
- **Vorlagenbildladen ist zwischengespeichert**: Mehrmalige Suche schneller

### 4.4 Lesbarkeit

- **Einheitliches Rückgabeformat**: Alle Tools geben gleiche Struktur zurück
- **Fehlercodes sind modular**: Schnelle Identifikation der Problemkategorie
- **Menschenlesbare Nachrichten**: message-Feld ist direkt verständlich
