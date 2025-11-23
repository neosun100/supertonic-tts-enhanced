# Supertonic TTS - 网络访问配置

## ✅ 已配置完成

所有 Docker 服务已配置为**允许所有 IP 访问**！

---

## 🌐 当前网络配置

### 端口绑定状态

| 服务 | 端口 | 绑定地址 | 状态 |
|------|------|----------|------|
| **TTS API 服务器** | 8088 | 0.0.0.0 | ✅ 允许所有 IP |
| **Streamlit UI** | 8501 | 0.0.0.0 | ✅ 允许所有 IP |

### 验证命令输出

```bash
# docker-compose ps
supertonic-tts-server   0.0.0.0:8088->8000/tcp   ✓
supertonic-tts-ui       0.0.0.0:8501->8501/tcp   ✓

# ss -tuln | grep -E "(8088|8501)"
tcp   LISTEN 0.0.0.0:8088   ✓
tcp   LISTEN 0.0.0.0:8501   ✓
```

---

## 🔌 访问方式

### 本地访问（当前机器）

#### Streamlit UI（推荐）
```
http://localhost:8501
http://127.0.0.1:8501
```

#### API 服务器
```
http://localhost:8088
http://127.0.0.1:8088
```

### 局域网访问（同一网络内的其他设备）

假设服务器 IP 为 `192.168.1.100`：

#### Streamlit UI
```
http://192.168.1.100:8501
```

#### API 服务器
```
http://192.168.1.100:8088
```

### 公网访问（通过公网 IP 或域名）

假设服务器公网 IP 为 `203.0.113.10`：

#### Streamlit UI
```
http://203.0.113.10:8501
```

#### API 服务器
```
http://203.0.113.10:8088
```

**注意**: 公网访问需要确保防火墙和云服务商安全组已开放相应端口。

---

## 🖥️ 查看服务器 IP 地址

### 查看本机所有 IP
```bash
# 方法 1: ip 命令
ip addr show

# 方法 2: ifconfig 命令
ifconfig

# 方法 3: hostname 命令
hostname -I
```

### 常见网络接口

| 接口 | 说明 | 示例 IP |
|------|------|---------|
| `lo` | 本地回环 | 127.0.0.1 |
| `eth0` | 以太网 | 192.168.1.100 |
| `ens3` | 云服务器网卡 | 10.0.0.5 |
| `wlan0` | 无线网卡 | 192.168.1.200 |

---

## 🔥 防火墙配置

### Ubuntu/Debian (ufw)

```bash
# 允许端口 8088 (API)
sudo ufw allow 8088/tcp

# 允许端口 8501 (UI)
sudo ufw allow 8501/tcp

# 查看防火墙状态
sudo ufw status

# 如果防火墙未启用，可以启用
sudo ufw enable
```

### CentOS/RHEL (firewalld)

```bash
# 允许端口 8088 (API)
sudo firewall-cmd --permanent --add-port=8088/tcp

# 允许端口 8501 (UI)
sudo firewall-cmd --permanent --add-port=8501/tcp

# 重新加载防火墙
sudo firewall-cmd --reload

# 查看开放的端口
sudo firewall-cmd --list-ports
```

### iptables

```bash
# 允许端口 8088 (API)
sudo iptables -A INPUT -p tcp --dport 8088 -j ACCEPT

# 允许端口 8501 (UI)
sudo iptables -A INPUT -p tcp --dport 8501 -j ACCEPT

# 保存规则
sudo iptables-save > /etc/iptables/rules.v4
```

---

## ☁️ 云服务商安全组配置

如果服务器部署在云平台，需要在安全组中开放端口：

### AWS (Security Groups)
1. 进入 EC2 控制台
2. 选择实例的安全组
3. 添加入站规则：
   - 类型: 自定义 TCP
   - 端口: 8088, 8501
   - 源: 0.0.0.0/0 (所有 IP) 或指定 IP 段

### 阿里云 (安全组规则)
1. 进入 ECS 控制台
2. 选择实例的安全组
3. 配置规则 → 添加安全组规则：
   - 端口范围: 8088/8088 和 8501/8501
   - 授权对象: 0.0.0.0/0

### 腾讯云 (安全组)
1. 进入云服务器控制台
2. 选择实例的安全组
3. 入站规则 → 添加规则：
   - 类型: 自定义
   - 端口: 8088, 8501
   - 来源: 0.0.0.0/0

