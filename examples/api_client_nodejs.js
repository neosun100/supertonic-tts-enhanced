#!/usr/bin/env node
/**
 * Supertonic TTS - Node.js API Client Example
 * 调用 HTTP API 进行文本转语音的 Node.js 客户端示例
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// API 配置
const API_BASE_URL = process.env.API_URL || 'http://localhost:8088';

/**
 * 发送 HTTP 请求的辅助函数
 */
function httpRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
        const urlObj = new URL(url);
        const protocol = urlObj.protocol === 'https:' ? https : http;
        
        const reqOptions = {
            hostname: urlObj.hostname,
            port: urlObj.port || (urlObj.protocol === 'https:' ? 443 : 80),
            path: urlObj.pathname + urlObj.search,
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };
        
        const req = protocol.request(reqOptions, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    try {
                        const jsonData = JSON.parse(data);
                        resolve({ statusCode: res.statusCode, data: jsonData });
                    } catch (e) {
                        resolve({ statusCode: res.statusCode, data: data });
                    }
                } else {
                    reject(new Error(`HTTP ${res.statusCode}: ${data}`));
                }
            });
        });
        
        req.on('error', (e) => {
            reject(e);
        });
        
        if (options.body) {
            req.write(JSON.stringify(options.body));
        }
        
        req.end();
    });
}

/**
 * 检查 API 服务健康状态
 */
async function checkHealth() {
    try {
        const response = await httpRequest(`${API_BASE_URL}/health`);
        console.log(`✅ 服务状态: ${response.data.status}`);
        console.log(`✅ GPU 加速: ${response.data.gpu_enabled ? '已启用' : '未启用'}`);
        return true;
    } catch (error) {
        console.error(`❌ 无法连接到服务器: ${API_BASE_URL}`);
        console.error(`   错误: ${error.message}`);
        console.error('   请确保 API 服务正在运行');
        return false;
    }
}

/**
 * 调用 API 生成语音
 */
async function synthesizeSpeech(text, voiceStyle = 'assets/voice_styles/M1.json', 
                               totalSteps = 5, speed = 1.05, saveFile = true) {
    const url = `${API_BASE_URL}/synthesize`;
    
    const payload = {
        text: text,
        voice_style: voiceStyle,
        total_steps: totalSteps,
        speed: speed
    };
    
    try {
        console.log(`📤 发送请求: ${text.substring(0, 50)}...`);
        const response = await httpRequest(url, {
            method: 'POST',
            body: payload
        });
        
        const result = response.data;
        console.log('✅ 生成成功!');
        console.log(`   文件: ${result.output_file}`);
        console.log(`   生成时间: ${result.generation_time}秒`);
        console.log(`   音频时长: ${result.audio_duration}秒`);
        console.log(`   文本长度: ${result.text_length}字符`);
        
        // 下载音频文件
        if (saveFile) {
            await downloadAudio(result.output_file);
        }
        
        return result;
    } catch (error) {
        console.error(`❌ API 错误: ${error.message}`);
        return null;
    }
}

/**
 * 下载生成的音频文件
 */
async function downloadAudio(filename) {
    const url = `${API_BASE_URL}/${filename}`;
    
    return new Promise((resolve, reject) => {
        const urlObj = new URL(url);
        const protocol = urlObj.protocol === 'https:' ? https : http;
        
        const req = protocol.get({
            hostname: urlObj.hostname,
            port: urlObj.port || (urlObj.protocol === 'https:' ? 443 : 80),
            path: urlObj.pathname
        }, (res) => {
            if (res.statusCode !== 200) {
                reject(new Error(`下载失败: HTTP ${res.statusCode}`));
                return;
            }
            
            const filePath = path.join(process.cwd(), filename);
            const fileStream = fs.createWriteStream(filePath);
            
            res.pipe(fileStream);
            
            fileStream.on('finish', () => {
                fileStream.close();
                console.log(`💾 音频已保存: ${filePath}`);
                resolve(filePath);
            });
        });
        
        req.on('error', (e) => {
            console.error(`❌ 下载错误: ${e.message}`);
            reject(e);
        });
    });
}

/**
 * 主函数
 */
async function main() {
    console.log('='.repeat(60));
    console.log('Supertonic TTS - Node.js API Client');
    console.log('='.repeat(60));
    console.log();
    
    // 1. 检查服务健康状态
    console.log('1️⃣ 检查服务状态...');
    const isHealthy = await checkHealth();
    if (!isHealthy) {
        process.exit(1);
    }
    console.log();
    
    // 2. 生成语音示例
    console.log('2️⃣ 生成语音...');
    
    // 示例 1: 基本使用
    const text1 = '你好，这是 Supertonic TTS 的测试。';
    const result1 = await synthesizeSpeech(
        text1,
        'assets/voice_styles/M1.json',
        5,
        1.05
    );
    console.log();
    
    // 示例 2: 使用不同语音风格
    if (result1) {
        const text2 = 'Hello, this is a test of the Supertonic TTS system.';
        const result2 = await synthesizeSpeech(
            text2,
            'assets/voice_styles/F1.json',
            5,
            1.0
        );
        console.log();
    }
    
    // 示例 3: 高质量模式
    if (result1) {
        const text3 = '这是一个高质量语音合成的测试，使用了更多的去噪步骤。';
        const result3 = await synthesizeSpeech(
            text3,
            'assets/voice_styles/M2.json',
            10,  // 更多步数 = 更高质量
            1.05
        );
        console.log();
    }
    
    console.log('='.repeat(60));
    console.log('✅ 完成!');
    console.log('='.repeat(60));
}

// 如果提供了命令行参数，使用第一个参数作为文本
if (process.argv.length > 2) {
    const text = process.argv.slice(2).join(' ');
    console.log('='.repeat(60));
    console.log('Supertonic TTS - Node.js API Client');
    console.log('='.repeat(60));
    console.log();
    
    checkHealth().then((isHealthy) => {
        if (isHealthy) {
            synthesizeSpeech(text);
        }
    });
} else {
    main().catch(console.error);
}
