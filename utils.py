import os
import numpy as np
import pandas as pd
from tqdm import tqdm

# -------------------------------
# Helper Functions
# -------------------------------

def load_embedding(embedding_id, folder):
    """
    Load an embedding (.npy file) for a given embedding ID from the specified folder.
    """
    file_path = os.path.join(folder, f"{embedding_id}.npy")
    embedding = np.load(file_path)
    return embedding

def compute_prod_diff(enroll_embedding, trial_embedding):
    """
    Compute the element-wise product and absolute difference between two embeddings.
    Returns:
      prod: Element-wise product.
      diff: Absolute difference.
    """
    prod = enroll_embedding * trial_embedding
    diff = np.abs(enroll_embedding - trial_embedding)

    # Turning embeddings to scalar
    prod = np.sum(prod)
    diff = np.sum(diff)
    
    return prod, diff

def compute_manhattan(enroll_embedding, trial_embedding):
    """
    Compute the Manhattan (L1) distance between two embeddings.
    Returns:
      A scalar value representing the Manhattan distance.
    """
    return np.sum(np.abs(enroll_embedding - trial_embedding))

# -------------------------------
# Modular Feature Extraction Functions
# -------------------------------

def get_voiceprint_features(speaker_id, utterance_id, folder_paths, dataset):
    """
    Load voiceprint enrollment and trial embeddings, then compute product and difference features.
    
    Returns:
      vp_prod: Product of voiceprint embeddings.
      vp_diff: Absolute difference of voiceprint embeddings.
      vp_enroll_embedding: Enrollment embedding (for later Manhattan calculation).
      vp_trial_embedding: Trial embedding.
    """
    vp_enroll_folder = folder_paths[dataset]['voiceprint']['enroll_path']
    vp_trial_folder = folder_paths[dataset]['voiceprint']['trial_path']
    vp_enroll_embedding = load_embedding(speaker_id, vp_enroll_folder).squeeze()
    vp_trial_embedding = load_embedding(utterance_id, vp_trial_folder).squeeze()
    vp_prod, vp_diff = compute_prod_diff(vp_enroll_embedding, vp_trial_embedding)
    return vp_prod, vp_diff, vp_enroll_embedding, vp_trial_embedding

def get_prosody_features(speaker_id, utterance_id, folder_paths, dataset):
    """
    Load prosody enrollment and trial embeddings, then compute product and difference features.
    
    Returns:
      pr_prod: Product of prosody embeddings.
      pr_diff: Absolute difference of prosody embeddings.
    """
    pr_enroll_folder = folder_paths[dataset]['prosody']['enroll_path']
    pr_trial_folder = folder_paths[dataset]['prosody']['trial_path']
    pr_enroll_embedding = load_embedding(speaker_id, pr_enroll_folder).squeeze()
    pr_trial_embedding = load_embedding(utterance_id, pr_trial_folder).squeeze()
    pr_prod, pr_diff = compute_prod_diff(pr_enroll_embedding, pr_trial_embedding)

    return pr_prod, pr_diff

def compute_feature_vector(speaker_id, utterance_id, folder_paths, dataset):
    """
    Compute and concatenate feature vectors in a modular manner:
      1. Compute voiceprint product and difference.
      2. Compute prosody product and difference.
      3. Compute Manhattan distance for voiceprint embeddings.
      4. Concatenate all features in the following order:
         [voiceprint_prod, voiceprint_diff, prosody_prod, prosody_diff, voiceprint_manhattan].
    
    Returns:
      A single concatenated feature vector.
    """
    # Compute voiceprint features
    vp_prod, vp_diff, vp_enroll_embedding, vp_trial_embedding = get_voiceprint_features(
        speaker_id, utterance_id, folder_paths, dataset)
    
    # Compute prosody features
    pr_prod, pr_diff = get_prosody_features(speaker_id, utterance_id, folder_paths, dataset)
    
    # Compute Manhattan distance for voiceprint
    vp_manhattan = compute_manhattan(vp_enroll_embedding, vp_trial_embedding)

    # for scalar
    feature_vector = np.concatenate([
        np.array([vp_prod]),
        np.array([vp_diff]),
        np.array([pr_prod]),
        np.array([pr_diff]),
        np.array([vp_manhattan]),
    ])
    
    return feature_vector

# -------------------------------
# Main Processing Function
# -------------------------------

def process_trials_for_dataset(trial_df, dataset, folder_paths):
    """
    Process each trial row by computing the complete feature vector using the modular functions.
    Convert the trial label to binary (target -> 1, nontarget -> 0).
    
    Returns:
      X: Array of feature vectors.
      y: Array of binary labels.
    """
    X_list = []
    y_list = []
    
    for idx, row in tqdm(trial_df.iterrows(), total=len(trial_df), desc=f"Processing {dataset} trials"):
        speaker_id = str(row['Speaker_ID'])
        utterance_id = str(row['Utterance_ID'])
        label_str = str(row['Label'])
        
        # Compute feature vector (modular steps inside compute_feature_vector)
        feature_vector = compute_feature_vector(speaker_id, utterance_id, folder_paths, dataset)
        X_list.append(feature_vector)
        
        # Convert label to binary (target -> 1, nontarget -> 0)
        y_val = 1 if label_str.lower() == 'target' else 0
        y_list.append(y_val)
        
    X = np.array(X_list)
    y = np.array(y_list)
    return X, y