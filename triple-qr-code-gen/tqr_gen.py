from qr_gen import QR, get_capacity_value, make_2d_array

def make_tqr(text0, text1, text2):
    def combine_qrs():
        matrix0, matrix1, matrix2 = qr_matrix0, qr_matrix1 * 2, qr_matrix2 * 4
        return matrix0 + matrix1 + matrix2

    qr0, qr1, qr2 = QR(text0), QR(text1), QR(text2)
    largest_val = max(qr0.data_len, qr1.data_len, qr2.data_len)
    level = get_capacity_value(largest_val)
    qr0.set_level_and_fill(level)
    qr1.set_level_and_fill(level)
    qr2.set_level_and_fill(level)
    qr_matrix0, qr_matrix1, qr_matrix2 = make_2d_array(qr0), make_2d_array(qr1), make_2d_array(qr2)
    return combine_qrs()