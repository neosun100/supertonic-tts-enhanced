# Supertonic TTS - Quick Deployment Guide

## 🚀 One-Command Deployment

```bash
docker run -d --name supertonic \
  --gpus all \
  -p 0.0.0.0:8088:8088 \
  -p 0.0.0.0:8501:8501 \
  neosun/supertonic-allinone:latest
```

## 📡 Access

- **Web UI**: http://your-server-ip:8501
- **API Docs**: http://your-server-ip:8088/docs
- **API Health**: http://your-server-ip:8088/health

## 🧪 Quick Test

```bash
# Health check
curl http://localhost:8088/health

# Generate speech
curl -X POST http://localhost:8088/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is Supertonic.",
    "voice_style": "assets/voice_styles/M1.json",
    "total_steps": 5
  }'
```

## 🎨 Voice Styles

- `assets/voice_styles/M1.json` - Male voice 1
- `assets/voice_styles/M2.json` - Male voice 2
- `assets/voice_styles/F1.json` - Female voice 1
- `assets/voice_styles/F2.json` - Female voice 2

## 🔧 Management

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
# Run command again
```

## 📦 What's Included

- FastAPI server (port 8088)
- Streamlit Web UI (port 8501)
- GPU support (CUDA 12.6.3)
- Pre-loaded TTS models
- 4 voice styles
- Health checks

## 🐳 Docker Hub

https://hub.docker.com/r/neosun/supertonic-allinone
