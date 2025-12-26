import subprocess
import os
import tempfile

# Directory and file paths for the output and temporary silence file.
OUT_DIR = "/runtime/data/output_podcast"
OUT_FILE = os.path.join(OUT_DIR, "final.wav")
SILENCE_FILE = os.path.join(OUT_DIR, "silence_1s.wav")


def _ensure_silence():
    """
    Creates a 1-second silent WAV file if it does not already exist.

    This silent clip is used to add pauses between stitched audio segments.
    The audio is generated at 16kHz mono, matching the expected format of the clips.
    """
    if os.path.exists(SILENCE_FILE):
        return

    os.makedirs(OUT_DIR, exist_ok=True)

    # Use FFmpeg to generate a 1-second silent audio file.
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "anullsrc=r=16000:cl=mono", # Use lavfi anullsrc filter
            "-t", "1", # Duration of 1 second
            SILENCE_FILE
        ],
        check=True,
        capture_output=True,
        text=True
    )


def stitch_audio(clips: list):
    """
    Stitches a list of audio clips together into a single WAV file.

    A 1-second silent pause is inserted between each clip. This function uses
    FFmpeg's concat demuxer for stitching.

    Args:
        clips: A list of paths to the audio clips to be stitched.

    Returns:
        The path to the final stitched audio file, or None if the input list is empty.
    """
    if not clips:
        return None

    os.makedirs(OUT_DIR, exist_ok=True)
    _ensure_silence()

    # Create a temporary file to list the clips for FFmpeg's concat demuxer.
    fd, concat_list_path = tempfile.mkstemp(suffix=".txt", text=True)

    try:
        # Write the list of files to the temporary file.
        with os.fdopen(fd, 'w') as f:
            for i, clip_path in enumerate(clips):
                # Sanitize path for the concat file.
                safe_clip = clip_path.replace(os.path.sep, '/').replace("'", "'\\''")
                f.write(f"file '{safe_clip}'\n")

                # Insert 1 second of silence between clips.
                if i < len(clips) - 1:
                    safe_silence = SILENCE_FILE.replace(os.path.sep, '/')
                    f.write(f"file '{safe_silence}'\n")

        # FFmpeg command to concatenate the files listed in the temp file.
        command = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0", # Disable safety checks for file paths
            "-i", concat_list_path,
            "-c:a", "pcm_s16le",   # Re-encode to a standard PCM format
            OUT_FILE
        ]

        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )

    finally:
        # Clean up the temporary file.
        os.remove(concat_list_path)

    return OUT_FILE
