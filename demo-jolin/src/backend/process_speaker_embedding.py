# import os
# import shutil
# import numpy as np
# from tqdm import tqdm  # Optional: Shows a progress bar
# from tacatron import TacatronProsodyExtractor
# from ecapa_tdnn import ECAPAVoiceprintExtractor
# from sentences import sentences  # Import the sentence list

# # Initialize Extractors
# voiceprint_extractor = ECAPAVoiceprintExtractor()
# prosody_extractor = TacatronProsodyExtractor(use_cuda=False)

# def save_audios(audios, user_id, output_folder):
#     """
#     Saves exactly 20 audio files to the output folder with formatted filenames.
#     """
#     if len(audios) != 20:
#         raise ValueError("Expected exactly 20 audio files.")
    
#     os.makedirs(output_folder, exist_ok=True)
#     saved_files = []

#     for i, audio_path in enumerate(audios, start=1):
#         new_filename = f"{user_id}-{i:03d}.wav"
#         destination_path = os.path.join(output_folder, new_filename)
#         shutil.copy(audio_path, destination_path)
#         print(f"✅ Saved: {audio_path} as {destination_path}")
#         saved_files.append(destination_path)
    
#     return saved_files

# def combine_embeddings(user_id, input_folder, output_folder):
#     """
#     Combines embeddings by averaging all .npy embeddings found in the input folder.
#     """
#     os.makedirs(output_folder, exist_ok=True)
#     embeddings = []

#     for file in os.listdir(input_folder):
#         if file.startswith(f"{user_id}-") and file.endswith('.npy'):
#             file_path = os.path.join(input_folder, file)
#             try:
#                 embedding = np.load(file_path, allow_pickle=True)  # ✅ Fix: allow_pickle=True
#                 embeddings.append(embedding)
#             except Exception as e:
#                 print(f"⚠️ Error loading file {file_path}: {e}")

#     if embeddings:
#         avg_embedding = np.mean(np.vstack(embeddings), axis=0)
#         output_file = os.path.join(output_folder, f"{user_id}.npy")
#         np.save(output_file, avg_embedding)
#         print(f"✅ Saved average embedding for '{user_id}' to {output_file}")
#         return avg_embedding
#     else:
#         print(f"⚠️ No embeddings found for user '{user_id}' in {input_folder}")
#         return None

# def process_speaker_embedding(user_id, audio_files):
#     """
#     Processes speaker embeddings by:
#       1. Saving & renaming 20 audio files.
#       2. Extracting voiceprint & prosody embeddings.
#       3. Combining embeddings for clustering.
#     """

#     # Define folders
#     output_dir = "demo/wav"
#     voiceprint_embeddings_folder = "demo/embeddings/speaker_embeddings/voiceprint"
#     prosody_embeddings_folder = "demo/embeddings/speaker_embeddings/prosody"
#     voiceprint_combined_embeddings_folder = "demo/embeddings/combined_speaker_embeddings/voiceprint"
#     prosody_combined_embeddings_folder = "demo/embeddings/combined_speaker_embeddings/prosody"

#     # Ensure folders exist
#     os.makedirs(output_dir, exist_ok=True)
#     os.makedirs(voiceprint_embeddings_folder, exist_ok=True)
#     os.makedirs(prosody_embeddings_folder, exist_ok=True)
#     os.makedirs(voiceprint_combined_embeddings_folder, exist_ok=True)
#     os.makedirs(prosody_combined_embeddings_folder, exist_ok=True)

#     # ✅ Save and rename audio files
#     saved_audio_files = save_audios(audio_files, user_id, output_dir)

#     # ✅ Extract voiceprint enrollment embeddings
#     enroll_embeddings = voiceprint_extractor.process_files(saved_audio_files, voiceprint_embeddings_folder)
#     print("✅ Voiceprint embeddings extracted and saved!")

#     # ✅ Extract prosody embeddings
#     for i, audio_path in enumerate(saved_audio_files):
#         if i < len(sentences):  # Ensure index is within bounds
#             text = sentences[i]

#             # Extract prosody embedding
#             embedding = prosody_extractor.get_prosody_embedding(audio_path, text)

#             # Debugging: Print shape of extracted embeddings
#             if isinstance(embedding, np.ndarray):
#                 print(f"🔍 Debug: Prosody embedding shape for {audio_path}: {embedding.shape}")
#             else:
#                 print(f"⚠️ Warning: Unexpected type for {audio_path}: {type(embedding)}")

#             # ✅ Check for 'capacitron_vae_outputs' before accessing
#             if isinstance(embedding, dict) and "outputs" in embedding and "capacitron_vae_outputs" in embedding["outputs"]:
#                 capacitron_vae_outputs = embedding["outputs"]["capacitron_vae_outputs"]
#             else:
#                 print(f"⚠️ Warning: 'capacitron_vae_outputs' missing for {audio_path}. Using fallback.")
#                 capacitron_vae_outputs = np.random.normal(0, 0.1, (128,))  # ✅ Fix: Use fallback random noise instead of None

#             # Convert to NumPy array before saving
#             capacitron_vae_outputs = np.array(capacitron_vae_outputs)

#             # Save embedding as .npy
#             base_filename = os.path.basename(audio_path)
#             npy_filename = base_filename.replace('.wav', '.npy')
#             output_path = os.path.join(prosody_embeddings_folder, npy_filename)
#             np.save(output_path, capacitron_vae_outputs)
#             print(f"✅ Saved prosody embedding for {audio_path} as {output_path}")
#         else:
#             print(f"⚠️ No sentence found for audio index {i}")

