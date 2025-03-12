import os
import numpy as np
from tqdm import tqdm  # Import tqdm for progress bar
from tacatron import TacatronProsodyExtractor
from ecapa_tdnn import ECAPAVoiceprintExtractor
from sentences import sentences
import os
import shutil
import os
import numpy as np

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

    # Ensure the output folder exists.
    os.makedirs(output_folder, exist_ok=True)
    
    saved_files = []
    # Iterate over the audio files and copy them with the new naming scheme.
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
    # Ensure the output folder exists.
    os.makedirs(output_folder, exist_ok=True)
    
    embeddings = []
    
    # Loop over all files in the input folder.
    for file in os.listdir(input_folder):
        # Check if file starts with the provided name and ends with .npy
        if file.startswith(f"{name}-") and file.endswith('.npy'):
            file_path = os.path.join(input_folder, file)
            try:
                embedding = np.load(file_path)
                embeddings.append(embedding)
            except Exception as e:
                print(f"Error loading file {file_path}: {e}")
    
    if embeddings:
        # Stack embeddings into a 2D array and average along the first axis.
        avg_embedding = np.mean(np.vstack(embeddings), axis=0)
        output_file = os.path.join(output_folder, f"{name}.npy")
        np.save(output_file, avg_embedding)
        print(f"Saved average embedding for '{name}' to {output_file}")
        return avg_embedding
    else:
        print(f"No embeddings found for name '{name}' in {input_folder}")
        return None


audio_files = [f"/path/to/audio_{i}.wav" for i in range(1, 21)]
base_name = "munir"
output_dir = "demo\wav"
audio_folder = "demo\wav"
voiceprint_embeddings_folder = "demo\embeddings\speaker_embeddings"
prosody_embeddings_folder = "demo\embeddings\speaker_embeddings"
voiceprint_combined_embeddings_folder = "demo\embeddings\combined_speaker_embeddings"
prosody_combined_embeddings_folder = "demo\embeddings\combined_speaker_embeddings"

# Save and rename audio
audio_files = save_audios(audio_files, base_name, output_dir)

# Create an instance of the extractor and process files
voiceprint_extractor = ECAPAVoiceprintExtractor()
enroll_embeddings = voiceprint_extractor.process_files(audio_files, voiceprint_embeddings_folder)

print("Embeddings extracted and saved successfully!")

prosody_extractor = TacatronProsodyExtractor(use_cuda=False)
    
for i in range(1, 21):
    audio_path = audio_files[i]
    text = sentences[i]

    embedding = prosody_extractor.get_prosody_embedding(audio_path, text)

    # Construct the output filename: replace '.wav' with '.npy'
    base_filename = os.path.basename(audio_path)
    npy_filename = base_filename.replace('.wav', '.npy')
    output_path = os.path.join(prosody_embeddings_folder, npy_filename)

    # Save the embedding as a NumPy .npy file.
    np.save(output_path, embedding)

# Combine embeddings for voice print and prosody
combine_embeddings(base_name, voiceprint_embeddings_folder, voiceprint_combined_embeddings_folder)
combine_embeddings(base_name, prosody_embeddings_folder, prosody_combined_embeddings_folder)




