import subprocess
import shlex
from utils.logger import logger
from config.limits import MAX_AUDIO_DURATION_SECONDS

def _ffprobe_duration(path: str) -> float:
    """
    Uses ffprobe to get the duration of an audio file in seconds.

    Args:
        path: The path to the audio file.

    Returns:
        The duration of the audio file in seconds as a float.

    Raises:
        RuntimeError: If the ffprobe command fails.
    """
    # Command to get the duration of the audio file using ffprobe.
    # -v error: Only show errors.
    # -show_entries format=duration: Show only the duration from the format information.
    # -of default=noprint_wrappers=1:nokey=1: Output format that's easy to parse (just the value).
    cmd = (
        "ffprobe -v error "
        "-show_entries format=duration "
        "-of default=noprint_wrappers=1:nokey=1 "
        f"{shlex.quote(path)}"
    )
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe error: {proc.stderr.strip()}")
    # The output of the command is the duration in seconds as a string, so we convert it to float.
    return float(proc.stdout.strip())

def validate_audio_duration(path: str) -> float:
    """
    Validates that the audio duration is within the allowed limit.

    This is a required preflight check for the pipeline controller.

    Args:
        path: The path to the audio file.

    Returns:
        The duration of the audio file in seconds.

    Raises:
        RuntimeError: If the audio duration exceeds the maximum allowed duration.
    """
    duration = _ffprobe_duration(path)
    logger.info(f"Audio duration: {duration} seconds")

    # Check if the duration exceeds the maximum allowed duration from the config.
    if duration > MAX_AUDIO_DURATION_SECONDS:
        raise RuntimeError(
            f"AUDIO_TOO_LONG: {duration:.2f}s > {MAX_AUDIO_DURATION_SECONDS}s"
        )

    return duration
