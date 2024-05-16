$(document).ready(function () {
    $('#month-picker').change(function () {
        let selectedMonth = $(this).val();
        let startDate = new Date(selectedMonth + '-01');
        let endDate = new Date(startDate.getFullYear(), startDate.getMonth() + 1, 0, 12);
        startDate = startDate.toISOString().split('T')[0];
        endDate = endDate.toISOString().split('T')[0];

        generateTable(startDate, endDate);
    });

    let date = new Date();
    let month = date.getMonth() + 1; // getMonth() is zero-based
    let year = date.getFullYear();
    month = month < 10 ? '0' + month : month; // prepend 0 to single digit months
    $('#month-picker').val(year + '-' + month).trigger('change');
});

function generateTable(startDate, endDate) {
    // adding the startDate and endDate to the URL as query parameters
    let url = '/results-data?startDate=' + startDate + '&endDate=' + endDate;
    // URL encoded the query parameters
    url = encodeURI(url);

    if ($.fn.dataTable.isDataTable('#result')) {
        // If the table has already been initialized, destroy it
        $('#result').DataTable().destroy();
    }

    new DataTable('#result', {
        ajax: url,
        columns: [
            { data: 'date' },
            { data: 'cityCode' },
            { data: 'prediction' },
            { data: 'actual' },
            { data: 'matched' }
        ],
        paging: false,
        scrollCollapse: true,
        scrollY: '70vh',
        order: [[0, 'desc']],
        drawCallback: function (settings) {
            var lastValue = null;
            var colorClass = 'group1';
            var api = this.api();

            api.rows().every(function () {
                var data = this.data();
                var value = data.date;

                if (value !== lastValue) {
                    // switch color class every time the value changes
                    colorClass = (colorClass === 'group1') ? 'group2' : 'group1';
                    lastValue = value;
                }

                $(this.node()).addClass(colorClass);
            });
        }
    });
}
