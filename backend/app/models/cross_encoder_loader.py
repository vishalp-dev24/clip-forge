from sentence_transformers import CrossEncoder
import torch


# Global variable to hold the loaded CrossEncoder model.
# This is used to ensure the model is loaded only once.
_model = None

def load_cross_encoder():
    global _model
    if _model is None:
        
        # Determine the device to run the model on.
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Load the CrossEncoder model.
        _model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2",
            device=device
        )

    return _model
