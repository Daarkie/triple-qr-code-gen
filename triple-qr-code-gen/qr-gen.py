from docutils.utils.roman import OutOfRangeError
from reedsolo import RSCodec


class QR:
    def __init__(self, text_data):
        self.text_data = text_data
        self.data_len = len(text_data)
        self.level = 0
        self.ec = 'L'
        self.encoded = "0010"

    def set_level_and_fill(self, level):
        self.level = level
        fill_qr(self)


# get character value
def get_alphanumeric_value(char):
    # digits 0-9 to values 0-9
    if '0' <= char <= '9':
        return ord(char) - ord('0')
    # uppercase letters A-Z to values 10-35
    elif 'A' <= char <= 'Z':
        return ord(char) - ord('A') + 10
    # special characters
    elif char == ' ':
        return 36
    elif char == '$':
        return 37
    elif char == '%':
        return 38
    elif char == '*':
        return 39
    elif char == '+':
        return 40
    elif char == '-':
        return 41
    elif char == '.':
        return 42
    elif char == '/':
        return 43
    elif char == ':':
        return 44
    else:
        raise ValueError(f"Character '{char}' not supported in alphanumeric mode")


def get_data_codeword_capacity(version, error_correction):
    # capacity table for versions 2-6
    capacity_table = {
        2: {'L': 34, 'M': 28, 'Q': 22, 'H': 16},
        3: {'L': 55, 'M': 44, 'Q': 34, 'H': 26},
        4: {'L': 80, 'M': 64, 'Q': 48, 'H': 36},
        5: {'L': 108, 'M': 86, 'Q': 62, 'H': 46},
        6: {'L': 136, 'M': 108, 'Q': 76, 'H': 60}
    }

    return capacity_table[version][error_correction]


# get capacity value
def get_capacity_value(data_size, level=0):
    capacity_table = {
        2: {'L': 47, 'M': 38, 'Q': 29, 'H': 20},
        3: {'L': 77, 'M': 61, 'Q': 47, 'H': 35},
        4: {'L': 114, 'M': 90, 'Q': 67, 'H': 50},
        5: {'L': 154, 'M': 122, 'Q': 87, 'H': 64},
        6: {'L': 195, 'M': 154, 'Q': 108, 'H': 84}
    }
    if level == 0:
        for i in range(2, 10):
            if capacity_table[i]['L'] >= data_size:
                return i
        raise OutOfRangeError(f"Size of data '{data_size}' not supported")
    else:
        if capacity_table[level]['H'] >= data_size:
            return 'H'
        if capacity_table[level]['Q'] >= data_size:
            return 'Q'
        if capacity_table[level]['M'] >= data_size:
            return 'M'
        return 'L'


# encoding with qr bits
def encode_alphanumeric_to_qr_binary(qr):
    text = qr.text_data.upper()

    # character count indicator (fill to 9 since we are only using versions 2-6)
    char_count = bin(len(text))[2:].zfill(9)
    qr.encoded += char_count

    # processing characters
    for i in range(0, len(text), 2):
        if i + 1 < len(text):
            # process a pair
            val1 = get_alphanumeric_value(text[i])
            val2 = get_alphanumeric_value(text[i + 1])
            value = val1 * 45 + val2
            # convert to 11-bit binary
            binary = bin(value)[2:].zfill(11)
            qr.encoded += binary
        else:
            # process a single character (last one if odd length)
            val = get_alphanumeric_value(text[i])
            # 6-bit binary
            binary = bin(val)[2:].zfill(6)
            qr.encoded += binary


def add_padding_bits(qr):
    # get room
    total_capacity_bits = get_data_codeword_capacity(qr.level, qr.ec) * 8

    # add terminator if there's room
    remaining_bits = total_capacity_bits - len(qr.encoded)
    if remaining_bits >= 4:
        qr.encoded += '0000'
        remaining_bits -= 4
    elif remaining_bits > 0:
        qr.encoded += '0' * remaining_bits
        remaining_bits = 0

    # make the length a multiple of 8 (byte alignment)
    bits_to_add = remaining_bits % 8
    if bits_to_add > 0:
        qr.encoded += '0' * bits_to_add
        remaining_bits += bits_to_add

    # add padding bytes
    padding_bytes = ['11101100', '00010001']
    remaining_bytes = remaining_bits // 8
    for i in range(remaining_bytes):
        qr.encoded += padding_bytes[i % 2]


