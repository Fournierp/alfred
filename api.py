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


def stock(company_symbols, type):
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
