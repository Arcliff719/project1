#!/usr/bin/env python3
"""
Project 1 — Huffman Coding: Lossless Text Compression
======================================================
Command-line interface for compressing and decompressing text files
using Huffman coding.

Usage
-----
  # Compress a text file
  python main.py compress input.txt -o compressed.huff

  # Decompress a .huff file
  python main.py decompress compressed.huff -o output.txt

  # Full pipeline with verification report
  python main.py run input.txt
"""

import argparse
import os
import sys

from huffman.tree import build_codebook_from_text, count_frequencies
from huffman.encoder import compress, save_compressed
from huffman.decoder import decompress, save_decompressed
from huffman.verify import print_report


def cmd_compress(args):
    """Compress a text file using Huffman coding."""
    # Read input text
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    if not text:
        print("Error: input file is empty.", file=sys.stderr)
        sys.exit(1)

    print(f"Read {len(text):,} characters from '{args.input}'")

    # Student A: build frequency table, tree, and codebook
    codebook, tree_root, freq = build_codebook_from_text(text)
    print(f"Built codebook with {len(codebook)} unique characters")
    print(f"Tree depth: {_tree_depth(tree_root)}")

    # Student B: compress to binary
    compressed_data = compress(text, codebook)
    output_path = args.output or args.input + ".huff"
    with open(output_path, "wb") as f:
        f.write(compressed_data)

    original_size = len(text.encode("utf-8"))
    compressed_size = len(compressed_data)
    ratio = compressed_size / original_size if original_size > 0 else 1.0

    print(f"Compressed: {original_size:,} → {compressed_size:,} bytes "
          f"(ratio: {ratio:.4f}, saving: {(1-ratio)*100:.2f}%)")
    print(f"Saved to: '{output_path}'")


def cmd_decompress(args):
    """Decompress a .huff file back to text."""
    print(f"Decompressing '{args.input}'...")

    # Student C: decompress
    text = decompress(args.input)

    output_path = args.output or args.input.replace(".huff", "") + ".txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Decompressed {len(text):,} characters to '{output_path}'")


def cmd_run(args):
    """Full pipeline: compress → decompress → verify."""
    input_path = args.input
    compressed_path = args.input + ".huff"
    reconstructed_path = args.input + ".reconstructed.txt"

    # Read original
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    if not text:
        print("Error: input file is empty.", file=sys.stderr)
        sys.exit(1)

    print(f"=== Pipeline: {input_path} ===")
    print(f"Original text: {len(text):,} characters, "
          f"{len(text.encode('utf-8')):,} bytes\n")

    # Student A
    codebook, tree_root, freq = build_codebook_from_text(text)
    print(f"[Student A] Codebook: {len(codebook)} unique symbols")
    print(f"[Student A] Tree max depth: {_tree_depth(tree_root)}")

    # Student B
    save_compressed(compressed_path, text, codebook)
    compressed_size = os.path.getsize(compressed_path)
    print(f"[Student B] Compressed: {compressed_size:,} bytes → '{compressed_path}'")

    # Student C
    reconstructed = save_decompressed(compressed_path, reconstructed_path)
    print(f"[Student C] Decompressed: {len(reconstructed):,} chars → '{reconstructed_path}'")

    # Student D
    print()
    print_report(input_path, compressed_path, reconstructed_path,
                 codebook, freq)


def _tree_depth(node, depth=0):
    """Compute max depth of the Huffman tree."""
    if node is None:
        return depth
    if node.is_leaf():
        return depth
    return max(_tree_depth(node.left, depth + 1),
               _tree_depth(node.right, depth + 1))


def main():
    parser = argparse.ArgumentParser(
        description="Huffman Coding — Lossless Text Compression (Project 1)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ---- compress ----
    p_comp = sub.add_parser("compress", help="Compress a text file")
    p_comp.add_argument("input", help="Input .txt file")
    p_comp.add_argument("-o", "--output", help="Output .huff file")

    # ---- decompress ----
    p_decomp = sub.add_parser("decompress", help="Decompress a .huff file")
    p_decomp.add_argument("input", help="Input .huff file")
    p_decomp.add_argument("-o", "--output", help="Output .txt file")

    # ---- run (full pipeline) ----
    p_run = sub.add_parser("run", help="Run full compress→decompress→verify pipeline")
    p_run.add_argument("input", help="Input .txt file")

    args = parser.parse_args()

    if args.command == "compress":
        cmd_compress(args)
    elif args.command == "decompress":
        cmd_decompress(args)
    elif args.command == "run":
        cmd_run(args)


if __name__ == "__main__":
    main()
