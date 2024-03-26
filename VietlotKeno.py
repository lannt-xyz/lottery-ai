import requests
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup

# define constant for the URL
URL = 'https://vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.GameKenoCompareWebPart,Vietlott.PlugIn.WebParts.ashx'

# define constant for the ROW_PER_PAGE
ROW_PER_PAGE = 6

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
        "WebPage": None,
        "SiteName": "Vietlott",
        "OrgPageAlias": None,
        "PageAlias": None,
        "FullPageAlias": None,
        "RefKey": None,
        "System": 1
    },
    "GameId": "6",
    "GameDrawNo": "",
    "number": "",
    "DrawDate": "14/07/2023",
    "ProcessType": 0,
    "OddEven": 2,
    "UpperLower": 2,
    "PageIndex": 0,
    "TotalRow": 0
}

class VietlotKeno:
    def __init__(self):
        # Initialize any variables you need here
        pass

    def craw(self, processingDate: datetime):
        results = {}
        firstRun = self.request(processingDate, 0, 0)
        if firstRun is None:
            return results
        # get number of records
        rowNum = firstRun['value']['RetNumber']

        # calculate loopIndex = ceil(rowNum / ROW_PER_PAGE)
        loopIndex = rowNum // ROW_PER_PAGE
        print('loopIndex: ', loopIndex)
        while loopIndex > 0:
            crawData = self.crawData(processingDate, loopIndex, rowNum)
            if crawData is not None:
                for data in crawData:
                    results.update(data)
            loopIndex -= 1

        return results

    def request(self, processingDate: datetime, pageIndex: int = 0, totalRow: int = 0):
        # prepare the payload for the request
        payload['DrawDate'] = processingDate.strftime('%d/%m/%Y')
        payload['PageIndex'] = pageIndex
        payload['TotalRow'] = totalRow
        data = json.dumps(payload)

        r = requests.post(URL, data=data, headers={'Content-Type': 'application/json', 'x-ajaxpro-method': 'ServerSideDrawResult'})

        # the response is the text in json format, so we need to convert it to object
        if r.status_code != 200:
            print('Error: ', r.status_code)
            return None

        # convert the response to object
        return r.json()

    def crawData(self, processingDate: datetime, pageIndex: int = 0, totalRow: int = 0):
        # call the request function to get the response
        r = self.request(processingDate, pageIndex, totalRow)

        # if the response is None, then return None
        if r is None or r['value'] is None:
            return None

        value = r['value']
        html = value['HtmlContent']
        # replace the `\r\n` with empty string
        html = html.replace('\r\n', '')

        # Parse the HTML content with BeautifulSoup
        divResultContent = BeautifulSoup(html, 'html.parser')

        # find the table on the divResultContent
        table = divResultContent.find('table')
        # if the table is None, then return None
        if table is None:
            return None

        # find all row belonging the tbody of the table
        rows = table.find('tbody').find_all('tr')
        # the first row is the header, so we need to remove it
        rows = rows[1:]

        # if the length of the rows is 0, then hasNextFlag is false
        # for debuging stop process for 10 pages ->> add `or pageIndex == 10`
        if len(rows) == 0:
            return None

        # on each row, find all cell and print the text of each cell
        numbers = []
        for row in rows:
            cells = row.find_all('td')
            # extract date on the first cell is the child element as a link
            date = cells[0].find('a').text

            # compare the date value with the processing date
            if date != processingDate.strftime('%d/%m/%Y'):
                continue

            # get value of the td
            td = cells[1]

            # find the div tag with class is `day_so_ket_qua_v2` as the winning number container in the third cell
            containers = td.find_all('div', {'class': 'day_so_ket_qua_v2'})

            winning_numbers = []
            for container in containers:
                # extract the winning number on the third cell with span tag has class is `day_so_ket_qua_v2` for each number
                winning_number = container.find_all('span', {'class': 'bong_tron'})
                targetNumber = [number.text for number in winning_number]
                winning_numbers.append(targetNumber)

            # wining numbers is a list of list, so flatten it
            winning_numbers = [item for sublist in winning_numbers for item in sublist]

            # crawlData is an two-dimensional array, it may include the empty arrays, so remove it
            winning_numbers = [item for item in winning_numbers if item]

            if len(winning_numbers) == 0:
                continue

            # extract term on the first cell is the child element as a link which wrapped by div
            term = cells[0].find('div').find('a').text

            prizze = {
                f'vietlot-keno__{term}': winning_numbers
            }

            numbers.append(prizze)

        return numbers
