import os
import gc
import shutil
import torch
from pathlib import Path

from config.paths import (
    RUNTIME_STATE_PATH,
    RUNTIME_DATA_INPUT,
    RUNTIME_DATA_NORMALIZED,
    RUNTIME_DATA_OUTPUT,
    RUNTIME_DATA_CLIPS,
    RUNTIME_DATA_SENTENCE_SELECTION,
)

from stages.audio_cutting.cut import cut_audio
from stages.audio_stitching.stitch import stitch_audio

from pipeline.state_manager import StateManager
from stages.preflight_validation.audio_duration_check import validate_audio_duration
from stages.audio_normalization.normalize import normalize_audio
from stages.transcription.whisper_stage import run_whisper_transcription
from stages.sentence_selection.cross_encoder_stage import run_sentence_selection

from utils.logger import logger


def _cleanup_after_success():
    """
    Removes temporary runtime directories after a successful pipeline run.
    This helps to keep the filesystem clean.
    """
    for path in [
        RUNTIME_DATA_INPUT,
        RUNTIME_DATA_NORMALIZED,
        RUNTIME_DATA_CLIPS,
        RUNTIME_DATA_SENTENCE_SELECTION,
        os.path.dirname(RUNTIME_STATE_PATH),
    ]:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)


class PipelineController:
    """
    Manages the execution of the audio processing pipeline.
    """
    def __init__(self):
        """
        Initializes the PipelineController, setting up the state manager.
        """
        self.state_manager = StateManager(RUNTIME_STATE_PATH)

    def run_pipeline(
        self,
        pipeline_id: str,
        input_path: str,
        tone: str = "informative"
    ):
        """
        Runs the full audio processing pipeline.

        Args:
            pipeline_id: A unique identifier for this pipeline run.
            input_path: The path to the input audio file.
            tone: The desired tone for sentence selection.
        """
        # Create necessary runtime directories
        os.makedirs(RUNTIME_DATA_INPUT, exist_ok=True)
        os.makedirs(RUNTIME_DATA_NORMALIZED, exist_ok=True)
        os.makedirs(RUNTIME_DATA_CLIPS, exist_ok=True)
        os.makedirs(RUNTIME_DATA_OUTPUT, exist_ok=True)
        os.makedirs(os.path.dirname(RUNTIME_STATE_PATH), exist_ok=True)

        # Reset the state for a new pipeline run
        self.state_manager.reset_state()

        # Extract the base name of the audio file, required for Whisper
        audio_basename = Path(input_path).stem.lower()

        # Initialize the state for this pipeline run
        state = {
            "pipeline_id": pipeline_id,
            "current_stage": "initialized",
            "artifacts": {
                "original_audio": input_path,
                "audio_basename": audio_basename,
            }
        }

        # Define the path for the normalized audio file
        normalized_path = os.path.join(
            RUNTIME_DATA_NORMALIZED, f"{pipeline_id}.wav"
        )

        # Ensure the input audio file exists
        if not os.path.isfile(input_path):
            raise RuntimeError("Input audio missing")

        # --- PIPELINE STAGES ---

        # 1. Validate the duration of the audio
        validate_audio_duration(input_path)
        state["current_stage"] = "audio_validated"
        self.state_manager.update_state(**state)

        # 2. Normalize the audio
        normalize_audio(input_path, normalized_path)
        state["artifacts"]["normalized_audio"] = normalized_path
        state["current_stage"] = "audio_normalized"
        self.state_manager.update_state(**state)

        # 3. Transcribe the audio using Whisper
        run_whisper_transcription(
            audio_path=normalized_path,
            state=state
        )
        self.state_manager.update_state(**state)

        # 4. Select sentences based on the specified tone
        run_sentence_selection(
            whisper_json_path=state["artifacts"]["whisper_output"],
            tone=tone,
            state=state
        )

        selected = state["artifacts"]["selected_sentences"]

        # 5. Cut the audio into clips based on selected sentences
        clip_paths = cut_audio(
            input_path=normalized_path,
            selections=selected
        )

        # 6. Stitch the selected audio clips together
        final_audio = stitch_audio(clip_paths)

        # Clean up temporary files after a successful run
        _cleanup_after_success()

        # Return the final results
        return {
            "pipeline_id": pipeline_id,
            "final_audio": final_audio,
            "clips": clip_paths
        }
