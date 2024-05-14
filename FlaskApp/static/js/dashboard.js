$(document).ready(function () {

    fetch('/dashboard-cover')
        .then(response => response.json())
        .then(data => {
            createBarChart('coverChart', data);
        });

    fetch('/dashboard-fst-spec')
        .then(response => response.json())
        .then(data => {
            createBarChart('fstSpecChart', data);
        });

    fetch('/dashboard-cover-profit')
        .then(response => response.json())
        .then(data => {
            createPieChart('coverChartProfit', data);
        });

    fetch('/dashboard-fst-spec-profit')
        .then(response => response.json())
        .then(data => {
            createPieChart('fstSpecChartProfit', data);
        });

});

function convertToTransparentColor(item) {
    let color = item.color;
    color = color.replace('#', '');
    let r = parseInt(color.substring(0, 2), 16);
    let g = parseInt(color.substring(2, 4), 16);
    let b = parseInt(color.substring(4, 6), 16);
    return 'rgba(' + r + ',' + g + ',' + b + ',0.2)';
}

function createBarChart(chartName, data) {
    var canvas = document.getElementById(chartName);
    var ctx = canvas.getContext('2d');

    fetch('/dashboard-accuracy')
        .then(response => response.json())
        .then(lineData => {
            var lines = [];
            var maxValue = Math.max(...data.map(item => item.count));
            data.forEach(e => {
                let predication = x => e.label == x.label;
                if ('fstSpecChart' == chartName) {
                    predication = x => x.label.includes('fstSpec_') && x.label.replace('fstSpec_', '') == e.label;
                }
                let line = lineData.filter(predication).map(x => x.value * maxValue / 100)[0];
                lines.push(line);
            });

            new Chart(ctx, {
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
        });
}

function createPieChart(chartId, data) {
    var ctx = document.getElementById(chartId).getContext('2d');
    new Chart(ctx, {
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
                        var value = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                        var res = value.toLocaleString('vi-VN', { style: 'currency', currency: 'VND' });
                        console.log(res);
                        return res;
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false,
        }
    });
}
