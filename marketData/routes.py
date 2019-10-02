from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse, Namespace
from binance.client import Client
from newsapi import NewsApiClient
from keys import API_KEY_BINANCE, API_SECRET_BINANCE, API_KEY_NEWS
from datetime import datetime, timedelta, date

api = Namespace("marketdata")

# BINANCE API ROUTES

client = Client(API_KEY_BINANCE, API_SECRET_BINANCE)
newsapi = NewsApiClient(api_key=API_KEY_NEWS)


@api.route("/getsymbolinfo")
class GetSymbolInfo(Resource):
    def put(self):
        parser = binance_parser()
        args = parser.parse_args()
        return client.get_symbol_ticker(symbol=args["symbol"])


@api.route("/twodaykline")
class TwoDayKline(Resource):
    def put(self):
        parser = binance_parser()
        args = parser.parse_args()
        exchange_time = client.get_server_time()
        two_days_back = exchange_time["serverTime"] - 172800000
        return client.get_klines(
            symbol=args["symbol"],
            interval=Client.KLINE_INTERVAL_1HOUR,
            startTime=two_days_back)


@api.route("/getallsymbols")  # Get all available tickers from binance
class GetAllSymbols(Resource):
    def get(self):
        return client.get_all_tickers()


# NEWS API ROUTES
@api.route("/topstories")
class GetTopStories(Resource):
    def get(self):  # Need to use time but configure date as specified below
        return newsapi.get_everything(q='bitcoin',
                                      from_param=(datetime.now().date(
                                      ) - timedelta(days=7)).isoformat(),
                                      to=datetime.now().date().isoformat(),
                                      language='en',
                                      sort_by='relevancy',
                                      page=2)


# PARSER

def binance_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("symbol", required=True)
    return parser
