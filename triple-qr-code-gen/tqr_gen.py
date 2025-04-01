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
    qr_matrix1, qr_matrix2 = None, None
    version0 = qr_matrix0.get_version()
    error_correction = [QrCode.Ecc.LOW, QrCode.Ecc.MEDIUM, QrCode.Ecc.QUARTILE, QrCode.Ecc.HIGH]
    version2 = float("inf")
    level = 4
    while version2 > version0:
        level -= 1
        qr_matrix2 = QrCode.encode_segments(QrSegment.make_segments(text_list[2]), error_correction[level],
                                                      minversion=version0)
        version2 = qr_matrix2.get_version()
    version1 = version2 + 1
    while version1 > version0:
        level -= 1
        qr_matrix1 = QrCode.encode_segments(QrSegment.make_segments(text_list[1]), error_correction[level],
                                                      minversion=version0)
        version1 = qr_matrix1.get_version()
    return combine_qrs(qr_matrix0, qr_matrix1, qr_matrix2)
