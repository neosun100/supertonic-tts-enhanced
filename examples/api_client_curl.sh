#!/bin/bash
# Supertonic TTS - cURL API Client Example
# 调用 HTTP API 进行文本转语音的 cURL 客户端示例

API_BASE_URL="${API_URL:-http://localhost:8088}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查服务健康状态
check_health() {
    echo -e "${BLUE}1️⃣ 检查服务状态...${NC}"
    
    response=$(curl -s -w "\n%{http_code}" "${API_BASE_URL}/health")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        status=$(echo "$body" | jq -r '.status')
        gpu_enabled=$(echo "$body" | jq -r '.gpu_enabled')
        
        echo -e "${GREEN}✅ 服务状态: ${status}${NC}"
        if [ "$gpu_enabled" = "true" ]; then
            echo -e "${GREEN}✅ GPU 加速: 已启用${NC}"
        else
            echo -e "${GREEN}✅ GPU 加速: 未启用${NC}"
        fi
        return 0
    else
        echo -e "${RED}❌ 无法连接到服务器: ${API_BASE_URL}${NC}"
        echo -e "${RED}   请确保 API 服务正在运行${NC}"
        return 1
    fi
}

# 调用 API 生成语音
synthesize_speech() {
    local text="$1"
    local voice_style="${2:-assets/voice_styles/M1.json}"
    local total_steps="${3:-5}"
    local speed="${4:-1.05}"
    
    local preview_text="${text:0:50}"
    if [ ${#text} -gt 50 ]; then
        preview_text="${preview_text}..."
    fi
    
    echo -e "${BLUE}📤 发送请求: ${preview_text}${NC}"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE_URL}/synthesize" \
        -H "Content-Type: application/json" \
        -d "{
            \"text\": \"${text}\",
            \"voice_style\": \"${voice_style}\",
            \"total_steps\": ${total_steps},
            \"speed\": ${speed}
        }")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        output_file=$(echo "$body" | jq -r '.output_file')
        generation_time=$(echo "$body" | jq -r '.generation_time')
        audio_duration=$(echo "$body" | jq -r '.audio_duration')
        text_length=$(echo "$body" | jq -r '.text_length')
        
        echo -e "${GREEN}✅ 生成成功!${NC}"
        echo -e "   文件: ${output_file}"
        echo -e "   生成时间: ${generation_time}秒"
        echo -e "   音频时长: ${audio_duration}秒"
        echo -e "   文本长度: ${text_length}字符"
        
        # 下载音频文件
        download_audio "$output_file"
        
        echo "$output_file"
    else
        echo -e "${RED}❌ API 错误: HTTP ${http_code}${NC}"
        echo -e "${RED}   响应: ${body}${NC}"
        return 1
    fi
}

# 下载生成的音频文件
download_audio() {
    local filename="$1"
    local url="${API_BASE_URL}/${filename}"
    
    echo -e "${BLUE}💾 下载音频文件...${NC}"
    
    if curl -s -f -o "$filename" "$url"; then
        abs_path=$(realpath "$filename")
        echo -e "${GREEN}💾 音频已保存: ${abs_path}${NC}"
    else
        echo -e "${RED}❌ 下载失败${NC}"
    fi
}

# 主函数
main() {
    echo "============================================================"
    echo "Supertonic TTS - cURL API Client"
    echo "============================================================"
    echo ""
    
    # 检查 jq 是否安装
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}⚠️  警告: jq 未安装，JSON 解析可能失败${NC}"
        echo -e "${YELLOW}   安装方法: sudo apt-get install jq 或 brew install jq${NC}"
        echo ""
    fi
    
    # 如果提供了命令行参数，使用第一个参数作为文本
    if [ $# -gt 0 ]; then
        text="$*"
        if check_health; then
            synthesize_speech "$text"
        fi
        exit 0
    fi
    
    # 1. 检查服务健康状态
    if ! check_health; then
        exit 1
    fi
    echo ""
    
    # 2. 生成语音示例
    echo -e "${BLUE}2️⃣ 生成语音...${NC}"
    
    # 示例 1: 基本使用
    text1="你好，这是 Supertonic TTS 的测试。"
    result1=$(synthesize_speech "$text1" "assets/voice_styles/M1.json" 5 1.05)
    echo ""
    
    # 示例 2: 使用不同语音风格
    if [ -n "$result1" ]; then
        text2="Hello, this is a test of the Supertonic TTS system."
        result2=$(synthesize_speech "$text2" "assets/voice_styles/F1.json" 5 1.0)
        echo ""
        
        # 示例 3: 高质量模式
        if [ -n "$result2" ]; then
            text3="这是一个高质量语音合成的测试，使用了更多的去噪步骤。"
            synthesize_speech "$text3" "assets/voice_styles/M2.json" 10 1.05
            echo ""
        fi
    fi
    
    echo "============================================================"
    echo -e "${GREEN}✅ 完成!${NC}"
    echo "============================================================"
}

# 运行主函数
main "$@"
