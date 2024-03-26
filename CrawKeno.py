from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from LotteryAi import LotteryAi
from XSBD import XSBD
from Vietlot655 import Vietlot655
from VietlotKeno import VietlotKeno
from DataAccess import DataAccess

# load .env variables
load_dotenv()

# create the output directory if not exist
dir_name = os.getenv('OUTDIR') + '/xosobinhduong'
if not os.path.exists(dir_name):
    os.mkdir(dir_name)

# define startDate is 2019-06-03 in Date data type with format is yyyy-MM-dd
startDate = datetime.strptime('2019-06-03', '%Y-%m-%d')

# check the checkpoint file to get the last processing date
checkpointFile = os.getenv('OUTDIR') + '/' + os.getenv('CHECKPOINT')
if os.path.exists(checkpointFile):
    with open(checkpointFile, 'r') as f:
        startDateStr = f.read()
        # trim the startDate for removing the new line character and white space
        startDateStr = startDateStr.strip()
        # convert the start date to the Date data type if not empty
        if startDateStr != '':
            startDate = datetime.strptime(startDateStr, '%Y-%m-%d')
            # increase the startDate by 1 day
            startDate += timedelta(days=1)

# TODO: remove debug code
#endDate = datetime.strptime('2019-07-01', '%Y-%m-%d')

# define endDate is the previous day of the system date
endDate = datetime.now()

print("Start Crawing: " + startDate.strftime('%Y-%m-%d'))

# define the processing date is the startDate
processingDate = startDate

# must re-train the model
mustRetrain = []

# loop until the processing date is less than or equal to the endDate
while processingDate <= endDate:
    # define the prizzeMap is empty
    prizzeMap = {}

    # # call the function craw to get the prizzeMap from XSBD
    # xsbdMap = XSBD().craw(processingDate)
    # if xsbdMap is not None:
    #     prizzeMap = xsbdMap

    # # call the function craw to get the prizzeMap from Vietlot, if None then not set the prizzeMap
    # vietlot655Map = Vietlot655().craw(processingDate)
    # if vietlot655Map is not None:
    #     if prizzeMap is not None:
    #         for key in vietlot655Map:
    #             if key in prizzeMap:
    #                 prizzeMap[key] = prizzeMap[key] + vietlot655Map[key]
    #             else:
    #                 prizzeMap[key] = vietlot655Map[key]

    # call the function craw to get the prizzeMap from Vietlot, if None then not set the prizzeMap
    vietlotKenoMap = VietlotKeno().craw(processingDate)
    if vietlotKenoMap is not None:
        if prizzeMap is not None:
            for key in vietlotKenoMap:
                if key in prizzeMap:
                    prizzeMap[key] = prizzeMap[key] + vietlotKenoMap[key]
                else:
                    prizzeMap[key] = vietlotKenoMap[key]

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

        # add the cityCode to the mustRetrain list
        mustRetrain.append(cityCode)

    processingDateStr = processingDate.strftime('%Y-%m-%d')
    # store the processing date to the file for the next run as a checkpoint
    with open(checkpointFile, 'w') as f:
        f.write(processingDateStr)

    # store the prizeMap to a file named `actual.csv` to sqlite db by DataAccess
    dataAccess = DataAccess()
    for key in prizzeMap:
        # convert prizzeMap[key] to string array before insert to the database
        dataAccess.insertActual(processingDateStr, key, '_'.join(list(map(str, prizzeMap[key]))))

    # increase the processing date by 1 day
    processingDate += timedelta(days=1)

print('End crawling: ' + endDate.strftime('%Y-%m-%d'))

# distinct the mustRetrain
mustRetrain = list(set(mustRetrain))

print('Must retrain: ', mustRetrain)
print('Start retrain model...')
# Training the model
for file in mustRetrain:
    ai = LotteryAi()
    ai.train(file)
print('Finish retrain model...')
