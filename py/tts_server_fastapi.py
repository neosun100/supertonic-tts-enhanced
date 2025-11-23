#!/usr/bin/env python3
"""
FastAPI server for Supertonic TTS with Swagger documentation
Provides a REST API for text-to-speech synthesis with auto-generated API docs
"""

import os
import time
import argparse
import soundfile as sf
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

# Import TTS helper functions
from helper import load_text_to_speech, load_voice_style

# ============================================================================
# API Models (Pydantic schemas for request/response validation)
# ============================================================================

class SynthesizeRequest(BaseModel):
    """Request model for TTS synthesis"""
    text: str = Field(..., description="Text to synthesize", example="Hello, this is a test.")
    voice_style: Optional[str] = Field(
        None,
        description="Path to voice style JSON file",
        example="assets/voice_styles/M1.json"
    )
    total_steps: int = Field(
        5,
        description="Number of diffusion steps (higher = better quality, slower)",
        ge=1,
        le=50,
        example=5
    )
    speed: float = Field(
        1.05,
        description="Speech speed multiplier",
        ge=0.5,
        le=2.0,
        example=1.05
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "Hello, this is a test of the Supertonic TTS system.",
                "total_steps": 5,
                "speed": 1.05
            }
        }


class SynthesizeResponse(BaseModel):
    """Response model for TTS synthesis"""
    status: str = Field(..., description="Status of the operation", example="success")
    output_file: str = Field(..., description="Generated audio filename", example="output_1234567890.wav")
    generation_time: float = Field(..., description="Time taken to generate audio in seconds", example=2.345)
    text_length: int = Field(..., description="Length of input text", example=42)
    audio_duration: float = Field(..., description="Duration of generated audio in seconds", example=3.5)


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status", example="healthy")
    service: str = Field(..., description="Service name", example="Supertonic TTS")
    gpu_enabled: bool = Field(..., description="Whether GPU acceleration is enabled", example=False)


# ============================================================================
# FastAPI Application
# ============================================================================

# Create FastAPI app with metadata for Swagger UI
app = FastAPI(
    title="Supertonic TTS API",
    description="""
    ## Supertonic Text-to-Speech API

    This API provides high-quality text-to-speech synthesis using the Supertonic TTS model.

    ### Features
    - High-quality voice synthesis
    - Customizable voice styles
    - Adjustable speech speed
    - GPU acceleration support (when available)

    ### Endpoints
    - **GET /health** - Check service health status
    - **POST /synthesize** - Generate speech from text
    - **GET /docs** - Interactive API documentation (Swagger UI)
    - **GET /redoc** - Alternative API documentation (ReDoc)

    ### Usage Example
    ```bash
    curl -X POST http://localhost:8088/synthesize \\
      -H "Content-Type: application/json" \\
      -d '{
        "text": "Hello, this is a test.",
        "total_steps": 5,
        "speed": 1.05
      }'
    ```
    """,
    version="1.0.0",
    contact={
        "name": "Supertonic TTS",
        "url": "https://github.com/your-repo/supertonic",
    },
    license_info={
        "name": "MIT",
    },
)

# Global TTS model instance
tts_model = None
use_gpu = False
default_voice_style = None
results_dir = None


@app.on_event("startup")
async def startup_event():
    """Initialize TTS model on startup"""
    global tts_model, use_gpu, default_voice_style, results_dir

    print("="*60)
    print("Supertonic TTS FastAPI Server")
    print("="*60)

    # Get configuration from app state (set during server start)
    onnx_dir = app.state.onnx_dir
    use_gpu = app.state.use_gpu
    default_voice_style = app.state.default_voice_style
    results_dir = app.state.results_dir

    print(f"Loading TTS model from {onnx_dir}...")

    # Check GPU availability
    if use_gpu:
        print("⚠️  WARNING: GPU mode is experimental but enabled")
        print("Attempting to enable GPU support...")
        try:
            import onnxruntime as ort
            available_providers = ort.get_available_providers()
            print(f"Available ONNX providers: {available_providers}")

            if "CUDAExecutionProvider" in available_providers:
                print("✓ CUDA is available - enabling GPU mode")
            else:
                print("⚠️  CUDA not available, falling back to CPU")
                use_gpu = False
        except Exception as e:
            print(f"Error checking GPU: {e}")
            use_gpu = False

    # Load TTS model
    tts_model = load_text_to_speech(onnx_dir, use_gpu)
    print("✓ TTS model loaded successfully")

    # Create results directory
    os.makedirs(results_dir, exist_ok=True)

    print(f"✓ Server ready")
    print(f"  - API documentation: http://0.0.0.0:8000/docs")
    print(f"  - Alternative docs:  http://0.0.0.0:8000/redoc")
    print(f"  - Health check:      http://0.0.0.0:8000/health")
    print(f"  - Synthesize:        http://0.0.0.0:8000/synthesize")
    print(f"  - Download audio:    http://0.0.0.0:8000/{{filename}}")
    print("="*60)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the TTS service is running and healthy",
    tags=["Health"]
)
async def health_check():
    """
    Check the health status of the TTS service.

    Returns:
        HealthResponse: Service health information
    """
    return HealthResponse(
        status="healthy",
        service="Supertonic TTS",
        gpu_enabled=use_gpu
    )


