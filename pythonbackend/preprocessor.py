import re
import pandas as pd

def preprocess(data):
    """
    Preprocess the WhatsApp chat data.
    """
    try:
        # Pattern for date and time
        pattern = r'\d{1,2}/\d{1,2}/\d{4},\s\d{1,2}:\d{2}\s[ap]m\s-\s'
        
        messages = re.split(pattern, data)[1:]
        dates = re.findall(pattern, data)
        
        df = pd.DataFrame({'user_message': messages, 'message_date': dates})
        
        # Convert message_date type
        df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %I:%M %p - ', errors='coerce')
        
        users = []
        messages = []
        
        for message in df['user_message']:
            entry = re.split('((?:\+\d{1,3}\s\d{5}\s\d{5}|[^:]+)):\s', message)
            if len(entry) > 1:  # Regular message
                users.append(entry[1].strip())
                messages.append(entry[2].strip())
            else:  # System message or no colon
                users.append('system_notification')
                messages.append(entry[0].strip())
            
        df['user'] = users
        df['message'] = messages
        df.drop('user_message', axis=1, inplace=True)
        
        # Extract time features
        df['year'] = df['message_date'].dt.year
        df['month_num'] = df['message_date'].dt.month
        df['month'] = df['message_date'].dt.strftime('%B')
        df['day'] = df['message_date'].dt.day
        df['day_name'] = df['message_date'].dt.day_name()
        df['hour'] = df['message_date'].dt.hour
        df['minute'] = df['message_date'].dt.minute
        df['only_date'] = df['message_date'].dt.date
        
        # Clean up user names (remove phone numbers for privacy)
        df['user'] = df['user'].apply(lambda x: x.split('(')[0].strip() if '(' in x else x)
        df['user'] = df['user'].apply(lambda x: 'Anonymous' if x.startswith('+91') else x)
        
        # Debug print
        print(f"Processed {len(df)} messages")
        print(f"Columns: {df.columns.tolist()}")
        
        return df
        
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error
