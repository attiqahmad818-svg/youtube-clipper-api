from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess
import uuid
import os

app = FastAPI()

# Allow your website to connect to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClipRequest(BaseModel):
    url: str
    start: int
    end: int

@app.get("/")
def home():
    return {"status": "Clipper Backend is Live!"}

@app.post("/api/clip")
def make_clip(req: ClipRequest):
    if req.end <= req.start or (req.end - req.start) > 180:
        raise HTTPException(status_code=400, detail="Clip must be between 1 and 180 seconds.")

    clip_id = str(uuid.uuid4())
    output_path = f"/tmp/{clip_id}.mp4"

    cmd = [
        "yt-dlp",
        "--download-sections", f"*{req.start}-{req.end}",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "--merge-output-format", "mp4",
        "-o", output_path,
        req.url
    ]

    try:
        subprocess.run(cmd, check=True, timeout=120)
        return FileResponse(output_path, media_type="video/mp4", filename="clip.mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clip video: {str(e)}")