@app.post(
    "/synthesize",
    response_model=SynthesizeResponse,
    summary="Synthesize Speech",
    description="Generate speech audio from input text",
    tags=["TTS"]
)
async def synthesize_speech(request: SynthesizeRequest):
    """
    Generate speech from text using the Supertonic TTS model.

    Args:
        request (SynthesizeRequest): TTS synthesis parameters

    Returns:
        SynthesizeResponse: Information about the generated audio

    Raises:
        HTTPException: If synthesis fails
    """
    try:
        # Use default voice style if not provided
        voice_style_path = request.voice_style or default_voice_style

        # Load voice style
        style = load_voice_style([voice_style_path], verbose=False)

        # Generate speech
        start_time = time.time()
        wav, duration = tts_model(request.text, style, request.total_steps, request.speed)
        generation_time = time.time() - start_time

        # Trim audio to actual duration
        audio = wav[0, : int(tts_model.sample_rate * duration[0].item())]

        # Save to file
        output_filename = f"output_{int(time.time())}.wav"
        output_path = os.path.join(results_dir, output_filename)

        sf.write(output_path, audio, samplerate=tts_model.sample_rate)

        # Return response
        return SynthesizeResponse(
            status="success",
            output_file=output_filename,
            generation_time=round(generation_time, 3),
            text_length=len(request.text),
            audio_duration=float(duration[0].item())
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during synthesis: {str(e)}"
        )


@app.get(
    "/",
    summary="API Information",
    description="Get basic information about the API",
    tags=["Info"]
)
async def root():
    """
    Get basic API information and links to documentation.
    """
    return {
        "service": "Supertonic TTS API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "download": "/{filename}",
        "message": "Welcome to Supertonic TTS API! Visit /docs for interactive documentation."
    }


@app.get(
    "/{filename}",
    summary="Download Audio File",
    description="Download a generated audio file by filename",
    tags=["Download"],
    response_class=FileResponse
)
async def download_audio(filename: str):
    """
    Download a generated audio file.

    Args:
        filename (str): Name of the audio file (e.g., output_1234567890.wav)

    Returns:
        FileResponse: The audio file

    Raises:
        HTTPException: If file not found
    """
    # Security: Only allow .wav files and prevent directory traversal
    if not filename.endswith('.wav') or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = os.path.join(results_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        media_type="audio/wav",
        filename=filename
    )


# ============================================================================
# Server Entry Point
# ============================================================================

def run_server(host='0.0.0.0', port=8000, onnx_dir='assets/onnx',
               voice_style='assets/voice_styles/M1.json', use_gpu_flag=False,
               results_dir_path='results'):
    """Start the FastAPI TTS server"""

    # Set configuration in app state
    app.state.onnx_dir = onnx_dir
    app.state.use_gpu = use_gpu_flag
    app.state.default_voice_style = voice_style
    app.state.results_dir = results_dir_path

    # Run server with uvicorn
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Supertonic TTS FastAPI Server with Swagger')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--onnx-dir', type=str, default='assets/onnx', help='ONNX model directory')
    parser.add_argument('--voice-style', type=str, default='assets/voice_styles/M1.json',
                        help='Default voice style file')
    parser.add_argument('--use-gpu', action='store_true', help='Use GPU for inference (experimental)')
    parser.add_argument('--results-dir', type=str, default='results', help='Output directory')

    args = parser.parse_args()

    run_server(
        host=args.host,
        port=args.port,
        onnx_dir=args.onnx_dir,
        voice_style=args.voice_style,
        use_gpu_flag=args.use_gpu,
        results_dir_path=args.results_dir
    )
