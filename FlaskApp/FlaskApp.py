import json
import os
from dotenv import load_dotenv
from datetime import timedelta

from flask import Flask, render_template, request, jsonify
from datetime import datetime

from DB.DataAccess import DataAccess

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

lotMap = json.loads(os.getenv('LOT_MAP'))

# declare final variable as the amount of money to buy a ticket
coverPayment = int(os.getenv('COVER_PAYMENT'))
#coverPayment = 160000
firstSpecPayment = 10000

# declare wining amount for each prize
winingAmount = int(os.getenv('COVER_WINNING_AMOUNT'))
#winingAmount = 750000

# declare the function of count matched number for the Cover
def countCoverMatched(i, p, a):
    # if a is an array with one empty element, return 0
    if len(a) == 1 and a[0] == '':
        return 0

    # convert array a in String to array of number
    actuals = [int(x) for x in a]
    prediction = int(p)

    return actuals.count(prediction)

coverMatchedFunction = countCoverMatched

# declare the function of count matched number for the First-Spec
def countFirstSpecMatched(i, p, a):
    # if a is an array with one empty element, return 0
    if len(a) == 1 and a[0] == '':
        return 0

    # convert array a in String to array of number
    actuals = [int(x) for x in a]
    prediction = int(p)

    if prediction == actuals[i]:
        return 1

    return 0


# declare the function of count matched number for the First-Spec
def countFirstMatched(i, p, a):
    # if a is an array with one empty element, return 0
    if len(a) == 1 and a[0] == '':
        return 0

    # convert array a in String to array of number
    actuals = [int(x) for x in a]
    prediction = int(p)

    if prediction == actuals[16]:
        return 1

    return 0

# declare the function of count matched number for the First-Spec
def countFirstMatched(i, p, a):
    # if a is an array with one empty element, return 0
    if len(a) == 1 and a[0] == '':
        return 0

    # convert array a in String to array of number
    actuals = [int(x) for x in a]
    prediction = int(p)

    if prediction == actuals[17]:
        return 1

    return 0

firstSpecMatchedFunction = countFirstSpecMatched
firstMatchedFunction = countFirstSpecMatched
specialMatchedFunction = countFirstSpecMatched

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/results', methods=['GET'])
def results():
    return render_template('results.html')

@app.route('/results-data', methods=['GET'])
def resultsData():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    includeFirstSpec = request.args.get('includeFirstSpec')
    includeFirstSpec = True if includeFirstSpec.lower() == 'true' else False

    return jsonify(resultsData(startDate, endDate, includeFirstSpec))

def resultsData(startDate, endDate, includeFirstSpec):
    dataAccess = DataAccess()
    data = dataAccess.getResults(startDate, endDate, includeFirstSpec).to_dict(orient='records')

    for item in data:
        prediction_numbers = item.get('prediction', '').split('_')
        actual_numbers = item.get('actual', '').split('_')
        countMatched = coverMatchedFunction
        if 'fstSpec' in item.get('cityCode'):
            countMatched = firstSpecMatchedFunction
        if 'first' in item.get('cityCode'):
            countMatched = firstMatchedFunction
        if 'special' in item.get('cityCode'):
            countMatched = specialMatchedFunction
        matched = ''
        index = 0
        for number in prediction_numbers:
            predictionNumber = int(number.split('(')[0])
            prediction = "{:02}".format(predictionNumber)
            matched_count = countMatched(index, predictionNumber, actual_numbers)
            if matched_count > 0:
                matched += ' ' + prediction + '(' + str(matched_count) + ')'
            index += 1

        item['matched'] = matched
        item['prediction'] = item.get('prediction', '').replace('_', ', ')
        item['actual'] = item.get('actual', '').replace('_', ', ')

    resultsData = {
        'data': data
    }

    return resultsData

def processBarDashboardData(data, countMatched):
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
        index = 0
        for prediction in predictions:
            # count p in actual
            count += countMatched(index, prediction, actuals)
            index += 1

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
            index += 1

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
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    dataAccess = DataAccess()
    data=dataAccess.getCoverResults(startDate, endDate).to_dict(orient='records')

    return processBarDashboardData(data, coverMatchedFunction)

@app.route('/dashboard-cover-absent', methods=['GET'])
def dashboardCoverAbsent():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    dataAccess = DataAccess()
    data=dataAccess.getCoverResults(startDate, endDate).to_dict(orient='records')
    # filter data to get the rows that cityCode contain 'absent_' and remove the prefix 'absent_'
    data = [x for x in data if 'absent_' in x['cityCode']]
    for x in data:
        x['cityCode'] = x['cityCode'].replace('absent_', '')

    return processBarDashboardData(data, coverMatchedFunction)

