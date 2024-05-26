from datetime import date
import re
from time import sleep
import requests


BASE = "https://vajiramias.com"
URL = BASE + "/current-affairs-partial"
YEAR = 2019

LINK_PATTERN = re.compile("\\/current-affairs\\/[^\\/]+\\/[a-f0-9]{24}\\/")
TITLE_PATTERN = re.compile("<title> (.*) <\\/title>")
CONTENT_PATTERN = re.compile("<meta name=\"description\" content=\"([^\"]*)\"")
SOURCE_PATTERN = re.compile("Source :\\s*<a href=\":?([^\"]*)\"")

OUT_DIR = "data"


def get_content(year, month):
    page = 1
    more = True
    while more:
        print(year, month, page)
        r = requests.get(f"{URL}/{year}/{month}?page={page}")
        if r.status_code != 200:
            print("ERROR in response")
            print(r.text)
            break
        data = r.json()
        if not data["success"]:
            print("ERROR in data:")
            print(data)
            break
        more = data["has_more"]
        content = data["content"]

        x = re.findall(LINK_PATTERN, content)
        print(len(x))
        for link in x:
            print(link)
            try:
                r = requests.get(BASE+link)
                if r.status_code != 200:
                    print("ERROR in link")
                    print(r.text)
                    continue
                text = r.text
                tm = re.search(TITLE_PATTERN, text)
                assert tm, link
                cm = re.search(CONTENT_PATTERN, text)
                assert cm, link
                sm = re.search(SOURCE_PATTERN, text)
                # assert sm, link
                title = tm.group(1)
                content = cm.group(1)
                src = "NOSRC"
                if sm:
                    src = sm.group(1)

                fname = f"{OUT_DIR}/{year}-{month}-{link.split('/')[-2]}.txt".strip().replace(
                    " ", "_")
                with open(fname, "w") as f:
                    f.write("\n".join((title, content, src, BASE+link)))
                sleep(1)
            except Exception as e:
                print("Failed to get", link, e)
        if more:
            page += 1


if __name__ == "__main__":
    for year in range(2019, 2024):
        for month in range(1, 13):
            get_content(year, month)

    while True:
        get_content(date.today().year, date.today().month)
        sleep(3600)  # sleep for an hour
