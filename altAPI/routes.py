from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse, Namespace
from binance.client import Client
from newsapi import NewsApiClient
from keys import *

api = Namespace("altapi")

# BINANCE API ROUTES

client = Client(API_KEY_BINANCE, API_SECRET_BINANCE)
newsapi = NewsApiClient(api_key=API_KEY_NEWS)


@api.route("/getsymbolinfo")
class GetSymbolInfo(Resource):
    def put(self):
        parser = binance_parser()
        args = parser.parse_args()
        symbol = args["symbol"]
        symbol_info = client.get_symbol_ticker(symbol=symbol)
        return symbol_info


@api.route("/twodaykline")
class TwoDayKline(Resource):
    def put(self):
        parser = binance_parser()
        args = parser.parse_args()
        symbol = args["symbol"]
        exchange_time = client.get_server_time()
        two_days_back = exchange_time["serverTime"] - 172800000
        klines = client.get_klines(
            symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, startTime=two_days_back)
        return klines


@api.route("/getallsymbols")  # Get all available tickers from binance
class GetAllSymbols(Resource):
    def get(self):
        all_symbols = client.get_all_tickers()
        return all_symbols


# NEWS API ROUTES
@api.route("/topstories")
class GetTopStories(Resource):
    def get(self):  # Need to use time but configure date as specified below
        return newsapi.get_everything(q='bitcoin',
                                      from_param='2019-09-01',
                                      to='2019-09-18',
                                      language='en',
                                      sort_by='relevancy',
                                      page=2)


# PARSER

def binance_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("symbol", required=True)
    return parser
