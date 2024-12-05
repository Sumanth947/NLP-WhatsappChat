from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from random import randint
from nltk.corpus import movie_reviews
import requests
from bs4 import BeautifulSoup
import nltk
from transformers import AutoModelForCausalLM, AutoTokenizer
import re

# Download necessary NLTK data
nltk.download('movie_reviews')
nltk.download('vader_lexicon')

# Initialize tools
extract = URLExtract()
sentiments = SentimentIntensityAnalyzer()

# Train a Naive Bayes Model on NLTK movie reviews dataset
def train_naive_bayes():
    documents = [(movie_reviews.raw(fileid), category)
                 for category in movie_reviews.categories()
                 for fileid in movie_reviews.fileids(category)]
    texts, labels = zip(*documents)
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)
    model = make_pipeline(CountVectorizer(), MultinomialNB())
    model.fit(X_train, y_train)
    return model

# Initialize Naive Bayes model
nb_model = train_naive_bayes()

# Fetch chat statistics
def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    words = df['message'].str.split().str.len().sum()
    num_media_messages = df[df['message'] == '<Media omitted>'].shape[0]

    return num_messages, words, num_media_messages

# Fetch most active users
def most_active_user(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(columns={'index': 'name', 'user': 'percent'})
    return x, df

# Create word cloud
def create_wordcloud(selected_user, df):
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read()
    with open('stopwords-hindi.txt', 'r', encoding='utf-8') as f1:
        stop_words_hindi = f1.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Convert all messages to strings and handle NaN values
    temp = df.copy()
    temp['message'] = temp['message'].apply(lambda x: str(x) if pd.notnull(x) else "")
    
    # Remove stop words
    temp['message'] = temp['message'].apply(remove_stop_words)
    
    # Create word cloud
    if temp['message'].str.strip().str.len().sum() > 0:
        wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
        df_wc = wc.generate(temp['message'].str.cat(sep=" "))
        return df_wc
    else:
        return None

# Generate random colors for word cloud
def random_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    r, g, b = randint(0, 255), randint(0, 255), randint(0, 255)
    return f"rgb({r}, {g}, {b})"

# Emoji analysis
def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Convert messages to strings and handle NaN values
    messages = df['message'].apply(lambda x: str(x) if pd.notnull(x) else "")
    
    emojis = []
    for message in messages:
        try:
            emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])
        except Exception as e:
            print(f"Error processing message for emojis: {e}")
            continue
    
    emoji_df = pd.DataFrame(Counter(emojis).most_common(), columns=['Emoji', 'Count'])
    
    return emoji_df if not emoji_df.empty else pd.DataFrame(columns=['Emoji', 'Count'])

# Monthly timeline
def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline.apply(lambda x: f"{x['month']}-{x['year']}", axis=1)
    return timeline

# Daily timeline
def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline

# Weekly activity map
def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()

# Monthly activity map
def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month']