# convert to codewords (bytes)
def make_codewords(qr):
    codewords = []
    binary_data = qr.encoded
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i + 8]
        codewords.append(int(byte, 2))

    # initialize Reed-Solomon codec
    rs_codec = RSCodec(get_data_codeword_capacity(qr.level, qr.ec))

    for codeword in rs_codec.encode(codewords):
        # Convert each byte to 8 bits
        for bit_position in range(7, -1, -1):
            bit = (codeword >> bit_position) & 1
            qr.encoded.append(bit)


def add_finder_patterns(matrix):
    size = len(matrix)
    # top-left finder pattern
    for i in range(4, 12):
        for j in range(4, 12):
            if (i == 4 or i == 10 or j == 4 or j == 10 or
                    (6 <= i <= 8 and 6 <= j <= 8)):
                matrix[i][j] = 1
            else:
                matrix[i][j] = 0

    # top-right finder pattern
    for i in range(4, 12):
        for j in range(size - 12, size - 4):
            if (i == 4 or i == 10 or j == size - 11 or j == size - 5 or
                    (6 <= i <= 8 and size - 9 <= j <= size - 7)):
                matrix[i][j] = 1
            else:
                matrix[i][j] = 0

    # bottom-left finder pattern
    for i in range(size - 12, size - 4):
        for j in range(4, 12):
            if (i == size - 11 or i == size - 5 or j == 4 or j == 10 or
                    (size - 9 <= i <= size - 7 and 6 <= j <= 8)):
                matrix[i][j] = 1
            else:
                matrix[i][j] = 0


def add_alignment_patterns(matrix):
    # for selected versions, there's only one alignment pattern
    size = len(matrix)
    pos = size - 11

    # Draw 5x5 alignment pattern
    for i in range(pos - 2, pos + 3):
        for j in range(pos - 2, pos + 3):
            if i == pos - 2 or i == pos + 2 or j == pos - 2 or j == pos + 2 or (i == pos and j == pos):
                matrix[i][j] = 1
            else:
                matrix[i][j] = 0


def add_timing_patterns(matrix):
    size = len(matrix)
    # timing patterns
    for i in range(12, size - 12):
        matrix[10][i] = 1 if i % 2 == 0 else 0
        matrix[i][10] = 1 if i % 2 == 0 else 0


def add_format_information(matrix, error_correction_level, mask_pattern):
    pass

def mask_fixed_patterns(matrix):
    size = len(matrix)

    for i in range(4, 12):
        for j in range(4, 12):
            matrix[i][j] = 1
            matrix[size - i][j] = 1
            matrix[i][size - j] = 1

    # timing patterns
    for i in range(12, size - 12):
        matrix[10][i] = 1
        matrix[i][10] = 1

    # alignment pattern
    for i in range(size - 13, size - 8):
        for j in range(size - 13, size - 8):
            matrix[i][j] = 1

def add_fixed_patterns(matrix):
    add_finder_patterns(matrix)
    add_alignment_patterns(matrix)
    add_timing_patterns(matrix)
    # Dark module is always present at position (4*version + 9, 8)


def add_data_patterns(matrix, qr):
    size = len(matrix)

    y = size - 5
    direction_up = True


    for x in range(size - 5, 3, -2):
        if x <= 10:
            pass


def make_2d_array(qr):
    # number of modules + padding
    modules = qr.level * 4 + 17 + 4 * 2
    qr_matrix = [[0 for j in range(modules)] for i in range(modules)]
    mask_fixed_patterns(qr_matrix)
    add_data_patterns(qr_matrix, qr)
    add_fixed_patterns(qr_matrix)



def fill_qr(qr):
    qr.ec = get_capacity_value(qr.data_len, qr.level)
    encode_alphanumeric_to_qr_binary(qr)
    add_padding_bits(qr)
    make_codewords(qr)

    # add reminder bits for v2 - v6
    qr.encoded.append('0000000')


def make_qr(text0, text1, text2):
    qr0, qr1, qr2 = QR(text0), QR(text1), QR(text2)
    largest_val = max(qr0.data_len, qr1.data_len, qr2.data_len)
    level = get_capacity_value(largest_val)
    qr0.set_level_and_fill(level)
    qr1.set_level_and_fill(level)
    qr2.set_level_and_fill(level)
