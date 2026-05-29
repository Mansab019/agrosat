// ── COLOR MAP FOR INDICES ──────────────────────────────────────────────────
const INDEX_COLORS = {
  NDVI:    '#39D353',
  EVI:     '#00B4D8',
  NDMI:    '#00B4D8',
  NDWI:    '#0080FF',
  LST:     '#F4A623',
  SAR_RVI: '#F85149',
};

// ── INITIALIZE MAP ─────────────────────────────────────────────────────────
const map = L.map('map').setView([31.5214, 74.3597], 15);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap'
}).addTo(map);

// ── FETCH INDICES ──────────────────────────────────────────────────────────
fetch('/api/indices/')
  .then(r => r.json())
  .then(data => {

    // Draw farm polygon on map
    const poly = L.polygon(data.farm_polygon, {
      color: '#39D353',
      fillColor: '#39D353',
      fillOpacity: 0.25,
      weight: 2
    }).addTo(map);
    poly.bindPopup('<b>Sample Farm</b><br>Punjab, Pakistan');
    map.fitBounds(poly.getBounds());

    // Build index cards
    const grid = document.getElementById('indicesGrid');
    grid.innerHTML = '';
    for (const [key, idx] of Object.entries(data.indices)) {
      const color = INDEX_COLORS[key] || '#F0F6FF';
      grid.innerHTML += `
        <div class="index-card">
          <div class="name"  style="color:${color}">${key}</div>
          <div class="value" style="color:${color}">${idx.value}${idx.unit}</div>
          <div class="label">${idx.label}</div>
        </div>`;
    }

    // Weather row
    const w = data.weather;
    document.getElementById('weatherRow').innerHTML = `
      <div class="weather-item">
        <div class="wval">${w.temperature}°C</div>
        <div class="wlab">Air Temperature</div>
      </div>
      <div class="weather-item">
        <div class="wval">${w.humidity}%</div>
        <div class="wlab">Humidity</div>
      </div>
      <div class="weather-item">
        <div class="wval">${(w.soil_moisture * 100).toFixed(1)}%</div>
        <div class="wlab">Soil Moisture</div>
      </div>`;

    // Generate alerts
    const idx = data.indices;
    const alerts = [];

    if (idx.NDVI.value >= 0.5)
      alerts.push({ text: '✅ Crop Health: Good', cls: 'alert-ok' });
    else if (idx.NDVI.value >= 0.3)
      alerts.push({ text: '⚠️ Crop Health: Monitor', cls: 'alert-warn' });
    else
      alerts.push({ text: '🚨 Crop Health: Critical', cls: 'alert-crit' });

    if (idx.NDMI.value >= 0.1)
      alerts.push({ text: '✅ Moisture: Adequate', cls: 'alert-ok' });
    else
      alerts.push({ text: '⚠️ Irrigation Needed', cls: 'alert-warn' });

    if (idx.LST.value > 42)
      alerts.push({ text: '🚨 Heat Stress Detected', cls: 'alert-crit' });
    else if (idx.LST.value > 38)
      alerts.push({ text: '⚠️ High Temperature', cls: 'alert-warn' });
    else
      alerts.push({ text: '✅ Temperature: Normal', cls: 'alert-ok' });

    if (idx.SAR_RVI.value >= 0.5)
      alerts.push({ text: '✅ SAR Biomass: Dense', cls: 'alert-ok' });
    else
      alerts.push({ text: '⚠️ SAR Biomass: Sparse', cls: 'alert-warn' });

    document.getElementById('alertBar').innerHTML =
      alerts.map(a => `<span class="alert-item ${a.cls}">${a.text}</span>`).join('');
  });

// ── FETCH TIMESERIES + BUILD CHARTS ───────────────────────────────────────
fetch('/api/timeseries/')
  .then(r => r.json())
  .then(data => {

    const layout = () => ({
      paper_bgcolor: 'transparent',
      plot_bgcolor:  'transparent',
      margin: { t: 10, b: 40, l: 40, r: 10 },
      xaxis: {
        tickfont: { color: '#8B949E', size: 9 },
        gridcolor: '#30363D',
        tickangle: -45
      },
      yaxis: {
        tickfont: { color: '#8B949E', size: 9 },
        gridcolor: '#30363D'
      },
      showlegend: false,
    });

    const line = (x, y, color) => [{
      x, y,
      type: 'scatter',
      mode: 'lines+markers',
      line:   { color, width: 2, shape: 'spline' },
      marker: { color, size: 3 },
      fill:      'tozeroy',
      fillcolor:  color + '22',
    }];

    Plotly.newPlot('ndviChart',
      line(data.dates, data.ndvi, '#39D353'), layout(),
      { responsive: true, displayModeBar: false });

    Plotly.newPlot('ndmiChart',
      line(data.dates, data.ndmi, '#00B4D8'), layout(),
      { responsive: true, displayModeBar: false });

    Plotly.newPlot('lstChart',
      line(data.dates, data.lst, '#F4A623'), layout(),
      { responsive: true, displayModeBar: false });
  });