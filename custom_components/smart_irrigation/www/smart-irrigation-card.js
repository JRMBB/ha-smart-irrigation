/**
 * Smart Irrigation Card
 * Custom Lovelace Card für die Smart Irrigation Integration
 * 
 * Verwendung:
 * type: custom:smart-irrigation-card
 * zones:
 *   - name: Rasen
 *     moisture_entity: sensor.bewasserung_rasen_feuchtigkeit
 *     status_entity: sensor.bewasserung_rasen_status
 *     rain_entity: sensor.bewasserung_rasen_regenvorhersage
 *     watering_entity: binary_sensor.bewasserung_rasen_aktiv
 *     rain_expected_entity: binary_sensor.bewasserung_rasen_regen_erwartet
 *     enable_entity: switch.bewasserung_rasen_aktiv
 */

const CARD_VERSION = '1.0.0';

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

  :host {
    --si-bg: var(--card-background-color, #1a1f2e);
    --si-text: var(--primary-text-color, #e1e5ee);
    --si-text-secondary: var(--secondary-text-color, #8892a4);
    --si-accent: #22c55e;
    --si-accent-glow: rgba(34, 197, 94, 0.15);
    --si-water-blue: #38bdf8;
    --si-rain-blue: #60a5fa;
    --si-warning: #f59e0b;
    --si-danger: #ef4444;
    --si-card-bg: var(--ha-card-background, rgba(255,255,255,0.03));
    --si-border: rgba(255,255,255,0.06);
    --si-radius: 16px;
    --si-radius-sm: 10px;
    font-family: 'DM Sans', sans-serif;
  }

  ha-card {
    background: var(--si-bg);
    border: 1px solid var(--si-border);
    border-radius: var(--si-radius);
    overflow: hidden;
    padding: 0;
  }

  /* ── Header ── */
  .si-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 24px 12px;
  }
  .si-header-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .si-logo {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--si-accent), #16a34a);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 16px var(--si-accent-glow);
  }
  .si-logo ha-icon {
    color: #fff;
    --mdc-icon-size: 22px;
  }
  .si-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--si-text);
    letter-spacing: -0.02em;
  }
  .si-subtitle {
    font-size: 12px;
    color: var(--si-text-secondary);
    margin-top: 1px;
  }
  .si-header-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .si-header-badge.active {
    background: var(--si-accent-glow);
    color: var(--si-accent);
    border: 1px solid rgba(34,197,94,0.2);
  }
  .si-header-badge.idle {
    background: rgba(255,255,255,0.05);
    color: var(--si-text-secondary);
    border: 1px solid var(--si-border);
  }

  /* ── Summary Bar ── */
  .si-summary {
    display: flex;
    gap: 1px;
    margin: 0 24px 16px;
    background: var(--si-border);
    border-radius: var(--si-radius-sm);
    overflow: hidden;
  }
  .si-summary-item {
    flex: 1;
    padding: 12px 8px;
    text-align: center;
    background: var(--si-card-bg);
  }
  .si-summary-item:first-child { border-radius: var(--si-radius-sm) 0 0 var(--si-radius-sm); }
  .si-summary-item:last-child { border-radius: 0 var(--si-radius-sm) var(--si-radius-sm) 0; }
  .si-summary-value {
    font-size: 20px;
    font-weight: 700;
    color: var(--si-text);
  }
  .si-summary-label {
    font-size: 10px;
    color: var(--si-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 2px;
  }

  /* ── Zone Cards ── */
  .si-zones {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 0 16px 16px;
  }

  .si-zone {
    background: var(--si-card-bg);
    border: 1px solid var(--si-border);
    border-radius: var(--si-radius-sm);
    overflow: hidden;
    transition: border-color 0.3s, box-shadow 0.3s;
  }
  .si-zone.watering {
    border-color: rgba(56, 189, 248, 0.3);
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.08);
  }
  .si-zone.disabled {
    opacity: 0.5;
  }

  /* Zone header row */
  .si-zone-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 16px 8px;
  }
  .si-zone-name-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .si-zone-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .si-zone-icon.idle {
    background: rgba(255,255,255,0.05);
  }
  .si-zone-icon.idle ha-icon {
    color: var(--si-text-secondary);
    --mdc-icon-size: 18px;
  }
  .si-zone-icon.watering {
    background: rgba(56, 189, 248, 0.15);
    animation: si-pulse 2s ease-in-out infinite;
  }
  .si-zone-icon.watering ha-icon {
    color: var(--si-water-blue);
    --mdc-icon-size: 18px;
  }
  .si-zone-icon.rain {
    background: rgba(96, 165, 250, 0.15);
  }
  .si-zone-icon.rain ha-icon {
    color: var(--si-rain-blue);
    --mdc-icon-size: 18px;
  }

  @keyframes si-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(56,189,248,0.3); }
    50% { box-shadow: 0 0 0 8px rgba(56,189,248,0); }
  }

  .si-zone-name {
    font-size: 14px;
    font-weight: 600;
    color: var(--si-text);
  }
  .si-zone-status {
    font-size: 11px;
    color: var(--si-text-secondary);
    margin-top: 1px;
  }
  .si-zone-status.watering {
    color: var(--si-water-blue);
    font-weight: 500;
  }

  /* Toggle */
  .si-toggle {
    position: relative;
    width: 42px;
    height: 24px;
    flex-shrink: 0;
    cursor: pointer;
  }
  .si-toggle input {
    opacity: 0;
    width: 0;
    height: 0;
  }
  .si-toggle-track {
    position: absolute;
    inset: 0;
    border-radius: 12px;
    background: rgba(255,255,255,0.1);
    transition: background 0.3s;
  }
  .si-toggle input:checked + .si-toggle-track {
    background: var(--si-accent);
  }
  .si-toggle-thumb {
    position: absolute;
    top: 3px;
    left: 3px;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #fff;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 4px rgba(0,0,0,0.3);
  }
  .si-toggle input:checked ~ .si-toggle-thumb {
    transform: translateX(18px);
  }

  /* Zone metrics row */
  .si-zone-metrics {
    display: flex;
    gap: 1px;
    margin: 0 12px;
    background: var(--si-border);
    border-radius: 8px;
    overflow: hidden;
  }
  .si-metric {
    flex: 1;
    padding: 10px 8px;
    text-align: center;
    background: rgba(0,0,0,0.15);
  }
  .si-metric:first-child { border-radius: 8px 0 0 8px; }
  .si-metric:last-child { border-radius: 0 8px 8px 0; }
  .si-metric-icon {
    --mdc-icon-size: 14px;
    margin-bottom: 4px;
  }
  .si-metric-value {
    font-size: 16px;
    font-weight: 700;
    color: var(--si-text);
  }
  .si-metric-label {
    font-size: 9px;
    color: var(--si-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 2px;
  }

  /* Moisture bar */
  .si-moisture-bar-container {
    padding: 10px 16px 14px;
  }
  .si-moisture-bar-bg {
    height: 6px;
    background: rgba(255,255,255,0.06);
    border-radius: 3px;
    overflow: hidden;
    position: relative;
  }
  .si-moisture-bar {
    height: 100%;
    border-radius: 3px;
    transition: width 1s ease;
    position: relative;
  }
  .si-moisture-bar.low {
    background: linear-gradient(90deg, var(--si-danger), var(--si-warning));
  }
  .si-moisture-bar.ok {
    background: linear-gradient(90deg, var(--si-accent), #4ade80);
  }
  .si-moisture-bar.high {
    background: linear-gradient(90deg, var(--si-water-blue), var(--si-rain-blue));
  }
  .si-moisture-markers {
    display: flex;
    justify-content: space-between;
    margin-top: 4px;
  }
  .si-moisture-marker {
    font-size: 9px;
    color: var(--si-text-secondary);
  }

  /* Zone action buttons */
  .si-zone-actions {
    display: flex;
    gap: 6px;
    padding: 0 12px 12px;
  }
  .si-btn {
    flex: 1;
    padding: 8px 6px;
    border: 1px solid var(--si-border);
    border-radius: 8px;
    background: transparent;
    color: var(--si-text-secondary);
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    transition: all 0.2s;
  }
  .si-btn:hover {
    background: rgba(255,255,255,0.05);
    color: var(--si-text);
    border-color: rgba(255,255,255,0.12);
  }
  .si-btn.water {
    border-color: rgba(56,189,248,0.2);
    color: var(--si-water-blue);
  }
  .si-btn.water:hover {
    background: rgba(56,189,248,0.1);
  }
  .si-btn.stop {
    border-color: rgba(239,68,68,0.2);
    color: var(--si-danger);
  }
  .si-btn.stop:hover {
    background: rgba(239,68,68,0.1);
  }
  .si-btn ha-icon {
    --mdc-icon-size: 14px;
  }

  /* ── Footer ── */
  .si-footer {
    padding: 10px 24px 14px;
    border-top: 1px solid var(--si-border);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .si-footer-text {
    font-size: 10px;
    color: var(--si-text-secondary);
  }
  .si-footer-btn {
    padding: 5px 14px;
    border-radius: 6px;
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--si-border);
    color: var(--si-text-secondary);
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
    transition: all 0.2s;
  }
  .si-footer-btn:hover {
    background: rgba(255,255,255,0.08);
    color: var(--si-text);
  }
  .si-footer-btn ha-icon {
    --mdc-icon-size: 14px;
  }

  /* No zones */
  .si-empty {
    padding: 40px 24px;
    text-align: center;
    color: var(--si-text-secondary);
  }
  .si-empty ha-icon {
    --mdc-icon-size: 48px;
    color: rgba(255,255,255,0.1);
    margin-bottom: 12px;
    display: block;
  }
  .si-empty-text {
    font-size: 14px;
  }
`;

class SmartIrrigationCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._hass = null;
    this._config = null;
  }

  static getConfigElement() {
    return document.createElement('smart-irrigation-card-editor');
  }

  static getStubConfig() {
    return {
      zones: []
    };
  }

  setConfig(config) {
    if (!config.zones || !Array.isArray(config.zones)) {
      throw new Error('Bitte konfiguriere mindestens eine Zone.');
    }
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _getState(entityId) {
    if (!this._hass || !entityId) return null;
    return this._hass.states[entityId] || null;
  }

  _getStateValue(entityId, fallback = '–') {
    const state = this._getState(entityId);
    if (!state || state.state === 'unavailable' || state.state === 'unknown') return fallback;
    return state.state;
  }

  _getNumericValue(entityId, fallback = null) {
    const val = this._getStateValue(entityId, null);
    if (val === null) return fallback;
    const num = parseFloat(val);
    return isNaN(num) ? fallback : num;
  }

  _isOn(entityId) {
    return this._getStateValue(entityId) === 'on';
  }

  _callService(domain, service, data) {
    if (this._hass) {
      this._hass.callService(domain, service, data);
    }
  }

  _getMoistureClass(value, zone) {
    if (value === null) return 'ok';
    const low = zone.moisture_low || 30;
    const high = zone.moisture_high || 60;
    if (value < low) return 'low';
    if (value > high) return 'high';
    return 'ok';
  }

  _getZoneIconState(zone) {
    if (this._isOn(zone.watering_entity)) return 'watering';
    if (this._isOn(zone.rain_expected_entity)) return 'rain';
    return 'idle';
  }

  _getZoneIcon(iconState) {
    switch (iconState) {
      case 'watering': return 'mdi:sprinkler';
      case 'rain': return 'mdi:weather-rainy';
      default: return 'mdi:sprinkler-variant';
    }
  }

  _render() {
    if (!this._config || !this._hass) return;

    const zones = this._config.zones || [];
    
    // Calculate summary
    let totalZones = zones.length;
    let activeCount = 0;
    let wateringCount = 0;
    let rainCount = 0;

    zones.forEach(z => {
      if (this._isOn(z.enable_entity)) activeCount++;
      if (this._isOn(z.watering_entity)) wateringCount++;
      if (this._isOn(z.rain_expected_entity)) rainCount++;
    });

    const isAnyWatering = wateringCount > 0;

    this.shadowRoot.innerHTML = `
      <style>${styles}</style>
      <ha-card>
        <div class="si-header">
          <div class="si-header-left">
            <div class="si-logo">
              <ha-icon icon="mdi:sprinkler"></ha-icon>
            </div>
            <div>
              <div class="si-title">${this._config.title || 'Bewässerung'}</div>
              <div class="si-subtitle">${totalZones} Zone${totalZones !== 1 ? 'n' : ''} konfiguriert</div>
            </div>
          </div>
          <div class="si-header-badge ${isAnyWatering ? 'active' : 'idle'}">
            ${isAnyWatering ? '● Aktiv' : 'Standby'}
          </div>
        </div>

        <div class="si-summary">
          <div class="si-summary-item">
            <div class="si-summary-value" style="color: var(--si-accent)">${activeCount}</div>
            <div class="si-summary-label">Aktiv</div>
          </div>
          <div class="si-summary-item">
            <div class="si-summary-value" style="color: var(--si-water-blue)">${wateringCount}</div>
            <div class="si-summary-label">Bewässert</div>
          </div>
          <div class="si-summary-item">
            <div class="si-summary-value" style="color: var(--si-rain-blue)">${rainCount}</div>
            <div class="si-summary-label">Regen</div>
          </div>
        </div>

        ${zones.length === 0 ? `
          <div class="si-empty">
            <ha-icon icon="mdi:sprinkler-variant"></ha-icon>
            <div class="si-empty-text">Keine Zonen konfiguriert</div>
          </div>
        ` : `
          <div class="si-zones">
            ${zones.map((zone, i) => this._renderZone(zone, i)).join('')}
          </div>
        `}

        <div class="si-footer">
          <div class="si-footer-text">Smart Irrigation v${CARD_VERSION}</div>
          <button class="si-footer-btn" id="btn-force-check">
            <ha-icon icon="mdi:refresh"></ha-icon>
            Prüfen
          </button>
        </div>
      </ha-card>
    `;

    // Bind events
    this._bindEvents();
  }

  _renderZone(zone, index) {
    const isWatering = this._isOn(zone.watering_entity);
    const isEnabled = this._isOn(zone.enable_entity);
    const moisture = this._getNumericValue(zone.moisture_entity);
    const rain = this._getNumericValue(zone.rain_entity, 0);
    const status = this._getStateValue(zone.status_entity, 'Unbekannt');
    const iconState = this._getZoneIconState(zone);
    const moistureClass = this._getMoistureClass(moisture, zone);
    const isRainExpected = this._isOn(zone.rain_expected_entity);

    // Get attributes for schedule info
    const statusState = this._getState(zone.status_entity);
    const schedule = statusState?.attributes?.schedule || '';
    const lastWatered = statusState?.attributes?.last_watered || null;

    let statusText = status;
    if (isWatering) statusText = 'Bewässert gerade…';

    return `
      <div class="si-zone ${isWatering ? 'watering' : ''} ${!isEnabled ? 'disabled' : ''}" data-zone="${index}">
        <div class="si-zone-header">
          <div class="si-zone-name-row">
            <div class="si-zone-icon ${iconState}">
              <ha-icon icon="${this._getZoneIcon(iconState)}"></ha-icon>
            </div>
            <div>
              <div class="si-zone-name">${zone.name || 'Zone ' + (index + 1)}</div>
              <div class="si-zone-status ${isWatering ? 'watering' : ''}">${statusText}</div>
            </div>
          </div>
          <label class="si-toggle" data-entity="${zone.enable_entity}">
            <input type="checkbox" ${isEnabled ? 'checked' : ''}>
            <div class="si-toggle-track"></div>
            <div class="si-toggle-thumb"></div>
          </label>
        </div>

        <div class="si-zone-metrics">
          <div class="si-metric">
            <ha-icon class="si-metric-icon" icon="mdi:water-percent" style="color: ${moistureClass === 'low' ? 'var(--si-danger)' : moistureClass === 'high' ? 'var(--si-water-blue)' : 'var(--si-accent)'}"></ha-icon>
            <div class="si-metric-value">${moisture !== null ? Math.round(moisture) + '%' : '–'}</div>
            <div class="si-metric-label">Feuchtigkeit</div>
          </div>
          <div class="si-metric">
            <ha-icon class="si-metric-icon" icon="mdi:weather-pouring" style="color: ${isRainExpected ? 'var(--si-rain-blue)' : 'var(--si-text-secondary)'}"></ha-icon>
            <div class="si-metric-value">${rain.toFixed(1)}<span style="font-size:11px">mm</span></div>
            <div class="si-metric-label">Regen 24h</div>
          </div>
          <div class="si-metric">
            <ha-icon class="si-metric-icon" icon="mdi:clock-outline" style="color: var(--si-text-secondary)"></ha-icon>
            <div class="si-metric-value" style="font-size:12px">${schedule || '–'}</div>
            <div class="si-metric-label">Zeitfenster</div>
          </div>
        </div>

        ${moisture !== null ? `
          <div class="si-moisture-bar-container">
            <div class="si-moisture-bar-bg">
              <div class="si-moisture-bar ${moistureClass}" style="width: ${Math.min(100, Math.max(0, moisture))}%"></div>
            </div>
            <div class="si-moisture-markers">
              <span class="si-moisture-marker">0%</span>
              <span class="si-moisture-marker">${zone.moisture_low || 30}%</span>
              <span class="si-moisture-marker">${zone.moisture_high || 60}%</span>
              <span class="si-moisture-marker">100%</span>
            </div>
          </div>
        ` : ''}

        <div class="si-zone-actions">
          ${isWatering ? `
            <button class="si-btn stop" data-action="stop" data-zone-id="${zone.zone_id || zone.name.toLowerCase().replace(/\\s+/g, '_')}">
              <ha-icon icon="mdi:stop"></ha-icon>
              Stoppen
            </button>
          ` : `
            <button class="si-btn water" data-action="water" data-zone-id="${zone.zone_id || zone.name.toLowerCase().replace(/\\s+/g, '_')}">
              <ha-icon icon="mdi:play"></ha-icon>
              Manuell
            </button>
          `}
          <button class="si-btn" data-action="skip" data-zone-id="${zone.zone_id || zone.name.toLowerCase().replace(/\\s+/g, '_')}">
            <ha-icon icon="mdi:skip-next"></ha-icon>
            Überspringen
          </button>
        </div>
      </div>
    `;
  }

  _bindEvents() {
    // Toggle switches
    this.shadowRoot.querySelectorAll('.si-toggle').forEach(toggle => {
      toggle.addEventListener('click', (e) => {
        e.preventDefault();
        const entityId = toggle.dataset.entity;
        if (entityId) {
          const input = toggle.querySelector('input');
          const service = input.checked ? 'turn_off' : 'turn_on';
          this._callService('switch', service, { entity_id: entityId });
        }
      });
    });

    // Action buttons
    this.shadowRoot.querySelectorAll('.si-btn[data-action]').forEach(btn => {
      btn.addEventListener('click', () => {
        const action = btn.dataset.action;
        const zoneId = btn.dataset.zoneId;

        switch (action) {
          case 'water':
            this._callService('smart_irrigation', 'manual_water', { zone_id: zoneId });
            break;
          case 'stop':
            // Find the switch entity for this zone and turn it off
            const zone = this._config.zones.find(z => 
              (z.zone_id || z.name.toLowerCase().replace(/\s+/g, '_')) === zoneId
            );
            if (zone?.enable_entity) {
              // Toggle off then on to stop current watering
              const switchEntity = zone.enable_entity.replace('_aktiv', '_aktiv');
              this._callService('switch', 'turn_off', { entity_id: switchEntity });
            }
            break;
          case 'skip':
            this._callService('smart_irrigation', 'skip_next', { zone_id: zoneId });
            break;
        }
      });
    });

    // Force check button
    const forceBtn = this.shadowRoot.getElementById('btn-force-check');
    if (forceBtn) {
      forceBtn.addEventListener('click', () => {
        this._callService('smart_irrigation', 'force_check', {});
      });
    }
  }

  getCardSize() {
    const zones = this._config?.zones?.length || 0;
    return 3 + zones * 3;
  }
}

/* ── Card Editor ── */
class SmartIrrigationCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
  }

  _render() {
    this.shadowRoot.innerHTML = `
      <style>
        .editor { padding: 16px; font-family: sans-serif; }
        .editor label { display: block; margin: 8px 0 4px; font-weight: 500; font-size: 14px; }
        .editor textarea { width: 100%; min-height: 200px; font-family: monospace; font-size: 13px; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        .editor p { font-size: 12px; color: #888; margin-top: 4px; }
      </style>
      <div class="editor">
        <label>Konfiguration (YAML)</label>
        <p>Konfiguriere die Card über den YAML-Editor.</p>
        <p>Beispiel: zones: [{name: "Rasen", moisture_entity: "sensor.bewasserung_rasen_feuchtigkeit", ...}]</p>
      </div>
    `;
  }
}

customElements.define('smart-irrigation-card', SmartIrrigationCard);
customElements.define('smart-irrigation-card-editor', SmartIrrigationCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'smart-irrigation-card',
  name: 'Smart Irrigation Card',
  description: 'Bewässerungs-Schaltzentrale mit Zonen, Feuchtigkeit und Wettervorhersage',
  preview: true,
  documentationURL: 'https://github.com/JRMBB/ha-smart-irrigation',
});

console.info(
  `%c SMART-IRRIGATION-CARD %c v${CARD_VERSION} `,
  'color: white; background: #22c55e; font-weight: 700; padding: 2px 6px; border-radius: 4px 0 0 4px',
  'color: #22c55e; background: #1a1f2e; font-weight: 700; padding: 2px 6px; border-radius: 0 4px 4px 0'
);
