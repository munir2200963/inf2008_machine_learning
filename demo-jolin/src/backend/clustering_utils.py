import os
import numpy as np
import umap
import hdbscan
from collections import defaultdict, Counter
from sklearn.metrics.pairwise import cosine_similarity

###############################################
# Module 1: Enroll Data Processing & Clustering
###############################################

def load_enroll_data(enroll_folder_path):
    """
    Loads enroll embeddings from a folder of .npy files.
    Assumes each file is a 1D embedding of length 192 and the speaker ID is the first part of the filename (split by '-').
    
    Returns:
        X_enroll: numpy array of shape (n_samples, 192)
        enroll_speaker_ids: list of speaker IDs as strings
    """
    enroll_files = [os.path.join(enroll_folder_path, f) for f in os.listdir(enroll_folder_path) if f.endswith('.npy')]
    print(f"Found {len(enroll_files)} enroll files.")
    
    enroll_embeddings = []
    enroll_speaker_ids = []
    for file in enroll_files:
        emb = np.load(file)
        emb = np.squeeze(emb)  # Remove singleton dimensions
        enroll_embeddings.append(emb)
        base = os.path.basename(file)
        speaker_id = base.split('-')[0]
        enroll_speaker_ids.append(speaker_id)
    
    X_enroll = np.array(enroll_embeddings)
    print("Enroll embeddings shape:", X_enroll.shape)
    return X_enroll, enroll_speaker_ids

def reduce_embeddings_umap(X, n_components=2, random_state=42):
    """
    Reduces high-dimensional embeddings using UMAP.
    
    Returns:
        umap_model: fitted UMAP model.
        X_umap: the reduced embeddings.
    """
    umap_model = umap.UMAP(n_components=n_components, random_state=random_state)
    X_umap = umap_model.fit_transform(X)
    return umap_model, X_umap

def cluster_enroll_hdbscan(X_umap, min_cluster_size=5, min_samples=5):
    """
    Runs HDBSCAN on UMAP-projected enroll embeddings.
    
    Returns:
        hdbscan_labels: array of cluster labels.
    """
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples)
    hdbscan_labels = clusterer.fit_predict(X_umap)
    print("HDBSCAN labels:", hdbscan_labels)
    num_clusters = len(set(hdbscan_labels)) - (1 if -1 in hdbscan_labels else 0)
    print(f"Number of HDBSCAN clusters (excluding noise): {num_clusters}")
    return hdbscan_labels

def get_speaker_cluster_mapping(enroll_speaker_ids, hdbscan_labels):
    """
    For each speaker (from enroll data), computes the majority cluster label based on HDBSCAN labels.
    
    Returns:
        speaker_cluster_mapping: dict mapping speaker_id to majority cluster label.
    """
    speaker_to_labels = defaultdict(list)
    for speaker_id, label in zip(enroll_speaker_ids, hdbscan_labels):
        if label != -1:  # Consider only non-noise points.
            speaker_to_labels[speaker_id].append(label)
    speaker_cluster_mapping = {}
    for speaker_id, labels in speaker_to_labels.items():
        if labels:
            majority_label = Counter(labels).most_common(1)[0][0]
            speaker_cluster_mapping[speaker_id] = majority_label
    print("Speaker to Cluster Mapping (from enroll):")
    for speaker, cluster in speaker_cluster_mapping.items():
        print(f"Speaker {speaker}: Cluster {cluster}")
    return speaker_cluster_mapping

def compute_cluster_centroids(X_umap, hdbscan_labels):
    """
    Computes centroids in UMAP space for each cluster label (excluding noise).
    
    Returns:
        cluster_centroids: dict mapping cluster label to centroid (array of shape (2,)).
    """
    cluster_points = defaultdict(list)
    for point, label in zip(X_umap, hdbscan_labels):
        if label != -1:
            cluster_points[label].append(point)
    cluster_centroids = {label: np.mean(points, axis=0) for label, points in cluster_points.items()}
    return cluster_centroids

