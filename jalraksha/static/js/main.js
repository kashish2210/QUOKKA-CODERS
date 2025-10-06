// JalRaksha Dashboard - Live Updates Without Page Reload

let charts = {};
let updateInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('JalRaksha Dashboard Loading...');
    
    if (window.location.pathname.includes('analytics')) {
        initializeAnalyticsDashboard();
        startLiveUpdates();
    }
    
    initializeGeneralFeatures();
});

function initializeAnalyticsDashboard() {
    console.log('Initializing Analytics Dashboard...');
    
    const flowRateData = JSON.parse(document.getElementById('flowRateData')?.textContent || '{"labels":[],"values":[]}');
    const pressureData = JSON.parse(document.getElementById('pressureData')?.textContent || '{"labels":[],"values":[]}');
    const consumptionData = JSON.parse(document.getElementById('consumptionData')?.textContent || '{"labels":[],"values":[]}');
    const sensorStatusData = JSON.parse(document.getElementById('sensorStatusData')?.textContent || '{"labels":[],"values":[]}');
    
    initializeCharts(flowRateData, pressureData, consumptionData, sensorStatusData);
    setupEventListeners();
    
    console.log('Analytics Dashboard Initialized');
}

function initializeCharts(flowRateData, pressureData, consumptionData, sensorStatusData) {
    const chartDefaults = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 750
        }
    };
    
    // Flow Rate Chart
    const flowCtx = document.getElementById('flowRateChart');
    if (flowCtx) {
        charts.flowRate = new Chart(flowCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: flowRateData.labels.length > 0 ? flowRateData.labels : generateTimeLabels(24),
                datasets: [{
                    label: 'Flow Rate (L/min)',
                    data: flowRateData.values.length > 0 ? flowRateData.values : [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 3
                }]
            },
            options: {
                ...chartDefaults,
                plugins: {
                    legend: { display: true, position: 'top' },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Flow Rate (L/min)' },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    },
                    x: {
                        title: { display: true, text: 'Time' },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // Pressure Chart
    const pressureCtx = document.getElementById('pressureChart');
    if (pressureCtx) {
        charts.pressure = new Chart(pressureCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: pressureData.labels.length > 0 ? pressureData.labels : generateTimeLabels(24),
                datasets: [{
                    label: 'Pressure (PSI)',
                    data: pressureData.values.length > 0 ? pressureData.values : [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 3
                }]
            },
            options: {
                ...chartDefaults,
                plugins: { legend: { display: true, position: 'top' } },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Pressure (PSI)' },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // Consumption Pattern Chart
    const consumptionCtx = document.getElementById('consumptionPatternChart');
    if (consumptionCtx) {
        charts.consumption = new Chart(consumptionCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: consumptionData.labels.length > 0 ? consumptionData.labels : ['12AM', '3AM', '6AM', '9AM', '12PM', '3PM', '6PM', '9PM'],
                datasets: [{
                    label: 'Consumption (Liters)',
                    data: consumptionData.values.length > 0 ? consumptionData.values : [],
                    backgroundColor: '#8b5cf6',
                    borderRadius: 6
                }]
            },
            options: {
                ...chartDefaults,
                plugins: { legend: { display: true, position: 'top' } },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Volume (Liters)' },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // Leak Heatmap Chart
    const leakCtx = document.getElementById('leakHeatmapChart');
    if (leakCtx) {
        charts.leak = new Chart(leakCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Critical',
                    data: [2, 1, 0, 3, 1, 0, 1],
                    backgroundColor: '#ef4444'
                }, {
                    label: 'High',
                    data: [3, 4, 2, 2, 3, 1, 2],
                    backgroundColor: '#f59e0b'
                }, {
                    label: 'Medium',
                    data: [5, 3, 4, 4, 5, 3, 4],
                    backgroundColor: '#eab308'
                }]
            },
            options: {
                ...chartDefaults,
                plugins: { legend: { display: true, position: 'top' } },
                scales: {
                    x: { stacked: true, grid: { display: false } },
                    y: { 
                        stacked: true, 
                        beginAtZero: true,
                        title: { display: true, text: 'Number of Leaks' },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    }
                }
            }
        });
    }

    // Sensor Status Chart
    const statusCtx = document.getElementById('sensorStatusChart');
    if (statusCtx) {
        charts.status = new Chart(statusCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: sensorStatusData.labels.length > 0 ? sensorStatusData.labels : ['Active', 'Warning', 'Offline'],
                datasets: [{
                    data: sensorStatusData.values.length > 0 ? sensorStatusData.values : [3, 0, 0],
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444']
                }]
            },
            options: {
                ...chartDefaults,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { padding: 15, usePointStyle: true }
                    }
                }
            }
        });
    }

    // Water Loss Breakdown
    const lossCtx = document.getElementById('lossBreakdownChart');
    if (lossCtx) {
        charts.loss = new Chart(lossCtx.getContext('2d'), {
            type: 'pie',
            data: {
                labels: ['Leaks', 'Theft', 'Meter Error', 'Other'],
                datasets: [{
                    data: [45, 25, 20, 10],
                    backgroundColor: ['#ef4444', '#f59e0b', '#eab308', '#94a3b8']
                }]
            },
            options: {
                ...chartDefaults,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { padding: 15, usePointStyle: true }
                    }
                }
            }
        });
    }

    // Sensor Comparison Radar
    const comparisonCtx = document.getElementById('sensorComparisonChart');
    if (comparisonCtx) {
        charts.comparison = new Chart(comparisonCtx.getContext('2d'), {
            type: 'radar',
            data: {
                labels: ['Flow Rate', 'Pressure', 'Reliability', 'Uptime', 'Efficiency'],
                datasets: [{
                    label: 'SENSOR001',
                    data: [85, 78, 92, 95, 88],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderWidth: 2
                }, {
                    label: 'SENSOR002',
                    data: [92, 85, 88, 90, 85],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    borderWidth: 2
                }, {
                    label: 'SENSOR003',
                    data: [78, 82, 85, 88, 80],
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.2)',
                    borderWidth: 2
                }]
            },
            options: {
                ...chartDefaults,
                plugins: { legend: { position: 'top' } },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { stepSize: 20 }
                    }
                }
            }
        });
    }

    // Demand Forecast
    const forecastCtx = document.getElementById('demandForecastChart');
    if (forecastCtx) {
        charts.forecast = new Chart(forecastCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
                datasets: [{
                    label: 'Predicted Demand',
                    data: [35000, 38000, 40000, 42000, 45000, 43000, 41000],
                    borderColor: '#8b5cf6',
                    borderDash: [5, 5],
                    fill: false,
                    borderWidth: 2
                }, {
                    label: 'Historical Average',
                    data: [36000, 37000, 39000, 41000, 43000, 42000, 40000],
                    borderColor: '#6b7280',
                    fill: false,
                    borderWidth: 2
                }]
            },
            options: {
                ...chartDefaults,
                plugins: { legend: { position: 'top' } },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: { display: true, text: 'Volume (Liters)' },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // Anomaly Detection
    const anomalyCtx = document.getElementById('anomalyChart');
    if (anomalyCtx) {
        charts.anomaly = new Chart(anomalyCtx.getContext('2d'), {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Normal',
                    data: generateScatterData(30, 10, 40, 20, 45),
                    backgroundColor: '#10b981',
                    pointRadius: 5
                }, {
                    label: 'Anomaly',
                    data: [{x: 12, y: 50}, {x: 28, y: 15}, {x: 32, y: 55}],
                    backgroundColor: '#ef4444',
                    pointRadius: 8
                }]
            },
            options: {
                ...chartDefaults,
                plugins: { legend: { position: 'top' } },
                scales: {
                    x: { 
                        title: { display: true, text: 'Flow Rate' },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    },
                    y: { 
                        title: { display: true, text: 'Pressure' },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    }
                }
            }
        });
    }
}

