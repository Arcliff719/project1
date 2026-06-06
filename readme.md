diff --git a/readme.md b/readme.md
index e69de29bb2d1d6434b8b29ae775ad8c2e48c5391..47684fc870aae7dd8afb6276f2dc707f96b7170f 100644
--- a/readme.md
+++ b/readme.md
@@ -0,0 +1,39 @@
+# 信息论 Project 1：Task B 位流编码器

+## 压缩文件格式
+
+压缩结果采用自描述格式，便于同学 C 跨文件解析：
+
+1. `4` 字节 magic：`ITP1`
+2. `1` 字节版本号：`1`
+3. `4` 字节大端 JSON 头部长度
+4. UTF-8 JSON 头部：包含 `padding_bits`、`original_length`、`encoded_bit_length` 和 `codebook`
+5. 按高位优先写入的压缩 payload bytes
+
+## 使用方法
+
+同学 A 的密码本可保存为以下任意 JSON 形式：
+
+```json
+{"a": "0", "b": "10", "\n": "110", "中": "111"}
+```
+
+或：
+
+```json
+{"codebook": {"a": "0", "b": "10", "\n": "110", "中": "111"}}
+```
+
+运行压缩：
+
+```bash
+python huffman_bitstream_encoder.py input.txt compressed.bin --codebook codebook.json
+```
+
+核心接口：
+
+- `encode_text(text, codebook)`：返回完整压缩二进制内容。
+- `encode_file(input_path, output_path, codebook)`：从文本文件生成压缩二进制文件。
+- `parse_compressed_header(compressed)`：解析文件头并返回 `(header, payload)`，供同学 C 对接解压器。
