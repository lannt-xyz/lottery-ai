import datetime
from Utils.LotteryAi import LotteryAi
from collections import Counter

import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    ai = LotteryAi()
    channel = 'tra-vinh'
    prediction = ai.predict(channel, 16)
    print('Prediction: ', ', '.join(prediction))


if __name__ == "__main__":
    main()
