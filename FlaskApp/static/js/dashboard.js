// Register the plugin to all charts:
Chart.register(ChartDataLabels);

let chartList = [];
let lineData = [];

$(document).ready(function () {
    initializeScreen();
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

    fetch('/matched-results' + queryParameters)
        .then(response => response.json())
        .then(data => {
            let canvas = document.getElementById('matchedPredictionChart');
            let ctx = canvas.getContext('2d');

            // Step 1: Extract dates
            let dates = data.data.map(x => x.date);

            // Step 2: Remove duplicates
            let uniqueDates = dates.reduce((acc, current) => {
            if (acc.indexOf(current) === -1) {
                acc.push(current);
            }
            return acc;
            }, []);

            // Step 3: Sort dates (optional)
            // Assuming your dates are in a format that can be directly compared (e.g., 'YYYY-MM-DD'),
            // otherwise, you might need to parse them into Date objects for comparison.
            uniqueDates.sort((a, b) => new Date(a) - new Date(b));

            let chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: uniqueDates,
                    datasets: [{
                        label: 'Cycle',
                        data: data.data.filter(x => x.type === 'cycle').map(x => x.count),
                        borderColor: '#ff0000',
                        backgroundColor: 'rgba(255, 0, 0, 0.2)',
                        borderWidth: 1,
                        fill: true,
                        tension: 0.4,
                        borderRadius: 20
                    }, {
                        label: 'Absent',
                        data: data.data.filter(x => x.type === 'absent').map(x => x.count),
                        borderColor: '#00ff00',
                        backgroundColor: 'rgba(0, 255, 0, 0.2)',
                        borderWidth: 1,
                        fill: true,
                        tension: 0.4,
                        borderRadius: 20
                    }, {
                        label: 'Combine',
                        data: data.data.filter(x => x.type === 'combine').map(x => x.count),
                        borderColor: '#400C85',
                        backgroundColor: 'rgba(169, 210, 213, 0.2)',
                        borderWidth: 1,
                        fill: true,
                        tension: 0.4,
                        borderRadius: 20
                    }, {
                        label: 'Common',
                        data: data.data.filter(x => x.type === 'common').map(x => x.count),
                        borderColor: '#0000ff',
                        backgroundColor: 'rgba(0, 0, 255, 0.2)',
                        borderWidth: 1,
                        fill: true,
                        tension: 0.4,
                        borderRadius: 20
                    }]
                },
                options: {
                    scales: {
                        x: {
                            type: 'category',
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Matched Count'
                            },
                            ticks: {
                                beginAtZero: true,
                                stepSize: 1
                            }
                        }
                    },
                    // Add responsive options here
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
            chart.canvas.parentNode.style.width = '100%';
            chartList.push(chart);
        });
    
    fetch('/profit-summary' + queryParameters)
        .then(response => response.json())
        .then(data => {
            let canvas = document.getElementById('profitSummaryChart');
            let ctx = canvas.getContext('2d');

            const categories = Object.keys(data);
            const formattedCategories = categories.map(category => category.charAt(0).toUpperCase() + category.slice(1));
            const totalPayData = categories.map(category => data[category].find(item => item.label === "Total Pay").value);
            const totalWinningData = categories.map(category => data[category].find(item => item.label === "Total Winning").value);
            const profitData = totalWinningData.map((winning, index) => winning - totalPayData[index]); // Calculate profit for each category

            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: formattedCategories,
                    datasets: [{
                        label: 'Total Pay',
                        data: totalPayData,
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }, {
                        label: 'Total Winning',
                        data: totalWinningData,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }, {
                        label: 'Profit',
                        data: profitData,
                        backgroundColor: 'rgba(255, 206, 86, 0.2)',
                        borderColor: 'rgba(255, 206, 86, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        x: {
                            stacked: false,
                            title: {
                                display: true,
                                text: 'Decision Making Categories'
                            }
                        },
                        y: {
                            stacked: false,
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Amount (VND)'
                            },
                        }
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        datalabels: {
                            align: 'end',
                            anchor: 'end',
                            formatter: (value, context) => {
                                return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value);
                            }
                        }
                    }
                }
            });

            chart.canvas.parentNode.style.width = '100%';
            chartList.push(chart);
        });
}
