# from pymongo import MongoClient
# import datetime
# from mongoengine import *
# from flask import Flask, request, jsonify
# from flask_restplus import Api, Resource, reqparse
# from binance.client import Client
# from flask_cors import CORS
# from keys import *
# import dateparser
# import time
# from parsers import *
# from app import *

# # Schema Setup


# class Purchase_Lots(EmbeddedDocument):
#     purchase_date_time = DateTimeField(default=datetime.datetime.now())
#     units_purchased = FloatField(default=0.00)
#     cost_per_unit = FloatField(default=0.00)

#     def serializer_purchase_lots(self):
#         return{
#             "purchase_date_time": self.purchase_date_time.isoformat(),
#             "units_purchased": self.units_purchased,
#             "cost_per_unit": self.cost_per_unit
#         }


# class Holdings(EmbeddedDocument):
#     symbol = StringField(default="")
#     units_held = FloatField(default=0.00)
#     average_cost_per_unit = FloatField(default=0.00)
#     purchase_lots = EmbeddedDocumentListField('Purchase_Lots', default=list)

#     def serializer_test(self):
#         return{
#             "symbol": self.symbol,
#             "units_held": self.units_held,
#             "average_cost_per_unit": self.average_cost_per_unit,
#             "purchase_lots": self.purchase_lots
#         }

#     def serializer_symbol_only(self):
#         return{"symbol": self.symbol}

#     def serializer_holdings(self):
#         current_price = float(client.get_symbol_ticker(
#             symbol=self.symbol)['price'])
#         return{
#             "symbol": self.symbol,
#             "units_held": self.units_held,
#             "average_cost_per_unit": self.average_cost_per_unit,
#             "current_price": current_price,
#             "position_value": self.units_held * current_price,
#             "total_cost_basis": self.units_held * self.average_cost_per_unit,
#             "profit_or_loss": (current_price - self.average_cost_per_unit) * self.units_held
#         }


# class Realized_Positions(EmbeddedDocument):
#     symbol = StringField(default="")
#     purchase_date_time = DateTimeField(default=datetime.datetime.now())
#     sale_date_time = DateTimeField(default=datetime.datetime.now())
#     purchase_price = FloatField(default=0.00)
#     sale_price = FloatField(default=0.00)
#     units_sold = FloatField(default=0.00)
#     profit_loss = FloatField(default=0.00)
#     profit_loss_percent = FloatField(default=0.00)


# class Users(Document):
#     user_name = StringField(max_length=20)
#     password = StringField(max_length=20, default="")
#     bitcoin = FloatField(default=0.00)
#     holdings = EmbeddedDocumentListField("Holdings", default=list)
#     realized_positions = EmbeddedDocumentListField(
#         "Realized_Positions", default=list)
