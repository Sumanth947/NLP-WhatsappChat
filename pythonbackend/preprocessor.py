import re
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def preprocessor(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s[APap][Mm] - '

    messages = re.split(pattern, data)[1:]
    dat = re.findall(pattern, data)
    dates = [match.replace('\u202f', ' ') for match in dat]

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p - ')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('Group notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Check if 'Group notification' is in the user list and remove if present
    if 'Group notification' in df['user'].values:
        df = df[df['user'] != 'Group notification']

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
        try:
            hour, minute, am_pm = time_components.split()
            hour_int = int(hour)

            # Adjust the hour for the period range, handle 12-hour format
            if hour_int == 12:
                next_hour = '01' if am_pm.lower() == 'am' else '00'  # Handle noon and midnight cases
            else:
                next_hour = str((hour_int % 12) + 1).zfill(2)

            period.append(f"{hour.zfill(2)}-{next_hour} {am_pm}")
        except ValueError:
            # Append a default or error value if unpacking fails
            period.append("Unknown")

    df['period'] = period
    return df
