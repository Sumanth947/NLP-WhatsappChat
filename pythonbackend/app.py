import streamlit as st
from chatbot import get_chatbot_response
import helper  # Import helper which contains preprocess
import matplotlib.pyplot as plt
import seaborn as sns
from helper import count_links, extract_urls

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# File upload
uploaded_file = st.sidebar.file_uploader("Choose a file")

# Create the heatmap
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    
    # Process the uploaded data using helper.preprocess()
    df = helper.preprocess(data)

    # Select user from the uploaded data
    user_list = df['user'].unique().tolist()
    user_list.sort()
    user_list.insert(0, "Overall")  # Add 'Overall' as an option

    # Streamlit selectbox for user selection (with a unique key)
    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list, key="select_user")

    # Generate the heatmap
    user_heatmap = helper.activity_heatmap(selected_user, df)

    # Ensure that the heatmap data is not empty before plotting
    if not user_heatmap.empty and user_heatmap.shape[0] > 0 and user_heatmap.shape[1] > 0:
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)
    else:
        st.warning("No data available to display in the heatmap.")

# Main interface
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    
    # Process the uploaded data using helper.preprocess()
    df = helper.preprocess(data)
    
    # Get unique users
    user_list = df['user'].unique().tolist()
    try:
        user_list.remove('system_notification')
    except ValueError:
        pass
    user_list.sort()
    user_list.insert(0, "Overall")
    
    # Select user from the uploaded data (with a unique key)
    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list, key="select_user_2")

    # Stats Area
    stats = helper.fetch_stats(selected_user, df)
    st.sidebar.write(f"Debug - Stats: {stats}")
    num_messages, words, num_media_messages = stats
    num_links = count_links(df)
    urls = extract_urls(df)
    
    # Create tabs for Analysis and Chat
    tab1, tab2 = st.tabs(["Analysis", "Chat"])
    
    with tab1:
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

        # Daily timeline
        # st.title("Daily Timeline")
        # daily_timeline = helper.daily_timeline(selected_user, df)
        # fig, ax = plt.subplots()
        # ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        # plt.xticks(rotation='vertical')
        # st.pyplot(fig)

        # Activity map
        # st.title('Activity Map')
        # col1, col2 = st.columns(2)

        # with col1:
        #     st.header("Most busy day")
        #     busy_day = helper.week_activity_map(selected_user, df)
        #     fig, ax = plt.subplots()
        #     ax.bar(busy_day.index, busy_day.values, color='purple')
        #     plt.xticks(rotation='vertical')
        #     st.pyplot(fig)

        # with col2:
        #     st.header("Most busy month")
        #     busy_month = helper.month_activity_map(selected_user, df)
        #     fig, ax = plt.subplots()
        #     ax.bar(busy_month['month'].tolist(), busy_month['message'].tolist(), color='orange')
        #     plt.xticks(rotation='vertical')
        #     st.pyplot(fig)

        # Weekly activity map
        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # Finding the busiest users in the group
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Most common words
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1])
        plt.xticks(rotation='vertical')
        st.title('Most common words')
        st.pyplot(fig)

        # Emoji analysis
        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df['Count'].head(), labels=emoji_df['Emoji'].head(), autopct="%0.2f")
            st.pyplot(fig)

        # URL Analysis Section
        st.subheader("URL Analysis")
        if urls:
            selected_url = st.selectbox("Select a URL to open:", urls)
            if selected_url:
                st.markdown(f"[Click here to open the URL]({selected_url})", unsafe_allow_html=True)

                # Optionally, you could add sentiment analysis, title, description, etc., if required
                sentiment, title, description = helper.analyze_url(selected_url)
                st.write(f"Sentiment: {sentiment}")
                st.write(f"Title: {title}")
                st.write(f"Description: {description}")

        else:
            st.write("No URLs found in the chat.")

    # Chat tab
    with tab2:
        st.header("Chat with Bot")
        
        # Show data status
        if df is not None and not df.empty:
            st.success(f"Chat data loaded: {len(df)} messages")
        
        # Single chat input
        user_input = st.text_input("Ask me anything:", key="single_chat_input")
        
        # When user submits a question
        if user_input:
            try:
                response = get_chatbot_response(user_input, df)
                st.session_state.chat_history.append(("You", user_input))
                st.session_state.chat_history.append(("Bot", response))
            except Exception as e:
                st.error(f"Error occurred: {str(e)}")

        # Display chat history
        if st.session_state.chat_history:
            st.write("Chat History:")
            for role, message in st.session_state.chat_history:
                if role == "You":
                    st.markdown(f"**You:** {message}")
                else:
                    st.markdown(f"**Bot:** {message}")

else:
    st.sidebar.warning("Please upload a WhatsApp chat file to begin analysis.")
