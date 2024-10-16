import datetime
from Utils.LotteryAi import LotteryAi
from collections import Counter

import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    ai = LotteryAi()
    channel = 'an-giang'
    prediction = ai.predict(channel, 18)
    print('Prediction: ', ', '.join(prediction))


if __name__ == "__main__":
    main()
