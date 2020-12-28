import numpy as np
import random
import itertools
import time


def op(c, a, b):
    return int(c) | (int(a) & int(b))


def dot(A, B):
    C = np.dot(A, B)

    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            C[i][j] = C[i][j] % 2

    return C


G = np.array([[1, 0, 1, 1],
             [1, 1, 0, 1],
             [0, 0, 0, 1],
             [1, 1, 1, 0],
             [0, 0, 1, 0],
             [0, 1, 0, 0],
             [1, 0, 0, 0]])


def coded(code):
    return np.array([dot(G, block) for block in code], np.int16)


H = np.array([[0, 0, 0, 1, 1, 1, 1],
             [0, 1, 1, 0, 0, 1, 1],
             [1, 0, 1, 0, 1, 0, 1]])


def control_sum(code):
    return np.array([dot(H, block) for block in code])


def error_in(control):
    return control[2][0] * 1 + control[1][0] * 2 + control[0][0] * 4 - 1


def to_bits(string):
    res = np.array([], np.int16)
    for i in string:
        for j in range(8):
            res = np.append(res, (ord(i) >> j) & 1)

    return res.reshape((len(res)//4, 4, 1))


def rnd():
    from datetime import datetime
    random.seed(datetime.now())
    return int(random.random()*100)


def corrupted(blocks):
    blocks[int(rnd() % blocks.shape[0])][rnd() % 4][0] = int(blocks[int(rnd() % blocks.shape[0])][rnd() % 4][0]) ^ 1

    return blocks


def unhamming(blocks):
    key = []
    source = []

    for i in itertools.product([0, 1], repeat=4):
        key.append(dot(G, np.array(i).reshape((4, 1))))
        source.append(i)

    bits = np.array([], np.int)
    for i in blocks:
        for j in range(len(key)):
            if (key[j] == i).all():
                for k in source[j]:
                    bits = np.append(bits, [k])
    return bits


def to_str(bits):
    string = ""
    for i in range(len(bits) // 8):
        k = 0
        for j in range(8):
            k += (int(bits[i * 8 + j]) << j)

        string += chr(k)

    return string


def run(string):
    bits = to_bits(string)
    blocks = coded(bits.copy())

    corrupted_blocks = corrupted(blocks.copy())

    control = control_sum(corrupted_blocks.copy())

    tmp_blocks = corrupted_blocks.copy()
    corrupted_block_number = np.argmax(control) // 3
    corrupted_block_control = control[corrupted_block_number]

    tmp_blocks[corrupted_block_number][error_in(corrupted_block_control)][0] = \
        tmp_blocks[corrupted_block_number][error_in(corrupted_block_control)][0] ^ 1
    repaired_blocks = tmp_blocks.copy()

    assert ((blocks == repaired_blocks).all())

    repaired_bits = unhamming(repaired_blocks)

    assert ((bits.ravel() == repaired_bits).all())

    repaired_str = to_str(repaired_bits)

    assert (string == repaired_str)

    return repaired_str


if __name__ == '__main__':
    print(run("qwerty 123"))

