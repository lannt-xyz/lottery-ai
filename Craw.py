from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from LotteryAi import LotteryAi
from XSBD import XSBD
from Vietlot import Vietlot
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
    prizzeMap = []

    # call the function craw to get the prizzeMap from XSBD
    xsbdMap = XSBD().craw(processingDate)

    # call the function craw to get the prizzeMap from Vietlot, if None then not set the prizzeMap
    vietlotMap = Vietlot().craw(processingDate)

    # merge the prizzeMap from XSBD and Vietlot
    if xsbdMap is not None:
        prizzeMap = xsbdMap
    if vietlotMap is not None:
        if prizzeMap is not None:
            for key in vietlotMap:
                if key in prizzeMap:
                    prizzeMap[key] = prizzeMap[key] + vietlotMap[key]
                else:
                    prizzeMap[key] = vietlotMap[key]

    # if prizzeMap is None then increase the processing date by 1 day
    if prizzeMap is None:
        processingDate += timedelta(days=1)
        continue

    # with each prize in the prizzeMap, write to each file with the name is the key of the prizzeMap
    for key in prizzeMap:
        mustRetrain.append(key)

        # create the file if not exist
        fileName = dir_name + '/' + key + '.csv'
        if not os.path.exists(fileName):
            with open(fileName, 'w') as f:
                f.write('')
        # write the prize to the file
        with open(fileName, 'a') as f:
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
    # store the processing date to the file for the next run as a checkpoint
    with open(checkpointFile, 'w') as f:
        f.write(processingDateStr)

    # store the prizeMap to a file named `actual.csv` to sqlite db by DataAccess
    dataAccess = DataAccess()
    for key in prizzeMap:
        dataAccess.insertActual(processingDateStr, key, '_'.join(prizzeMap[key]))

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
