from flask import Flask, request, jsonify
import os
import numpy as np
from tacatron import TacatronProsodyExtractor
from ecapa_tdnn import ECAPAVoiceprintExtractor

app = Flask(__name__)

# Instantiate extractors once when the app starts.
voiceprint_extractor = ECAPAVoiceprintExtractor()
prosody_extractor = TacatronProsodyExtractor(use_cuda=False)

@app.route('/process_speaker_embedding', methods=['POST'])
def process_speaker_embedding_endpoint():
    data = request.get_json()
    base_name = data.get('base_name')
    audio_files = data.get('audio_files')

    # Call your function to process the speaker embeddings.
    process_speaker_embedding(base_name, audio_files)
    return jsonify({"message": "Speaker embeddings processed successfully."})

@app.route('/validate_trial', methods=['POST'])
def validate_trial_endpoint():
    data = request.get_json()
    speaker_name = data.get('speaker_name')
    trialAudio = data.get('trialAudio')
    text = data.get('text')
    
    # Use the global extractors in your validation function.
    result = validateTrial(speaker_name, trialAudio, text)

    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True)
