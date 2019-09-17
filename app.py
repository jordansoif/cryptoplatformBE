import datetime
from mongoengine import *
from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse
from binance.client import Client
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
import dateparser
import time
from keys import *
from user.model import Users, Holdings, Realized_Positions, Purchase_Lots
from auth import api as auth_api, login_page_parser
from user import api as user_api
from bson.objectid import ObjectId

# Init App
app = Flask(__name__)

config = {
  'ORIGINS': [
    'http://localhost:1234',  # React
    'http://127.0.0.1:1234',  # React
  ],
}

api = Api()
api.init_app(app)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)
api.add_namespace(auth_api, path="/auth")
api.add_namespace(user_api, path="/user")
CORS(app, resources={ r'/*': {'origins': config['ORIGINS']}}, supports_credentials=True)

connect('cryptoplatform')

# Parsers Init

def update_bitcoin_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("user_name", required=True)
    parser.add_argument("bitcoin")
    return parser

def trade_page_purchase_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("user", required=True)
    parser.add_argument("symbol",
                        required=True)
    parser.add_argument("cost_per_unit")
    parser.add_argument("units_purchased")
    return parser

def trade_page_sale_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("user", required=True)
    parser.add_argument("symbol",
                        required=True)
    parser.add_argument("share_price", type=float)
    parser.add_argument("trade_value_calc", type=float)
    parser.add_argument("total_shares_being_sold", type=float)
    parser.add_argument("sale_lots", type=dict, action="append")
    return parser

def get_user_symbol_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("user", required=True)
    parser.add_argument("symbol")
    return parser


# HOLDINGS PAGE ROUTES

# Get All Holdings
@api.route("/getallholdings")
class get_all_holdings(Resource):
    def put(self):
        parser = get_user_symbol_parser()
        args = parser.parse_args()
        user = args["user"]
        user_finder = Users.objects(user_name=user).first()
        holdings_finder = user_finder.holdings
        return [holding.serializer_holdings() for holding in holdings_finder]

# Get All Symbols in Holdings
@api.route("/getallsymbolholdings")
class get_all_symbol_holdings(Resource):
    def put(self):
        parser = get_user_symbol_parser()
        args = parser.parse_args()
        user = args["user"]
        user_finder = Users.objects(user_name=user).first()
        holdings_finder = user_finder.holdings
        return [holding.serializer_holdings() for holding in holdings_finder]


# Get All Realized from User
@api.route("/getallrealized")
class get_all_realized(Resource):
    def put(self):
        parser = get_user_symbol_parser()
        args = parser.parse_args()
        user = args["user"]
        user_finder = Users.objects(user_name=user).first()
        realized_finder = user_finder.realized_positions
        return [realized.serializer_realized_gain_loss_display() for realized in realized_finder]

# FUND ACCOUNT PAGE ROUTES

# Get User bitcoin
@api.route("/getuserbitcoin/<user>")
class get_user(Resource):
    # @jwt_required
    def get(self,user):
        # current_user = get_jwt_identity() #this is returning an id
        # user_finder = Users.objects(id=current_user).first()
        # return user_finder.bitcoin
        user_finder = Users.objects(user_name=user).first()
        return user_finder.bitcoin

# Update User bitcoin
@api.route("/updatebitcoin")
class update_bitcoin(Resource):
    def put(self):
        parser = update_bitcoin_parser()
        args = parser.parse_args()
        user = args['user_name']
        bitcoin = args['bitcoin']
        float_bitcoin = float(bitcoin)
        user_finder = Users.objects(user_name=user).first()
        current_bitcoin = user_finder.bitcoin
        if type(float_bitcoin) == float:
            user_finder.update(set__bitcoin=(current_bitcoin + float_bitcoin))
            user_finder.save()
            return "Bitcoin has been updated."
        return "Bitcoin was not updated."


# TRADE PAGE ROUTES

# Purchase Security
@api.route('/purchasecrypto')
class purchase_crypto(Resource):
    def put(self):
        parser = trade_page_purchase_parser()
        args = parser.parse_args()
        current_user = args['user']
        new_symbol = args['symbol']
        new_purchase_price = float(args['cost_per_unit'])
        new_units_purchased = float(args['units_purchased'])
        user_finder = Users.objects(user_name=current_user).first()
        symbol_finder = user_finder.holdings.filter(symbol=new_symbol).first()
        current_bitcoin = user_finder.bitcoin
        if symbol_finder == None:
            add_new_lot_no_holding = Purchase_Lots(units_purchased = new_units_purchased, cost_per_unit = new_purchase_price)
            new_holding = Holdings(symbol = new_symbol,units_held = new_units_purchased,average_cost_per_unit = new_purchase_price,)
            new_holding.purchase_lots.append(add_new_lot_no_holding)
            user_finder.holdings.append(new_holding)
            user_finder.update(set__bitcoin=(
                current_bitcoin-(new_purchase_price*new_units_purchased)))
            user_finder.save()
            return "New Holding and New Lot"
        if symbol_finder:
            current_units_held = symbol_finder['units_held']
            current_average_cost_per_unit = symbol_finder['average_cost_per_unit']
            new_units_held = current_units_held + new_units_purchased
            new_average_cost_per_unit = ((current_units_held/new_units_held)*current_average_cost_per_unit) + (
                (new_units_purchased/new_units_held)*new_purchase_price)
            symbol_finder.units_held = new_units_held
            symbol_finder.average_cost_per_unit = new_average_cost_per_unit
            add_new_lot = Purchase_Lots(units_purchased = new_units_purchased,cost_per_unit = new_purchase_price)
            symbol_finder.purchase_lots.append(add_new_lot)
            user_finder.update(set__bitcoin=(
                current_bitcoin-(new_purchase_price*new_units_purchased)))
            user_finder.save()
            return "New Lot Only"
        else:
            return "Security was not purchased."


