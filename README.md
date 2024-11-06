# WhatsApp Chat Analyzer

## Overview
WhatsApp Chat Analyzer is a web application that processes and analyzes exported WhatsApp chat data to provide insights such as the total number of messages, most active users, sentiment analysis, word clouds, and more. The backend is built with FastAPI, and the frontend uses React for an interactive user experience.

## Features
- **Upload WhatsApp Chat Data**: Users can upload `.txt` or `.csv` files containing exported chat data.
- **Statistics Overview**: Get an overview of total messages, words, media shared, and links.
- **Word Cloud Generation**: Visualize the most commonly used words in the chat.
- **Emoji Analysis**: Discover the most frequently used emojis.
- **Monthly and Daily Timelines**: View chat activity over time.
- **Sentiment Analysis**: Understand the overall sentiment of the chat.
- **Interactive Visuals**: Graphs and charts for detailed analysis.

## Technologies Used
- **Backend**: FastAPI (Python)
- **Frontend**: React.js, Vite.js
- **Data Processing**: Pandas, NLTK, WordCloud
- **Charting**: Matplotlib, Seaborn, React components
- **Deployment**: Uvicorn (development server)

## Installation

### Prerequisites
- Python 3.7+
- Node.js 14+ and npm or Yarn

### Backend Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/username/whatsapp-chat-analyzer.git
   cd whatsapp-chat-analyzer/pythonbackend
