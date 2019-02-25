from lxml import html
import requests
import ast
import json
import matplotlib.pyplot as plt
import urllib.request
import re
from datetime import datetime, timedelta

def get_api_key(name):
    with open('api_key.json') as f:
        data = json.load(f)
        api_key = data[name]
        return api_key


def nasdaq_parse(link):
    """
    Get a list of the top 100 companies listed on NASDAQ
    """
    # Request
    page = requests.get(link)
    tree = html.fromstring(page.content)
    # Parse
    companies_str = tree.xpath('//script[@type="text/javascript"]/text()')[12][17:-27]
    companies_list = format_nasdaq(companies_str)

    return companies_list


def format_nasdaq(companies):
    """
    Convert the parsed companies list to format that is interpretable by dash_core_components.dropdown
    """
    companies_list = ast.literal_eval(companies)
    options=[]
    # Get the company name and symbol.
    for i in range(len(companies_list)):
        new_company = {'label': companies_list[i][1], 'value': companies_list[i][0]}
        options.append(new_company)

    return options


def get_stocks_daily(company_symbols):
    """
    Make API call to get the stock variations of the selected companies
    """
    # Get the api key
    api_key = get_api_key("alphavantage")
    # Make the request
    contents = urllib.request.urlopen("https://www.alphavantage.co/query?function="
    + "TIME_SERIES_DAILY&symbol=" + company_symbols + "&apikey=" + api_key).read()
    # Parse it
    json_res = json.loads(contents)
    series = json_res["Time Series (Daily)"]
    days = [day for day in series]
    closing = [series[day]["4. close"] for day in days]

    return days, closing


def get_hidden_stocks_daily(company_symbols):
    """
    Make API call to get the stock variations of the selected companies and returns
    it in JSON format
    """
    # Get the api key
    api_key = get_api_key("alphavantage")
    # Make the request
    contents = urllib.request.urlopen("https://www.alphavantage.co/query?function="
    + "TIME_SERIES_DAILY&symbol=" + company_symbols + "&apikey=" + api_key).read()
    return contents


def get_stocks_intraday(company_symbols):
    """
    Make API call to get the stock variations of the selected companies
    """
    # Get the api key
    api_key = get_api_key("alphavantage")
    # Make the request
    contents = urllib.request.urlopen("https://www.alphavantage.co/query?function="
    + "TIME_SERIES_INTRADAY&symbol=" + company_symbols + "&interval=5min&apikey="
    + api_key).read()
    # Parse it
    json_res = json.loads(contents)
    series = json_res["Time Series (5min)"]
    days = [day for day in series]
    closing = [series[day]["4. close"] for day in days]

    return days, closing


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

    options=[]
    # Get the company name and symbol
    for i in range(len(sources)):
        new_source = {'label': sources[i][0], 'value': ids[i]}
        options.append(new_source)

    return options


def format_companies(company):
    """
    Format the selected company so that the API can find relevant articles.
    """
    # Get the company names and symbols
    nasdaq = nasdaq_parse("https://www.nasdaq.com/quotes/nasdaq-100-stocks.aspx")
    # Find the right company name given the symbol
    formatted_companies = ""
    for nasdaq_company in nasdaq:
        if(nasdaq_company['value'] == company):
            # Remove junk at the end of the names
            if(nasdaq_company['label'][-6:] == ", Inc."):
                return re.sub(r' ', "-", nasdaq_company['label'][:-6])

            if(nasdaq_company['label'][-5:] == ", Inc"):
                return re.sub(r' ', "-", nasdaq_company['label'][:-5])

            if(nasdaq_company['label'][-5:] == " Inc."):
                return re.sub(r' ', "-", nasdaq_company['label'][:-5])

            return re.sub(r' ', "-", nasdaq_company['label'])


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
    contents = urllib.request.urlopen("http://newsapi.org/v2/everything?sources="
    + formatted_sources + "&q=" + formatted_company + "&sortBy=relevancy&from="
    + start + "&to=" + end + "&apikey=" + api_key).read()

    # Parse them
    json_res = json.loads(contents)

    return json_res
