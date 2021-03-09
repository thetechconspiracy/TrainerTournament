from bs4 import BeautifulSoup
import os
import requests
import sys


if(len(sys.argv) != 2):
    print("Usage: downloadBulbapedia.py <URL>")
    exit()
catPage = sys.argv[1]
catCode = requests.get(catPage).content
soup = BeautifulSoup(catCode, 'html.parser')
for div in soup.select("div[class=mw-category]"):
    links = div.findAll("a")
    for link in links:
        linkStr = str(link.get('href'))[6:]
        if "User:" in linkStr:
            continue #This will only cause issues, there aren't any trainers here anyway
        if "/" in linkStr:
            continue
        wikicodeURL = "https://bulbapedia.bulbagarden.net/w/index.php?title=" + linkStr + "&action=raw"
        code = requests.get(wikicodeURL).content
        with open("wiki/"+linkStr, "wb") as f:
            f.write(code)

#wikicodeURL = "https://bulbapedia.bulbagarden.net/w/index.php?title=" + page + "&action=raw"