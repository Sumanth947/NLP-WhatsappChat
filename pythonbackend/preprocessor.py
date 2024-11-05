import re
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def preprocessor(data):
    pattern = '\d{1,2}\/\d{1,2}\/\d{2},\s\d{1,2}:\d{2}\s[APap][Mm] -\s'

    messages = re.split(pattern, data)[1:]
    dat = re.findall(pattern, data)
    dates = [match.replace('\u202f', ' ') for match in dat]

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p - ')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('Group notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.strftime('%I')
    df['minute'] = df['date'].dt.minute
    df['am_pm'] = df['date'].dt.strftime('%p')

    period = []
    for time_components in df[['hour', 'minute', 'am_pm']].astype(str).agg(' '.join, axis=1):
        hour, minute, am_pm = time_components.split()
        if hour == '12':
            period.append(hour + "-" + '00')
        elif hour == '0':
            period.append('00' + "-" + str(int(hour) + 1))
        else:
            period.append(hour + "-" + str(int(hour) + 1))

    df['period'] = period
    return df