# Sell Security
@api.route('/sellcrypto')
class sell_crypto(Resource):
    def put(self):
        parser = trade_page_sale_parser()
        args = parser.parse_args()
        arg_user = args['user'] #Making payload info usable #THIS NEEDS TO CHANGE TO USER ID
        arg_symbol = args['symbol']
        arg_share_price = args['share_price']
        arg_trade_value_calc = args['trade_value_calc']
        arg_total_shares_being_sold = args['total_shares_being_sold']
        arg_sale_lots = args['sale_lots'] # this now works, returns a list(array) of dicts(objects)
        user_finder = Users.objects(user_name=arg_user).first() #Find user # THIS WILL CHANGE TO USER ID
        holdings_finder = user_finder.holdings.filter(symbol=arg_symbol) #Find symbol being traded
        # Purchase_lot adjustment
        purchase_lots_finder = holdings_finder[0]['purchase_lots']  #Find tax lots for the holding
        for lots in arg_sale_lots: # loop over sale_lots to find matching purchase lots and update them
            lot_finder = purchase_lots_finder.filter(_id = ObjectId(lots["saleLotInfo"]["id"]))
            if lot_finder:
                found_lot_units_purchased = lot_finder[0]['units_purchased']
                lot_finder.update(units_purchased= found_lot_units_purchased - lots["value"])
        purchase_lots_finder.filter(units_purchased=0).delete() # Delete function for now empty purchase lots
        # Holdings adjustment
        holdings_finder.update(units_held=(holdings_finder[0]["units_held"]-arg_total_shares_being_sold))
        if purchase_lots_finder.count() == 0: # delete a holding if it no longer has purchase_lots, this means you longer hold any units in the holding
            holdings_finder.delete()
                    #make a formula to adjust the avg_cost_per_unit
        #Realized Positions adjustment
        for lots in arg_sale_lots:
            new_realized_position = Realized_Positions(
                    symbol = arg_symbol,
                    purchase_date_time = lots["saleLotInfo"]["purchase_date_time"],
                    sale_date_time = datetime.datetime.now(),
                    purchase_price = lots["saleLotInfo"]["cost_per_unit"],
                    sale_price = arg_share_price,
                    units_sold = lots["value"],
                    profit_loss = (arg_share_price - lots["saleLotInfo"]["cost_per_unit"])*lots["value"],
                    profit_loss_percent = (arg_share_price/lots["saleLotInfo"]["cost_per_unit"])/100
            )
            user_finder.realized_positions.append(new_realized_position)
        # Users adjustment
        user_finder.update(bitcoin= user_finder.bitcoin + arg_trade_value_calc)
        # END TEST
        user_finder.save()
        return "Action completed"


# Get User Purchase Lots for Single Symbol
@api.route("/getsymbolpurchaselots")
class get_all_symbol_purchase_lots(Resource):
    def put(self):
        parser = get_user_symbol_parser()
        args = parser.parse_args()
        user = args["user"]
        symbol = args["symbol"]
        user_finder = Users.objects(user_name=user).first()
        holdings_finder = user_finder.holdings.filter(symbol=symbol)
        serialized_holding = [purchase_lot.serializer_test()
                              for purchase_lot in holdings_finder]
        purchase_lot_finder = serialized_holding[0]["purchase_lots"]
        return purchase_lot_finder


# BINANCE API ROUTES

client = Client(API_KEY, API_SECRET)


@api.route("/getsymbolinfo/<symbol>")
class get_symbol_info(Resource):
    def get(self, symbol):
        symbol_info = client.get_symbol_ticker(symbol=symbol)
        return symbol_info


@api.route("/twodaykline/<symbol>")
class two_day_kline(Resource):
    def get(self, symbol):
        exchange_time = client.get_server_time()
        two_days_back = exchange_time["serverTime"] - 172800000
        klines = client.get_klines(
            symbol="BNBBTC", interval=Client.KLINE_INTERVAL_1HOUR, startTime=two_days_back)
        return klines


@api.route("/getallsymbols") #Get all available tickers from binance
class get_all_symbols(Resource):
    def get(self):
        all_symbols = client.get_all_tickers()
        return all_symbols



if __name__ == '__main__':
    app.run(debug=True)
