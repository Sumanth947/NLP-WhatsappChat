import re
import pandas as pd

def preprocess_chat(chat_lines):
    data = []
    # Pattern to match messages with date, time, sender, and message
    pattern = r'(\d{1,2}/\d{1,2}/\d{4}), (\d{1,2}:\d{2} (?:AM|PM|am|pm)) - (.*?): (.*)'
    # Pattern for system messages without a sender
    no_sender_pattern = r'(\d{1,2}/\d{1,2}/\d{4}), (\d{1,2}:\d{2} (?:AM|PM|am|pm)) - (.*)'

    for i, line in enumerate(chat_lines):
        try:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                date, time, sender, message = match.groups()
                data.append([date, time, sender, message])
            else:
                match_no_sender = re.match(no_sender_pattern, line, re.IGNORECASE)
                if match_no_sender:
                    date, time, message = match_no_sender.groups()
                    data.append([date, time, "System Notification", message])
                else:
                    # Append multiline message to the last entry
                    if data:
                        data[-1][-1] += " " + line.strip()
        except Exception as e:
            print(f"Skipping line {i} due to parsing error: {line.strip()}")
            continue

    # Create a DataFrame with the appropriate columns
    chat_df = pd.DataFrame(data, columns=['Date', 'Time', 'user', 'message'])

    # Combine Date and Time into a single DateTime column
    chat_df['DateTime'] = pd.to_datetime(chat_df['Date'] + ' ' + chat_df['Time'], errors='coerce')
    chat_df.drop(['Date', 'Time'], axis=1, inplace=True)

    # Extract additional date information for analysis
    chat_df['only_date'] = chat_df['DateTime'].dt.date
    chat_df['year'] = chat_df['DateTime'].dt.year
    chat_df['month'] = chat_df['DateTime'].dt.strftime('%B')
    chat_df['month_num'] = chat_df['DateTime'].dt.month
    chat_df['day_name'] = chat_df['DateTime'].dt.day_name()

    # Define periods based on the time of day
    def get_period(hour):
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    chat_df['period'] = chat_df['DateTime'].dt.hour.apply(get_period)

    return chat_df
