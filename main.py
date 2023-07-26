import json
import os.path
import sys

import requests

# host = "https://negotech.service.canada.ca/search/index.html?"
host = "https://search-recherche.service.canada.ca/negotech"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "content-type": "application/json"
}


params = {
    "api-version": "2021-04-30-Preview"
}


def download_agreement(url,lang, title=None, path="files"):
    url = url.split("/")[-2:]
    if lang == "eng":
        url = f"https://negotech.service.canada.ca/{lang}/agreements/{url[0]}/{url[1]}"
    elif lang == "fra":
        url = f"https://negotech.service.canada.ca/{lang}/ententes/{url[0]}/{url[1]}"
    print(url)
    if not os.path.exists(path):
        os.mkdir("files")
    res = requests.get(url)
    if title is None:
        title = url.split("/")[-1]
    with open(f"{path}/{title.split('.')[0]} ({lang}) .{title.split('.')[-1]}", "wb") as file:
        file.write(res.content)


def scrap_one_list(count, offset):
    print(f"scraping {offset}-{offset + count}")
    count = str(count)
    offset = str(offset)
    data = '{"searchFields":"agreementcontent_txt_en,agreementcontent_txt_fr,summarycontent_txt_en,summarycontent_txt_fr","highlight":"agreementcontent_txt_en,agreementcontent_txt_fr,companyname_txt_en,companyname_txt_fr,unionname_txt_en,unionname_txt_fr,summarycontent_txt_en,summarycontent_txt_fr,naicsname_txt_en,naicsname_txt_fr,nocname_txt_en,nocname_txt_fr,cityprovincename_txt_en,cityprovincename_txt_fr,cityname_txt_en,cityname_txt_fr","top":{count},"skip":{offset},"count":true,"orderby":"search.score() desc, agreementfull_i desc","filter":"(file_extension ne null) and (agreementfull_i ne null) ","highlightPreTag":"<mark>","highlightPostTag":"</mark>","queryType":"full","searchMode":"all"}'
    data = '{"searchFields":"agreementcontent_txt_en,agreementcontent_txt_fr,summarycontent_txt_en,summarycontent_txt_fr","highlight":"agreementcontent_txt_en,companyname_txt_en,unionname_txt_en,summarycontent_txt_en,naicsname_txt_en,nocname_txt_en,cityprovincename_txt_en,cityname_txt_en","top":{count},"skip":{offset},"count":true,"orderby":"search.score() desc, agreementfull_i desc","filter":"(file_extension ne null) and (agreementfull_i ne null) ","highlightPreTag":"<mark>","highlightPostTag":"</mark>","queryType":"full","searchMode":"all"}'
    data = data.replace("{count}", str(count)).replace("{offset}", str(offset))
    assesments = requests.post(host, headers=headers, data=data, params=params).json()["value"]
    need_download = False
    if need_download:
        for item in assesments:

            if item["agreeengpath_s"] is not None:
                download_agreement(item["agreeengpath_s"], lang="eng")
            elif item["agreefrapath_s"] is not None:
                download_agreement(item["agreefrapath_s"], lang="fra")
            else:
                print(f"{item['id']} - no file")
    return assesments

def main():
    counter = 0
    total = []
    count = 100
    offset = 0
    assessments = scrap_one_list(count, offset)
    total.extend(assessments)

    while len(assessments) == count:
        with open(f"part/{offset}-{offset+count}.json", "w", encoding="utf-8") as file:
            json.dump(total, file, indent=4, ensure_ascii=False)
        total = []
        offset += count
        assessments = scrap_one_list(count, offset)
        counter += len(assessments)
        total.extend(assessments)

    print(f"scraped {counter} data")


if __name__ == "__main__":
    main()
