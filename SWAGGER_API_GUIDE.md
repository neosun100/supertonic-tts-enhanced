# Swagger API 使用指南 / Swagger API Usage Guide

## 概述 / Overview

本项目提供了两个 API 服务器版本：

1. **基础版本** (`tts_server.py`) - 使用 Python HTTPServer，轻量级
2. **FastAPI 版本** (`tts_server_fastapi.py`) - 带有完整的 Swagger/OpenAPI 文档支持 ✨ **推荐**

This project provides two API server versions:

1. **Basic version** (`tts_server.py`) - Using Python HTTPServer, lightweight
2. **FastAPI version** (`tts_server_fastapi.py`) - With complete Swagger/OpenAPI documentation support ✨ **Recommended**

---

## FastAPI 版本特性 / FastAPI Version Features

### ✨ 主要特性 / Key Features

- 🔥 **自动生成 Swagger UI** - 交互式 API 文档
- 📚 **ReDoc 文档** - 美观的 API 参考文档
- ✅ **请求验证** - 自动验证请求参数
- 🎯 **类型安全** - 使用 Pydantic 模型确保类型安全
- 📝 **详细的 API 描述** - 包含示例和说明
- ⚡ **高性能** - 基于 Starlette 的异步框架

---

## 安装依赖 / Install Dependencies

### 方式 1：使用 FastAPI requirements

```bash
pip install -r py/requirements_fastapi.txt
```

### 方式 2：手动安装

```bash
pip install fastapi uvicorn[standard] pydantic
```

---

## 启动服务 / Start the Server

### 本地运行 / Run Locally

```bash
cd py
python3 tts_server_fastapi.py --host 0.0.0.0 --port 8000
```

### 使用 Docker / Using Docker

#### 1. 修改 Dockerfile

在 `Dockerfile` 中添加 FastAPI 依赖：

```dockerfile
# 在 RUN pip3 install 部分添加
RUN pip3 install --no-cache-dir \
    fastapi>=0.104.0 \
    uvicorn[standard]>=0.24.0 \
    pydantic>=2.0.0 \
    onnxruntime-gpu==1.23.2 \
    numpy>=1.26.0 \
    soundfile>=0.12.1 \
    librosa>=0.10.0 \
    PyYAML>=6.0
```

#### 2. 修改 docker-compose.yml

更新服务命令以使用 FastAPI 服务器：

```yaml
services:
  supertonic-tts-server:
    # ... 其他配置 ...
    command: python3 tts_server_fastapi.py --host 0.0.0.0 --port 8000
```

#### 3. 重建并启动

```bash
docker-compose build
docker-compose up -d
```

---

## 访问 API 文档 / Access API Documentation

启动服务后，可以通过以下 URL 访问文档：

After starting the server, access the documentation via:

### 1. Swagger UI（交互式文档 / Interactive Docs）

```
http://localhost:8088/docs
```

**特性 / Features:**
- ✅ 直接在浏览器中测试 API
- ✅ 查看请求/响应模型
- ✅ 自动生成示例代码
- ✅ 在线试用所有端点

### 2. ReDoc（美观的文档 / Beautiful Docs）

```
http://localhost:8088/redoc
```

**特性 / Features:**
- ✅ 清晰的 API 参考文档
- ✅ 易于阅读的布局
- ✅ 搜索功能
- ✅ 响应式设计

### 3. OpenAPI JSON Schema

```
http://localhost:8088/openapi.json
```

获取完整的 OpenAPI 规范（可用于生成客户端代码）

Get the complete OpenAPI specification (for generating client code)

---

## API 端点说明 / API Endpoints

### 1. 健康检查 / Health Check

**端点 / Endpoint:** `GET /health`

**描述 / Description:** 检查服务是否正常运行

**响应示例 / Response Example:**

```json
{
  "status": "healthy",
  "service": "Supertonic TTS",
  "gpu_enabled": false
}
```

**cURL 示例:**

```bash
curl http://localhost:8088/health
```

---

### 2. 语音合成 / Speech Synthesis

**端点 / Endpoint:** `POST /synthesize`

**描述 / Description:** 将文本转换为语音

