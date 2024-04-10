import datetime
from LotteryAi import LotteryAi
from VietlotKeno import VietlotKeno
from collections import Counter

import os
from dotenv import load_dotenv

def main():
    # load .env file
    load_dotenv()
    # overwrite value of .env
    os.environ['STORE_DIR'] = './crawing-data_keno/xosobinhduong'
    os.environ['MODEL_DIR'] = './models_keno'

    ai = LotteryAi()
    vietlotKeno = VietlotKeno()
    data = vietlotKeno.craw(datetime.datetime.now())
    # get all key from data
    keys = data.keys()
    # sort the keys by descending
    keys = sorted(keys, reverse=True)
    # get the first 20 keys
    keys = keys[:20]
    # revert sorted keys to ascending
    keys = sorted(keys)
    print(keys)
    # get the value of the first 20 keys
    val_data = [data[key] for key in keys]
    # val_data is a two dimensional array of String, convert it to a two dimensional array of int
    val_data = [[int(val) for val in data] for data in val_data]

    prediction = ai.predict('vietlot-keno', val_data, None)
    # prediction has format like 10(0%) I want extract the number only
    prediction = [pred.split('(')[0] for pred in prediction]
    # convert prediction to int
    prediction = [int(pred) for pred in prediction]
    # sort the prediction
    prediction = sorted(prediction)

    # Flatten val_data from 2D list to 1D list
    flat_val_data = [item for sublist in val_data for item in sublist]

    # Count the occurrences of each number in prediction in flat_val_data
    counter = Counter(flat_val_data)
    print(counter)

    # with each prediction number, get the number of times it appears based on counter in format number:count
    most_common_nums = [f'{pred}:{counter[pred]}' for pred in prediction]

    # sort the most_common_nums by count descending
    most_common_nums = sorted(most_common_nums, key=lambda x: int(x.split(':')[1]), reverse=True)

    # convert prediction to string
    prediction = [str(pred) for pred in prediction]
    print('Prediction: ', ', '.join(prediction))

    print('Most common: ', ', '.join(map(str, most_common_nums)))

if __name__ == "__main__":
    main()
