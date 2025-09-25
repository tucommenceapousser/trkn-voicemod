from flask import Flask, request, render_template, send_file
import os
import subprocess
import io
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

@app.route('/test_voice/<voice>')
def test_voice(voice):
    output = io.BytesIO()
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-tts",
        voice=voice,
        input="Salut ! Ici la voix de test générée par trhacknon."
    ) as response:
        response.stream_to_file(output)

    output.seek(0)
    return send_file(
        output,
        mimetype="audio/mpeg",
        as_attachment=True,
        download_name=f"voice_{voice}.mp3"
    )

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

    # Conversion (pas utilisée pour la démo TTS statique, mais utile si tu veux transcrire avant)
    wav_file = convert_to_wav(file)

    # ✅ Nouvelle syntaxe TTS OpenAI
    output = io.BytesIO()
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-tts",
        voice="fable",
        input="Salut ! Voici ta voix transformée par trhacknon."
    ) as response:
        response.stream_to_file(output)

    output.seek(0)
    return send_file(
        output,
        mimetype="audio/mpeg",
        as_attachment=True,
        download_name="voice_modified.mp3"
    )

@app.route('/live', methods=['POST'])
def live_audio():
    data = request.files['audio'].read()
    wav_file = convert_to_wav(io.BytesIO(data))

    # Pour l’instant : on renvoie l’audio brut converti
    # (tu peux remplacer ça par un TTS dynamique si tu veux un vrai modulateur live)
    return send_file(
        wav_file,
        mimetype="audio/wav"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
