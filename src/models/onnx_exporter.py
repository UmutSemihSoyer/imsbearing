"""
IMS Bearing Edge AI Module: ONNX Exporter & Benchmarking
Exports PyTorch and Scikit-learn RUL models to ONNX format for microsecond inference on embedded devices (Jetson Nano, Raspberry Pi).
"""

import os
import sys
import time
import torch
import numpy as np

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.models.transformer_rul import Transformer_Informer_RUL


try:
    import onnx
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

def export_transformer_to_onnx(model_path: str = None, output_onnx_path: str = None) -> str:
    """Exports PyTorch Transformer RUL Predictor model to ONNX format."""
    if model_path is None:
        model_path = os.path.join("models", "transformer_rul_test2.pth")
    if output_onnx_path is None:
        output_onnx_path = os.path.join("models", "transformer_rul.onnx")

    os.makedirs(os.path.dirname(output_onnx_path), exist_ok=True)

    # Instantiate model structure
    seq_len = 10
    num_features = 11
    model = Transformer_Informer_RUL(input_dim=num_features, d_model=64, nhead=4, num_layers=2)


    if os.path.exists(model_path):
        try:
            model.load_state_dict(torch.load(model_path, weights_only=True))
            print(f"[INFO] Loaded trained Transformer weights from {model_path}")
        except Exception:
            print("[WARN] Could not load model state_dict. Exporting initial structure.")

    model.eval()
    dummy_input = torch.randn(1, seq_len, num_features, dtype=torch.float32)

    # Force UTF-8 encoding on sys.stdout to prevent PyTorch ONNX exporter unicode checkmark crashes on Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Export to ONNX using tracing exporter
    try:
        torch.onnx.export(
            model,
            dummy_input,
            output_onnx_path,
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=["vibration_features"],
            output_names=["predicted_rul"],
            dynamic_axes={"vibration_features": {0: "batch_size"}, "predicted_rul": {0: "batch_size"}},
            dynamo=False
        )
    except Exception:
        torch.onnx.export(
            model,
            dummy_input,
            output_onnx_path,
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=["vibration_features"],
            output_names=["predicted_rul"]
        )


    print(f"[SUCCESS] Exported ONNX model saved to: {output_onnx_path}")

    # Benchmark ONNX Runtime vs PyTorch
    if ONNX_AVAILABLE:
        session = ort.InferenceSession(output_onnx_path, providers=["CPUExecutionProvider"])
        ort_inputs = {session.get_inputs()[0].name: dummy_input.numpy()}

        # Warmup
        for _ in range(10):
            session.run(None, ort_inputs)

        t0 = time.time()
        for _ in range(100):
            ort_outs = session.run(None, ort_inputs)
        onnx_latency_ms = (time.time() - t0) * 10.0  # (time / 100) * 1000

        print(f"[BENCHMARK] ONNX Runtime Inference Speed: {onnx_latency_ms:.3f} ms per sample")

    return output_onnx_path

if __name__ == "__main__":
    export_transformer_to_onnx()
