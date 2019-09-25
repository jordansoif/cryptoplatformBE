from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse, Namespace
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from .controller import *

api = Namespace("accountinfo")

# HOLDINGS PAGE ROUTES ONLY


# NEEDS COMPLETE OVERHAUL
# Get All Holdings
@api.route("/getallholdings")
class GetAllHoldings(Resource):
    @jwt_required
    def get(self):
        new_puchase_lot = Purchase_Lots()
        new_puchase_lot.save()
        return "created"

# REALIZED GAIN LOSS PAGE ONLY

# Get All Realized from User
@api.route("/getallrealized")
class GetAllRealized(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        return get_all_realized(user_id)


# FUND ACCOUNT PAGE ROUTES

# Get User bitcoin
@api.route("/getuserbitcoin")
class GetUserBitcoin(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        user_finder = Users.objects(id=user_id).first()
        return user_finder.bitcoin

# Update User bitcoin
@api.route("/updatebitcoin")
class UpdateBitcoin(Resource):
    @jwt_required
    def put(self):
        parser = update_bitcoin_parser()
        args = parser.parse_args()
        user_id = get_jwt_identity()
        return update_bitcoin(user_id, bitcoin=args['bitcoin'])


# PARSERS

def update_bitcoin_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("bitcoin")
    return parser


def get_user_symbol_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("user", required=True)
    parser.add_argument("symbol")
    return parser