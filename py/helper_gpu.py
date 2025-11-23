#!/usr/bin/env python3
"""
Modified helper.py with GPU support enabled
This is an experimental version that allows GPU inference
"""

# Import all from original helper
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import everything from helper
from helper import *
import onnxruntime as ort

# Override the load_text_to_speech function to enable GPU
def load_text_to_speech_gpu(onnx_dir: str, use_gpu: bool = False):
    """
    Load TTS model with GPU support enabled

    Args:
        onnx_dir: Path to ONNX model directory
        use_gpu: Whether to use GPU (experimental)

    Returns:
        TextToSpeech object
    """
    opts = ort.SessionOptions()

    if use_gpu:
        print("⚠️  WARNING: GPU mode is experimental and not fully tested")
        print("Attempting to use CUDA Execution Provider...")
        try:
            # Try CUDA first
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            # Test if CUDA provider is available
            available_providers = ort.get_available_providers()
            if "CUDAExecutionProvider" in available_providers:
                print("✓ CUDA Execution Provider is available")
            else:
                print("⚠️  CUDA Execution Provider not available, falling back to CPU")
                providers = ["CPUExecutionProvider"]
        except Exception as e:
            print(f"⚠️  Error initializing GPU: {e}")
            print("Falling back to CPU")
            providers = ["CPUExecutionProvider"]
    else:
        providers = ["CPUExecutionProvider"]
        print("Using CPU for inference")

    cfgs = load_cfgs(onnx_dir)
    dp_ort, text_enc_ort, vector_est_ort, vocoder_ort = load_onnx_all(
        onnx_dir, opts, providers
    )

    # Print which provider is actually being used
    if use_gpu:
        print(f"Duration Predictor using: {dp_ort.get_providers()}")
        print(f"Text Encoder using: {text_enc_ort.get_providers()}")
        print(f"Vector Estimator using: {vector_est_ort.get_providers()}")
        print(f"Vocoder using: {vocoder_ort.get_providers()}")

    tts = TextToSpeech(
        cfgs=cfgs,
        duration_predictor=dp_ort,
        text_encoder=text_enc_ort,
        vector_estimator=vector_est_ort,
        vocoder=vocoder_ort,
    )
    return tts


if __name__ == "__main__":
    print("This is a helper module for GPU-enabled TTS")
    print("Use with tts_server.py or example scripts")
