from flask import Flask, render_template, request, send_file
import fitz  # PyMuPDF
from gtts import gTTS
from moviepy.editor import *

import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def pdf_to_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def text_to_audio(text, audio_path):
    tts = gTTS(text=text, lang='ne')
    tts.save(audio_path)

def create_video(text, output_path):
    lines = text.split("\n")

    clips = []
    for i, line in enumerate(lines):
        if line.strip() == "":
            continue
        
        audio_file = f"temp_{i}.mp3"
        tts = gTTS(text=line, lang='ne')
        tts.save(audio_file)

        audio = AudioFileClip(audio_file)
        txt_clip = TextClip(line, fontsize=40, color='white', size=(1280,720))
        txt_clip = txt_clip.set_duration(audio.duration).set_audio(audio)

        clips.append(txt_clip)

    final_video = concatenate_videoclips(clips)
    final_video.write_videofile(output_path, fps=24)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["pdf"]
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        text = pdf_to_text(pdf_path)

        video_path = "static/output.mp4"
        create_video(text, video_path)

        return send_file(video_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
