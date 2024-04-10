from LotteryAi import LotteryAi
from collections import Counter

def main():
    model_name = 'vietlot-655'
    ai = LotteryAi()
    res = ai.predict(model_name, None, None)
    print(res)

if __name__ == "__main__":
    main()
