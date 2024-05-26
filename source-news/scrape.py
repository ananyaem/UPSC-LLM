from http.client import HTTPException
import json
from time import sleep
from bs4 import BeautifulSoup
import requests
import os

OUT_DIR = "data"
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

BASE = "https://epaper.thehindu.com/ccidist-ws/th/th_delhi/issues"


def get(url):
    """
    Get content from a URL
    Args:
        url: The URL to get content from
    Returns:
        response: The response object from requests get call
    - Make a GET request to the given URL using the requests library
    - If an HTTPException occurs, print the error and recursively call the function to retry the request
    - Return the response object if request succeeds"""

    try:
        return requests.get(url)
    except HTTPException as e:
        print(e)
        return get(url)


init = get(BASE)
START = int(init.json()["issues"]["web"][0]["url"].split("/")[-2])

for issue in reversed(range(START+1)):
    CONF = f"/tmp/config-{issue}.txt"
    if os.path.exists(CONF):
        continue
    print(issue)

    CONFIG = f"{BASE}/{issue}/?json=true"
    config = get(CONFIG)
    if config.status_code != 200:
        json.dump({}, open(CONF, "w"))
        continue
    config = config.json()
    date = config["issueName"]
    date = date.split("-")
    date = f"{date[2]}-{date[1]}-{date[0]}"

    URL = f"{BASE}/{issue}/OPS"
    PAPER = URL + "/cciobjects.json"
    paper = get(PAPER)
    if paper.status_code != 200:
        continue
    paper = paper.json()

    docs = []
    for page in paper["children"]:
        for article in page["children"]:
            for content in article["content"]:
                if content["kind"] == "Text":
                    ref = content["reference"]
                    fname = os.path.join(OUT_DIR, f"{date}_{ref}")
                    if os.path.exists(fname):
                        continue
                    print(ref)
                    url = URL + "/" + ref
                    r = get(url)
                    if r.status_code == 200:
                        try:
                            soup = BeautifulSoup(r.text, "html.parser")
                            title = soup.find('title')
                            body = soup.find(class_="body")
                            if body:
                                if body.text:
                                    with open(fname, "w") as out:
                                        out.write(body.text)
                                        sleep(1)
                        except Exception as e:
                            print(e)

    print("Done", file=open(CONF, "w"))
