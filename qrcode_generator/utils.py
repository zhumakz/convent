import qrcode
import json
import qrcode
from io import BytesIO
from django.core.files import File
import json


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
    img.save(buffer, format="PNG")
    buffer.seek(0)
    filebuffer = File(buffer, name=f"{filename_prefix}_qr.png")

    return filebuffer
