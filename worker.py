# -*- coding: utf-8 -*-
import requests
import os
import json
import time

# ---------- Target URL ----------
URL = "https://zath.qd.je/vr/"
PARAMS = {'page': "vr"}

HEADERS = {
    'User-Agent': "Mozilla/5.0 (Linux; Android 16; SM-S921B Build/BP4A.251205.006) AppleWebKit/537.36 (KHTML, like Gecko) Xcmcsy/4.0 Chrome/150.0.7871.124 Mobile Safari/537.36",
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    'Accept-Encoding': "gzip, deflate, br, zstd",
    'cache-control': "max-age=0",
    'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
    'sec-ch-ua-mobile': "?1",
    'sec-ch-ua-platform': '"Android"',
    'upgrade-insecure-requests': "1",
    'origin': "https://zath.qd.je",
    'x-requested-with': "com.mycompany.app.soulbrowser",
    'sec-fetch-site': "same-origin",
    'sec-fetch-mode': "navigate",
    'sec-fetch-user': "?1",
    'sec-fetch-dest': "document",
    'referer': "https://zath.qd.je/vr/?page=vr",
    'accept-language': "en-GB,en-US;q=0.9,en;q=0.8",
    'priority': "u=0, i",
    'Cookie': "PHPSESSID=i19oms4r2drk48tdgdovqvo9gu"
}

CREATE_BASE = {
    'lang_id': "46",
    'create_bulk_vr': "",
    '_active_page': "vr"
}

CLOSE_PAYLOAD = {
    'close_bulk_vr': "",
    '_active_page': "vr"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
COUNT_FILE = os.path.join(BASE_DIR, "count.txt")
STATUS_FILE = os.path.join(BASE_DIR, "status.txt")

def load_config():
    default = {"vr_title1": "", "vr_title2": "", "vr_announcement": "", "enabled": False}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return default

def update_count():
    try:
        with open(COUNT_FILE, "r") as f:
            count = int(f.read().strip()) + 1
    except:
        count = 1
    with open(COUNT_FILE, "w") as f:
        f.write(str(count))

def update_status(create_status, close_status):
    with open(STATUS_FILE, "w") as f:
        f.write(f"CREATE {create_status} | CLOSE {close_status}")

def main():
    config = load_config()
    if not config.get("enabled", False):
        return

    create_payload = {
        'vr_title1': config.get("vr_title1", ""),
        'vr_title2': config.get("vr_title2", ""),
        'vr_announcement': config.get("vr_announcement", ""),
        **CREATE_BASE
    }

    try:
        r1 = requests.post(URL, params=PARAMS, data=create_payload, headers=HEADERS, timeout=30)
        create_code = r1.status_code
        time.sleep(1)
        r2 = requests.post(URL, params=PARAMS, data=CLOSE_PAYLOAD, headers=HEADERS, timeout=30)
        close_code = r2.status_code

        update_count()
        update_status(create_code, close_code)
        print(f"[worker] OK – CREATE {create_code}, CLOSE {close_code}")

    except Exception as e:
        with open(STATUS_FILE, "w") as f:
            f.write(f"ERROR: {str(e)}")
        print(f"[worker] ERROR: {e}")

if __name__ == "__main__":
    main()
