# Supertonic TTS - Nginx 反向代理配置完成

## ✅ 配置已完成

Nginx 反向代理已成功配置并部署！

---

## 🌐 域名和服务映射

### 1. **Streamlit UI 界面**
- **域名**: https://supertonic.aws.xin
- **目标服务器**: 10.68.2.212:8501 (当前机器)
- **说明**: 用户友好的 Web 图形界面
- **特性**:
  - ✅ 完整 Streamlit WebSocket 支持
  - ✅ CORS 跨域访问支持
  - ✅ SSL/TLS 加密 (HTTPS)
  - ✅ HTTP 自动重定向到 HTTPS
  - ✅ HSTS 安全头

### 2. **HTTP API 服务**
- **域名**: https://supertonic-api.aws.xin
- **目标服务器**: 10.68.2.212:8088 (当前机器)
- **说明**: RESTful API 接口
- **特性**:
  - ✅ 完整 CORS 跨域访问支持
  - ✅ SSL/TLS 加密 (HTTPS)
  - ✅ HTTP 自动重定向到 HTTPS
  - ✅ 60秒超时设置（适合 TTS 生成）
  - ✅ 速率限制保护

---

## 🔧 Nginx 配置详情

### 反向代理服务器
- **IP 地址**: 107.172.39.47
- **配置文件**: /etc/nginx/nginx.conf
- **备份文件**: /etc/nginx/nginx.conf.backup.20251123_001657

### 目标服务器（当前机器）
- **IP 地址**: 10.68.2.212
- **UI 端口**: 8501 (Streamlit)
- **API 端口**: 8088 (FastAPI)

### SSL 证书
- **证书文件**: /etc/nginx/aws.xin.pem
- **私钥文件**: /etc/nginx/aws.xin.pem
- **协议**: TLSv1.2, TLSv1.3

---

## 📡 访问方式

### 推荐：Streamlit UI（最佳用户体验）
```
https://supertonic.aws.xin
```

**功能**:
- 4 种语音风格选择 (M1, M2, F1, F2)
- 质量控制 (1-20 步)
- 语速调节 (0.5-2.0x)
- 在线播放
- 一键下载
- 历史记录

### 备用：HTTP API（程序调用）
```
https://supertonic-api.aws.xin
```

**端点**:
- `GET /health` - 健康检查
- `POST /synthesize` - 语音合成

---

## 🔍 测试访问

### 1. 测试 UI 界面
```bash
# 从任何地方访问
curl -I https://supertonic.aws.xin

# 预期响应: HTTP/2 200
```

### 2. 测试 API 健康检查
```bash
curl https://supertonic-api.aws.xin/health

# 预期响应: {"status": "healthy", "service": "Supertonic TTS", "gpu_enabled": true}
```

### 3. 测试 API 语音合成
```bash
curl -X POST https://supertonic-api.aws.xin/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好世界，欢迎使用 Supertonic TTS！",
    "voice_style": "assets/voice_styles/M1.json",
    "total_steps": 5,
    "speed": 1.05
  }'
```

---

## 🎯 Nginx 配置要点

### 1. Streamlit WebSocket 支持
```nginx
# 最关键的 WebSocket 端点
location /_stcore/stream {
    proxy_pass http://10.68.2.212:8501/_stcore/stream;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
    proxy_buffering off;
}
```

### 2. CORS 跨域支持
```nginx
# 处理 OPTIONS 预检请求
if ($request_method = 'OPTIONS') {
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With" always;
    return 204;
}

# 所有请求添加 CORS 头
add_header Access-Control-Allow-Origin "*" always;
```

### 3. 安全头部
```nginx
add_header Strict-Transport-Security "max-age=63072000" always;
add_header X-Content-Type-Options nosniff;
add_header X-Frame-Options DENY;
add_header X-XSS-Protection "1; mode=block";
```

### 4. 速率限制
```nginx
limit_req zone=one burst=10 nodelay;
```

---

## 🔄 管理命令

### Nginx 服务管理
```bash
# 测试配置
sudo nginx -t

# 重载配置（不中断服务）
sudo systemctl reload nginx

# 重启服务
sudo systemctl restart nginx

# 查看状态
sudo systemctl status nginx

# 查看日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 恢复备份
```bash
# 如果需要恢复到之前的配置
sudo cp /etc/nginx/nginx.conf.backup.20251123_001657 /etc/nginx/nginx.conf
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📊 网络架构

```
用户浏览器/客户端
    ↓
    ↓ HTTPS (域名访问)
    ↓
Nginx 反向代理服务器 (107.172.39.47)
    ├─ supertonic.aws.xin → 10.68.2.212:8501 (Streamlit UI)
    └─ supertonic-api.aws.xin → 10.68.2.212:8088 (FastAPI)
    ↓
    ↓ HTTP (内网转发)
    ↓
Supertonic TTS 服务器 (10.68.2.212)
    ├─ Docker 容器: supertonic-tts-ui (端口 8501)
    └─ Docker 容器: supertonic-tts-server (端口 8088)
    ↓
    ↓ CUDA 加速
    ↓
NVIDIA L40S GPU 0
```

