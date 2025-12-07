# Supertonic — 极速设备端 TTS

[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

[![Demo](https://img.shields.io/badge/🤗%20Hugging%20Face-Demo-yellow)](https://huggingface.co/spaces/Supertone/supertonic#interactive-demo)
[![Models](https://img.shields.io/badge/🤗%20Hugging%20Face-Models-blue)](https://huggingface.co/Supertone/supertonic)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Hub-blue?logo=docker)](https://hub.docker.com/r/neosun/supertonic-allinone)

**Supertonic** 是一个极速、设备端文本转语音系统，专为极致性能和最小计算开销而设计。基于 ONNX Runtime，完全在您的设备上运行——无需云端、无需 API 调用、无需隐私担忧。

## ✨ 主要特性

- ⚡ **极速生成**: 实时速度的 167 倍
- 🪶 **超轻量级**: 仅 66M 参数
- 📱 **设备端运行**: 完全隐私保护
- 🎨 **自然文本处理**: 无缝处理数字、日期、货币
- 🐳 **一键部署**: Docker 支持，GPU 加速

## 🚀 快速开始

### Docker 部署（推荐）

```bash
# 拉取镜像
docker pull neosun/supertonic-allinone:latest

# 使用 GPU 运行 ⚡ 推荐
docker run -d --name supertonic \
  --gpus all \
  -p 0.0.0.0:8088:8088 \
  -p 0.0.0.0:8501:8501 \
  neosun/supertonic-allinone:latest

# 或不使用 GPU（CPU 模式 - 较慢）
docker run -d --name supertonic \
  -p 0.0.0.0:8088:8088 \
  -p 0.0.0.0:8501:8501 \
  neosun/supertonic-allinone:latest
```

> **⚡ GPU 支持**: 镜像包含 CUDA 12.6.3 支持。使用 `--gpus all` 启用 GPU 加速（更快）。不使用 GPU 则运行在 CPU 上（较慢但仍可用）。

### 访问服务

- **Web UI**: http://你的服务器IP:8501
- **API 文档**: http://你的服务器IP:8088/docs
- **API 健康检查**: http://你的服务器IP:8088/health

### 包含内容

- Supertonic TTS 模型（已预加载）
- 所有依赖
- 4 种语音风格（M1, M2, F1, F2）
- FastAPI 服务器（端口 8088）
- Streamlit Web UI（端口 8501）
- **⚡ GPU 支持（CUDA 12.6.3）**
- 双服务健康检查

## 📡 API 使用

### Python 示例

```python
import requests

# 合成语音
response = requests.post(
    "http://localhost:8088/synthesize",
    json={
        "text": "你好，我是 Supertonic。",
        "voice_style": "assets/voice_styles/M1.json",
        "total_steps": 5,
        "speed": 1.05
    }
)

# 获取结果
result = response.json()
print(f"状态: {result['status']}")
print(f"音频文件: {result['output_file']}")
print(f"生成时间: {result['generation_time']}秒")

# 下载音频
audio_url = f"http://localhost:8088/{result['output_file']}"
audio_response = requests.get(audio_url)
with open("output.wav", "wb") as f:
    f.write(audio_response.content)
```

### 快速测试

```bash
# 健康检查
curl http://localhost:8088/health

# 生成语音
curl -X POST http://localhost:8088/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，这是一个测试。",
    "voice_style": "assets/voice_styles/M1.json",
    "total_steps": 5
  }'
```

## 🎨 语音风格

- `assets/voice_styles/M1.json` - 男声 1
- `assets/voice_styles/M2.json` - 男声 2
- `assets/voice_styles/F1.json` - 女声 1
- `assets/voice_styles/F2.json` - 女声 2

## 🔧 容器管理

```bash
# 查看日志
docker logs -f supertonic

# 重启
docker restart supertonic

# 停止
docker stop supertonic

# 删除
docker rm -f supertonic

# 更新到最新版本
docker pull neosun/supertonic-allinone:latest
docker rm -f supertonic
# 重新运行启动命令
```

## 📄 许可证

本项目示例代码采用 MIT License。模型文件采用 OpenRAIL-M License。

## 🙏 致谢

- [Supertone Inc.](https://github.com/supertone-inc) - 原始项目
- [Hugging Face](https://huggingface.co/Supertone/supertonic) - 模型托管
- [ONNX Runtime](https://onnxruntime.ai/) - 推理引擎

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/supertonic-tts-enhanced&type=Date)](https://star-history.com/#neosun100/supertonic-tts-enhanced)

## 📱 关注公众号

扫码关注获取更多 AI 项目和技术分享：

<p align="center">
  <img src="https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png" alt="公众号" width="300">
</p>

---

<p align="center">
  <b>⭐ 如果这个项目对你有帮助，请给我们一个 Star！⭐</b>
</p>
