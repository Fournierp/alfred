from flask import Flask
from flask import render_template
import urllib.request
import json
import os

from pipeline import cleaning, sentence_segmenting, speech_to_text
from stock import code, parse, get_advice

# export FLASK_DEBUG = 1

app = Flask(__name__)
FOLDER = os.path.join('static', 'photo')
app.config['UPLOAD_FOLDER'] = FOLDER

with open('api_key.json') as f:
    data = json.load(f)
    api_key = data["api_key"]

@app.route('/')
def home():
    plot = os.path.join(FOLDER, 'fdabb11c9bf59e72dcb7fad3135af9cf1f8a9915db950f04ca8c8a81be4ec76b.gif')
    return render_template('home.html', path=plot)


@app.route('/stock')
def display():
    # order_en = speech_to_text()
    order_en = "Alfred, buy a hundred American Airlines Group Inc stock"
    # order_en = "hello "
    processed = cleaning(order_en)
    company, number, action = sentence_segmenting(processed)
    print(company, number, action)

    if(not company):
        plot = os.path.join(FOLDER, '33bd129cfdda664095629a3fa170a797ae66cbde05b5f864358586e735d4db33.gif')
        return render_template('hello.html', path=plot, company=None, number=None, action=None)
    else:
        company_code = code(company)
        print(company, api_key)
        contents = urllib.request.urlopen("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + company_code + "&apikey=" + api_key).read()
        plot = parse(contents, FOLDER)

        articles, links, price = get_advice("company")
        if(articles):
            return render_template('hello.html', path=plot, company=company, number=number, action=action, articles0 = articles[0][0], articles1 = articles[1][0], articles2 = articles[2][0], links0 = links[0], links1 = links[1], links2 = links[2], price =price)
        else:
            return render_template('hello.html', path=plot, company=company, number=number, action=action)
