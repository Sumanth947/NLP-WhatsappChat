WhatsApp Chat Analyzer
Overview
WhatsApp Chat Analyzer is a web application that processes and analyzes exported WhatsApp chat data to provide insights such as the total number of messages, most active users, sentiment analysis, word clouds, and more. The backend is built with FastAPI, and the frontend uses React for an interactive user experience.

Features
Upload WhatsApp Chat Data: Users can upload .txt or .csv files containing exported chat data.
Statistics Overview: Get an overview of total messages, words, media shared, and links.
Word Cloud Generation: Visualize the most commonly used words in the chat.
Emoji Analysis: Discover the most frequently used emojis.
Monthly and Daily Timelines: View chat activity over time.
Sentiment Analysis: Understand the overall sentiment of the chat.
Interactive Visuals: Graphs and charts for detailed analysis.
Technologies Used
Backend: FastAPI (Python)
Frontend: React.js, Vite.js
Data Processing: Pandas, NLTK, WordCloud
Charting: Matplotlib, Seaborn, React components
Deployment: Uvicorn (development server)
Installation
Prerequisites
Python 3.7+
Node.js 14+ and npm or Yarn
Backend Setup
Clone the repository:

bash
Copy code
git clone https://github.com/username/whatsapp-chat-analyzer.git
cd whatsapp-chat-analyzer/pythonbackend
Create a virtual environment and activate it:

bash
Copy code
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Run the FastAPI server:

bash
Copy code
uvicorn main:app --reload
Frontend Setup
Navigate to the frontend directory:

bash
Copy code
cd ../reactfrontend
Install dependencies:

bash
Copy code
npm install  # Or: yarn install
Run the frontend development server:

bash
Copy code
npm run dev  # Or: yarn dev
Usage
Access the frontend at http://localhost:5173.
Upload a WhatsApp chat file (either .txt or .csv).
Click Analyze Chat to process the data.
View the results, including statistics, word clouds, emoji analysis, and sentiment overview.
API Endpoints
POST /api/analyze
Uploads a chat file and returns analysis results.
GET /api/wordcloud
Returns a base64-encoded word cloud image.
GET /api/emoji-analysis
Provides a list of the most frequently used emojis in the chat.
GET /api/timeline
Returns data for monthly chat activity.
Troubleshooting
CORS Errors: Ensure CORS middleware is enabled in main.py.
File Parsing Issues: Check the chat file format and ensure it matches the expected structure.
Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

License
This project is licensed under the MIT License.

Acknowledgements
FastAPI
React
NLTK
WordCloud
