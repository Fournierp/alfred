import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib import request

import requests


def get_api_key(name: str) -> str:
    with Path('api_key.json').open() as f:
        data = json.load(f)
        data = json.load(f)
        return data[name]


def get_news_sources() -> list[dict[str, str]]:
    api_key = get_api_key('newsapi')

    response = requests.get('https://newsapi.org/v2/sources?language=en&apiKey=' + api_key, timeout=10)
    json_res = response.json()['sources']
    sources = [[source['name']] for source in json_res]
    ids = [source['id'] for source in json_res]

    options = []
    for i in range(len(sources)):
        new_source = {'label': sources[i][0], 'value': ids[i]}
        options.append(new_source)

    return options


def format_companies(company: str) -> str:
    if company[-6:] == ', Inc.':
        return re.sub(r' ', '-', company[:-6])

    if company[-5:] == ', Inc':
        return re.sub(r' ', '-', company[:-5])

    if company[-5:] == ' Inc.':
        return re.sub(r' ', '-', company[:-5])

    return re.sub(r' ', '-', company)


def format_sources(sources: list[dict[str, str]]) -> str:
    formatted_sources = ''
    for source in sources:
        formatted_sources += source['value'] + ','

    return formatted_sources


def get_articles(company: str) -> dict:
    sources = get_news_sources()
    formatted_sources = format_sources(sources)
    formatted_company = format_companies(company)
    api_key = get_api_key('newsapi')
    end = datetime.now(tz=UTC).strftime('%Y-%m-%d')
    start = (datetime.now(tz=UTC) - timedelta(days=14)).strftime('%Y-%m-%d')
    contents = request.urlopen(
        'http://newsapi.org/v2/everything?sources='
        + formatted_sources
        + '&q='
        + formatted_company
        + '&sortBy=relevancy&from='
        + start
        + '&to='
        + end
        + '&apikey='
        + api_key
    ).read()

    return json.loads(contents)
