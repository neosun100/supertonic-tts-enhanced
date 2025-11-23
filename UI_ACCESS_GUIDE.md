# Supertonic TTS - Streamlit UI 访问指南

## ✅ 部署完成

Streamlit Web UI 已成功部署并运行！

---

## 🌐 访问方式

### 🎨 Streamlit Web UI（推荐）
- **地址**: http://localhost:8501
- **说明**: 美观易用的图形界面，支持所有 TTS 功能
- **状态**: ✅ 运行中

### 📡 HTTP API（原始方式）
- **地址**: http://localhost:8088
- **健康检查**: http://localhost:8088/health
- **状态**: ✅ 运行中（GPU 加速）

---

## 🎤 Streamlit UI 功能

### 📝 文本合成选项卡

#### 1. 语音选择
- **Male 1 (M1)**: 👨 标准男声，适合新闻播报、叙述
- **Male 2 (M2)**: 👨‍💼 年轻男声，适合对话、讲解
- **Female 1 (F1)**: 👩 温柔女声，适合有声读物、导航
- **Female 2 (F2)**: 👩‍💼 活泼女声，适合广告、客服

#### 2. 质量设置
- **去噪步骤**: 1-20 步可调
  - 1-3 步: ⚡ 快速模式（质量较低）
  - 4-7 步: 🎯 平衡模式（推荐，默认 5 步）
  - 8-20 步: 💎 高质量模式（速度较慢）

#### 3. 语速设置
- **语速倍率**: 0.5x - 2.0x
  - 0.5-0.9x: 🐌 慢速
  - 0.9-1.1x: 🎯 正常（默认 1.05x）
  - 1.1-1.5x: 🚀 快速
  - 1.5-2.0x: ⚡ 极速

#### 4. 输入模式
- **单句输入**: 适合短文本（500 字以内）
- **长文本输入**: 系统自动分段处理

#### 5. 实时统计
- 字符数统计
- 预计音频时长
- 预计生成时间

#### 6. 生成结果
- 🔊 **在线播放**: 内嵌音频播放器
- 📥 **下载音频**: 一键下载 WAV 格式
- 📊 **详细统计**:
  - 字符数
  - 音频时长
  - 生成时间
  - 实时因子（RTF）

### 📜 历史记录选项卡

- 保存最近 20 次生成记录
- 显示生成时间、语音风格、参数
- 可重新播放历史音频
- 可下载历史音频文件
- 一键清空历史记录

### ℹ️ 关于选项卡

- 项目介绍和特性说明
- 可用语音列表
- 技术栈信息
- API 使用示例
- 项目链接（GitHub、Hugging Face）

---

## 🚀 使用示例

### 方式 1: Streamlit UI（推荐）

1. **打开浏览器访问**: http://localhost:8501

2. **选择语音风格**: 在左侧边栏选择 M1/M2/F1/F2

3. **调整参数**:
   - 去噪步骤: 5（推荐）
   - 语速: 1.05x（推荐）

4. **输入文本**: 在文本框中输入要转换的文本

5. **生成语音**: 点击 "🎬 生成语音" 按钮

6. **播放/下载**:
   - 使用内嵌播放器试听
   - 点击下载链接保存音频

### 方式 2: API 调用

```bash
# 健康检查
curl http://localhost:8088/health

# 生成语音
curl -X POST http://localhost:8088/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好世界，欢迎使用 Supertonic TTS！",
    "voice_style": "assets/voice_styles/M1.json",
    "total_steps": 5,
    "speed": 1.05
  }'
```

响应示例：
```json
{
  "status": "success",
  "output_file": "tts_output_20251122_123456.wav",
  "text_length": 20,
  "audio_duration": 4.15,
  "generation_time": 0.38,
  "voice_style": "M1.json"
}
```

---

## 📊 性能指标

在 NVIDIA L40S GPU 上的实测性能：

| 指标 | 数值 |
|------|------|
| GPU 型号 | NVIDIA L40S (46GB) |
| CUDA 版本 | 12.6.3（容器）/ 13.0（主机） |
| 平均生成速度 | ~10x 实时速度 |
| GPU 内存占用 | ~932 MiB |
| 模型参数量 | 66M |
| 音频采样率 | 16 kHz |

---

## 🎨 UI 设计特点

### 视觉设计
- 🌈 **渐变配色**: 紫色主题（#667eea → #764ba2）
- 🎯 **响应式布局**: 自适应宽度设计
- 📦 **卡片式组件**: 清晰的信息层次
- 🎭 **Emoji 图标**: 直观的功能标识

### 用户体验
- ⚡ **实时反馈**: 加载动画和进度提示
- 📈 **数据可视化**: 统计数据卡片展示
- 🎵 **音频预览**: 内嵌播放器即时试听
- 💾 **历史管理**: 自动保存生成记录
- 🔧 **高级设置**: 可折叠的专业参数

### 交互优化
- 📱 **单页应用**: 标签式导航
- 🎚️ **滑块控制**: 直观的参数调节
- 📝 **智能提示**: 参数说明和建议值
- ⚙️ **配置预设**: 快速/平衡/高质量模式

---

## 🔧 容器管理

