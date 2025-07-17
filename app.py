from flask import Flask, request, jsonify, render_template_string
import requests
import os
import sys

app = Flask(__name__)

WAQI_TOKEN = 'f0ee6276f0618800724543191076bc4a4393417b'  # Hardcoded as requested

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>EnviroSense: Environmental Monitoring</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <style>
        body { background: linear-gradient(135deg, #e0e7ff 0%, #f8fafc 100%); }
        #map { height: 40vh; min-height: 250px; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.10); }
        .main-title { font-family: 'Segoe UI', Arial, sans-serif; font-weight: 800; letter-spacing: 1px; color: #2d3a4a; margin-bottom: 0.5rem; }
        .card { box-shadow: 0 4px 24px rgba(0,0,0,0.10); margin-bottom: 1rem; border-radius: 18px; border: none; background: #fff; transition: box-shadow 0.2s; }
        .card:hover { box-shadow: 0 8px 32px rgba(0,0,0,0.13); }
        .card-header { background: linear-gradient(90deg, #6366f1 0%, #60a5fa 100%); color: #fff; border-radius: 18px 18px 0 0; font-weight: 700; font-size: 1.13rem; letter-spacing: 0.5px; }
        .card-body { padding: 1.3rem 1rem 1rem 1rem; }
        .chart-container { height: 210px; background: #f1f5f9; border-radius: 10px; margin-bottom: 0.5rem; }
        .demo-label { color: #fff; background: #6366f1; border-radius: 8px; padding: 2px 12px; font-size: 1rem; font-weight: 700; display: inline-block; margin-top: 0.5rem; letter-spacing: 0.5px; }
        .nodata-msg { color: #b00; font-weight: 600; text-align: center; margin-top: 1rem; }
        .coords-label { font-size: 1.08rem; color: #374151; margin-bottom: 0.7rem; text-align: center; font-weight: 500; }
        .spinner-border { width: 1.5rem; height: 1.5rem; color: #6366f1; vertical-align: middle; margin-right: 0.5rem; }
        .loading-label { color: #6366f1; font-weight: 600; font-size: 1.05rem; }
        @media (max-width: 768px) {
            #map { height: 30vh; min-height: 180px; }
            .chart-container { height: 120px; }
            .card-header { font-size: 1rem; }
        }
    </style>
</head>
<body>
    <div class="container py-3">
        <h1 class="main-title text-center">EnviroSense</h1>
        <div class="coords-label" id="coordsLabel">Selected Location: (20.00, 0.00)</div>
        <div class="row mb-3">
            <div class="col-12">
                <div id="map"></div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-4 col-12 mb-3">
                <div class="card h-100">
                    <div class="card-header">Soil Condition</div>
                    <div class="card-body">
                        <canvas id="soilChart" class="chart-container"></canvas>
                        <div id="soilData" class="mt-2"></div>
                        <div id="soilNoData" class="nodata-msg" style="display:none"></div>
                        <div id="soilDemoLabel" class="demo-label" style="display:none">Demo Data</div>
                        <div id="soilError" class="nodata-msg" style="display:none"></div>
                        <div id="soilLoading" class="loading-label" style="display:none"><span class="spinner-border spinner-border-sm"></span>Loading...</div>
                    </div>
                </div>
            </div>
            <div class="col-md-4 col-12 mb-3">
                <div class="card h-100">
                    <div class="card-header">Air Quality</div>
                    <div class="card-body">
                        <canvas id="airChart" class="chart-container"></canvas>
                        <div id="airData" class="mt-2"></div>
                        <div id="airNoData" class="nodata-msg" style="display:none"></div>
                        <div id="airDemoLabel" class="demo-label" style="display:none">Demo Data</div>
                        <div id="airError" class="nodata-msg" style="display:none"></div>
                        <div id="airLoading" class="loading-label" style="display:none"><span class="spinner-border spinner-border-sm"></span>Loading...</div>
                    </div>
                </div>
            </div>
            <div class="col-md-4 col-12 mb-3">
                <div class="card h-100">
                    <div class="card-header">Water Quality</div>
                    <div class="card-body">
                        <canvas id="waterChart" class="chart-container"></canvas>
                        <div id="waterData" class="mt-2"></div>
                        <div id="waterNoData" class="nodata-msg" style="display:none"></div>
                        <div id="waterDemoLabel" class="demo-label" style="display:none">Demo Data</div>
                        <div id="waterError" class="nodata-msg" style="display:none"></div>
                        <div id="waterLoading" class="loading-label" style="display:none"><span class="spinner-border spinner-border-sm"></span>Loading...</div>
                    </div>
                </div>
            </div>
        </div>
        <div id="allNoData" class="nodata-msg" style="display:none">No real data available for this location. Try another location or check your internet connection.</div>
    </div>
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
    let selectedLat = 20.0, selectedLon = 0.0;
    let marker = null;
    const map = L.map('map').setView([selectedLat, selectedLon], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    function setMarker(lat, lon) {
        if (marker) { marker.setLatLng([lat, lon]); }
        else { marker = L.marker([lat, lon]).addTo(map); }
    }
    setMarker(selectedLat, selectedLon);
    function updateCoordsLabel(lat, lon) {
        document.getElementById('coordsLabel').textContent = `Selected Location: (${lat.toFixed(2)}, ${lon.toFixed(2)})`;
    }
    map.on('click', function(e) {
        selectedLat = e.latlng.lat;
        selectedLon = e.latlng.lng;
        setMarker(selectedLat, selectedLon);
        updateCoordsLabel(selectedLat, selectedLon);
        fetchData(selectedLat, selectedLon);
    });
    let soilChart, airChart, waterChart;
    function createOrUpdateChart(ctx, label, data, color) {
        if (ctx.chart) {
            ctx.chart.data.datasets[0].data = data;
            ctx.chart.update();
            return ctx.chart;
        }
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: label,
                datasets: [{
                    label: label,
                    data: data,
                    backgroundColor: color
                }]
            },
            options: {responsive: true, plugins: {legend: {display: false}}}
        });
    }
    function showLoading() {
        document.getElementById('soilLoading').style.display = '';
        document.getElementById('airLoading').style.display = '';
        document.getElementById('waterLoading').style.display = '';
    }
    function hideLoading() {
        document.getElementById('soilLoading').style.display = 'none';
        document.getElementById('airLoading').style.display = 'none';
        document.getElementById('waterLoading').style.display = 'none';
    }
    function fetchData(lat, lon) {
        document.getElementById('soilData').innerHTML = '';
        document.getElementById('airData').innerHTML = '';
        document.getElementById('waterData').innerHTML = '';
        document.getElementById('soilNoData').style.display = 'none';
        document.getElementById('airNoData').style.display = 'none';
        document.getElementById('waterNoData').style.display = 'none';
        document.getElementById('allNoData').style.display = 'none';
        document.getElementById('soilDemoLabel').style.display = 'none';
        document.getElementById('airDemoLabel').style.display = 'none';
        document.getElementById('waterDemoLabel').style.display = 'none';
        document.getElementById('soilError').style.display = 'none';
        document.getElementById('airError').style.display = 'none';
        document.getElementById('waterError').style.display = 'none';
        showLoading();
        fetch(`/api/environment?lat=${lat}&lon=${lon}`)
            .then(res => {
                if (!res.ok) throw new Error('Network response was not ok');
                return res.json();
            })
            .then(data => {
                hideLoading();
                let soilNoData = isSoilNoData(data.soil);
                let airNoData = isAirNoData(data.air);
                let waterNoData = isWaterNoData(data.water);
                if (!soilNoData) {
                    updateSoil(data.soil);
                    if (data.soil.demo) document.getElementById('soilDemoLabel').style.display = '';
                } else showNoData('soil');
                if (!airNoData) {
                    updateAir(data.air);
                    if (data.air.demo) document.getElementById('airDemoLabel').style.display = '';
                } else showNoData('air');
                if (!waterNoData) {
                    updateWater(data.water);
                    if (data.water.demo) document.getElementById('waterDemoLabel').style.display = '';
                } else showNoData('water');
                if (soilNoData && airNoData && waterNoData) {
                    document.getElementById('allNoData').style.display = '';
                }
            })
            .catch(() => {
                hideLoading();
                document.getElementById('soilData').innerHTML = '';
                document.getElementById('airData').innerHTML = '';
                document.getElementById('waterData').innerHTML = '';
                document.getElementById('soilError').textContent = 'Error loading soil data.';
                document.getElementById('soilError').style.display = '';
                document.getElementById('airError').textContent = 'Error loading air data.';
                document.getElementById('airError').style.display = '';
                document.getElementById('waterError').textContent = 'Error loading water data.';
                document.getElementById('waterError').style.display = '';
            });
    }
    function isSoilNoData(soil) {
        return !soil || (soil.moisture === 'No data' && soil.temperature === 'No data');
    }
    function isAirNoData(air) {
        return !air || (air.aqi === 'No data' && air.pm25 === 'No data' && air.pm10 === 'No data' && air.o3 === 'No data' && air.co === 'No data' && air.no2 === 'No data' && air.so2 === 'No data' && air.t === 'No data');
    }
    function isWaterNoData(water) {
        return !water || (water.ph === 'No data' && water.turbidity === 'No data' && water.contaminants === 'No data');
    }
    function showNoData(type) {
        if (type === 'soil') {
            document.getElementById('soilData').innerHTML = '';
            document.getElementById('soilNoData').textContent = 'No real soil data available for this location.';
            document.getElementById('soilNoData').style.display = '';
        } else if (type === 'air') {
            document.getElementById('airData').innerHTML = '';
            document.getElementById('airNoData').textContent = 'No real air quality data available for this location.';
            document.getElementById('airNoData').style.display = '';
        } else if (type === 'water') {
            document.getElementById('waterData').innerHTML = '';
            document.getElementById('waterNoData').textContent = 'No real water data available for this location.';
            document.getElementById('waterNoData').style.display = '';
        }
    }
    function updateSoil(soil) {
        const ctx = document.getElementById('soilChart').getContext('2d');
        if (!soilChart) soilChart = createOrUpdateChart(ctx, ['Moisture', 'Temperature'], [soil.moisture, soil.temperature], 'rgba(139,69,19,0.7)');
        else createOrUpdateChart(ctx, ['Moisture', 'Temperature'], [soil.moisture, soil.temperature], 'rgba(139,69,19,0.7)');
        document.getElementById('soilData').innerHTML = `Moisture: ${soil.moisture} %<br>Temperature: ${soil.temperature} °C`;
    }
    function updateAir(air) {
        const ctx = document.getElementById('airChart').getContext('2d');
        const labels = ['AQI', 'PM2.5', 'PM10', 'O₃', 'CO', 'NO₂', 'SO₂', 'Temp'];
        const data = [air.aqi, air.pm25, air.pm10, air.o3, air.co, air.no2, air.so2, air.t];
        if (!airChart) airChart = createOrUpdateChart(ctx, labels, data, 'rgba(30,144,255,0.7)');
        else createOrUpdateChart(ctx, labels, data, 'rgba(30,144,255,0.7)');
        document.getElementById('airData').innerHTML = `
            AQI: ${air.aqi}<br>
            PM2.5: ${air.pm25} µg/m³<br>
            PM10: ${air.pm10} µg/m³<br>
            O₃: ${air.o3} µg/m³<br>
            CO: ${air.co} µg/m³<br>
            NO₂: ${air.no2} µg/m³<br>
            SO₂: ${air.so2} µg/m³<br>
            Temp: ${air.t} °C
        `;
    }
    function updateWater(water) {
        const ctx = document.getElementById('waterChart').getContext('2d');
        if (!waterChart) waterChart = createOrUpdateChart(ctx, ['pH', 'Turbidity', 'Contaminants'], [water.ph, water.turbidity, water.contaminants], 'rgba(0,191,255,0.7)');
        else createOrUpdateChart(ctx, ['pH', 'Turbidity', 'Contaminants'], [water.ph, water.turbidity, water.contaminants], 'rgba(0,191,255,0.7)');
        document.getElementById('waterData').innerHTML = `pH: ${water.ph}<br>Turbidity: ${water.turbidity} NTU<br>Contaminants: ${water.contaminants}`;
    }
    setMarker(selectedLat, selectedLon);
    updateCoordsLabel(selectedLat, selectedLon);
    fetchData(selectedLat, selectedLon);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/environment')
def environment():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    air, air_demo = get_air_quality(lat, lon)
    soil, soil_demo = get_soil_data(lat, lon)
    water, water_demo = get_water_data(lat, lon)
    # Always return all three keys, even if some are 'No data'
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
        resp = requests.get(url, timeout=15)
        data = resp.json()
        print('WAQI response:', data, file=sys.stderr)
        if data.get('status') == 'ok':
            iaqi = data['data'].get('iaqi', {})
            # If any real value found, return it (not demo)
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
    # Demo/sample data fallback
    return ({'aqi': 45, 'pm25': 30, 'pm10': 25, 'o3': 10, 'co': 0.5, 'no2': 12, 'so2': 2, 't': 27}, True)

def get_soil_data(lat, lon):
    try:
        url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=soil_temperature_0cm,soil_moisture_0_1cm&forecast_days=1&timezone=auto'
        resp = requests.get(url, timeout=15)
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
    # Demo/sample data fallback
    return ({'moisture': 12, 'temperature': 32}, True)

def get_water_data(lat, lon):
    try:
        url = f'https://www.waterqualitydata.us/data/Result/search?lat={lat}&long={lon}&within=5&mimeType=json'
        resp = requests.get(url, timeout=15)
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
        # If any real value found, return it (not demo)
        if ph != 'No data' or turbidity != 'No data' or contaminants != 'No data':
            return ({'ph': ph, 'turbidity': turbidity, 'contaminants': contaminants}, False)
    except Exception as e:
        print('Water Quality Portal error:', e, file=sys.stderr)
    # Demo/sample data fallback
    return ({'ph': 7.2, 'turbidity': 2.5, 'contaminants': 5}, True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
