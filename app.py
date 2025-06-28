from flask import Flask, render_template, request
import asyncio
from transcript_worker import process_url

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    if request.method == "POST":
        url = request.form.get("video_url")
        async def run_single():
            await process_url(url)
            from pathlib import Path
            files = sorted(Path("transcripts").glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
            if files:
                return files[0].read_text()
            return "[No transcript file found]"
        transcript = asyncio.run(run_single())
    return render_template("index.html", transcript=transcript)

if __name__ == "__main__":
    app.run(debug=True)