from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess, uuid, os, sys
import imageio_ffmpeg

app = FastAPI()

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
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-playlist",
        "--extractor-args", "youtube:player_client=android,ios",
        "--ffmpeg-location", ffmpeg_path,
        "--download-sections", f"*{req.start}-{req.end}",
        "-f", "b[ext=mp4]/bv*[ext=mp4]+ba[ext=m4a]/b",
        "--merge-output-format", "mp4",
        "-o", output_path,
        req.url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0 or not os.path.exists(output_path):
        err_msg = (result.stderr or result.stdout or "Unknown yt-dlp error")[-250:]
        raise HTTPException(status_code=500, detail=err_msg)

    return FileResponse(output_path, media_type="video/mp4", filename="clip.mp4")
