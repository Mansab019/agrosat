import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
import random
import os
import base64
import requests
from io import BytesIO
from PIL import Image
import math

# ── Farm polygon (Punjab, Pakistan — sample wheat farm) ──────────────────────
FARM_POLYGON = [
    [31.5204, 74.3587],
    [31.5224, 74.3587],
    [31.5224, 74.3607],
    [31.5204, 74.3607],
    [31.5204, 74.3587],
]

FARM_CENTER = [31.5214, 74.3597]  # Lahore region

# ── 1. Main dashboard page ────────────────────────────────────────────────────
def index(request):
    return render(request, 'agroboard/index.html')

# ── 2. API: current index values ──────────────────────────────────────────────
def api_indices(request):
    # Fetch real weather data from Open-Meteo (no API key needed)
    try:
        lat = request.GET.get('lat', '31.5214')
        lon = request.GET.get('lon', '74.3597')

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,"
            "soil_moisture_0_to_1cm,et0_fao_evapotranspiration"
            "&daily=temperature_2m_max,precipitation_sum"
            "&forecast_days=1"
        )
        response = requests.get(url, timeout=5)
        weather = response.json()

        temp     = weather['current']['temperature_2m']
        humidity = weather['current']['relative_humidity_2m']
        soil_moist = weather['current']['soil_moisture_0_to_1cm']

    except Exception:
        # Fallback if API is down
        temp, humidity, soil_moist = 34.0, 55.0, 0.18
        
    # Derive location-sensitive index values
    # Using more weather variables for spatial variation

    lat_f = float(lat)
    lon_f = float(lon)

    # NDVI: vegetation index — driven by humidity + soil + small lat/lon variation
    # lat/lon add spatial uniqueness so nearby points differ slightly
    ndvi = round(min(0.85, max(0.1,
        0.25
        + (humidity / 250)
        + (soil_moist * 2.0)
        + (math.sin(lat_f * 10) * 0.04)
        + (math.cos(lon_f * 10) * 0.03)
    )), 2)

    # EVI: enhanced vegetation — slightly lower than NDVI
    evi = round(min(0.80, max(0.1, ndvi * 0.87 + (math.cos(lat_f * 7) * 0.02))), 2)

    # NDMI: moisture index — soil moisture dominant driver
    ndmi = round(min(0.6, max(-0.3,
        soil_moist * 3.0
        - 0.15
        + (math.sin(lon_f * 8) * 0.03)
    )), 2)

    # NDWI: surface water — very low unless flooded
    ndwi = round(min(0.4, max(-0.4,
        soil_moist * 2.0
        - 0.3
        + (math.cos(lat_f * 12) * 0.02)
    )), 2)

    # LST: land surface temp — driven by air temp + lat variation
    lst = round(temp + 3.5 + (math.sin(lat_f * 5) * 1.5) + (math.cos(lon_f * 6) * 1.2), 1)

    # SAR-RVI: radar biomass
    sar_rvi = round(min(0.9, max(0.1,
        ndvi * 0.82
        + (math.sin(lat_f * 9) * 0.03)
    )), 2)

    # Derive realistic index values from real weather data
    # NDVI: healthy crops in Pakistan range 0.4–0.8
    ndvi  = round(min(0.85, max(0.2, 0.3 + (humidity / 200) + (soil_moist * 1.5))), 2)
    # EVI: slightly lower than NDVI, more accurate in dense areas
    evi   = round(ndvi * 0.88, 2)
    # NDMI: moisture index driven by soil moisture
    ndmi  = round(min(0.6, max(-0.2, soil_moist * 2.5 - 0.1)), 2)
    # NDWI: surface water — low for farmland unless flooded
    ndwi  = round(min(0.4, max(-0.3, soil_moist * 1.8 - 0.25)), 2)
    # LST: derived from air temperature
    lst   = round(temp + random.uniform(2, 5), 1)
    # SAR-RVI: radar biomass 0–1
    sar_rvi = round(min(0.9, max(0.1, ndvi * 0.85 + random.uniform(-0.05, 0.05))), 2)

    return JsonResponse({
        'farm_center': FARM_CENTER,
        'farm_polygon': FARM_POLYGON,
        'indices': {
            'NDVI':    {'value': ndvi,    'unit': '',   'label': 'Crop Health'},
            'EVI':     {'value': evi,     'unit': '',   'label': 'Enhanced Vegetation'},
            'NDMI':    {'value': ndmi,    'unit': '',   'label': 'Moisture'},
            'NDWI':    {'value': ndwi,    'unit': '',   'label': 'Surface Water'},
            'LST':     {'value': lst,     'unit': '°C', 'label': 'Land Surface Temp'},
            'SAR_RVI': {'value': sar_rvi, 'unit': '',   'label': 'Radar Vegetation'},
        },
        'weather': {
            'temperature': temp,
            'humidity': humidity,
            'soil_moisture': soil_moist,
        }
    })

