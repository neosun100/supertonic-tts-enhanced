# Supertonic — Lightning Fast, On-Device TTS

[![Demo](https://img.shields.io/badge/🤗%20Hugging%20Face-Demo-yellow)](https://huggingface.co/spaces/Supertone/supertonic#interactive-demo)
[![Models](https://img.shields.io/badge/🤗%20Hugging%20Face-Models-blue)](https://huggingface.co/Supertone/supertonic)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

<p align="center">
  <img src="img/Supertonic_IMG_v02_4x.webp" alt="Supertonic Banner" width="600">
</p>

**Supertonic** 是一个极速、设备端文本转语音系统，专为**极致性能**和最小计算开销而设计。基于 ONNX Runtime，完全在您的设备上运行——无需云端、无需 API 调用、无需隐私担忧。

> 🎧 **立即体验**: 在浏览器中使用我们的 [**交互式演示**](https://huggingface.co/spaces/Supertone/supertonic#interactive-demo)，或从 [**Hugging Face Hub**](https://huggingface.co/Supertone/supertonic) 获取预训练模型

## ✨ 主要特性

- **⚡ 极速生成**: 在消费级硬件（M4 Pro）上可达到**实时速度的 167 倍**——超越任何其他 TTS 系统
- **🪶 超轻量级**: 仅 **66M 参数**，针对设备端高效性能优化，占用空间极小
- **📱 设备端运行**: **完全隐私保护**和**零延迟**——所有处理都在本地设备上进行
- **🎨 自然文本处理**: 无缝处理数字、日期、货币、缩写和复杂表达式，无需预处理
- **⚙️ 高度可配置**: 可调整推理步数、批处理和其他参数以满足您的特定需求
- **🧩 灵活部署**: 可在服务器、浏览器和边缘设备上无缝部署，支持多种运行时后端
- **🌐 Web UI**: 美观易用的 Streamlit 图形界面，支持实时语音生成和预览
- **🚀 RESTful API**: 基于 FastAPI 的完整 API 服务，支持 Swagger 文档和自动验证
- **🐳 Docker 支持**: 一键部署，支持 GPU 加速，开箱即用

## 📋 目录

- [快速开始](#快速开始)
  - [一键部署（3 步完成）](#一键部署3-步完成)
  - [Docker 镜像构建详解](#docker-镜像构建详解)
  - [管理服务](#管理服务)
- [功能特性](#功能特性)
- [使用指南](#使用指南)
  - [Web UI 使用](#web-ui-使用)
  - [API 调用方法](#api-调用方法)
    - [四种语音风格调用](#2-四种语音风格调用)
    - [Python/JavaScript 完整示例](#6-python-客户端完整示例)
- [API 文档](#api-文档)
- [语言支持](#语言支持)
- [性能指标](#性能指标)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 🚀 快速开始

### 前置要求

- **Docker** 和 **Docker Compose**（必需）
- **NVIDIA GPU**（可选，用于 GPU 加速，推荐）
- **Git LFS**（用于下载模型文件）

### 一键部署（3 步完成）

#### 步骤 1: 克隆仓库并下载模型

```bash
# 克隆仓库
git clone https://github.com/neosun100/supertonic-tts-enhanced.git
cd supertonic-tts-enhanced

# 下载模型文件（约 200MB，需要 Git LFS）
./download_models.sh
```

> **注意**: 如果 `download_models.sh` 执行失败，请确保已安装 Git LFS：
> ```bash
> # macOS
> brew install git-lfs && git lfs install
> # Ubuntu/Debian
> sudo apt-get install git-lfs && git lfs install
> ```

#### 步骤 2: 构建 Docker 镜像

```bash
# 构建所有服务镜像（首次构建需要 5-10 分钟）
docker-compose build

# 或者只构建 API 服务器
docker-compose build supertonic-tts-server

# 或者只构建 Web UI
docker-compose build supertonic-tts-ui
```

**构建说明**:
- **TTS 服务器镜像** (`Dockerfile`): 基于 NVIDIA CUDA 12.6.3，包含 ONNX Runtime GPU 支持
- **Web UI 镜像** (`Dockerfile.streamlit`): 基于 Python 3.10，包含 Streamlit 和依赖
- 首次构建会下载基础镜像和依赖，需要一些时间
- 后续构建会使用缓存，速度更快

#### 步骤 3: 启动服务

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

**服务说明**:
- **API 服务器**: 运行在 `http://localhost:8088`
- **Web UI**: 运行在 `http://localhost:8501`
- **Swagger 文档**: `http://localhost:8088/docs`

#### 验证部署

```bash
# 检查 API 服务健康状态
curl http://localhost:8088/health

# 预期响应:
# {"status":"healthy","service":"Supertonic TTS","gpu_enabled":true}
```

### Docker 镜像构建详解

#### 构建 TTS 服务器镜像

```bash
# 使用 Dockerfile 构建
docker build -t supertonic-tts:latest -f Dockerfile .

# 查看构建过程
docker build --progress=plain -t supertonic-tts:latest -f Dockerfile .

# 不使用缓存重新构建
docker build --no-cache -t supertonic-tts:latest -f Dockerfile .
```

**Dockerfile 说明**:
```dockerfile
# 基础镜像: NVIDIA CUDA 12.6.3 (支持 GPU)
FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip git git-lfs \
    libsndfile1 ffmpeg wget curl

# 安装 Python 依赖（包括 GPU 支持）
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

#### 构建 Web UI 镜像

```bash
# 使用 Dockerfile.streamlit 构建
docker build -t supertonic-tts-ui:latest -f Dockerfile.streamlit .
```

**Dockerfile.streamlit 说明**:
```dockerfile
# 基础镜像: Python 3.10
FROM python:3.10-slim

# 安装系统依赖（包括 curl 用于健康检查）
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY streamlit_requirements.txt .
RUN pip install --no-cache-dir -r streamlit_requirements.txt

# 复制 Streamlit 应用
COPY streamlit_app.py .
EXPOSE 8501
```

#### 自定义构建

**修改 GPU 版本**:
```dockerfile
# 编辑 Dockerfile，修改 CUDA 版本
FROM nvidia/cuda:11.8.0-cudnn-runtime-ubuntu22.04  # 改为你需要的版本
```

**修改 Python 版本**:
```dockerfile
# 编辑 Dockerfile，修改 Python 版本
RUN apt-get install -y python3.11 python3-pip  # 改为你需要的版本
```

**添加额外依赖**:
```dockerfile
# 在安装 Python 依赖部分添加
RUN pip3 install --no-cache-dir \
    your-package-name \
    ...
```

#### 验证镜像

```bash
# 查看镜像列表
docker images | grep supertonic

# 检查镜像大小
docker images supertonic-tts
docker images supertonic-tts-ui

# 测试运行
docker run --rm supertonic-tts:latest python3 --version
docker run --rm supertonic-tts:latest nvidia-smi  # 如果支持 GPU
```

### 管理服务

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f supertonic-tts-server  # API 服务日志
docker-compose logs -f supertonic-tts-ui     # UI 服务日志

# 进入容器
docker exec -it supertonic-tts-server bash
docker exec -it supertonic-tts-ui bash

# 查看资源使用
docker stats supertonic-tts-server
```

## 🎯 功能特性

### Web UI 界面

- 🎨 **美观的图形界面**: 基于 Streamlit 的现代化 Web 界面
- 🎤 **4 种语音风格**: 男声（M1, M2）和女声（F1, F2）
- ⚙️ **参数调节**: 可调整去噪步数（1-20）和语速（0.5-2.0x）
- 📊 **实时统计**: 显示字符数、预计时长、生成时间等
- 🔊 **在线播放**: 内嵌音频播放器，即时试听
- 📥 **一键下载**: 生成的音频文件可直接下载
- 📜 **历史记录**: 自动保存最近 20 次生成记录

### RESTful API

- 🔥 **FastAPI 框架**: 高性能异步 API 服务
- 📚 **Swagger 文档**: 自动生成的交互式 API 文档
- ✅ **请求验证**: 自动验证请求参数和类型
- 🎯 **类型安全**: 使用 Pydantic 模型确保类型安全
- 📝 **完整文档**: 包含示例和详细说明
- 🔒 **安全特性**: 支持 CORS、速率限制等

### 核心功能

- ⚡ **GPU 加速**: 支持 NVIDIA GPU 加速
- 🎤 **高质量合成**: 可生成自然流畅的语音
- 🌍 **多语言支持**: 支持多种语言和方言
- 📱 **跨平台**: 支持多种编程语言和平台

## 📦 部署方式

### Docker 部署（推荐）

#### 基本部署

```bash
# 1. 下载模型
./download_models.sh

# 2. 启动所有服务
docker-compose up -d

# 3. 查看服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f
```

#### 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| `supertonic-tts-server` | 8088 | FastAPI 服务器（GPU 加速） |
| `supertonic-tts-ui` | 8501 | Streamlit Web UI |

#### GPU 配置

默认使用 GPU 2，如需更改，编辑 `docker-compose.yml`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          device_ids: ['0']  # 改为你想使用的 GPU 编号
```

#### 管理命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f supertonic-tts-server
docker-compose logs -f supertonic-tts-ui

# 进入容器
docker exec -it supertonic-tts-server bash
```

详细 Docker 配置说明请参考 [DOCKER_SETUP.md](DOCKER_SETUP.md)

### 本地安装

#### Python 环境

```bash
cd py
uv sync  # 或 pip install -r requirements.txt
uv run example_onnx.py
```

#### 其他语言

请参考各语言目录下的 README 文件。

## 📖 使用指南

### Web UI 使用

1. **访问界面**: 打开浏览器访问 http://localhost:8501

2. **选择语音**: 在左侧边栏选择语音风格
   - **M1**: 标准男声，适合新闻播报
   - **M2**: 年轻男声，适合对话讲解
   - **F1**: 温柔女声，适合有声读物
   - **F2**: 活泼女声，适合广告客服

3. **调整参数**:
   - **去噪步骤**: 1-20（推荐 5，质量与速度平衡）
   - **语速**: 0.5-2.0x（推荐 1.05，正常语速）

4. **输入文本**: 在文本框中输入要转换的文本

5. **生成语音**: 点击 "🎬 生成语音" 按钮

6. **播放/下载**: 使用内嵌播放器试听或点击下载链接

详细 UI 使用指南请参考 [UI_ACCESS_GUIDE.md](UI_ACCESS_GUIDE.md)

### API 调用方法

#### 1. 健康检查

首先检查服务是否正常运行：

```bash
curl http://localhost:8088/health
```

**响应示例**:
```json
{
  "status": "healthy",
  "service": "Supertonic TTS",
  "gpu_enabled": true
}
```

#### 2. 四种语音风格调用

Supertonic TTS 提供 **4 种预设语音风格**，每种都有不同的特点：

| 语音风格 | 文件路径 | 特点 | 适用场景 |
|---------|---------|------|----------|
| **M1** (男声 1) | `assets/voice_styles/M1.json` | 标准男声，沉稳 | 新闻播报、叙述、正式场合 |
| **M2** (男声 2) | `assets/voice_styles/M2.json` | 年轻男声，活泼 | 对话、讲解、教育内容 |
| **F1** (女声 1) | `assets/voice_styles/F1.json` | 温柔女声，柔和 | 有声读物、导航、温馨内容 |
| **F2** (女声 2) | `assets/voice_styles/F2.json` | 活泼女声，明亮 | 广告、客服、轻松内容 |

##### 使用 M1 (标准男声)

```bash
curl -X POST http://localhost:8088/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "欢迎使用 Supertonic TTS，这是标准男声的测试。",
    "voice_style": "assets/voice_styles/M1.json",
    "total_steps": 5,
    "speed": 1.05
  }'
```

##### 使用 M2 (年轻男声)

```bash
curl -X POST http://localhost:8088/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，这是年轻男声的测试，声音更加活泼。",
    "voice_style": "assets/voice_styles/M2.json",
    "total_steps": 5,
    "speed": 1.05
  }'
```

##### 使用 F1 (温柔女声)

```bash
curl -X POST http://localhost:8088/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "欢迎使用 Supertonic TTS，这是温柔女声的测试。",
    "voice_style": "assets/voice_styles/F1.json",
    "total_steps": 5,
    "speed": 1.05
  }'
```

##### 使用 F2 (活泼女声)

```bash
curl -X POST http://localhost:8088/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，这是活泼女声的测试，声音更加明亮。",
    "voice_style": "assets/voice_styles/F2.json",
    "total_steps": 5,
    "speed": 1.05
  }'
```

#### 3. API 响应格式

所有语音合成请求返回相同的格式：

```json
{
  "status": "success",
  "output_file": "output_1234567890.wav",
  "generation_time": 0.417,
  "text_length": 20,
  "audio_duration": 4.15
}
```

**字段说明**:
- `status`: 请求状态（"success" 表示成功）
- `output_file`: 生成的音频文件名
- `generation_time`: 生成耗时（秒）
- `text_length`: 输入文本长度（字符数）
- `audio_duration`: 生成的音频时长（秒）

#### 4. 下载音频文件

生成成功后，使用返回的 `output_file` 下载音频：

```bash
# 方法 1: 使用 curl 下载
curl -O http://localhost:8088/output_1234567890.wav

# 方法 2: 使用 wget 下载
wget http://localhost:8088/output_1234567890.wav

# 方法 3: 直接播放（需要 ffplay）
curl -s http://localhost:8088/output_1234567890.wav | ffplay -nodisp -autoexit -
```

#### 5. 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `text` | string | ✅ | - | 要合成的文本（必需） |
| `voice_style` | string | ❌ | `M1.json` | 语音风格文件路径 |
| `total_steps` | int | ❌ | 5 | 去噪步数（1-50），越高质量越好但越慢 |
| `speed` | float | ❌ | 1.05 | 语速倍数（0.5-2.0） |

**参数建议**:
- **total_steps**: 
  - `1-3`: 快速模式，质量较低，适合测试
  - `4-7`: 平衡模式（推荐），质量与速度平衡
  - `8-20`: 高质量模式，速度较慢，适合重要内容
- **speed**: 
  - `0.5-0.9`: 慢速，适合有声读物
  - `0.9-1.1`: 正常语速（推荐）
  - `1.1-1.5`: 快速，适合快速浏览
  - `1.5-2.0`: 极速，可能影响清晰度

#### 6. Python 客户端完整示例

```python
import requests
import os

# API 配置
API_URL = "http://localhost:8088"

def synthesize_speech(text, voice_style="M1", total_steps=5, speed=1.05):
    """
    调用 API 生成语音
    
    Args:
        text: 要转换的文本
        voice_style: 语音风格 (M1, M2, F1, F2)
        total_steps: 去噪步数
        speed: 语速倍数
    
    Returns:
        dict: API 响应结果
    """
    url = f"{API_URL}/synthesize"
    
    payload = {
        "text": text,
        "voice_style": f"assets/voice_styles/{voice_style}.json",
        "total_steps": total_steps,
        "speed": speed
    }
    
    try:
        print(f"📤 生成语音: {text[:50]}...")
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ 生成成功!")
        print(f"   文件: {result['output_file']}")
        print(f"   耗时: {result['generation_time']}秒")
        print(f"   时长: {result['audio_duration']}秒")
        
        # 下载音频
        download_audio(result['output_file'])
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None

def download_audio(filename):
    """下载生成的音频文件"""
    url = f"{API_URL}/{filename}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        abs_path = os.path.abspath(filename)
        print(f"💾 音频已保存: {abs_path}")
        return abs_path
    except requests.exceptions.RequestException as e:
        print(f"❌ 下载失败: {e}")
        return None

# 使用示例：测试所有语音风格
if __name__ == "__main__":
    test_text = "欢迎使用 Supertonic TTS 文本转语音系统。"
    
    # 测试所有四种语音风格
    voices = ["M1", "M2", "F1", "F2"]
    for voice in voices:
        print(f"\n{'='*60}")
        print(f"测试语音风格: {voice}")
        print(f"{'='*60}")
        synthesize_speech(test_text, voice_style=voice)
```

#### 7. JavaScript/Node.js 客户端完整示例

```javascript
const http = require('http');
const fs = require('fs');

const API_URL = 'http://localhost:8088';

/**
 * 调用 API 生成语音
 */
function synthesizeSpeech(text, voiceStyle = 'M1', totalSteps = 5, speed = 1.05) {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify({
            text: text,
            voice_style: `assets/voice_styles/${voiceStyle}.json`,
            total_steps: totalSteps,
            speed: speed
        });

        const options = {
            hostname: 'localhost',
            port: 8088,
            path: '/synthesize',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': data.length
            }
        };

        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => { body += chunk; });
            res.on('end', () => {
                if (res.statusCode === 200) {
                    const result = JSON.parse(body);
                    console.log('✅ 生成成功!');
                    console.log(`   文件: ${result.output_file}`);
                    console.log(`   耗时: ${result.generation_time}秒`);
                    console.log(`   时长: ${result.audio_duration}秒`);
                    
                    // 下载音频
                    downloadAudio(result.output_file).then(() => {
                        resolve(result);
                    });
                } else {
                    reject(new Error(`HTTP ${res.statusCode}: ${body}`));
                }
            });
        });

        req.on('error', reject);
        req.write(data);
        req.end();
    });
}

/**
 * 下载音频文件
 */
function downloadAudio(filename) {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(filename);
        http.get(`${API_URL}/${filename}`, (response) => {
            response.pipe(file);
            file.on('finish', () => {
                file.close();
                console.log(`💾 音频已保存: ${filename}`);
                resolve(filename);
            });
        }).on('error', reject);
    });
}

// 使用示例：测试所有语音风格
const testText = '欢迎使用 Supertonic TTS 文本转语音系统。';
const voices = ['M1', 'M2', 'F1', 'F2'];

async function testAllVoices() {
    for (const voice of voices) {
        console.log(`\n${'='.repeat(60)}`);
        console.log(`测试语音风格: ${voice}`);
        console.log('='.repeat(60));
        try {
            await synthesizeSpeech(testText, voice);
        } catch (error) {
            console.error(`❌ 错误: ${error.message}`);
        }
    }
}

testAllVoices();
```

#### 8. cURL 批量测试脚本

```bash
#!/bin/bash
# 测试所有四种语音风格

API_URL="http://localhost:8088"
TEST_TEXT="欢迎使用 Supertonic TTS 文本转语音系统。"

echo "测试 Supertonic TTS API - 所有语音风格"
echo "========================================"

for voice in "M1" "M2" "F1" "F2"; do
    echo ""
    echo "测试语音风格: $voice"
    echo "----------------------------------------"
    
    # 生成语音
    response=$(curl -s -X POST "$API_URL/synthesize" \
        -H "Content-Type: application/json" \
        -d "{
            \"text\": \"$TEST_TEXT\",
            \"voice_style\": \"assets/voice_styles/${voice}.json\",
            \"total_steps\": 5,
            \"speed\": 1.05
        }")
    
    # 提取文件名
    filename=$(echo $response | grep -o '"output_file":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$filename" ]; then
        echo "✅ 生成成功: $filename"
        
        # 下载音频
        curl -s -O "$API_URL/$filename"
        echo "💾 已下载: $filename"
    else
        echo "❌ 生成失败"
    fi
done

echo ""
echo "========================================"
echo "✅ 所有测试完成!"
```

保存为 `test_voices.sh`，添加执行权限后运行：
```bash
chmod +x test_voices.sh
./test_voices.sh
```

#### 9. 在线 API 文档

访问 Swagger UI 查看完整的交互式 API 文档：

```
http://localhost:8088/docs
```

在 Swagger UI 中，你可以：
- 查看所有 API 端点
- 查看请求/响应格式
- 直接在浏览器中测试 API
- 查看参数说明和示例

---

**更多 API 使用示例请参考**: [examples/README.md](examples/README.md)


## 📚 API 文档

### Swagger UI（交互式文档）

访问 http://localhost:8088/docs 查看完整的交互式 API 文档。

**特性**:
- ✅ 直接在浏览器中测试 API
- ✅ 查看请求/响应模型
- ✅ 自动生成示例代码
- ✅ 在线试用所有端点

### ReDoc（美观文档）

访问 http://localhost:8088/redoc 查看美观的 API 参考文档。

### OpenAPI 规范

访问 http://localhost:8088/openapi.json 获取完整的 OpenAPI 规范（可用于生成客户端代码）。

详细 API 使用指南请参考 [SWAGGER_API_GUIDE.md](SWAGGER_API_GUIDE.md)

## 🌍 语言支持

我们提供跨多个生态系统的 TTS 推理示例：

| 语言/平台 | 路径 | 说明 |
|-----------|------|------|
| [**Python**](py/) | `py/` | ONNX Runtime 推理 |
| [**Node.js**](nodejs/) | `nodejs/` | 服务端 JavaScript |
| [**Browser**](web/) | `web/` | WebGPU/WASM 推理 |
| [**Java**](java/) | `java/` | 跨平台 JVM |
| [**C++**](cpp/) | `cpp/` | 高性能 C++ |
| [**C#**](csharp/) | `csharp/` | .NET 生态系统 |
| [**Go**](go/) | `go/` | Go 实现 |
| [**Swift**](swift/) | `swift/` | macOS 应用 |
| [**iOS**](ios/) | `ios/` | 原生 iOS 应用 |
| [**Rust**](rust/) | `rust/` | 内存安全的系统语言 |

> 详细使用说明请参考各语言目录下的 README.md 文件。

## 📊 性能指标

### 字符每秒（Characters per Second）

| 系统 | Short (59 chars) | Mid (152 chars) | Long (266 chars) |
|------|-----------------|----------------|-----------------|
| **Supertonic** (M4 pro - CPU) | 912 | 1048 | 1263 |
| **Supertonic** (M4 pro - WebGPU) | 996 | 1801 | 2509 |
| **Supertonic** (RTX4090) | 2615 | 6548 | 12164 |
| `API` ElevenLabs Flash v2.5 | 144 | 209 | 287 |
| `API` OpenAI TTS-1 | 37 | 55 | 82 |
| `API` Gemini 2.5 Flash TTS | 12 | 18 | 24 |
| `Open` Kokoro | 104 | 107 | 117 |
| `Open` NeuTTS Air | 37 | 42 | 47 |

### 实时因子（Real-time Factor）

| 系统 | Short (59 chars) | Mid (152 chars) | Long (266 chars) |
|------|-----------------|----------------|-----------------|
| **Supertonic** (M4 pro - CPU) | 0.015 | 0.013 | 0.012 |
| **Supertonic** (M4 pro - WebGPU) | 0.014 | 0.007 | 0.006 |
| **Supertonic** (RTX4090) | 0.005 | 0.002 | 0.001 |
| `API` ElevenLabs Flash v2.5 | 0.133 | 0.077 | 0.057 |
| `API` OpenAI TTS-1 | 0.471 | 0.302 | 0.201 |
| `API` Gemini 2.5 Flash TTS | 1.060 | 0.673 | 0.541 |
| `Open` Kokoro | 0.144 | 0.124 | 0.126 |
| `Open` NeuTTS Air | 0.390 | 0.338 | 0.343 |

> **说明**:  
> `API` = 基于云端的 API 服务（从首尔测量）  
> `Open` = 开源模型  
> Supertonic (M4 pro - CPU) 和 (M4 pro - WebGPU): 使用 ONNX 测试  
> Supertonic (RTX4090): 使用 PyTorch 模型测试

### GPU 性能（实测）

在 NVIDIA L40S GPU 上的实测性能：

| 指标 | 数值 |
|------|------|
| GPU 型号 | NVIDIA L40S (46GB) |
| CUDA 版本 | 12.6.3 |
| 平均生成速度 | ~10x 实时速度 |
| GPU 内存占用 | ~1.1GB |
| 模型参数量 | 66M |
| 音频采样率 | 16 kHz |

## 🔧 配置说明

### 语音风格

项目包含 4 种预设语音风格：

- **M1.json**: 标准男声
- **M2.json**: 年轻男声
- **F1.json**: 温柔女声
- **F2.json**: 活泼女声

位置: `assets/voice_styles/`

### 参数说明

| 参数 | 类型 | 默认值 | 范围 | 说明 |
|------|------|--------|------|------|
| `text` | string | - | - | 要合成的文本（必需） |
| `voice_style` | string | M1.json | - | 语音风格文件路径 |
| `total_steps` | int | 5 | 1-50 | 去噪步数，越高质量越好但越慢 |
| `speed` | float | 1.05 | 0.5-2.0 | 语速倍数 |

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `NVIDIA_VISIBLE_DEVICES` | 可见的 GPU 设备 | 2 |
| `CUDA_VISIBLE_DEVICES` | 容器内 GPU 设备映射 | 0 |

## 🐛 常见问题

### Q1: 如何切换 GPU？

编辑 `docker-compose.yml` 中的 `device_ids`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          device_ids: ['0']  # 改为你想使用的 GPU 编号
```

### Q2: 如何提高生成质量？

增加 `total_steps` 参数（例如：10-20），但会降低生成速度。

### Q3: 如何调整语速？

修改 `speed` 参数：
- 0.5-0.9: 慢速
- 0.9-1.1: 正常（推荐）
- 1.1-1.5: 快速
- 1.5-2.0: 极速

### Q4: 容器无法访问 GPU？

确保已安装 NVIDIA Docker runtime:

```bash
# 检查 nvidia-docker
docker run --rm --gpus all nvidia/cuda:12.6.3-base-ubuntu22.04 nvidia-smi
```

### Q5: 如何查看服务日志？

```bash
# API 服务日志
docker-compose logs -f supertonic-tts-server

# UI 服务日志
docker-compose logs -f supertonic-tts-ui
```

### Q6: 如何从其他机器访问？

1. 确保防火墙开放端口 8088 和 8501
2. 使用服务器 IP 地址访问: `http://<服务器IP>:8501`
3. 详细说明请参考 [NETWORK_ACCESS.md](NETWORK_ACCESS.md)

更多问题请参考：
- [QUICK_START.md](QUICK_START.md) - 快速启动指南
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Docker 配置说明
- [UI_ACCESS_GUIDE.md](UI_ACCESS_GUIDE.md) - UI 使用指南
- [SWAGGER_API_GUIDE.md](SWAGGER_API_GUIDE.md) - API 使用指南

## 📖 相关文档

- [**使用指南**](USAGE_GUIDE.md) - ⭐ **各语言调用方法和 Docker 构建说明**
- [快速开始指南](QUICK_START.md) - 快速部署和使用
- [Docker 部署指南](DOCKER_SETUP.md) - 详细的 Docker 配置说明
- [Web UI 使用指南](UI_ACCESS_GUIDE.md) - Streamlit UI 完整使用说明
- [API 使用指南](SWAGGER_API_GUIDE.md) - FastAPI 和 Swagger 文档
- [网络访问配置](NETWORK_ACCESS.md) - 局域网和公网访问配置
- [Nginx 反向代理](NGINX_PROXY_SETUP.md) - 生产环境部署配置
- [音频下载指南](AUDIO_DOWNLOAD_GUIDE.md) - API 音频文件下载说明
- [部署总结](DEPLOYMENT_SUMMARY.md) - 完整部署过程记录

## 🤝 贡献指南

我们欢迎所有形式的贡献！请参考以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目示例代码采用 **MIT License** - 详见 [LICENSE](LICENSE) 文件。

模型文件采用 **OpenRAIL-M License** - 详见 [Hugging Face LICENSE](https://huggingface.co/Supertone/supertonic/blob/main/LICENSE)。

模型训练使用 PyTorch，采用 **BSD 3-Clause License**，但本项目不重新分发 PyTorch。

Copyright (c) 2025 Supertone Inc.

## 🙏 致谢

- [Supertone Inc.](https://github.com/supertone-inc) - 原始项目开发者
- [Hugging Face](https://huggingface.co/Supertone/supertonic) - 模型托管
- [ONNX Runtime](https://onnxruntime.ai/) - 推理引擎
- [FastAPI](https://fastapi.tiangolo.com/) - API 框架
- [Streamlit](https://streamlit.io/) - Web UI 框架

## 📞 支持

- **GitHub Issues**: [提交问题](https://github.com/neosun100/supertonic-tts-enhanced/issues)
- **Hugging Face**: [模型页面](https://huggingface.co/Supertone/supertonic)
- **在线演示**: [交互式演示](https://huggingface.co/spaces/Supertone/supertonic)

---

<p align="center">
  <b>⭐ 如果这个项目对你有帮助，请给我们一个 Star！⭐</b>
</p>
