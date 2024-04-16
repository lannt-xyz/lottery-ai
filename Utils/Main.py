from LotteryAi import LotteryAi
from collections import Counter

def main():
    model_name = 'vung-tau'
    ai = LotteryAi()
    res = ai.predict(model_name, 1)
    print(res)

if __name__ == "__main__":
    main()
