############## THIS IS FOR COSINE SIMILARITY #####################################


# import os
# import numpy as np
# import torch
# from pydub import AudioSegment
# from tacatron import TacatronProsodyExtractor
# from ecapa_tdnn import ECAPAVoiceprintExtractor

# # Directory for saving properly converted WAV files
# CONVERTED_AUDIO_DIR = "uploads/converted_wav"
# os.makedirs(CONVERTED_AUDIO_DIR, exist_ok=True)

# # --- Helper Functions ---
# def convert_to_wav(file_path):
#     """
#     Converts any audio file to a proper WAV format (PCM 16-bit, 16kHz, mono).
#     Saves the converted file and returns the new file path.
#     """
#     try:
#         if not os.path.exists(file_path):
#             print(f"❌ File not found: {file_path}")
#             return None
#         filename = os.path.splitext(os.path.basename(file_path))[0]
#         converted_path = os.path.join(CONVERTED_AUDIO_DIR, f"{filename}_converted.wav")
#         print("⚠️ Converting audio to proper WAV format...")
#         # Convert using pydub
#         audio = AudioSegment.from_file(file_path)
#         audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
#         # Save properly formatted WAV file
#         audio.export(converted_path, format="wav")
#         print(f"✅ Converted and saved WAV file: {converted_path}")
#         return converted_path
#     except Exception as e:
#         print(f"❌ Error converting audio: {e}")
#         return None

# def compute_similarity(embedding1, embedding2):
#     """Computes cosine similarity between two embeddings."""
#     similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
#     return similarity

# # --- Main Function ---
# def validateTrial(speaker_name, trialAudio, text):
#     """
#     Validates a trial audio by comparing its extracted embedding to the stored speaker embedding.
    
#     Returns:
#     - `True` if the speaker is verified.
#     - `False` otherwise.
#     """
#     print(f"🔹 Validating trial for speaker: {speaker_name}")
    
#     # Load stored `.npy` embedding for this speaker
#     embedding_folder = "demo/embeddings/combined_speaker_embeddings/voiceprint"
#     speaker_embedding_path = os.path.join(embedding_folder, f"{speaker_name}.npy")
    
#     if not os.path.exists(speaker_embedding_path):
#         print(f"❌ No stored embedding found for speaker: {speaker_name}")
#         return False
    
#     speaker_embedding = np.load(speaker_embedding_path)
#     print(f"✅ Loaded speaker embedding with shape: {speaker_embedding.shape}")
    
#     # Convert trial audio to WAV format
#     converted_trialAudio = convert_to_wav(trialAudio)
#     if converted_trialAudio is None:
#         print("❌ Audio conversion failed. Exiting function.")
#         return False
    
#     # Initialize the voice print extractor
#     voiceprint_extractor = ECAPAVoiceprintExtractor()
    
#     # Process the trial audio directly using the ECAPAVoiceprintExtractor
#     try:
#         # Load and preprocess audio using the extractor's methods
#         audio = voiceprint_extractor.load_audio(converted_trialAudio)
#         audio_tensor = voiceprint_extractor.preprocess_audio(audio)
        
#         # Extract embedding
#         trial_embedding = voiceprint_extractor.extract_embedding(audio_tensor)
#         print(f"✅ Trial voiceprint embedding extracted with shape: {trial_embedding.shape}")
        
#         # Compare stored speaker embedding with extracted trial embedding
#         similarity = compute_similarity(speaker_embedding, trial_embedding)
#         print(f"✅ Cosine Similarity: {similarity:.4f}")
        
#         # Use a threshold for speaker verification
#         THRESHOLD = 0.6  
#         is_valid_speaker = bool(similarity >= THRESHOLD)  # Convert NumPy bool_ to Python bool
#         print(f"✅ Speaker Validation Result: {'Verified ✓' if is_valid_speaker else 'Not Verified ✗'}")
        
#         return is_valid_speaker
        
#     except Exception as e:
#         print(f"❌ Error during validation: {e}")
#         return False




############## THIS IS FOR MANHATTEN DISTANCE ETC #####################################



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
def validateTrial(speaker_name, trialAudio, text):
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
    
    # For scaling new data using X_train data
    scaler = joblib.load("scaler.pkl")

    # For cluster
    with open("umap_model_demo.pkl", "rb") as f:
        umap_data = pickle.load(f)

    umap_model_demo = umap_data["umap_model"]
    speaker_cluster_mapping_demo = umap_data["speaker_cluster_mapping"]
    cluster_centroids_demo = umap_data["cluster_centroids"]

    # Model
    speaker_validation_model = joblib.load("model_final.pkl")
    
    try:
        # Instantiate extractors
        voiceprint_extractor = ECAPAVoiceprintExtractor() 
        prosody_extractor = TacatronProsodyExtractor(use_cuda=False)
        
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

        feature_vector = scaler.transform(feature_vector)
    
        print(f"✅ Feature vector: {feature_vector}")

        predictions = speaker_validation_model.predict(feature_vector.reshape(1, -1))

        is_valid_speaker = int(predictions[0])

        print(f"✅ Speaker Validation Result: {'Verified ✓' if is_valid_speaker else 'Not Verified ✗'}")
        
        return is_valid_speaker
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False