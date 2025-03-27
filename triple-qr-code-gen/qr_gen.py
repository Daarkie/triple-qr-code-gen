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
        for i in range(2, 7):
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


def make_2d_array(qr):
    def mask_fixed_patterns(matrix):
        size = len(matrix)

        # finder patterns + format info
        for i in range(4, 13):
            for j in range(4, 13):
                matrix[i][j] = 2
                if j < 12:
                    matrix[size - j - 1][i] = 2
                    matrix[i][size - j - 1] = 2

        # timing patterns
        for i in range(12, size - 12):
            matrix[10][i] = 2
            matrix[i][10] = 2

        # alignment pattern
        for i in range(size - 13, size - 8):
            for j in range(size - 13, size - 8):
                matrix[i][j] = 2

    def apply_mask(matrix, mask):
        def should_mask(x, y):
            if mask == 0:
                return (x + y) % 2 == 0
            elif mask == 1:
                return y % 2 == 0
            elif mask == 2:
                return y % 3 == 0
            elif mask == 3:
                return (x + y) % 3 == 0
            elif mask == 4:
                return (x / 3 + y / 2) % 2 == 0
            elif mask == 5:
                return (x * y) % 2 + (x * y) % 3 == 0
            elif mask == 6:
                return ((x * y) % 2 + (x * y) % 3) % 2 == 0
            elif mask == 7:
                return ((x + y) % 2 + (x * y) % 3) % 2 == 0

        size = len(matrix)
        masked_matrix = matrix

        for col in range(4, size - 4):
            for row in range(4, size - 4):
                if should_mask(col, row):
                    masked_matrix[col][row] = 1 - int(masked_matrix[col][row])

        return masked_matrix

    def choose_masking_pattern(matrix):
        def calculate_penalty():
            size = len(masked)

            # rule 1: adjacent same color modules in row/column
            def rule1_penalty():
                penalty = 0
                # Horizontal check
                for row in range(4, size - 4):
                    run = 0
                    current = masked[row][4]
                    for col in range(4, size - 4):
                        if masked[row][col] == current:
                            run += 1
                        else:
                            current = masked[row][col]
                            run = 1
                        if run == 5 and current < 2:
                            penalty += 3
                        elif run > 5 and current < 2:
                            penalty += 1

                # Vertical check
                for col in range(4, size - 4):
                    run = 0
                    current = masked[0][col]
                    for row in range(4, size - 4):
                        if masked[row][col] == current:
                            run += 1
                        else:
                            current = masked[row][col]
                            run = 1
                        if run == 5 and current < 2:
                            penalty += 3
                        elif run > 5 and current < 2:
                            penalty += 1
                return penalty

            # rule 2: 2x2 blocks of same color
            def rule2_penalty():
                penalty = 0
                for x in range(4, size - 5):
                    for y in range(4, size - 5):
                        if (masked[y][x] == masked[y][x + 1] and masked[y][x] == masked[y + 1][x] and masked[y][x] ==
                            masked[y + 1][
                                x + 1]) and masked[y][x] < 2:
                            penalty += 3
                return penalty

            # rule 3: finder-like patterns
            def rule3_penalty():
                penalty = 0
                pattern = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0]
                for x in range(4, size - 5):
                    for y in range(4, size - 5 - len(pattern)):
                        window0 = masked[x][y: y + len(pattern)]
                        window1 = [row[x] for row in masked[y: y + len(pattern)]]
                        if window0 == pattern or window0 == [not i for i in pattern]:
                            penalty += 40
                        if window1 == pattern or window1 == [not i for i in pattern]:
                            penalty += 40
                return penalty

            # rule 4: dark/light module balance
            def rule4_penalty():
                dark = sum(row.count(1) for row in masked)
                total = (size - 8) ** 2
                ratio = (dark / total) * 100
                nearest_multiple = 5 * round(ratio / 5)
                penalty = int(10 * abs(nearest_multiple - 50) / 5)
                return penalty

            final_penalty = 0

            final_penalty += rule1_penalty()

            final_penalty += rule2_penalty()

            final_penalty += rule3_penalty()

            final_penalty += rule4_penalty()

            return final_penalty

        min_score = float('inf')
        best_mask = 0

        for m in range(8):
            masked = apply_mask(matrix, m)
            mask_fixed_patterns(masked)
            score = calculate_penalty()

            if score < min_score:
                min_score = score
                best_mask = m

        return best_mask

    def add_fixed_patterns(matrix, ec):
        size = len(matrix)

        def add_finder_patterns():
            # top-left finder pattern
            for i in range(4, 12):
                for j in range(4, 12):
                    if i == 11 or j == 11:
                        matrix[i][j] = 0
                    elif (i == 4 or i == 10 or j == 4 or j == 10 or
                            (6 <= i <= 8 and 6 <= j <= 8)):
                        matrix[i][j] = 1
                    else:
                        matrix[i][j] = 0

            # top-right finder pattern
            for i in range(4, 12):
                for j in range(size - 12, size - 4):
                    if i == 11 or j == size - 12:
                        matrix[i][j] = 0
                    elif (i == 4 or i == 10 or j == size - 11 or j == size - 5 or
                            (6 <= i <= 8 and size - 9 <= j <= size - 7)):
                        matrix[i][j] = 1
                    else:
                        matrix[i][j] = 0

            # bottom-left finder pattern
            for i in range(size - 12, size - 4):
                for j in range(4, 12):
                    if i == size - 12 or j == 11:
                        matrix[i][j] = 0
                    elif (i == size - 11 or i == size - 5 or j == 4 or j == 10 or
                            (size - 9 <= i <= size - 7 and 6 <= j <= 8)):
                        matrix[i][j] = 1
                    else:
                        matrix[i][j] = 0

        def add_alignment_patterns():
            # for selected versions, there's only one alignment pattern
            pos = size - 11

            # Draw 5x5 alignment pattern
            for i in range(pos - 2, pos + 3):
                for j in range(pos - 2, pos + 3):
                    if i == pos - 2 or i == pos + 2 or j == pos - 2 or j == pos + 2 or (i == pos and j == pos):
                        matrix[i][j] = 1
                    else:
                        matrix[i][j] = 0

        def add_timing_patterns():
            # timing patterns
            for i in range(12, size - 12):
                matrix[10][i] = 1 if i % 2 == 0 else 0
                matrix[i][10] = 1 if i % 2 == 0 else 0

        def place_format_information():

            def get_format_information():
                # error correction bits
                ec_levels = {"L": "01", "M": "00", "Q": "11", "H": "10"}
                format_bits = ec_levels[ec]

                # add mask pattern (3-bit binary)
                format_bits += format(mask_num, '03b')

                # BCH Error Correction (XOR with 101010000010010)
                generator = 0b101010000010010
                format_num = int(format_bits, 2) << 10  # append 10 zero bits for BCH

                for z in range(14, 9, -1):  # apply BCH encoding
                    if (format_num >> z) & 1:
                        format_num ^= generator << (z - 10)

                # final 15-bit format string
                return format_bits + format(format_num, '010b')

            format_info = list(get_format_information())
            for i in range(4, 13):
                if i < 10:
                    matrix[12][i] = matrix[size - i - 1][12] = 0 if format_info.pop(0) == "0" else 1
                else:
                    matrix[12][i + 1] = matrix[size - i - 1][12] = 0 if format_info.pop(0) == "0" else 1

            for i in range(4, 12):
                if i < 10:
                    matrix[i][12] = matrix[12][size - i] = 0 if format_info.pop(0) == "0" else 1
                else:
                    matrix[i + 1][12] = matrix[12][size - i] = 0 if format_info.pop(0) == "0" else 1

            matrix[12][size - 12] = 1

        add_finder_patterns()
        add_alignment_patterns()
        add_timing_patterns()
        place_format_information()
        print(matrix)

    def add_data_patterns(matrix):
        size = len(matrix)

        def input_data_in_matrix(x, is_upwards):
            if is_upwards:
                start = size - 5
                end = 3
            else:
                start = 4
                end = size - 4
            # check each row
            for y in range(start, end):
                for offset in [0, 1]:
                    if len(data) == 0:
                        break
                    if matrix[x - offset][y] == 0:
                        matrix[x - offset][y] = 0 if data.pop(0) == "0" else 1

        size = len(matrix)
        data = list(qr.encoded)

        # go through the pairs or cols
        for col in range(size - 5, 3, -2):
            input_data_in_matrix(col, col % 4 == 0)

    # number of modules + padding
    modules = qr.level * 4 + 17 + 4 * 2
    qr_matrix = [[0 for j in range(modules)] for i in range(modules)]
    mask_fixed_patterns(qr_matrix)
    add_data_patterns(qr_matrix)
    mask_num = choose_masking_pattern(qr_matrix)
    qr_matrix = apply_mask(qr_matrix, mask_num)
    add_fixed_patterns(qr_matrix, qr.ec)
    return qr_matrix


