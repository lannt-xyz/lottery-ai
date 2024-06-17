import datetime
import json
import os
import asyncio
import numpy as np
from tensorflow import keras

from dotenv import load_dotenv
from telegram import Bot

from Utils.LotteryAi import LotteryAi
from DB.DataAccess import DataAccess

load_dotenv()

# define constant of model directory
MODEL_DIR = os.getenv('MODEL_DIR')

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
# for each item on the cityCodes, if does not `vietlot-655` then keeping current and add a new item with prefix is `fstSpec` to the list
cityCodes = [cityCode for cityCode in cityCodes if cityCode != 'vietlot-655'] + [f'fstSpec_{cityCode}' for cityCode in cityCodes]
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

# Main function to run everything   
def predict(model_name):
    # Load and preprocess data 
    train_data, val_data, max_value = aiLot.load_data(model_name)
    special_val = np.array([[row[16]] for row in val_data])

    # Load the model from a file
    model_file = f'{MODEL_DIR}/{model_name}.keras'
    print('model_file: ', model_file)
    model = keras.models.load_model(model_file)

    # Predict numbers using trained model 
    predicted_numbers = aiLot.predict_numbers(model, special_val, 1)
    res = predicted_numbers[0]

    # Convert the predicted numbers to a list of strings
    return [str(num) for num in res]

# Generate the predictions
predictions = ['Today\'s Frist Prizze Predictions:' + today.strftime('%A, %B %d, %Y') + ':']
for cityCode in cityCodes:
    if 'fstSpec' in cityCode:
        continue

    result = predict(cityCode)
    predictions.append(f"- {cityCode}: {', '.join(result)}")

    # store the prediction to sqlite db by DataAccess
    dataAccess = DataAccess()
    joined = '_'.join(result)
    dataAccess.insertPrediction(today.strftime('%Y-%m-%d'), 'first_' + cityCode, joined)

message = "\n".join(predictions)
# print(message)

# get chat id from .env file
chat_id = os.getenv('CHAT_ID')

# Send all predictions as a single message
asyncio.run(bot.send_message(chat_id=chat_id, text=message))
