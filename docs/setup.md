# Faster Whisper with OpenAI-Compatible API Setup

This project uses [Speaches](https://github.com/speaches-ai/speaches), an OpenAI API-compatible server powered by faster-whisper.

## Quick Start

### Local Development (Apple Silicon M4)

```bash
# Start the server
./scripts/start.sh local
```

Server will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- UI: http://localhost:8000 (Gradio interface)

### RunPod (NVIDIA GPU)

```bash
# Start the server
./scripts/start.sh runpod
```

## Installation (First Time Setup)

```bash
# Install uv package manager (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python and dependencies
uv python install
uv venv
source .venv/bin/activate
uv sync
```

### Download Model (Required Before First Use)

Models are downloaded from Hugging Face. Download before starting:

```bash
# Option 1: Use the API (server must be running)
curl -X POST "http://localhost:8000/v1/models/Systran/faster-whisper-large-v3"

# Option 2: Use Python directly
source .venv/bin/activate
python -c "from faster_whisper import WhisperModel; WhisperModel('Systran/faster-whisper-large-v3')"
```

**Note:** The Gradio UI will show an error if no models are downloaded. Use the transcription endpoint directly or download the model first.

## API Usage

### OpenAI Python SDK (Drop-in Replacement)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # or your configured API key
)

# Transcribe audio
with open("audio.mp3", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="Systran/faster-whisper-large-v3",
        file=audio_file
    )
    print(transcript.text)
```

### cURL

```bash
# Transcribe audio file
curl -X POST "http://localhost:8000/v1/audio/transcriptions" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.mp3" \
  -F "model=Systran/faster-whisper-large-v3"

# List available models
curl "http://localhost:8000/v1/models"
```

### Python with requests

```python
import requests

url = "http://localhost:8000/v1/audio/transcriptions"

with open("audio.mp3", "rb") as f:
    response = requests.post(
        url,
        files={"file": f},
        data={"model": "Systran/faster-whisper-large-v3"}
    )

print(response.json())
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/audio/transcriptions` | POST | Transcribe audio to text |
| `/v1/audio/translations` | POST | Translate audio to English |
| `/v1/models` | GET | List available models |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UVICORN_HOST` | `0.0.0.0` | Server host |
| `UVICORN_PORT` | `8000` | Server port |
| `WHISPER__INFERENCE_DEVICE` | `auto` | Device: `cpu`, `cuda`, `auto` |
| `WHISPER__COMPUTE_TYPE` | `default` | Quantization: `float16`, `int8`, etc. |
| `WHISPER__MODEL` | - | Default model to load |
| `STT_MODEL_TTL` | `300` | Seconds before unloading model (-1 = never) |
| `LOG_LEVEL` | `info` | Logging level |

### Config Files

- `config/local.env` - Apple Silicon M4 (CPU mode)
- `config/runpod.env` - RunPod NVIDIA GPU (CUDA mode)

## Available Models

- `Systran/faster-whisper-large-v3` - Best accuracy (~3GB)
- `Systran/faster-whisper-medium` - Good balance (~1.5GB)
- `Systran/faster-whisper-small` - Faster, less accurate (~500MB)
- `Systran/faster-whisper-large-v3-turbo` - Faster large model

## RunPod Deployment

1. Create a RunPod instance with:
   - CUDA 12+
   - Python 3.11+
   - At least 8GB VRAM for large-v3

2. Clone this repository on the RunPod instance

3. Install dependencies:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.bashrc  # or restart shell
   uv sync
   ```

4. Start the server:
   ```bash
   ./scripts/start.sh runpod
   ```

5. Expose port 8000 in RunPod settings

## Troubleshooting

### Model download slow
Models are downloaded from Hugging Face on first use. You can pre-download:
```bash
source .venv/bin/activate
python -c "from faster_whisper import WhisperModel; WhisperModel('large-v3')"
```

### Out of memory on M4
Try using a smaller model or reducing batch size:
```bash
# Edit config/local.env
WHISPER__MODEL=Systran/faster-whisper-medium
```

### CUDA not detected on RunPod
Ensure CUDA libraries are installed:
```bash
nvidia-smi  # Should show GPU info
python -c "import torch; print(torch.cuda.is_available())"
```
