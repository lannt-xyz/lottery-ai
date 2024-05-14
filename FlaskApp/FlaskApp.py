import json
import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify
from datetime import datetime

from DB.DataAccess import DataAccess

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

lotMap = json.loads(os.getenv('LOT_MAP'))

# declare final variable as the amount of money to buy a ticket
coverPayment = 160000
firstSpecPayment = 20000

# declare wining amount for each prize
winingAmount = 750000

@app.route('/with-date', methods=['POST'])
def handle_date():
    date_str = request.form.get('date')
    return get_prediction(date_str)

@app.route('/')
def home():
    # get the current date's day of week
    today = datetime.now().strftime('%Y-%m-%d')
    return get_prediction(today)

def get_prediction(targetDateStr):

    targetDate = datetime.strptime(targetDateStr, '%Y-%m-%d')
    # get the day of week of the target date
    dayOfWeek = targetDate.weekday()
    # get the city codes of the current day
    cityCodes = lotMap[str(dayOfWeek)]

    # get the dayOfWeek name
    dayOfWeekName = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][dayOfWeek]

    
    predictions = []
    dataAccess = DataAccess()
    for cityCode in cityCodes:
        result = dataAccess.getPredictions(targetDateStr, cityCode)
        # do not contain any prediction then continue
        if len(result) == 0:
            continue

        predictions.append({
            'cityCode': cityCode,
            'result': ', '.join(result['prediction'])
        })

    return render_template('home.html', today=targetDate.strftime('%Y-%m-%d'), dayOfWeekName=dayOfWeekName, predictions=predictions)

@app.route('/results', methods=['GET'])
def results():
    dataAccess = DataAccess()
    data = dataAccess.getResults().to_dict(orient='records')

    for item in data:
        prediction_numbers = item.get('prediction', '').split('_')
        actual_numbers = item.get('actual', '').split('_')
        matched = ''
        for number in prediction_numbers:
            predictionNumber = number.split('(')[0]
            prediction = "{:02}".format(int(predictionNumber))
            matched_count = len(actual_numbers) - len([x for x in actual_numbers if x != prediction])
            if matched_count > 0:
                matched += ' ' + prediction + '(' + str(matched_count) + ')'
        item['matched'] = matched
        item['prediction'] = item.get('prediction', '').replace('_', ', ')
        item['actual'] = item.get('actual', '').replace('_', ', ')

    return render_template('results.html', data=data)

def processBarDashboardData(data):
    dashboardData = {}
    # get data from environment variable named LOT_MAP
    lotMap = json.loads(os.getenv('LOT_MAP'))

    # generate 7 colors for the chart coressponding with the data on the lotMap
    colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#00FFFF', '#FF00FF', '#C0C0C0']

    # loop through the data, with each city_code, get the prediction and actual
    for row in data:
        cityCode = row['cityCode']
        # return soon if cityCode is vietlot-655
        if cityCode == 'vietlot-655':
            continue

        prediction = row['prediction']
        actual = row['actual']
        actuals = actual.split('_')

        predictions = prediction.split('_')
        # predictions's item is in format ##(%##), extract the number only
        predictions = [x.split('(')[0] for x in predictions]
        # format the number in 2 digits
        predictions = [x.zfill(2) for x in predictions]

        # find the key of lotMap that contain cityCode, the cityCode may has prefix fstSpec_ but value of map is not
        # so check it also by removing the prefix fstSpec_ from the cityCode then check it also
        lotMapKey = [key for key, value in lotMap.items() if cityCode in value or cityCode.replace('fstSpec_', '') in value]

        if len(lotMapKey) == 0:
            continue
        # get the color for the cityCode
        color = colors[int(lotMapKey[0])]

        # count the number of time the prediction appears in the actual
        count = 0
        for p in predictions:
            # count p in actual
            count += actuals.count(p)

        # if dashboarData contain key cityCode, add the count to the existing count, and set the color for the cityCode
        if cityCode in dashboardData:
            dashboardData[cityCode]['count'] += count
        else:
            dashboardData[cityCode] = {
                'count': count,
                'color': color,
                'order': lotMapKey[0]
            }

    # sort the dashboardData by order
    dashboardData = dict(sorted(dashboardData.items(), key=lambda item: item[1]['order']))
    # convert dashboardData to list with the key of dashboardData is included in the value
    dashboardData = [{'label': key, **value} for key, value in dashboardData.items()]
    # by using the order of data, I want to convert it to name of day of week
    dayOfWeekName = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
    # add the name of day of week to the label of data by String concatenation
    for i in range(len(dashboardData)):
        label = dayOfWeekName[int(dashboardData[i]['order'])] + ' - ' + dashboardData[i]['label']
        dashboardData[i]['label'] = label.replace('fstSpec_', '')

    return jsonify(dashboardData)

