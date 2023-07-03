import requests
import json
from loguru import logger
from time import sleep
import pandas as pd


def get_github_search_results(search_term):
    page = 1
    results = list()
    url = "https://api.github.com/search/repositories"
    for i in range(10):
        logger.info(f'Search Results Page: {page}')
        params = {
            "q": search_term,
            "per_page": 100,
            "page": page,
        }
        response = requests.get(url, params=params)
        sleep(3)
        if response.status_code == 200:
            data = json.loads(response.content)
            results.extend(data['items'])
            page += 1
        else:
            print(response.status_code)
            print(response.text)
    return results


def main(input_search_term):
    results = get_github_search_results(input_search_term)
    repos = [{'name': x['full_name'], 'url':f'https://www.github.com/{x["full_name"]}'} for x in results]
    return pd.DataFrame(repos)


if __name__ == "__main__":
    search_term = input('Enter Search Term: ')
    df = main(search_term)
    df.to_excel(f"SearchResults_{search_term.replace(' ', '_')}.xlsx", index=False)
