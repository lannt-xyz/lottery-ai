window.constants = {
    KEY_MONTH_START_DATE: 'monthStartDate'
};

function getMonthStartDate() {
    var monthStartDate = localStorage.getItem(window.constants.KEY_MONTH_START_DATE);
    if (monthStartDate === null || monthStartDate === undefined || monthStartDate === '') {
        return '01';
    }

    return monthStartDate;
}
