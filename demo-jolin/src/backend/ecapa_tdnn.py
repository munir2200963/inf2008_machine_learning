import os
import torch
import torchaudio
import librosa
import numpy as np
from speechbrain.pretrained import EncoderClassifier

class ECAPAVoiceprintExtractor:
    def __init__(self, 
                 model_source="speechbrain/spkrec-ecapa-voxceleb", 
                 model_dir="pretrained_models/spkrec-ecapa-voxceleb",
                 sample_rate=16000):
        """
        Initialize the extractor by loading the pre-trained model and setting parameters.
        
        Args:
            model_source (str): Path or identifier for the pre-trained model.
            model_dir (str): Directory to store the pre-trained model.
            sample_rate (int): Target sample rate for audio processing.
        """
        self.sample_rate = sample_rate
        self.classifier = EncoderClassifier.from_hparams(
            source=model_source,
            savedir=model_dir
        )
        
    def load_audio(self, file_path):
        """
        Load an audio file and resample to the target sample rate.
        
        Args:
            file_path (str): Path to the audio file.
        
        Returns:
            np.ndarray: Loaded audio data.
        """
        audio, sr = librosa.load(file_path, sr=self.sample_rate)
        return audio

    def preprocess_audio(self, audio):
        """
        Convert the audio signal to a PyTorch tensor and add a batch dimension.
        
        Args:
            audio (np.ndarray): Audio data.
        
        Returns:
            torch.Tensor: Preprocessed audio tensor.
        """
        audio_tensor = torch.tensor(audio).unsqueeze(0)
        return audio_tensor

    def extract_embedding(self, audio_tensor):
        """
        Extract embeddings from the audio tensor using the pre-trained model.
        
        Args:
            audio_tensor (torch.Tensor): Preprocessed audio tensor.
        
        Returns:
            np.ndarray: Extracted embedding.
        """
        with torch.no_grad():
            embeddings = self.classifier.encode_batch(audio_tensor)
        # Remove extra dimensions and convert to numpy array
        return embeddings.squeeze().numpy()

    def process_files(self, file_list, output_folder):
        """
        Process a list of audio files to extract and save embeddings.
        
        Args:
            file_list (list): List of audio file paths.
            output_folder (str): Directory where embeddings will be saved.
        
        Returns:
            dict: A dictionary mapping filenames to embeddings.
        """
        os.makedirs(output_folder, exist_ok=True)
        embeddings_dict = {}
        for file_path in file_list:
            # Load and preprocess audio
            audio = self.load_audio(file_path)
            audio_tensor = self.preprocess_audio(audio)
            
            # Extract embedding
            embedding = self.extract_embedding(audio_tensor)
            
            # Save the embedding using the same filename as the audio file
            file_name = os.path.basename(file_path).replace('.wav', '.npy')
            output_path = os.path.join(output_folder, file_name)
            np.save(output_path, embedding)
            
            # Optionally store embedding in dictionary
            embeddings_dict[file_name] = embedding
        
        return embeddings_dict

# Example usage:
if __name__ == "__main__":
    # Define folders
    enroll_folder = "uploads/"
    output_folder = "demo/embeddings/speaker_embeddings/voiceprint"

    # List all .wav files in the enroll folder
    enroll_files = [os.path.join(enroll_folder, f) for f in os.listdir(enroll_folder) if f.endswith('.wav')]

    print(f"Found {len(enroll_files)} enroll files.")

    # Create an instance of the extractor and process files
    extractor = ECAPAVoiceprintExtractor()
    enroll_embeddings = extractor.process_files(enroll_files, output_folder)

    print("Embeddings extracted and saved successfully!")
    print("Enroll Embeddings:", os.listdir(output_folder))

