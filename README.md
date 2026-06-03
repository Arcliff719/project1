# Project 1: 无损信源编码 — 霍夫曼编码 (Huffman Coding)

## 项目流程

```
初始文档 D  ──压缩──▶  压缩文档 C  ──解压──▶  重构文档 D'
                          (二进制 .bin)
```

D 与 D' 必须完全一致（无损），通过 MD5 校验或逐字符比对验证。

## A: 频率统计与霍夫曼树构建

### 使用方法

```bash
# 处理所有测试文本，生成密码本 JSON
python huffman_coding.py
```

### 输入

- 任意 `.txt` 文本文件（UTF-8 编码）

### 输出

对每个输入文件生成一个 `mapping_<文件名>.json`：

```json
{
  "source_file": "sample_news.txt",
  "total_chars": 1796,
  "unique_chars": 59,
  "mapping": {
    "e": "010",
    " ": "110",
    "t": "1110",
    "a": "1000",
    ...
  }
}
```

| 字段 | 说明 |
|------|------|
| `source_file` | 原始文件名 |
| `total_chars` | 原始文本总字符数 |
| `unique_chars` | 不同字符的数量 |
| `mapping` | 字符 → 二进制编码 的映射表（前缀码） |

### 控制台输出

运行后还会打印：
- 字符频率表（按频率降序）
- 霍夫曼编码表（按码长排序）
- 信息熵 H(X)、平均码长 L、编码效率

### 给 B 的接口

```python
import json

# 同学 B 加载密码本
with open('mapping_sample_news.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

mapping = data['mapping']  # dict: {char: binary_str}
# 例: mapping['e'] → '010'
#     mapping[' '] → '110'
```

## 测试结果概览

| 测试文件 | 字符数 | 不同字符 | 熵 H(X) | 平均码长 | 编码效率 | 理论压缩比 |
|---------|--------|---------|---------|---------|---------|-----------|
| sample_mygo.txt | 2,168 | 47 | 4.3273 | 4.3570 | 99.32% | 54.46% |
| sample_news.txt | 1,796 | 59 | 4.4431 | 4.4627 | 99.56% | 55.78% |
| sample_literature.txt | 1,993 | 47 | 4.4110 | 4.4581 | 98.94% | 55.73% |
| sample_technical.txt | 2,107 | 57 | 4.4448 | 4.4656 | 99.54% | 55.82% |
| sample_dialogue.txt | 1,725 | 50 | 4.5271 | 4.5623 | 99.23% | 57.03% |

---
