import uuid
import os
import re
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException

from utils.file_io import save_upload_file
from pipeline.controller import PipelineController
from config.paths import (
    RUNTIME_DATA_INPUT,
    RUNTIME_DATA_NORMALIZED,
    RUNTIME_DATA_CLIPS,
    RUNTIME_DATA_SENTENCE_SELECTION,
    RUNTIME_STATE_PATH,
)
from utils.logger import logger

# Create a new API router instance
router = APIRouter()

# Create a new PipelineController instance
controller = PipelineController()

# Define the set of allowed audio file extensions
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}


def sanitize_filename(name: str) -> str:
    """
    Sanitizes a filename by removing or replacing characters that are not
    alphanumeric, dots, underscores, or hyphens.

    Args:
        name: The original filename.

    Returns:
        The sanitized filename.
    """
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9._-]", "_", name)
    return name


def _clean_runtime_before_upload():
    """
    Cleans the runtime directories before a new file is uploaded. This ensures
    that data from previous runs is removed.
    """
    for path in [
        RUNTIME_DATA_NORMALIZED,
        RUNTIME_DATA_CLIPS,
        RUNTIME_DATA_SENTENCE_SELECTION,
        os.path.dirname(RUNTIME_STATE_PATH),
    ]:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path, exist_ok=True)


@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    tone: str = "informative"
):
    """
    Handles audio file uploads. It validates the file, cleans the runtime
    environment, saves the uploaded file, and then runs the processing pipeline.

    Args:
        file: The audio file to upload.
        tone: The tone to be used for sentence selection in the pipeline.
              Defaults to "informative".

    Returns:
        A dictionary containing the pipeline ID, the tone used, and the
        result of the pipeline execution.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Check if the file extension is allowed
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # Clean up runtime directories before processing a new file
    _clean_runtime_before_upload()

    # Generate a unique ID for the pipeline run
    pipeline_id = str(uuid.uuid4())
    logger.info(f"[{pipeline_id}] New upload request received")

    # Create a destination directory for the uploaded file
    dest_dir = os.path.join(RUNTIME_DATA_INPUT, pipeline_id)
    os.makedirs(dest_dir, exist_ok=True)

    # Sanitize the filename to prevent security issues
    safe_filename = sanitize_filename(file.filename)
    dest_path = os.path.join(dest_dir, safe_filename)

    # Save the uploaded file to the destination path
    await save_upload_file(file, dest_path)

    # Verify that the file was saved correctly
    if not os.path.isfile(dest_path):
        raise HTTPException(status_code=500, detail="Uploaded file missing after save")

    # Run the processing pipeline with the uploaded file
    result = controller.run_pipeline(
        pipeline_id=pipeline_id,
        input_path=dest_path,
        tone=tone
    )

    # Return the results of the pipeline
    return {
        "pipeline_id": pipeline_id,
        "tone": tone,
        "result": result
    }
