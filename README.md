# Alfred

## :trophy: Code.Jam(2018): Patter Recognition :trophy:

The implementation of efficient Sentiment Analysis models used for Stock Prediction earned me the Second Position in the Natural Language Processing category at a Machine Learning Hackathon at McGill University.

## Introduction

Alfred is a web app designed with Plotly's Dashboard tool. This appealing web-interface for will be your personal Virtual Assistant for your Stock Market Investments. From the visualization of recent stock price variations for any of the current Top 100 NASDAQ companies, to recent articles about these companies, you can explore many sources of information to make accurate decisions for your next trades.

## Installation

Firstly, ensure that you have pip install. In which case follow these steps using the command line:

```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

Then install the required libraries listed in the requirements.txt
```
pip install -r requirements.txt
```

## Usage Example
```
python index.py
```

## Release history

* 2.0
    * Dash Proof of Concept: web-interface using Dash, visualizations of stock prices and articles about a company.

* 1.0
    * Codejam Submission: web-interface using Flask, language Recognition to record stock trade requests, logistic regression Sentiment Analysis on headlines.


## Built With

* [Dash](https://github.com/plotly/dash/) Analytical Web Apps for Python
* [alphavantage](https://www.alphavantage.co/) Realtime and historical stock data
* [newsapi](https://newsapi.org/) Search worldwide news with code


## Authors

* **Paul Fournier** - *Initial work* - [Fournierp](https://github.com/Fournierp)


## License

This project is licensed under the Apache License - see the LICENSE.md file for details
