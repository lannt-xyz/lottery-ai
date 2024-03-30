from flask import Flask, render_template, request
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from DataAccess import DataAccess

load_dotenv()

app = Flask(__name__)

lotMap = json.loads(os.getenv('LOT_MAP'))

# print(lotMap)


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
        # print(result)
        predictions.append({
            'cityCode': cityCode,
            'result': ', '.join(result['prediction'])
        })

    return render_template('home.html', today=targetDate.strftime('%Y-%m-%d'), dayOfWeekName=dayOfWeekName, predictions=predictions)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    dataAccess = DataAccess()
    data=dataAccess.getDashboardData().to_dict(orient='records')
    # print(data)
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)