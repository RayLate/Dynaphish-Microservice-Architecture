import json
import os

import requests
from helper import convert_image_to_base64, append, check_duplicate


class CaptchaIdentifier:
    def __init__(self):
        self.DOCKER_HOSTNAME = "192.168.59.165"
        self.PORT = "5000"
        self.URL = f"http://{self.DOCKER_HOSTNAME}:{self.PORT}"

    def reset_database(self):
        res = requests.post(f"{self.URL}/database/reset")
        print(f"status code <{res.status_code}>")
        if res.status_code == 200:
            print("databased reset successfully")
        else:
            print("something went wrong")

    def make_prediction(self, screenshot: str):
        # screenshot in base 64
        payload = {"screenshot": screenshot}
        headers = {"Content-Type": "application/json; charset=utf-8"}
        # print(f'payload: {json.dumps(payload)}')
        res = requests.post(f"{self.URL}/predict", json=payload, headers=headers)
        print(f"status code <{res.status_code}>")
        print(res.json())
        if res.status_code == 200:
            return res.json()


identifier = CaptchaIdentifier()
# identifier.reset_database()

# Set the path to your image file
image_path = r"E:\screenshots_rf\2023-03-05\canteo.xyz\shot.png"

base64_img = convert_image_to_base64(image_path)
if base64_img:
    print(base64_img)
else:
    print("something went wrong")

# result = identifier.make_prediction(base64_img)
# print(result.detected)
# print(result.results)

folders = os.listdir(r"E:\screenshots_rf")
for folder in folders:
    print(f"checking through {folder}")
    websites = os.listdir(os.path.join(r"E:\screenshots_rf", folder))
    print(len(websites), "websites")
    for website in websites:
        if check_duplicate("result.txt", website):
            continue
        image_path = os.path.join(r"E:\screenshots_rf", folder, website, "shot.png")
        print(image_path)
        try:
            base64_img = convert_image_to_base64(image_path)
            result = identifier.make_prediction(base64_img)
            detected = result.get("detected", False)
            results = result.get("results", [])
            message = f"{website};{detected};{results}"
            append("result.txt", message)
            if detected:
                print(website, "contains Captcha")
        except Exception as e:
            print(e)
            continue
