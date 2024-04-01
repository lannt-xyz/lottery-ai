import os
from LotteryAi import LotteryAi

def main():
    # get system environment variables
    var_value = os.getenv('CHANELS')
    # check if environment variable is set
    if var_value is None:
        print('Environment variable CHANELS is not set.')
        return
    # split string to list by comma
    channels = var_value.split(',')
    # train model for each channel
    for channel in channels:
        ai = LotteryAi()
        ai.train(channel)
    

if __name__ == "__main__":
    main()
