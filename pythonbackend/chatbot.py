import streamlit as st
import pandas as pd
from textblob import TextBlob
import emoji
from collections import Counter
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

# Download required NLTK data
try:
    nltk.download('punkt')
    nltk.download('stopwords')
except:
    pass

def get_common_words(messages, n=5):
    """Extract most common words excluding stopwords."""
    words = []
    stop_words = set(stopwords.words('english'))
    for msg in messages:
        if isinstance(msg, str):
            tokens = word_tokenize(msg.lower())
            words.extend([word for word in tokens if word.isalnum() and word not in stop_words])
    return Counter(words).most_common(n)

def get_chatbot_response(user_input, chat_data):
    """
    Generate responses based on different types of questions about the chat data.
    """
    try:
        question = user_input.lower()
        
        # 1. Most active user
        if "most active" in question or "who sent most" in question:
            user_counts = chat_data['user'].value_counts()
            most_active = user_counts.index[0]
            count = user_counts.values[0]
            return f"The most active user is '{most_active}' with {count} messages."
        
        # 2. Total messages
        elif "how many" in question or "total messages" in question:
            total = len(chat_data)
            return f"There are {total} messages in the chat."
            
        # 3. Emoji analysis
        elif "emoji" in question:
            all_emojis = []
            for message in chat_data['message']:
                if isinstance(message, str):
                    emojis = [c for c in message if c in emoji.EMOJI_DATA]
                    all_emojis.extend(emojis)
            
            if all_emojis:
                emoji_counts = Counter(all_emojis).most_common(5)
                response = "Most used emojis are:\n"
                for em, count in emoji_counts:
                    response += f"{em}: {count} times\n"
                return response
            else:
                return "No emojis found in the chat."
                
        # 4. Time analysis
        elif "time" in question or "when" in question:
            if "day" in question:
                day_counts = chat_data['day_name'].value_counts()
                busiest_day = day_counts.index[0]
                return f"The busiest day is {busiest_day} with {day_counts.max()} messages."
            else:
                active_hours = chat_data['hour'].value_counts().sort_index()
                most_active_hour = active_hours.index[active_hours.argmax()]
                return f"The most active hour is {most_active_hour}:00 with {active_hours.max()} messages."

        # 5. Common words
        elif "common words" in question or "most used words" in question:
            common_words = get_common_words(chat_data['message'])
            response = "Most common words are:\n"
            for word, count in common_words:
                response += f"'{word}': {count} times\n"
            return response

        # 6. Media analysis
        elif "media" in question or "images" in question or "videos" in question:
            media_count = sum(chat_data['message'].str.contains('<Media omitted>', case=False, na=False))
            return f"There are {media_count} media messages (images/videos/files) shared in the chat."

        # 7. Links shared
        elif "links" in question or "urls" in question:
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            links_count = sum(chat_data['message'].str.contains(url_pattern, case=False, na=False))
            return f"There are {links_count} links shared in the chat."

        # 8. Monthly trends
        elif "month" in question or "monthly" in question:
            monthly_counts = chat_data.groupby('month').size()
            busiest_month = monthly_counts.idxmax()
            month_name = pd.datetime(2020, busiest_month, 1).strftime('%B')
            return f"The busiest month is {month_name} with {monthly_counts.max()} messages."

        # 9. Specific user analysis
        elif "about user" in question or "tell me about" in question:
            name = question.split("about")[-1].strip()
            if name in chat_data['user'].values:
                user_msgs = chat_data[chat_data['user'] == name]
                msg_count = len(user_msgs)
                active_hour = user_msgs['hour'].mode()[0]
                return f"User '{name}' has sent {msg_count} messages. They are most active at {active_hour}:00 hours."
            else:
                return f"User '{name}' not found in the chat."

        # 10. Message patterns
        elif "pattern" in question or "message length" in question:
            avg_length = chat_data['message'].str.len().mean()
            max_length = chat_data['message'].str.len().max()
            return f"Average message length is {avg_length:.1f} characters. Longest message has {max_length} characters."
            
        # Default response with suggestions
        else:
            return ("I can help you analyze the chat! Try asking questions like:\n"
                   "- Who is the most active user?\n"
                   "- How many messages are there?\n"
                   "- What are the most used emojis?\n"
                   "- When is the chat most active?\n"
                   "- What are the most common words?\n"
                   "- How many media files were shared?\n"
                   "- How many links were shared?\n"
                   "- Show me monthly trends\n"
                   "- Tell me about [user name]\n"
                   "- What are the message patterns?")
            
    except Exception as e:
        st.error(f"Error in chatbot: {str(e)}")
        return f"Error analyzing the chat: {str(e)}" 