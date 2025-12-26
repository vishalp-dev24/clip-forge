import shutil
import os

# The root directory for all runtime data.
RUNTIME_ROOT = "/runtime"

# A list of subdirectories within the runtime root that should be cleaned.
SUB_DIRS = [
    "data/input_audio",
    "data/normalized_audio",
    "data/clips",
    "data/output_podcast",
    "state"
]

def clean_runtime():
    """
    Cleans the runtime directories by deleting and recreating them.

    This function iterates through the subdirectories defined in SUB_DIRS and
    removes them. It then recreates the empty directories. It also cleans
    out the log files. This is useful for clearing out data from previous
    pipeline runs.
    """
    for sub in SUB_DIRS:
        path = os.path.join(RUNTIME_ROOT, sub)
        if os.path.exists(path):
            # Remove the directory and all its contents.
            shutil.rmtree(path, ignore_errors=True)
            # Recreate the empty directory.
            os.makedirs(path, exist_ok=True)

    # Optional: clean log files without deleting the logs directory itself.
    logs = os.path.join(RUNTIME_ROOT, "logs")
    if os.path.exists(logs):
        for f in os.listdir(logs):
            try:
                os.remove(os.path.join(logs, f))
            except:
                pass

    print("✅ Runtime cleaned successfully")