### Google Cloud (Firewall Rules)
1. 进入 VPC 网络 → 防火墙
2. 创建防火墙规则：
   - 目标: 网络中的所有实例
   - 协议和端口: tcp:8088,8501
   - 来源 IP 范围: 0.0.0.0/0

---

## 🧪 连接测试

### 从其他机器测试 API

```bash
# 替换 SERVER_IP 为实际服务器 IP
SERVER_IP="192.168.1.100"

# 测试 API 健康检查
curl http://${SERVER_IP}:8088/health

# 测试语音合成
curl -X POST http://${SERVER_IP}:8088/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "测试文本",
    "voice_style": "assets/voice_styles/M1.json",
    "total_steps": 5,
    "speed": 1.05
  }'
```

### 从其他机器测试 UI

1. 打开浏览器
2. 访问 `http://SERVER_IP:8501`
3. 应该能看到 Streamlit 界面

---

## 📱 移动设备访问

### 手机/平板访问

1. **确保设备在同一 WiFi 网络**
2. **查找服务器 IP**:
   ```bash
   # 在服务器上执行
   hostname -I | awk '{print $1}'
   ```
3. **在移动设备浏览器中访问**:
   - UI: `http://[服务器IP]:8501`
   - API: `http://[服务器IP]:8088`

### 示例

假设服务器 IP 为 `192.168.1.100`：
- 在手机浏览器输入: `http://192.168.1.100:8501`

---

## 🔒 安全建议

### 生产环境部署

当前配置允许所有 IP 访问，适合以下场景：
- ✅ 内网环境
- ✅ 开发测试
- ✅ 有其他安全层保护（如 VPN、负载均衡器）

**如果要公网部署，建议添加以下安全措施**：

#### 1. 使用 Nginx 反向代理 + SSL

```nginx
# /etc/nginx/sites-available/supertonic
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # UI
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8088/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 2. 添加 API 认证

修改 `py/tts_server.py` 添加 API Key 验证：

```python
API_KEY = os.getenv("API_KEY", "your-secret-key")

@app.before_request
def verify_api_key():
    if request.path != "/health":
        key = request.headers.get("X-API-Key")
        if key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
```

#### 3. 限制 IP 访问范围

如果只允许特定 IP 段访问，修改 `docker-compose.yml`：

```yaml
ports:
  - "192.168.1.0/24:8088:8000"  # 仅允许 192.168.1.x 网段访问
```

#### 4. 使用 VPN

- 部署 WireGuard 或 OpenVPN
- 只允许 VPN 用户访问服务
- 端口映射改为 localhost only:
  ```yaml
  ports:
    - "127.0.0.1:8088:8000"
  ```

#### 5. 启用速率限制

使用 Nginx limit_req 模块：

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20;
    proxy_pass http://localhost:8088/;
}
```

---

## 🛠️ Docker 配置详情

### docker-compose.yml 端口配置

```yaml
services:
  supertonic-tts-server:
    ports:
      - "0.0.0.0:8088:8000"  # ✓ 允许所有 IP 访问
    command: python3 tts_server.py --host 0.0.0.0 --port 8000 --use-gpu
    # ↑ --host 0.0.0.0 确保容器内服务监听所有接口

  supertonic-tts-ui:
    ports:
      - "0.0.0.0:8501:8501"  # ✓ 允许所有 IP 访问
    # Streamlit 启动命令包含 --server.address=0.0.0.0
```

### 端口绑定格式说明

| 格式 | 说明 | 访问范围 |
|------|------|----------|
| `"8088:8000"` | 默认绑定到 0.0.0.0 | 所有 IP ✓ |
| `"0.0.0.0:8088:8000"` | 显式绑定到所有 IP | 所有 IP ✓ |
| `"127.0.0.1:8088:8000"` | 仅本地访问 | 仅 localhost |
| `"192.168.1.100:8088:8000"` | 仅指定 IP | 仅该 IP |

**当前配置**: `"0.0.0.0:8088:8000"` 和 `"0.0.0.0:8501:8501"` ✅

---

## 📊 网络连接监控

### 查看当前连接

```bash
# 查看端口监听状态
ss -tuln | grep -E "(8088|8501)"

# 查看活跃连接
ss -tun | grep -E "(8088|8501)"

# 查看 Docker 容器网络
docker inspect supertonic-tts-server | grep IPAddress
docker inspect supertonic-tts-ui | grep IPAddress
```

