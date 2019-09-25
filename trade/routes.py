from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from .controller import *

api = Namespace("trade")

# ROUTES

# Purchase Security
@api.route('/buycrypto')
class PurchaseCrypto(Resource):
    @jwt_required
    def put(self):
        parser = trade_page_parser()
        args = parser.parse_args()
        user_id = get_jwt_identity()
        return purchase_crypto(user_id,
                               symbol=args['symbol'],
                               purchase_price=float(args['share_price']),
                               units_purchased=float(args['total_shares']))

# Sell Security
@api.route('/sellcrypto')
class SellCrypto(Resource):
    @jwt_required
    def put(self):
        parser = trade_page_parser()
        args = parser.parse_args()
        user_id = get_jwt_identity()
        return sell_crypto(user_id,
                           symbol=args['symbol'],
                           share_price=args['share_price'],
                           trade_value_calc=args['trade_value_calc'],
                           total_shares_being_sold=args['total_shares'],
                           sale_lots=args['sale_lots'])


# Get User Purchase Lots for Single Symbol
@api.route("/getsymbolpurchaselots")
class GetAllSymbolPurchaseLots(Resource):
    @jwt_required
    def put(self):
        parser = trade_page_parser()
        args = parser.parse_args()
        user_id = get_jwt_identity()
        return get_all_symbol_purchase_lots(user_id,
                                            symbol=args["symbol"])

# Get All Symbols in Holdings
@api.route("/getallsymbolholdings")
class GetAllSymbolHoldings(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        return get_all_symbol_holdings(user_id)


# PARSERS


def trade_page_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("symbol",
                        required=True)
    parser.add_argument("share_price", type=float)
    parser.add_argument("total_shares", type=float)
    parser.add_argument("trade_value_calc", type=float)
    parser.add_argument("sale_lots", type=dict, action="append")
    return parser
