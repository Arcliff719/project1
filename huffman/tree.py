"""
Student A: Frequency Statistics & Huffman Tree Builder
========================================================
Core tasks:
  1. Read input .txt file and count character frequencies/probabilities
  2. Build Huffman Tree using a min-heap / priority queue
  3. Generate the codebook (char -> binary code string) for Student B

Dependencies: Python standard library only (collections.Counter, heapq)
"""

import heapq
from collections import Counter
from typing import Dict, Optional, Tuple


# ---------------------------------------------------------------------------
# Huffman Tree Node
# ---------------------------------------------------------------------------

class HuffmanNode:
    """Node in a Huffman tree.

    Attributes
    ----------
    char : str or None
        The character stored at this leaf node (None for internal nodes).
    freq : int
        Frequency (or weight) of this node.
    left : HuffmanNode or None
        Left child (represents binary '0').
    right : HuffmanNode or None
        Right child (represents binary '1').
    """

    def __init__(self, char: Optional[str], freq: int,
                 left: Optional["HuffmanNode"] = None,
                 right: Optional["HuffmanNode"] = None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def is_leaf(self) -> bool:
        """Return True if this node is a leaf (has a character)."""
        return self.char is not None

    # Comparison operators for heapq (min-heap by frequency)
    def __lt__(self, other: "HuffmanNode") -> bool:
        return self.freq < other.freq

    def __eq__(self, other: "HuffmanNode") -> bool:
        return self.freq == other.freq


# ---------------------------------------------------------------------------
# Frequency counting
# ---------------------------------------------------------------------------

def count_frequencies(text: str) -> Counter:
    """Count the frequency of each character in the input text.

    Parameters
    ----------
    text : str
        The input text to analyze.

    Returns
    -------
    collections.Counter
        A counter mapping each character to its occurrence count.
    """
    return Counter(text)


# ---------------------------------------------------------------------------
# Huffman tree construction
# ---------------------------------------------------------------------------

def build_huffman_tree(freq_table: Dict[str, int]) -> HuffmanNode:
    """Build a Huffman tree from a character frequency table.

    Uses a min-heap (priority queue) to repeatedly combine the two
    lowest-frequency nodes until a single root remains.

    Parameters
    ----------
    freq_table : dict
        Mapping from character (str) to frequency count (int).
        Must contain at least one character.

    Returns
    -------
    HuffmanNode
        The root node of the constructed Huffman tree.

    Raises
    ------
    ValueError
        If the frequency table is empty.
    """
    if not freq_table:
        raise ValueError("Cannot build Huffman tree from empty frequency table.")

    # Create a leaf node for each character and push into min-heap
    heap: list = []
    for char, freq in freq_table.items():
        heapq.heappush(heap, HuffmanNode(char=char, freq=freq))

    # Edge case: single unique character → create a dummy node so the tree
    # has at least one internal node (required for proper encoding).
    if len(heap) == 1:
        only_node = heap[0]
        # Create a parent with a dummy left child; the only char is on the right.
        dummy = HuffmanNode(char=None, freq=only_node.freq,
                            left=None, right=only_node)
        heap = [dummy]

    # Repeatedly merge the two smallest-frequency nodes
    while len(heap) > 1:
        left = heapq.heappop(heap)   # smaller freq → '0' branch
        right = heapq.heappop(heap)  # larger freq  → '1' branch
        parent = HuffmanNode(char=None, freq=left.freq + right.freq,
                             left=left, right=right)
        heapq.heappush(heap, parent)

    return heap[0]


# ---------------------------------------------------------------------------
# Codebook generation
# ---------------------------------------------------------------------------

def build_codebook(root: HuffmanNode) -> Dict[str, str]:
    """Traverse the Huffman tree to produce a codebook: char → binary code string.

    Performs a DFS from the root.  Left edges append '0', right edges append '1'.
    When a leaf node is reached, the accumulated bit-string is recorded.

    Parameters
    ----------
    root : HuffmanNode
        The root of the Huffman tree.

    Returns
    -------
    dict
        Mapping from character (str) to its Huffman code (str of '0'/'1').
    """
    codebook: Dict[str, str] = {}

    def _dfs(node: HuffmanNode, code: str):
        if node.is_leaf():
            codebook[node.char] = code
            return
        if node.left:
            _dfs(node.left, code + "0")
        if node.right:
            _dfs(node.right, code + "1")

    _dfs(root, "")
    return codebook


# ---------------------------------------------------------------------------
# Convenience: full pipeline from text → codebook
# ---------------------------------------------------------------------------

def build_codebook_from_text(text: str) -> Tuple[Dict[str, str], HuffmanNode, Counter]:
    """One-shot: count frequencies, build tree, generate codebook.

    Parameters
    ----------
    text : str
        The input text.

    Returns
    -------
    tuple (codebook, tree_root, freq_counter)
    """
    freq = count_frequencies(text)
    root = build_huffman_tree(dict(freq))
    codebook = build_codebook(root)
    return codebook, root, freq
