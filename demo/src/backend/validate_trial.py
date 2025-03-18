import os
import numpy as np
import torch
import pickle
import joblib
from pydub import AudioSegment
from tacatron import TacatronProsodyExtractor
from ecapa_tdnn import ECAPAVoiceprintExtractor
from clustering_utils import * 

# Directory for saving properly converted WAV files
CONVERTED_AUDIO_DIR = "uploads/converted_wav"
os.makedirs(CONVERTED_AUDIO_DIR, exist_ok=True)

# --- Helper Functions ---
def convert_to_wav(file_path):
    """
    Converts any audio file to a proper WAV format (PCM 16-bit, 16kHz, mono).
    Saves the converted file and returns the new file path.
    """
    try:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None
        filename = os.path.splitext(os.path.basename(file_path))[0]
        converted_path = os.path.join(CONVERTED_AUDIO_DIR, f"{filename}_converted.wav")
        print("⚠️ Converting audio to proper WAV format...")
        # Convert using pydub
        audio = AudioSegment.from_file(file_path)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        # Save properly formatted WAV file
        audio.export(converted_path, format="wav")
        print(f"✅ Converted and saved WAV file: {converted_path}")
        return converted_path
    except Exception as e:
        print(f"❌ Error converting audio: {e}")
        return None

def load_embedding(embedding_id, folder):
    """
    Load an embedding (.npy file) for a given embedding ID from the specified folder.
    """
    file_path = os.path.join(folder, f"{embedding_id}.npy")
    if not os.path.exists(file_path):
        print(f"❌ Embedding file not found: {file_path}")
        return None
    return np.load(file_path)

def compute_prod_diff(enroll_embedding, trial_embedding):
    """
    Compute the element-wise product and absolute difference between two embeddings.
    
    Returns:
      prod: Sum of element-wise product.
      diff: Sum of absolute differences.
    """
    prod = np.sum(enroll_embedding * trial_embedding)
    diff = np.sum(np.abs(enroll_embedding - trial_embedding))
    return prod, diff

def compute_manhattan(enroll_embedding, trial_embedding):
    """
    Compute the Manhattan (L1) distance between two embeddings.
    
    Returns:
      A scalar representing the Manhattan distance.
    """
    return np.sum(np.abs(enroll_embedding - trial_embedding))

def compute_similarity(embedding1, embedding2):
    """Computes cosine similarity between two embeddings."""
    similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    return similarity

