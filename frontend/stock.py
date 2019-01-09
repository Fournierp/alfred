import pandas as pd
import json
import os
import matplotlib.pyplot as plt
from lxml import html
import requests
import pickle


import re
import nltk
import pandas as pd
import numpy as np

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
english_stemmer=nltk.stem.SnowballStemmer('english')

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from sklearn.feature_extraction.text import CountVectorizer

import pickle

def code(company_name):
    """
    Find the company code in the NASDAQ top 100 list
    """
    nasdaq = pd.read_csv("../data/nasdaq100list.csv")
    for index, row in nasdaq.iterrows():
        cmp = row[1]
        if(company_name in cmp):
            return row[0]

    return None

def parse(json_res, folder):
    """
    Plot 25 units worth os closing price
    """
    json_res = json.loads(json_res)
    series = json_res["Time Series (Daily)"]
    days = [day for day in series]
    closing = [series[day]["4. close"] for day in days]

    plt.plot(days[:25], closing[:25])
    # plt.savefig(os.path.join(folder, 'testplot.png'))
    return os.path.join(folder, '19Alfred-Batman.gif')

def get_advice(company_name):
    data = pd.read_csv('../data/Combined_News_DJIA.csv')
    train = data
    trainheadlines = []
    for row in range(0,len(train.index)):
        trainheadlines.append(' '.join(str(x) for x in train.iloc[row,2:27]))

    advancedvectorizer = TfidfVectorizer( min_df=0.03, max_df=0.97, max_features = 200000, ngram_range = (2, 2))
    advancedtrain = advancedvectorizer.fit_transform(trainheadlines)

    advancedmodel = LogisticRegression()
    advancedmodel = advancedmodel.fit(advancedtrain, train["Label"])

    url = ('https://newsapi.org/v2/everything?'
           'q=' + company_name + '&'
           'from=2018-11-11&'
           'sortBy=popularity&'
           'apiKey=3423b13b0b374ba789418fccd815a5e5')
    response = requests.get(url)
    json_res = response.json()["articles"]
    articles = [[article["title"]] for article in json_res]
    links = [article["url"] for article in json_res]


    testheadlines = []
    for row in range(0,len(articles)):
        testheadlines.append(' '.join(str(x) for x in articles[2:27]))
    advancedtest = advancedvectorizer.transform(testheadlines)
    preds2 = advancedmodel.predict(advancedtest)
    decision = np.sum(preds2)/len(preds2)
    if(decision > 0.5):
        price = "Increase"
    else:
        price = "Decrease"
    return articles[:3], links[:3], price
