import datetime
import json
import os
import asyncio

from collections import defaultdict
from dotenv import load_dotenv
from telegram import Bot

from DB.DataAccess import DataAccess

load_dotenv()

lotMap = json.loads(os.getenv('LOT_MAP'))
# get bot token from .env file
bot_token = os.getenv('BOT_TOKEN')

# Initialize Telegram bot
bot = Bot(token=bot_token)

# Get the current day of the week
today = datetime.date.today()
# Generate the predictions
predictions = ['Today\'s Results:' + today.strftime('%A, %B %d, %Y') + ':']

today_str = today.strftime('%Y-%m-%d')
dataAccess = DataAccess()
results = dataAccess.getResults(today_str, today_str, False).to_dict(orient='records')

# Group by cityCode
grouped_results = defaultdict(list)
for result in results:
    grouped_results[result['cityCode']].append(result)

# Categorize results by prefix and then by cityCode
categorized_results = defaultdict(lambda: defaultdict(list))
for result in results:
    cityCode = result['cityCode']
    if cityCode.startswith('cycle_'):
        category = 'Cycle'
        newCityCode = cityCode.split('cycle_')[1]
    elif cityCode.startswith('absent_'):
        category = 'Absent'
        newCityCode = cityCode.split('absent_')[1]
    elif cityCode.startswith('combine_'):
        category = 'Combine'
        newCityCode = cityCode.split('combine_')[1]
    else:
        category = 'Common'  # Change from 'Other' to 'Common'
        newCityCode = cityCode
    categorized_results[category][newCityCode].append(result)

# Create the output string with categories
for category, cities in categorized_results.items():
    # Add category heading for all categories including 'Common'
    predictions.append(f"{category}:")
    for cityCode, entries in cities.items():
        for entry in entries:
            prediction_found = entry['prediction'] in entry['actual']
            found_text = 'Yes' if prediction_found else 'No'
            # Indent all entries, including those under 'Common'
            predictions.append(f"  - {cityCode}, Prediction: {entry['prediction']}, Found: {found_text}")


message = "\n".join(predictions)
# print(message)

# get chat id from .env file
chat_id = os.getenv('CHAT_ID')

# Send all predictions as a single message
asyncio.run(bot.send_message(chat_id=chat_id, text=message))
