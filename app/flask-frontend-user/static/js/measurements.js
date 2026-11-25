
let ws = null;
let currentDeviceId = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded event fired');

    initMeasurements();

    setInterval(updateMeasurementsData, 30000);

    updateMeasurementsData();

    const deviceSelect = document.getElementById('device-select');
    if (deviceSelect) {
        console.log('Device select element found:', deviceSelect);
        deviceSelect.addEventListener('change', function() {
            console.log('Device selector changed');
            handleDeviceChange();
        });

        if (deviceSelect.value) {
            console.log('Device already selected on load:', deviceSelect.value);
            connectWebSocket(deviceSelect.value);
            currentDeviceId = deviceSelect.value;
        } else {
            console.log('No device selected on load');
        }
    } else {
        console.log('Device select element NOT found');
    }
});

function initMeasurements() {

    console.log('Measurements initialized');
}

function getSelectedDeviceId() {
    const deviceSelect = document.getElementById('device-select');
    if (deviceSelect) {
        return deviceSelect.value;
    }
    return '';
}

function handleDeviceChange() {
    const newDeviceId = getSelectedDeviceId();
    if (newDeviceId !== currentDeviceId) {

        if (ws) {
            ws.close();
            ws = null;
        }
        currentDeviceId = newDeviceId;

        connectWebSocket(newDeviceId);

        updateMeasurementsData();
    }
}

function connectWebSocket(deviceId) {
    if (!deviceId) {
        return;
    }

    fetch('/measurements/api/stream-ticket/' + encodeURIComponent(deviceId), {
        headers: { Accept: 'application/json' }
    })
        .then(async response => {
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Nie można uzyskać dostępu do podglądu');
            const wsBase = document.body.dataset.wsBase;
            if (!wsBase) throw new Error('Brak adresu podglądu na żywo');
            const wsUrl = `${wsBase.replace(/\/$/, '')}/${encodeURIComponent(deviceId)}`;
            ws = new WebSocket(wsUrl, ['ad-stream', `ticket.${data.ticket}`]);

            ws.onmessage = event => {
                try {
                    const message = JSON.parse(event.data);
                    if (message.type === 'measurement') updateMeasurementDisplayFromWS(message);
                } catch (error) {
                    console.error('Niepoprawna wiadomość pomiaru na żywo');
                }
            };
            ws.onerror = () => console.warn('Podgląd na żywo jest chwilowo niedostępny');
            ws.onclose = () => { ws = null; };
        })
        .catch(error => {
            console.warn('Nie udało się połączyć z podglądem na żywo:', error.message);
        });
}

function updateMeasurementsData() {
    const deviceId = getSelectedDeviceId();

    fetchCurrentMeasurement(deviceId);

    updateMeasurementsChart(deviceId);
}

function fetchCurrentMeasurement(deviceId) {

    if (!deviceId) {
        updateMeasurementDisplay({
            water_quality_ph: '--',
            water_quality_turbidity: '--',
            temperature: '--',
            humidity: '--',
            measurement_time: '--'
        });
        return;
    }

    const url = `/api/v1/measurements/${deviceId}/latest`;

    fetch(url, {
        headers: {
            'Authorization': 'Bearer ' + getAuthToken()
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        updateMeasurementDisplay(data);
    })
    .catch(error => {
        console.error('Error fetching current measurement:', error);
        updateMeasurementDisplay({
            water_quality_ph: '--',
            water_quality_turbidity: '--',
            temperature: '--',
            humidity: '--',
            measurement_time: 'Błąd'
        });
    });
}

function updateMeasurementDisplay(data) {
    document.getElementById('water-ph').textContent = data.water_quality_ph !== null ? parseFloat(data.water_quality_ph).toFixed(2) : '--';
    document.getElementById('water-turbidity').textContent = data.water_quality_turbidity !== null ? parseFloat(data.water_quality_turbidity).toFixed(2) : '--';
    document.getElementById('water-temperature').textContent = data.temperature !== null ? parseFloat(data.temperature).toFixed(1) : '--';
    document.getElementById('water-humidity').textContent = data.humidity !== null ? parseFloat(data.humidity).toFixed(1) : '--';

    const timeElement = document.getElementById('measurement-time');
    if (data.measurement_time) {
        const date = new Date(data.measurement_time);
        timeElement.textContent = date.toLocaleString();
    } else {
        timeElement.textContent = '--';
    }
}

function updateMeasurementDisplayFromWS(data) {

    const wsData = {
        water_quality_ph: data.data?.ph ?? null,
        water_quality_turbidity: data.data?.ec ?? null,
        temperature: data.data?.temperature ?? null,
        humidity: null,
        measurement_time: data.timestamp ?? null
    };

    updateMeasurementDisplay(wsData);
}

function updateMeasurementsChart(deviceId) {

    if (!deviceId) {
        clearChart();
        return;
    }

    const url = `/api/v1/measurements/${deviceId}?limit=100`;

    fetch(url, {
        headers: {
            'Authorization': 'Bearer ' + getAuthToken()
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        renderChart(data);
    })
    .catch(error => {
        console.error('Error fetching measurements for chart:', error);
        clearChart();
    });
}

function renderChart(measurements) {
    const ctx = document.getElementById('historyChart');
    if (!ctx) return;

    if (window.measurementsChart) {
        window.measurementsChart.destroy();
    }

    const labels = measurements.map(m => {
        const date = new Date(m.measurement_time);
        return date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }).reverse();

    const phData = measurements.map(m => m.water_quality_ph !== null ? parseFloat(m.water_quality_ph) : null).reverse();
    const ecData = measurements.map(m => m.water_quality_turbidity !== null ? parseFloat(m.water_quality_turbidity) : null).reverse();
    const tempData = measurements.map(m => m.temperature !== null ? parseFloat(m.temperature) : null).reverse();

    window.measurementsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'pH',
                    data: phData,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    tension: 0.1,
                    yAxisID: 'y-left'
                },
                {
                    label: 'EC (NTU)',
                    data: ecData,
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    tension: 0.1,
                    yAxisID: 'y-right'
                },
                {
                    label: 'Temperatura (°C)',
                    data: tempData,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    tension: 0.1,
                    yAxisID: 'y-right'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'pH'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'EC / Temperatura'
                    },
                    grid: {
                        drawOnChartArea: false,
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Historia pomiarów (24h)'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            }
        }
    });
}

function clearChart() {
    const ctx = document.getElementById('historyChart');
    if (!ctx) return;

    if (window.measurementsChart) {
        window.measurementsChart.destroy();
        window.measurementsChart = null;
    }

    const ctx2d = ctx.getContext('2d');
    ctx2d.clearRect(0, 0, ctx.width, ctx.height);
}

function getAuthToken() {

    const token = localStorage.getItem('authToken');
    if (token) return token;

    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('authToken=')) {
            return cookie.substring('authToken='.length, cookie.length);
        }
    }

    return '';
}