# ── 3. API: 30-day time series ────────────────────────────────────────────────
def api_timeseries(request):
    try:
        end   = datetime.today()
        start = end - timedelta(days=29)
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude=31.5214&longitude=74.3597"
            f"&daily=temperature_2m_max,relative_humidity_2m_max,"
            f"precipitation_sum"
            f"&start_date={start.strftime('%Y-%m-%d')}"
            f"&end_date={end.strftime('%Y-%m-%d')}"
        )
        response = requests.get(url, timeout=5)
        data = response.json()['daily']

        dates    = data['time']
        temps    = data['temperature_2m_max']
        humidity = data['relative_humidity_2m_max']
        # Simulate soil moisture from humidity (Open-Meteo free tier limitation)
        soil     = [round(h / 500 + 0.1, 3) for h in humidity]

    except Exception:
        # Fallback simulated data
        dates    = [(datetime.today() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]
        temps    = [32 + random.uniform(-4, 6) for _ in range(30)]
        humidity = [55 + random.uniform(-10, 15) for _ in range(30)]
        soil     = [0.18 + random.uniform(-0.05, 0.08) for _ in range(30)]

    # Derive index trends
    ndvi_series = [round(min(0.85, max(0.2, 0.3 + (h/200) + (s*1.5))), 2)
                   for h, s in zip(humidity, soil)]
    ndmi_series = [round(min(0.6, max(-0.2, s*2.5 - 0.1)), 2) for s in soil]
    lst_series  = [round(t + random.uniform(2, 5), 1) for t in temps]

    return JsonResponse({
        'dates': dates,
        'ndvi':  ndvi_series,
        'ndmi':  ndmi_series,
        'lst':   lst_series,
    })
    
    # ── 4. API: CNN Land Classification ──────────────────────────────────────────
def api_classify(request):
    lat = request.GET.get('lat', '31.5214')
    lon = request.GET.get('lon', '74.3597')
    
    try:
        # Fetch satellite tile image for this location
        zoom = 15
        # Convert lat/lon to tile coordinates
        import math
        lat_r = math.radians(float(lat))
        n = 2 ** zoom
        x_tile = int((float(lon) + 180.0) / 360.0 * n)
        y_tile = int((1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n)
        
        # Fetch Esri satellite tile
        tile_url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y_tile}/{x_tile}"
        tile_response = requests.get(tile_url, timeout=10)
        
        # Convert to PIL Image and resize for model
        img = Image.open(BytesIO(tile_response.content)).convert('RGB')
        img = img.resize((224, 224))
        
        # Convert to base64 for HuggingFace API
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        img_bytes = buffer.getvalue()
        
        # Call HuggingFace Inference API
        hf_token = os.getenv('HF_TOKEN')
        hf_url = "https://router.huggingface.co/hf-inference/models/google/vit-base-patch16-224"
        
        hf_response = requests.post(
            hf_url,
            headers={"Authorization": f"Bearer {hf_token}"},
            data=img_bytes,
            timeout=15
        )
        
        result = hf_response.json()
        
        # Extract top 3 classifications
        if isinstance(result, list):
            top3 = result[:3]
            classifications = [
                {
                    'label': item['label'],
                    'confidence': round(item['score'] * 100, 1)
                }
                for item in top3
            ]
        else:
            classifications = [{'label': 'Unknown', 'confidence': 0}]
            
    except Exception as e:
        classifications = [{'label': f'Error: {str(e)}', 'confidence': 0}]
    
    return JsonResponse({
        'lat': lat,
        'lon': lon,
        'classifications': classifications
    })