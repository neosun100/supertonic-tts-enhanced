#!/usr/bin/env python3
"""
Supertonic TTS - Streamlit Web UI
GPU-accelerated Text-to-Speech with beautiful interface
"""

import streamlit as st
import requests
import json
import time
import os
from pathlib import Path
import base64
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Supertonic TTS",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem 0;
        border: none;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
        border: none;
    }
    .stat-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
    .success-box {
        background: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
# When running in Docker, use container name; otherwise use localhost
import socket
try:
    socket.gethostbyname('supertonic-tts-server')
    API_BASE_URL = "http://supertonic-tts-server:8000"
except:
    API_BASE_URL = "http://localhost:8088"

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# Voice styles configuration
VOICE_STYLES = {
    "Male 1 (M1)": {
        "path": "assets/voice_styles/M1.json",
        "description": "🎙️ 标准男声，适合新闻播报、叙述",
        "emoji": "👨"
    },
    "Male 2 (M2)": {
        "path": "assets/voice_styles/M2.json",
        "description": "🎙️ 年轻男声，适合对话、讲解",
        "emoji": "👨‍💼"
    },
    "Female 1 (F1)": {
        "path": "assets/voice_styles/F1.json",
        "description": "🎙️ 温柔女声，适合有声读物、导航",
        "emoji": "👩"
    },
    "Female 2 (F2)": {
        "path": "assets/voice_styles/F2.json",
        "description": "🎙️ 活泼女声，适合广告、客服",
        "emoji": "👩‍💼"
    }
}

# Session state initialization
if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []

def check_api_health():
    """检查 API 服务健康状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def synthesize_speech(text, voice_style, total_steps, speed):
    """调用 TTS API 生成语音"""
    url = f"{API_BASE_URL}/synthesize"
    data = {
        "text": text,
        "voice_style": voice_style,
        "total_steps": total_steps,
        "speed": speed
    }

    try:
        response = requests.post(url, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API 错误: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.Timeout:
        st.error("请求超时，请尝试缩短文本或减少生成步骤")
        return None
    except Exception as e:
        st.error(f"请求失败: {str(e)}")
        return None

def get_audio_player(audio_file):
    """生成音频播放器 HTML"""
    if not os.path.exists(audio_file):
        return None

    with open(audio_file, 'rb') as f:
        audio_bytes = f.read()

    audio_b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f'''
    <audio controls style="width: 100%;">
        <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
        Your browser does not support the audio element.
    </audio>
    '''
    return audio_html

def get_download_link(audio_file, filename):
    """生成下载链接"""
    if not os.path.exists(audio_file):
        return None

    with open(audio_file, 'rb') as f:
        audio_bytes = f.read()

    b64 = base64.b64encode(audio_bytes).decode()
    href = f'<a href="data:audio/wav;base64,{b64}" download="{filename}">📥 下载音频文件</a>'
    return href

# ===== MAIN UI =====

# Header
st.markdown('<h1 class="main-header">🎤 Supertonic TTS</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">⚡ Lightning Fast, GPU-Accelerated Text-to-Speech</p>', unsafe_allow_html=True)

# Check API status
api_status = check_api_health()
if api_status:
    st.markdown('<div class="success-box">✅ API 服务运行正常</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="warning-box">⚠️ 无法连接到 API 服务，请确保 Docker 容器正在运行</div>', unsafe_allow_html=True)
    st.stop()

# Sidebar - Settings
with st.sidebar:
    st.header("⚙️ 生成设置")

    # Voice selection
    st.subheader("🎤 语音选择")
    selected_voice = st.selectbox(
        "选择语音风格",
        options=list(VOICE_STYLES.keys()),
        format_func=lambda x: f"{VOICE_STYLES[x]['emoji']} {x}"
    )
    st.info(VOICE_STYLES[selected_voice]['description'])
    voice_style_path = VOICE_STYLES[selected_voice]['path']

    st.divider()

    # Quality settings
    st.subheader("🎨 质量设置")
    total_steps = st.slider(
        "去噪步骤 (Total Steps)",
        min_value=1,
        max_value=20,
        value=5,
        help="步骤越多质量越好，但生成速度越慢。推荐值：5-10"
    )

    quality_info = {
        range(1, 4): "⚡ 快速模式（质量较低）",
        range(4, 8): "🎯 平衡模式（推荐）",
        range(8, 21): "💎 高质量模式（速度较慢）"
    }

    for r, info in quality_info.items():
        if total_steps in r:
            st.caption(info)
            break

    st.divider()

    # Speed settings
    st.subheader("⏱️ 语速设置")
    speed = st.slider(
        "语速倍率",
        min_value=0.5,
        max_value=2.0,
        value=1.05,
        step=0.05,
        help="调整语音播放速度。1.0 = 正常速度"
    )

    speed_info = {
        (0.5, 0.9): "🐌 慢速",
        (0.9, 1.1): "🎯 正常",
        (1.1, 1.5): "🚀 快速",
        (1.5, 2.1): "⚡ 极速"
    }

    for (low, high), info in speed_info.items():
        if low <= speed < high:
            st.caption(info)
            break

    st.divider()

    # Advanced settings
    with st.expander("🔬 高级设置"):
        show_stats = st.checkbox("显示详细统计", value=True)
        auto_play = st.checkbox("生成后自动播放", value=False)
        save_history = st.checkbox("保存生成历史", value=True)

    st.divider()

    # Statistics
    st.subheader("📊 使用统计")
    total_generations = len(st.session_state.generation_history)
    st.metric("总生成次数", total_generations)

    if total_generations > 0:
        avg_time = sum(h['generation_time'] for h in st.session_state.generation_history) / total_generations
        st.metric("平均生成时间", f"{avg_time:.2f}s")

# Main content area
tab1, tab2, tab3 = st.tabs(["📝 文本合成", "📜 历史记录", "ℹ️ 关于"])

with tab1:
    st.header("输入文本")

    # Text input modes
    input_mode = st.radio(
        "输入模式",
        ["单句输入", "长文本输入"],
        horizontal=True
    )

    if input_mode == "单句输入":
        text_input = st.text_area(
            "输入要转换的文本",
            height=150,
            placeholder="例如：今天天气真不错，阳光明媚，适合出去走走。",
            help="输入单句或短文本（建议 500 字以内）"
        )
    else:
        text_input = st.text_area(
            "输入要转换的长文本",
            height=300,
            placeholder="可以输入长文本，系统会自动分段处理...",
            help="长文本会自动分段合成，适合文章、故事等"
        )

    # Character count
    char_count = len(text_input)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("字符数", char_count)
    with col2:
        estimated_duration = char_count * 0.075  # 粗略估算
        st.metric("预计时长", f"{estimated_duration:.1f}s")
    with col3:
        estimated_time = char_count / 200  # 粗略估算生成时间
        st.metric("预计生成", f"{estimated_time:.1f}s")

    # Generate button
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("🎬 生成语音", type="primary", use_container_width=True)

    # Generation process
    if generate_button:
        if not text_input.strip():
            st.error("❌ 请输入文本内容")
        else:
            with st.spinner("🎙️ 正在生成语音，请稍候..."):
                start_time = time.time()

                # Call API
                result = synthesize_speech(
                    text=text_input.strip(),
                    voice_style=voice_style_path,
                    total_steps=total_steps,
                    speed=speed
                )

                if result and result['status'] == 'success':
                    generation_time = time.time() - start_time

                    # Display success message
                    st.success("✅ 语音生成成功！")

                    # Get audio file path
                    audio_file = RESULTS_DIR / result['output_file']

                    # Display audio player
                    st.markdown("### 🔊 播放音频")
                    audio_html = get_audio_player(audio_file)
                    if audio_html:
                        st.markdown(audio_html, unsafe_allow_html=True)

                    # Statistics
                    if show_stats:
                        st.markdown("### 📊 生成统计")
                        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

                        with stat_col1:
                            st.markdown(f'<div class="stat-box"><div class="stat-value">{result["text_length"]}</div><div class="stat-label">字符数</div></div>', unsafe_allow_html=True)

                        with stat_col2:
                            st.markdown(f'<div class="stat-box"><div class="stat-value">{result["audio_duration"]:.2f}s</div><div class="stat-label">音频时长</div></div>', unsafe_allow_html=True)

                        with stat_col3:
                            st.markdown(f'<div class="stat-box"><div class="stat-value">{result["generation_time"]:.2f}s</div><div class="stat-label">生成时间</div></div>', unsafe_allow_html=True)

                        with stat_col4:
                            rtf = result["generation_time"] / result["audio_duration"]
                            st.markdown(f'<div class="stat-box"><div class="stat-value">{rtf:.2f}x</div><div class="stat-label">实时因子</div></div>', unsafe_allow_html=True)

                    # Download button
                    st.markdown("### 📥 下载")
                    download_link = get_download_link(audio_file, result['output_file'])
                    if download_link:
                        st.markdown(download_link, unsafe_allow_html=True)

                    # Save to history
                    if save_history:
                        history_entry = {
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'text': text_input[:100] + "..." if len(text_input) > 100 else text_input,
                            'voice': selected_voice,
                            'steps': total_steps,
                            'speed': speed,
                            'generation_time': result['generation_time'],
                            'audio_duration': result['audio_duration'],
                            'audio_file': str(audio_file)
                        }
                        st.session_state.generation_history.insert(0, history_entry)

                        # Keep only last 20 entries
                        if len(st.session_state.generation_history) > 20:
                            st.session_state.generation_history = st.session_state.generation_history[:20]

with tab2:
    st.header("📜 生成历史")

    if not st.session_state.generation_history:
        st.info("还没有生成记录。开始生成你的第一个语音吧！")
    else:
        # Clear history button
        if st.button("🗑️ 清空历史"):
            st.session_state.generation_history = []
            st.rerun()

        st.divider()

        # Display history
        for idx, entry in enumerate(st.session_state.generation_history):
            with st.expander(f"🎤 {entry['timestamp']} - {entry['voice']}"):
                st.markdown(f"**文本预览**: {entry['text']}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("质量", f"{entry['steps']} 步")
                with col2:
                    st.metric("语速", f"{entry['speed']:.2f}x")
                with col3:
                    st.metric("生成时间", f"{entry['generation_time']:.2f}s")

                # Audio player
                if os.path.exists(entry['audio_file']):
                    audio_html = get_audio_player(entry['audio_file'])
                    if audio_html:
                        st.markdown(audio_html, unsafe_allow_html=True)

                    # Download
                    filename = os.path.basename(entry['audio_file'])
                    download_link = get_download_link(entry['audio_file'], filename)
                    if download_link:
                        st.markdown(download_link, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ 音频文件已被删除")

with tab3:
    st.header("ℹ️ 关于 Supertonic TTS")

    st.markdown("""
    ### 🎙️ Supertonic TTS

    **Supertonic** 是一个超高速、设备端运行的文本转语音系统，专为极致性能设计。

    #### ⚡ 核心特性

    - **🚀 极速生成**: 在 M4 Pro 上达到实时 167 倍速度
    - **🪶 轻量级**: 仅 66M 参数，优化的设备端性能
    - **📱 本地运行**: 完全隐私，零延迟
    - **🎨 自然文本处理**: 无需预处理即可处理数字、日期、货币等
    - **⚙️ 高度可配置**: 可调节推理步骤、批处理等参数
    - **🧩 灵活部署**: 支持服务器、浏览器和边缘设备

    #### 🎤 可用语音

    - **Male 1 (M1)**: 标准男声
    - **Male 2 (M2)**: 年轻男声
    - **Female 1 (F1)**: 温柔女声
    - **Female 2 (F2)**: 活泼女声

    #### 🔧 技术栈

    - **Runtime**: ONNX Runtime (GPU 加速)
    - **Backend**: Python + FastAPI
    - **Frontend**: Streamlit
    - **GPU**: NVIDIA CUDA 12.6.3

    #### 📚 更多信息

    - [GitHub](https://github.com/supertone-inc/supertonic)
    - [Hugging Face](https://huggingface.co/Supertone/supertonic)
    - [在线演示](https://huggingface.co/spaces/Supertone/supertonic)

    ---

    ### 🛠️ API 信息

    本 UI 连接到后端 API 服务：
    - **端口**: 8088
    - **健康检查**: `GET /health`
    - **语音合成**: `POST /synthesize`

    #### 示例 API 调用

    ```bash
    curl -X POST http://localhost:8088/synthesize \\
      -H "Content-Type: application/json" \\
      -d '{
        "text": "你好世界",
        "voice_style": "assets/voice_styles/M1.json",
        "total_steps": 5,
        "speed": 1.05
      }'
    ```

    ---

    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>Made with ❤️ by Supertone Inc.</p>
        <p>Powered by ONNX Runtime & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Supertonic TTS v1.0**")
with col2:
    st.markdown("🖥️ GPU 加速模式")
with col3:
    st.markdown("📡 API 端口: 8088")
