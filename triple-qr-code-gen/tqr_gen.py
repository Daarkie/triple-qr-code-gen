import numpy as np
import qrcodegen
from qrcodegen import *


def make_tqr(text0, text1, text2):
    def combine_qrs(matrix0, matrix1, matrix2):
        matrix0, matrix1, matrix2 = matrix0, matrix1 * 2, matrix2 * 4
        return matrix0 + matrix1 + matrix2

    text_list = [text0, text1, text2]
    list.sort(text_list, key=len)
    qr_matrix0 = qrcodegen.QrCode.encode_text(text_list[0], QrCode.Ecc.LOW)
    qr_matrix1 = qrcodegen.QrCode.encode_segments(QrSegment.make_segments(text_list[1]), QrCode.Ecc.LOW,
                                                  minversion=qr_matrix0.get_version())
    qr_matrix2 = qrcodegen.QrCode.encode_segments(QrSegment.make_segments(text_list[2]), QrCode.Ecc.LOW,
                                                  minversion=qr_matrix0.get_version())
    return combine_qrs(qr_matrix0, qr_matrix1, qr_matrix2)
