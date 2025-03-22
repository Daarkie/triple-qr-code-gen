class QR:
    def __init__(self, text_data):
        self.text_data = text_data
        self.data_len = len(text_data)
        self.level = 0
        self.quality = 'L'

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


# Convert to codewords (bytes)
def get_codewords(binary_data):
    codewords = []
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i + 8]
        codewords.append(int(byte, 2))

    return codewords


def get_data_codeword_capacity(version, error_correction):
    # Capacity table for versions 1-9
    # Format: (version, L, M, Q, H)
    capacity_table = {
        1: {'L': 19, 'M': 16, 'Q': 13, 'H': 9},
        2: {'L': 34, 'M': 28, 'Q': 22, 'H': 16},
        3: {'L': 55, 'M': 44, 'Q': 34, 'H': 26},
        4: {'L': 80, 'M': 64, 'Q': 48, 'H': 36},
        5: {'L': 108, 'M': 86, 'Q': 62, 'H': 46},
        6: {'L': 136, 'M': 108, 'Q': 76, 'H': 60},
        7: {'L': 156, 'M': 124, 'Q': 88, 'H': 66},
        8: {'L': 194, 'M': 154, 'Q': 110, 'H': 86},
        9: {'L': 232, 'M': 182, 'Q': 132, 'H': 100}
    }

    return capacity_table[version][error_correction]


# get capacity value
def get_capacity_value(data_size, level = 0):
    capacity_table = {
        1: {'L': 25, 'M': 20, 'Q': 16, 'H': 10},
        2: {'L': 47, 'M': 38, 'Q': 29, 'H': 20},
        3: {'L': 77, 'M': 61, 'Q': 47, 'H': 35},
        4: {'L': 114, 'M': 90, 'Q': 67, 'H': 50},
        5: {'L': 154, 'M': 122, 'Q': 87, 'H': 64},
        6: {'L': 195, 'M': 154, 'Q': 108, 'H': 84},
        7: {'L': 224, 'M': 178, 'Q': 125, 'H': 93},
        8: {'L': 279, 'M': 221, 'Q': 157, 'H': 122},
        9: {'L': 335, 'M': 262, 'Q': 189, 'H': 143}
    }
    if level == 0:
        for i in range(1, 10):
            if capacity_table[i]['L'] >= data_size:
                return i
    else:
        if capacity_table[level]['H'] >= data_size:
            return 'H'
        if capacity_table[level]['Q'] >= data_size:
            return 'Q'
        if capacity_table[level]['M'] >= data_size:
            return 'M'
        return 'L'

# encoding with qr bits
def encode_alphanumeric_to_qr_binary(text):
    text = text.upper()

    # indicate alphanumeric
    result = "0010"

    # character count indicator (fill to 9 since we are only using versions 1-9)
    char_count = bin(len(text))[2:].zfill(9)
    result += char_count

    # processing characters
    for i in range(0, len(text), 2):
        if i + 1 < len(text):
            # process a pair
            val1 = get_alphanumeric_value(text[i])
            val2 = get_alphanumeric_value(text[i + 1])
            value = val1 * 45 + val2
            # convert to 11-bit binary
            binary = bin(value)[2:].zfill(11)
            result += binary
        else:
            # process a single character (last one if odd length)
            val = get_alphanumeric_value(text[i])
            # 6-bit binary
            binary = bin(val)[2:].zfill(6)
            result += binary

    return result


def add_padding_bits(binary_data, total_capacity_bits):
    # Add terminator if there's room
    remaining_bits = total_capacity_bits - len(binary_data)
    if remaining_bits >= 4:
        binary_data += '0000'
        remaining_bits -= 4
    elif remaining_bits > 0:
        binary_data += '0' * remaining_bits
        remaining_bits = 0

    # Make the length a multiple of 8 (byte alignment)
    bits_to_add = remaining_bits % 8
    if bits_to_add > 0:
        binary_data += '0' * bits_to_add
        remaining_bits += bits_to_add

    # Add padding bytes
    padding_bytes = ['11101100', '00010001']
    remaining_bytes = remaining_bits // 8
    for i in range(remaining_bytes):
        binary_data += padding_bytes[i % 2]

    return binary_data


def combine(qr0, qr1, qr2):
    pass

def make_qr(text0, text1, text2):
    qr0 = QR(text0)
    qr1 = QR(text1)
    qr2 = QR(text2)
    largest_val = max(qr0.data_len, qr1.data_len, qr2.data_len)
    qr0.level, qr1.level, qr2.level = get_capacity_value(largest_val)
    qr0.quality = get_capacity_value(qr0.data_len, qr0.level)
    qr1.quality = get_capacity_value(qr1.data_len, qr1.level)
    qr2.quality = get_capacity_value(qr2.data_len, qr2.level)