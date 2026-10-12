"""
Confirmed as the 2026 sweet spot on modern accelerators: FP8
quantization in production serving, with INT4 further down the
memory/quality tradeoff curve for more aggressive compression. This
works the actual quantization math, scale and zero-point, on a real
weight value, then computes the memory savings at a realistic model
size, not just the compression ratio in the abstract.
"""

import numpy as np


def quantize_to_int8(weights: np.ndarray) -> dict:
    """
    The real quantization formula: find the scale that maps the
    weight range onto the available integer range, then round every
    weight to its nearest representable integer value.
    """
    w_min, w_max = weights.min(), weights.max()
    scale = (w_max - w_min) / 255  # int8 range is 0-255 once zero-pointed
    zero_point = round(-w_min / scale)

    quantized = np.round(weights / scale + zero_point).astype(np.int32)
    quantized = np.clip(quantized, 0, 255)

    dequantized = (quantized.astype(np.float32) - zero_point) * scale
    return {"scale": scale, "zero_point": zero_point, "quantized": quantized, "dequantized": dequantized}


def main() -> None:
    # A handful of real-looking weight values, small enough to verify
    # the quantization and dequantization error by hand.
    weights = np.array([-0.342, 0.128, 0.891, -0.675, 0.045, 0.332])

    result = quantize_to_int8(weights)

    print(f"Original FP32 weights: {weights}")
    print(f"Scale: {result['scale']:.6f}, zero point: {result['zero_point']}")
    print(f"Quantized to INT8 (0-255): {result['quantized']}")
    print(f"Dequantized back to float: {np.round(result['dequantized'], 4)}")

    error = np.abs(weights - result['dequantized'])
    print(f"Quantization error per weight: {np.round(error, 5)}")
    print(f"Max error: {error.max():.5f}, this is the real, permanent precision lost to quantization")

    # Memory savings at a realistic model size.
    n_params = 70_000_000_000  # a 70B parameter model
    fp32_bytes = n_params * 4
    fp16_bytes = n_params * 2
    fp8_bytes = n_params * 1
    int4_bytes = n_params * 0.5

    print(f"\nMemory needed to hold a {n_params/1e9:.0f}B parameter model's weights:")
    print(f"  FP32: {fp32_bytes/1e9:.1f} GB")
    print(f"  FP16: {fp16_bytes/1e9:.1f} GB  ({100*(1-fp16_bytes/fp32_bytes):.0f}% smaller than FP32)")
    print(f"  FP8:  {fp8_bytes/1e9:.1f} GB  ({100*(1-fp8_bytes/fp32_bytes):.0f}% smaller than FP32)")
    print(f"  INT4: {int4_bytes/1e9:.1f} GB  ({100*(1-int4_bytes/fp32_bytes):.0f}% smaller than FP32)")

    print(
        "\nConfirmed as the current 2026 default for production serving on "
        "modern accelerators: FP8 is the sweet spot, roughly halving FP16's "
        "memory footprint with quality loss small enough to be acceptable "
        "for most workloads. INT4 goes further, down to an eighth of the "
        "original FP32 size, at a real, measurable quality cost, which is "
        "why it's reached for specifically when memory is the binding "
        "constraint, not reached for by default."
    )
    print(
        "\nThe per-weight error computed above is not a rounding artifact "
        "to ignore. It's the actual, permanent precision every single "
        "weight loses, multiplied across every parameter in the model. "
        "Quantization is a real tradeoff, not a free compression trick, "
        "which is exactly why the choice of precision is a production "
        "decision, not an automatic default."
    )


if __name__ == "__main__":
    main()
