import json
import os
import gc
from pathlib import Path
from faster_whisper import WhisperModel
from utils.logger import logger


def _group_segments_to_sentences(segments):
    """
    Groups Whisper segments into sentences.

    This function takes the raw segments from Whisper and formats them into a
    cleaner list of sentences with start, end, and text.

    Args:
        segments: A list of segment dictionaries from Whisper.

    Returns:
        A list of sentence dictionaries.
    """
    sentences = []

    for seg in segments:
        text = seg.get("text", "").strip()
        if not text:
            continue

        sentences.append({
            "start": float(seg["start"]),
            "end": float(seg["end"]),
            "text": text
        })

    return sentences


def run_whisper_transcription(audio_path: str, state: dict):
    """
    Runs the Whisper transcription process on an audio file.

    Args:
        audio_path: The path to the audio file to be transcribed.
        state: The current pipeline state dictionary.

    Returns:
        A dictionary containing the transcription results.
    """
    artifacts = state.get("artifacts", {})
    audio_basename = artifacts.get("audio_basename")

    if not audio_basename:
        raise RuntimeError("audio_basename missing in state.artifacts")

    # Define the output path for the Whisper JSON result.
    whisper_output_path = Path("/runtime/state") / f"{audio_basename}_whisper.json"
    whisper_output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Loading Whisper model (medium) on CUDA")
    # Load the faster-whisper model.
    model = WhisperModel(
        "medium",
        device="cuda",
        compute_type="int8_float16",  # Use mixed precision for performance.
        cpu_threads=4,
        num_workers=1
    )
    logger.info("Model loaded")

    try:
        # Transcribe the audio file.
        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=False,
            word_timestamps=False
        )

        # Convert generator to list and group segments into sentences.
        segs = [{"start": s.start, "end": s.end, "text": s.text} for s in segments]
        sentences = _group_segments_to_sentences(segs)

        # Prepare the output data structure.
        out = {
            "audio_metadata": {
                "original_filename": os.path.basename(audio_path),
                "duration_seconds": float(info.duration),
                "language": info.language
            },
            "model_info": {
                "model_name": "whisper-medium",
                "device": "cuda",
                "precision": "int8_float16"
            },
            "sentences": sentences
        }

        # Write the transcription output to a JSON file.
        with whisper_output_path.open("w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)

        # Update the pipeline state with the path to the output and the current stage.
        state.setdefault("artifacts", {})
        state["artifacts"]["whisper_output"] = str(whisper_output_path)
        state["current_stage"] = "transcription_done"

        return out

    finally:
        # Force release of GPU memory. This is crucial for long-running services
        # to prevent memory leaks from the Whisper model.
        try:
            del model
        except Exception:
            pass

        gc.collect()

        import torch
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
