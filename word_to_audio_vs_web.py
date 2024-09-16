# word_to_audio_vs_web.py
from flask import Flask, request, render_template, send_file
import edge_tts
import asyncio
import os
import tempfile
import re
from docx import Document

app = Flask(__name__)

def preprocess_text(text):
    text = re.sub(r'/+', ' y ', text)
    text = re.sub(r'(\d+):(\d+)', r'\1 punto \2', text)
    text = re.sub(r'(\d+)-(\d+)', r'\1 a \2', text)
    return text

async def text_to_speech(text, filename):
    communicate = edge_tts.Communicate(text, voice="es-MX-JorgeNeural")
    await communicate.save(filename)

def read_word_file(file_path):
    doc = Document(file_path)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return '\n'.join(text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # Guardar el archivo temporalmente y procesarlo
    with tempfile.TemporaryDirectory() as tmpdirname:
        file_path = os.path.join(tmpdirname, file.filename)
        file.save(file_path)

        # Leer y procesar el archivo
        text = read_word_file(file_path)
        processed_text = preprocess_text(text)

        # Convertir a audio
        tmp_audio_path = os.path.join(tmpdirname, 'texto_a_audio.mp3')
        asyncio.run(text_to_speech(processed_text, tmp_audio_path))

        # Enviar el archivo de audio al usuario
        return send_file(tmp_audio_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
