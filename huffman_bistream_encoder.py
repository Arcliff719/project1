"""Task B: bit-level Huffman encoder for lossless text compression.

This module is intentionally focused on the encoder role in the project split:
- teammate A supplies a Huffman codebook: ``{character: "010..."}``
- this encoder packs the resulting bits into real bytes, not a text string of 0/1
- teammate C can read the self-describing file header and then decode the payload

Compressed file layout (big-endian):
    4 bytes   magic: b"ITP1"
    1 byte    version: 1
    4 bytes   JSON header length N
    N bytes   UTF-8 JSON header
    ...       packed payload bits, most-significant bit first in each byte
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Mapping, Sequence, Any

MAGIC = b"ITP1"
VERSION = 1
_HEADER_PREFIX = ">4sBI"  # magic, version, JSON header length
_HEADER_PREFIX_SIZE = struct.calcsize(_HEADER_PREFIX)


class CodebookError(ValueError):
    """Raised when the Huffman codebook cannot be used safely."""


def validate_codebook(codebook: Mapping[str, str]) -> dict[str, str]:
    """Return a normalized, prefix-free codebook.

    The encoder accepts exactly one Unicode character per key and bit strings as
    values. Prefix-free validation catches accidental non-Huffman mappings before
    producing a file that teammate C cannot decode unambiguously.
    """
    if not codebook:
        raise CodebookError("codebook must not be empty")

    normalized: dict[str, str] = {}
    for character, bits in codebook.items():
        if not isinstance(character, str) or len(character) != 1:
            raise CodebookError(f"codebook key {character!r} must be one character")
        if not isinstance(bits, str) or not bits or set(bits) - {"0", "1"}:
            raise CodebookError(f"code for {character!r} must be a non-empty bit string")
        normalized[character] = bits

    sorted_codes = sorted(normalized.items(), key=lambda item: (len(item[1]), item[1]))
    for index, (left_char, left_bits) in enumerate(sorted_codes):
        for right_char, right_bits in sorted_codes[index + 1 :]:
            if len(right_bits) <= len(left_bits):
                continue
            if right_bits.startswith(left_bits):
                raise CodebookError(
                    f"codebook is not prefix-free: {left_char!r}->{left_bits!r} "
                    f"is a prefix of {right_char!r}->{right_bits!r}"
                )
    return normalized


def pack_bits(bit_stream: str) -> tuple[bytes, int]:
    """Pack a string of 0/1 bits into bytes and return ``(payload, padding)``.

    Bits are written most-significant first. The final byte is padded with zeroes
    only when needed; the exact number of padding bits is stored in the header.
    """
    if set(bit_stream) - {"0", "1"}:
        raise ValueError("bit_stream may only contain '0' and '1'")

    padding_bits = (-len(bit_stream)) % 8
    padded_bits = bit_stream + ("0" * padding_bits)
    payload = bytearray()
    for start in range(0, len(padded_bits), 8):
        byte_bits = padded_bits[start : start + 8]
        payload.append(int(byte_bits, 2))
    return bytes(payload), padding_bits


def encode_text_to_payload(text: str, codebook: Mapping[str, str]) -> tuple[bytes, int, int]:
    """Encode text with ``codebook`` and return payload bytes plus metadata."""
    normalized = validate_codebook(codebook)
    missing = sorted({character for character in text if character not in normalized})
    if missing:
        preview = ", ".join(repr(character) for character in missing[:8])
        raise CodebookError(f"text contains characters missing from codebook: {preview}")

    bit_stream = "".join(normalized[character] for character in text)
    payload, padding_bits = pack_bits(bit_stream)
    return payload, padding_bits, len(bit_stream)


def build_header(
    *,
    codebook: Mapping[str, str],
    padding_bits: int,
    original_length: int,
    encoded_bit_length: int,
) -> bytes:
    """Build the UTF-8 JSON header needed by teammate C's decoder."""
    normalized = validate_codebook(codebook)
    header = {
        "format": "huffman-bitstream-v1",
        "codec": "huffman",
        "padding_bits": padding_bits,
        "original_length": original_length,
        "encoded_bit_length": encoded_bit_length,
        "codebook": [[character, normalized[character]] for character in sorted(normalized)],
    }
    return json.dumps(header, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def encode_text(text: str, codebook: Mapping[str, str]) -> bytes:
    """Return the complete compressed binary document for ``text``."""
    normalized = validate_codebook(codebook)
    payload, padding_bits, encoded_bit_length = encode_text_to_payload(text, normalized)
    header_bytes = build_header(
        codebook=normalized,
        padding_bits=padding_bits,
        original_length=len(text),
        encoded_bit_length=encoded_bit_length,
    )
    prefix = struct.pack(_HEADER_PREFIX, MAGIC, VERSION, len(header_bytes))
    return prefix + header_bytes + payload


def encode_file(input_path: str | Path, output_path: str | Path, codebook: Mapping[str, str]) -> None:
    """Read a UTF-8 text file and write the compressed binary file."""
    text = Path(input_path).read_text(encoding="utf-8")
    compressed = encode_text(text, codebook)
    Path(output_path).write_bytes(compressed)


def parse_compressed_header(compressed: bytes) -> tuple[dict[str, Any], bytes]:
    """Parse the file header and return ``(header, payload)`` for teammate C."""
    if len(compressed) < _HEADER_PREFIX_SIZE:
        raise ValueError("compressed data is too short to contain a header")
    magic, version, header_length = struct.unpack(
        _HEADER_PREFIX, compressed[:_HEADER_PREFIX_SIZE]
    )
    if magic != MAGIC:
        raise ValueError(f"bad magic {magic!r}; expected {MAGIC!r}")
    if version != VERSION:
        raise ValueError(f"unsupported version {version}; expected {VERSION}")

    header_start = _HEADER_PREFIX_SIZE
    header_end = header_start + header_length
    if len(compressed) < header_end:
        raise ValueError("compressed data ended before the JSON header was complete")
    header = json.loads(compressed[header_start:header_end].decode("utf-8"))
    return header, compressed[header_end:]


def load_codebook(path: str | Path) -> dict[str, str]:
    """Load teammate A's codebook from JSON.

    Supported JSON forms:
    - ``{"a": "0", "b": "10"}``
    - ``{"codebook": {"a": "0", "b": "10"}}``
    - ``[["a", "0"], ["b", "10"]]``
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "codebook" in raw:
        raw = raw["codebook"]
    if isinstance(raw, dict):
        return validate_codebook({str(character): str(bits) for character, bits in raw.items()})
    if isinstance(raw, Sequence):
        return validate_codebook({str(character): str(bits) for character, bits in raw})
    raise CodebookError("codebook JSON must be a mapping or a list of [character, bits] pairs")


def main() -> None:
    parser = argparse.ArgumentParser(description="Task B Huffman bitstream encoder")
    parser.add_argument("input", help="UTF-8 source text file from document D")
    parser.add_argument("output", help="binary compressed document C to write")
    parser.add_argument("--codebook", required=True, help="JSON codebook generated by teammate A")
    args = parser.parse_args()

    codebook = load_codebook(args.codebook)
    encode_file(args.input, args.output, codebook)


if __name__ == "__main__":
    main()
