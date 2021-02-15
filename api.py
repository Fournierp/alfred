import json
import requests
import re
from datetime import datetime, timedelta
from urllib import request


def get_api_key(name):
    with open('api_key.json') as f:
        data = json.load(f)
        api_key = data[name]
        return api_key


def get_news_sources():
    """
    Function to get all the support News Sources in English.
    """
    # Get the api key
    api_key = get_api_key("newsapi")

    # Make the API call
    response = requests.get('https://newsapi.org/v2/sources?language=en&apiKey=' + api_key)
    json_res = response.json()["sources"]
    sources = [[source["name"]] for source in json_res]
    ids = [source["id"] for source in json_res]

    options = []
    # Get the company name and symbol
    for i in range(len(sources)):
        new_source = {'label': sources[i][0], 'value': ids[i]}
        options.append(new_source)

    return options


def format_companies(company):
    """
    Format the selected company so that the API can find relevant articles.
    """
    # Remove junk at the end of the names
    if company[-6:] == ", Inc.":
        return re.sub(r' ', "-", company[:-6])

    if company[-5:] == ", Inc":
        return re.sub(r' ', "-", company[:-5])

    if company[-5:] == " Inc.":
        return re.sub(r' ', "-", company[:-5])

    return re.sub(r' ', "-", company)


def format_sources(sources):
    """
    Make a comma separated string of news source labels.
    """
    formatted_sources = ""
    for source in sources:
        formatted_sources += source["value"] + ','

    return formatted_sources


def get_articles(company):
    """
    Function that makes the api calls given company names.
    """
    # Get the news sources
    sources = get_news_sources()
    # Format the news sources
    formatted_sources = format_sources(sources)
    # Format the companies
    formatted_company = format_companies(company)
    # Get the api key
    api_key = get_api_key("newsapi")
    # Create a timespan : 14 days
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
    # Get the articles
    contents = request.urlopen("http://newsapi.org/v2/everything?sources="
                               + formatted_sources + "&q=" + formatted_company + "&sortBy=relevancy&from="
                               + start + "&to=" + end + "&apikey=" + api_key).read()

    # Parse them
    json_res = json.loads(contents)

    return json_res
