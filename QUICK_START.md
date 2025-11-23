# Supertonic TTS - Docker 快速启动指南

## ✅ 已完成配置

Supertonic TTS 已成功配置为 Docker 服务，支持 **GPU 加速**！

## 🚀 服务状态

当前服务正在运行：
- **容器名称**: `supertonic-tts-server`
- **访问端口**: `8088` (映射到容器的 8000)
- **GPU 支持**: ✅ 已启用 (CUDA)
- **重启策略**: `always` (自动重启)

## 📡 API 端点

### 健康检查
```bash
curl http://localhost:8088/health
```

**响应示例:**
```json
{
  "status": "healthy",
  "service": "Supertonic TTS",
  "gpu_enabled": true
}
```

### 语音合成
```bash
curl -X POST http://localhost:8088/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of GPU-accelerated text to speech.",
    "total_steps": 5,
    "speed": 1.05,
    "voice_style": "assets/voice_styles/M1.json"
  }'
```

**请求参数:**
- `text` (必需): 要转换的文本
- `total_steps` (可选): 去噪步骤数，默认 5，越高质量越好但越慢
- `speed` (可选): 语速，默认 1.05，范围 0.9-1.5
- `voice_style` (可选): 语音风格文件路径，默认 M1.json

**可用的语音风格:**
- `assets/voice_styles/M1.json` - 男声 1
- `assets/voice_styles/M2.json` - 男声 2
- `assets/voice_styles/F1.json` - 女声 1
- `assets/voice_styles/F2.json` - 女声 2

**响应示例:**
```json
{
  "status": "success",
  "output_file": "output_1763824659.wav",
  "generation_time": 0.417,
  "text_length": 53,
  "audio_duration": 4.0025
}
```

## 📁 输出文件

生成的音频文件保存在：
```bash
./results/
```

所有 API 生成的文件格式为：`output_<timestamp>.wav`

## 🔧 Docker 命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
docker-compose logs supertonic-tts-server
# 或实时查看
docker-compose logs -f supertonic-tts-server
```

### 重启服务
```bash
docker-compose restart supertonic-tts-server
```

### 停止服务
```bash
docker-compose down
```

### 启动服务
```bash
docker-compose up -d supertonic-tts-server
```

## 🎮 高级用法

### 使用不同的 GPU
编辑 `docker-compose.yml`，修改环境变量：
```yaml
environment:
  - NVIDIA_VISIBLE_DEVICES=1  # 使用 GPU 1
  - CUDA_VISIBLE_DEVICES=1
```

### 使用所有 GPU
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

### 命令行直接运行（一次性）
```bash
docker-compose run --rm supertonic-tts python3 example_onnx.py \
  --text "Your text here" \
  --voice-style assets/voice_styles/F1.json \
  --total-step 10
```

### 进入容器交互式 Shell
```bash
docker exec -it supertonic-tts-server bash
```

在容器内可以运行：
```bash
# 测试 CPU 模式
python3 example_onnx.py --text "Test"

# 测试 GPU 模式
python3 example_onnx.py --use-gpu --text "Test"
```

## 📊 性能信息

**当前配置:**
- GPU: NVIDIA L40S
- CUDA: 12.6.3
- ONNX Runtime: 1.23.2 (GPU)

**预期性能:**
- CPU 模式: ~0.2秒/句 (中等长度文本)
- GPU 模式: 更快 (取决于 GPU 型号和文本长度)

## 🔍 故障排除

### 容器一直重启
```bash
# 查看日志找出原因
docker-compose logs --tail 100 supertonic-tts-server
```

### GPU 访问失败
```bash
# 检查 GPU 是否可用
docker run --rm --gpus all nvidia/cuda:12.6.3-base-ubuntu22.04 nvidia-smi
```

### 端口冲突
如果端口 8088 被占用，修改 `docker-compose.yml`:
```yaml
ports:
  - "8089:8000"  # 改用 8089
```

### 重新构建镜像
如果修改了代码：
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d supertonic-tts-server
```

## 📝 Python 客户端示例

```python
import requests
import json

# TTS API 端点
url = "http://localhost:8088/synthesize"

# 请求数据
data = {
    "text": "这是一个语音合成测试。",
    "total_steps": 5,
    "speed": 1.0,
    "voice_style": "assets/voice_styles/F2.json"
}

# 发送请求
response = requests.post(url, json=data)
result = response.json()

print(f"生成成功！文件: {result['output_file']}")
print(f"耗时: {result['generation_time']}秒")
print(f"音频时长: {result['audio_duration']}秒")
```

## 🔐 生产环境建议

1. **端口安全**: 考虑使用反向代理（Nginx）并添加认证
2. **资源限制**: 在 docker-compose.yml 中添加 CPU/内存限制
3. **日志管理**: 配置日志轮转避免磁盘占满
4. **监控**: 使用 Prometheus + Grafana 监控服务状态
5. **备份**: 定期备份 results 目录

## 📚 更多信息

- 项目文档: [README.md](README.md)
- Docker 详细配置: [DOCKER_SETUP.md](DOCKER_SETUP.md)
- 原始项目: https://github.com/supertone-inc/supertonic
- Hugging Face: https://huggingface.co/Supertone/supertonic

## 🎯 下一步

1. 测试不同的语音风格
2. 调整 `total_steps` 参数找到质量和速度的最佳平衡
3. 尝试长文本合成
4. 集成到你的应用中

---

**享受使用 Supertonic TTS！** 🎤✨
