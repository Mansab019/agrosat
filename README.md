# 🛰 AgroSat Intelligence Platform

Satellite-powered crop health monitoring dashboard for Pakistani farmers.

Built by **Mansab Ali** — AI/ML Trainee, NetSol Technologies

---

## What It Does

AgroSat scrapes real weather and satellite-derived data, computes
6 spectral indices over a farm polygon, and visualizes them as:

- Interactive farm map with polygon overlay
- Live spectral index cards (NDVI, EVI, NDMI, NDWI, LST, SAR-RVI)
- 30-day trend charts for NDVI, NDMI, and LST
- Smart alerts for crop health, moisture, and heat stress

---

## 6 Key Indices

| Index | Detects | Source |
|-------|---------|--------|
| NDVI | Crop greenness & health | Sentinel-2 |
| EVI | Dense canopy, yield estimation | Sentinel-2 |
| NDMI | Plant moisture, drought early warning | Sentinel-2 |
| NDWI | Surface water & flooding | Sentinel-2 |
| LST | Ground temperature, heat stress | Landsat/MODIS |
| SAR-RVI | Radar biomass (works through clouds) | Sentinel-1 |

---

## Tech Stack

- **Backend:** Python, Django 5.2
- **Frontend:** HTML, CSS, JavaScript
- **Maps:** Leaflet.js
- **Charts:** Plotly.js
- **Data:** Open-Meteo API (real-time weather)
- **Architecture:** REST API + Django Template Engine

---

## Project Structure