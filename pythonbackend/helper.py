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
    words = sum(df['message'].apply(lambda x: len(x.split())))
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    num_links = sum(df['message'].apply(lambda x: len(extract.find_urls(x))))
    return num_messages, words, num_media_messages, num_links

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

    temp = df[df['user'] != 'Group notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        return " ".join([word for word in message.lower().split() if word not in stop_words and word not in stop_words_hindi])

    wc = WordCloud(width=500, height=500, max_words=80, min_font_size=10, background_color='white', color_func=random_color_func)
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

# Generate random colors for word cloud
def random_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    r, g, b = randint(0, 255), randint(0, 255), randint(0, 255)
    return f"rgb({r}, {g}, {b})"

# Emoji analysis
def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    emojis = [c for message in df['message'] for c in message if c in emoji.UNICODE_EMOJI['en']]
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df

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
    vader_scores = df['message'].apply(lambda x: sentiments.polarity_scores(x)['compound'])
    nb_predictions = df['message'].apply(lambda x: nb_model.predict([x])[0])
    nb_score = nb_predictions.value_counts().get('pos', 0) - nb_predictions.value_counts().get('neg', 0)
    avg_score = (vader_scores.mean() + nb_score) / 2
    if avg_score > 0.05:
        return "Positive"
    elif avg_score < -0.05:
        return "Negative"
    else:
        return "Neutral"

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
