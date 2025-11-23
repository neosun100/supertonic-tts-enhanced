#!/usr/bin/env python3
"""
Simple HTTP server for Supertonic TTS
Provides a REST API for text-to-speech synthesis
"""

import json
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import argparse
import soundfile as sf

# Import TTS helper functions
from helper import load_text_to_speech, load_voice_style

class TTSHandler(BaseHTTPRequestHandler):
    """HTTP request handler for TTS API"""

    def do_GET(self):
        """Handle GET requests - health check"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'healthy',
                'service': 'Supertonic TTS',
                'gpu_enabled': self.server.use_gpu
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle POST requests - TTS synthesis"""
        if self.path == '/synthesize':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode())

                # Extract parameters
                text = data.get('text', '')
                voice_style_path = data.get('voice_style', self.server.default_voice_style)
                total_steps = data.get('total_steps', 5)
                speed = data.get('speed', 1.05)

                if not text:
                    self.send_error(400, "Missing 'text' parameter")
                    return

                # Load voice style
                style = load_voice_style([voice_style_path], verbose=False)

                # Generate speech
                start_time = time.time()
                wav, duration = self.server.tts(text, style, total_steps, speed)
                generation_time = time.time() - start_time

                # Trim audio to actual duration
                audio = wav[0, : int(self.server.tts.sample_rate * duration[0].item())]

                # Save to file
                output_filename = f"output_{int(time.time())}.wav"
                output_path = os.path.join(self.server.results_dir, output_filename)

                sf.write(output_path, audio, samplerate=self.server.tts.sample_rate)

                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                response = {
                    'status': 'success',
                    'output_file': output_filename,
                    'generation_time': round(generation_time, 3),
                    'text_length': len(text),
                    'audio_duration': float(duration[0].item())
                }
                self.wfile.write(json.dumps(response).encode())

            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_error(500, f"Error during synthesis: {str(e)}")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(host='0.0.0.0', port=8000, onnx_dir='assets/onnx',
               voice_style='assets/voice_styles/M1.json', use_gpu=False,
               results_dir='results'):
    """Start the TTS HTTP server"""

    print("="*60)
    print("Supertonic TTS Server")
    print("="*60)

    # Load TTS model
    print(f"Loading TTS model from {onnx_dir}...")

    # If GPU is requested, check availability
    if use_gpu:
        print("⚠️  WARNING: GPU mode is experimental but enabled")
        print("Attempting to enable GPU support...")
        try:
            # Import onnxruntime to check providers
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

    tts = load_text_to_speech(onnx_dir, use_gpu)
    print("✓ TTS model loaded successfully")

    # Create results directory
    os.makedirs(results_dir, exist_ok=True)

    # Create server
    server = HTTPServer((host, port), TTSHandler)
    server.tts = tts
    server.use_gpu = use_gpu
    server.default_voice_style = voice_style
    server.results_dir = results_dir

    print(f"✓ Server listening on http://{host}:{port}")
    print(f"  - Health check: GET  http://{host}:{port}/health")
    print(f"  - Synthesize:   POST http://{host}:{port}/synthesize")
    print("\nExample curl command:")
    print(f'curl -X POST http://localhost:8088/synthesize \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"text": "Hello, this is a test.", "total_steps": 5}\'')
    print("\nPress Ctrl+C to stop the server")
    print("="*60)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Supertonic TTS HTTP Server')
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
        use_gpu=args.use_gpu,
        results_dir=args.results_dir
    )
