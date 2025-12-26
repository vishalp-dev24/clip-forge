import subprocess
import os

# Directory to save the output audio clips.
CLIP_DIR = "/runtime/data/clips"

# Padding in seconds to add to the start and end of each clip.
# This helps to preserve the full phonemes at the boundaries.
PAD_START = 0.47   # seconds
PAD_END = 0.47     # seconds

# Duration of the fade-in and fade-out effects in seconds.
# This should not be changed to maintain audio quality.
FADE_DURATION = 0.8  # DO NOT CHANGE


def cut_audio(input_path: str, selections: list):
    """
    Cuts an audio file into multiple clips based on a list of time segments.

    This function uses FFmpeg to perform the cutting. It applies padding and
    fade effects to each clip to ensure smooth transitions.

    Args:
        input_path: The path to the input audio file.
        selections: A list of dictionaries, where each dictionary represents a
                    segment to be cut and contains 'start' and 'end' times.

    Returns:
        A list of paths to the generated audio clips.
    """
    if not selections:
        return []

    os.makedirs(CLIP_DIR, exist_ok=True)

    # Base FFmpeg command.
    command = ["ffmpeg", "-y", "-i", input_path]
    filter_complex_parts = []
    output_clips = []

    for i, seg in enumerate(selections):
        output_path = os.path.join(CLIP_DIR, f"clip_{i}.wav")
        output_clips.append(output_path)

        # Calculate start and end times with padding.
        start = max(0.0, seg["start"] - PAD_START)
        end = seg["end"] + PAD_END
        duration = end - start

        # Construct the filter complex part for this clip.
        # It trims the audio, resets the timestamp, and applies fade effects.
        filter_complex_parts.append(
            f"[0:a]"
            f"atrim=start={start}:end={end},"
            f"asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d={FADE_DURATION},"
            f"afade=t=out:st={max(0.0, duration - FADE_DURATION)}:d={FADE_DURATION}"
            f"[a{i}]"
        )

        # Map the processed audio stream to the output file.
        command.extend(["-map", f"[a{i}]", output_path])

    # Insert the filter_complex string into the command.
    command.insert(4, ";".join(filter_complex_parts))
    command.insert(4, "-filter_complex")

    # Run the FFmpeg command.
    subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True
    )

    return output_clips
