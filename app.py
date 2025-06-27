from flask import Flask, request, render_template
import asyncio
import io
from contextlib import redirect_stdout
from transcript_worker import process_url

from pathlib import Path

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    logs = ""

    if request.method == "POST":
        url = request.form.get("video_url")

        async def run_and_capture():
            f = io.StringIO()

            try:
                # Capture all stdout from process_url
                with redirect_stdout(f):
                    await process_url(url)
            except Exception as e:
                f.write(f"[ERROR] Exception during processing: {e}\n")

            log_output = f.getvalue()

            # Try to find the newest transcript file
            transcript_dir = Path("transcripts")
            if transcript_dir.exists():
                txt_files = sorted(transcript_dir.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
                if txt_files:
                    transcript_text = txt_files[0].read_text()
                    return transcript_text, log_output

            return "[No transcript file found]", log_output

        transcript, logs = asyncio.run(run_and_capture())

    return render_template("index.html", transcript=transcript, logs=logs)

if __name__ == "__main__":
    app.run(debug=True)
