# from pymongo import MongoClient
# import datetime
# from mongoengine import *
# from flask import Flask, request, jsonify
# from flask_restplus import Api, Resource, reqparse
# from binance.client import Client
# from flask_cors import CORS
# import dateparser
# import time
# from keys import *
# from classSchemas import *


# # Parsers Init


# def login_page_parser():
#     parser = reqparse.RequestParser()
#     parser.add_argument("user_name",
#                         required=True,
#                         help="Create User Arg Parser")
#     parser.add_argument("password",
#                         required=True,
#                         help="Password Arg Parser")
#     parser.add_argument("new_password",
#                         required=False,
#                         help="New Password Arg Parser")
#     return parser


# def update_bitcoin_parser():
#     parser = reqparse.RequestParser()
#     parser.add_argument("user_name", required=True)
#     parser.add_argument("bitcoin")
#     return parser


# def trade_page_purchase_parser():
#     parser = reqparse.RequestParser()
#     parser.add_argument("user", required=True)
#     parser.add_argument("symbol",
#                         required=True)
#     parser.add_argument("cost_per_unit")
#     parser.add_argument("units_purchased")
#     return parser

# # # Sale Lot Example
# # sale_lots = [
# #     {
# #         index: "2019-09-10T18:49:43.583000",

# #         value: 6,

# #         saleLotInfo:
# #             [
# #                 {
# #                 cost_per_unit: 0.01781,
# #                 purchase_date_time: "2019-09-10T18:49:43.583000",
# #                 units_purchased: 9
# #                 }
# #             ]
# #     ]


# def trade_page_sale_parser():
#     parser = reqparse.RequestParser()
#     parser.add_argument("user", required=True)
#     parser.add_argument("symbol",
#                         required=True)
#     parser.add_argument("share_price")
#     parser.add_argument("trade_value_calc")
#     parser.add_argument("total_shares_being_sold")
#     parser.add_argument("sale_lots")
#     return parser


# # @api.route("/getsymbolpurchaselots/<user>/<symbol>")
# # class get_all_symbol_purchase_lots(Resource):
# #     def get(self, user, symbol):
# #         user_finder = Users.objects(user_name=user).first()
# #         holdings_finder = user_finder.holdings.filter(symbol=symbol)
# #         serialized_holding = [purchase_lot.serializer_test()
# #                               for purchase_lot in holdings_finder]
# #         purchase_lot_finder = serialized_holding[0]["purchase_lots"]
# #         return [lot.serializer_purchase_lots() for lot in purchase_lot_finder]
