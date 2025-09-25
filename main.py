from flask import Flask, request, render_template, send_file
import openai
import os
from pydub import AudioSegment
import io

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return "Aucun fichier envoyé", 400
    
    file = request.files['audio']
    if file.filename == '':
        return "Fichier vide", 400

    audio = AudioSegment.from_file(file)
    buf = io.BytesIO()
    audio.export(buf, format='wav')
    buf.seek(0)

    # Appel OpenAI TTS
    response = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input="Salut ! Voici ta voix transformée par trhacknon."
    )

    tts_audio = io.BytesIO(response.audio)
    tts_audio.seek(0)
    
    return send_file(
        tts_audio,
        mimetype="audio/mpeg",
        as_attachment=True,
        download_name="voice_modified.mp3"
    )

# Endpoint pour live audio streaming
@app.route('/live', methods=['POST'])
def live_audio():
    # Recevoir un petit segment audio depuis le front
    data = request.files['audio'].read()
    buf = io.BytesIO(data)
    audio = AudioSegment.from_file(buf)
    
    # Ici on pourrait faire du TTS ou filtrage, pour l'instant on renvoie juste le même audio
    output = io.BytesIO()
    audio.export(output, format='wav')
    output.seek(0)
    
    return send_file(output, mimetype="audio/wav")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
