import requests
import datetime as dt
from datetime import timedelta
from twilio.rest import Client
import os

# establish initial constants
# STOCK requires stock symbol
STOCK = "GOOGL"
COMPANY_NAME = "Google"

ALPHA_API = os.environ.get('VAR_ALPHA_API')
FUNCT = 'TIME_SERIES_INTRADAY'
INTERVAL = '30min'

NEWS_API = os.environ.get('VAR_NEWS_API')
NEWS_PARAM = {
    'category': 'business',
    'q': "Google",
    'language': "en",
    'apiKey': NEWS_API,
}

MARKET_CLOSE = ' 16:00:00'
MARKET_OPEN = ' 09:00:00'

PARAMETERS = {
    'function': FUNCT,
    'symbol': STOCK,
    'interval': INTERVAL,
    'apikey': ALPHA_API
}

TWI_AUTH = os.environ.get('VAR_TWI_AUTH')
TWI_ACC_SID = os.environ.get('VAR_TWI_SID')
NUM = os.environ.get('VAR_FROM_NUM')
TO_NUM = os.environ.get('VAR_TO_NUM')

# establish date variables and time functionality

time = dt.datetime

today = time.today()
today_str = str(time.today())[:10]
today_open = today_str + MARKET_OPEN

yesterday = today - timedelta(days=3)
yesterday_str = str(yesterday)[:10]
yesterday_close = yesterday_str + MARKET_CLOSE

day_before_yesterday = today - timedelta(days=4)
day_before_yesterday_str = str(day_before_yesterday)[:10]
day_before_yesterday_close = day_before_yesterday_str + MARKET_CLOSE

# API stock request and data formation

request = requests.get(url='https://www.alphavantage.co/query', params=PARAMETERS)
request.raise_for_status()

stock_data = request.json()
print(stock_data)

# price at close yesterday, today's open

# WILL NEED A TRY SOMEWHERE IN HERE

stock_yesterday_close = float(stock_data['Time Series (30min)'][yesterday_close]['4. close'])
print(stock_yesterday_close)
stock_before_yesterday_close = float(stock_data['Time Series (30min)'][day_before_yesterday_close]['1. open'])
print(stock_before_yesterday_close)

# initialize API news request, etc

request_news = requests.get(url='https://newsapi.org/v2/top-headlines', params=NEWS_PARAM)
request_news.raise_for_status()

news_data = request_news.json()

# calculate percent difference and alert user with most recent headlines
# if change is greater than 5%, pos or neg

percent_change = ((stock_before_yesterday_close - stock_yesterday_close) / stock_yesterday_close) * 100
percent_change_str = str(percent_change)
print(percent_change_str)

# method to compile headlines into one list

def fetch_headlines():
    headlines = []
    for x in range(3):
        title = news_data['articles'][x]['title']
        description = news_data['articles'][x]['description']
        entry = {'title': title, 'description': description}
        headlines.append(entry)
    return headlines


headlines = fetch_headlines()

def send_text(msg, frm_num, to_num):
    client = Client(TWI_ACC_SID, TWI_AUTH)
    to_send = client.messages.create(
        body=msg,
        from_= frm_num,
        to=to_num,
    )
    print(to_send.status)

def forecast(var, list, stock, percentage):
    if var == 'up':
        for entry in list:
            title = entry['title']
            description = entry['description']
            message = f'{stock} 🔺 {percentage}%\n' \
                      f'Headline: {title}\n' \
                      f'Brief: {description}'
            send_text(msg=message, frm_num=NUM, to_num=TO_NUM)
    elif var == 'down':
        for entry in list:
            title = entry['title']
            description = entry['description']
            message = f'{stock} 🔻 {percentage}%\n' \
                      f'Headline: {title}\n' \
                      f'Brief: {description}'
            send_text(msg=message, frm_num=NUM, to_num=TO_NUM)

if percent_change > 5:
    forecast(var='up', list=headlines, stock=STOCK, percentage=percent_change_str)
elif percent_change < -5:
    forecast(var='down', list=headlines, stock=STOCK, percentage=percent_change_str)




