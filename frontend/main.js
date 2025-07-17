// Set this to your deployed backend API URL
const BACKEND_URL = 'https://your-backend-url.onrender.com/api'; // <-- CHANGE THIS after backend deployment

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
function fetchData(lat, lon) {
    document.getElementById('soilData').innerHTML = 'Loading...';
    document.getElementById('airData').innerHTML = 'Loading...';
    document.getElementById('waterData').innerHTML = 'Loading...';
    document.getElementById('soilNoData').style.display = 'none';
    document.getElementById('airNoData').style.display = 'none';
    document.getElementById('waterNoData').style.display = 'none';
    document.getElementById('allNoData').style.display = 'none';
    document.getElementById('soilDemoLabel').style.display = 'none';
    document.getElementById('airDemoLabel').style.display = 'none';
    document.getElementById('waterDemoLabel').style.display = 'none';
    fetch(`${BACKEND_URL}/environment?lat=${lat}&lon=${lon}`)
        .then(res => {
            if (!res.ok) throw new Error('Network response was not ok');
            return res.json();
        })
        .then(data => {
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
            document.getElementById('soilData').innerHTML = 'Error loading soil data.';
            document.getElementById('airData').innerHTML = 'Error loading air data.';
            document.getElementById('waterData').innerHTML = 'Error loading water data.';
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