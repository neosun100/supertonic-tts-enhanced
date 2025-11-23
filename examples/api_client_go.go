package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

// API 配置
var apiBaseURL = getEnv("API_URL", "http://localhost:8088")

// 响应结构体
type HealthResponse struct {
	Status     string `json:"status"`
	Service    string `json:"service"`
	GpuEnabled bool   `json:"gpu_enabled"`
}

type SynthesizeRequest struct {
	Text       string  `json:"text"`
	VoiceStyle string  `json:"voice_style,omitempty"`
	TotalSteps int     `json:"total_steps,omitempty"`
	Speed      float64 `json:"speed,omitempty"`
}

type SynthesizeResponse struct {
	Status         string  `json:"status"`
	OutputFile     string  `json:"output_file"`
	GenerationTime float64 `json:"generation_time"`
	TextLength     int     `json:"text_length"`
	AudioDuration  float64 `json:"audio_duration"`
}

// 获取环境变量，如果不存在则返回默认值
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// 检查 API 服务健康状态
func checkHealth() bool {
	url := apiBaseURL + "/health"
	
	resp, err := http.Get(url)
	if err != nil {
		fmt.Printf("❌ 无法连接到服务器: %s\n", apiBaseURL)
		fmt.Printf("   错误: %v\n", err)
		fmt.Println("   请确保 API 服务正在运行")
		return false
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != 200 {
		fmt.Printf("❌ 服务异常: HTTP %d\n", resp.StatusCode)
		return false
	}
	
	var health HealthResponse
	if err := json.NewDecoder(resp.Body).Decode(&health); err != nil {
		fmt.Printf("❌ 解析响应失败: %v\n", err)
		return false
	}
	
	fmt.Printf("✅ 服务状态: %s\n", health.Status)
	gpuStatus := "未启用"
	if health.GpuEnabled {
		gpuStatus = "已启用"
	}
	fmt.Printf("✅ GPU 加速: %s\n", gpuStatus)
	return true
}

// 调用 API 生成语音
func synthesizeSpeech(text, voiceStyle string, totalSteps int, speed float64, saveFile bool) *SynthesizeResponse {
	url := apiBaseURL + "/synthesize"
	
	// 设置默认值
	if voiceStyle == "" {
		voiceStyle = "assets/voice_styles/M1.json"
	}
	if totalSteps == 0 {
		totalSteps = 5
	}
	if speed == 0 {
		speed = 1.05
	}
	
	reqBody := SynthesizeRequest{
		Text:       text,
		VoiceStyle: voiceStyle,
		TotalSteps: totalSteps,
		Speed:      speed,
	}
	
	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		fmt.Printf("❌ 序列化请求失败: %v\n", err)
		return nil
	}
	
	previewText := text
	if len(previewText) > 50 {
		previewText = previewText[:50] + "..."
	}
	fmt.Printf("📤 发送请求: %s\n", previewText)
	
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		fmt.Printf("❌ 创建请求失败: %v\n", err)
		return nil
	}
	
	req.Header.Set("Content-Type", "application/json")
	
	client := &http.Client{Timeout: 60 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ API 错误: %v\n", err)
		return nil
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != 200 {
		body, _ := io.ReadAll(resp.Body)
		fmt.Printf("❌ API 错误: HTTP %d: %s\n", resp.StatusCode, string(body))
		return nil
	}
	
	var result SynthesizeResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		fmt.Printf("❌ 解析响应失败: %v\n", err)
		return nil
	}
	
	fmt.Println("✅ 生成成功!")
	fmt.Printf("   文件: %s\n", result.OutputFile)
	fmt.Printf("   生成时间: %.3f秒\n", result.GenerationTime)
	fmt.Printf("   音频时长: %.2f秒\n", result.AudioDuration)
	fmt.Printf("   文本长度: %d字符\n", result.TextLength)
	
	// 下载音频文件
	if saveFile {
		downloadAudio(result.OutputFile)
	}
	
	return &result
}

// 下载生成的音频文件
func downloadAudio(filename string) {
	url := apiBaseURL + "/" + filename
	
	resp, err := http.Get(url)
	if err != nil {
		fmt.Printf("❌ 下载错误: %v\n", err)
		return
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != 200 {
		fmt.Printf("❌ 下载失败: HTTP %d\n", resp.StatusCode)
		return
	}
	
	file, err := os.Create(filename)
	if err != nil {
		fmt.Printf("❌ 创建文件失败: %v\n", err)
		return
	}
	defer file.Close()
	
	_, err = io.Copy(file, resp.Body)
	if err != nil {
		fmt.Printf("❌ 保存文件失败: %v\n", err)
		return
	}
	
	absPath, _ := os.Abs(filename)
	fmt.Printf("💾 音频已保存: %s\n", absPath)
}

// 主函数
func main() {
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println("Supertonic TTS - Go API Client")
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println()
	
	// 如果提供了命令行参数，使用第一个参数作为文本
	if len(os.Args) > 1 {
		text := strings.Join(os.Args[1:], " ")
		if checkHealth() {
			synthesizeSpeech(text, "assets/voice_styles/M1.json", 5, 1.05, true)
		}
		return
	}
	
	// 1. 检查服务健康状态
	fmt.Println("1️⃣ 检查服务状态...")
	if !checkHealth() {
		os.Exit(1)
	}
	fmt.Println()
	
	// 2. 生成语音示例
	fmt.Println("2️⃣ 生成语音...")
	
	// 示例 1: 基本使用
	text1 := "你好，这是 Supertonic TTS 的测试。"
	result1 := synthesizeSpeech(text1, "assets/voice_styles/M1.json", 5, 1.05, true)
	fmt.Println()
	
	// 示例 2: 使用不同语音风格
	if result1 != nil {
		text2 := "Hello, this is a test of the Supertonic TTS system."
		result2 := synthesizeSpeech(text2, "assets/voice_styles/F1.json", 5, 1.0, true)
		fmt.Println()
		
		// 示例 3: 高质量模式
		if result2 != nil {
			text3 := "这是一个高质量语音合成的测试，使用了更多的去噪步骤。"
			synthesizeSpeech(text3, "assets/voice_styles/M2.json", 10, 1.05, true)
			fmt.Println()
		}
	}
	
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println("✅ 完成!")
	fmt.Println(strings.Repeat("=", 60))
}
