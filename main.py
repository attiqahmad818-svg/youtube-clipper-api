cat << 'EOF' > main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess, uuid, os, sys
import imageio_ffmpeg

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

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
        raise HTTPException(status_code=400, detail="Clip must be 1-180s.")
    out = f"/tmp/{uuid.uuid4()}.mp4"
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-playlist",
        "--extractor-args", "youtube:player_client=tv,android_vr,mweb",
        "--ffmpeg-location", ff,
        "--download-sections", f"*{req.start}-{req.end}",
        "-f", "b[ext=mp4]/bv*[ext=mp4]+ba[ext=m4a]/b",
        "--merge-output-format", "mp4",
        "-o", out, req.url
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if res.returncode != 0 or not os.path.exists(out):
        raise HTTPException(status_code=500, detail=(res.stderr or res.stdout)[-250:])
    return FileResponse(out, media_type="video/mp4", filename="clip.mp4")
EOF
python3 run.py
