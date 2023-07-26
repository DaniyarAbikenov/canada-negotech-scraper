import json
import os.path
import sys

import requests
import argparse

# host = "https://negotech.service.canada.ca/search/index.html?"
host = "https://search-recherche.service.canada.ca/negotech"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "content-type": "application/json"
}

params = {
    "api-version": "2021-04-30-Preview"
}


def take_arguments():
    parser = argparse.ArgumentParser(description='Scraper data from https://negotech.service.canada.ca/')
    filters = parser.add_argument_group(title="filters")
    filters.add_argument('-e', '--employer', type=str, help="Filter: Employer name", dest="employer_name")
    filters.add_argument('-l', '--location', type=str, help="Location", dest="location")
    filters.add_argument('-u', '--union', type=str, help="Union name", dest="union_name")
    filters.add_argument('-s', '--sector', help="Sector", dest="sector", choices=["public", "private"])
    filters.add_argument('-d', '--docstatus', help="Document Status", dest="document_status",
                         choices=["current", "active", "historical"])

    # parser.add_argument('-S', '--sort', help="Sort By", dest="sort",
    #                     choices=["Score", "Agreement Number", "Employer Name", "Union Name",
    #                              "Effective Date", "Expiry Date", "Employee Count"],
    #                     default="Score")

    return parser.parse_args()


def filter_item(item, value, filter_, **kwargs):
    if "choices" not in kwargs:
        if item is not None:
            filter_.append(f'({value.replace("{value}", item)})')
    else:
        if item is not None:
            filter_.append(f'({value.replace("{value}", kwargs["choices"][item])})')
    return filter_


def create_filters(params):
    filter_ = ["(file_extension ne null)", "(agreementfull_i ne null)"]
    queries = [
        [params.employer_name, "search.ismatchscoring('{value}', 'companyname_txt_en')"],
        [params.location, "search.ismatchscoring('{value}', 'cityprovincename_txt_en,cityname_txt_en')"],
        [params.union_name, "(search.ismatchscoring('{value}', 'unionname_txt_en')"],
    ]
    queries_select = [
        [params.sector, "publicprivate_i eq {value}", {"public": 0, "private": 1, }],
        [params.document_status, "currentindicator_s eq '{value}'", {"current": "Current", "active": "Active",
                                                                    "historical": "Historical", "all": "All"}]
    ]
    for item in queries:
        filter_ = filter_item(item[0], item[1], filter_)

    for item in queries_select:
        filter_ = filter_item(item[0], item[1], filter_, choices=item[2])
    return filter_


def download_agreement(url, lang, title=None, path="files"):
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


def scrape_one_list(count, offset, filter_obj):
    print(f"scraping {offset}-{offset + count}")
    count = str(count)
    offset = str(offset)
    data = '{"searchFields":"agreementcontent_txt_en,agreementcontent_txt_fr,summarycontent_txt_en,summarycontent_txt_fr","highlight":"agreementcontent_txt_en,agreementcontent_txt_fr,companyname_txt_en,companyname_txt_fr,unionname_txt_en,unionname_txt_fr,summarycontent_txt_en,summarycontent_txt_fr,naicsname_txt_en,naicsname_txt_fr,nocname_txt_en,nocname_txt_fr,cityprovincename_txt_en,cityprovincename_txt_fr,cityname_txt_en,cityname_txt_fr","top":{count},"skip":{offset},"count":true,"orderby":"search.score() desc, agreementfull_i desc","filter":"(file_extension ne null) and (agreementfull_i ne null) ","highlightPreTag":"<mark>","highlightPostTag":"</mark>","queryType":"full","searchMode":"all"}'
    data = {
        "searchFields":"agreementcontent_txt_en,agreementcontent_txt_fr,summarycontent_txt_en,summarycontent_txt_fr",
        "highlight":"agreementcontent_txt_en,companyname_txt_en,unionname_txt_en,summarycontent_txt_en,naicsname_txt_en,nocname_txt_en,cityprovincename_txt_en,cityname_txt_en",
        "top":"{count}",
        "skip":"{offset}",
        "count":'true',
        "orderby":"search.score() desc, agreementfull_i desc",
        "filter":filter_obj,
        "highlightPreTag":"<mark>",
        "highlightPostTag":"</mark>",
        "queryType":"full",
        "searchMode":"all"}
    data = str(data)
    data = data.replace("{count}", str(count)).replace("{offset}", str(offset)).replace("'", '"').replace("!!!", "'")
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
    filters = take_arguments()
    filter_obj = ' and '.join(create_filters(filters)).replace("'", "!!!")
    print(filter_obj)
    total = []
    count = 100
    offset = 0
    assesments = scrape_one_list(count, offset, filter_obj)
    total.extend(assesments)

    while len(assesments) == count:
        with open(f"part/{offset}-{offset + count}.json", "w", encoding="utf-8") as file:
            json.dump(total, file, indent=4, ensure_ascii=False)
        total = []
        offset += count
        assesments = scrape_one_list(count, offset, filter_obj)
        counter += len(assesments)
        total.extend(assesments)

    print(counter)


if __name__ == "__main__":
    main()
