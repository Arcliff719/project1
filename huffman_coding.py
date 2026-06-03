"""
同学 A: 频率统计与霍夫曼树构建 (Frequency Statistics & Huffman Tree Builder)

核心功能:
  1. 读取 .txt 文本文件，统计每个字符的出现频率/概率
  2. 使用最小堆/优先队列 (heapq) 构建霍夫曼树
  3. 生成 "字符 -> 二进制字符串" 的密码本 (Mapping Table)
  4. 将密码本导出为 JSON 文件，供同学 B 使用
  5. 计算信息熵、平均码长等理论指标

协作接口:
  - 输出: mapping_<filename>.json  (供同学 B 的编码器使用)
  - 输出: 控制台打印频率表、霍夫曼编码表、效率指标
"""

import heapq
import json
import math
import os
from collections import Counter


class HuffmanNode:
    """霍夫曼树节点"""

    def __init__(self, char, freq, left=None, right=None):
        self.char = char          # 字符 (叶子节点), 内部节点为 None
        self.freq = freq          # 频率/权重
        self.left = left          # 左子节点 (路径: '0')
        self.right = right        # 右子节点 (路径: '1')

    def __lt__(self, other):
        """用于 heapq 最小堆排序，按频率比较"""
        return self.freq < other.freq


def count_frequencies(text: str) -> dict:
    """
    统计文本中每个字符的出现次数和概率。

    参数:
        text: 输入文本字符串

    返回:
        dict: {char: {'count': int, 'probability': float}, ...}
    """
    total = len(text)
    if total == 0:
        return {}

    counter = Counter(text)
    freq_dict = {}
    for char, count in counter.items():
        freq_dict[char] = {
            'count': count,
            'probability': count / total
        }
    return freq_dict


def build_huffman_tree(freq_dict: dict) -> HuffmanNode:
    """
    使用最小堆构建霍夫曼树。

    参数:
        freq_dict: {char: {'count': int, 'probability': float}, ...}

    返回:
        HuffmanNode: 霍夫曼树的根节点
    """
    if not freq_dict:
        return None

    # 为每个字符创建叶子节点，压入最小堆
    heap = []
    for char, info in freq_dict.items():
        node = HuffmanNode(char=char, freq=info['count'])
        heapq.heappush(heap, node)

    # 特殊情况：只有一个字符时，创建一个虚拟父节点
    if len(heap) == 1:
        only_node = heapq.heappop(heap)
        parent = HuffmanNode(char=None, freq=only_node.freq, left=only_node, right=None)
        return parent

    # 循环合并频率最小的两个节点
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(
            char=None,
            freq=left.freq + right.freq,
            left=left,
            right=right
        )
        heapq.heappush(heap, merged)

    return heap[0]


def generate_codes(root: HuffmanNode) -> dict:
    """
    从霍夫曼树根节点出发，深度优先遍历生成每个字符的二进制编码。

    规则: 走左分支追加 '0', 走右分支追加 '1'

    参数:
        root: 霍夫曼树的根节点

    返回:
        dict: {char: binary_string, ...}
    """
    if root is None:
        return {}

    codes = {}

    def dfs(node: HuffmanNode, code: str):
        if node.char is not None:
            # 叶子节点：存入编码
            codes[node.char] = code if code else '0'  # 单字符情况用 '0'
            return
        if node.left:
            dfs(node.left, code + '0')
        if node.right:
            dfs(node.right, code + '1')

    dfs(root, '')
    return codes


def calculate_entropy(freq_dict: dict) -> float:
    """
    计算信息熵 H(X) = -Σ p(x) log₂ p(x)

    参数:
        freq_dict: 频率字典

    返回:
        float: 信息熵 (bits per symbol)
    """
    entropy = 0.0
    for info in freq_dict.values():
        p = info['probability']
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def calculate_avg_code_length(freq_dict: dict, codes: dict) -> float:
    """
    计算平均码长 L = Σ p(x) * len(code(x))

    参数:
        freq_dict: 频率字典
        codes: 字符->编码 映射

    返回:
        float: 平均码长
    """
    avg_len = 0.0
    for char, info in freq_dict.items():
        if char in codes:
            avg_len += info['probability'] * len(codes[char])
    return avg_len


def calculate_efficiency(entropy: float, avg_code_length: float) -> float:
    """
    计算编码效率 = 熵 / 平均码长 * 100%
    """
    if avg_code_length == 0:
        return 0.0
    return (entropy / avg_code_length) * 100.0


