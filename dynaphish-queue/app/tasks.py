import time
import requests


def send_request_to_server(port, queue, folder):
    s = time.time()
    try:
        url = f"http://192.168.1.5:{port}/{queue}/{folder}"
        res = requests.post(url, timeout=None)
        print(res.text)
    except Exception as e:
        print(str(e))

    e= time.time()
    print(f"time taken: {e-s} ")
