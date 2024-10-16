// Register the plugin to all charts:
Chart.register(ChartDataLabels);

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
        let monthStartDate = getMonthStartDate();
        // Extract year and month from selectedMonth
        let [year, month] = selectedMonth.split('-').map(Number);
        // Convert monthStartDate from string to intege
        let startDay = parseInt(monthStartDate, 10);
        let startDate = new Date(year, month - 1, startDay, 12); // month is 0-indexed in Date
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

    fetch('/dashboard-cover-absent' + queryParameters)
        .then(response => response.json())
        .then(data => {
            createBarChart('coverChartAbsent', data);
        });

    fetch('/dashboard-cover-cycle' + queryParameters)
        .then(response => response.json())
        .then(data => {
            createBarChart('coverChartCycle', data);
        });

        fetch('/dashboard-cover-combine' + queryParameters)
        .then(response => response.json())
        .then(data => {
            createBarChart('coverChartCombine', data);
        });

    // fetch('/dashboard-fst-spec' + queryParameters)
    //     .then(response => response.json())
    //     .then(data => {
    //         createBarChart('fstSpecChart', data);
    //     });

    // fetch('/dashboard-fst' + queryParameters)
    //     .then(response => response.json())
    //     .then(data => {
    //         createBarChart('fstChart', data);
    //     });

    // fetch('/dashboard-spec' + queryParameters)
    //     .then(response => response.json())
    //     .then(data => {
    //         createBarChart('specChart', data);
    //     });

    fetch('/dashboard-cover-profit' + queryParameters)
        .then(response => response.json())
        .then(data => {
            createPieChart('coverChartProfit', data);
        });

    fetch('/dashboard-cover-profit-absent' + queryParameters)
        .then(response => response.json())
        .then(data => {
            createPieChart('coverChartProfitAbsent', data);
        });

    fetch('/dashboard-cover-profit-cycle' + queryParameters)
        .then(response => response.json())
        .then(data => {
            createPieChart('coverChartProfitCycle', data);
        });

        fetch('/dashboard-cover-profit-combine' + queryParameters)
        .then(response => response.json())
        .then(data => {
            createPieChart('coverChartProfitCombine', data);
        });

    // fetch('/dashboard-fst-spec-profit' + queryParameters)
    //     .then(response => response.json())
    //     .then(data => {
    //         createPieChart('fstSpecChartProfit', data);
    //     });

    // fetch('/dashboard-spec-profit' + queryParameters)
    //     .then(response => response.json())
    //     .then(data => {
    //         createPieChart('specChartProfit', data);
    //     });

    // fetch('/dashboard-fst-profit' + queryParameters)
    //     .then(response => response.json())
    //     .then(data => {
    //         createPieChart('fstChartProfit', data);
    //     });
}

function convertToTransparentColor(color) {
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
                backgroundColor: data.map(item => convertToTransparentColor(item.color)),
                borderColor: data.map(item => item.color),
                borderWidth: 1
            }, {
                type: 'line',
                label: 'Prediction accuracy',
                data: lines,
                borderColor: '#34b7eb',
                backgroundColor: '#34b7eb',
                datalabels: {
                    align: 'end',
                    anchor: 'end',
                }
            }]
        },
        plugins: [ChartDataLabels],
        options: {
            hover: { mode: null },
            responsive: true,
            maintainAspectRatio: false,
            legend: { display: false },
            plugins: {
                datalabels: {
                    backgroundColor: function (context) {
                        return context.dataset.backgroundColor;
                    },
                    borderRadius: 4,
                    color: 'white',
                    font: {
                        weight: 'bold',
                        size: 9
                    },
                    formatter: function (value, context) {
                        if (context.dataset.type === 'line') {
                            return (value * 100 / maxValue).toFixed(0) + '%';
                        } else {
                            return null;
                        }
                    },
                    padding: 6
                }
            },
            // Core options
            aspectRatio: 5 / 3,
            layout: {
                padding: {
                    top: 32,
                    right: 16,
                    bottom: 16,
                    left: 8
                }
            },
            elements: {
                line: {
                    fill: false,
                    tension: 0.4
                }
            },
            scales: {
                y: {
                    stacked: true
                }
            }
        }
    });
    chartList.push(chart);
}

function createPieChart(chartId, data) {
    let ctx = document.getElementById(chartId).getContext('2d');
    const pay = data.filter(x => x.label === 'Total Pay')[0].value
    const win = data.filter(x => x.label === 'Total Winning')[0].value
    const profit = win - pay
    const formattedProfit = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(profit)

    let chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(item => item.label),
            datasets: [{
                data: data.map(item => item.value),
                backgroundColor: data.map(item => convertToTransparentColor(item.color)),
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
            plugins: {
                datalabels: {
                    backgroundColor: function (context) {
                        return context.dataset.backgroundColor;
                    },
                    borderRadius: 4,
                    color: 'black',
                    font: {
                        weight: 'bold',
                        size: 9
                    },
                    formatter: function (value, context) {
                        return value.toLocaleString('vi-VN', { style: 'currency', currency: 'VND' });
                    },
                    padding: 6
                },
                title: {
                    display: true,
                    text: 'Current profit: ' + formattedProfit,
                    font: {
                        size: 20
                    },
                    padding: {
                        top: 10,
                        bottom: 30
                    }
                }
            }
        }
    });
    chartList.push(chart);
}
