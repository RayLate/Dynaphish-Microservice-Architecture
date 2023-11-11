from xdriver.xutils.PhishIntentionWrapper import PhishIntentionWrapper
from datetime import datetime
import warnings
from db.db import *
from bs4 import BeautifulSoup
import re
import time
from flask import Flask, jsonify, render_template, request
from util.util import *

warnings.filterwarnings("ignore")


app = Flask(__name__)
app.name = "HAS_LOGO_SERVER"
logger = MyLogger(f"/field_study_logo2brand/LOG/{app.name}.runtime.log.txt")
counter = 0

phishintention_config_path = "/field_study_logo2brand/configs.yaml"
PhishIntention = PhishIntentionWrapper(
    config_path=phishintention_config_path, reload_targetlist=False
)


def has_logo_test(screenshot_path):
    # Has a logo or not?
    global counter
    global PhishIntention
    if counter == 100:
        # reload targetlist every 100 domain
        logger.log("reloading target list")
        PhishIntention = PhishIntentionWrapper(
            config_path=phishintention_config_path, reload_targetlist=False
        )
        counter = 0
    else:
        counter += 1
    has_logo, in_target_list = PhishIntention.has_logo(screenshot_path=screenshot_path)
    print("Has logo? {} Is in targetlist? {}".format(has_logo, in_target_list))
    return has_logo, in_target_list


def forbidden_words_test(domain, title):
    # Function to check for forbidden words in a URL
    try:
        print("Domain:", domain, "Title:", title)
        if not title:
            return True
        if domain in title.lower() or re.search(
            OnlineForbiddenWord.WEBHOSTING_TEXT, title, re.IGNORECASE
        ):
            print("Hit forbidden words")
            return True
        print("No forbidden words")
        return False
    except Exception as e:
        print(e)
        return True


def get_info_for_domain(domain, screenshot_path):
    try:
        url = f"https://{domain}"
        response = requests.get(url)
        response.raise_for_status()

        # Extracting information
        html_content = response.content
        soup = BeautifulSoup(html_content, "html.parser")
        url = response.url
        domain = response.url.split("/")[2]
        html_title = soup.title.string if soup.title else ""
        result = {
            "url": url,
            "domain": domain,
            "html_title": html_title,
            "has_forbidden_words": forbidden_words_test(domain, html_title),
        }

        if not result.get("has_forbidden_words"):
            has_logo, brand_inside_targetlist = has_logo_test(screenshot_path)
            result["has_logo"] = has_logo
            result["brand_inside_targetlist"] = brand_inside_targetlist

        return {**result, "success": True}

    except Exception as e:
        return {"error": str(e), "success": False}


def process_logo(domain):
    template = get_sample_data(domain)
    folder = os.path.join("/data/has-logo-queue", domain)
    screenshot_path = os.path.join(folder, "shot.png")
    if folder and os.path.exists(folder) and os.path.join(folder, "shot.png"):
        s = time.time()
        result = get_info_for_domain(domain, screenshot_path)
        runtime = time.time() - s
        result["has_logo_runtime"] = int(runtime * 1000) / 1000
        result["modified"] = int(datetime.now().timestamp())
        if result.get("success"):
            data = get_one(folder)
            del result["success"]
            if data:
                del data["_id"]
                result = {**data, **result}
                update_one(result)
            else:
                result = {**template, **result}
                add_one(result)

            # based on the result do some
            if result.get("has_logo"):
                if result.get("brand_inside_targetlist"):
                    # send folder name to Phishintention API Server
                    cut_folder(folder, "/data/phishintention-queue")
                    requests.post(
                        "http://192.168.1.5:8000/phishintention-queue/{}".format(domain)
                    )
                else:
                    # send folder name to KE API server
                    try:
                        print("Knowledge Expanding")
                        cut_folder(folder, "/data/knowledge-expansion-queue")
                        requests.post("http://192.168.1.5:8000/knowledge-expansion-queue/{}".format(domain))
                    except Exception as e:
                        print(str(e))
            else:
                cut_folder(folder, "/data/finished")
        else:
            cut_folder(folder, "/data/failed")
        return result
    else:
        delete_folder(folder)
        return {}


@app.route("/")
def index():
    container_ip = get_container_ip()
    print(f"The IP address of this container is: {container_ip}")
    return f"Server is running on {container_ip}"


@app.route("/has-logo-queue/<string:folder>", methods=["GET", "POST"])
def get(folder):
    if request.method == "GET":
        s = time.time()
        try:
            r = process_logo(folder)
        except Exception as e:
            r = {"status": "failed", "folder_path": folder, "error": str(e)}
        e = time.time()
        logger.log(f"{folder};{int((e-s)/1000)/1000}")
        return render_template("table.html", data=r)

    elif request.method == "POST":
        s = time.time()
        try:
            r = process_logo(folder)
        except Exception as e:
            r = {"status": "failed", "folder_path": folder, "error": str(e)}
        e = time.time()
        logger.log(r)
        logger.log(f"{folder};{int((e-s)*1000)/1000}")
        return jsonify(r)


# Testing
# print(get_info_for_domain("accounts.g.cdcde.com","./datasets/accounts.g.cdcde.com/shot.png"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
