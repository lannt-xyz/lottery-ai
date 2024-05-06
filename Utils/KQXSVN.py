import requests
from unidecode import unidecode
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# define constant for the URL
URL = 'https://www.kqxs.vn/mien-nam?date='

class KQXSVN:
    def __init__(self):
        # Initialize any variables you need here
        pass

    def craw(self, processingDate: datetime):
        # request URL will be the URL with the processing date in the format yyyy-MM-dd
        requestUrl = URL + processingDate.strftime('%d-%m-%Y')
        print('Crawing date: ' + processingDate.strftime('%Y-%m-%d'))
        # Make a request to the URL with the payload in the POST method
        r = requests.get(requestUrl)

        # the response is the text in json format, so we need to convert it to object
        if r.status_code != 200:
            print('Error: ', r.status_code)
            processingDate += timedelta(days=1)
            return None

        # convert the response to BeautifulSoup object
        response = BeautifulSoup(r.text, 'html.parser')
        # find the table with class `table-result-lottery`
        table = response.find('table', class_='table-result-lottery')
        # process next date if the table is not exist
        if table is None:
            processingDate += timedelta(days=1)
            return {}

        # find the tbody in the table
        tbody = table.find('tbody')

        # find the channelWrapper which is the first row all rows in the tbody
        rows = tbody.find_all('tr')
        # get the first row
        channelWrapper = rows[0]
        # get the channelWrapper's cells which is the td tag has class `results`
        channelWrapper = channelWrapper.find('td', class_='results')
        # channel is the span tags in the channelWrapper
        channels = channelWrapper.find_all('span')
        # get the channel name by getting text inside the span tags
        channels = [x.text for x in channels]
        # get the channel code by convert vietnamese to non-vietnamese
        channels = [unidecode(x).lower().replace(' ', '-') for x in channels]
        # if the channel is `ho-chi-minh`, then replace it with `tp-hcm`
        channels = ['tp-hcm' if x == 'ho-chi-minh' else x for x in channels]

        # define a map to store the prizzeValue and cityCode
        prizzeMap = {}
        # loop through all rows in the tbody ignoring the first row
        for row in rows[1:]:
            # get the results
            cells = row.find('td', class_='results')
            # get the numberWrapper
            numberWrapper = cells.find('div', class_='quantity-of-number')
            # get the numbers
            numbers = numberWrapper.find_all('span', class_='number')
            numbers = [x['data-value'] for x in numbers]

            # find quantity of the numbers is the div tag has class `quantity-of-number`
            quantity = row.find('div', class_='quantity-of-number')
            # get the quantity of the numbers is the property `data-quantity`, then convert it to integer
            quantity = quantity['data-quantity']
            quantity = int(quantity)

            # loop through all the numbers
            index = 0
            for number in numbers:
                # get the city code by getting the index of the number
                cityCode = channels[index % (quantity)]

                # extract number to get the last 2 numbers
                prizzeTail = number[-2:]
                # if cityCode is not exist in the prizzeMap, then create a new list for the cityCode
                if cityCode not in prizzeMap:
                    prizzeMap[cityCode] = [prizzeTail]
                else:
                    prizzeMap[cityCode].append(prizzeTail)

                index += 1

        return prizzeMap
