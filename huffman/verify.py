"""
Student D: Verification & Efficiency Metrics
=============================================
Core tasks:
  1. Verify lossless: byte-by-byte or MD5 comparison of D vs D'
  2. Calculate compression ratio
  3. Compute information entropy H(X)
  4. Compute average code length and coding efficiency
"""

import hashlib
import math
import os
from collections import Counter


def md5_checksum(text: str) -> str:
    """Compute the MD5 hash of a text string (UTF-8 encoded)."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def verify_lossless(original: str, reconstructed: str) -> bool:
    """Check that original D and reconstructed D' are identical.

    Returns True if they are byte-for-byte identical.
    """
    return original == reconstructed


def compression_ratio(original_size: int, compressed_size: int) -> float:
    """Compute the compression ratio.

    compression_ratio = compressed_size / original_size

    Lower values indicate better compression.
    """
    if original_size == 0:
        return 1.0
    return compressed_size / original_size


def compression_saving(original_size: int, compressed_size: int) -> float:
    """Space saving: (1 - compressed/original) * 100%"""
    if original_size == 0:
        return 0.0
    return (1.0 - compressed_size / original_size) * 100.0


def information_entropy(freq_counter: Counter) -> float:
    """Calculate Shannon entropy H(X) = -Σ p(x) log₂ p(x).

    Parameters
    ----------
    freq_counter : collections.Counter
        Character frequency counts.

    Returns
    -------
    float
        Entropy in bits per symbol.
    """
    total = freq_counter.total()
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in freq_counter.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def average_code_length(codebook: dict, freq_counter: Counter) -> float:
    """Compute average code length L̄ = Σ p(x) · length(code(x)).

    Parameters
    ----------
    codebook : dict
        char → binary code string.
    freq_counter : Counter
        Character frequency counts.

    Returns
    -------
    float
        Average code length in bits per symbol.
    """
    total = freq_counter.total()
    if total == 0:
        return 0.0
    avg_len = 0.0
    for char, count in freq_counter.items():
        p = count / total
        avg_len += p * len(codebook[char])
    return avg_len


def coding_efficiency(entropy: float, avg_code_len: float) -> float:
    """Coding efficiency η = H(X) / L̄.

    Returns value in [0, 1].  Closer to 1 = better.
    """
    if avg_code_len == 0:
        return 1.0
    return entropy / avg_code_len


def print_report(original_path: str, compressed_path: str,
                 reconstructed_path: str, codebook: dict,
                 freq_counter: Counter):
    """Print a full verification and efficiency report."""
    with open(original_path, "r", encoding="utf-8") as f:
        original = f.read()
    with open(reconstructed_path, "r", encoding="utf-8") as f:
        reconstructed = f.read()

    original_size = os.path.getsize(original_path)
    compressed_size = os.path.getsize(compressed_path)

    lossless = verify_lossless(original, reconstructed)
    cr = compression_ratio(original_size, compressed_size)
    saving = compression_saving(original_size, compressed_size)
    entropy = information_entropy(freq_counter)
    avg_len = average_code_length(codebook, freq_counter)
    efficiency = coding_efficiency(entropy, avg_len)

    print("=" * 60)
    print("  Project 1 — Huffman Coding Verification Report")
    print("=" * 60)
    print(f"  Original file:        {original_path}")
    print(f"  Compressed file:      {compressed_path}")
    print(f"  Reconstructed file:   {reconstructed_path}")
    print(f"  MD5(D):               {md5_checksum(original)}")
    print(f"  MD5(D'):              {md5_checksum(reconstructed)}")
    print(f"  Lossless (D == D'):   {'✓ PASS' if lossless else '✗ FAIL'}")
    print("-" * 60)
    print(f"  Original size:        {original_size:>10,} bytes")
    print(f"  Compressed size:      {compressed_size:>10,} bytes")
    print(f"  Compression ratio:    {cr:>10.4f}")
    print(f"  Space saving:         {saving:>10.2f}%")
    print("-" * 60)
    print(f"  Entropy H(X):         {entropy:>10.4f} bits/symbol")
    print(f"  Avg code length L̄:    {avg_len:>10.4f} bits/symbol")
    print(f"  Coding efficiency η:  {efficiency:>10.4f} ({efficiency*100:.2f}%)")
    print("=" * 60)
