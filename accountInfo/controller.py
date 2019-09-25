from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse
from user.model import *

# NEEDS COMPLETE OVERHAUL
# Get All Holdings


def get_all_holdings(user_id):
    user_finder = Users.objects(id=user_id).first()
    holdings_finder = user_finder.holdings
    return [holding.serializer_holdings() for holding in holdings_finder]


# Get All Realized from User
def get_all_realized(user_id):
    user_finder = Users.objects(id=user_id).first()
    realized_finder = user_finder.realized_positions
    return [realized.serializer_realized_gain_loss_display() for realized in realized_finder]


# Update User bitcoin
def update_bitcoin(user_id, bitcoin):
    float_bitcoin = float(bitcoin)
    user_finder = Users.objects(id=user_id).first()
    current_bitcoin = user_finder.bitcoin
    if float_bitcoin:
        user_finder.update(set__bitcoin=(current_bitcoin + float_bitcoin))
        user_finder.save()
        return "Bitcoin has been updated."
    return "Bitcoin was not updated."
