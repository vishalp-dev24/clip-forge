# ClipForge

ClipForge is an offline-first system that transforms long audio recordings into short, engaging, podcast-style clips. It uses a pipeline of AI and audio processing tools to automatically select the most impactful segments of your audio.

## Features

-   **Speech-to-Text:** High-quality transcription using `faster-whisper with medium`.
-   **Content-Aware Selection:** A Cross-Encoder model identifies and selects the most relevant sentences.
-   **Automated Audio Engineering:**
    -   Clips are cut with precise padding.
    -   Gentle fade-in/fade-out effects are applied for smooth transitions.
    -   Clips are stitched together with appropriate silences.
-   **Local & Private:** Runs entirely on your own machine. No data leaves your computer.
-   **Optimized for GPUs:** Designed to leverage NVIDIA GPUs for fast processing.

---

## Requirements

### Hardware
-   **GPU:** NVIDIA GPU with at least 6GB of VRAM.
-   **Storage:** 10GB of free space for models and processing.

### Software
-   **Docker:** The recommended way to run ClipForge.
    -   [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) with the WSL2 backend.
-   **NVIDIA Container Toolkit:** To allow Docker to access the GPU.
-   **Git:** For cloning the repository.

---

### PROCESS STEPS:

### 1. Clone the Repository

git clone https://github.com/vishalp-dev24/clip-forge.git


### 2. Build the Docker Image

`Git bash:`

cd backend
docker build --no-cache -t clipforge-backend .


### 3. Run the Docker Container

This command starts the FastAPI server on `http://localhost:8000` and maps the `runtime` directory to your local disk, so you can access output files.

`Git bash:`

docker rm -f clipforge-run
docker run --gpus all -p 8000:8000 \
-v "$(pwd)/runtime:/runtime" \
--name clipforge-run \
clipforge-backend


### 4. Upload Audio for Processing

Open a **new terminal** and use the following command to send an audio file to the running application. Place your audio file (e.g., `my_lecture.mp3`) in the root `clip-forge` directory.

You can specify a `tone` to guide the sentence selection process. This example uses `tone=motivational`.

**Available Tones:**
- `informative` 
- `motivational`
- `storytelling`
- `calm`
- `excitement`

`Git bash:`

curl -X POST "http://localhost:8000/api/upload?tone=TONE_NAME" \
-F "file=@/PATH_TO_AUDIO_FILE/audio_file.mp3"
### NOTE: USE "/"


Once processing is complete, the final edited audio will be available in `backend/runtime/data/output_podcast/final.wav`.