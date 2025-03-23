from reedsolo import RSCodec


class QR:
    def __init__(self, text_data):
        self.text_data = text_data
        self.data_len = len(text_data)
        self.level = 0
        self.ec = 'L'
        self.encoded = "0010"

    def set_level(self, level):
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
        raise ValueError(f"Size of data '{data_size}' not supported")
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


def combine(qr0, qr1):
    pass


def fill_qr(qr):
    qr.ec = get_capacity_value(qr.data_len, qr.level)
    encode_alphanumeric_to_qr_binary(qr)
    add_padding_bits(qr)
    make_codewords(qr)

    # add reminder bits for v2 - v6
    qr.encoded.append('0000000')


def make_qr(text0, text1, text2):
    qr0 = QR(text0)
    qr1 = QR(text1)
    qr2 = QR(text2)
    largest_val = max(qr0.data_len, qr1.data_len, qr2.data_len)
    level = get_capacity_value(largest_val)
    qr0.set_level(level)
    qr1.set_level(level)
    qr2.set_level(level)
