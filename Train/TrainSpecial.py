import os
import json
import datetime
import numpy as np

from dotenv import load_dotenv
from Utils.LotteryAi import LotteryAi

load_dotenv()

# define constant of model directory
MODEL_DIR = os.getenv('MODEL_DIR')

def main():
    lotMap = json.loads(os.getenv('LOT_MAP'))
    # Get the current day of the week
    today = datetime.date.today()
    dayOfWeek = today.weekday()

    # Get the training date from the environment variable
    trainingDate = os.getenv('TRAINING_DATE')
    if trainingDate is not None:
        # parse training date
        try:
            trainingDate = datetime.datetime.strptime(trainingDate, '%Y-%m-%d').date()
            dayOfWeek = trainingDate.weekday()
        except ValueError:
            print('Invalid training date format. Please use YYYY-MM-DD format.')

    # Get the city codes of the current day
    cityCodes = lotMap[str(dayOfWeek)]

    # train model for each channel
    for cityCode in cityCodes:
        train_model(cityCode)

# Function to train the model
def train_model(channel):
    ai = LotteryAi()

    # Load and preprocess data 
    train_data, val_data, max_value = ai.load_data(channel)
    special = np.array([[row[17]] for row in train_data])
    special_val = np.array([[row[17]] for row in val_data])

    # Create and compile model with number_of_feature is 1 fixed and max_value is 99 fixed
    model = ai.create_model(1, 99)

    # Fit the model on the training data and validate on the validation data for 100 epochs
    history = model.fit(special, special, validation_data=(special_val, special_val), epochs=100)

    # Create the model directory if it does not exist
    if not os.path.exists(MODEL_DIR):
        os.mkdir(MODEL_DIR)

    # Delete the previous model file if it exists
    model_file = f'{MODEL_DIR}/{channel}.keras'
    if os.path.exists(model_file):
        os.remove(model_file)

    # Save the model to a file
    model.save(model_file)

    # Get the validation accuracy from the history
    val_accuracy = history.history['val_accuracy'][-1]
    with open(f'{MODEL_DIR}/{channel}_val_accuracy.txt', 'w') as f:
        f.write(str(val_accuracy))


if __name__ == "__main__":
    main()
