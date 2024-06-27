import qrcode
from io import BytesIO
from django.core.files import File
import json


def generate_qr_code(data, filename):
    """
    Генерирует QR-код на основе данных и сохраняет его в файл.

    :param data: Данные, которые нужно закодировать в QR-коде.
    :param filename: Имя файла для сохранения изображения QR-кода.
    :return: Объект файла с изображением QR-кода.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(data))
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)  # Обязательно верните указатель в начало файла
    return File(buffer, name=f"{filename}.png")
