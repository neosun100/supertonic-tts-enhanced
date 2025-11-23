# Supertonic TTS API 客户端示例

本目录包含各种编程语言调用 Supertonic TTS HTTP API 的客户端示例。

## 📚 可用示例

| 语言 | 文件 | 说明 |
|------|------|------|
| **Python** | `api_client_python.py` | 使用 `requests` 库调用 API |
| **Node.js** | `api_client_nodejs.js` | 使用 Node.js 内置 `http/https` 模块 |
| **Java** | `api_client_java.java` | 使用 `HttpURLConnection` 和 `org.json` |
| **Go** | `api_client_go.go` | 使用标准库 `net/http` |
| **cURL** | `api_client_curl.sh` | Bash 脚本，使用 `curl` 命令 |

## 🚀 快速开始

### 前置要求

1. **API 服务运行中**: 确保 Supertonic TTS API 服务正在运行
   ```bash
   # 检查服务状态
   curl http://localhost:8088/health
   ```

2. **安装依赖** (根据使用的语言):
   - **Python**: `pip install requests`
   - **Node.js**: 无需额外依赖（使用内置模块）
   - **Java**: 需要 `org.json` 库
   - **Go**: 无需额外依赖（使用标准库）
   - **cURL**: 需要 `curl` 和 `jq`（可选，用于 JSON 解析）

### 使用方法

#### Python

```bash
# 基本使用
python3 api_client_python.py

# 指定文本
python3 api_client_python.py "你好，世界！"
```

#### Node.js

```bash
# 基本使用
node api_client_nodejs.js

# 指定文本
node api_client_nodejs.js "Hello, world!"
```

#### Java

```bash
# 编译
javac -cp ".:json-20231013.jar" api_client_java.java

# 运行
java -cp ".:json-20231013.jar" ApiClientJava

# 指定文本
java -cp ".:json-20231013.jar" ApiClientJava "你好，世界！"
```

#### Go

```bash
# 运行
go run api_client_go.go

# 指定文本
go run api_client_go.go "Hello, world!"
```

#### cURL (Bash)

```bash
# 添加执行权限
chmod +x api_client_curl.sh

# 基本使用
./api_client_curl.sh

# 指定文本
./api_client_curl.sh "你好，世界！"
```

## 📖 API 端点说明

### 1. 健康检查

```bash
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "service": "Supertonic TTS",
  "gpu_enabled": true
}
```

### 2. 语音合成

```bash
POST /synthesize
Content-Type: application/json

{
  "text": "要转换的文本",
  "voice_style": "assets/voice_styles/M1.json",
  "total_steps": 5,
  "speed": 1.05
}
```

**响应示例**:
```json
{
  "status": "success",
  "output_file": "output_1234567890.wav",
  "generation_time": 0.417,
  "text_length": 20,
  "audio_duration": 4.15
}
```

### 3. 下载音频文件

```bash
GET /{filename}
```

例如: `GET /output_1234567890.wav`

## 🔧 配置

### 修改 API 地址

所有示例都支持通过环境变量修改 API 地址：

```bash
# Python
export API_URL="http://your-server:8088"
python3 api_client_python.py

# Node.js
export API_URL="http://your-server:8088"
node api_client_nodejs.js

# Go
export API_URL="http://your-server:8088"
go run api_client_go.go

# cURL
export API_URL="http://your-server:8088"
./api_client_curl.sh
```

或者在代码中直接修改 `API_BASE_URL` 变量。

## 📝 代码示例

### Python

```python
import requests

API_URL = "http://localhost:8088"

# 健康检查
response = requests.get(f"{API_URL}/health")
print(response.json())

# 生成语音
response = requests.post(f"{API_URL}/synthesize", json={
    "text": "Hello, world!",
    "total_steps": 5,
    "speed": 1.05
})
result = response.json()
print(f"生成文件: {result['output_file']}")

# 下载音频
audio_url = f"{API_URL}/{result['output_file']}"
audio_response = requests.get(audio_url)
with open(result['output_file'], 'wb') as f:
    f.write(audio_response.content)
```

### Node.js

```javascript
const http = require('http');

const API_URL = 'http://localhost:8088';

// 生成语音
const data = JSON.stringify({
    text: 'Hello, world!',
    total_steps: 5,
    speed: 1.05
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
    let data = '';
    res.on('data', (chunk) => { data += chunk; });
    res.on('end', () => {
        const result = JSON.parse(data);
        console.log('生成文件:', result.output_file);
    });
});

req.write(data);
req.end();
```

### Java

```java
import java.net.HttpURLConnection;
import java.net.URL;
import org.json.JSONObject;

String apiUrl = "http://localhost:8088";

// 创建请求
URL url = new URL(apiUrl + "/synthesize");
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
conn.setRequestMethod("POST");
conn.setRequestProperty("Content-Type", "application/json");
conn.setDoOutput(true);

// 发送数据
JSONObject payload = new JSONObject();
payload.put("text", "Hello, world!");
payload.put("total_steps", 5);
payload.put("speed", 1.05);

try (OutputStream os = conn.getOutputStream()) {
    byte[] input = payload.toString().getBytes("utf-8");
    os.write(input, 0, input.length);
}

// 读取响应
JSONObject response = new JSONObject(
    new String(conn.getInputStream().readAllBytes())
);
System.out.println("生成文件: " + response.getString("output_file"));
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "net/http"
)

apiURL := "http://localhost:8088"

// 创建请求
payload := map[string]interface{}{
    "text": "Hello, world!",
    "total_steps": 5,
    "speed": 1.05,
}

jsonData, _ := json.Marshal(payload)
req, _ := http.NewRequest("POST", apiURL+"/synthesize", bytes.NewBuffer(jsonData))
req.Header.Set("Content-Type", "application/json")

// 发送请求
client := &http.Client{}
resp, _ := client.Do(req)
defer resp.Body.Close()

// 解析响应
var result map[string]interface{}
json.NewDecoder(resp.Body).Decode(&result)
fmt.Println("生成文件:", result["output_file"])
```

### cURL

```bash
# 健康检查
curl http://localhost:8088/health

# 生成语音
curl -X POST http://localhost:8088/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "total_steps": 5,
    "speed": 1.05
  }'

# 下载音频
curl -O http://localhost:8088/output_1234567890.wav
```

## 🐛 故障排除

### 连接失败

如果遇到连接错误，请检查：

1. **API 服务是否运行**:
   ```bash
   curl http://localhost:8088/health
   ```

2. **端口是否正确**: 默认端口是 8088

3. **防火墙设置**: 确保端口未被阻止

### JSON 解析错误

- **Java**: 确保已添加 `org.json` 依赖
- **cURL**: 安装 `jq` 用于 JSON 解析（可选）

### 超时错误

如果文本很长，可能需要增加超时时间：

- **Python**: `requests.post(url, json=data, timeout=120)`
- **Go**: `client := &http.Client{Timeout: 120 * time.Second}`
- **Node.js**: 在请求选项中设置超时

## 📚 更多资源

- [API 文档](http://localhost:8088/docs) - Swagger UI 交互式文档
- [API 使用指南](../SWAGGER_API_GUIDE.md) - 详细的 API 使用说明
- [项目 README](../README.md) - 项目完整文档

## 🤝 贡献

欢迎提交更多语言的客户端示例！
