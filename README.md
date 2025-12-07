# Supertonic — Lightning Fast, On-Device TTS

[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

[![Demo](https://img.shields.io/badge/🤗%20Hugging%20Face-Demo-yellow)](https://huggingface.co/spaces/Supertone/supertonic#interactive-demo)
[![Models](https://img.shields.io/badge/🤗%20Hugging%20Face-Models-blue)](https://huggingface.co/Supertone/supertonic)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Hub-blue?logo=docker)](https://hub.docker.com/r/neosun/supertonic-allinone)
[![Paper](https://img.shields.io/badge/arXiv-2503.23108-b31b1b.svg)](https://arxiv.org/abs/2503.23108)

<p align="center">
  <img src="img/Supertonic_IMG_v02_4x.webp" alt="Supertonic Banner" width="600">
</p>

**Supertonic** is an ultra-fast, on-device text-to-speech system designed for **extreme performance** with minimal computational overhead. Built on ONNX Runtime, it runs entirely on your device—no cloud, no API calls, no privacy concerns.

## ✨ Key Features

- ⚡ **Lightning Fast**: 167x faster than real-time on consumer hardware
- 🪶 **Ultra Lightweight**: Only 66M parameters
- 📱 **On-Device**: Complete privacy protection, zero latency
- 🎨 **Natural Text Processing**: Seamlessly handles numbers, dates, currencies
- 🐳 **One-Click Deploy**: Docker support with GPU acceleration

---

## 🚀 Quick Start (One Command)

```bash
docker run -d --name supertonic \
  --gpus all \
  -p 0.0.0.0:8088:8088 \
  -p 0.0.0.0:8501:8501 \
  neosun/supertonic-allinone:latest
```

> **⚡ GPU Recommended**: Use `--gpus all` for GPU acceleration (much faster). Remove it for CPU-only mode.

**Access:**
- 🌐 **Web UI**: http://your-server-ip:8501
- 📡 **API Docs**: http://your-server-ip:8088/docs
- ❤️ **Health Check**: http://your-server-ip:8088/health

**What's Included:**
- FastAPI Server (port 8088)
- Streamlit Web UI (port 8501)
- Pre-loaded TTS models
- 4 voice styles (M1, M2, F1, F2)
- GPU support (CUDA 12.6.3)
- Health checks

---

## 🌐 Web UI

Access the intuitive Streamlit interface at `http://your-server-ip:8501`:

<p align="center">
  <img src="img/ui-screenshot.png" alt="Supertonic Web UI" width="800">
</p>

**Features:**
- 🎤 Real-time text-to-speech generation
- 🎨 4 voice style options
- ⚙️ Adjustable speed and quality settings
- 📊 Generation statistics
- 💾 Download generated audio files
- 📝 History tracking

---

## 📡 API Usage

### Python Example

```python
import requests

# Synthesize speech
response = requests.post(
    "http://localhost:8088/synthesize",
    json={
        "text": "Hello, this is Supertonic speaking.",
        "voice_style": "assets/voice_styles/M1.json",
        "total_steps": 5,
        "speed": 1.05
    }
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Audio file: {result['output_file']}")
print(f"Generation time: {result['generation_time']}s")

# Download audio
audio_url = f"http://localhost:8088/{result['output_file']}"
audio = requests.get(audio_url).content
with open("output.wav", "wb") as f:
    f.write(audio)
```

### cURL Example

```bash
# Health check
curl http://localhost:8088/health

# Generate speech
curl -X POST http://localhost:8088/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test.",
    "voice_style": "assets/voice_styles/M1.json",
    "total_steps": 5
  }'

# Response:
# {
#   "status": "success",
#   "output_file": "output_1765119221.wav",
#   "generation_time": 0.164,
#   "audio_duration": 3.42
# }

# Download audio
curl http://localhost:8088/output_1765119221.wav -o output.wav
```

### JavaScript Example

```javascript
// Synthesize speech
const response = await fetch('http://localhost:8088/synthesize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Hello, this is Supertonic.',
    voice_style: 'assets/voice_styles/M1.json',
    total_steps: 5
  })
});

const result = await response.json();
console.log(`Audio: ${result.output_file}`);

// Download audio
const audioUrl = `http://localhost:8088/${result.output_file}`;
const audioBlob = await fetch(audioUrl).then(r => r.blob());
```

---

## 🎨 Voice Styles

| Voice | Description |
|-------|-------------|
| `assets/voice_styles/M1.json` | Male voice 1 |
| `assets/voice_styles/M2.json` | Male voice 2 |
| `assets/voice_styles/F1.json` | Female voice 1 |
| `assets/voice_styles/F2.json` | Female voice 2 |

---

## 🔧 Container Management

```bash
# View logs
docker logs -f supertonic

# Restart
docker restart supertonic

# Stop
docker stop supertonic

# Remove
docker rm -f supertonic

# Update to latest
docker pull neosun/supertonic-allinone:latest
docker rm -f supertonic
# Run the start command again
```

---

## 📊 Performance

- **Speed**: 167x faster than real-time (M4 Pro)
- **Latency**: ~300ms first audio
- **Model Size**: 66M parameters
- **Audio Quality**: 16-bit PCM, 44.1kHz

---

## 🛠️ Advanced: Build from Source

<details>
<summary>Click to expand</summary>

```bash
# Clone repository
git clone https://github.com/neosun100/supertonic-tts-enhanced.git
cd supertonic-tts-enhanced

# Download models
./download_models.sh

# Build with Docker Compose
docker-compose build

# Run services
docker-compose up -d
```

See [DEPLOY.md](DEPLOY.md) for detailed deployment options.

</details>

---

## 📄 License

- Code: MIT License
- Models: OpenRAIL-M License

Copyright (c) 2025 Supertone Inc.

---

## 📄 Paper

**SupertonicTTS: Towards Highly Efficient and Streamlined Text-to-Speech System**

- 📝 arXiv: https://arxiv.org/abs/2503.23108
- 📄 PDF: https://arxiv.org/pdf/2503.23108
- 🌐 Demo: https://supertonictts.github.io/

**Authors:** Hyeongju Kim, Jinhyeok Yang, Yechan Yu, Seunghun Ji, Jacob Morton, Frederik Bous, Joon Byun, Juheon Lee

**Abstract:** SupertonicTTS is a novel TTS system with only 44M parameters, delivering performance comparable to contemporary zero-shot TTS models while significantly reducing architectural complexity and computational cost.

---

## 🙏 Credits

- [Supertone Inc.](https://github.com/supertone-inc) - Original project
- [Hugging Face](https://huggingface.co/Supertone/supertonic) - Model hosting
- [ONNX Runtime](https://onnxruntime.ai/) - Inference engine

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/supertonic-tts-enhanced&type=Date)](https://star-history.com/#neosun100/supertonic-tts-enhanced)

## 📱 Follow Us

Scan to follow for more AI projects and tech updates:

<p align="center">
  <img src="https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png" alt="WeChat" width="300">
</p>

---

<p align="center">
  <b>⭐ If this project helps you, please give us a Star! ⭐</b>
</p>
