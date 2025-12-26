import subprocess
import shlex
from utils.logger import logger

def normalize_audio(input_path: str, output_path: str):
    """
    Normalizes an audio file to a standard format for Automatic Speech Recognition (ASR).

    This function uses FFmpeg to convert the input audio to a 16kHz, mono,
    16-bit PCM WAV file, which is a common requirement for many ASR systems.

    Args:
        input_path: The path to the input audio file.
        output_path: The path where the normalized audio file will be saved.

    Returns:
        The path to the normalized output file.

    Raises:
        RuntimeError: If the FFmpeg command fails.
    """
    # The FFmpeg command to perform the normalization.
    # -y: Overwrite output file if it exists.
    # -i: Input file path.
    # -ac 1: Set the number of audio channels to 1 (mono).
    # -ar 16000: Set the audio sampling frequency to 16kHz.
    # -sample_fmt s16: Set the sample format to 16-bit signed integer (PCM).
    # shlex.quote is used to safely handle file paths with spaces or special characters.
    cmd = (
        f"ffmpeg -y -i {shlex.quote(input_path)} "
        f"-ac 1 -ar 16000 -sample_fmt s16 {shlex.quote(output_path)}"
    )
    logger.info(f"Running ffmpeg normalize: {cmd}")
    # Execute the FFmpeg command.
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    # Check if the command was successful.
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg normalization failed: {proc.stderr}")
    return output_path
