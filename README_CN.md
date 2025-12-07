# Supertonic — 极速设备端 TTS

[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

[![Demo](https://img.shields.io/badge/🤗%20Hugging%20Face-Demo-yellow)](https://huggingface.co/spaces/Supertone/supertonic#interactive-demo)
[![Models](https://img.shields.io/badge/🤗%20Hugging%20Face-Models-blue)](https://huggingface.co/Supertone/supertonic)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Hub-blue?logo=docker)](https://hub.docker.com/r/neosun/supertonic-allinone)

<p align="center">
  <img src="img/Supertonic_IMG_v02_4x.webp" alt="Supertonic Banner" width="600">
</p>

**Supertonic** 是一个极速、设备端文本转语音系统，专为极致性能和最小计算开销而设计。基于 ONNX Runtime，完全在您的设备上运行——无需云端、无需 API 调用、无需隐私担忧。

## ✨ 主要特性

- ⚡ **极速生成**: 实时速度的 167 倍
- 🪶 **超轻量级**: 仅 66M 参数
- 📱 **设备端运行**: 完全隐私保护，零延迟
- 🎨 **自然文本处理**: 无缝处理数字、日期、货币
- 🐳 **一键部署**: Docker 支持，GPU 加速

---

## 🚀 快速开始（一行命令）

```bash
docker run -d --name supertonic \
  --gpus all \
  -p 0.0.0.0:8088:8088 \
  -p 0.0.0.0:8501:8501 \
  neosun/supertonic-allinone:latest
```

> **⚡ 推荐使用 GPU**: 使用 `--gpus all` 启用 GPU 加速（更快）。去掉该参数则使用 CPU 模式。

**访问地址:**
- 🌐 **Web UI**: http://你的服务器IP:8501
- 📡 **API 文档**: http://你的服务器IP:8088/docs
- ❤️ **健康检查**: http://你的服务器IP:8088/health

**包含内容:**
- FastAPI 服务器（端口 8088）
- Streamlit Web UI（端口 8501）
- 预加载 TTS 模型
- 4 种语音风格（M1, M2, F1, F2）
- GPU 支持（CUDA 12.6.3）
- 健康检查

---

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

result = response.json()
print(f"状态: {result['status']}")
print(f"音频文件: {result['output_file']}")
print(f"生成时间: {result['generation_time']}秒")

# 下载音频
audio_url = f"http://localhost:8088/{result['output_file']}"
audio = requests.get(audio_url).content
with open("output.wav", "wb") as f:
    f.write(audio)
```

### cURL 示例

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

# 响应示例:
# {
#   "status": "success",
#   "output_file": "output_1765119221.wav",
#   "generation_time": 0.164,
#   "audio_duration": 3.42
# }

# 下载音频
curl http://localhost:8088/output_1765119221.wav -o output.wav
```

### JavaScript 示例

```javascript
// 合成语音
const response = await fetch('http://localhost:8088/synthesize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: '你好，我是 Supertonic。',
    voice_style: 'assets/voice_styles/M1.json',
    total_steps: 5
  })
});

const result = await response.json();
console.log(`音频: ${result.output_file}`);

// 下载音频
const audioUrl = `http://localhost:8088/${result.output_file}`;
const audioBlob = await fetch(audioUrl).then(r => r.blob());
```

---

## 🎨 语音风格

| 语音 | 说明 |
|------|------|
| `assets/voice_styles/M1.json` | 男声 1 |
| `assets/voice_styles/M2.json` | 男声 2 |
| `assets/voice_styles/F1.json` | 女声 1 |
| `assets/voice_styles/F2.json` | 女声 2 |

---

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

---

## 📊 性能指标

- **速度**: 实时速度的 167 倍（M4 Pro）
- **延迟**: 首个音频约 300ms
- **模型大小**: 66M 参数
- **音频质量**: 16-bit PCM, 44.1kHz

---

## 📄 许可证

- 代码: MIT License
- 模型: OpenRAIL-M License

Copyright (c) 2025 Supertone Inc.

---

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
