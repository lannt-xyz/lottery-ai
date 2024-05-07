import requests
from datetime import datetime, timedelta
from Logging.Config import configure_logger

logger = configure_logger(__name__)

# define constant for the URL
URL = 'https://www.xosobinhduong.com.vn/get-lottery-mn?mask=getResultLoteryMn&skip=true&flagNumber=-1&lotdate='

class XSBD:
    def __init__(self):
        # Initialize any variables you need here
        pass

    def craw(self, processingDate: datetime):
        # request URL will be the URL with the processing date in the format yyyy-MM-dd
        requestUrl = URL + processingDate.strftime('%Y-%m-%d')

        # Make a request to the URL with the payload in the POST method
        r = requests.post(requestUrl)

        # the response is the text in json format, so we need to convert it to object
        if r.status_code != 200:
            logger.info('Error: %s', r.status_code)
            processingDate += timedelta(days=1)
            return None

        # convert the response to object
        jsonStr = r.json()

        # check the status of the response
        status = jsonStr['status']
        if status != 1:
            logger.info('Error: %s', jsonStr['message'])
            processingDate += timedelta(days=1)
            return None

        data = jsonStr['data']
        # define a map to store the prizzeValue and cityCode
        prizzeMap = {}
        for record in data['body']:
            for prizze in record['data']:
                for prizzeDetail in prizze:
                    prizzeValue = prizzeDetail['value']
                    # extract prizzeValue to get the last 2 numbers
                    prizzeTail = prizzeValue[-2:]
                    cityCode = prizzeDetail['city_code']
                    # if cityCode is not exist in the prizzeMap, then create a new list for the cityCode
                    if cityCode not in prizzeMap:
                        prizzeMap[cityCode] = [prizzeTail]
                    else:
                        prizzeMap[cityCode].append(prizzeTail)

        return prizzeMap
