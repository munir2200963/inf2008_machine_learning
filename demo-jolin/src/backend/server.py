from flask import Flask, request, jsonify
import os
import numpy as np
from flask_cors import CORS  # Handles CORS
from tacatron import TacatronProsodyExtractor
from ecapa_tdnn import ECAPAVoiceprintExtractor
from process_speaker_embedding import process_speaker_embedding
from validate_trial import validateTrial
import sentences  # Import sentences dynamically

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Ensure necessary folders exist
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Instantiate extractors
voiceprint_extractor = ECAPAVoiceprintExtractor()
prosody_extractor = TacatronProsodyExtractor(use_cuda=False)

@app.route("/")
def home():
    return jsonify({"message": "Server is running!"}), 200

@app.route("/get-sentences", methods=["GET"])
def get_sentences():
    """
    Fetch all 20 sentences from `sentences.py`.
    """
    return jsonify({"sentences": sentences.sentences}), 200  

@app.route("/enroll", methods=["POST"])
def enroll_user():
    """
    Enrolls a user by saving 20 recorded sentences and generating embeddings.
    """
    print("Enrollment request received")
    print("FILES RECEIVED:", request.files.keys())  # Debugging
    print("FORM DATA:", request.form)  # Debugging form data
    
    user_id = request.form.get("user_id")  # Get user_id dynamically from the frontend form
    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400

    # Ensure 20 audio files are received
    saved_files = []
    for i in range(20):  # Expecting 20 sentences
        file_key = f"audio_{i}"
        if file_key in request.files:
            audio_file = request.files[file_key]
            filename = f"{user_id}_audio_{i}.wav" 
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            # Save file
            audio_file.save(file_path)

            # Verify if saved
            if os.path.exists(file_path):
                saved_files.append(file_path)
                print(f"✅ Saved: {file_path}")  # Debugging
            else:
                print(f"❌ Failed to save {file_key}")  # Debugging

    if len(saved_files) != 20:
        return jsonify({"error": f"Expected 20 files, but received {len(saved_files)}!"}), 500

    # ✅ Now pass the dynamically received user_id
    process_speaker_embedding(user_id, saved_files)

    return jsonify({
        "message": "✅ Enrollment successful!",
        "saved_files": saved_files,
        "user_id": user_id
    }), 200


@app.route('/validate_trial', methods=['POST'])
def validate_trial_endpoint():
    """
    Validates a speaker's trial audio against stored embeddings.
    """
    user_id = request.form.get("speaker_name")
    text = request.form.get("text")
    trial_audio = request.files.get("trialAudio")

    if not user_id or not text or not trial_audio:
        return jsonify({"error": "Missing speaker_name, text, or trial audio"}), 400

    # Save trial audio
    trial_path = os.path.join(UPLOAD_FOLDER, f"{user_id}_trial.wav")
    trial_audio.save(trial_path)

    # Validate
    result = validateTrial(user_id, trial_path, text)

    return jsonify({"result": result}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
