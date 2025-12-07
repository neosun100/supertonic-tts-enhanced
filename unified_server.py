#!/usr/bin/env python3
"""
统一服务 - 单端口提供 UI、API 和 MCP
- /          -> Streamlit UI (反向代理)
- /api/*     -> FastAPI REST API
- /mcp/*     -> MCP WebSocket
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from threading import Thread

sys.path.insert(0, str(Path(__file__).parent / "py"))

from fastapi import FastAPI, HTTPException, WebSocket, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import soundfile as sf
import httpx

from helper import load_text_to_speech, load_voice_style

# ============================================================================
# 配置
# ============================================================================

STREAMLIT_PORT = 8502
API_PORT = 8501

# ============================================================================
# FastAPI 应用
# ============================================================================

app = FastAPI(
    title="Supertonic TTS",
    description="统一 TTS 服务：UI + API + MCP",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# 模型
# ============================================================================

class SynthesizeRequest(BaseModel):
    text: str = Field(..., description="要合成的文本")
    voice_style: str = Field("assets/voice_styles/M1.json")
    total_steps: int = Field(5, ge=1, le=50)
    speed: float = Field(1.05, ge=0.5, le=2.0)

# ============================================================================
# 全局变量
# ============================================================================

tts_model = None
results_dir = Path("/app/results")
results_dir.mkdir(exist_ok=True)
streamlit_process = None

# ============================================================================
# Streamlit 后台进程
# ============================================================================

def start_streamlit():
    """启动 Streamlit"""
    global streamlit_process
    time.sleep(2)  # 等待 FastAPI 启动
    streamlit_process = subprocess.Popen([
        "streamlit", "run", "/app/streamlit_app.py",
        "--server.port", str(STREAMLIT_PORT),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "true",
        "--server.enableXsrfProtection", "false",
        "--server.enableWebsocketCompression", "false",
        "--server.baseUrlPath", ""
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"✅ Streamlit 已启动在端口 {STREAMLIT_PORT}")

Thread(target=start_streamlit, daemon=True).start()

# ============================================================================
# 启动事件
# ============================================================================

@app.on_event("startup")
async def startup():
    global tts_model
    print("🚀 加载 TTS 模型...")
    use_gpu = os.getenv("USE_GPU", "true").lower() == "true"
    onnx_dir = "/app/assets/onnx"
    tts_model = load_text_to_speech(onnx_dir, use_gpu=use_gpu)
    print("✅ TTS 模型加载完成")

# ============================================================================
# API 路由
# ============================================================================

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "service": "Supertonic TTS Unified",
        "gpu_enabled": os.getenv("USE_GPU", "true").lower() == "true"
    }

@app.post("/api/synthesize")
async def synthesize(req: SynthesizeRequest):
    try:
        start = time.time()
        
        voice_path = Path(req.voice_style)
        if not voice_path.exists():
            voice_path = Path("/app") / req.voice_style
        
        voice_style = load_voice_style(str(voice_path))
        audio = tts_model(req.text, voice_style, total_steps=req.total_steps, speed=req.speed)
        
        filename = f"output_{int(time.time()*1000)}.wav"
        output_path = results_dir / filename
        sf.write(str(output_path), audio, 16000)
        
        return {
            "status": "success",
            "output_file": filename,
            "generation_time": round(time.time() - start, 3),
            "text_length": len(req.text),
            "audio_duration": round(len(audio) / 16000, 2)
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/results/{filename}")
async def get_audio(filename: str):
    file_path = results_dir / filename
    if not file_path.exists():
        raise HTTPException(404, "文件不存在")
    return FileResponse(file_path, media_type="audio/wav")

# ============================================================================
# MCP WebSocket
# ============================================================================

@app.websocket("/mcp/ws")
async def mcp_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("method") == "synthesize":
                params = data.get("params", {})
                req = SynthesizeRequest(**params)
                result = await synthesize(req)
                
                await websocket.send_json({
                    "id": data.get("id"),
                    "result": result
                })
            else:
                await websocket.send_json({
                    "id": data.get("id"),
                    "error": {"code": -32601, "message": "方法不存在"}
                })
    except:
        pass

@app.get("/mcp/info")
async def mcp_info():
    return {
        "name": "Supertonic TTS MCP",
        "version": "1.0.0",
        "endpoint": "/mcp/ws",
        "methods": ["synthesize"]
    }

# ============================================================================
# Streamlit 反向代理
# ============================================================================

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_streamlit(request: Request, path: str):
    """代理所有其他请求到 Streamlit"""
    
    # 跳过已处理的路径
    if path.startswith("api/") or path.startswith("mcp/"):
        raise HTTPException(404)
    
    url = f"http://127.0.0.1:{STREAMLIT_PORT}/{path}"
    query = str(request.url.query)
    if query:
        url = f"{url}?{query}"
    
    async with httpx.AsyncClient() as client:
        headers = dict(request.headers)
        headers.pop("host", None)
        
        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=await request.body(),
                timeout=30.0
            )
            
            return StreamingResponse(
                response.aiter_bytes(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.ConnectError:
            raise HTTPException(503, "Streamlit 服务未就绪")

# ============================================================================
# 主入口
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Supertonic TTS 统一服务")
    print("=" * 60)
    print(f"📍 UI:  http://localhost:{API_PORT}/")
    print(f"📍 API: http://localhost:{API_PORT}/api/")
    print(f"📍 MCP: ws://localhost:{API_PORT}/mcp/ws")
    print(f"📍 文档: http://localhost:{API_PORT}/api/docs")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=API_PORT, log_level="info")
