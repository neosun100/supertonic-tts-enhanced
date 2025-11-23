# Supertonic TTS - 使用指南

本文档详细说明如何使用 Supertonic TTS 进行文本转语音，包括各种编程语言的调用方法和 Docker 镜像构建方法。

## 📋 目录

- [前置要求](#前置要求)
- [模型下载](#模型下载)
- [各语言调用方法](#各语言调用方法)
  - [Python](#python)
  - [Node.js](#nodejs)
  - [Java](#java)
  - [C++](#c)
  - [Go](#go)
  - [C#](#c-1)
  - [Swift](#swift)
  - [Rust](#rust)
  - [iOS](#ios)
- [Docker 镜像构建](#docker-镜像构建)
- [参数说明](#参数说明)
- [常见问题](#常见问题)

---

## 前置要求

### 系统要求

- **操作系统**: Linux, macOS, Windows
- **Python**: 3.10+ (如果使用 Python)
- **Git LFS**: 用于下载大文件模型

### 安装 Git LFS

```bash
# macOS
brew install git-lfs && git lfs install

# Ubuntu/Debian
sudo apt-get install git-lfs && git lfs install

# 其他系统
# 参考: https://git-lfs.com
```

---

## 模型下载

在开始使用之前，需要下载 ONNX 模型文件和语音风格文件：

```bash
# 方法 1: 使用下载脚本（推荐）
./download_models.sh

# 方法 2: 手动克隆
git clone https://huggingface.co/Supertone/supertonic assets
```

下载完成后，目录结构应该是：

```
assets/
├── onnx/              # ONNX 模型文件
│   ├── duration_predictor.onnx
│   ├── text_encoder.onnx
│   ├── vector_estimator.onnx
│   ├── vocoder.onnx
│   └── ...
└── voice_styles/      # 语音风格文件
    ├── M1.json        # 男声 1
    ├── M2.json        # 男声 2
    ├── F1.json        # 女声 1
    └── F2.json        # 女声 2
```

---

## 各语言调用方法

### Python

#### 安装依赖

```bash
cd py
uv sync
# 或
pip install -r requirements.txt
```

#### 基本使用

```bash
# 基本调用（CPU）
python3 example_onnx.py --text "Hello, world!"

# 使用 GPU
python3 example_onnx.py --use-gpu --text "Hello, world!"

# 指定语音风格
python3 example_onnx.py \
  --voice-style assets/voice_styles/F1.json \
  --text "Hello, world!"

# 调整质量（更多步数 = 更高质量但更慢）
python3 example_onnx.py \
  --total-step 10 \
  --text "Hello, world!"

# 调整语速
python3 example_onnx.py \
  --speed 1.2 \
  --text "Hello, world!"

# 批量处理
python3 example_onnx.py \
  --batch \
  --voice-style assets/voice_styles/M1.json assets/voice_styles/F1.json \
  --text "First text" "Second text"
```

#### 代码示例

```python
from helper import load_text_to_speech, load_voice_style
import soundfile as sf

# 1. 加载 TTS 模型
tts = load_text_to_speech("assets/onnx", use_gpu=False)

# 2. 加载语音风格
style = load_voice_style(["assets/voice_styles/M1.json"], verbose=True)

# 3. 生成语音
text = "Hello, world!"
wav, duration = tts(text, style, total_step=5, speed=1.05)

# 4. 保存音频
audio = wav[0, :int(tts.sample_rate * duration[0].item())]
sf.write("output.wav", audio, tts.sample_rate)
```

#### 完整参数列表

```bash
python3 example_onnx.py --help
```

---

### Node.js

#### 安装依赖

```bash
cd nodejs
npm install
```

#### 基本使用

```bash
# 基本调用（CPU）
node example_onnx.js --text "Hello, world!"

# 使用 GPU
node example_onnx.js --use-gpu --text "Hello, world!"

# 指定语音风格
node example_onnx.js \
  --voice-style assets/voice_styles/F1.json \
  --text "Hello, world!"

# 批量处理
node example_onnx.js \
  --batch \
  --voice-style assets/voice_styles/M1.json,assets/voice_styles/F1.json \
  --text "First text|Second text"
```

#### 代码示例

```javascript
import { loadTextToSpeech, loadVoiceStyle, writeWavFile } from './helper.js';

// 1. 加载 TTS 模型
const tts = await loadTextToSpeech('assets/onnx', useGpu=false);

// 2. 加载语音风格
const style = loadVoiceStyle(['assets/voice_styles/M1.json'], true);

// 3. 生成语音
const text = 'Hello, world!';
const { wav, duration } = await tts.call(text, style, 5, 1.05);

// 4. 保存音频
const wavLen = Math.floor(tts.sampleRate * duration[0]);
const wavOut = wav.slice(0, wavLen);
writeWavFile('output.wav', wavOut, tts.sampleRate);
```

---

### Java

#### 安装依赖

```bash
cd java
mvn clean install
```

#### 基本使用

```bash
# 基本调用（CPU）
mvn exec:java -Dexec.mainClass="ExampleONNX" \
  -Dexec.args="--text 'Hello, world!'"

# 使用 GPU
mvn exec:java -Dexec.mainClass="ExampleONNX" \
  -Dexec.args="--use-gpu --text 'Hello, world!'"

# 指定语音风格
mvn exec:java -Dexec.mainClass="ExampleONNX" \
  -Dexec.args="--voice-style assets/voice_styles/F1.json --text 'Hello, world!'"
```

#### 代码示例

```java
import ai.onnxruntime.*;
import Helper.*;

// 1. 初始化环境
OrtEnvironment env = OrtEnvironment.getEnvironment();

// 2. 加载 TTS 模型
TextToSpeech tts = Helper.loadTextToSpeech("assets/onnx", false, env);

// 3. 加载语音风格
Style style = Helper.loadVoiceStyle(
    Arrays.asList("assets/voice_styles/M1.json"), 
    true, 
    env
);

// 4. 生成语音
String text = "Hello, world!";
TTSResult result = tts.call(text, style, 5, 1.05f, 0.3f, env);

// 5. 保存音频
float[] wav = result.wav;
float[] duration = result.duration;
int wavLen = (int)(tts.sampleRate * duration[0]);
float[] wavOut = Arrays.copyOf(wav, wavLen);
Helper.writeWavFile("output.wav", wavOut, tts.sampleRate);
```

---

### C++

#### 编译

```bash
cd cpp
mkdir build && cd build
cmake ..
cmake --build . --config Release
```

#### 基本使用

```bash
# 基本调用
./example_onnx --text "Hello, world!"

# 指定语音风格
./example_onnx \
  --voice-style assets/voice_styles/F1.json \
  --text "Hello, world!"

# 批量处理
./example_onnx \
  --batch \
  --voice-style assets/voice_styles/M1.json,assets/voice_styles/F1.json \
  --text "First text|Second text"
```

#### 代码示例

```cpp
#include "helper.h"
#include <iostream>

int main() {
    // 1. 初始化环境
    Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "TTS");
    Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(
        OrtAllocatorType::OrtArenaAllocator, 
        OrtMemType::OrtMemTypeDefault
    );
    
    // 2. 加载 TTS 模型
    auto tts = loadTextToSpeech(env, "assets/onnx", false);
    
    // 3. 加载语音风格
    std::vector<std::string> voice_styles = {"assets/voice_styles/M1.json"};
    auto style = loadVoiceStyle(voice_styles, true);
    
    // 4. 生成语音
    std::string text = "Hello, world!";
    auto result = tts->call(memory_info, text, style, 5, 1.05f);
    
    // 5. 保存音频
    int wavLen = static_cast<int>(tts->getSampleRate() * result.duration[0]);
    std::vector<float> wavOut(result.wav.begin(), 
                              result.wav.begin() + wavLen);
    writeWavFile("output.wav", wavOut, tts->getSampleRate());
    
    return 0;
}
```

---

### Go

#### 安装依赖

```bash
cd go
go mod download
```

#### 基本使用

```bash
# 基本调用（CPU）
go run example_onnx.go helper.go --text "Hello, world!"

# 使用 GPU
go run example_onnx.go helper.go --use-gpu --text "Hello, world!"

# 指定语音风格
go run example_onnx.go helper.go \
  --voice-style assets/voice_styles/F1.json \
  --text "Hello, world!"
```

#### 代码示例

```go
package main

import (
    "fmt"
    ort "github.com/yalue/onnxruntime_go"
)

func main() {
    // 1. 初始化 ONNX Runtime
    InitializeONNXRuntime()
    defer ort.DestroyEnvironment()
    
    // 2. 加载配置
    cfg, _ := LoadCfgs("assets/onnx")
    
    // 3. 加载 TTS 模型
    tts, _ := LoadTextToSpeech("assets/onnx", false, cfg)
    defer tts.Destroy()
    
    // 4. 加载语音风格
    voiceStyles := []string{"assets/voice_styles/M1.json"}
    style, _ := LoadVoiceStyle(voiceStyles, true)
    defer style.Destroy()
    
    // 5. 生成语音
    text := "Hello, world!"
    wav, duration, _ := tts.Call(text, style, 5, 1.05, 0.3)
    
    // 6. 保存音频
    wavLen := int(float32(tts.SampleRate) * duration)
    wavOut := make([]float64, wavLen)
    for i := 0; i < wavLen && i < len(wav); i++ {
        wavOut[i] = float64(wav[i])
    }
    writeWavFile("output.wav", wavOut, tts.SampleRate)
}
```

---

### C#

#### 安装依赖

```bash
cd csharp
dotnet restore
```

#### 基本使用

```bash
# 基本调用
dotnet run -- --text "Hello, world!"

# 使用 GPU
dotnet run -- --use-gpu --text "Hello, world!"

# 指定语音风格
dotnet run -- \
  --voice-style assets/voice_styles/F1.json \
  --text "Hello, world!"
```

#### 代码示例

```csharp
using System;
using Supertonic;

class Program
{
    static void Main()
    {
        // 1. 加载 TTS 模型
        var tts = Helper.LoadTextToSpeech("assets/onnx", useGpu: false);
        
        // 2. 加载语音风格
        var voiceStyles = new List<string> { "assets/voice_styles/M1.json" };
        var style = Helper.LoadVoiceStyle(voiceStyles, verbose: true);
        
        // 3. 生成语音
        string text = "Hello, world!";
        var (wav, duration) = tts.Call(text, style, totalStep: 5, speed: 1.05f);
        
        // 4. 保存音频
        int wavLen = (int)(tts.SampleRate * duration[0]);
        float[] wavOut = new float[wavLen];
        Array.Copy(wav, 0, wavOut, 0, wavLen);
        Helper.WriteWavFile("output.wav", wavOut, tts.SampleRate);
    }
}
```

---

### Swift

#### 编译

```bash
cd swift
swift build -c release
```

#### 基本使用

```bash
.build/release/example_onnx --text "Hello, world!"
```

详细说明请参考 [swift/README.md](swift/README.md)

---

### Rust

#### 编译

```bash
cd rust
cargo build --release
```

#### 基本使用

```bash
./target/release/example_onnx --text "Hello, world!"
```

详细说明请参考 [rust/README.md](rust/README.md)

---

### iOS

#### 设置

```bash
cd ios/ExampleiOSApp
xcodegen generate
open ExampleiOSApp.xcodeproj
```

在 Xcode 中：
1. Targets → ExampleiOSApp → Signing: 选择你的 Team
2. 选择 iPhone 作为运行目标
3. Build & Run

详细说明请参考 [ios/README.md](ios/README.md)

---

## Docker 镜像构建

### 构建 TTS 服务器镜像

#### 方法 1: 使用 Dockerfile

```bash
# 构建镜像
docker build -t supertonic-tts:latest -f Dockerfile .

# 运行容器（CPU 模式）
docker run --rm -it \
  -v $(pwd)/assets:/app/assets \
  -v $(pwd)/results:/app/results \
  supertonic-tts:latest \
  python3 example_onnx.py --text "Hello, world!"

# 运行容器（GPU 模式）
docker run --rm -it \
  --gpus all \
  -v $(pwd)/assets:/app/assets \
  -v $(pwd)/results:/app/results \
  supertonic-tts:latest \
  python3 example_onnx.py --use-gpu --text "Hello, world!"
```

#### 方法 2: 使用 Docker Compose

```bash
# 构建所有服务
docker-compose build

# 构建特定服务
docker-compose build supertonic-tts-server

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f supertonic-tts-server

# 停止服务
docker-compose down
```

### 构建 Streamlit UI 镜像

```bash
# 构建 UI 镜像
docker build -t supertonic-tts-ui:latest -f Dockerfile.streamlit .

# 运行 UI 容器
docker run --rm -it \
  -p 8501:8501 \
  -v $(pwd)/results:/app/results \
  supertonic-tts-ui:latest
```

### Dockerfile 说明

#### Dockerfile (TTS 服务器)

```dockerfile
# 基础镜像: NVIDIA CUDA 12.6.3
FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip git git-lfs \
    libsndfile1 ffmpeg wget curl

# 安装 Python 依赖
RUN pip3 install --no-cache-dir \
    onnxruntime-gpu==1.23.2 \
    numpy>=1.26.0 \
    soundfile>=0.12.1 \
    librosa>=0.10.0 \
    PyYAML>=6.0 \
    fastapi>=0.104.0 \
    uvicorn[standard]>=0.24.0 \
    pydantic>=2.0.0

# 复制项目文件
COPY . /app/
WORKDIR /app/py
```

### 自定义构建

#### 修改 GPU 版本

编辑 `Dockerfile`，修改 CUDA 版本：

```dockerfile
FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04
# 改为其他版本，例如:
# FROM nvidia/cuda:11.8.0-cudnn-runtime-ubuntu22.04
```

#### 修改 Python 版本

```dockerfile
# 修改 Python 版本
RUN apt-get install -y python3.11 python3-pip
```

#### 添加额外依赖

```dockerfile
# 在安装 Python 依赖部分添加
RUN pip3 install --no-cache-dir \
    your-package-name \
    ...
```

### 构建优化

#### 使用构建缓存

```bash
# 利用 Docker 缓存，先复制 requirements.txt
COPY py/requirements.txt /app/py/
RUN pip3 install -r /app/py/requirements.txt

# 然后复制其他文件
COPY . /app/
```

#### 多阶段构建（可选）

```dockerfile
# 构建阶段
FROM nvidia/cuda:12.6.3-cudnn-devel-ubuntu22.04 AS builder
# ... 构建步骤 ...

# 运行阶段
FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04
COPY --from=builder /app /app
```

### 验证构建

```bash
# 检查镜像大小
docker images supertonic-tts

# 检查镜像内容
docker run --rm supertonic-tts:latest ls -la /app

# 测试运行
docker run --rm supertonic-tts:latest python3 --version
```

---

## 参数说明

### 通用参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--use-gpu` | flag | false | 使用 GPU 加速（如果可用） |
| `--onnx-dir` | string | `assets/onnx` | ONNX 模型目录路径 |
| `--total-step` | int | 5 | 去噪步数（1-50），越高质量越好但越慢 |
| `--speed` | float | 1.05 | 语速倍数（0.5-2.0） |
| `--voice-style` | string | `M1.json` | 语音风格文件路径 |
| `--text` | string | - | 要合成的文本 |
| `--save-dir` | string | `results` | 输出目录 |
| `--batch` | flag | false | 启用批量处理模式 |
| `--n-test` | int | 4 | 生成次数 |

### 语音风格

| 文件 | 说明 | 适用场景 |
|------|------|----------|
| `M1.json` | 标准男声 | 新闻播报、叙述 |
| `M2.json` | 年轻男声 | 对话、讲解 |
| `F1.json` | 温柔女声 | 有声读物、导航 |
| `F2.json` | 活泼女声 | 广告、客服 |

---

## 常见问题

### Q1: 如何选择 total_step 参数？

- **1-3 步**: 快速模式，质量较低，适合测试
- **4-7 步**: 平衡模式（推荐），质量与速度平衡
- **8-20 步**: 高质量模式，速度较慢，适合重要内容

### Q2: GPU 不可用怎么办？

确保：
1. 已安装 NVIDIA 驱动
2. 已安装 CUDA
3. 已安装 `onnxruntime-gpu`（Python）或对应 GPU 版本

### Q3: 如何批量处理多个文本？

使用 `--batch` 参数：

```bash
python3 example_onnx.py \
  --batch \
  --voice-style M1.json F1.json \
  --text "Text 1" "Text 2"
```

### Q4: 生成的音频在哪里？

默认保存在 `results/` 目录，可通过 `--save-dir` 参数修改。

### Q5: Docker 构建失败？

检查：
1. Docker 版本是否支持多阶段构建
2. 网络连接是否正常（下载依赖）
3. 磁盘空间是否充足

---

## 更多资源

- [项目 README](README.md) - 完整项目文档
- [快速开始](QUICK_START.md) - 快速部署指南
- [Docker 设置](DOCKER_SETUP.md) - Docker 详细配置
- [API 文档](SWAGGER_API_GUIDE.md) - HTTP API 使用指南

---

**享受使用 Supertonic TTS！** 🎤✨