@app.route('/dashboard-cover-cycle', methods=['GET'])
def dashboardCoverCycle():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    dataAccess = DataAccess()
    data=dataAccess.getCoverResults(startDate, endDate).to_dict(orient='records')
    # filter data to get the rows that cityCode contain 'absent_' and remove the prefix 'absent_'
    data = [x for x in data if 'cycle_' in x['cityCode']]
    for x in data:
        x['cityCode'] = x['cityCode'].replace('cycle_', '')

    return processBarDashboardData(data, coverMatchedFunction)

@app.route('/dashboard-cover-combine', methods=['GET'])
def dashboardCoverCombine():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    dataAccess = DataAccess()
    data=dataAccess.getCoverResults(startDate, endDate).to_dict(orient='records')
    # filter data to get the rows that cityCode contain 'absent_' and remove the prefix 'absent_'
    data = [x for x in data if 'combine_' in x['cityCode']]
    for x in data:
        x['cityCode'] = x['cityCode'].replace('combine_', '')

    return processBarDashboardData(data, coverMatchedFunction)

@app.route('/dashboard-fst-spec', methods=['GET'])
def dashboardFstSpec():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    dataAccess = DataAccess()
    data=dataAccess.getFstSpecResults(startDate, endDate).to_dict(orient='records')

    return processBarDashboardData(data, firstSpecMatchedFunction)

@app.route('/dashboard-spec', methods=['GET'])
def dashboardSpec():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    dataAccess = DataAccess()
    data=dataAccess.getSpecResults(startDate, endDate).to_dict(orient='records')

    return processBarDashboardData(data, specMatchedFunction)

@app.route('/dashboard-fst', methods=['GET'])
def dashboardFst():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    dataAccess = DataAccess()
    data=dataAccess.getFstResults(startDate, endDate).to_dict(orient='records')

    return processBarDashboardData(data, firstMatchedFunction)

@app.route('/dashboard-cover-profit', methods=['GET'])
def dashboardCoverProfit():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    dataAccess = DataAccess()
    data = dataAccess.getCoverResults(startDate, endDate).to_dict(orient='records')

    return processPieChartData(data, coverPayment, coverMatchedFunction)

@app.route('/dashboard-cover-profit-absent', methods=['GET'])
def dashboardCoverProfitAbsent():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    dataAccess = DataAccess()
    data = dataAccess.getCoverResults(startDate, endDate).to_dict(orient='records')
    # filter data to get the rows that cityCode contain 'absent_' and remove the prefix 'absent_'
    data = [x for x in data if 'absent_' in x['cityCode']]
    for x in data:
        x['cityCode'] = x['cityCode'].replace('absent_', '')

    return processPieChartData(data, coverPayment, coverMatchedFunction)

@app.route('/dashboard-cover-profit-cycle', methods=['GET'])
def dashboardCoverProfitCycle():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    dataAccess = DataAccess()
    data = dataAccess.getCoverResults(startDate, endDate).to_dict(orient='records')
    # filter data to get the rows that cityCode contain 'absent_' and remove the prefix 'absent_'
    data = [x for x in data if 'cycle_' in x['cityCode']]
    for x in data:
        x['cityCode'] = x['cityCode'].replace('cycle_', '')

    return processPieChartData(data, coverPayment, coverMatchedFunction)

@app.route('/dashboard-cover-profit-combine', methods=['GET'])
def dashboardCoverProfitCombine():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    dataAccess = DataAccess()
    data = dataAccess.getCoverResults(startDate, endDate).to_dict(orient='records')
    # filter data to get the rows that cityCode contain 'absent_' and remove the prefix 'absent_'
    data = [x for x in data if 'combine_' in x['cityCode']]
    for x in data:
        x['cityCode'] = x['cityCode'].replace('combine_', '')

    return processPieChartData(data, coverPayment, coverMatchedFunction)

@app.route('/dashboard-fst-spec-profit', methods=['GET'])
def dashboardFstSpecProfit():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    dataAccess = DataAccess()
    data = dataAccess.getFstSpecResults(startDate, endDate).to_dict(orient='records')

    return processPieChartData(data, firstSpecPayment, firstSpecMatchedFunction)

