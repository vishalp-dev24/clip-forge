import json
from pathlib import Path

from models.cross_encoder_loader import load_cross_encoder
from config.paths import RUNTIME_DATA_SENTENCE_SELECTION
from utils.logger import logger


# Maximum gap in seconds between two segments to be considered for merging.
MERGE_GAP = 0.6  # seconds

# Pre-defined queries for different tones, used by the Cross-Encoder model.
TONE_QUERIES = {
    "informative": (
        "Educational content that teaches concepts, steps, facts, "
        "instructions, explanations, or actionable knowledge."
    ),
    "motivational": (
        "Motivational speech that inspires action, confidence, "
        "discipline, or personal growth."
    ),
    "storytelling": (
        "Narrative storytelling with examples, experiences, "
        "scenarios, or stories."
    ),
    "calm": (
        "Calm, reassuring, reflective content spoken in a relaxed manner."
    ),
    "excitement": (
        "Energetic, enthusiastic, high-energy speech expressing excitement."
    ),
}

def _merge_close_segments(segments):
    """
    Merges consecutive text segments that are close to each other.

    Args:
        segments: A list of sentence segments, each with 'start' and 'end' times.

    Returns:
        A new list of merged sentence segments.
    """
    if not segments:
        return []

    # Sort segments by start time to ensure correct merging order.
    segments = sorted(segments, key=lambda s: s["start"])
    merged = [segments[0]]

    for cur in segments[1:]:
        prev = merged[-1]

        # If the gap between the previous and current segment is small enough, merge them.
        if cur["start"] - prev["end"] <= MERGE_GAP:
            prev["end"] = max(prev["end"], cur["end"])
            prev["text"] = prev["text"] + " " + cur["text"]
        else:
            merged.append(cur)

    return merged


def run_sentence_selection(
    whisper_json_path: str,
    tone: str,
    state: dict,
    top_k: int = 12
):
    """
    Selects the most relevant sentences from a transcription based on a given tone.

    This function uses a Cross-Encoder model to score sentences against a query
    representing the desired tone.

    Args:
        whisper_json_path: Path to the JSON output from the Whisper transcription stage.
        tone: The desired tone for sentence selection (e.g., "informative").
        state: The current pipeline state dictionary.
        top_k: The number of top-scoring sentences to select.

    Returns:
        A list of the selected and merged sentence segments.
    """
    logger.info("Running Cross-Encoder sentence selection")

    with open(whisper_json_path, "r", encoding="utf-8") as f:
        whisper_data = json.load(f)

    sentences = whisper_data["sentences"]

    if tone not in TONE_QUERIES:
        raise RuntimeError(f"Unsupported tone: {tone}")

    query = TONE_QUERIES[tone]

    # Create pairs of (query, sentence) for the Cross-Encoder model.
    pairs = [(query, s["text"]) for s in sentences]

    # Load the Cross-Encoder model and predict scores for the pairs.
    model = load_cross_encoder()
    scores = model.predict(pairs)

    # Rank sentences by their scores in descending order.
    ranked = sorted(
        zip(scores, sentences),
        key=lambda x: x[0],
        reverse=True
    )

    # Select the top_k sentences.
    selected = [s for _, s in ranked[:top_k]]

    # Merge sentences that are close to each other.
    selected_sentences = _merge_close_segments(selected)

    # Update the pipeline state with the selected sentences.
    state["artifacts"]["selected_sentences"] = selected_sentences
    state["current_stage"] = "sentences_selected"

    pipeline_id = state.get("pipeline_id")
    if not pipeline_id:
        raise RuntimeError("pipeline_id missing in state")

    # Write the selected sentences to a JSON file for debugging and records.
    out_dir = Path(RUNTIME_DATA_SENTENCE_SELECTION)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{pipeline_id}_sentences.json"

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "pipeline_id": pipeline_id,
                "model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
                "tone": tone,
                "sentences": selected_sentences
            },
            f,
            indent=2,
            ensure_ascii=False
        )

    state["artifacts"]["sentence_selection_output"] = str(out_path)

    return selected_sentences
