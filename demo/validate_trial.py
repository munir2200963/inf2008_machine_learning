import os
import numpy as np

from tacatron import TacatronProsodyExtractor
from ecapa_tdnn import ECAPAVoiceprintExtractor

# --- Helper Functions ---

def load_embedding(embedding_id, folder):
    """
    Load an embedding (.npy file) for a given embedding ID from the specified folder.
    """
    file_path = os.path.join(folder, f"{embedding_id}.npy")
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
      6. Add the feature vector to a cluster and send it to a model.
    
    Args:
      speaker_name (str): Identifier for the speaker.
      trialAudio (str): File path for the trial audio.
      
    Returns:
      model_result (int): The prediction result by model
    """
    # Define embeddings folder paths (update paths as needed)
    voiceprint_folder = "demo/embeddings/combined_speaker_embeddings/voiceprint"
    prosody_folder = "demo/embeddings/combined_speaker_embeddings/prosody"
    
    # Load enrollment embeddings for the speaker (for both modalities)
    speaker_voiceprint = load_embedding(speaker_name, voiceprint_folder).squeeze()
    speaker_prosody = load_embedding(speaker_name, prosody_folder).squeeze()
    
    # Instantiate extractors 
    voiceprint_extractor = ECAPAVoiceprintExtractor() 
    prosody_extractor = TacatronProsodyExtractor(use_cuda=False) 
    
    # Extract trial embeddings from the trial audio using placeholder methods
    trial_voiceprint = voiceprint_extractor.extract_embedding(trialAudio) 
    trial_prosody = prosody_extractor.get_prosody_embedding(trialAudio, text)  

    # Compute product and difference features for both voiceprint and prosody embeddings
    vp_prod, vp_diff = compute_prod_diff(speaker_voiceprint, trial_voiceprint)
    pr_prod, pr_diff = compute_prod_diff(speaker_prosody, trial_prosody)
    
    # Compute Manhattan (L1) distance for voiceprint embeddings
    vp_manhattan = compute_manhattan(speaker_voiceprint, trial_voiceprint)
    
    # Concatenate all computed features into a single feature vector
    feature_vector = np.concatenate([
        np.array([vp_prod]),
        np.array([vp_diff]),
        np.array([pr_prod]),
        np.array([pr_diff]),
        np.array([vp_manhattan])
    ])
    
    # Placeholder: Add the feature vector to a cluster
    # TODO: Implement clustering logic here
    # cluster_result = add_to_cluster(feature_vector)
    
    # Placeholder: Send the feature vector to a model for prediction
    # TODO: Implement model prediction logic here
    # model_result = send_to_model(feature_vector)
    model_result = 0 # Placeholder result

    return model_result