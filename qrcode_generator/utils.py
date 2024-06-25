import qrcode
import json
from io import BytesIO
from django.core.files import File


def generate_qr_code(data, filename_prefix):
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
    img.save(buffer)
    filename = f"{filename_prefix}_qr.png"
    filebuffer = File(buffer, name=filename)

    return filebuffer, filename
