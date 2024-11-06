import streamlit as st
import preprocessor  # Import the module
import helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("WhatsApp Chat Analyzer")

# File uploader in the sidebar
uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp chat file", type="txt")

if uploaded_file is not None:
    # Read the uploaded file and decode it
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    
    # Use the correct function name from preprocessor.py
    df = preprocessor.preprocess_chat(data.splitlines())

    # Fetch unique users
    user_list = df['user'].unique().tolist()

    # Remove "Group notification" and prepare user selection options
    if 'Group notification' in user_list:
        user_list.remove('Group notification')
    user_list.sort()
    user_list.insert(0, "Overall")  # Add an option for "Overall" analysis

    # User selection for analysis
    selected_user = st.sidebar.selectbox("Show analysis with respect to", user_list)

    # Button to trigger analysis
    if st.sidebar.button("Show Analysis"):

        # Display top statistics
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # Monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity map
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # Weekly activity heatmap
        st.header("Weekly Activity Map")
        user_heatmap = helper.heatmap_activity(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax, cmap="YlGnBu")
        st.pyplot(fig)

        # Daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Busiest users (group level)
        if selected_user == 'Overall':
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

        # Word cloud
        st.title("Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis('off')  # Remove axes for better visualization
        st.pyplot(fig)

        # Emoji analysis
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df).head(15)
        st.dataframe(emoji_df)

        # Sentiment analysis
        st.title("Sentiment Analysis")
        result = helper.sentiment_analysis(selected_user, df)
        st.write(result)
