import os
import shutil
import numpy as np
from tqdm import tqdm 
from tacatron import TacatronProsodyExtractor
from ecapa_tdnn import ECAPAVoiceprintExtractor
from sentences import sentences  # Assumes this is a list of texts for the audios

def save_audios(audios, name, output_folder):
    """
    Saves exactly 20 audio files to the output folder with filenames formatted as [name]-001.wav, [name]-002.wav, etc.
    
    Args:
        audios (list): List of file paths to the 20 audio files.
        name (str): The base name to use for the output files.
        output_folder (str): The directory where the audio files will be saved.
        
    Raises:
        ValueError: If the number of audio files provided is not 20.
        
    Returns:
        list: List of full paths to the saved audio files in the output folder.
    """
    if len(audios) != 20:
        raise ValueError("Expected exactly 20 audio files.")
    
    os.makedirs(output_folder, exist_ok=True)
    saved_files = []
    
    for i, audio_path in enumerate(audios, start=1):
        new_filename = f"{name}-{i:03d}.wav"
        destination_path = os.path.join(output_folder, new_filename)
        shutil.copy(audio_path, destination_path)
        print(f"Saved {audio_path} as {destination_path}")
        saved_files.append(destination_path)
        
    return saved_files

def combine_embeddings(name, input_folder, output_folder):
    """
    Combines embeddings for files in the input folder that start with the given name and
    have the .npy extension. The function loads all matching embeddings, averages them,
    and saves the average embedding to the output folder as [name].npy.
    
    Args:
        name (str): The base name to filter files (e.g., 'munir').
        input_folder (str): Directory containing the .npy embedding files.
        output_folder (str): Directory where the combined embedding will be saved.
        
    Returns:
        np.ndarray or None: The averaged embedding, or None if no embeddings were found.
    """
    os.makedirs(output_folder, exist_ok=True)
    embeddings = []
    
    for file in os.listdir(input_folder):
        if file.startswith(f"{name}-") and file.endswith('.npy'):
            file_path = os.path.join(input_folder, file)
            try:
                embedding = np.load(file_path)
                embeddings.append(embedding)
            except Exception as e:
                print(f"Error loading file {file_path}: {e}")
    
    if embeddings:
        avg_embedding = np.mean(np.vstack(embeddings), axis=0)
        output_file = os.path.join(output_folder, f"{name}.npy")
        np.save(output_file, avg_embedding)
        print(f"Saved average embedding for '{name}' to {output_file}")
        return avg_embedding
    else:
        print(f"No embeddings found for name '{name}' in {input_folder}")
        return None

def process_speaker_embedding(base_name, audio_files):
    """
    Processes speaker embeddings by performing the following:
      1. Save and rename 20 audio files using the provided base name.
      2. Extract voiceprint enrollment embeddings using a batch extraction method.
      3. Extract prosody embeddings for each audio file.
      4. Combine the extracted embeddings for both voiceprint and prosody.
      5. (Placeholder) Add clustering logic with the combined embeddings.
    
    Args:
      base_name (str): The base name/identifier for the speaker (e.g., 'munir').
      audio_files (list): List of 20 file paths to the speaker's audio files.
    
    Returns:
      None
    """

    output_dir = "demo/wav" # Directory where the renamed audio files will be saved.
    voiceprint_embeddings_folder = "demo/embeddings/speaker_embeddings/voiceprint" # Folder where voiceprint embeddings will be saved.
    prosody_embeddings_folder = "demo/embeddings/speaker_embeddings/prosody" # Folder where prosody embeddings will be saved.
    voiceprint_combined_embeddings_folder = "demo/embeddings/combined_speaker_embeddings/voiceprint" # Folder to save the combined voiceprint embedding.
    prosody_combined_embeddings_folder = "demo/embeddings/combined_speaker_embeddings/prosody" # Folder to save the combined prosody embedding.

    # Save and rename audio files
    saved_audio_files = save_audios(audio_files, base_name, output_dir)
    
    # Extract voiceprint enrollment embeddings (batch processing)
    enroll_embeddings = voiceprint_extractor.process_files(saved_audio_files, voiceprint_embeddings_folder)
    print("Voiceprint embeddings extracted and saved successfully!")
    
    # Extract prosody embeddings for each audio file
    for i in range(len(saved_audio_files)):
        audio_path = saved_audio_files[i]
        # Adjust index for sentences if needed (assuming sentences is a list with 20 items)
        text = sentences[i]
        
        embedding = prosody_extractor.get_prosody_embedding(audio_path, text)
        base_filename = os.path.basename(audio_path)
        npy_filename = base_filename.replace('.wav', '.npy')
        output_path = os.path.join(prosody_embeddings_folder, npy_filename)
        np.save(output_path, embedding)
        print(f"Saved prosody embedding for {audio_path} as {output_path}")
    
    # Combine embeddings for voiceprint and prosody
    combine_embeddings(base_name, voiceprint_embeddings_folder, voiceprint_combined_embeddings_folder)
    combine_embeddings(base_name, prosody_embeddings_folder, prosody_combined_embeddings_folder)
    
    # Placeholder: Add clustering logic here
    # TODO: Implement clustering process with the combined embeddings.
    print("Clustering placeholder: Add clustering logic here.")
    
    # Optionally, return some output or simply finish processing.
    return

# Example usage:
if __name__ == "__main__":
    # Define input parameters
    audio_files = [f"/path/to/audio_{i}.wav" for i in range(1, 21)]
    base_name = "munir"
    
    # Process speaker embeddings and run placeholder clustering
    process_speaker_embedding(base_name, audio_files)
