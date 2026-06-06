import json
import tempfile
import unittest
from pathlib import Path

from huffman_bitstream_encoder import (
    CodebookError,
    encode_file,
    encode_text,
    load_codebook,
    pack_bits,
    parse_compressed_header,
)


def decode_for_test(compressed: bytes) -> str:
    header, payload = parse_compressed_header(compressed)
    reverse_codebook = {bits: character for character, bits in header["codebook"]}
    bits = "".join(f"{byte:08b}" for byte in payload)
    if header["padding_bits"]:
        bits = bits[: -header["padding_bits"]]

    decoded = []
    current = ""
    for bit in bits:
        current += bit
        if current in reverse_codebook:
            decoded.append(reverse_codebook[current])
            current = ""
    if current:
        raise AssertionError(f"leftover undecoded bits: {current}")
    return "".join(decoded)


class HuffmanBitstreamEncoderTest(unittest.TestCase):
    def test_pack_bits_uses_real_bytes_with_padding_metadata(self):
        payload, padding = pack_bits("101010101")
        self.assertEqual(payload, bytes([0b10101010, 0b10000000]))
        self.assertEqual(padding, 7)

    def test_encode_text_writes_self_describing_lossless_binary_document(self):
        codebook = {"a": "0", "b": "10", "\n": "110", "中": "111"}
        source = "abba\n中a"

        compressed = encode_text(source, codebook)
        header, payload = parse_compressed_header(compressed)

        self.assertEqual(header["format"], "huffman-bitstream-v1")
        self.assertEqual(header["original_length"], len(source))
        self.assertGreater(len(payload), 0)
        self.assertEqual(decode_for_test(compressed), source)

    def test_encode_file_accepts_json_codebook_from_teammate_a(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            input_path = directory_path / "input.txt"
            codebook_path = directory_path / "codebook.json"
            output_path = directory_path / "compressed.bin"
            input_path.write_text("cab cab", encoding="utf-8")
            codebook_path.write_text(
                json.dumps({"codebook": {"c": "00", "a": "01", "b": "10", " ": "11"}}),
                encoding="utf-8",
            )

            encode_file(input_path, output_path, load_codebook(codebook_path))

            self.assertEqual(decode_for_test(output_path.read_bytes()), "cab cab")

    def test_rejects_ambiguous_non_prefix_free_codebook(self):
        with self.assertRaises(CodebookError):
            encode_text("ab", {"a": "0", "b": "01"})


if __name__ == "__main__":
    unittest.main()
