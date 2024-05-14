let chartList = [];
let lineData = [];

$(document).ready(function () {
    if (lineData.length == 0) {
        fetch('/dashboard-accuracy')
            .then(response => response.json())
            .then(data => {
                lineData = data;
                initializeScreen();
            });
    }
});

function initializeScreen() {
    $('#month-picker').change(function () {
        let selectedMonth = $(this).val();
        let startDate = new Date(selectedMonth + '-01');
        let endDate = new Date(startDate.getFullYear(), startDate.getMonth() + 1, 0, 12);
        startDate = startDate.toISOString().split('T')[0];
        endDate = endDate.toISOString().split('T')[0];

        generateCharts(startDate, endDate);
    });

    let date = new Date();
    let month = date.getMonth() + 1; // getMonth() is zero-based
    let year = date.getFullYear();
    month = month < 10 ? '0' + month : month; // prepend 0 to single digit months
    $('#month-picker').val(year + '-' + month).trigger('change');
}

function generateCharts(startDate, endDate) {

    chartList.forEach(chart => chart.destroy());

    // adding the startDate and endDate to the URL as query parameters
    let queryParameters = '?startDate=' + startDate + '&endDate=' + endDate;
    // URL encoded the query parameters
    queryParameters = encodeURI(queryParameters);

    fetch('/dashboard-cover' + queryParameters)
        .then(response => response.json())
        .then(data => {
            createBarChart('coverChart', data);
        });

    fetch('/dashboard-fst-spec' + queryParameters)
        .then(response => response.json())
        .then(data => {
            createBarChart('fstSpecChart', data);
        });

    fetch('/dashboard-cover-profit' + queryParameters)
        .then(response => response.json())
        .then(data => {
            createPieChart('coverChartProfit', data);
        });

    fetch('/dashboard-fst-spec-profit' + queryParameters)
        .then(response => response.json())
        .then(data => {
            createPieChart('fstSpecChartProfit', data);
        });
}

function convertToTransparentColor(item) {
    let color = item.color;
    color = color.replace('#', '');
    let r = parseInt(color.substring(0, 2), 16);
    let g = parseInt(color.substring(2, 4), 16);
    let b = parseInt(color.substring(4, 6), 16);
    return 'rgba(' + r + ',' + g + ',' + b + ',0.2)';
}

function createBarChart(chartName, data) {
    let canvas = document.getElementById(chartName);
    let ctx = canvas.getContext('2d');
    let lines = [];
    let maxValue = Math.max(...data.map(item => item.count));
    data.forEach(e => {
        let predication = x => e.label == x.label;
        if ('fstSpecChart' == chartName) {
            predication = x => x.label.includes('fstSpec_') && x.label.replace('fstSpec_', '') == e.label;
        }
        let line = lineData.filter(predication).map(x => x.value * maxValue / 100)[0];
        lines.push(line);
    });
    let chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.label),
            datasets: [{
                label: '# of Matched Numbers',
                data: data.map(item => item.count),
                backgroundColor: data.map(item => convertToTransparentColor(item)),
                borderColor: data.map(item => item.color),
                borderWidth: 1
            }, {
                type: 'line',
                label: 'Prediction accuracy',
                data: lines,
                fill: false,
                borderColor: '#0000ff',
                backgroundColor: '#0000ff',
                pointBackgroundColor: '#0000ff',
                pointBorderColor: '#0000ff',
                pointHoverBackgroundColor: '#0000ff',
                pointHoverBorderColor: '#0000ff',
                datalabels: {
                    display: true,
                    color: 'black'
                }
            }]
        },
        options: {
            hover: { mode: null },
            responsive: true,
            maintainAspectRatio: false,
            legend: { display: false },
            plugins: {
                datalabels: {
                    formatter: (value, ctx) => {
                        return value.toFixed(2);  // format the value here
                    }
                }
            }
        }
    });
    chartList.push(chart);
}

function createPieChart(chartId, data) {
    let ctx = document.getElementById(chartId).getContext('2d');
    let chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(item => item.label),
            datasets: [{
                data: data.map(item => item.value),
                backgroundColor: data.map(item => convertToTransparentColor(item)),
                borderColor: data.map(item => item.color),
                borderWidth: 1
            }]
        },
        options: {
            tooltips: {
                callbacks: {
                    label: function (tooltipItem, data) {
                        let value = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                        let res = value.toLocaleString('vi-VN', { style: 'currency', currency: 'VND' });
                        console.log(res);
                        return res;
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false,
        }
    });
    chartList.push(chart);
}
