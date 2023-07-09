import numpy as np
from PIL import Image
import io

class AdaptiveHuffman:
    class Node:
        def __init__(self, symbol=None, weight=0, parent=None, left=None, right=None):
            self.symbol = symbol
            self.weight = weight
            self.parent = parent
            self.left = left
            self.right = right

    def __init__(self, path=None, file=None):
        self.path = path
        if file is not None:
            self.file = file.read()

        self.data = None
        self.tree = None
        self.dictionary = {}
        self.next_code = 0

    def initialize_tree(self):
        self.tree = self.Node(weight=0)
        self.dictionary = {}
        self.next_code = 0

    def update_tree(self, symbol):
        if symbol in self.dictionary:
            node = self.dictionary[symbol]
            while node.parent is not None:
                node.weight += 1
                node = node.parent
            node.weight += 1
        else:
            if self.tree.left is None:
                new_node = self.Node(symbol=symbol, weight=1, parent=self.tree, left=None, right=None)
                self.tree.left = new_node
                self.dictionary[symbol] = new_node
                self.next_code += 1
                self.check_node(new_node)
            else:
                node = self.tree.left
                while node.right is not None:
                    node = node.right
                new_node = self.Node(symbol=symbol, weight=1, parent=node.parent, left=None, right=None)
                node.right = new_node
                self.dictionary[symbol] = new_node
                self.next_code += 1
                self.check_node(new_node)

    def check_node(self, node):
        while node is not None:
            max_weight_node = self.get_max_weight_node(node)
            if max_weight_node is not None and max_weight_node is not node:
                self.swap_nodes(node, max_weight_node)
            node = node.parent

    def get_max_weight_node(self, node):
        max_weight_node = None
        if node is not None and node.parent is not None:
            if node.parent.left is not None:
                max_weight_node = node.parent.left
            if node.parent.right is not None and node.parent.right.weight > max_weight_node.weight:
                max_weight_node = node.parent.right
        return max_weight_node

    def swap_nodes(self, node1, node2):
        node1.symbol, node2.symbol = node2.symbol, node1.symbol
        self.dictionary[node1.symbol], self.dictionary[node2.symbol] = self.dictionary[node2.symbol], self.dictionary[node1.symbol]

    def encode_adaptive_huffman(self, text):
        self.initialize_tree()
        encoded_numbers = []
        encoded_letters = []
        for symbol in text:
            if symbol in self.dictionary:
                node = self.dictionary[symbol]
                code = self.get_code(node)
                encoded_numbers.append(code)
                encoded_letters.append("")
                self.update_tree(symbol)
            else:
                encoded_numbers.append(self.next_code)
                encoded_letters.append(symbol)
                self.update_tree(symbol)
        return encoded_numbers, encoded_letters

    def get_code(self, node):
        code = ""
        while node.parent is not None:
            if node.parent.left is node:
                code = "0" + code
            else:
                code = "1" + code
            node = node.parent
        return code

    def get_image_size(self):
        image = Image.open(io.BytesIO(self.file))
        return image.size

    def decode_adaptive_huffman(self, encoded_data, channels=3):
        self.initialize_tree()
        decoded_string = ""
        i = 0
        while i < len(encoded_data):
            code = int(encoded_data[i])
            if code in self.dictionary.keys():
                symbol = self.dictionary[code].symbol
                decoded_string += str(symbol)
                self.update_tree(symbol)
            else:
                symbol = encoded_data[i + 1]
                decoded_string += str(symbol)
                self.update_tree(symbol)
                i += 1
            i += 1
        return decoded_string, self.get_image_shape(decoded_string, channels)

    def get_image_shape(self, decoded_string, channels):
        width, height = self.get_image_size()
        total_pixels = width * height
        expected_length = total_pixels * channels
        if len(decoded_string) != expected_length:
            raise ValueError("Decoded string length does not match the expected image size.")
        return width, height

    def compress(self):
        image = Image.open(self.path)
        data = np.asarray(image, dtype=np.uint8)
        string_to_encode = data.tobytes()
        compressed_data = self.encode_adaptive_huffman(string_to_encode)
        return compressed_data

    def decompress(self):
        decoded_rows = []
        for line in self.file:
            decoded_row = self.decompressRow(line)
            decoded_rows.append(decoded_row)

        decoded_image = np.array(decoded_rows, dtype=np.uint8)
        image = Image.fromarray(decoded_image, 'RGB')
        return image

    def decompressRow(self, line):
        current_row = line.split(",")
        current_row[-1] = current_row[-1][:-1]
        decoded_row = []
        decoded_row.append(int(current_row[0]))
        word = str(current_row[0])
        for i in range(1, len(current_row)):
            new = int(current_row[i])
            if new in self.decompressionDictionary:
                entry = self.decompressionDictionary[new]
            else:
                entry = word + word[0]
            decoded_row.append(entry)
            self.decompressionDictionary[self.decompressionIndex] = word + entry[0]
            self.decompressionIndex += 1
            word = entry
        return decoded_row

