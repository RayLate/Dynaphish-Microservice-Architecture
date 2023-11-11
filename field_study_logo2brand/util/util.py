import shutil

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
