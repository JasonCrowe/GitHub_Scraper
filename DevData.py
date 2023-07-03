import requests
from time import sleep
from loguru import logger
# from parsel import Selector
# from pprint import pprint


def parse_user(input_json):
    fields = ['login', 'html_url', 'name', 'blog', 'location', 'email', 'bio', 'repos_url']
    item = dict()
    for f in fields:
        item[f] = input_json[f]
    return item


def parse_user_repos(input_json):
    items = list()
    for repo in input_json:
        fields = ['name', 'full_name', 'fork', ]
        item = dict()
        for f in fields:
            item[f] = repo[f]
        items.append(item)
    return items


def get_starred_data(input_user, threshold=15):
    url = f"https://api.github.com/repos/{input_user}/starred"
    page = 1
    starred_data = []
    while True:
        sleep(threshold)
        logger.info(f'Starred Repos Page: {page}')
        r = requests.get(url, params={'page': page, 'per_page': 100})
        if r.status_code == 200:
            logger.debug(len(r.json()))
            starred_data.extend(r.json())
            if len(r.json()) == 0:
                break
        else:
            break
        page += 1
    return starred_data


def main(input_user):
    r1 = requests.get(f'https://api.github.com/users/{input_user}')
    user = parse_user(r1.json())
    r2 = requests.get(f'https://api.github.com/users/{input_user}/repos')
    user['repos'] = parse_user_repos(r2.json())
    user['starred'] = get_starred_data(input_user)
    return user


if __name__ == "__main__":
    dev_name = 'Yidadaa'
    user_data = main(dev_name)
