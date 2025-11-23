#!/usr/bin/env python3
"""
Supertonic TTS - Python API Client Example
调用 HTTP API 进行文本转语音的 Python 客户端示例
"""

import requests
import json
import sys
from pathlib import Path

# API 配置
API_BASE_URL = "http://localhost:8088"  # 修改为你的服务器地址


def check_health():
    """检查 API 服务健康状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务状态: {data['status']}")
            print(f"✅ GPU 加速: {'已启用' if data.get('gpu_enabled') else '未启用'}")
            return True
        else:
            print(f"❌ 服务异常: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到服务器: {API_BASE_URL}")
        print("   请确保 API 服务正在运行")
        return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


def synthesize_speech(text, voice_style="assets/voice_styles/M1.json", 
                     total_steps=5, speed=1.05, save_file=True):
    """
    调用 API 生成语音
    
    Args:
        text: 要转换的文本
        voice_style: 语音风格文件路径
        total_steps: 去噪步数 (1-50)
        speed: 语速倍数 (0.5-2.0)
        save_file: 是否保存音频文件
    
    Returns:
        dict: API 响应结果
    """
    url = f"{API_BASE_URL}/synthesize"
    
    payload = {
        "text": text,
        "voice_style": voice_style,
        "total_steps": total_steps,
        "speed": speed
    }
    
    try:
        print(f"📤 发送请求: {text[:50]}...")
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 生成成功!")
            print(f"   文件: {result['output_file']}")
            print(f"   生成时间: {result['generation_time']}秒")
            print(f"   音频时长: {result['audio_duration']}秒")
            print(f"   文本长度: {result['text_length']}字符")
            
            # 下载音频文件
            if save_file:
                download_audio(result['output_file'])
            
            return result
        else:
            print(f"❌ API 错误: HTTP {response.status_code}")
            print(f"   响应: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请尝试缩短文本或减少生成步骤")
        return None
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return None


def download_audio(filename):
    """下载生成的音频文件"""
    url = f"{API_BASE_URL}/{filename}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            # 保存到当前目录
            output_path = Path(filename)
            output_path.write_bytes(response.content)
            print(f"💾 音频已保存: {output_path.absolute()}")
            return output_path
        else:
            print(f"❌ 下载失败: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 下载错误: {str(e)}")
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("Supertonic TTS - Python API Client")
    print("=" * 60)
    print()
    
    # 1. 检查服务健康状态
    print("1️⃣ 检查服务状态...")
    if not check_health():
        sys.exit(1)
    print()
    
    # 2. 生成语音示例
    print("2️⃣ 生成语音...")
    
    # 示例 1: 基本使用
    text1 = "你好，这是 Supertonic TTS 的测试。"
    result1 = synthesize_speech(
        text=text1,
        voice_style="assets/voice_styles/M1.json",
        total_steps=5,
        speed=1.05
    )
    print()
    
    # 示例 2: 使用不同语音风格
    if result1:
        text2 = "Hello, this is a test of the Supertonic TTS system."
        result2 = synthesize_speech(
            text=text2,
            voice_style="assets/voice_styles/F1.json",
            total_steps=5,
            speed=1.0
        )
        print()
    
    # 示例 3: 高质量模式（更多步数）
    if result1:
        text3 = "这是一个高质量语音合成的测试，使用了更多的去噪步骤。"
        result3 = synthesize_speech(
            text=text3,
            voice_style="assets/voice_styles/M2.json",
            total_steps=10,  # 更多步数 = 更高质量
            speed=1.05
        )
        print()
    
    print("=" * 60)
    print("✅ 完成!")
    print("=" * 60)


if __name__ == "__main__":
    # 如果提供了命令行参数，使用第一个参数作为文本
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        print("=" * 60)
        print("Supertonic TTS - Python API Client")
        print("=" * 60)
        print()
        
        if check_health():
            synthesize_speech(text)
    else:
        main()
