from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from random import randint

extract = URLExtract()

def fetch_stats(selected_user,df):

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

def sentiment_analysis(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    sentiments = SentimentIntensityAnalyzer()
    df['positive'] = [sentiments.polarity_scores(i)["pos"] for i in df['message']]
    df['negative'] = [sentiments.polarity_scores(i)["neg"] for i in df['message']]
    df['neutral'] = [sentiments.polarity_scores(i)["neu"] for i in df['message']]
    x = sum(df['positive'])
    y = sum(df['negative'])
    z = sum(df['neutral'])

    def score(a, b, c):
        if (a > b) and (a > c):
            return "positive"
        elif (b > a) and (b > c):
            return "Negative"
        elif (c > a) and (c > b):
            return "Neutral"
        else:
            return "Undetermined"

    return score(x, y, z)

def heatmap_activity(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap