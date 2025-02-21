import requests
from bs4 import BeautifulSoup
import csv

URL = "https://fimea.fi/apteekit/verkkopalvelutoiminta/lailliset_apteekin_verkkopalvelut"
# it actually has a space at the end, but only works like this?
DIVCLASSNAME = "journal-content-article"


# returns list of bs4.elements.Tag objects
# (<p> tags with pharmacy name and link(s))
def list_pharmas(online=False):
    all_listings = []
    listings_with_links = []
    if online:
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
    else:
        contents = ""
        with open("./thepage/fimea.html", "r", encoding="utf8") as savedpage:
            contents = savedpage.read()
        soup = BeautifulSoup(contents, "html.parser")
    div_with_list = soup.find(class_=DIVCLASSNAME)
    all_listings = div_with_list.find_all("p", recursive=False)
    for ptag in all_listings:
        if (ptag.find_all("a")):
            listings_with_links.append(ptag)
    return listings_with_links


def sort_pharmas(listings):
    magento = []
    eapteekki = []
    others = []
    failed = []
    for i, ptag in enumerate(listings):
        try:
            storepage = requests.get(ptag.find("a")["href"])
            storesoup = BeautifulSoup(storepage.content, "html.parser")
            if storesoup.find("script", type="text/x-magento-init"):
                magento.append(ptag)
            elif storesoup.find("link", href="https://media.eapteekki.fi/static/site/img/favicon.44cd71b050d4.ico"):
                eapteekki.append(ptag)
            else:
                others.append(ptag)
        except Exception as err:
            print(err)
            failed.append(ptag)
        print(f"{i}\r")
    print(f"\nListings: {len(listings)}\n")
    print(f"Magento: {len(magento)}\n")
    print(f"eAPTEEKKI: {len(eapteekki)}\n")
    print(f"Others: {len(others)}\n")
    print(f"Failed: {len(failed)}\n")
    return magento, eapteekki, others, failed

def save_to_csv(pharmatype, listings):
    filepath = f"./csvs/{pharmatype}.csv"
    fields = ["NAME", "LINKS"]
    rows = []
    for ptag in listings:
        try:
            name = (ptag.find("strong")).string
        except:
            continue
        links = []
        for atag in ptag.find_all("a"):
            links.append(atag["href"])
        rows.append([name, links])
    with open(filepath, "w", encoding="utf8") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)


#print("hell")
magento, eapteekki, others, failed = sort_pharmas(list_pharmas())

save_to_csv("magento", magento)
save_to_csv("eapteekki", eapteekki)
save_to_csv("others", others)
save_to_csv("failed", failed)


