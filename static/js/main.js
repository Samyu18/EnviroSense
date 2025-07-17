// === CONFIGURATION ===
// Use relative path since frontend and backend are served together
const BACKEND_URL = '/api';

// Initialize Leaflet map
const map = L.map('map').setView([20, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

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

map.on('click', function(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    fetchData(lat, lon);
});

function fetchData(lat, lon) {
    document.getElementById('soilData').innerHTML = 'Loading...';
    document.getElementById('airData').innerHTML = 'Loading...';
    document.getElementById('waterData').innerHTML = 'Loading...';
    fetch(`${BACKEND_URL}/environment?lat=${lat}&lon=${lon}`)
        .then(res => res.json())
        .then(data => {
            updateSoil(data.soil);
            updateAir(data.air);
            updateWater(data.water);
        })
        .catch(() => {
            document.getElementById('soilData').innerHTML = 'Error loading data.';
            document.getElementById('airData').innerHTML = 'Error loading data.';
            document.getElementById('waterData').innerHTML = 'Error loading data.';
        });
}

function updateSoil(soil) {
    const ctx = document.getElementById('soilChart').getContext('2d');
    if (!soilChart) soilChart = createOrUpdateChart(ctx, ['pH', 'Moisture', 'Nutrients'], [soil.ph, soil.moisture, soil.nutrients], 'rgba(139,69,19,0.7)');
    else createOrUpdateChart(ctx, ['pH', 'Moisture', 'Nutrients'], [soil.ph, soil.moisture, soil.nutrients], 'rgba(139,69,19,0.7)');
    document.getElementById('soilData').innerHTML = `pH: ${soil.ph}<br>Moisture: ${soil.moisture}%<br>Nutrients: ${soil.nutrients}`;
}

function updateAir(air) {
    const ctx = document.getElementById('airChart').getContext('2d');
    if (!airChart) airChart = createOrUpdateChart(ctx, ['AQI', 'PM2.5', 'PM10'], [air.aqi, air.pm25, air.pm10], 'rgba(30,144,255,0.7)');
    else createOrUpdateChart(ctx, ['AQI', 'PM2.5', 'PM10'], [air.aqi, air.pm25, air.pm10], 'rgba(30,144,255,0.7)');
    document.getElementById('airData').innerHTML = `AQI: ${air.aqi}<br>PM2.5: ${air.pm25} µg/m³<br>PM10: ${air.pm10} µg/m³`;
}

function updateWater(water) {
    const ctx = document.getElementById('waterChart').getContext('2d');
    if (!waterChart) waterChart = createOrUpdateChart(ctx, ['pH', 'Turbidity', 'Contaminants'], [water.ph, water.turbidity, water.contaminants], 'rgba(0,191,255,0.7)');
    else createOrUpdateChart(ctx, ['pH', 'Turbidity', 'Contaminants'], [water.ph, water.turbidity, water.contaminants], 'rgba(0,191,255,0.7)');
    document.getElementById('waterData').innerHTML = `pH: ${water.ph}<br>Turbidity: ${water.turbidity} NTU<br>Contaminants: ${water.contaminants}`;
}

// Initial fetch for default location
fetchData(20, 0);