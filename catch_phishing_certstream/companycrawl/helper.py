import base64
from PIL import Image
from io import BytesIO
import os


def convert_image_to_base64(path: str) -> str:
    # Set the path to your image file
    image_path = path

    try:
        # Check if the file exists and is a valid image file
        if not os.path.exists(image_path):
            raise ValueError("File not found")

        if not Image.open(image_path).format:
            raise ValueError("File is not a valid image")

        # Open the image file using PIL

        with open(image_path, "rb") as image_file:
            image = Image.open(image_file)

            # Convert the image to a base64 string
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Print the base64 string
            return img_str

    except Exception as e:
        print(f"Error: {str(e)}")


def append(path: str, message: str):
    with open(path, "a") as f:
        f.write(message + "\n")


def check_duplicate(path: str, website: str):
    with open(path, "r") as f:
        body = f.read()
        if website in body:
            return True
        return False


def check_domain_is_reachable(domain):
    import socket

    domain = str(domain).strip()
    ip_address = None

    # Get the IP address of the domain
    try:
        ip_address = socket.gethostbyname(domain)
        # print("IP address:", ip_address)
    except socket.gaierror as e:
        pass
        # print("Could not get IP address:", e)

    # Check if the domain is reachable
    if ip_address is not None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        try:
            result = sock.connect_ex((ip_address, 80))
            if result == 0:
                return True

        except socket.error as e:
            print("Socket error:", e)
        sock.close()
    return False