# Heatmap activity
def heatmap_activity(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return user_heatmap

# Sentiment analysis
def sentiment_analysis(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Convert messages to strings and handle NaN values
    df['message'] = df['message'].apply(lambda x: str(x) if pd.notnull(x) else "")
    
    try:
        # Calculate sentiment scores
        vader_scores = df['message'].apply(lambda x: sentiments.polarity_scores(x)['compound'])
        
        # Calculate average sentiment
        average_sentiment = vader_scores.mean()
        
        # Categorize sentiments
        sentiment_counts = pd.cut(vader_scores, 
                                bins=[-1, -0.1, 0.1, 1], 
                                labels=['Negative', 'Neutral', 'Positive']).value_counts()
        
        return {
            'average_sentiment': average_sentiment,
            'sentiment_distribution': sentiment_counts,
            'detailed_scores': vader_scores
        }
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return None

# URL sentiment analysis
def url_sentiment_analysis(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    urls = [url for message in df['message'] for url in extract.find_urls(message)]
    return {url: scrape_url_sentiment(url) for url in urls}

# Scrape URL content and perform sentiment analysis
def scrape_url_sentiment(url):
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
    except Exception:
        return "Error", "Error fetching URL", "Error"

def create_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    if df.empty:
        return pd.DataFrame()  # Return empty DataFrame if no data
    
    try:
        # Create period column
        df['period'] = df['day_name'] + '-' + df['hour'].astype(str)
        
        # Create pivot table with default value
        user_heatmap = df.pivot_table(
            index='day_name', 
            columns='hour',
            values='message',
            aggfunc='count',
            fill_value=0
        )
        
        # Ensure we have some data
        if user_heatmap.empty or user_heatmap.isna().all().all():
            return pd.DataFrame()
            
        return user_heatmap
        
    except Exception as e:
        print(f"Error creating heatmap: {e}")
        return pd.DataFrame()

def remove_stop_words(message):
    if pd.isna(message) or not isinstance(message, str):
        return ""
    
    try:
        return " ".join([word for word in str(message).lower().split() 
                        if word not in stop_words and word not in stop_words_hindi])
    except Exception as e:
        print(f"Error processing message: {e}")
        return ""

def initialize_model():
    try:
        # Suppress torch warnings
        import warnings
        warnings.filterwarnings("ignore", category=UserWarning)
        
        # Initialize your model here
        model = AutoModelForCausalLM.from_pretrained("your_model_name")
        tokenizer = AutoTokenizer.from_pretrained("your_model_name")
        
        return model, tokenizer
    except Exception as e:
        print(f"Error initializing model: {e}")
        return None, None

def process_chatbot_response(question, model, tokenizer):
    try:
        if model is None or tokenizer is None:
            return "Sorry, the chatbot is not available at the moment."
            
        # Your existing chatbot logic here
        inputs = tokenizer(question, return_tensors="pt")
        outputs = model.generate(**inputs)
        response = tokenizer.decode(outputs[0])
        
        return response
    except Exception as e:
        print(f"Error processing chatbot response: {e}")
        return "Sorry, I couldn't process your question. Please try again."

def activity_heatmap(selected_user, df):
    """
    Generate a heatmap of user activity by day of the week and hour of the day.
    """
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    # Create a pivot table for heatmap
    heatmap_data = df.pivot_table(index='day_name', columns='hour', values='message', aggfunc='count').fillna(0)
    
    # Reorder the days of the week
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data.reindex(days_order)
    
    return heatmap_data

def most_busy_users(df):
    """
    Find the most active users in the chat.
    Returns:
    - x: Series with user message counts
    - new_df: DataFrame with user stats
    """
    # Remove group notifications
    df = df[df['user'] != 'system_notification']
    
    # Count messages by user
    x = df['user'].value_counts()
    
    # Calculate percentage
    df_stats = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()
    df_stats.columns = ['name', 'percent']
    
    return x, df_stats

def create_wordcloud(selected_user, df):
    """
    Create a word cloud from messages.
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Remove group notifications, media messages, and links
    temp = df[df['user'] != 'system_notification']
    temp = temp[temp['message'] != '<Media omitted>']

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df):
    """
    Find most common words in messages.
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'system_notification']
    temp = temp[temp['message'] != '<Media omitted>']

    words = []
    for message in temp['message']:
        words.extend(message.lower().split())

    # Get most common words
    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user, df):
    """
    Analyze emoji usage in messages.
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        if isinstance(message, str):
            emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df

def count_links(df):
    """
    Count the number of links shared in the chat.
    """
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    
    # Ensure the 'message' column is treated as string and handle NaN values
    links_count = df['message'].astype(str).str.count(url_pattern).sum()
    return links_count

def extract_urls(df):
    """
    Extract all URLs from the chat messages.
    Returns a list of unique URLs.
    """
    url_pattern = r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)'
    urls = df['message'].str.extractall(url_pattern)[0].unique()  # Extract all URLs and get unique ones
    return urls.tolist()  # Return as a list
