import os
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from utils import format_timestamp, groupTranscript

load_dotenv()


async def getTitle(video_id: str):
    """
    Fetch video title from YouTube Data API.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet",
        "id": video_id,
        "key": api_key
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            return data["items"][0]["snippet"]["title"]
        else:
            return "Unknown Title"
    except Exception as e:
        return {"error": str(e)}


async def getVideoDetails(video_url: str):
    """
    Get video title, transcript text, and formatted transcript array.
    """
    try:
        video_id = video_url.split("v=")[1]

        fetched_transcript = YouTubeTranscriptApi().fetch(video_id, languages=['en'])
        transcript = fetched_transcript.to_raw_data()
        grouped_transcript = groupTranscript(transcript, 30)

        formatted_transcript = []
        transcript_text_parts = []

        for entry in grouped_transcript:
            transcript_text_parts.append(entry["text"])
            formatted_transcript.append({
                "timestamp": format_timestamp(entry["start"]),
                "text": entry["text"]
            })

        transcript_text = " ".join(transcript_text_parts)
        title = await getTitle(video_id)

        if isinstance(title, dict) and "error" in title:
            return {"error": title["error"]}

        return {
            "title": title,
            "transcript_text": transcript_text,
            "formatted_transcript": formatted_transcript
        }
    except Exception as e:
        return {"error": str(e)}
