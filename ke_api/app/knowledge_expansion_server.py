import tldextract
import yaml
from phishintention.src.OCR_siamese_utils.inference import pred_siamese_OCR
import pickle
from xdriver.xutils.PhishIntentionWrapper import PhishIntentionWrapper
from knowledge_expansion.brand_knowledge_online import BrandKnowledgeConstruction
from knowledge_expansion.utils import *
import os
import numpy as np
import time
from datetime import datetime
import CONFIGS as configs
from xdriver.XDriver import XDriver
from db.db import *
from flask import Flask, request, jsonify
from util.util import *

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = configs.google_cloud_json_credentials

app = Flask(__name__)
app.name = "KNOWLEDGE EXPANSION SERVER"


logger = MyLogger(f"/field_study_logo2brand/LOG/{app.name}.runtime.log.txt")

def domain_already_in_targetlist(domain_map_path, new_brand):
    with open(domain_map_path, "rb") as handle:
        domain_map = pickle.load(handle)
    existing_brands = domain_map.keys()

    if new_brand in existing_brands:
        return domain_map, True
    return domain_map, False


def expand_targetlist(config_path, new_brand, new_domains, new_logos):
    s = time.time()
    # PhishIntention config file
    global PhishIntention
    with open(config_path) as file:
        configs = yaml.load(file, Loader=yaml.FullLoader)

    # expand domain map
    domain_map, domain_in_target = domain_already_in_targetlist(
        domain_map_path=configs["SIAMESE_MODEL"]["DOMAIN_MAP_PATH"], new_brand=new_brand
    )
    if not domain_in_target:  # if this domain is not in targetlist ==> add it
        domain_map[new_brand] = list(set(new_domains))
        with open(configs["SIAMESE_MODEL"]["DOMAIN_MAP_PATH"], "wb") as handle:
            pickle.dump(domain_map, handle)

    # expand logo list
    valid_logo = [a for a in new_logos if a is not None]
    if len(valid_logo) == 0:  # no valid logo
        e = time.time()
        return

    targetlist_path = configs["SIAMESE_MODEL"]["TARGETLIST_PATH"].split(".zip")[0]
    new_logo_save_folder = os.path.join(targetlist_path, new_brand)
    os.makedirs(new_logo_save_folder, exist_ok=True)

    exist_num_files = len(os.listdir(new_logo_save_folder))
    new_logo_save_paths = []
    for ct, logo in enumerate(valid_logo):
        this_logo_save_path = os.path.join(
            new_logo_save_folder, "{}.png".format(exist_num_files + ct)
        )
        if os.path.exists(this_logo_save_path):
            this_logo_save_path = os.path.join(
                new_logo_save_folder, "{}_expand.png".format(exist_num_files + ct)
            )
        logo.save(this_logo_save_path)
        new_logo_save_paths.append(this_logo_save_path)

    # expand cached logo features list
    prev_logo_feats = np.load(
        os.path.join(
            os.path.dirname(configs["SIAMESE_MODEL"]["TARGETLIST_PATH"]),
            "LOGO_FEATS.npy",
        )
    )
    prev_file_name_list = np.load(
        os.path.join(
            os.path.dirname(configs["SIAMESE_MODEL"]["TARGETLIST_PATH"]),
            "LOGO_FILES.npy",
        )
    )
    prev_logo_feats = prev_logo_feats.tolist()
    prev_file_name_list = prev_file_name_list.tolist()

    new_logo_feats = []
    new_file_name_list = []

    for logo_path in new_logo_save_paths:
        new_logo_feats.append(
            pred_siamese_OCR(
                img=logo_path,
                model=PhishIntention.SIAMESE_MODEL,
                ocr_model=PhishIntention.OCR_MODEL,
                grayscale=False,
            )
        )
        new_file_name_list.append(str(logo_path))

    agg_logo_feats = prev_logo_feats + new_logo_feats
    agg_file_name_list = prev_file_name_list + new_file_name_list
    np.save(
        os.path.join(
            os.path.dirname(configs["SIAMESE_MODEL"]["TARGETLIST_PATH"]), "LOGO_FEATS"
        ),
        np.asarray(agg_logo_feats),
    )
    np.save(
        os.path.join(
            os.path.dirname(configs["SIAMESE_MODEL"]["TARGETLIST_PATH"]), "LOGO_FILES"
        ),
        np.asarray(agg_file_name_list),
    )

    # update reference list
    PhishIntention.LOGO_FEATS = np.asarray(agg_logo_feats)
    PhishIntention.LOGO_FILES = np.asarray(agg_file_name_list)


