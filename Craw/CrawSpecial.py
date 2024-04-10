from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from XSBDSpecial import XSBDSpecial

# load .env variables
load_dotenv()

# create the output directory if not exist
dir_name = os.getenv('OUTDIR') + '/xosobinhduong_special'
if not os.path.exists(dir_name):
    os.mkdir(dir_name)

# define startDate is 2019-06-03 in Date data type with format is yyyy-MM-dd
startDate = datetime.strptime('2019-06-03', '%Y-%m-%d')

# define endDate is the previous day of the system date
endDate = datetime.now()


# TODO: remove debug code
# startDate = datetime.strptime('2024-03-27', '%Y-%m-%d')
# endDate = datetime.strptime('2019-06-10', '%Y-%m-%d')


print("Start Crawing: " + startDate.strftime('%Y-%m-%d'))

# define the processing date is the startDate
processingDate = startDate

# loop until the processing date is less than or equal to the endDate
while processingDate <= endDate:
    # find the day of the week of the processing date
    dayOfWeek = processingDate.weekday()
    # if the day of the week is not Monday, then increase the processing date by 1 day
    if dayOfWeek != 0:
        processingDate += timedelta(days=1)
        continue

    # define the prizzeMap is empty
    prizzeMap = {}

    # call the function craw to get the prizzeMap from XSBD
    xsbdMap = XSBDSpecial().craw(processingDate)
    if xsbdMap is not None:
        prizzeMap = xsbdMap

    # if prizzeMap is None then increase the processing date by 1 day
    if prizzeMap is None:
        processingDate += timedelta(days=1)
        continue

    # get all the keys of the prizzeMap, then sort the keys
    keys = sorted(prizzeMap.keys())

    # with each prize in the prizzeMap, write to each file with the name is the key of the prizzeMap
    for key in keys:
        # key may contains the __1, __2, __3, ... so we need to get the text before for the cityCode
        cityCode = key.split('__')[0]

        # create the file if not exist
        filePath = f'{dir_name}/{cityCode}.csv'
        if not os.path.exists(filePath):
            with open(filePath, 'w') as f:
                f.write('')
        # write the prize to the file
        with open(filePath, 'a') as f:
            # try to skip the error when the prizzeMap[key] is empty or prizzeMap[key] is empty
            if len(prizzeMap[key]) > 0:
                try:
                    # convert to number and sort the list before writing to the file
                    sortedPrize = sorted(list(map(int, prizzeMap[key])))
                    # convert to string before writing to the file
                    sortedPrize = list(map(str, sortedPrize))
                    # write to the file with the format is csv
                    f.write(','.join(sortedPrize) + '\n')
                except:
                    print('Error: ', prizzeMap[key])
                    continue

    processingDateStr = processingDate.strftime('%Y-%m-%d')

    # increase the processing date by 1 day
    processingDate += timedelta(days=1)

print('End crawling: ' + endDate.strftime('%Y-%m-%d'))
