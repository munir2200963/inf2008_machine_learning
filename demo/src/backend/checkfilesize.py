import numpy as np
import os

# Paths to embeddings
voiceprint_embedding_path = "demo/embeddings/combined_speaker_embeddings/voiceprint/huang.npy"
prosody_embedding_path = "demo/embeddings/combined_speaker_embeddings/prosody/huang.npy"

# Load the embeddings
voiceprint_embedding = np.load(voiceprint_embedding_path, allow_pickle=True)
prosody_embedding = np.load(prosody_embedding_path, allow_pickle=True)

# Print shape & type
print(f"📏 Voiceprint Embedding Shape: {voiceprint_embedding.shape}, Type: {type(voiceprint_embedding)}")
print(f"📏 Prosody Embedding Shape: {prosody_embedding.shape}, Type: {type(prosody_embedding)}")

# Check a small sample of values
print(f"🧐 Sample Voiceprint Values: {voiceprint_embedding[:20]}")
print(f"🧐 Sample Prosody Values: {prosody_embedding[:20]}")
