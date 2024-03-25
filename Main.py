from LotteryAi import LotteryAi
from DataAccess import DataAccess

def main():
    ai = LotteryAi()
    # ai.train('vietlot-655')
    prediction = ai.predict('binh-duong', 1)
    print(', '.join(prediction))

    # dataAccess = DataAccess()
    # res = dataAccess.getDashboardData()
    # # res = dataAccess.getPredictions('2024-03-20', 'soc-trang')
    # print(res)

if __name__ == "__main__":
    main()
