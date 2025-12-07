# Supertonic — 極速設備端 TTS

[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

[![Demo](https://img.shields.io/badge/🤗%20Hugging%20Face-Demo-yellow)](https://huggingface.co/spaces/Supertone/supertonic#interactive-demo)
[![Models](https://img.shields.io/badge/🤗%20Hugging%20Face-Models-blue)](https://huggingface.co/Supertone/supertonic)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Hub-blue?logo=docker)](https://hub.docker.com/r/neosun/supertonic-allinone)

**Supertonic** 是一個極速、設備端文本轉語音系統，專為極致性能和最小計算開銷而設計。基於 ONNX Runtime，完全在您的設備上運行——無需雲端、無需 API 調用、無需隱私擔憂。

## ✨ 主要特性

- ⚡ **極速生成**: 實時速度的 167 倍
- 🪶 **超輕量級**: 僅 66M 參數
- 📱 **設備端運行**: 完全隱私保護
- 🎨 **自然文本處理**: 無縫處理數字、日期、貨幣
- 🐳 **一鍵部署**: Docker 支持，GPU 加速

## 🚀 快速開始

### Docker 部署（推薦）

```bash
# 拉取鏡像
docker pull neosun/supertonic-allinone:latest

# 使用 GPU 運行 ⚡ 推薦
docker run -d --name supertonic \
  --gpus all \
  -p 0.0.0.0:8088:8088 \
  -p 0.0.0.0:8501:8501 \
  neosun/supertonic-allinone:latest
```

### 訪問服務

- **Web UI**: http://你的伺服器IP:8501
- **API 文檔**: http://你的伺服器IP:8088/docs
- **API 健康檢查**: http://你的伺服器IP:8088/health

## 📡 API 使用

```bash
# 健康檢查
curl http://localhost:8088/health

# 生成語音
curl -X POST http://localhost:8088/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，這是一個測試。",
    "voice_style": "assets/voice_styles/M1.json",
    "total_steps": 5
  }'
```

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/supertonic-tts-enhanced&type=Date)](https://star-history.com/#neosun100/supertonic-tts-enhanced)

## 📱 關注公眾號

掃碼關注獲取更多 AI 項目和技術分享：

<p align="center">
  <img src="https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png" alt="公眾號" width="300">
</p>

---

<p align="center">
  <b>⭐ 如果這個項目對你有幫助，請給我們一個 Star！⭐</b>
</p>
