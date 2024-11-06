from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import base64
import io
from preprocessor import preprocess_chat
from helper import (
    fetch_stats, create_wordcloud, emoji_helper, monthly_timeline, 
    daily_timeline, week_activity_map, month_activity_map, 
    sentiment_analysis, heatmap_activity
)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace with "*" for all origins if necessary
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze_chat(file: UploadFile):
    if not file.filename.endswith(('.txt', '.csv')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a .txt or .csv file.")
    
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")
        
        data = content.decode("utf-8").splitlines()
        df = preprocess_chat(data)

        if df.empty:
            raise HTTPException(status_code=400, detail="Data processing resulted in an empty DataFrame.")
        
        # Calculate statistics
        num_messages, words, num_media, num_links = fetch_stats('Overall', df)
        sentiment_result = sentiment_analysis('Overall', df)

        # Prepare response data
        result_data = {
            "total_messages": num_messages,
            "words": words,
            "num_media": num_media,
            "num_links": num_links,
            "sentiment_result": sentiment_result,
        }

        return JSONResponse(content=result_data)

    except Exception as e:
        print("Error during file processing:", e)
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")

@app.get("/api/wordcloud")
async def get_wordcloud():
    try:
        # Load your processed DataFrame as needed
        df = pd.read_csv('whatsapp-chat-data.txt')  # Replace with actual processed DataFrame

        # Generate word cloud
        wc_image = create_wordcloud('Overall', df)
        buf = io.BytesIO()
        wc_image.to_image().save(buf, format='PNG')
        base64_image = base64.b64encode(buf.getvalue()).decode("utf-8")
        return {"wordcloud": base64_image}

    except Exception as e:
        print("Error generating word cloud:", e)
        raise HTTPException(status_code=500, detail="An error occurred while generating the word cloud.")

@app.get("/api/emoji-analysis")
async def get_emoji_analysis():
    try:
        df = pd.read_csv('whatsapp-chat-data.txt')  # Replace with actual processed DataFrame
        emoji_data = emoji_helper('Overall', df).to_dict(orient='records')
        return {"emoji_analysis": emoji_data}
    except Exception as e:
        print("Error during emoji analysis:", e)
        raise HTTPException(status_code=500, detail="An error occurred during emoji analysis.")
@app.get("/api/monthly-timeline")
async def get_monthly_timeline():
    try:
        print("Loading processed chat data...")
        df = pd.read_csv('whatsapp-chat-data.txt')
        print("Data loaded:", df.head())  # Print first few rows for verification

        if df.empty:
            print("DataFrame is empty.")
            raise HTTPException(status_code=404, detail="Processed data not found or is empty.")

        print("Generating monthly timeline...")
        timeline = monthly_timeline('Overall', df)
        print("Monthly timeline generated successfully:", timeline.head())  # Print sample timeline data

        return {"monthly_timeline": timeline.to_dict(orient='records')}
    except FileNotFoundError:
        print("Processed chat data file not found.")
        raise HTTPException(status_code=500, detail="Processed chat data file not found.")
    except pd.errors.EmptyDataError:
        print("Processed chat data file is empty.")
        raise HTTPException(status_code=500, detail="Processed chat data file is empty.")
    except Exception as e:
        print("Error generating monthly timeline:", e)
        raise HTTPException(status_code=500, detail=f"An error occurred while generating the monthly timeline: {e}")


@app.get("/api/timeline")
async def get_timeline():
    try:
        df = pd.read_csv('whatsapp-chat-data.txt')  # Replace with actual processed DataFrame
        timeline = monthly_timeline('Overall', df).to_dict(orient='records')
        return {"timeline": timeline}
    except Exception as e:
        print("Error generating timeline:", e)
        raise HTTPException(status_code=500, detail="An error occurred while generating the timeline.")

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


