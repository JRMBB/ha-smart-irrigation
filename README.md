# 🌱 Smart Irrigation - Home Assistant Integration

Intelligente Bewässerungssteuerung für Home Assistant. Plant und steuert die Bewässerung mehrerer Zonen basierend auf Bodenfeuchtigkeit, Zeitfenstern und Wettervorhersage.

## Features

- **Mehrere Bewässerungszonen** — Jede Zone mit eigenen Einstellungen
- **Bodenfeuchtigkeit** — Bewässerung nur wenn der Boden trocken genug ist
- **Wettervorhersage** — Kein Gießen wenn Regen erwartet wird (24h Vorhersage)
- **Zeitfenster** — Bewässerung nur zu bestimmten Uhrzeiten (z.B. morgens 6-8 Uhr)
- **UI-Konfiguration** — Komplett über die HA-Oberfläche einrichtbar (kein YAML)
- **Services** — Manuelles Starten, Überspringen, Sofort-Check
- **Deutsche & Englische UI**

## Installation

### HACS (empfohlen)

1. HACS öffnen → **Integrationen** → **⋮** (oben rechts) → **Benutzerdefinierte Repositories**
2. URL eingeben: `https://github.com/JRMBB/ha-smart-irrigation`
3. Kategorie: **Integration**
4. **Hinzufügen** → **Smart Irrigation** installieren
5. Home Assistant neu starten

### Manuell

1. Den Ordner `custom_components/smart_irrigation` in dein HA `config/custom_components/` kopieren
2. Home Assistant neu starten

## Einrichtung

1. **Einstellungen** → **Geräte & Dienste** → **Integration hinzufügen**
2. **Smart Irrigation** suchen
3. Zone konfigurieren:
   - **Zonenname** — z.B. "Rasen", "Hochbeet", "Hecke"
   - **Ventil/Schalter** — Die Switch-Entity die das Magnetventil steuert
   - **Bodenfeuchtigkeit-Sensor** (optional) — z.B. Zigbee/Bluetooth Sensor
   - **Wetter-Entity** (optional) — Für Regenvorhersage
   - **Schwellwerte** — Ab wann bewässert werden soll
   - **Zeitfenster** — Wann bewässert werden darf
   - **Regenschwelle** — Ab wieviel mm erwartetem Regen nicht gegossen wird

## Entities pro Zone

| Entity | Typ | Beschreibung |
|--------|-----|--------------|
| `sensor.bewasserung_[zone]_feuchtigkeit` | Sensor | Aktuelle Bodenfeuchtigkeit |
| `sensor.bewasserung_[zone]_status` | Sensor | Status (Bereit/Bewässert/Pause) |
| `sensor.bewasserung_[zone]_regenvorhersage` | Sensor | Erwarteter Regen in mm |
| `binary_sensor.bewasserung_[zone]_aktiv` | Binary Sensor | Bewässerung läuft ja/nein |
| `binary_sensor.bewasserung_[zone]_regen_erwartet` | Binary Sensor | Regen erwartet ja/nein |
| `switch.bewasserung_[zone]_aktiv` | Switch | Zone aktivieren/deaktivieren |

## Services

| Service | Beschreibung |
|---------|--------------|
| `smart_irrigation.manual_water` | Zone manuell bewässern (mit optionaler Dauer) |
| `smart_irrigation.skip_next` | Nächste Bewässerung überspringen |
| `smart_irrigation.force_check` | Alle Zonen sofort prüfen |

## Bewässerungslogik

```
Alle 5 Minuten prüft die Integration:
1. Ist die Zone aktiviert? → Sonst überspringen
2. Sind wir im Zeitfenster? → Sonst warten
3. Ist Regen vorhergesagt (>Schwelle)? → Dann überspringen
4. Ist die Bodenfeuchtigkeit unter dem Schwellwert? → Dann bewässern
5. Kein Sensor vorhanden? → Nach Zeitplan bewässern
6. Wurde in den letzten 4h bereits bewässert? → Dann überspringen
```

## Beispiel-Automatisierung

```yaml
automation:
  - alias: "Bewässerung Benachrichtigung"
    trigger:
      - platform: state
        entity_id: binary_sensor.bewasserung_rasen_aktiv
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "🌱 Bewässerung"
          message: "Rasen wird jetzt bewässert!"
```

## Hardware-Empfehlungen

- **Magnetventile:** 24V AC Ventile mit Zigbee/WiFi Relais (z.B. Shelly 1)
- **Bodenfeuchtigkeit:** Zigbee Sensoren (z.B. Xiaomi HHCCJCY01) oder ESP32 mit kapazitivem Sensor
- **Wetter:** HA-eigene Wetter-Integration oder OpenWeatherMap

## Lizenz

MIT License