def save_mapping(codes: dict, freq_dict: dict, filepath: str, source_file: str):
    """
    将密码本和相关元数据导出为 JSON 文件，供同学 B 使用。

    JSON 结构:
    {
        "source_file": "原始文件名",
        "total_chars": 总字符数,
        "unique_chars": 不同字符数量,
        "mapping": { 字符: 二进制编码, ... }
    }
    """
    mapping_data = {
        "source_file": source_file,
        "total_chars": sum(info['count'] for info in freq_dict.values()),
        "unique_chars": len(codes),
        "mapping": codes
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(mapping_data, f, ensure_ascii=False, indent=2)


def process_file(filepath: str):
    """
    处理单个文本文件：统计频率、构建树、生成编码、输出结果。

    参数:
        filepath: .txt 文件的路径
    """
    print("=" * 70)
    print(f"处理文件: {filepath}")
    print(f"文件名:   {os.path.basename(filepath)}")
    print("=" * 70)

    # 读取文本
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    if not text:
        print("⚠ 文件为空，跳过处理。\n")
        return

    total_chars = len(text)
    print(f"\n文件大小: {total_chars} 字符")

    # 1. 统计字符频率
    freq_dict = count_frequencies(text)
    unique_chars = len(freq_dict)
    print(f"不同字符数: {unique_chars}\n")

    # 2. 打印频率表 (按频率降序)
    print("字符频率表 (按频率降序, 前 30 个):")
    print("-" * 50)
    print(f"{'字符':<8} {'次数':<10} {'概率':<12} {'显示'}")
    print("-" * 50)
    sorted_freq = sorted(freq_dict.items(), key=lambda x: x[1]['count'], reverse=True)
    for char, info in sorted_freq[:30]:
        display = repr(char)
        print(f"{display:<8} {info['count']:<10} {info['probability']:<12.6f} {display}")
    if unique_chars > 30:
        print(f"... 共 {unique_chars} 个不同字符，仅显示前 30 个")
    print()

    # 3. 构建霍夫曼树
    root = build_huffman_tree(freq_dict)

    # 4. 生成编码表
    codes = generate_codes(root)

    # 5. 打印编码表
    print("霍夫曼编码表 (按码长排序, 前 30 个):")
    print("-" * 50)
    print(f"{'字符':<8} {'频率':<8} {'码长':<8} {'编码'}")
    print("-" * 50)
    sorted_codes = sorted(codes.items(), key=lambda x: (len(x[1]), x[1]))
    for char, code in sorted_codes[:30]:
        display = repr(char)
        freq_info = freq_dict[char]
        print(f"{display:<8} {freq_info['count']:<8} {len(code):<8} {code}")
    if len(codes) > 30:
        print(f"... 共 {len(codes)} 个编码，仅显示前 30 个")
    print()

    # 6. 计算理论指标
    entropy = calculate_entropy(freq_dict)
    avg_code_length = calculate_avg_code_length(freq_dict, codes)
    efficiency = calculate_efficiency(entropy, avg_code_length)
    original_bits = total_chars * 8  # ASCII/UTF-8 按 8 bits 每字符估算
    compressed_bits = sum(
        freq_dict[char]['count'] * len(codes[char])
        for char in codes
    )
    compression_ratio = compressed_bits / original_bits
    original_bytes = total_chars
    compressed_bytes = math.ceil(compressed_bits / 8)

    print("编码效率分析:")
    print("-" * 50)
    print(f"  信息熵 H(X):          {entropy:.4f} bits/字符")
    print(f"  平均码长 L:            {avg_code_length:.4f} bits/字符")
    print(f"  编码效率:              {efficiency:.2f}%")
    print(f"  原始大小 (8-bit):      {original_bytes} bytes (约)")
    print(f"  压缩后估计大小:        {compressed_bytes} bytes (约)")
    print(f"  理论压缩比:            {compression_ratio:.4f} ({compression_ratio*100:.2f}%)")
    print(f"  理论空间节省:          {(1-compression_ratio)*100:.2f}%")

    # 7. 保存映射表供同学 B 使用
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    mapping_path = os.path.join(os.path.dirname(filepath), f"mapping_{base_name}.json")
    save_mapping(codes, freq_dict, mapping_path, os.path.basename(filepath))
    print(f"\n密码本已导出至: {mapping_path}")
    print()


def main():
    """主入口：处理所有测试文本文件"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 测试文件列表
    test_files = [
        os.path.join(script_dir, "sample_mygo.txt"),
        os.path.join(script_dir, "sample_news.txt"),
        os.path.join(script_dir, "sample_literature.txt"),
        os.path.join(script_dir, "sample_technical.txt"),
        os.path.join(script_dir, "sample_dialogue.txt"),
    ]

    print("\n" + "=" * 70)
    print("  霍夫曼编码 - 频率统计与编码表生成 (同学 A)")
    print("=" * 70)

    for filepath in test_files:
        if os.path.exists(filepath):
            process_file(filepath)
        else:
            print(f"\n⚠ 文件不存在，跳过: {filepath}")

    print("=" * 70)
    print("  所有文件处理完毕！密码本 JSON 文件已生成。")
    print("=" * 70)


if __name__ == '__main__':
    main()