### 实时监控连接

```bash
# 监控 API 服务连接
watch -n 1 'ss -tun | grep 8088 | wc -l'

# 监控 UI 服务连接
watch -n 1 'ss -tun | grep 8501 | wc -l'
```

---

## 🔍 故障排除

### 问题 1: 无法从其他机器访问

**检查清单**:
1. ✓ 服务是否运行: `docker-compose ps`
2. ✓ 端口是否监听: `ss -tuln | grep -E "(8088|8501)"`
3. ✓ 防火墙是否开放: `sudo ufw status`
4. ✓ 云安全组是否配置
5. ✓ 网络连通性: `ping SERVER_IP`

**解决方案**:
```bash
# 1. 检查服务状态
docker-compose ps

# 2. 检查端口
ss -tuln | grep -E "(8088|8501)"

# 3. 测试本地访问
curl http://localhost:8088/health
curl http://localhost:8501/_stcore/health

# 4. 检查防火墙
sudo ufw status
sudo ufw allow 8088/tcp
sudo ufw allow 8501/tcp

# 5. 重启服务
docker-compose restart
```

### 问题 2: 端口已被占用

```bash
# 查找占用端口的进程
sudo lsof -i :8088
sudo lsof -i :8501

# 或使用 ss
ss -tulpn | grep -E "(8088|8501)"

# 停止占用的进程或更换端口
```

### 问题 3: 连接超时

可能原因：
- 防火墙阻止
- 路由问题
- 服务未正确绑定到 0.0.0.0

**验证**:
```bash
# 在服务器上测试
curl http://localhost:8088/health

# 从其他机器测试
telnet SERVER_IP 8088
telnet SERVER_IP 8501
```

---

## 📝 使用示例

### Python 客户端

```python
import requests

# 替换为实际服务器 IP
SERVER_IP = "192.168.1.100"
API_URL = f"http://{SERVER_IP}:8088"

def synthesize(text, voice="M1", steps=5, speed=1.05):
    url = f"{API_URL}/synthesize"
    data = {
        "text": text,
        "voice_style": f"assets/voice_styles/{voice}.json",
        "total_steps": steps,
        "speed": speed
    }
    response = requests.post(url, json=data)
    return response.json()

# 使用
result = synthesize("你好，世界！")
print(f"音频文件: {result['output_file']}")
```

### JavaScript 客户端

```javascript
// 替换为实际服务器 IP
const SERVER_IP = '192.168.1.100';
const API_URL = `http://${SERVER_IP}:8088`;

async function synthesize(text, voice = 'M1', steps = 5, speed = 1.05) {
  const response = await fetch(`${API_URL}/synthesize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text,
      voice_style: `assets/voice_styles/${voice}.json`,
      total_steps: steps,
      speed: speed
    })
  });
  return await response.json();
}

// 使用
synthesize('你好，世界！').then(result => {
  console.log('音频文件:', result.output_file);
});
```

---

## ✅ 配置验证

### 当前状态检查

```bash
# 1. 服务状态
docker-compose ps
# 预期: 两个服务都是 "Up"

# 2. 端口绑定
ss -tuln | grep -E "(8088|8501)"
# 预期:
# tcp   LISTEN 0.0.0.0:8088
# tcp   LISTEN 0.0.0.0:8501

# 3. API 健康检查
curl http://localhost:8088/health
# 预期: {"status": "healthy", "gpu_enabled": true}

# 4. UI 健康检查
curl http://localhost:8501/_stcore/health
# 预期: ok
```

### 访问测试清单

- [x] 本地访问 API: http://localhost:8088/health
- [x] 本地访问 UI: http://localhost:8501
- [ ] 局域网访问 API: http://[服务器IP]:8088/health
- [ ] 局域网访问 UI: http://[服务器IP]:8501
- [ ] 公网访问（如需要）

---

## 🎉 配置完成

所有服务已配置为允许所有 IP 访问：

✅ **API 服务器**: 0.0.0.0:8088 → 8000
✅ **Streamlit UI**: 0.0.0.0:8501 → 8501
✅ **容器内服务**: 监听 0.0.0.0
✅ **自动重启**: always
✅ **GPU 加速**: 已启用

**现在可以从任何网络位置访问服务！**

---

*更新时间: 2025-11-22*
*配置状态: ✅ 已验证*
