import collections
import math


def bin_str2bool_list(binary_string):
    return [c == '1' for c in binary_string]


def bool_list2bin_str(boolean_list):
    return ''.join('1' if i else '0' for i in boolean_list)


def bool_list2int(boolean_list):
    return sum(v << i for i, v in enumerate(reversed(boolean_list)))


def entropy(byte_seq):
    counter = collections.Counter(byte_seq)
    ret = 0
    for count in counter.values():
        prob = count / sum(counter.values())
        ret += prob * math.log2(prob)
    return -ret
