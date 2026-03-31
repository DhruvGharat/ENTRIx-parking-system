import qrcode

def create_qr(plate_number):
    url = f"http://localhost:5000/session/{plate_number}"
    qr = qrcode.make(url)
    file_path = f"qr_codes/{plate_number}.png"
    qr.save(file_path)
    return file_path
