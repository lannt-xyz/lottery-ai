from telegram import Bot
from LotteryAi import LotteryAi
import datetime
import json
import os
from dotenv import load_dotenv
import asyncio
from DataAccess import DataAccess

load_dotenv()

lotMap = json.loads(os.getenv('LOT_MAP'))
# get bot token from .env file
bot_token = os.getenv('BOT_TOKEN')

# Initialize Telegram bot
bot = Bot(token=bot_token)

# Get the current day of the week
today = datetime.date.today()
dayOfWeek = today.weekday()

# Get the city codes of the current day
cityCodes = lotMap[str(dayOfWeek)]

# Initialize the LotteryAi
aiLot = LotteryAi()

# Generate the predictions
predictions = ['Today\'s Predictions:' + today.strftime('%A, %B %d, %Y') + ':']
for cityCode in cityCodes:
    result = aiLot.predict(cityCode, 1)
    predictions.append(f"- {cityCode}: {', '.join(result)}")

    # store the prediction to sqlite db by DataAccess
    dataAccess = DataAccess()
    joined = '_'.join(result)
    dataAccess.insertPrediction(today.strftime('%Y-%m-%d'), cityCode, joined)

message = "\n".join(predictions)
print(message)

# get chat id from .env file
chat_id = os.getenv('CHAT_ID')

# Send all predictions as a single message
asyncio.run(bot.send_message(chat_id='1945394605', text=message))