def processPieChartData(data, payment, countMatched):
    dashboardData = {}
    # get data from environment variable named LOT_MAP
    lotMap = json.loads(os.getenv('LOT_MAP'))

    # loop through the data, with each city_code, get the prediction and actual
    for row in data:
        cityCode = row['cityCode']
        # return soon if cityCode is vietlot-655
        if cityCode == 'vietlot-655':
            continue

        prediction = row['prediction']
        actual = row['actual']
        actuals = actual.split('_')

        predictions = prediction.split('_')
        # predictions's item is in format ##(%##), extract the number only
        predictions = [x.split('(')[0] for x in predictions]
        # format the number in 2 digits
        predictions = [x.zfill(2) for x in predictions]

        # find the key of lotMap that contain cityCode, the cityCode may has prefix fstSpec_ but value of map is not
        # so check it also by removing the prefix fstSpec_ from the cityCode then check it also
        lotMapKey = [key for key, value in lotMap.items() if cityCode in value or cityCode.replace('fstSpec_', '') in value]

        if len(lotMapKey) == 0:
            continue

        # sum of the winning amount based on the prediction and the actual
        pay = 0
        winning = 0
        index = 0
        for prediction in predictions:
            winning += countMatched(index, prediction, actuals) * winingAmount
            pay += payment

        # if dashboarData contain key cityCode, add the count to the existing count, and set the color for the cityCode
        if cityCode in dashboardData:
            dashboardData[cityCode]['winning'] += winning
            dashboardData[cityCode]['pay'] += pay
        else:
            dashboardData[cityCode] = {
                'winning': winning,
                'pay': pay
            }

    totalWining = 0
    totalPay = 0
    for key, value in dashboardData.items():
        totalWining += value['winning']
        totalPay += value['pay']

    data = [{
            'label': 'Total Pay',
            'value': totalPay,
            'color': '#FF0000'
        },
        {
            'label': 'Total Winning',
            'value': totalWining,
            'color': '#00FF00'
        }]

    return jsonify(data)

@app.route('/dashboard-cover', methods=['GET'])
def dashboardCover():
    dataAccess = DataAccess()
    data=dataAccess.getCoverResults().to_dict(orient='records')

    return processBarDashboardData(data)

@app.route('/dashboard-fst-spec', methods=['GET'])
def dashboardFstSpec():
    dataAccess = DataAccess()
    data=dataAccess.getFstSpecResults().to_dict(orient='records')

    return processBarDashboardData(data)

@app.route('/dashboard-cover-profit', methods=['GET'])
def dashboardCoverProfit():
    dataAccess = DataAccess()
    data = dataAccess.getCoverResults().to_dict(orient='records')

    return processPieChartData(data, coverPayment, lambda i, p, a: a.count(p))

@app.route('/dashboard-fst-spec-profit', methods=['GET'])
def dashboardFstSpecProfit():
    dataAccess = DataAccess()
    data = dataAccess.getFstSpecResults().to_dict(orient='records')

    return processPieChartData(data, firstSpecPayment, lambda i, p, a: a.count(p))

@app.route('/dashboard-accuracy', methods=['GET'])
def dashboardAccuracy():
    # get model directory path from environment variable
    modelDir = os.getenv('MODEL_DIR')
    filePrefix = '_val_accuracy.txt'
    # get all files in the model folder has patterns of '*_accuracy.txt'
    files = [f for f in os.listdir(modelDir) if f.endswith(filePrefix)]
    # by using the order of data, I want to convert it to name of day of week
    dayOfWeekName = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
    # get data from environment variable named LOT_MAP
    lotMap = json.loads(os.getenv('LOT_MAP'))

    # create a map of data to return with key is the name of the file and value is the content of the file
    data = []
    for file in files:
        with open(f'{modelDir}/{file}', 'r') as f:
            # the file name is the key of the map, with removing _accuracy.txt
            cityCode = file.replace(filePrefix, '')
            seachingCityCode = cityCode.replace('fstSpec_', '')
            # based on the value of lotMap, get the order of the key
            order = [key for key, value in lotMap.items() if seachingCityCode in value]
            if order == None or len(order) == 0:
                continue

            # get the dayOfWeek name by using the order
            dayOfWeek = dayOfWeekName[int(order[0])]
            # data is content of the file in float value need to multiply with 100 to get the percentage
            value = float(f.read()) * 100
            # rounding to get value in integer
            value = round(value, 0)
            data.append({
                'label': f'{dayOfWeek} - {cityCode}',
                'value': value
            })

    return jsonify(data)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)