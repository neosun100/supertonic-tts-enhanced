# 音频文件下载功能使用指南

## 问题描述

**原始问题**: API 生成音频文件后，无法通过 HTTP 下载

**错误表现**:
```bash
curl https://supertonic-api.aws.xin/output_xxx.wav
# 返回 404 Not Found
```

**根本原因**: FastAPI 服务只有 `/synthesize` 端点生成文件，但没有提供文件下载端点

---

## 解决方案

已添加 **音频文件下载端点**：`GET /{filename}`

### 新增功能

1. **直接下载** - 通过文件名直接下载生成的音频
2. **安全验证** - 防止路径穿越攻击，只允许 .wav 文件
3. **Swagger 集成** - 下载端点已集成到 API 文档

---

## 使用方法

### 方法 1: 完整流程（推荐）

```bash
# 1. 合成语音并获取文件名
OUTPUT_FILE=$(curl -X POST https://supertonic-api.aws.xin/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test.", "total_steps": 5}' \
  | jq -r '.output_file')

# 2. 下载并播放
curl -s "https://supertonic-api.aws.xin/${OUTPUT_FILE}" | ffplay -nodisp -autoexit -

# 或者保存到文件
curl -s "https://supertonic-api.aws.xin/${OUTPUT_FILE}" -o my_audio.wav
```

### 方法 2: 单行命令（你的原始写法，现在可以正常工作了）

```bash
curl -X POST https://supertonic-api.aws.xin/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test.", "total_steps": 5, "speed": 1.05}' \
  | jq -r '.output_file' \
  | xargs -I {} bash -c 'curl -s https://supertonic-api.aws.xin/{} | ffplay -nodisp -autoexit -'
```

**现在这个命令应该可以正常工作了！** ✅

### 方法 3: 分步执行

```bash
# 步骤 1: 生成音频
curl -X POST https://supertonic-api.aws.xin/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，这是测试。",
    "total_steps": 10,
    "speed": 1.0
  }' | jq .

# 输出示例:
# {
#   "status": "success",
#   "output_file": "output_1763874863.wav",
#   "generation_time": 0.403,
#   "text_length": 20,
#   "audio_duration": 1.942
# }

# 步骤 2: 下载音频文件
curl -O https://supertonic-api.aws.xin/output_1763874863.wav

# 步骤 3: 播放
ffplay -nodisp -autoexit output_1763874863.wav
```

---

## API 端点详情

### `GET /{filename}`

**描述**: 下载生成的音频文件

**参数**:
- `filename` (path) - 音频文件名（例如：`output_1763874863.wav`）

**响应**:
- **200 OK** - 返回音频文件（Content-Type: audio/wav）
- **400 Bad Request** - 无效的文件名
- **404 Not Found** - 文件不存在

**安全特性**:
- ✅ 只允许 `.wav` 文件
- ✅ 防止目录遍历攻击（禁止 `/` 和 `\\`）
- ✅ 文件必须存在于 `results/` 目录

**示例**:
```bash
# 直接下载
curl https://supertonic-api.aws.xin/output_1763874863.wav -o audio.wav

# 检查文件信息
curl -I https://supertonic-api.aws.xin/output_1763874863.wav

# 管道传输到播放器
curl -s https://supertonic-api.aws.xin/output_1763874863.wav | ffplay -
```

---

## Swagger UI 测试

### 在线测试下载功能

1. **打开 Swagger UI**:
   ```
   https://supertonic-api.aws.xin/docs
   ```

2. **测试合成**:
   - 展开 `POST /synthesize`
   - 点击 "Try it out"
   - 输入测试文本
   - 点击 "Execute"
   - 记录返回的 `output_file`

3. **测试下载**:
   - 展开 `GET /{filename}`
   - 点击 "Try it out"
   - 输入上一步得到的文件名（如 `output_1763874863.wav`）
   - 点击 "Execute"
   - 点击 "Download file" 下载音频

---

## 常见问题

### Q1: 文件下载后显示 "Invalid data"？

**A**: 确保文件名正确，包含 `.wav` 扩展名：
```bash
# ✅ 正确
curl https://supertonic-api.aws.xin/output_1763874863.wav

# ❌ 错误（缺少扩展名）
curl https://supertonic-api.aws.xin/output_1763874863
```

### Q2: 404 Not Found？

**A**: 可能原因：
1. 文件名拼写错误
2. 文件已被清理（旧文件定期删除）
3. 使用了错误的域名或端口

**解决方法**:
```bash
# 确保使用最新生成的文件
LATEST=$(curl -X POST https://supertonic-api.aws.xin/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}' | jq -r '.output_file')

echo "最新文件: $LATEST"
curl "https://supertonic-api.aws.xin/$LATEST" -o test.wav
```

