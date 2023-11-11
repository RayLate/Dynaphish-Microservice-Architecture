from xdriver.xutils.PhishIntentionWrapper import PhishIntentionWrapper
import time
from xdriver.XDriver import XDriver
from db.db import *
from util.util import *
from db.db import *
from flask import Flask, request, jsonify
from datetime import datetime
import cv2

TIMEOUT = 60
app = Flask(__name__)
app.name = "PHISHINTENTION_SERVER"
logger = MyLogger(f"/field_study_logo2brand/LOG/{app.name}.runtime.log.txt")


def run_phishintention(folder):
    global PhishIntention
    global counter
    global phishintention_config_path
    counter += 1
    if counter == 100:
        PhishIntention.reset_model(phishintention_config_path)
        counter = 0
    folder_path, screenshot_path = check_folder(folder, "phishintention-queue")
    if not folder_path:
        delete_folder(folder_path)
        delete_one(folder)
        return {
            "status": "failed",
            "folder_path": folder,
            "error": "Screenshot not found in folder",
        }
    data = get_one(folder)
    if not data:
        cut_folder(folder_path, "/data/failed/")
        return {
            "status": "failed",
            "folder_path": folder,
            "error": "folder not found in database",
        }

    URL = data.get("url")
    s = time.time()
    kill_chrome()
    ph_driver = XDriver.boot(chrome=True)
    ph_driver.set_page_load_timeout(TIMEOUT)
    ph_driver.set_script_timeout(TIMEOUT)
    (
        phish_category,
        phish_target,
        plotvis,
        siamese_conf,
        dynamic,
        time_breakdown,
        pred_boxes,
        pred_classes,
    ) = PhishIntention.test_orig_phishintention(URL, screenshot_path, ph_driver)
    ph_driver.quit()
    e = time.time()
    phish_runtime = e - s
    if plotvis is not None:
        cv2.imwrite(
            os.path.join(folder_path, "predict_dyna{}.png".format("phishintention")),
            plotvis,
        )
    # update database
    del data["_id"]
    data["phish_prediction"] = phish_category
    data["target_prediction"] = phish_target or ""
    data["phishintention_runtime"] = int(float(phish_runtime) * 1000) / 1000
    data["modified"] = int(datetime.now().timestamp())
    update_one(data)
    cut_folder(folder_path, "/data/finished/")
    return {"status": "success", "folder_path": folder, "result": data}


# config phishing intention model
phishintention_config_path = "/field_study_logo2brand/configs.yaml"
PhishIntention = PhishIntentionWrapper(config_path=phishintention_config_path)
counter = 0


@app.route("/")
def index():
    container_ip = get_container_ip()
    print(f"The IP address of this container is: {container_ip}")
    return f"Server is running on {container_ip}"


@app.route("/phishintention-queue/<string:folder>", methods=["POST"])
def ke(folder):
    if request.method == "POST":
        s = time.time()
        try:
            r = run_phishintention(folder)
        except Exception as e:
            r = {"status": "failed", "folder_path": folder, "error": str(e)}
            cut_folder(f'/data/phishintention-queue/{folder}', "/data/failed/")
        e = time.time()
        logger.log("-" * 50)
        logger.log(f"{folder};{int((e-s)*1000)/1000}")
        logger.log(r)
        logger.log("-" * 50)
        return jsonify(r)

    return "Request method not found, Only POST is avilable", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