### 查看状态
```bash
# 查看所有服务
docker-compose ps

# 查看 UI 日志
docker-compose logs -f supertonic-tts-ui

# 查看 API 服务器日志
docker-compose logs -f supertonic-tts-server
```

### 重启服务
```bash
# 重启 UI
docker-compose restart supertonic-tts-ui

# 重启 API 服务器
docker-compose restart supertonic-tts-server

# 重启所有服务
docker-compose restart
```

### 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 更新服务
```bash
# 重新构建 UI
docker-compose build --no-cache supertonic-tts-ui

# 重新启动
docker-compose up -d supertonic-tts-ui
```

---

## 📁 生成文件位置

所有生成的音频文件保存在：
```
/home/neo/upload/supertonic/results/
```

文件命名格式：
```
tts_output_YYYYMMDD_HHMMSS.wav
```

示例：
- `tts_output_20251122_141530.wav`
- `tts_output_20251122_141845.wav`

---

## 🌐 网络架构

```
用户浏览器
    ↓
    ↓ HTTP (端口 8501)
    ↓
Streamlit UI 容器
    ↓
    ↓ HTTP API 调用
    ↓
TTS API 服务器容器 (端口 8088)
    ↓
    ↓ CUDA 加速
    ↓
NVIDIA L40S GPU 0
```

### Docker 网络配置
- **网络模式**: bridge
- **服务通信**: 容器名称解析
  - UI → API: http://supertonic-tts-server:8000
  - 外部访问 UI: http://localhost:8501
  - 外部访问 API: http://localhost:8088

### 共享资源
- **results/**: 生成的音频文件
- **assets/**: 模型和语音风格文件

---

## 🐛 故障排除

### UI 无法访问
```bash
# 1. 检查容器状态
docker-compose ps

# 2. 查看日志
docker-compose logs supertonic-tts-ui

# 3. 重启服务
docker-compose restart supertonic-tts-ui
```

### API 连接失败
```bash
# 1. 检查 API 服务器
curl http://localhost:8088/health

# 2. 查看 API 日志
docker-compose logs supertonic-tts-server

# 3. 确认网络连接
docker network inspect bridge
```

### 生成失败
可能原因：
1. **文本为空**: 确保输入了文本内容
2. **GPU 内存不足**: 降低 total_steps 或等待其他任务完成
3. **模型文件缺失**: 运行 `./download_models.sh` 重新下载

### 音频播放问题
1. **浏览器兼容性**: 使用 Chrome/Firefox/Edge 最新版本
2. **文件不存在**: 检查 results/ 目录是否有对应文件
3. **权限问题**: 确保 Docker 有权限读写 results/ 目录

---

## 📈 使用建议

### 最佳实践

1. **首次使用**:
   - 使用默认参数（5 步，1.05x 速度）
   - 选择适合场景的语音风格
   - 从短文本开始测试

2. **质量优化**:
   - 重要内容使用 8-10 步
   - 一般内容使用 5 步
   - 测试样本可用 2-3 步

3. **速度调整**:
   - 有声读物: 0.9-1.0x
   - 新闻播报: 1.0-1.1x
   - 快速浏览: 1.2-1.5x

4. **批量生成**:
   - 使用 API 方式
   - 编写脚本批量调用
   - 监控 GPU 使用率

### 性能优化

- **并发限制**: 单 GPU 建议 2-3 个并发请求
- **批处理**: 长文本自动分段处理
- **缓存复用**: 相同文本使用历史记录
- **资源监控**: 使用 `nvidia-smi` 监控 GPU

---

## 🎓 进阶功能

### 自定义语音风格

可以创建自定义语音风格 JSON 文件：

```bash
# 复制现有风格作为模板
cp assets/voice_styles/M1.json assets/voice_styles/custom.json

# 编辑 JSON 文件调整参数
# 然后在 API 中使用自定义路径
```

### 集成到其他应用

```python
import requests

def text_to_speech(text, voice="M1"):
    url = "http://localhost:8088/synthesize"
    data = {
        "text": text,
        "voice_style": f"assets/voice_styles/{voice}.json",
        "total_steps": 5,
        "speed": 1.05
    }
    response = requests.post(url, json=data)
    return response.json()

# 使用示例
result = text_to_speech("你好世界", voice="F1")
print(f"音频文件: {result['output_file']}")
```

---

## 📚 相关资源

- **项目主页**: https://github.com/supertone-inc/supertonic
- **Hugging Face**: https://huggingface.co/Supertone/supertonic
- **在线演示**: https://huggingface.co/spaces/Supertone/supertonic
- **ONNX Runtime**: https://onnxruntime.ai/
- **Streamlit 文档**: https://docs.streamlit.io/

---

## 🎉 快速开始

1. **访问 UI**: http://localhost:8501
2. **选择语音**: 左侧边栏选择 M1/M2/F1/F2
3. **输入文本**: "今天天气真不错，阳光明媚，适合出去走走。"
4. **点击生成**: 点击 "🎬 生成语音" 按钮
5. **播放试听**: 使用内嵌播放器听效果
6. **下载保存**: 点击下载链接保存文件

---

*文档更新时间: 2025-11-22*
*UI 版本: 1.0*
*部署状态: ✅ 运行中*
