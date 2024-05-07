from datetime import datetime, timedelta
from Utils.LotteryAi import LotteryAi

def main():
    lot = LotteryAi()
    res = lot.predict("ca-mau")
    print('res: ', res) 

if __name__ == "__main__":
    main()