---

## 🔐 安全特性

### 已启用的安全措施

1. **SSL/TLS 加密**
   - TLS 1.2 和 1.3 协议
   - 强加密套件
   - HSTS 启用

2. **速率限制**
   - 5 请求/秒基础速率
   - 10 请求突发容量
   - 防止 DDoS 攻击

3. **安全头部**
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - X-XSS-Protection: 1; mode=block

4. **访问控制**
   - CORS 策略（当前允许所有来源）
   - 可添加 IP 白名单（如需要）

### 可选增强措施

如需更严格的安全控制，可考虑：

1. **添加 HTTP 基本认证**
```nginx
auth_basic "Restricted Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

2. **限制 CORS 来源**
```nginx
add_header Access-Control-Allow-Origin "https://yourdomain.com" always;
```

3. **IP 白名单**
```nginx
allow 192.168.1.0/24;
deny all;
```

---

## 🐛 故障排除

### 1. 无法访问域名

**检查清单**:
```bash
# 1. DNS 解析
nslookup supertonic.aws.xin
# 应该返回: 107.172.39.47

# 2. Nginx 状态
sudo systemctl status nginx

# 3. 端口监听
sudo ss -tuln | grep -E "(443|80)"

# 4. 防火墙
sudo ufw status
```

### 2. UI 界面无法加载

**可能原因**:
- Streamlit 容器未运行
- WebSocket 连接失败

**检查方法**:
```bash
# 在 10.68.2.212 服务器上
docker ps | grep supertonic-tts-ui
curl http://localhost:8501/_stcore/health
```

### 3. API 请求失败

**可能原因**:
- API 容器未运行
- GPU 不可用

**检查方法**:
```bash
# 在 10.68.2.212 服务器上
docker ps | grep supertonic-tts-server
curl http://localhost:8088/health
```

### 4. 502 Bad Gateway 错误

**常见原因**:
- 后端服务未运行
- 网络连接问题

**解决方法**:
```bash
# 1. 检查后端服务
docker-compose ps

# 2. 重启服务
docker-compose restart

# 3. 查看 Nginx 错误日志
sudo tail -100 /var/log/nginx/error.log
```

---

## 📈 性能优化

### 当前配置

| 设置 | 值 | 说明 |
|------|-----|------|
| proxy_buffering | off | 禁用缓冲，实时传输 |
| proxy_read_timeout | 86400s (UI) / 60s (API) | 长连接/标准超时 |
| limit_req | 5r/s burst 10 | 速率限制 |
| keepalive_timeout | 系统默认 | 连接复用 |

### 监控建议

```bash
# 实时监控 Nginx 连接
watch -n 1 'ss -tun | grep -E "(8501|8088)" | wc -l'

# 查看访问日志
sudo tail -f /var/log/nginx/access.log | grep supertonic

# 查看错误日志
sudo tail -f /var/log/nginx/error.log | grep supertonic
```

---

## 📝 配置文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| **Nginx 主配置** | /etc/nginx/nginx.conf | 完整配置文件 |
| **配置备份** | /etc/nginx/nginx.conf.backup.20251123_001657 | 修改前的备份 |
| **SSL 证书** | /etc/nginx/aws.xin.pem | 证书和私钥 |
| **访问日志** | /var/log/nginx/access.log | 所有访问记录 |
| **错误日志** | /var/log/nginx/error.log | 错误和警告信息 |

---

## 🎉 部署成功！

所有配置已完成并测试通过：

✅ **Nginx 配置已更新**
✅ **配置语法检查通过**
✅ **Nginx 服务已重载**
✅ **备份文件已创建**
✅ **SSL/TLS 加密已启用**
✅ **WebSocket 支持已配置**
✅ **CORS 跨域已启用**

---

## 🌟 快速开始

### 方式 1: 使用 Web UI（推荐）

1. 打开浏览器访问: https://supertonic.aws.xin
2. 选择语音风格 (M1/M2/F1/F2)
3. 输入文本
4. 点击"生成语音"
5. 播放或下载生成的音频

### 方式 2: 使用 API

```bash
curl -X POST https://supertonic-api.aws.xin/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好世界！",
    "voice_style": "assets/voice_styles/M1.json",
    "total_steps": 5,
    "speed": 1.05
  }'
```

---

## 📚 相关文档

- **本地访问指南**: NETWORK_ACCESS.md
- **UI 使用指南**: UI_ACCESS_GUIDE.md
- **部署总结**: DEPLOYMENT_SUMMARY.md
- **Docker 配置**: docker-compose.yml

---

*配置完成时间: 2025-11-23*
*Nginx 服务器: 107.172.39.47*
*TTS 服务器: 10.68.2.212*
*配置状态: ✅ 运行中*