def fill_qr(qr):
    def get_data_codeword_capacity():
        # capacity table for versions 2-6
        capacity_table = {
            2: {'L': 34, 'M': 28, 'Q': 22, 'H': 16},
            3: {'L': 55, 'M': 44, 'Q': 34, 'H': 26},
            4: {'L': 80, 'M': 64, 'Q': 48, 'H': 36},
            5: {'L': 108, 'M': 86, 'Q': 62, 'H': 46},
            6: {'L': 136, 'M': 108, 'Q': 76, 'H': 60}
        }

        return capacity_table[qr.level][qr.ec]

    # encoding with qr bits
    def encode_alphanumeric_to_qr_binary():
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

    def add_padding_bits():
        # get room
        total_capacity_bits = get_data_codeword_capacity() * 8

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
    def make_codewords():
        codewords = []
        binary_data = qr.encoded
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i + 8]
            codewords.append(int(byte, 2))

        # initialize Reed-Solomon codec
        rs_codec = RSCodec(get_data_codeword_capacity())

        for codeword in rs_codec.encode(codewords):
            # Convert each byte to 8 bits
            for bit_position in range(7, -1, -1):
                bit = (codeword >> bit_position) & 1
                qr.encoded += str(bit)

    qr.ec = get_capacity_value(qr.data_len, qr.level)
    encode_alphanumeric_to_qr_binary()
    add_padding_bits()
    make_codewords()

    # add reminder bits for v2 - v6
    qr.encoded += "0000000"
