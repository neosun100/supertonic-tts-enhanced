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
    .github-star-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .github-star-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .github-star-button {
        display: inline-block;
        background: white;
        color: #667eea;
        padding: 0.6rem 1.5rem;
        border-radius: 25px;
        text-decoration: none;
        font-weight: bold;
        transition: all 0.3s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .github-star-button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
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

# GitHub Star 引导（页面顶部，首次访问时显示）
if 'star_shown' not in st.session_state:
    st.session_state.star_shown = True
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%); 
                padding: 1rem 1.5rem; 
                border-radius: 10px; 
                text-align: center; 
                margin: 0 0 1.5rem 0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                border: 2px solid #667eea;">
        <p style="color: #ffffff; 
                  margin: 0.3rem 0; 
                  font-size: 1rem; 
                  font-weight: 600;
                  text-shadow: 0 1px 3px rgba(0,0,0,0.3);">
            ⭐ 喜欢这个项目？<a href="https://github.com/neosun100/supertonic-tts-enhanced" target="_blank" 
            style="color: #ffd700; 
                   text-decoration: underline; 
                   font-weight: bold;
                   text-shadow: 0 1px 2px rgba(0,0,0,0.5);">给我们一个 Star</a> 支持一下！
        </p>
    </div>
    """, unsafe_allow_html=True)

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
    
    # Language support notice in sidebar
    st.markdown("---")
    st.markdown("""
    <div style="background: #fff3cd; 
                border-left: 3px solid #ffc107; 
                padding: 0.6rem 0.8rem; 
                border-radius: 4px; 
                margin: 0.5rem 0;">
        <p style="margin: 0; color: #856404; font-size: 0.85rem; font-weight: 500;">
            ⚠️ <strong>仅支持英文</strong><br>
            当前版本仅支持英文文本输入
        </p>
    </div>
    """, unsafe_allow_html=True)

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

    # GitHub Star Section - 醒目的 Star 引导
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%); 
                padding: 1.5rem; 
                border-radius: 10px; 
                text-align: center; 
                margin: 1rem 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                border: 2px solid #667eea;">
        <h3 style="color: #ffffff; 
                   margin: 0 0 0.5rem 0; 
                   font-weight: 700;
                   text-shadow: 0 2px 4px rgba(0,0,0,0.4);">⭐ 喜欢这个项目？给我们一个 Star！⭐</h3>
        <p style="color: #f7fafc; 
                  margin: 0.5rem 0; 
                  font-size: 0.95rem;
                  font-weight: 500;
                  text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
            如果这个项目对你有帮助，请在 GitHub 上给我们一个 Star 支持一下！
        </p>
        <div style="margin-top: 1rem;">
            <a href="https://github.com/neosun100/supertonic-tts-enhanced" 
               target="_blank" 
               style="display: inline-block; 
                      background: #ffd700; 
                      color: #1a202c; 
                      padding: 0.6rem 1.5rem; 
                      border-radius: 25px; 
                      text-decoration: none; 
                      font-weight: bold;
                      transition: transform 0.2s;
                      box-shadow: 0 3px 6px rgba(0,0,0,0.3);
                      border: 2px solid #ffed4e;">
                ⭐ 在 GitHub 上给我们 Star
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

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

    # Language support notice
    st.markdown("""
    <div style="background: #fff3cd; 
                border-left: 4px solid #ffc107; 
                padding: 0.8rem 1rem; 
                border-radius: 5px; 
                margin-bottom: 1rem;">
        <p style="margin: 0; color: #856404; font-weight: 500;">
            ⚠️ <strong>语言支持说明</strong>：当前版本仅支持 <strong>英文</strong> 文本输入。中文及其他语言支持正在开发中。
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Text input modes
    input_mode = st.radio(
        "输入模式",
        ["单句输入", "长文本输入"],
        horizontal=True
    )

    if input_mode == "单句输入":
        text_input = st.text_area(
            "输入要转换的文本（仅支持英文）",
            height=150,
            placeholder="例如：Hello, this is a test of the Supertonic TTS system. It supports natural text processing without preprocessing.",
            help="输入单句或短文本（建议 500 字以内）。注意：当前仅支持英文输入。"
        )
    else:
        text_input = st.text_area(
            "输入要转换的长文本（仅支持英文）",
            height=300,
            placeholder="Enter long text here. The system will automatically segment and process it. Note: Currently only English is supported.",
            help="长文本会自动分段合成，适合文章、故事等。注意：当前仅支持英文输入。"
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

    # GitHub Star 引导区域 - 最醒目的位置
    st.markdown("""
    <div style="background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%); 
                padding: 2rem; 
                border-radius: 15px; 
                text-align: center; 
                margin: 1rem 0 2rem 0;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
                border: 3px solid #667eea;">
        <h2 style="color: #ffffff; 
                   margin: 0 0 1rem 0; 
                   font-size: 1.8rem;
                   font-weight: 800;
                   text-shadow: 0 2px 6px rgba(0,0,0,0.5);">
            ⭐ 喜欢这个项目？给我们一个 Star！⭐
        </h2>
        <p style="color: #f7fafc; 
                  margin: 0.5rem 0 1.5rem 0; 
                  font-size: 1.1rem; 
                  line-height: 1.6;
                  font-weight: 500;
                  text-shadow: 0 1px 3px rgba(0,0,0,0.4);">
            如果这个项目对你有帮助，请在 GitHub 上给我们一个 Star 支持一下！<br>
            你的支持是我们持续改进的动力 💪
        </p>
        <div style="margin-top: 1.5rem;">
            <a href="https://github.com/neosun100/supertonic-tts-enhanced" 
               target="_blank" 
               style="display: inline-block; 
                      background: #ffd700; 
                      color: #1a202c; 
                      padding: 0.8rem 2rem; 
                      border-radius: 30px; 
                      text-decoration: none; 
                      font-weight: bold;
                      font-size: 1.1rem;
                      transition: all 0.3s;
                      box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
                      border: 2px solid #ffed4e;
                      margin: 0.5rem;">
                ⭐ 在 GitHub 上给我们 Star
            </a>
        </div>
        <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
            <a href="https://github.com/neosun100/supertonic-tts-enhanced" 
               target="_blank"
               style="color: #ffd700; 
                      text-decoration: none; 
                      font-size: 0.9rem;
                      font-weight: 600;
                      text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
                🏠 项目主页
            </a>
            <span style="color: rgba(255,255,255,0.4);">|</span>
            <a href="https://github.com/neosun100/supertonic-tts-enhanced/issues" 
               target="_blank"
               style="color: #ffd700; 
                      text-decoration: none; 
                      font-size: 0.9rem;
                      font-weight: 600;
                      text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
                🐛 问题反馈
            </a>
            <span style="color: rgba(255,255,255,0.4);">|</span>
            <a href="https://github.com/neosun100/supertonic-tts-enhanced/blob/main/README.md" 
               target="_blank"
               style="color: #ffd700; 
                      text-decoration: none; 
                      font-size: 0.9rem;
                      font-weight: 600;
                      text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
                📖 使用文档
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
    - **🐳 Docker 支持**: 一键部署，支持 GPU 加速
    - **🌐 Web UI**: 美观易用的图形界面
    - **🚀 RESTful API**: 完整的 FastAPI 服务，支持 Swagger 文档

    #### 🌍 语言支持

    <div style="background: #fff3cd; 
                border-left: 4px solid #ffc107; 
                padding: 1rem; 
                border-radius: 5px; 
                margin: 1rem 0;">
        <p style="margin: 0; color: #856404; font-weight: 600;">
            ⚠️ <strong>当前语言支持</strong>
        </p>
        <ul style="margin: 0.5rem 0 0 1.5rem; color: #856404;">
            <li><strong>✅ 英文</strong>：完全支持</li>
            <li>❌ 中文：暂不支持（开发中）</li>
            <li>❌ 其他语言：暂不支持（开发中）</li>
        </ul>
        <p style="margin: 0.5rem 0 0 0; color: #856404; font-size: 0.9rem;">
            💡 请使用英文文本进行语音合成。中文及其他语言支持将在后续版本中推出。
        </p>
    </div>

    #### 🎤 可用语音

    - **Male 1 (M1)**: 标准男声，适合新闻播报、叙述
    - **Male 2 (M2)**: 年轻男声，适合对话、讲解
    - **Female 1 (F1)**: 温柔女声，适合有声读物、导航
    - **Female 2 (F2)**: 活泼女声，适合广告、客服

    #### 🔧 技术栈

    - **Runtime**: ONNX Runtime (GPU 加速)
    - **Backend**: Python + FastAPI
    - **Frontend**: Streamlit
    - **GPU**: NVIDIA CUDA 12.6.3
    - **Docker**: 容器化部署

    #### 📚 更多信息

    - [GitHub 项目](https://github.com/neosun100/supertonic-tts-enhanced) - 完整源码和文档
    - [原始项目](https://github.com/supertone-inc/supertonic) - Supertone Inc. 官方仓库
    - [Hugging Face 模型](https://huggingface.co/Supertone/supertonic) - 模型下载
    - [在线演示](https://huggingface.co/spaces/Supertone/supertonic) - 交互式演示

    ---

    ### 🛠️ API 信息

    本 UI 连接到后端 API 服务：
    - **端口**: 8088
    - **健康检查**: `GET /health`
    - **语音合成**: `POST /synthesize`
    - **Swagger 文档**: `GET /docs`

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

    #### 一行命令测试（生成并播放）

    ```bash
    curl -X POST http://localhost:8088/synthesize \\
      -H "Content-Type: application/json" \\
      -d '{"text": "Hello, this is a test.", "total_steps": 5, "speed": 1.05, "voice_style": "assets/voice_styles/M1.json"}' \\
      | jq -r '.output_file' \\
      | xargs -I {} bash -c 'curl -s http://localhost:8088/{} | ffplay -nodisp -autoexit - 2>/dev/null'
    ```

    ---

    <div style="text-align: center; color: #666; margin-top: 2rem; padding: 1.5rem; background: #f8f9fa; border-radius: 10px;">
        <p style="margin: 0.5rem 0; font-size: 1rem;">
            <strong>Made with ❤️ by <a href="https://github.com/neosun100" target="_blank" style="color: #667eea; text-decoration: none;">@neosun100</a></strong>
        </p>
        <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #888;">
            Powered by ONNX Runtime & Streamlit
        </p>
        <p style="margin: 0.5rem 0; font-size: 0.85rem; color: #999;">
            Supertonic TTS Enhanced v1.0 | © 2025 | MIT License
        </p>
    </div>
    """, unsafe_allow_html=True)

# Footer with GitHub Star
st.markdown("---")

# GitHub Star 引导（页面底部）
st.markdown("""
<div style="background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e0 100%); 
            padding: 1.5rem; 
            border-radius: 10px; 
            text-align: center; 
            margin: 1rem 0;
            border: 2px solid #667eea;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <h3 style="color: #1a202c; 
               margin: 0 0 0.5rem 0; 
               font-size: 1.3rem;
               font-weight: 700;">
        ⭐ 如果这个项目对你有帮助，请给我们一个 Star！
    </h3>
    <p style="color: #2d3748; 
              margin: 0.5rem 0 1rem 0;
              font-weight: 500;">
        你的支持是我们持续改进的动力 💪
    </p>
    <a href="https://github.com/neosun100/supertonic-tts-enhanced" 
       target="_blank" 
       style="display: inline-block; 
              background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
              color: #ffffff; 
              padding: 0.7rem 2rem; 
              border-radius: 25px; 
              text-decoration: none; 
              font-weight: bold;
              font-size: 1rem;
              box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5);
              transition: transform 0.2s;
              text-shadow: 0 1px 2px rgba(0,0,0,0.2);">
        ⭐ 在 GitHub 上给我们 Star
    </a>
    <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap; font-size: 0.9rem;">
        <a href="https://github.com/neosun100/supertonic-tts-enhanced" 
           target="_blank"
           style="color: #667eea; 
                  text-decoration: none;
                  font-weight: 600;">
            🏠 项目主页
        </a>
        <a href="https://github.com/neosun100/supertonic-tts-enhanced/issues" 
           target="_blank"
           style="color: #667eea; 
                  text-decoration: none;
                  font-weight: 600;">
            🐛 问题反馈
        </a>
        <a href="https://github.com/neosun100/supertonic-tts-enhanced/blob/main/README.md" 
           target="_blank"
           style="color: #667eea; 
                  text-decoration: none;
                  font-weight: 600;">
            📖 使用文档
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer info
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Supertonic TTS Enhanced v1.0**")
with col2:
    st.markdown("🖥️ GPU 加速模式")
with col3:
    st.markdown("📡 API 端口: 8088")
