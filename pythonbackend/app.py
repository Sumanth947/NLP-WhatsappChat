import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import openai
from datetime import datetime

# Move the function definition to the top of the file, after imports
def get_chatbot_response(prompt, chat_data):
    """Generate chatbot response based on chat analysis"""
    try:
        # Create a context from chat data
        context = f"""
        Chat Statistics:
        - Total Messages: {len(chat_data)}
        - Time Period: {chat_data['date'].min()} to {chat_data['date'].max()}
        - Number of Participants: {len(chat_data['user'].unique())}
        """
        
        # Combine context and user prompt
        full_prompt = f"{context}\n\nUser Question: {prompt}\n\nAnswer:"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful chat analyzer assistant. Answer questions about the WhatsApp chat data provided."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Initialize session state for chatbot
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize session state for uploaded file and selected user
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
if "selected_user" not in st.session_state:
    st.session_state["selected_user"] = "Overall"

# Initialize OpenAI (you'll need to set this up with your API key)
openai.api_key = 'your_open_api_key'

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
        try:
            # Get URL sentiments
            url_sentiments = helper.url_sentiment_analysis(selected_user, df)
            
            if url_sentiments and len(url_sentiments) > 0:
                url_options = list(url_sentiments.keys())
                
                # Create a container for URL selection
                url_container = st.container()
                
                with url_container:
                    # Simple selectbox without session state
                    selected_url = st.selectbox(
                        "Select a URL to view sentiment", 
                        url_options,
                        key="url_select"
                    )
                    
                    # Display URL analysis in a separate container
                    analysis_container = st.container()
                    
                    with analysis_container:
                        if selected_url:
                            try:
                                sentiment, title, description = url_sentiments[selected_url]
                                
                                st.markdown("---")
                                st.subheader("URL Analysis")
                                st.write(f"🔗 **URL:** {selected_url}")
                                st.write(f"😊 **Sentiment:** {sentiment if sentiment else 'Not available'}")
                                
                                if title:
                                    st.write(f"📑 **Title:** {title}")
                                if description:
                                    st.write(f"📝 **Description:** {description}")
                                st.markdown("---")
                                
                            except Exception as url_error:
                                st.error(f"Error analyzing this URL: {str(url_error)}")
            else:
                st.warning("No valid URLs found in the chat or unable to analyze URLs.")
                
        except Exception as e:
            st.error(f"An error occurred while analyzing URLs: {str(e)}")
            st.info("Try checking your internet connection or try again later.")

        # Chatbot Interface
        st.title("Chat Analysis Assistant")
        
        # Create columns for input and button
        col1, col2 = st.columns([4, 1])
        with col1:
            user_question = st.text_input(
                "Ask me anything about your chat analysis:",
                key="chatbot_input"
            )
        with col2:
            submit_button = st.button("Ask", key="chatbot_button")

        # Process the question when button is clicked
        if submit_button and user_question:
            with st.spinner("Analyzing..."):
                try:
                    response = get_chatbot_response(user_question, df)
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "question": user_question,
                        "answer": response
                    })
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### Chat History")
            for chat in st.session_state.chat_history:
                st.markdown(f"**You:** {chat['question']}")
                st.markdown(f"**🤖 Assistant:** {chat['answer']}")
                st.markdown("---")

        # Example questions without nested expander
        st.markdown("### Example questions you can ask:")
        st.markdown("""
        - Who is the most active user in the chat?
        - What time of day is the chat most active?
        - What are the most common topics discussed?
        - What's the overall sentiment of the chat?
        - How many messages were sent on average per day?
        - What are the most used emojis in the chat?
        """)
else:
    st.write("Please upload a chat file to start analysis.")
