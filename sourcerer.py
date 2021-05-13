from dataclasses import dataclass
from typing import List
import yaml
import requests
from bs4 import BeautifulSoup
import re


@dataclass
class Candidate:
    name: str
    data_source: str
    linkedin: str
    position: str
    company: str
    github: str


@dataclass
class Candidates:
    candidates: List[Candidate]


def load_config():
    with open("config.yaml", 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def get_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0'
    }
    response = requests.request("GET", url, headers=headers)

    return response.text


def process_name(text):
    names = []
    two_words = re.match(r'^.*\ .*$', text.strip())
    email = re.match(r'([\w.-]+)@([\w.-]+)', text.strip()) 
    if "&" in text:
        names = [n.strip() for n in text.split('&')]
    elif two_words or email:
        names.append(text.strip())
    else:
        names = []
    return names


def main():
    names = []
    candidates = []
    c = load_config()
    for target in c['targets']:
        contents = get_page(target['url'])
        soup = BeautifulSoup(contents, 'html.parser')
        tag, attribute_type, attribute = target['capture_tag'].split('|')
        mydivs = soup.find_all(tag, {attribute_type: attribute})
        for n in mydivs:
            t = n.find("p").text
            name = process_name(t)
            if name:
                names.extend(name)

        for name in names:
            candidate = Candidate(name, target['url'], "", "", "", "")
            candidates.append(candidate)

    for c in candidates:
        print(c.name)


if __name__ == '__main__':
    main()