# Minimal helper to expose whether cuda is present
import torch

def cuda_available():
    return torch.cuda.is_available()
