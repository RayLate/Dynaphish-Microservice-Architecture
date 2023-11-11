import shutil
import os
import socket
from datetime import datetime


def cut_folder(source_path, destination_path):
    try:
        shutil.move(source_path, destination_path)
        print(f"Moved folder from {source_path} to {destination_path}")
    except Exception as e:
        print(f"Failed to move folder: {e}")


def delete_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Deleted folder: {folder_path}")
    except Exception as e:
        print(f"Failed to delete folder: {e}")


def kill_chrome():
    browser_exe = "chrome"
    os.system("pkill " + browser_exe)


def get_container_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


def check_folder(folder, queue):
    folder_path = f"/data/{queue}/{folder}"
    screenshot_path = os.path.join(folder_path, "shot.png")
    if not os.path.exists(screenshot_path):
        # screenshot does not exist
        delete_folder(folder_path)
        return None, None
    return folder_path, screenshot_path


class OnlineForbiddenWord:
    IGNORE_DOMAINS = [
        "wikipedia",
        "wiki",
        "bloomberg",
        "glassdoor",
        "linkedin",
        "jobstreet",
        "facebook",
        "twitter",
        "instagram",
        "youtube",
        "org",
        "accounting",
    ]

    # ignore those webhosting/domainhosting sites
    WEBHOSTING_TEXT = (
        "(webmail.*)|(.*godaddy.*)|(.*roundcube.*)|(.*clouddns.*)|(.*namecheap.*)|(.*plesk.*)|(.*rackspace.*)|(.*cpanel.*)|(.*virtualmin.*)|(.*control.*webpanel.*)|(.*hostgator.*)|(.*mirohost.*)|(.*hostinger.*)|(.*bisecthosting.*)|(.*misshosting.*)|(.*serveriai.*)|(.*register\.to.*)|(.*appspot.*)|"
        "(.*weebly.*)|(.*serv5.*)|(.*weebly.*)|(.*umbler.*)|(.*joomla.*)"
        "(.*webnode.*)|(.*duckdns.*)|(.*moonfruit.*)|(.*netlify.*)|"
        "(.*glitch.*)|(.*herokuapp.*)|(.*yolasite.*)|(.*dynv6.*)|(.*cdnvn.*)|"
        "(.*surge.*)|(.*myshn.*)|(.*azurewebsites.*)|(.*dreamhost.*)|host|cloak|domain|block|isp|azure|wordpress|weebly|dns|network|shortener|server|helpdesk|laravel|jellyfin|portainer|reddit|storybook"
    )

    WEBHOSTING_DOMAINS = [
        "godaddy",
        "roundcube",
        "clouddns",
        "namecheap",
        "plesk",
        "rackspace",
        "cpanel",
        "virtualmin",
        "control-webpanel",
        "hostgator",
        "mirohost",
        "hostinger",
        "bisecthosting",
        "misshosting",
        "serveriai",
        "register",
        "appspot",
        "weebly",
        "serv5",
        "weebly",
        "umbler",
        "joomla",
        "webnode",
        "duckdns",
        "moonfruit",
        "netlify",
        "glitch",
        "herokuapp",
        "yolasite",
        "dynv6",
        "cdnvn",
        "surge",
        "myshn",
        "azurewebsites",
        "dreamhost",
        "proisp",
        "accounting",
    ]


class MyLogger:
    def __init__(self, file_path):
        self.file_path = file_path

    def log(self, message):
        timestamp = datetime.now().strftime("%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {str(message)}"
        with open(self.file_path, "a") as file:
            file.write(log_message + "\n")
