from lxml import html
import requests
import ast
import json
import matplotlib.pyplot as plt
import urllib.request

def nasdaq_parse(link):
    """
    Get a list of the top 100 companies listed on NASDAQ
    """
    # Request
    page = requests.get(link)
    tree = html.fromstring(page.content)
    # Parse
    companies_str = tree.xpath('//script[@type="text/javascript"]/text()')[12][17:-27]
    companies_list = nasdaq_format(companies_str)

    return companies_list


def nasdaq_format(companies):
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


def get_stocks(company_symbols, type):
    """
    Make API call to get the stock variations of the selected companies
    """
    # Get the api key
    with open('api_key.json') as f:
        data = json.load(f)
        api_key = data["alphavantage"]

    # Make the request
    contents = urllib.request.urlopen("https://www.alphavantage.co/query?function="
    + type + "&symbol=" + company_symbols + "&apikey=" + api_key).read()
    # Parse it
    json_res = json.loads(contents)
    series = json_res["Time Series (Daily)"]
    days = [day for day in series]
    closing = [series[day]["4. close"] for day in days]

    return days, closing


def get_news_sources():
    # Get the api key
    with open('api_key.json') as f:
        data = json.load(f)
        api_key = data["newsapi"]

    url = ('https://newsapi.org/v2/sources?language=en&'
            'apiKey=' + api_key)

    response = requests.get(url)
    json_res = response.json()["sources"]
    sources = [[source["name"]] for source in json_res]
    ids = [source["id"] for source in json_res]

    options=[]
    # Get the company name and symbol.
    for i in range(len(sources)):
        new_source = {'label': sources[i][0], 'value': ids[i]}
        options.append(new_source)

    return options


def format_companies(companies):
    nasdaq = nasdaq_parse("https://www.nasdaq.com/quotes/nasdaq-100-stocks.aspx")

    formatted_companies = ""
    for company in nasdaq:
        if(company['value'] == companies[0]):

            if(company['label'][-6:] == ", Inc."):
                return company['label'][:-6]

            if(company['label'][-5:] == ", Inc"):
                return company['label'][:-5]

            if(company['label'][-5:] == " Inc."):
                return company['label'][:-5]

            return company['label']


def format_sources(sources):
    formatted_sources = ""
    for source in sources:
        formatted_sources += source["value"] + ','

    return formatted_sources


def get_articles(companies, date):
    # Get the news sources
    sources = get_news_sources()
    # Format the news sources
    formatted_sources = format_sources(sources)
    # Format the companies
    formatted_companies = format_companies(companies)
    print(formatted_companies)
    # Get the api key
    with open('api_key.json') as f:
        data = json.load(f)
        api_key = data["newsapi"]

    # Get the articles
    contents = urllib.request.urlopen("http://newsapi.org/v2/everything?sources="
    + formatted_sources + "&q=" + formatted_companies
    + "&sortBy=relevancy&from=" + date + "&apikey=" + api_key).read()

    # Parse them
    json_res = json.loads(contents)

    return json_res
