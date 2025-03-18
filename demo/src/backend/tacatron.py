import os
import torch
import numpy as np

import TTS
from TTS.utils.synthesizer import Synthesizer
from TTS.tts.utils.synthesis import synthesis
from TTS.config import load_config
from TTS.tts.models import setup_model as setup_tts_model

class TacatronProsodyExtractor:
    def __init__(self, model_dir: str = "tts_models--en--blizzard2013--capacitron-t2-c50/", use_cuda: bool = False):
        """
        Initialize the TTS Prosody Extractor.

        Args:
            model_dir (str): Directory containing the TTS model files (config.json, model_file.pth).
            use_cuda (bool): Whether to use CUDA (GPU) for inference.
        """
        self.model_dir = model_dir
        self.tts_checkpoint = os.path.join(model_dir, "model_file.pth")
        self.tts_config_path = os.path.join(model_dir, "config.json")
        self.use_cuda = use_cuda
        self.model, self.config = self.load_tts_model()

    def load_tts_model(self):
        """
        Load the TTS model from the provided configuration and checkpoint.

        Returns:
            tuple: (model, config) where 'model' is the loaded TTS model and 'config' is its configuration.
        """
        # Load the TTS configuration from the JSON file.
        tts_config = load_config(self.tts_config_path)

        # Initialize the model using the configuration.
        tts_model = setup_tts_model(config=tts_config)

        # Load the model weights from the checkpoint.
        tts_model.load_checkpoint(tts_config, self.tts_checkpoint, eval=True)

        # Move the model to GPU if requested.
        if self.use_cuda and torch.cuda.is_available():
            tts_model.cuda()

        return tts_model, tts_config

    def get_prosody_embedding(self, audio_path: str, text: str) -> np.ndarray:
        """
        Extract the prosody embedding from the TTS model using a reference audio and its transcript.

        Args:
            audio_path (str): Path to the reference audio (used as style input).
            text (str): The transcript corresponding to the reference audio.

        Returns:
            np.ndarray: A 1D NumPy array containing the prosody embedding.
        """
        # Synthesize voice using the reference information.
        # Note: the "text" parameter in synthesis is not used for embedding extraction, so a dummy text ("hello") is provided.
        outputs = synthesis(
            model=self.model,
            text="hello",
            CONFIG=self.config,
            use_cuda=self.use_cuda,
            speaker_id=None,
            style_wav=audio_path,
            style_text=text,
            use_griffin_lim=None,
            d_vector=None,
            language_id=None,
        )

        # Retrieve the Capacitron VAE outputs
        capacitron_vae_outputs = outputs["outputs"]["capacitron_vae_outputs"]

        # Get the posterior distribution (assumed to be the first output)
        posterior_dist = capacitron_vae_outputs[0]  # MultivariateNormal with shape [1, 128]

        # Get the embedding (mean) from the posterior distribution
        posterior_mean = posterior_dist.loc  # shape: [1, 128]

        # Convert to a NumPy array and return
        return posterior_mean.squeeze(0).detach().cpu().numpy()