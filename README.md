# Alfred

![Demo](demo_video.gif)

## :trophy: Code.Jam(2018): Patter Recognition :trophy:

The implementation of efficient Sentiment Analysis models used for Stock Prediction earned me the Second Position in the Natural Language Processing category at a Machine Learning Hackathon at McGill University.

## Introduction

Alfred is a web app designed with Streamlit. This web-interface serves as a personal virtual assistant to help you explore information related to Stock Market Investments. From the visualization of recent stock price variations for any of the current S&P 500 companies, to recent articles about these companies, you can explore various sources of information. 

**Note: This tool is for informational and educational purposes only. Do not rely on this model to make investment decisions. Always consult with a qualified financial advisor before making any investments.**

**Warning: yfinance may be subject to rate limits. Excessive requests in a short period may result in temporary blocks or degraded performance.**

## Installation

Firstly, ensure that you have [uv](https://docs.astral.sh/uv/getting-started/installation/) installed.

Install the required packages.
```
uv sync
```

## Requirements

Create an account on [newsapi](https://newsapi.org/) to get an API key. Then add it to the file *api_key.json*.

## Usage Example
```
uv run streamlit run app.py
```

## Release history

* 4.0
   * Use uv

* 3.0
   * Streamlit POC - web-interface, visualizations of stock prices and articles about a company.

* 2.0
    * Dash Proof of Concept: web-interface using Dash, visualizations of stock prices and articles about a company.

* 1.0
    * Codejam Submission: web-interface using Flask, language Recognition to record stock trade requests, logistic regression Sentiment Analysis on headlines.


## Built With

* [Streamlit](https://www.streamlit.io/) The fastest way to build and share data apps
* [newsapi](https://newsapi.org/) Search worldwide news with code

## Contribute

To build on this tool, please fork it and make pull requests. Or simply send me some suggestions !


## Authors

* **Paul Fournier** - *Initial work* - [Fournierp](https://github.com/Fournierp)


## License

This project is licensed under the Apache License - see the LICENSE.md file for details