# --- Main Function ---
def validateTrial(speaker_name, trialAudio, text, voiceprint_extractor, prosody_extractor):
    """
    Validate a trial audio against a speaker's enrollment embeddings.
    
    Steps:
      1. Load speaker's voiceprint and prosody enrollment embeddings.
      2. Extract trial embeddings for both modalities using the respective extractors.
      3. Compute product and difference features for each modality.
      4. Compute the Manhattan distance for the voiceprint embeddings.
      5. Concatenate all computed features into a feature vector.
      6. Make a prediction based on combined features.
    
    Args:
      speaker_name (str): Identifier for the speaker.
      trialAudio (str): File path for the trial audio.
      text (str): The text that should be spoken in the audio.
      
    Returns:
      is_valid_speaker (bool): True if the speaker is verified, False otherwise.
    """
    print(f"🔹 Validating trial for speaker: {speaker_name}")
    
    # Define embeddings folder paths
    voiceprint_folder = "demo/embeddings/combined_speaker_embeddings/voiceprint"
    prosody_folder = "demo/embeddings/combined_speaker_embeddings/prosody"
    
    # Load enrollment embeddings for the speaker (for both modalities)
    speaker_voiceprint = load_embedding(speaker_name, voiceprint_folder)
    speaker_prosody = load_embedding(speaker_name, prosody_folder)
    
    if speaker_voiceprint is None or speaker_prosody is None:
        print("❌ Missing speaker embeddings. Verification failed.")
        return False
    
    # Make sure embeddings are flattened vectors
    speaker_voiceprint = speaker_voiceprint.squeeze()
    speaker_prosody = speaker_prosody.squeeze()
    
    print(f"✅ Loaded speaker embeddings with shapes: {speaker_voiceprint.shape}, {speaker_prosody.shape}")
    
    # Convert trial audio to WAV format
    converted_trialAudio = convert_to_wav(trialAudio)
    if converted_trialAudio is None:
        print("❌ Audio conversion failed. Exiting function.")
        return False
    
    scaler = joblib.load("scaler.pkl")

    print("Scaler mean:", scaler.mean_)
    print("Scaler scale:", scaler.scale_)

    # Check if the scaler is effectively an identity transform
    if np.allclose(scaler.mean_, 0, atol=1e-5) and np.allclose(scaler.scale_, 1, atol=1e-5):
        print("Warning: The scaler appears to be an identity transform. Your training data may already be normalized.")
    else:
        print("Scaler parameters look as expected.")

    # For cluster
    with open("umap_model_demo.pkl", "rb") as f:
        umap_data = pickle.load(f)

    umap_model_demo = umap_data["umap_model"]
    speaker_cluster_mapping_demo = umap_data["speaker_cluster_mapping"]
    cluster_centroids_demo = umap_data["cluster_centroids"]

    # Model
    speaker_validation_model = joblib.load("model_final.pkl")
    
    try:
        # Extract trial embeddings from the trial audio
        # For voiceprint, we need to load and preprocess the audio
        audio = voiceprint_extractor.load_audio(converted_trialAudio)
        audio_tensor = voiceprint_extractor.preprocess_audio(audio)
        trial_voiceprint = voiceprint_extractor.extract_embedding(audio_tensor)
        
        # For prosody, we need the converted audio and the text
        trial_prosody = prosody_extractor.get_prosody_embedding(converted_trialAudio, text)
        
        print(f"✅ Trial embeddings extracted with shapes: {trial_voiceprint.shape}, {trial_prosody.shape}")
        
        # Compute product and difference features for both voiceprint and prosody embeddings
        vp_prod, vp_diff = compute_prod_diff(speaker_voiceprint, trial_voiceprint)
        pr_prod, pr_diff = compute_prod_diff(speaker_prosody, trial_prosody)
        
        # Compute Manhattan (L1) distance for voiceprint embeddings
        vp_manhattan = compute_manhattan(speaker_voiceprint, trial_voiceprint)

        cluster_match = get_cluster_match(speaker_name, trial_voiceprint, umap_model_demo, speaker_cluster_mapping_demo, cluster_centroids_demo)
        
        # Concatenate all computed features into a single feature vector
        feature_vector = np.concatenate([
            np.array([vp_prod]),
            np.array([vp_diff]),
            np.array([pr_prod]),
            np.array([pr_diff]),
            np.array([vp_manhattan]),
            np.array([cluster_match])
        ])
        print(f"Feature vector before scaling: {feature_vector}")

        # Reshape the feature vector to 2D (1 sample with 6 features)
        feature_vector = feature_vector.reshape(1, -1)

        # Scale the feature vector using the pre-loaded scaler
        feature_vector = scaler.transform(feature_vector)
        print(f"✅ Feature vector after pre-loaded scaler: {feature_vector}")

        # Define a shift variable for the first 5 features (the 6th feature remains unchanged)
        shift = np.array([18.83, 8.48, 0.82, 3.42, 8.48])

        # Apply the shift: subtract the shift values from the first five features
        feature_vector[:, :5] = feature_vector[:, :5] - shift
        print(f"Feature vector after shift: {feature_vector}")

        # Predict using the speaker validation model
        predictions = speaker_validation_model.predict(feature_vector)
        print(predictions)

        is_valid_speaker = int(predictions[0])

        print(f"✅ Speaker Validation Result: {'Verified ✓' if is_valid_speaker else 'Not Verified ✗'}")
        
        return is_valid_speaker
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False