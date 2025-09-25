from flask import Flask, request, render_template, send_file
import openai
import os
import subprocess
import io

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

def convert_to_wav(input_file):
    """Convertir n’importe quel audio en wav mono 16kHz via ffmpeg"""
    output = io.BytesIO()
    process = subprocess.run(
        ['ffmpeg', '-i', 'pipe:0', '-ar', '16000', '-ac', '1', '-f', 'wav', 'pipe:1'],
        input=input_file.read(),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )
    output.write(process.stdout)
    output.seek(0)
    return output

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

    wav_file = convert_to_wav(file)

    # Génération TTS OpenAI
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

@app.route('/live', methods=['POST'])
def live_audio():
    data = request.files['audio'].read()
    wav_file = convert_to_wav(io.BytesIO(data))

    # Pour le live on renvoie le même wav (optionnel: TTS temps réel)
    return send_file(
        wav_file,
        mimetype="audio/wav"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
