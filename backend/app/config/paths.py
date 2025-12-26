import os

RUNTIME_ROOT = "/runtime"

RUNTIME_DATA_INPUT = os.path.join(RUNTIME_ROOT, "data", "input_audio")
RUNTIME_DATA_NORMALIZED = os.path.join(RUNTIME_ROOT, "data", "normalized_audio")
RUNTIME_DATA_CLIPS = os.path.join(RUNTIME_ROOT, "data", "clips")
RUNTIME_DATA_OUTPUT = os.path.join(RUNTIME_ROOT, "data", "output_podcast")
RUNTIME_DATA_SENTENCE_SELECTION = os.path.join(
    RUNTIME_ROOT, "data", "sentence_selection"
)
RUNTIME_STATE_PATH = os.path.join(RUNTIME_ROOT, "state", "state.json")
RUNTIME_CACHE_MODELS = os.path.join(RUNTIME_ROOT, "cache", "models")
RUNTIME_CACHE_TORCH = os.path.join(RUNTIME_ROOT, "cache", "torch")
RUNTIME_LOGS_API = os.path.join(RUNTIME_ROOT, "logs", "api.log")
