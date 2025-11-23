# Supertonic Docker 部署指南

本文档介绍如何使用 Docker 运行 Supertonic TTS 项目，支持 GPU 加速。

## 系统要求

- Docker 和 Docker Compose
- NVIDIA GPU（推荐）
- NVIDIA Docker runtime（nvidia-container-toolkit）
- Git LFS（用于下载模型）

## 快速开始

### 1. 下载模型文件

首先需要下载 ONNX 模型和预设声音文件：

```bash
./download_models.sh
```

这个脚本会从 Hugging Face 下载约 200MB 的模型文件到 `assets` 目录。

### 2. 构建 Docker 镜像

```bash
docker-compose build
```

### 3. 运行容器（GPU 模式）

使用默认配置运行（使用 GPU 0）：

```bash
docker-compose up supertonic-tts
```

或者后台运行：

```bash
docker-compose up -d supertonic-tts
```

### 4. 查看生成的音频文件

生成的音频文件会保存在 `./results` 目录中。

## 高级用法

### 指定使用的 GPU

编辑 `docker-compose.yml` 文件，修改以下配置：

```yaml
environment:
  - NVIDIA_VISIBLE_DEVICES=0  # 改为你想使用的 GPU 编号
  - CUDA_VISIBLE_DEVICES=0
```

使用所有 GPU：

```yaml
environment:
  - NVIDIA_VISIBLE_DEVICES=all
  - CUDA_VISIBLE_DEVICES=all

deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all  # 改为 all
          capabilities: [gpu]
```

### 运行自定义命令

进入容器的交互式 Shell：

```bash
docker-compose run --rm supertonic-tts bash
```

在容器内运行自定义命令：

```bash
# 使用不同的 voice style
python3 example_onnx.py --use-gpu \
  --voice-style assets/voice_styles/F1.json \
  --text "Hello, this is a test."

# 高质量模式（更多去噪步骤）
python3 example_onnx.py --use-gpu --total-step 10

# 批量处理
python3 example_onnx.py --use-gpu \
  --voice-style assets/voice_styles/M1.json assets/voice_styles/F1.json \
  --text "First text." "Second text." \
  --batch

# 调整语速
python3 example_onnx.py --use-gpu \
  --speed 1.2 \
  --text "This is faster speech."
```

### CPU 模式（如果没有 GPU）

如果你想在没有 GPU 的情况下运行：

```bash
docker-compose --profile cpu up supertonic-tts-cpu
```

### 一次性运行并退出

```bash
docker-compose run --rm supertonic-tts python3 example_onnx.py --use-gpu
```

## 目录结构

```
supertonic/
├── Dockerfile                 # Docker 镜像定义
├── docker-compose.yml         # Docker Compose 配置
├── download_models.sh         # 模型下载脚本
├── DOCKER_SETUP.md           # 本文档
├── assets/                    # 模型和语音样式文件（需要下载）
│   ├── onnx/                 # ONNX 模型文件
│   └── voice_styles/         # 预设语音样式
├── py/                        # Python 实现
│   ├── example_onnx.py       # 主示例脚本
│   ├── helper.py             # 辅助函数
│   └── requirements.txt      # Python 依赖
└── results/                   # 输出音频文件（自动创建）
```

## 故障排除

### 1. GPU 访问问题

如果遇到 GPU 无法访问的错误：

```bash
# 检查 nvidia-docker 是否正确安装
docker run --rm --gpus all nvidia/cuda:12.6.3-base-ubuntu22.04 nvidia-smi

# 检查 Docker 是否能看到 GPU
docker-compose run --rm supertonic-tts nvidia-smi
```

### 2. 模型文件缺失

如果提示模型文件不存在：

```bash
# 确保已下载模型
ls -la assets/

# 重新下载模型
rm -rf assets
./download_models.sh
```

### 3. 内存不足

如果遇到内存问题，可以减少批量大小或降低质量：

```bash
# 减少去噪步骤
python3 example_onnx.py --use-gpu --total-step 2

# 单独处理（不使用 batch）
python3 example_onnx.py --use-gpu
```

### 4. 查看容器日志

```bash
docker-compose logs supertonic-tts
```

## 性能优化

### GPU 选择

如果你有多个 GPU，选择空闲的 GPU 可以获得更好的性能：

```bash
# 查看 GPU 使用情况
nvidia-smi

# 修改 docker-compose.yml 使用特定 GPU
NVIDIA_VISIBLE_DEVICES=1  # 使用 GPU 1
```

### 批量处理

对于大量文本，使用批量处理可以提高效率：

```bash
python3 example_onnx.py --use-gpu \
  --voice-style assets/voice_styles/M1.json assets/voice_styles/M1.json \
  --text "Text 1" "Text 2" \
  --batch
```

## 清理

停止容器：

```bash
docker-compose down
```

删除镜像（如果需要重新构建）：

```bash
docker-compose down --rmi all
docker image prune -f
```

## 技术细节

- **基础镜像**: nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04
- **Python 版本**: 3.10
- **ONNX Runtime**: 1.23.1 (GPU 版本)
- **CUDA 版本**: 12.6.3
- **GPU 架构支持**: 所有 NVIDIA GPU（需要 CUDA 支持）

## 参考资源

- [Supertonic GitHub](https://github.com/supertone-inc/supertonic)
- [Hugging Face Models](https://huggingface.co/Supertone/supertonic)
- [NVIDIA Docker 文档](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
