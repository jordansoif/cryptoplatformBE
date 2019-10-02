from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse
from user.model import Users, Purchase_Lots, Realized_Positions


# Get All Holdings
def get_all_holdings(user_id):
    purchase_lots = Purchase_Lots.objects(
        user_owner=user_id, units_remaining__gt=0).all()
    processed = {}
    for lots in purchase_lots:
        serialized = lots.serializer_holdings_page()
        if lots['symbol'] in processed:
            processed[lots['symbol']
                      ]["units_remaining"] += serialized["units_remaining"]
            processed[lots['symbol']
                      ]["position_value"] += serialized["position_value"]
            processed[lots['symbol']
                      ]["total_cost_basis"] += serialized["total_cost_basis"]
            processed[lots['symbol']
                      ]["profit_loss"] += serialized["profit_loss"]
        else:
            processed[lots['symbol']] = serialized
    return_list = []
    for lot in processed:
        return_list.append(processed[lot])
    return return_list


def get_all_realized(user_id):
    all_realized_for_user = Realized_Positions.objects(
        user_owner=user_id).all()
    return [realized.serializer_realized_gain_loss_display()
            for realized in all_realized_for_user]


# Update User Bitcoin
def update_bitcoin(user_id, bitcoin):
    user = Users.objects(id=user_id).first()
    new_bitcoin = user.bitcoin + float(bitcoin)
    user.update(set__bitcoin=new_bitcoin)
    user.save()
    return "Bitcoin has been updated."
