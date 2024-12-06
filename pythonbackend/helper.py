from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import requests
from bs4 import BeautifulSoup
import re

# Download necessary NLTK data
nltk.download('vader_lexicon')

# Initialize tools
extract = URLExtract()
sentiments = SentimentIntensityAnalyzer()

# Preprocess the chat data
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
        
        return df
        
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Count links in messages
def count_links(df):
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    links_count = df['message'].astype(str).str.count(url_pattern).sum()
    return links_count

# Extract URLs from messages
def extract_urls(df):
    url_pattern = r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)'
    urls = df['message'].str.extractall(url_pattern)[0].unique()
    return urls.tolist()

# Generate activity heatmap
def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    df['hour'] = pd.to_datetime(df['message_date']).dt.hour
    df['day_name'] = pd.to_datetime(df['message_date']).dt.day_name()
    
    heatmap_data = df.pivot_table(index='day_name', columns='hour', values='message', aggfunc='count').fillna(0)
    return heatmap_data

# Sentiment analysis for URLs
def analyze_url(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else "No title"
        description = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        description_text = description.get('content', '') if description else "No description"
        paragraphs = soup.find_all('p')
        text = ' '.join(p.text for p in paragraphs)
        sentiment_score = sentiments.polarity_scores(text)['compound']
        sentiment = "Positive" if sentiment_score > 0.05 else "Negative" if sentiment_score < -0.05 else "Neutral"
        return sentiment, title, description_text
    except Exception as e:
        return "Error", "Error fetching URL", "Error"

# Fetch statistics for the selected user
def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    num_messages = df.shape[0]  # Total number of messages
    
    # Ensure 'message' column is treated as strings and handle NaN values
    df['message'] = df['message'].fillna('')  # Replace NaN with an empty string
    df['message'] = df['message'].astype(str)  # Convert to string
    
    words = df['message'].str.split().str.len().sum()  # Total number of words
    num_media_messages = df[df['message'] == '<Media omitted>'].shape[0]  # Count media messages
    return num_messages, words, num_media_messages

# Monthly timeline function
def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    timeline = df.groupby(['year', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + ' ' + timeline['year'].astype(str)
    return timeline[['time', 'message']]

# Daily timeline function
def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline

# Week activity map function
def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Create a new column for the day of the week
    df['day_name'] = df['message_date'].dt.day_name()
    
    # Count the number of messages for each day of the week
    week_activity = df.groupby('day_name').count()['message'].reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    
    return week_activity

# Month activity map function
def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Count the number of messages for each month
    month_activity = df.groupby('month').count()['message'].reset_index()
    return month_activity

# Most busy users function
def most_busy_users(df):
    user_counts = df['user'].value_counts()  # Count messages per user
    most_busy = user_counts[user_counts > 0]  # Filter out users with no messages
    return most_busy, most_busy.reset_index(name='message_count').rename(columns={'index': 'user'})

# Create word cloud function
def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Combine all messages into a single string
    all_messages = ' '.join(df['message'].astype(str))
    
    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_messages)
    
    return wordcloud

# Most common words function
def most_common_words(selected_user, df, top_n=10):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Combine all messages into a single string
    all_messages = ' '.join(df['message'].astype(str))
    
    # Remove punctuation and split into words
    words = re.findall(r'\w+', all_messages.lower())
    
    # Count the frequency of each word
    most_common = Counter(words).most_common(top_n)
    
    # Split the result into two lists: words and their counts
    words, counts = zip(*most_common) if most_common else ([], [])
    
    return words, counts

# Emoji helper function
def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Extract emojis from messages
    all_emojis = ''.join(df['message'].astype(str).apply(lambda x: ''.join(c for c in x if c in emoji.EMOJI_DATA)))
    
    # Count the frequency of each emoji
    emoji_counts = Counter(all_emojis)
    
    # Create a DataFrame for the emoji counts
    emoji_df = pd.DataFrame(emoji_counts.items(), columns=['Emoji', 'Count'])
    emoji_df = emoji_df.sort_values(by='Count', ascending=False).reset_index(drop=True)
    
    return emoji_df
