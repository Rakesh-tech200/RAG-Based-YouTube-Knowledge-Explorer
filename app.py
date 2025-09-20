from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from getVideoDetails import getVideoDetails
from sumTranscript import sumTranscript
from chat import update_vector_store, ask_question
from getChapters import generate_chapters

app = FastAPI()


@app.get("/")
async def home():
    return "YouTube Summary API is working!"


@app.post("/api/get-video-details")
async def videoData(request: Request):
    data = await request.json()
    video_url = data.get("video_url")

    if not video_url:
        return JSONResponse(content={"error": "Missing video_url"}, status_code=400)

    result = getVideoDetails(video_url)

    if "error" in result:
        return JSONResponse(content={"error": result["error"]}, status_code=500)

    title = result["title"]
    transcript_text = result["transcript_text"]
    formatted_transcript = result["formatted_transcript"]

    summary = sumTranscript(transcript_text)
    chapters = generate_chapters(formatted_transcript)

    return {
        "title": title,
        "transcript": formatted_transcript,
        "chapter": chapters,
        "summary": summary
    }


@app.post("/api/update-vector-store")
async def update_vector(request: Request):
    data = await request.json()
    transcript_text = data.get("transcript_text")

    if not transcript_text:
        return JSONResponse(content={"error": "Missing transcript_text"}, status_code=400)

    try:
        update_vector_store(transcript_text)
        return {"message": "Vector store updated successfully"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/chat")
async def chat_with_video(request: Request):
    data = await request.json()
    question = data.get("question")

    if not question:
        return JSONResponse(content={"error": "Missing question"}, status_code=400)

    try:
        answer = ask_question(question)
        return {"answer": answer}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