def start_xdriver(sleep=2):
    kill_chrome()
    timeout = 60
    XDriver.set_headless()
    kb_driver = XDriver.boot(chrome=True)
    time.sleep(sleep)
    kb_driver.set_page_load_timeout(timeout)
    kb_driver.set_script_timeout(timeout)
    return kb_driver


def knowledge_expansion(
    screenshot_path,
    query_domain,
    query_tld,
    knowledge_expansion_branch="logo2brand",
):
    global KnowledgeExpansion
    global phishintention_config_path
    global counter
    global kb_driver

    # try kb_driver
    try:
        kb_driver.get("https://www.google.com", allow_redirections=False)
    except:
        i = 2
        while True:
            try:
                kb_driver= start_xdriver(i)
                break
            except:
                i += 1
                time.sleep(1)
        
    (
        _,
        new_brand_domains,
        new_brand_name,
        new_brand_logos,
        knowledge_discovery_runtime,
        comment,
    ) = KnowledgeExpansion.runit_simplified(
        driver=kb_driver,
        shot_path=screenshot_path,
        query_domain=query_domain,
        query_tld=query_tld,
        type=knowledge_expansion_branch,
    )


    """If the found knowledge is not inside targetlist -> expand targetlist"""
    expand_targetlist_runtime = 0
    if len(new_brand_domains) and np.sum([x is not None for x in new_brand_logos]) > 0:
        counter += 1
        if counter == 100:
            logger.log("resetting phishIntention Model")
            PhishIntention.reset_model(config_path=phishintention_config_path)
            counter = 0
        expand_targetlist_start = time.time()
        expand_targetlist(
            config_path=phishintention_config_path,
            new_brand=new_brand_name,
            new_domains=new_brand_domains,
            new_logos=new_brand_logos,
        )
        expand_targetlist_end = time.time()
        expand_targetlist_runtime = expand_targetlist_end - expand_targetlist_start
    return (
        new_brand_domains,
        new_brand_name,
        new_brand_logos,
        knowledge_discovery_runtime,
        comment,
        expand_targetlist_runtime,
    )


def run_knowledge_expansion(folder):
    folder_path, screenshot_path = check_folder(folder, "knowledge-expansion-queue")
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
    query_domain = tldextract.extract(URL).domain
    query_tld = tldextract.extract(URL).suffix
    (
        _,
        _,
        _,
        knowledge_discovery_runtime,
        comment,
        expand_targetlist_runtime,
    ) = knowledge_expansion(screenshot_path, query_domain, query_tld)
    del data["_id"]
    data["knowledge_discovery_branch"] = comment
    data["kd_runtime"] = int(float(knowledge_discovery_runtime) * 1000) / 1000
    if "success" in comment:
        data["found_knowledge"] = True
    data["expand_targetlist_runtime"] = expand_targetlist_runtime or 0
    data["modified"] = int(datetime.now().timestamp())
    update_one(data)
    cut_folder(folder_path, "/data/phishintention-queue/")
    requests.post("http://192.168.1.5:8000/phishintention-queue/{}".format(folder))
    return {"status": "success", "folder_path": folder, "result": data}


# config phishing intention model
phishintention_config_path = "/field_study_logo2brand/configs.yaml"
PhishIntention = PhishIntentionWrapper(phishintention_config_path)
counter = 0
# more configuration
API_KEY, SEARCH_ENGINE_ID = [
    x.strip() for x in open(configs.google_search_credentials).readlines()
]
KnowledgeExpansion = BrandKnowledgeConstruction(
    API_KEY, SEARCH_ENGINE_ID, PhishIntention
)
kb_driver=None

# Start kb_driver
i = 2
while True:
    try:
        kb_driver= start_xdriver(i)
        break
    except:
        i += 1
        time.sleep(1)


@app.route("/")
def index():
    container_ip = get_container_ip()
    print(f"The IP address of this container is: {container_ip}")
    return f"Server is running on {container_ip}"


@app.route("/knowledge-expansion-queue/<string:folder>", methods=["POST"])
def ke(folder):
    if request.method == "POST":
        s = time.time()
        try:
            r = run_knowledge_expansion(folder)
        except Exception as e:
            r = {"status": "failed", "folder_path": folder, "error": str(e)}
        e = time.time()
        logger.log("-" * 50)
        logger.log(f"{folder};{int((e-s)*1000)/1000}")
        logger.log(r)
        logger.log("-" * 50)
        return jsonify(r)

    return "Request method not found, Only POST is avilable", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