#     # ✅ Combine embeddings
#     combine_embeddings(user_id, voiceprint_embeddings_folder, voiceprint_combined_embeddings_folder)
#     combine_embeddings(user_id, prosody_embeddings_folder, prosody_combined_embeddings_folder)

#     # 🚀 Placeholder for clustering
#     print("⚡ Clustering placeholder: Add clustering logic here.")

#     return

# # Example Usage (For testing in standalone mode)
# if __name__ == "__main__":
#     user_id = "huang"  # Dynamically set based on form input
#     audio_files = [f"uploads/{user_id}_audio_{i}.wav" for i in range(20)]

#     # Process embeddings
#     process_speaker_embedding(user_id, audio_files)

import os
import shutil
import numpy as np
from tqdm import tqdm 
import pickle
from tacatron import TacatronProsodyExtractor
from ecapa_tdnn import ECAPAVoiceprintExtractor
from sentences import sentences 
from clustering_utils import * 


# Initialize Extractors
voiceprint_extractor = ECAPAVoiceprintExtractor()
prosody_extractor = TacatronProsodyExtractor(use_cuda=False)

def save_audios(audios, user_id, output_folder):
    """
    Saves exactly 20 audio files to the output folder with filenames formatted as [user_id]-001.wav, [user_id]-002.wav, etc.
    """
    if len(audios) != 20:
        raise ValueError("Expected exactly 20 audio files.")
    
    os.makedirs(output_folder, exist_ok=True)
    saved_files = []
    
    for i, audio_path in enumerate(audios, start=1):
        new_filename = f"{user_id}-{i:03d}.wav"
        destination_path = os.path.join(output_folder, new_filename)
        shutil.copy(audio_path, destination_path)
        print(f"Saved {audio_path} as {destination_path}")
        saved_files.append(destination_path)
        
    return saved_files

def combine_embeddings(user_id, input_folder, output_folder):
    """
    Combines embeddings for files in the input folder that start with the given user_id and
    have the .npy extension. The function loads all matching embeddings, averages them,
    and saves the average embedding to the output folder as [user_id].npy.
    """
    os.makedirs(output_folder, exist_ok=True)
    embeddings = []
    
    for file in os.listdir(input_folder):
        if file.startswith(f"{user_id}-") and file.endswith('.npy'):
            file_path = os.path.join(input_folder, file)
            try:
                embedding = np.load(file_path)
                embeddings.append(embedding)
            except Exception as e:
                print(f"Error loading file {file_path}: {e}")
    
    if embeddings:
        avg_embedding = np.mean(np.vstack(embeddings), axis=0)
        output_file = os.path.join(output_folder, f"{user_id}.npy")
        np.save(output_file, avg_embedding)
        print(f"Saved average embedding for '{user_id}' to {output_file}")
        return avg_embedding
    else:
        print(f"No embeddings found for user_id '{user_id}' in {input_folder}")
        return None

def process_speaker_embedding(user_id, audio_files):
    """
    Processes speaker embeddings:
      1. Save and rename 20 audio files using the provided user_id.
      2. Extract voiceprint enrollment embeddings using a batch extraction method.
      3. Extract prosody embeddings for each audio file.
      4. Combine the extracted embeddings for both voiceprint and prosody.
      5. Placeholder for clustering logic.
    """
    output_dir = "demo/wav"
    voiceprint_embeddings_folder = "demo/embeddings/speaker_embeddings/voiceprint"
    prosody_embeddings_folder = "demo/embeddings/speaker_embeddings/prosody"
    voiceprint_combined_embeddings_folder = "demo/embeddings/combined_speaker_embeddings/voiceprint"
    prosody_combined_embeddings_folder = "demo/embeddings/combined_speaker_embeddings/prosody"
    
    # Save and rename audio files
    saved_audio_files = save_audios(audio_files, user_id, output_dir)
    
    # Extract voiceprint enrollment embeddings (batch processing)
    enroll_embeddings = voiceprint_extractor.process_files(saved_audio_files, voiceprint_embeddings_folder)
    print("Voiceprint embeddings extracted and saved successfully!")
    
    # Extract prosody embeddings for each audio file
    for i in range(len(saved_audio_files)):
        audio_path = saved_audio_files[i]
        text = sentences[i]  # Assuming sentences is a list with 20 items
        
        embedding = prosody_extractor.get_prosody_embedding(audio_path, text)
        base_filename = os.path.basename(audio_path)
        npy_filename = base_filename.replace('.wav', '.npy')
        output_path = os.path.join(prosody_embeddings_folder, npy_filename)
        np.save(output_path, embedding)
        print(f"Saved prosody embedding for {audio_path} as {output_path}")
    
    # Combine embeddings for voiceprint and prosody
    combine_embeddings(user_id, voiceprint_embeddings_folder, voiceprint_combined_embeddings_folder)
    combine_embeddings(user_id, prosody_embeddings_folder, prosody_combined_embeddings_folder)
    
    # Compute clusters
    umap_model_demo, speaker_cluster_mapping_demo, cluster_centroids_demo = process_enroll_data(voiceprint_embeddings_folder, voiceprint_embeddings_folder)

    # Save the UMAP model, speaker cluster mapping, and cluster centroids to a file
    with open("umap_model_demo.pkl", "wb") as f:
        pickle.dump({
            "umap_model": umap_model_demo,
            "speaker_cluster_mapping": speaker_cluster_mapping_demo,
            "cluster_centroids": cluster_centroids_demo
        }, f)
    
    return

# Example usage:
if __name__ == "__main__":
    user_id = "huang"
    audio_files = [f"uploads/{user_id}_audio_{i}.wav" for i in range(20)]
    process_speaker_embedding(user_id, audio_files)