from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse
from user.model import Users, Purchase_Lots, Realized_Positions

# get all holdings and get all realized need to be dixed


# Get All Holdings
def get_all_holdings(user_id):
    purchase_lots = Purchase_Lots.objects(user_owner=user_id).all()
    return "Need to Fix"
    # for lots in purchase_lots:

    # return [purchase_lot.serializer_purchase_lots()
    #         for purchase_lot in purchase_lot_finder]

    # Get All Realized from User


def get_all_realized(user_id):
    user = Users.objects(id=user_id).first()
    return [realized.serializer_realized_gain_loss_display()
            for realized in user.realized_positions]


# Update User Bitcoin
def update_bitcoin(user_id, bitcoin):
    user = Users.objects(id=user_id).first()
    new_bitcoin = user.bitcoin + float(bitcoin)
    user.update(set__bitcoin=new_bitcoin)
    user.save()
    return "Bitcoin has been updated."
