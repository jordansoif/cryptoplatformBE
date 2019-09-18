from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse, Namespace
from binance.client import Client
from keys import *

api = Namespace("binance")

# BINANCE API ROUTES

client = Client(API_KEY, API_SECRET)


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


# PARSER

def binance_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("symbol", required=True)
    return parser
