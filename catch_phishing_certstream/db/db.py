
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from bson.objectid import ObjectId
import os

load_dotenv()
COLLECTION = os.getenv('COLLECTION')
DATABASE = os.getenv('DATABASE')
API_KEY = os.getenv('API_KEY')
URL = os.getenv('API_KEY')
ENABLE_DB = True
if not API_KEY:
    print("missing .env file") 
    print("create an .env file and update your mongodb endpoint, api key, database name and collection") 
    i ='a'
    while i!= 'Y':
        i = input('type Y to continue without DB information')
        if i == 'Y':
            ENABLE_DB = False

def check_enable_db():
    return ENABLE_DB

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

def get_all(filter,kwarg):
    url = f"{URL}/endpoint/data/v1/action/find"
    payload = json.dumps({
        "collection": COLLECTION,
        "database": DATABASE,
        "dataSource": "AtlasCluster",
        'filter': filter or {},
        **kwarg
    },cls=CustomJSONEncoder)
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': API_KEY,
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if 200 <= response.status_code < 300:
        print(
            f'status code : {response.status_code} | document length : {len(response.json().get("documents"))}')
        return response.json().get('documents')
    print(f'status code : {response.status_code} | message : {response.text}')
    return None

def update_all(filter={}, update={}):
    url = f"{URL}/endpoint/data/v1/action/updateMany"
    payload = json.dumps({
        "collection": COLLECTION,
        "database": DATABASE,
        "dataSource": "AtlasCluster",
        'filter': filter,
        'update': update
    })
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': API_KEY,
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if 200 <= response.status_code < 300:
        print(
            f'status code : {response.status_code} | message : {response.text}')
    else:
        print(
            f'status code : {response.status_code} | message : {response.text}')

    return response.status_code, response.text


def get_one(folder):
    url = f"{URL}/endpoint/data/v1/action/findOne"
    payload = json.dumps({
        "collection": COLLECTION,
        "database": DATABASE,
        "dataSource": "AtlasCluster",
        'filter': {"folder": folder}
    })
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': API_KEY,
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if 200 <= response.status_code < 300:
        print(
            f'status code : {response.status_code} | document found : {response.json().get("document")}')
        return response.json().get('document')
    print(f'status code : {response.status_code} | message : {response.text}')
    return None

def delete_one(folder):
    url = f"{URL}/endpoint/data/v1/action/deleteOne"
    payload = json.dumps({
        "collection": COLLECTION,
        "database": DATABASE,
        "dataSource": "AtlasCluster",
        'filter': {
            "folder":folder
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': API_KEY,
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    if 200 <= response.status_code < 300:
        print(
            f'status code : {response.status_code} | deletedCount : {response.json().get("deletedCount")}')
    else:
        print(
            f'status code : {response.status_code} | message : {response.text}')


def delete_many(filter={}):
    url = f"{URL}/endpoint/data/v1/action/deleteMany"
    payload = json.dumps({
        "collection": COLLECTION,
        "database": DATABASE,
        "dataSource": "AtlasCluster",
        'filter': filter
    })
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': API_KEY,
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if 200 <= response.status_code < 300:
        print(
            f'status code : {response.status_code} | deletedCount : {response.json().get("deletedCount")}')
    else:
        print(
            f'status code : {response.status_code} | message : {response.text}')



def reset_collection():
    url = f"{URL}/endpoint/data/v1/action/deleteMany"
    payload = json.dumps({
        "collection": COLLECTION,
        "database": DATABASE,
        "dataSource": "AtlasCluster",
        'filter': {}
    })
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': API_KEY,
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if 200 <= response.status_code < 300:
        print(
            f'status code : {response.status_code} | deletedCount : {response.json().get("deletedCount")}')
    else:
        print(
            f'status code : {response.status_code} | message : {response.text}')


def add_one(data: dict):
    url = f"{URL}/endpoint/data/v1/action/insertOne"
    payload = json.dumps({
        "collection": COLLECTION,
        "database": DATABASE,
        "dataSource": "AtlasCluster",
        "document": data
    })
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': API_KEY,
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if 200 <= response.status_code < 300:
        print(
            f'status code : {response.status_code} | insertedId : {response.json().get("insertedId")}')
    else:
        print(
            f'status code : {response.status_code} | message : {response.text}')


def update_one(data: dict):
    url = f"{URL}/endpoint/data/v1/action/updateOne"
    payload = json.dumps({
        "collection": COLLECTION,
        "database": DATABASE,
        "dataSource": "AtlasCluster",
        'filter': {
            'folder': data.get('folder')
        },
        "update": data,
        'upsert': True
    })
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': API_KEY,
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if 200 <= response.status_code < 300:
        print(
            f'status code : {response.status_code} | message : {response.text}')
    else:
        print(
            f'status code : {response.status_code} | message : {response.text}')

    return response.status_code, response.text


def get_sample_data(folder='') -> dict:

    sample_data = {'folder': folder,
                   'location': '',
                   'url': '',
                   'domain': '',
                   'html_title': '',
                   'phish_prediction': 0,
                   'target_prediction': '',
                   'has_logo': False,
                   'has_forbidden_words': False,
                   'brand_inside_targetlist': False,
                   'found_knowledge': False,
                   'knowledge_discovery_branch': '',
                   'has_logo_runtime': 0,
                   'phishintention_runtime': 0,
                   'kd_runtime': 0,
                   'wi_runtime': 0,
                   'expand_targetlist_runtime': 0,
                   'total_runtime': 0,
                   'modified': int(datetime.now().timestamp()),
                   'created': int(datetime.now().timestamp())
                   }

    return sample_data
