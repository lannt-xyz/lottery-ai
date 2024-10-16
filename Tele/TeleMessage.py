import datetime
import json
import os
import asyncio

from dotenv import load_dotenv
from telegram import Bot

from Utils.LotteryAi import LotteryAi
from DB.DataAccess import DataAccess
from PredictedDecision.DecisionMaker import DecisionMaker

load_dotenv()

lotMap = json.loads(os.getenv('LOT_MAP'))
# get bot token from .env file
bot_token = os.getenv('BOT_TOKEN')

# Initialize Telegram bot
bot = Bot(token=bot_token)

# Get the current day of the week
today = datetime.date.today()
# change value of today if the environment variable is set
if 'PREDICT_DATE' in os.environ:
    today = datetime.datetime.strptime(os.environ['PREDICT_DATE'], '%Y-%m-%d')
    print('today:', today)

#today = datetime.datetime(2024, 4, 6)
dayOfWeek = today.weekday()

# Get the city codes of the current day
cityCodes = lotMap[str(dayOfWeek)]
# for each item on the cityCodes, if does not `vietlot-655` then keeping current and add a new item with prefix is `fstSpec` to the list
cityCodes = [cityCode for cityCode in cityCodes if cityCode != 'vietlot-655'] # + [f'fstSpec_{cityCode}' for cityCode in cityCodes]
print('cityCodes:', cityCodes)

def getPredictionNumberBasedOnCityCode(cityCode):
    if cityCode == 'vietlot-655':
        return 7
    elif 'fstSpec' in cityCode:
        return 2
    else:
        return 18

# Initialize the LotteryAi
aiLot = LotteryAi()

# Generate the predictions
predictions = ['Today\'s Predictions:' + today.strftime('%A, %B %d, %Y') + ':']
for cityCode in cityCodes:
    numberOfPredictionNumber = getPredictionNumberBasedOnCityCode(cityCode)
    result = aiLot.predict(cityCode, numberOfPredictionNumber)
    # convert result to array of int
    predicted_number = [int(x) for x in result]
    decisionMaker = DecisionMaker(cityCode)
    if cityCode != 'vietlot-655' and 'fstSpec' not in cityCode:
        # find the most common number in the result
        mostCommon = str(decisionMaker.most_common(predicted_number))
        print('mostCommon:', mostCommon)
        result = [mostCommon]

    predictions.append(f"- {cityCode}: {', '.join(result)}")

    # store the prediction to sqlite db by DataAccess
    dataAccess = DataAccess()
    joined = '_'.join(result)
    dataAccess.insertPrediction(today.strftime('%Y-%m-%d'), cityCode, joined)

    longest_absent_number = decisionMaker.longest_absent_number(predicted_number)
    print('longest absent number:', longest_absent_number)
    dataAccess.insertPrediction(today.strftime('%Y-%m-%d'), 'absent_' + cityCode, longest_absent_number)

    most_consistent_number = decisionMaker.most_consistent_cycle(predicted_number)
    print('most consistent cycle:', most_consistent_number)
    dataAccess.insertPrediction(today.strftime('%Y-%m-%d'), 'cycle_' + cityCode, most_consistent_number)

    combined_absent_cycle = decisionMaker.calculate_combined_score(predicted_number)
    print('combined absent and cycle:', combined_absent_cycle)
    dataAccess.insertPrediction(today.strftime('%Y-%m-%d'), 'combine_' + cityCode, combined_absent_cycle)

    # convert predicted_number to array of str
    predicted_number_str = [str(x) for x in predicted_number]
    # store the full prediction from LotteryAi
    joined_prediction = '_'.join(predicted_number_str)
    print('joined_prediction:', joined_prediction)
    dataAccess.insertFullPrediction(today.strftime('%Y-%m-%d'), cityCode, joined_prediction)


message = "\n".join(predictions)
# print(message)

# get chat id from .env file
chat_id = os.getenv('CHAT_ID')

# Send all predictions as a single message
asyncio.run(bot.send_message(chat_id=chat_id, text=message))
