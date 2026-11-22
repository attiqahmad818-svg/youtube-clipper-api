import os, subprocess
subprocess.run(["pip", "install", "fastapi", "uvicorn", "yt-dlp", "imageio-ffmpeg"])
os.system("python3 -m uvicorn main:app --host 0.0.0.0 --port 10000")
