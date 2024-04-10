import datetime
import json
import os
import asyncio

from dotenv import load_dotenv
from telegram import Bot

from Utils.LotteryAi import LotteryAi
from DB.DataAccess import DataAccess

load_dotenv()

lotMap = json.loads(os.getenv('LOT_MAP'))
# get bot token from .env file
bot_token = os.getenv('BOT_TOKEN')

# Initialize Telegram bot
bot = Bot(token=bot_token)

# Get the current day of the week
today = datetime.date.today()
#today = datetime.datetime(2024, 4, 6)
dayOfWeek = today.weekday()

# Get the city codes of the current day
cityCodes = lotMap[str(dayOfWeek)]

# Initialize the LotteryAi
aiLot = LotteryAi()

# Generate the predictions
predictions = ['Today\'s Predictions:' + today.strftime('%A, %B %d, %Y') + ':']
for cityCode in cityCodes:
    result = aiLot.deep_predict(cityCode, None, 1)
    print (result)

    predictions.append(f"- {cityCode}: {', '.join(result)}")

    # store the prediction to sqlite db by DataAccess
    dataAccess = DataAccess()
    joined = '_'.join(result)
    dataAccess.insertPrediction(today.strftime('%Y-%m-%d'), cityCode, joined)

message = "\n".join(predictions)
# print(message)

# get chat id from .env file
chat_id = os.getenv('CHAT_ID')

# Send all predictions as a single message
asyncio.run(bot.send_message(chat_id=chat_id, text=message))
