import requests
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup
from Logging.Config import configure_logger

logger = configure_logger(__name__)


# define constant for the URL
URL = 'https://vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.Game655CompareWebPart,Vietlott.PlugIn.WebParts.ashx'

# define the payload for the request in json format then converting to object
payload = {
    "ORenderInfo": {
        "SiteId": "main.frontend.vi",
        "SiteAlias": "main.vi",
        "UserSessionId": "",
        "SiteLang": "vi",
        "IsPageDesign": False,
        "ExtraParam1": "",
        "ExtraParam2": "",
        "ExtraParam3": "",
        "SiteURL": "",
        "WebPage": "",
        "SiteName": "Vietlott",
        "OrgPageAlias": "",
        "PageAlias": "",
        "FullPageAlias": "",
        "RefKey": "",
        "System": 1
    },
    "Key": "b8fc87f6",
    "GameDrawId": "",
    "ArrayNumbers": [
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
        ]
    ],
    "CheckMulti": False,
    "PageIndex": 0
}

class Vietlot655:
    def __init__(self):
        # Initialize any variables you need here
        pass

    def craw(self, processingDate: datetime):
        payload['PageIndex'] = 0
        data = json.dumps(payload)
        r = requests.post(URL, data=data, headers={'Content-Type': 'application/json', 'x-ajaxpro-method': 'ServerSideDrawResult'})

        # the response is the text in json format, so we need to convert it to object
        if r.status_code != 200:
            logger.info('Error: %s', r.status_code)
            return None

        # convert the response to object
        r = r.json()

        # get the value of `HtmlContent` key inside the `value` key for the HTML content
        r = r['value']['HtmlContent']

        # replace the `\r\n` with empty string
        r = r.replace('\r\n', '')

        # Parse the HTML content with BeautifulSoup
        divResultContent = BeautifulSoup(r, 'html.parser')

        # find the table on the divResultContent
        table = divResultContent.find('table')

        # find all row belonging the tbody of the table
        rows = table.find('tbody').find_all('tr')

        # if the length of the rows is 0, then hasNextFlag is false
        # for debuging stop process for 10 pages ->> add `or pageIndex == 10`
        if len(rows) == 0:
            return None

        numbers = []
        for row in rows:
            cells = row.find_all('td')
            # extract date on the first cell
            date = cells[0].text

            # compare the date value with the processing date
            if date != processingDate.strftime('%d/%m/%Y'):
                continue

            # find the div tag with class is `day_so_ket_qua_v2` as the winning number container in the third cell
            container = cells[2].find('div', {'class': 'day_so_ket_qua_v2'})
            # extract the winning number on the third cell with span tag has class is `day_so_ket_qua_v2` for each number
            winning_numbers = container.find_all('span', {'class': 'bong_tron'})
            # the main wining number is the first 6 numbers
            main_winning_numbers = winning_numbers[:6]
            # the additional winning number is the last number
            additional_winning_number = winning_numbers[6]

            # merging main_winning_numbers and additional_winning_number to one and then convert an array of string to integers
            numbers = [number.text for number in main_winning_numbers]
            numbers.append(additional_winning_number.text)
            numbers = list(map(int, numbers))

            # sorting data ascending
            numbers.sort()

        # return None if numbers is empty
        if len(numbers) == 0:
            return None

        prizzeMap = {
            'vietlot-655': numbers
        }

        return prizzeMap
