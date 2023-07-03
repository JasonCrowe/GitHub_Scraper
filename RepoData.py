import requests
from time import sleep
from loguru import logger
from parsel import Selector
from pprint import pprint
import json


class GitHub(object):
    def __init__(self, repo):
        self.used_by = None
        self.repo = repo
        self.repo_auth = self.repo.split("/")[0]
        self.repo_name = self.repo.split("/")[1]
        self.repo_data = None
        self.contrib_data = list()
        self.stars_data = set()
        self.issues = dict()
        self.data = {}
        self.main()

    def main(self):
        self.get_repo_info()
        sleep(1)
        self.get_contrib_info()
        sleep(1)
        self.get_stars_info()
        sleep(1)
        self.scrape_issues()
        sleep(1)
        self.parse_repo_data()
        sleep(1)
        self.get_used_by()

    def get_repo_info(self):
        url = f"https://api.github.com/repos/{self.repo_auth}/{self.repo_name}"
        response = requests.get(url)
        if response.status_code == 200:
            self.repo_data = response.json()

    def get_contrib_info(self, threshold=15):
        url = f"https://api.github.com/repos/{self.repo_auth}/{self.repo_name}/contributors"
        page = 1

        while True:
            sleep(threshold)
            logger.info(f'Page: {page}')
            r = requests.get(url, params={'page': page, 'per_page': 100})
            if r.status_code == 200:
                logger.debug(len(r.json()))
                self.contrib_data.extend(r.json())
                if len(r.json()) == 0:
                    break
            # else:
            #     pprint(r.headers)
            #     print(r.text)
            #     print(r.status_code)
            page += 1

    def get_stars_info(self, threshold=5):
        url = f"https://github.com/{self.repo_auth}/{self.repo_name}/stargazers"
        page = 1

        while True:
            sleep(threshold)
            logger.info(f'Stars Page: {page}')
            r = requests.get(url, params={'page': page})
            if r.status_code == 200:
                sel = Selector(r.text)
                _ = [self.stars_data.add(x) for x in sel.xpath('//a[@data-hovercard-type="user"]/@href').getall()]
            else:
                pprint(r.headers)
                print(r.text)
                print(r.status_code)
                break
            page += 1

    def get_used_by(self):
        try:
            r = requests.get(f'https://github.com/{self.repo_auth}/{self.repo_name}/network/dependents')
            sel = Selector(r.text)
            used_by = [x.strip() for x in
                       sel.xpath('//a[contains(@href, "network/dependents?dependent_type=REPOSITORY")]/text()').getall()
                       if x.strip() != ''][0].split()[0]
        except Exception:
            used_by = None
        self.used_by = used_by

    @staticmethod
    def parse_number(value):
        nums = '0123456789'
        out_value = list()
        for v in value:
            if v in nums:
                out_value.append(v)
        return int(''.join(out_value))

    def scrape_issues(self):
        r = requests.get(f'https://github.com/{self.repo_auth}/{self.repo_name}/issues')
        sel = Selector(r.text)
        self.issues['open_issues'] = self.parse_number(list(set([x.strip() for x in sel.xpath('//a[@data-ga-click="Issues, Table state, Open"]//text()').getall() if x.strip() != '']))[0])
        self.issues['closed_issues'] = self.parse_number(list(set([x.strip() for x in sel.xpath('//a[@data-ga-click="Issues, Table state, Closed"]//text()').getall() if x.strip() != '']))[0])
        self.issues['total_issues'] = int(self.issues['open_issues']) + int(self.issues['closed_issues'])

    def parse_repo_data(self):
        self.data['stargazers_count'] = self.repo_data["stargazers_count"]
        self.data['forks_count'] = self.repo_data["forks_count"]
        self.data['contrib_count'] = len(self.contrib_data)
        self.data['contrib_users'] = [x['login'] for x in self.contrib_data]
        self.data['topics'] = self.repo_data["topics"]
        self.data.update(self.issues)
        self.data['used_by'] = self.used_by


if __name__ == "__main__":
    logger.info('Starting Scraping')
    repo_name = 'oppia/oppia'
    gh = GitHub(repo_name)
    with open(f"./repo_{repo_name.replace('/', '_')}.json", "w", encoding='utf8') as file:
        json.dump(gh.data, file, ensure_ascii=False)
        logger.info('File Saved')
    print(gh.data)
    logger.info('Scraper Complete')
