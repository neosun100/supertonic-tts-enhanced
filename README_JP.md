# Supertonic — 超高速オンデバイス TTS

[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

[![Demo](https://img.shields.io/badge/🤗%20Hugging%20Face-Demo-yellow)](https://huggingface.co/spaces/Supertone/supertonic#interactive-demo)
[![Models](https://img.shields.io/badge/🤗%20Hugging%20Face-Models-blue)](https://huggingface.co/Supertone/supertonic)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Hub-blue?logo=docker)](https://hub.docker.com/r/neosun/supertonic-allinone)

**Supertonic** は、極限のパフォーマンスと最小限の計算オーバーヘッドのために設計された、超高速オンデバイステキスト読み上げシステムです。ONNX Runtime をベースに、完全にデバイス上で動作します——クラウド不要、API 呼び出し不要、プライバシーの心配なし。

## ✨ 主な機能

- ⚡ **超高速生成**: リアルタイムの 167 倍の速度
- 🪶 **超軽量**: わずか 66M パラメータ
- 📱 **オンデバイス実行**: 完全なプライバシー保護
- 🎨 **自然なテキスト処理**: 数字、日付、通貨をシームレスに処理
- 🐳 **ワンクリックデプロイ**: Docker サポート、GPU アクセラレーション

## 🚀 クイックスタート

### Docker デプロイ（推奨）

```bash
# イメージをプル
docker pull neosun/supertonic-allinone:latest

# GPU を使用して実行 ⚡ 推奨
docker run -d --name supertonic \
  --gpus all \
  -p 0.0.0.0:8088:8088 \
  -p 0.0.0.0:8501:8501 \
  neosun/supertonic-allinone:latest
```

### サービスへのアクセス

- **Web UI**: http://サーバーIP:8501
- **API ドキュメント**: http://サーバーIP:8088/docs
- **API ヘルスチェック**: http://サーバーIP:8088/health

## 📡 API 使用方法

```bash
# ヘルスチェック
curl http://localhost:8088/health

# 音声生成
curl -X POST http://localhost:8088/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "こんにちは、これはテストです。",
    "voice_style": "assets/voice_styles/M1.json",
    "total_steps": 5
  }'
```

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/supertonic-tts-enhanced&type=Date)](https://star-history.com/#neosun100/supertonic-tts-enhanced)

## 📱 公式アカウントをフォロー

QR コードをスキャンして、より多くの AI プロジェクトと技術情報を入手：

<p align="center">
  <img src="https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png" alt="公式アカウント" width="300">
</p>

---

<p align="center">
  <b>⭐ このプロジェクトが役に立ったら、Star をください！⭐</b>
</p>