###############################################
# Module 2: Trial Processing & Feature Engineering
###############################################

def assign_cluster_to_trial(trial_embedding, umap_model, cluster_centroids):
    """
    Given a trial utterance embedding (192-dim), transforms it using the provided umap_model,
    then assigns it to the cluster whose centroid (in UMAP space) is most similar (via cosine similarity).
    
    Returns:
        assigned_label: the cluster label assigned to the trial utterance.
    """
    # Transform the trial embedding (reshape to (1, -1) as needed)
    X_trial_umap = umap_model.transform(trial_embedding.reshape(1, -1))
    best_label = None
    best_sim = -1
    for label, centroid in cluster_centroids.items():
        # Compute cosine similarity between trial UMAP and the centroid.
        sim = cosine_similarity(X_trial_umap, centroid.reshape(1, -1))[0, 0]
        if sim > best_sim:
            best_sim = sim
            best_label = label
    return best_label

def get_cluster_match(speaker_id, trial_embedding, umap_model, speaker_cluster_mapping, cluster_centroids):
    """
    Main function that computes the "Cluster Match" feature for a single trial utterance.
    
    Steps:
      1. Transform the trial embedding using the provided UMAP model.
      2. Assign the trial embedding to a cluster based on cosine similarity to enroll cluster centroids.
      3. Retrieve the majority cluster label for the given speaker (from enroll data).
      4. Return 1 if the trial's assigned cluster matches the speaker's enrolled cluster, else 0.
    
    Returns:
        cluster_match: 1 if match, 0 otherwise.
    """
    # Get the trial's assigned cluster
    trial_assigned_cluster = assign_cluster_to_trial(trial_embedding, umap_model, cluster_centroids)
    # Get the enroll (majority) cluster for this speaker
    enroll_cluster_for_speaker = speaker_cluster_mapping.get(speaker_id, -1)
    # Compare and return the binary feature
    cluster_match = 1 if trial_assigned_cluster == enroll_cluster_for_speaker else 0
    return cluster_match

def process_enroll_data(enroll_folder_path, test_folder_path):
    """
    Processes the enroll embeddings from two folders (enroll + test).
    1. Loads embeddings from both folders.
    2. Concatenates them.
    3. Reduces dimensionality with UMAP.
    4. Clusters the reduced data with HDBSCAN.
    5. Computes the majority cluster for each speaker and calculates cluster centroids.

    Args:
        enroll_folder_path (str): Path to the main enroll embeddings folder.
        test_folder_path   (str): Path to the test embeddings folder.

    Returns:
        umap_model (umap.UMAP): The fitted UMAP model.
        speaker_cluster_mapping (dict): Mapping from speaker ID to majority cluster label.
        cluster_centroids (dict): Mapping from cluster label to centroid in UMAP space.
    """

    # Load enroll data from test folder
    X_enroll1, enroll_speaker_ids1 = load_enroll_data(test_folder_path)

    # Load enroll data from enroll folder
    X_enroll2, enroll_speaker_ids2 = load_enroll_data(enroll_folder_path)

    # Combine the enroll embeddings and speaker IDs
    X_enroll_combined = np.concatenate((X_enroll1, X_enroll2), axis=0)
    enroll_speaker_ids_combined = enroll_speaker_ids1 + enroll_speaker_ids2

    # Reduce embeddings using UMAP
    umap_model, X_umap_2d = reduce_embeddings_umap(X_enroll_combined, n_components=2, random_state=42)
    
    # Cluster using HDBSCAN
    hdbscan_labels = cluster_enroll_hdbscan(X_umap_2d, min_cluster_size=5, min_samples=5)
    
    # Map each speaker to its majority cluster
    speaker_cluster_mapping = get_speaker_cluster_mapping(enroll_speaker_ids_combined, hdbscan_labels)
    
    # Compute centroids for each cluster in UMAP space
    cluster_centroids = compute_cluster_centroids(X_umap_2d, hdbscan_labels)
    
    return umap_model, speaker_cluster_mapping, cluster_centroids