@app.route('/dashboard-fst-profit', methods=['GET'])
def dashboardFstProfit():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    dataAccess = DataAccess()
    data = dataAccess.getFstResults(startDate, endDate).to_dict(orient='records')

    return processPieChartData(data, firstSpecPayment, firstMatchedFunction)

@app.route('/dashboard-spec-profit', methods=['GET'])
def dashboardSpecProfit():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    dataAccess = DataAccess()
    data = dataAccess.getSpecResults(startDate, endDate).to_dict(orient='records')

    return processPieChartData(data, firstSpecPayment, specialMatchedFunction)

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

@app.route('/matched-results', methods=['GET'])
def matched_results():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    return jsonify(find_matched(startDate, endDate))

def find_matched(startDate, endDate):

    # Call resultsData() to get the original data
    original_data = resultsData(startDate, endDate, False)

    # Convert startDate and endDate to datetime objects
    startInDate = datetime.strptime(startDate, '%Y-%m-%d')
    endInDate = datetime.strptime(endDate, '%Y-%m-%d')

    # Generate a list of all dates between startDate and endDate
    date_generated = [startInDate + timedelta(days=x) for x in range(0, (endInDate - startInDate).days + 1)]

    # Initialize a dictionary to hold counts for each date
    date_counts = {date.strftime("%Y-%m-%d"): 0 for date in date_generated}

    # Initialize a dictionary to hold the processed results
    processed_data = {
        "data": []
    }
    
    # Temporary storage to count items for each date and type
    counts = {}
    
    # Process each item in the original data
    for item in original_data['data']:
        date = item['date']
        cityCode = item['cityCode']
        matched = item['matched']

        # Initialize matched_num to 0 for each item
        matched_num = 0
        
        # Split the matched string by space and process each part
        for part in matched.split():
            # Check if part contains a number wrapped in parentheses
            if '(' in part and ')' in part:
                # Extract the number inside the parentheses
                num_str = part[part.find('(')+1:part.find(')')]
                try:
                    # Convert to integer and add to matched_num
                    matched_num += int(num_str)
                except ValueError:
                    # In case the extraction or conversion fails, ignore this part
                    pass
        
        # Determine the type based on the prefix of cityCode
        if cityCode.startswith('cycle_'):
            item_type = 'cycle'
        elif cityCode.startswith('absent_'):
            item_type = 'absent'
        elif cityCode.startswith('combine_'):
            item_type = 'combine'
        else:
            item_type = 'common'
        
        # Key to uniquely identify each date and type combination
        key = (date, item_type)
        
        # Increment count if matched is not empty
        if matched:
            counts[key] = counts.get(key, 0) + matched_num

    # After processing all items, ensure all dates and types are included
    for date in date_generated:
        for item_type in ['cycle', 'absent', 'combine', 'common']:  # Include all expected types
            key = (date.strftime("%Y-%m-%d"), item_type)
            # If a date and type combination was not encountered, set its count to 0
            if key not in counts:
                counts[key] = 0

    # Convert the counts dictionary to the desired output format
    for (date, item_type), count in counts.items():
        processed_data['data'].append({
            "date": date,
            "type": item_type,
            "count": count
        })

    # Sort the processed data by date
    processed_data['data'] = sorted(processed_data['data'], key=lambda x: x['date'])

    # Return the processed data
    return processed_data

@app.route('/daily-profit', methods=['GET'])
def daily_profit():
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    matched_data = find_matched(startDate, endDate)
    # loop through the matched_data, with each date, get the count
    data = matched_data['data']
    # get data from environment variable named LOT_MAP
    lotMap = json.loads(os.getenv('LOT_MAP'))
    
    # group the data by date, type and count the number of items
    daily_data = []
    for item in data:
        date_str = item['date']
        item_type = item['type']
        matched_count = item['count']
        # convert to date object from string
        date = datetime.strptime(date_str, '%Y-%m-%d')
        # get the day of week index from the date, then convert to string
        dayOfWeek = str(date.weekday())
        # get the number of cityCodes based on the key
        cityCodes = lotMap[dayOfWeek]
        # get the size of the cityCodes
        bought = len(cityCodes)

        daily_data.append({
            'date': date_str,
            'type': item_type,
            'profit': bought * coverPayment - matched_count * winingAmount
        })
    
    return jsonify(daily_data)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/dashboard-weekly', methods=['GET'])
def dashboard_weekly():
    return render_template('dashboard-weekly.html')


@app.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)