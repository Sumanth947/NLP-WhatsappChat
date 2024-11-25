import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize session state for uploaded file and selected user
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
if "selected_user" not in st.session_state:
    st.session_state["selected_user"] = "Overall"

# Streamlit Sidebar
st.sidebar.title("WhatsApp Chat Analyzer")

# File uploader
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file:
    st.session_state["uploaded_file"] = uploaded_file  # Save file in session state

# Check if a file has been uploaded
if st.session_state["uploaded_file"]:
    # Preprocess uploaded file
    bytes_data = st.session_state["uploaded_file"].getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocessor(data)

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    if 'Group notification' in user_list:
        user_list.remove('Group notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    # User selection (use session state to persist selection)
    selected_user = st.sidebar.selectbox(
        "Show analysis for", 
        user_list, 
        index=user_list.index(st.session_state["selected_user"])
    )
    st.session_state["selected_user"] = selected_user  # Save selection in session state

    # Button to trigger analysis
    if st.sidebar.button("Show Analysis"):
        # Chat Statistics
        st.title("Chat Statistics")
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Messages", num_messages)
        col2.metric("Words", words)
        col3.metric("Media Shared", num_media_messages)
        col4.metric("Links Shared", num_links)

        # Monthly Timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily Timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity Map
        st.title("Activity Map")
        col1, col2 = st.columns(2)
        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='blue')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # Weekly Heatmap
        st.header("Weekly Activity Map")
        user_heatmap = helper.heatmap_activity(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax)
        st.pyplot(fig)

        # Word Cloud
        st.title("Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Emoji Analysis
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df).head(15)
        st.dataframe(emoji_df)

        # Sentiment Analysis
        st.title("Sentiment Analysis")
        result = helper.sentiment_analysis(selected_user, df)
        st.text(result)

        # Busiest Users
        if selected_user == "Overall":
            st.title("Most Active Users")
            x, new_df = helper.most_active_user(df)
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)
            with col1:
                ax.bar(x.index, x.values, color='yellow')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # URL Sentiment Analysis
        st.title("URL Sentiment Analysis")
        url_sentiments = helper.url_sentiment_analysis(selected_user, df)
        if url_sentiments:
            url_options = list(url_sentiments.keys())
            selected_url = st.selectbox("Select a URL to view sentiment", url_options)
            if selected_url:
                sentiment, title, description = url_sentiments[selected_url]
                st.write(f"**URL:** {selected_url}")
                st.write(f"**Sentiment:** {sentiment}")
                st.write(f"**Title:** {title}")
                st.write(f"**Description:** {description}")
        else:
            st.write("No URLs found in the chat.")
else:
    st.write("Please upload a chat file to start analysis.")
