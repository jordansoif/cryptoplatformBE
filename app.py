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
# from classSchemas import *
# from parsers import *
# from app import *

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
    parser.add_argument("sale_lots", action="append")
    return parser


# HOLDINGS PAGE ROUTES

# Get All Holdings
@api.route("/getallholdings/<user>")
class get_all_holdings(Resource):
    def get(self, user):
        user_finder = Users.objects(user_name=user).first()
        holdings_finder = user_finder.holdings
        return [holding.serializer_holdings() for holding in holdings_finder]
        # BELOW WILL HELP A BUNCH, FOUND IN MONGO DOCS
        # Prints out the names of all the users in the database
        # for user in User.objects:
        #     print user.name

# Get All Symbols in Holdings
@api.route("/getallsymbolholdings/<user>")
class get_all_symbol_holdings(Resource):
    def get(self, user):
        user_finder = Users.objects(user_name=user).first()
        holdings_finder = user_finder.holdings
        return [holding.serializer_symbol_only() for holding in holdings_finder]

# FUND ACCOUNT PAGE ROUTES

# Get User bitcoin
@api.route("/getuserbitcoin")
class get_user(Resource):
    @jwt_required
    def get(self):
        current_user = get_jwt_identity() #this is returning an id
        user_finder = Users.objects(id=current_user).first()
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
            add_new_lot_no_holding = Purchase_Lots()
            add_new_lot_no_holding.units_purchased = new_units_purchased
            add_new_lot_no_holding.cost_per_unit = new_purchase_price
            new_holding = Holdings()
            new_holding.symbol = new_symbol
            new_holding.units_held = new_units_purchased
            new_holding.average_cost_per_unit = new_purchase_price
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
            # exchange_time = client.get_server_time()
            # exchange_time_value = exchange_time["serverTime"]
            # FIX ABOVE LATER IF YOU WANT, DEFAULT SHOULD WORK
            add_new_lot = Purchase_Lots()
            add_new_lot.units_purchased = new_units_purchased
            add_new_lot.cost_per_unit = new_purchase_price
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
        arg_user = args['user'] #Making payload info usable
        arg_symbol = args['symbol']
        arg_share_price = args['share_price']
        arg_trade_value_calc = args['trade_value_calc']
        arg_total_shares_being_sold = args['total_shares_being_sold']
        arg_sale_lots = args['sale_lots']
        return arg_sale_lots
        user_finder = Users.objects(user_name=arg_user).first() #Find user
        holdings_finder = user_finder.holdings.filter(symbol=arg_symbol) #Find symbol being traded
        purchase_lots_finder = holdings_finder[0]['purchase_lots']  #Find tax lots for the holding
        # purchase_to_sale_lot_filter = [purchase_lots_finder.filter(purchase_date_time = lots.purchase_date_time).update(units_purchased= (self.units_purchased - lots.units_purchased)) for lots in arg_sale_lots]  # Loop arg_sale_lots to find the matching purchase lots
        # TEST BELOW
        purchase_to_sale_lot_filter = [purchase_lots_finder.filter(units_purchased = lots.units_purchased) for lots in arg_sale_lots]  # Loop arg_sale_lots to find the matching purchase lots
        # TEST ABOVE   +++ .update(units_purchased= (self.units_purchased - lots.units_purchased)
        # purchase_lot_sale_update= purchase_to_sale_lot_filter.filter(units_purchased=0).delete() # Delete function for now empty purchase lots
        # purchase_lot_sale_update.save()
        
        # def purchase_lot_sale_update(self, sale_lot_filter):
        #     if self.purchase_date_time == sale_lot_filter.purchase_date_time:
        #         update_units_purchased = self.units_purchased - sale_lot_filter.units_purchased

        

        # purchase_lot_sale_update.filter(units_purchased=0).delete() # Delete function for now empty purchase lots

        #Purchase Lots: Loop over arg_sale_lots.saleLotInfo to filter purchase lots for potential matches of purchase dates
            #If found, subtract arg_sale_lots.salesLot.value from matched purchase lot
                #if units_purchase now == 0, delete the lot
        #Holdings: subtract arg_total_shares_being_sold from holdings.units_held
            #make a formula to adjust the avg_cost_per_unit
                #if purchase_lots.length = 0, delete the holding from user
        #Realized Positions: create and add a new realized position for each sale lot
            #build calculations for the remaining fields in realized_pos that arent in args
        #Users: add the arg_trade_calc_value to bitcoin balance
            #remove holding.symbol if no more units are held
                #add realized positions as mentioned above



        # symbol_finder = user_finder.holdings.objects(
        #     symbol=new_symbol).first()
        # lot_finder = symbol_finder.objects(cost_per_unit=new_unit_cost).first()
        # lot_purchase_date_time = lot_finder.purchase_date_time
        # lot_cost_per_unit = lot_finder.cost_per_unit
        # if request.method == "PUT":
        #     add_realized_position = Realized_Positions(
        #         new_symbol, lot_purchase_date_time, sale_date_time, lot_cost_per_unit, new_unit_cost, new_units_sold)
        #     user_finder.realized_positions.append(add_realized_position)
        #     user_finder.save()
        # if new_units_sold >= lot_finder.units_purchase:
        #     symbol_finder.objects(cost_per_unit=new_unit_cost).first().delete()
        #     symbol_finder.save()
        # else:
        #     return "Security was not sold."


# Get All Symbols in Holdings
@api.route("/getallsymbolholdings/<user>")
class get_all_symbol_holdings(Resource):
    def get(self, user):
        user_finder = Users.objects(user_name=user).first()
        holdings_finder = user_finder.holdings
        return [holding.serializer_symbol_only() for holding in holdings_finder]


# Get User Purchase Lots for Single Symbol
@api.route("/getsymbolpurchaselots/<user>/<symbol>")
class get_all_symbol_purchase_lots(Resource):
    def get(self, user, symbol):
        user_finder = Users.objects(user_name=user).first()
        holdings_finder = user_finder.holdings.filter(symbol=symbol)
        serialized_holding = [purchase_lot.serializer_test()
                              for purchase_lot in holdings_finder]
        purchase_lot_finder = serialized_holding[0]["purchase_lots"]
        return [lot.serializer_purchase_lots() for lot in purchase_lot_finder]


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


@api.route("/getallsymbols")
class get_all_symbols(Resource):
    def get(self):
        all_symbols = client.get_all_tickers()
        return all_symbols

# Schema Setup


if __name__ == '__main__':
    app.run(debug=True)
