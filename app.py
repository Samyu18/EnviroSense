from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import sys

app = Flask(__name__)
CORS(app)

WAQI_TOKEN = 'f0ee6276f0618800724543191076bc4a4393417b'  # Hardcoded as requested

@app.route('/api/environment')
def environment():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    air, air_demo = get_air_quality(lat, lon)
    soil, soil_demo = get_soil_data(lat, lon)
    water, water_demo = get_water_data(lat, lon)
    if soil_demo:
        soil['demo'] = True
    if air_demo:
        air['demo'] = True
    if water_demo:
        water['demo'] = True
    return jsonify({'soil': soil or {'moisture': 'No data', 'temperature': 'No data'},
                    'air': air or {'aqi': 'No data', 'pm25': 'No data', 'pm10': 'No data', 'o3': 'No data', 'co': 'No data', 'no2': 'No data', 'so2': 'No data', 't': 'No data'},
                    'water': water or {'ph': 'No data', 'turbidity': 'No data', 'contaminants': 'No data'}})

def get_air_quality(lat, lon):
    try:
        url = f'https://api.waqi.info/feed/geo:{lat};{lon}/?token={WAQI_TOKEN}'
        resp = requests.get(url, timeout=5)
        data = resp.json()
        print('WAQI response:', data, file=sys.stderr)
        if data.get('status') == 'ok':
            iaqi = data['data'].get('iaqi', {})
            aqi = data['data'].get('aqi', -1)
            pm25 = iaqi.get('pm25', {}).get('v', -1)
            pm10 = iaqi.get('pm10', {}).get('v', -1)
            o3 = iaqi.get('o3', {}).get('v', 'No data')
            co = iaqi.get('co', {}).get('v', 'No data')
            no2 = iaqi.get('no2', {}).get('v', 'No data')
            so2 = iaqi.get('so2', {}).get('v', 'No data')
            t = iaqi.get('t', {}).get('v', 'No data')
            if (aqi != -1 or pm25 != -1 or pm10 != -1 or o3 != 'No data' or co != 'No data' or no2 != 'No data' or so2 != 'No data' or t != 'No data'):
                return ({'aqi': aqi, 'pm25': pm25, 'pm10': pm10, 'o3': o3, 'co': co, 'no2': no2, 'so2': so2, 't': t}, False)
    except Exception as e:
        print('WAQI error:', e, file=sys.stderr)
    return ({'aqi': 45, 'pm25': 30, 'pm10': 25, 'o3': 10, 'co': 0.5, 'no2': 12, 'so2': 2, 't': 27}, True)

def get_soil_data(lat, lon):
    try:
        url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=soil_temperature_0cm,soil_moisture_0_1cm&forecast_days=1&timezone=auto'
        resp = requests.get(url, timeout=5)
        data = resp.json()
        print('Open-Meteo response:', data, file=sys.stderr)
        moisture = data.get('hourly', {}).get('soil_moisture_0_1cm', [None])[0]
        temperature = data.get('hourly', {}).get('soil_temperature_0cm', [None])[0]
        if moisture is not None or temperature is not None:
            moisture = round(moisture * 100, 2) if moisture is not None else 'No data'
            temperature = round(temperature, 2) if temperature is not None else 'No data'
            return ({'moisture': moisture, 'temperature': temperature}, False)
    except Exception as e:
        print('Open-Meteo error:', e, file=sys.stderr)
    return ({'moisture': 12, 'temperature': 32}, True)

def get_water_data(lat, lon):
    try:
        url = f'https://www.waterqualitydata.us/data/Result/search?lat={lat}&long={lon}&within=5&mimeType=json'
        resp = requests.get(url, timeout=5)
        data = resp.json()
        print('Water Quality Portal response:', data, file=sys.stderr)
        ph, turbidity, contaminants = 'No data', 'No data', 'No data'
        for r in data:
            if 'CharacteristicName' in r:
                if r['CharacteristicName'].lower() == 'ph' and ph == 'No data':
                    ph = r.get('ResultMeasureValue', 'No data')
                if r['CharacteristicName'].lower() == 'turbidity' and turbidity == 'No data':
                    turbidity = r.get('ResultMeasureValue', 'No data')
                if r['CharacteristicName'].lower() in ['nitrate', 'lead', 'arsenic', 'contaminant'] and contaminants == 'No data':
                    contaminants = r.get('ResultMeasureValue', 'No data')
        if ph != 'No data' or turbidity != 'No data' or contaminants != 'No data':
            return ({'ph': ph, 'turbidity': turbidity, 'contaminants': contaminants}, False)
    except Exception as e:
        print('Water Quality Portal error:', e, file=sys.stderr)
    return ({'ph': 7.2, 'turbidity': 2.5, 'contaminants': 5}, True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
