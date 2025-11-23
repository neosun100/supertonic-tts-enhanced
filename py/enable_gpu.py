#!/usr/bin/env python3
"""
GPU Enable Patch for Supertonic TTS

This script patches helper.py to enable GPU support.
Run this before starting the server if you want to use GPU.
"""

import sys

def patch_helper():
    """Patch helper.py to enable GPU support"""

    helper_file = 'helper.py'

    print("Reading helper.py...")
    with open(helper_file, 'r') as f:
        content = f.read()

    # Check if already patched
    if '# GPU ENABLED BY PATCH' in content:
        print("✓ helper.py is already patched for GPU support")
        return

    # Find and replace the GPU check
    old_code = '''def load_text_to_speech(onnx_dir: str, use_gpu: bool = False) -> TextToSpeech:
    opts = ort.SessionOptions()
    if use_gpu:
        raise NotImplementedError("GPU mode is not fully tested")
    else:
        providers = ["CPUExecutionProvider"]
        print("Using CPU for inference")'''

    new_code = '''def load_text_to_speech(onnx_dir: str, use_gpu: bool = False) -> TextToSpeech:
    opts = ort.SessionOptions()
    # GPU ENABLED BY PATCH
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
                print("✓ GPU mode enabled")
            else:
                print("⚠️  CUDA Execution Provider not available, falling back to CPU")
                providers = ["CPUExecutionProvider"]
        except Exception as e:
            print(f"⚠️  Error initializing GPU: {e}")
            print("Falling back to CPU")
            providers = ["CPUExecutionProvider"]
    else:
        providers = ["CPUExecutionProvider"]
        print("Using CPU for inference")'''

    if old_code not in content:
        print("ERROR: Could not find the code to patch in helper.py")
        print("The file may have been modified or this patch is incompatible.")
        return False

    # Apply patch
    content = content.replace(old_code, new_code)

    # Write back
    print("Writing patched helper.py...")
    with open(helper_file, 'w') as f:
        f.write(content)

    print("✓ Successfully patched helper.py for GPU support!")
    print("\nYou can now use --use-gpu flag with your scripts.")
    print("To test GPU support, run:")
    print("  python3 example_onnx.py --use-gpu")
    return True


if __name__ == '__main__':
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("="*60)
    print("Supertonic TTS - GPU Enable Patch")
    print("="*60)
    print()

    result = patch_helper()

    if result == False:
        sys.exit(1)
