from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from random import randint
from nltk.corpus import movie_reviews
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import nltk

# Ensure necessary data is downloaded
nltk.download('movie_reviews')

# Initialize URL extractor
extract = URLExtract()

# Train a Naive Bayes model on the NLTK movie reviews dataset
def train_naive_bayes():
    documents = [(movie_reviews.raw(fileid), category)
                 for category in movie_reviews.categories()
                 for fileid in movie_reviews.fileids(category)]
    
    texts, labels = zip(*documents)
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)
    
    # Use CountVectorizer with MultinomialNB
    model = make_pipeline(CountVectorizer(), MultinomialNB())
    model.fit(X_train, y_train)
    return model

# Initialize Naive Bayes model
nb_model = train_naive_bayes()

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch  number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)

def most_active_user(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(columns={'index':'name','user':'percent'})
    return x, df

def random_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    r, g, b = randint(0, 255), randint(0, 255), randint(0, 255)
    return f"rgb({r}, {g}, {b})"

def create_wordcloud(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    f1 = open('stopwords-hindi.txt', 'r', encoding='utf-8')
    stop_words_hindi = f1.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'Group notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words and word not in stop_words_hindi:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500, height=500, max_words=80, min_font_size=10, background_color='white', color_func=random_color_func)
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time
    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month']

def sentiment_analysis(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # VADER sentiment analysis
    sentiments = SentimentIntensityAnalyzer()
    df['happy'] = [sentiments.polarity_scores(i)["pos"] for i in df['message']]
    df['sad'] = [sentiments.polarity_scores(i)["neg"] for i in df['message']]
    df['ok'] = [sentiments.polarity_scores(i)["neu"] for i in df['message']]
    
    vader_score = sum(df['happy']) - sum(df['sad'])

    # Naive Bayes sentiment analysis
    nb_predictions = [nb_model.predict([msg])[0] for msg in df['message']]
    nb_score = nb_predictions.count('pos') - nb_predictions.count('neg')

    # Final sentiment score (average of VADER and Naive Bayes)
    final_score = (vader_score + nb_score) / 2

    if final_score > 0:
        return "positive"
    elif final_score < 0:
        return "negative"
    else:
        return "neutral"

def heatmap_activity(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return user_heatmap