### Q3: 可以下载其他格式的文件吗？

**A**: 当前只支持 `.wav` 格式。如需其他格式，可以使用 ffmpeg 转换：
```bash
# 下载并转换为 MP3
curl -s https://supertonic-api.aws.xin/output_xxx.wav \
  | ffmpeg -i - -codec:a libmp3lame -qscale:a 2 output.mp3

# 转换为 OGG
curl -s https://supertonic-api.aws.xin/output_xxx.wav \
  | ffmpeg -i - -codec:a libvorbis -qscale:a 4 output.ogg
```

### Q4: 文件会保留多久？

**A**: 生成的文件默认保留在服务器上，但可能会定期清理。建议：
- 生成后立即下载
- 重要音频保存到本地
- 不要依赖服务器长期存储

---

## 性能优化

### 流式播放（推荐）

```bash
# 边下载边播放（无需等待完整下载）
curl -s https://supertonic-api.aws.xin/output_xxx.wav | ffplay -nodisp -autoexit -
```

### 批量处理

```bash
# 批量生成并下载
texts=("第一句话" "第二句话" "第三句话")

for text in "${texts[@]}"; do
  echo "生成: $text"
  filename=$(curl -X POST https://supertonic-api.aws.xin/synthesize \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$text\"}" \
    | jq -r '.output_file')

  curl -s "https://supertonic-api.aws.xin/$filename" -o "${filename}"
  echo "已保存: ${filename}"
done
```

### 并发下载

```bash
# 使用 GNU parallel 加速下载
cat files.txt | parallel -j 4 \
  'curl -s https://supertonic-api.aws.xin/{} -o {}'
```

---

## Python 示例

```python
import requests

# 1. 生成语音
response = requests.post(
    "https://supertonic-api.aws.xin/synthesize",
    json={
        "text": "Hello, Python test",
        "total_steps": 5,
        "speed": 1.05
    }
)

result = response.json()
filename = result['output_file']

print(f"生成文件: {filename}")
print(f"生成时间: {result['generation_time']}秒")

# 2. 下载音频
audio_url = f"https://supertonic-api.aws.xin/{filename}"
audio_response = requests.get(audio_url)

# 3. 保存到文件
with open(f"downloaded_{filename}", "wb") as f:
    f.write(audio_response.content)

print(f"已下载: downloaded_{filename}")
```

---

## JavaScript 示例

```javascript
// 1. 生成语音
async function generateAndDownload() {
  // 生成
  const response = await fetch('https://supertonic-api.aws.xin/synthesize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: 'Hello, JavaScript test',
      total_steps: 5,
      speed: 1.05
    })
  });

  const result = await response.json();
  console.log('生成文件:', result.output_file);

  // 下载
  const audioUrl = `https://supertonic-api.aws.xin/${result.output_file}`;
  const audioResponse = await fetch(audioUrl);
  const blob = await audioResponse.blob();

  // 创建下载链接
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = result.output_file;
  a.click();
  URL.revokeObjectURL(url);

  console.log('下载完成');
}

generateAndDownload();
```

---

## 技术细节

### 实现方式

使用 **FastAPI FileResponse** 实现：
```python
@app.get("/{filename}", response_class=FileResponse)
async def download_audio(filename: str):
    file_path = os.path.join(results_dir, filename)
    return FileResponse(
        path=file_path,
        media_type="audio/wav",
        filename=filename
    )
```

### 安全特性

1. **文件名验证**:
   ```python
   if not filename.endswith('.wav') or '/' in filename or '\\' in filename:
       raise HTTPException(status_code=400, detail="Invalid filename")
   ```

2. **路径限制**: 只能访问 `results/` 目录中的文件

3. **存在性检查**: 返回 404 如果文件不存在

---

## 更新日志

### v1.1.0 (2025-11-23)
- ✅ 添加 `GET /{filename}` 下载端点
- ✅ 文件名安全验证
- ✅ Swagger UI 集成
- ✅ 完整的 API 文档

### v1.0.0 (2025-11-22)
- ✅ 基础 TTS API
- ✅ GPU 加速支持
- ✅ Swagger UI

---

## 相关文档

- **Swagger UI**: https://supertonic-api.aws.xin/docs
- **ReDoc**: https://supertonic-api.aws.xin/redoc
- **使用指南**: `SWAGGER_API_GUIDE.md`
- **恢复总结**: `RECOVERY_SUMMARY.md`

---

## 支持

如有问题，请检查：
1. 文件名是否正确（包含 .wav）
2. 网络连接是否正常
3. 服务器状态: `GET /health`

**测试端点**:
```bash
curl https://supertonic-api.aws.xin/health
```

---

**现在你的原始命令应该完全正常工作了！** 🎉
