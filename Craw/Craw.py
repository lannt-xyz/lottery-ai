from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

from Utils.LotteryAi import LotteryAi
from Utils.XSBD import XSBD
from Utils.KQXSVN import KQXSVN
from Utils.KQXSVNFirstSpecial import KQXSVNFirstSpecial
from Utils.Vietlot655 import Vietlot655
from Utils.VietlotKeno import VietlotKeno
from DB.DataAccess import DataAccess
from Logging.Config import configure_logger

# load .env variables
load_dotenv()

logger = configure_logger(__name__)

# create the output directory if not exist
dir_name = os.getenv('STORE_DIR')
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

# define endDate is the previous day of the system date
endDate = datetime.now()


# get the environment variables, if not set then use the default value
envStartDate = os.getenv('CRAWING_START_DATE')
envEndDate = os.getenv('CRAWING_END_DATE')
if envStartDate is not None and envStartDate != '':
    logger.info('Crawing from: %s', envStartDate)
    startDate = datetime.strptime(envStartDate, '%Y-%m-%d')
if envEndDate is not None and envEndDate != '':
    logger.info('Crawing to: %s', envEndDate)
    endDate = datetime.strptime(envEndDate, '%Y-%m-%d')

crawingTargetNames = os.getenv('CRAWING_TARGET')
if crawingTargetNames is not None and crawingTargetNames != '':
    crawingTargetNames = crawingTargetNames.split(',')
else:
    crawingTargetNames = ['XSBD', 'Vietlot655', 'KQXSVN']

logger.info("Crawing Target: " + str(crawingTargetNames))
logger.info("Start Crawing: " + startDate.strftime('%Y-%m-%d'))

# define the processing date is the startDate
processingDate = startDate

# must re-train the model
mustRetrain = []

def merge_prize(exitingPrizeMap, newPrizeMap):
    if newPrizeMap is not None:
        if exitingPrizeMap is not None:
            for key in newPrizeMap:
                if key in exitingPrizeMap:
                    exitingPrizeMap[key] = exitingPrizeMap[key] + newPrizeMap[key]
                else:
                    exitingPrizeMap[key] = newPrizeMap[key]

def craw(targetDate: datetime):
    # define the prizzeMap is empty
    prizzeMap = {}

    for crawingTargetName in crawingTargetNames:
        crawingTarget = globals()[crawingTargetName]()
        crawingTargetMap = crawingTarget.craw(targetDate)
        merge_prize(prizzeMap, crawingTargetMap)

    # if prizzeMap is None then increase the processing date by 1 day
    if prizzeMap is None:
        return

    # get all the keys of the prizzeMap, then sort the keys
    keys = sorted(prizzeMap.keys())

    # with each prize in the prizzeMap, write to each file with the name is the key of the prizzeMap
    for key in keys:
        # key may contains the __1, __2, __3, ... so we need to get the text before for the cityCode
        cityCode = key.split('__')[0]
        print(cityCode)

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
                    # convert to number before writing to the file
                    sortedPrize = list(map(int, prizzeMap[key]))
                    # convert to string before writing to the file
                    sortedPrize = list(map(str, sortedPrize))
                    # write to the file with the format is csv
                    f.write(','.join(sortedPrize) + '\n')
                except Exception as e:
                    logger.error('Error: ', prizzeMap[key])
                    logger.exception('Exception occurred: %s', e)
                    continue

        # add the cityCode to the mustRetrain list
        mustRetrain.append(cityCode)

    targetDateStr = targetDate.strftime('%Y-%m-%d')

    # if envStartDate is not None or envStartDate is not empty then
    if envStartDate is not None and envStartDate != '':
        # store the processing date to the file for the next run as a checkpoint
        with open(checkpointFile, 'w') as f:
            f.write(targetDateStr)

    # store the prizeMap to a file named `actual.csv` to sqlite db by DataAccess
    dataAccess = DataAccess()
    for key in prizzeMap:
        # convert prizzeMap[key] to string array before insert to the database
        dataAccess.insertActual(targetDateStr, key, '_'.join(list(map(str, prizzeMap[key]))))

# loop until the processing date is less than or equal to the endDate
while processingDate <= endDate:
    try:
        logger.info('Crawing: ' + processingDate.strftime('%Y-%m-%d'))
        craw(processingDate)
    except Exception as e:
        logger.exception("Exception occurred: %s", e)
    finally:
        # increase the processing date by 1 day
        processingDate += timedelta(days=1)


logger.info('End crawing: ' + endDate.strftime('%Y-%m-%d'))

# distinct the mustRetrain
mustRetrain = list(set(mustRetrain))

logger.info('Must retrain: %s', mustRetrain)
logger.info('Start retrain model...')
# Training the model
for file in mustRetrain:
    logger.info('Training model for: %s', file)
    ai = LotteryAi()
    ai.train(file)
logger.info('Finish retrain model...')