**请求参数 / Request Parameters:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| text | string | ✅ | - | 要合成的文本 |
| voice_style | string | ❌ | M1.json | 声音风格文件路径 |
| total_steps | integer | ❌ | 5 | 扩散步数（1-50），越高质量越好但越慢 |
| speed | float | ❌ | 1.05 | 语速倍数（0.5-2.0） |

**请求示例 / Request Example:**

```bash
curl -X POST http://localhost:8088/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of the Supertonic TTS system.",
    "total_steps": 5,
    "speed": 1.05
  }'
```

**响应示例 / Response Example:**

```json
{
  "status": "success",
  "output_file": "output_1234567890.wav",
  "generation_time": 2.345,
  "text_length": 42,
  "audio_duration": 3.5
}
```

---

## 在 Swagger UI 中测试 / Test in Swagger UI

### 步骤 / Steps:

1. 打开浏览器访问 `http://localhost:8088/docs`
2. 找到 `/synthesize` 端点
3. 点击 **"Try it out"** 按钮
4. 填写参数：
   ```json
   {
     "text": "你好，这是一个测试。",
     "total_steps": 5,
     "speed": 1.0
   }
   ```
5. 点击 **"Execute"** 按钮
6. 查看响应结果

---

## Python 客户端示例 / Python Client Example

```python
import requests

# API 地址
API_URL = "http://localhost:8088"

# 1. 检查健康状态
response = requests.get(f"{API_URL}/health")
print("Health:", response.json())

# 2. 合成语音
payload = {
    "text": "Hello, this is a test.",
    "total_steps": 5,
    "speed": 1.05
}

response = requests.post(f"{API_URL}/synthesize", json=payload)
result = response.json()

print(f"Status: {result['status']}")
print(f"Output file: {result['output_file']}")
print(f"Generation time: {result['generation_time']}s")
print(f"Audio duration: {result['audio_duration']}s")
```

---

## JavaScript 客户端示例 / JavaScript Client Example

```javascript
// API 地址
const API_URL = "http://localhost:8088";

// 1. 检查健康状态
async function checkHealth() {
  const response = await fetch(`${API_URL}/health`);
  const data = await response.json();
  console.log("Health:", data);
}

// 2. 合成语音
async function synthesizeSpeech(text) {
  const response = await fetch(`${API_URL}/synthesize`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text: text,
      total_steps: 5,
      speed: 1.05
    })
  });

  const result = await response.json();
  console.log("Result:", result);
  return result;
}

// 使用示例
checkHealth();
synthesizeSpeech("Hello, this is a test.");
```

---

## 常见问题 / FAQ

### Q1: 如何切换回基础版本？

修改 `docker-compose.yml` 中的 command：

```yaml
command: python3 tts_server.py --host 0.0.0.0 --port 8000
```

### Q2: FastAPI 版本性能如何？

FastAPI 是一个高性能异步框架，性能与基础版本相当甚至更好，同时提供了更多功能。

### Q3: 可以自定义 Swagger UI 吗？

可以！在 `tts_server_fastapi.py` 中修改 FastAPI 初始化参数：

```python
app = FastAPI(
    title="Your Custom Title",
    description="Your custom description",
    version="2.0.0"
)
```

### Q4: 如何在生产环境中部署？

推荐使用 Docker 部署，并配置 Nginx 反向代理：

```nginx
location /api {
    proxy_pass http://localhost:8088;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

## 对比：基础版 vs FastAPI 版 / Comparison

| 特性 | 基础版 | FastAPI 版 |
|------|--------|-----------|
| Swagger UI | ❌ | ✅ |
| 请求验证 | ❌ | ✅ |
| 自动文档 | ❌ | ✅ |
| 类型安全 | ❌ | ✅ |
| 异步支持 | ❌ | ✅ |
| 性能 | ✅ Good | ✅ Excellent |
| 易用性 | ✅ Simple | ✅ Feature-rich |

---

## 更多资源 / More Resources

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Swagger UI 文档](https://swagger.io/tools/swagger-ui/)
- [OpenAPI 规范](https://swagger.io/specification/)
- [Pydantic 文档](https://docs.pydantic.dev/)

---

## 支持 / Support

如有问题，请查看：
- 项目 README
- Swagger UI 在线文档
- FastAPI 官方文档

Happy coding! 🚀