// Start live updates (fetch new data every 10 seconds)
function startLiveUpdates() {
    console.log('Starting live updates every 10 seconds...');
    
    updateInterval = setInterval(() => {
        fetchLatestSensorData();
    }, 10000); // Update every 10 seconds
}

// Fetch latest sensor data via AJAX
function fetchLatestSensorData() {
    const timeRange = document.getElementById('timeRange')?.value || '24h';
    const sensor = document.getElementById('sensorFilter')?.value || 'all';
    
    fetch(`/analytics/advanced/?range=${timeRange}&sensor=${sensor}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        updateChartsWithNewData(data);
        updateKPIs(data);
        console.log('Charts updated with live sensor data');
    })
    .catch(error => {
        console.error('Error fetching sensor data:', error);
    });
}

// Update charts with new data (smooth animation)
function updateChartsWithNewData(data) {
    // Update Flow Rate Chart
    if (charts.flowRate && data.flow_rate_data) {
        charts.flowRate.data.labels = data.flow_rate_data.labels;
        charts.flowRate.data.datasets[0].data = data.flow_rate_data.values;
        charts.flowRate.update('none'); // No animation for smoother updates
    }
    
    // Update Pressure Chart
    if (charts.pressure && data.pressure_data) {
        charts.pressure.data.labels = data.pressure_data.labels;
        charts.pressure.data.datasets[0].data = data.pressure_data.values;
        charts.pressure.update('none');
    }
    
    // Update Consumption Chart
    if (charts.consumption && data.consumption_data) {
        charts.consumption.data.labels = data.consumption_data.labels;
        charts.consumption.data.datasets[0].data = data.consumption_data.values;
        charts.consumption.update('none');
    }
    
    // Update Sensor Status
    if (charts.status && data.sensor_status_data) {
        charts.status.data.datasets[0].data = data.sensor_status_data.values;
        charts.status.update('none');
    }
}

// Update KPI values
function updateKPIs(data) {
    if (data.total_flow !== undefined) {
        animateValue(document.getElementById('totalFlow'), data.total_flow, ' L');
    }
    if (data.total_loss !== undefined) {
        animateValue(document.getElementById('totalLoss'), data.total_loss, ' L');
    }
    if (data.nrw_percentage !== undefined) {
        animateValue(document.getElementById('nrwPercent'), data.nrw_percentage, '%');
    }
    if (data.efficiency_score !== undefined) {
        animateValue(document.getElementById('efficiency'), data.efficiency_score, '%');
    }
}

// Animate KPI number changes
function animateValue(element, newValue, suffix = '') {
    if (!element) return;
    
    const currentText = element.textContent.replace(/[^0-9.]/g, '');
    const currentValue = parseFloat(currentText) || 0;
    const duration = 500;
    const steps = 20;
    const increment = (newValue - currentValue) / steps;
    let current = currentValue;
    let step = 0;
    
    const timer = setInterval(() => {
        step++;
        current += increment;
        
        if (step >= steps) {
            clearInterval(timer);
            current = newValue;
        }
        
        if (suffix === '%') {
            element.textContent = current.toFixed(1) + suffix;
        } else {
            element.textContent = Math.floor(current).toLocaleString() + suffix;
        }
    }, duration / steps);
}

function setupEventListeners() {
    // Time Range Filter
    const timeRange = document.getElementById('timeRange');
    if (timeRange) {
        timeRange.addEventListener('change', function() {
            fetchLatestSensorData();
        });
    }

    // Sensor Filter
    const sensorFilter = document.getElementById('sensorFilter');
    if (sensorFilter) {
        sensorFilter.addEventListener('change', function() {
            fetchLatestSensorData();
        });
    }

    // Chart type buttons
    document.querySelectorAll('.chart-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const chartType = this.dataset.chart;
            const parent = this.closest('.chart-container');
            
            parent.querySelectorAll('.chart-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            if (charts.flowRate) {
                toggleChartType(charts.flowRate, chartType);
            }
        });
    });
}

function toggleChartType(chart, type) {
    if (type === 'area') {
        chart.data.datasets[0].fill = true;
        chart.data.datasets[0].backgroundColor = 'rgba(59, 130, 246, 0.2)';
    } else {
        chart.data.datasets[0].fill = false;
        chart.data.datasets[0].backgroundColor = 'rgba(59, 130, 246, 0.1)';
    }
    chart.update();
}

function exportReport() {
    showNotification('Generating PDF report...', 'info');
    setTimeout(() => {
        showNotification('PDF export requires backend implementation', 'warning');
    }, 1000);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 250px; animation: slideIn 0.3s ease;';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Utility functions
function generateTimeLabels(count) {
    const labels = [];
    const now = new Date();
    
    for (let i = count - 1; i >= 0; i--) {
        const time = new Date(now - i * 60 * 60 * 1000);
        labels.push(time.getHours() + ':00');
    }
    
    return labels;
}

function generateScatterData(count, minX, maxX, minY, maxY) {
    const data = [];
    
    for (let i = 0; i < count; i++) {
        data.push({
            x: Math.floor(Math.random() * (maxX - minX)) + minX,
            y: Math.floor(Math.random() * (maxY - minY)) + minY
        });
    }
    
    return data;
}

function initializeGeneralFeatures() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    setTimeout(() => {
        const messages = document.querySelector('.messages');
        if (messages) {
            messages.style.transition = 'opacity 0.5s';
            messages.style.opacity = '0';
            setTimeout(() => messages.remove(), 500);
        }
    }, 5000);
}

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

console.log('JalRaksha Dashboard Loaded');