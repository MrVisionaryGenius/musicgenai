from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import replicate
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

replicate.api_token = os.getenv('REPLICATE_API_TOKEN')
google_api_key = os.getenv('GOOGLE_API_KEY')

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Configure Google Generative AI
genai.configure(api_key=google_api_key)

def generate_lyrics(prompt):
    model = genai.GenerativeModel(
        "models/gemini-1.5-flash",
        system_instruction="You are a music lyrics writer and your task is to write lyrics of music under 30 words based on user's prompt. Just return the lyrics and nothing else.",
    )
    response = model.generate_content(prompt)
    output = response.text
    cleaned_output = output.replace('\n', " ")
    formatted_lyrics = f"♪ {cleaned_output} ♪"
    return formatted_lyrics

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-music")
async def generate_music(prompt: str = Form(...), duration: int = Form(...)):
    lyrics = generate_lyrics(prompt)
    prompt_with_lyrics = lyrics
    print(prompt_with_lyrics)

    input_data = {
        "prompt": prompt_with_lyrics,
        "text_temp": 0.7,
        "output_full": False,
        "waveform_temp": 0.7
    }

    output = replicate.run(
        "suno-ai/bark:b76242b40d67c76ab6742e987628a2a9ac019e11d56ab96c4e91ce03b79b2787",
        input=input_data
    )
    print(output)
    music_url = output['audio_out']
    music_path_or_url = music_url
    print(music_path_or_url)
    return JSONResponse(content={"url": music_path_or_url})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
