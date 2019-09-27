from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse
from user.model import Users, Purchase_Lots, Realized_Positions

# get all holdings and get all realized need to be fixed


# Get All Holdings
def get_all_holdings(user_id):
    return_list = []
    purchase_lots = Purchase_Lots.objects(user_owner=user_id).all()
    serialized_lots = [lots.serializer_holdings_page()
                       for lots in purchase_lots]
    for lots in serialized_lots:
        list_search_index = find(return_list, "symbol", lots["symbol"])
        if list_search_index == -1 and lots["units_remaining"] != 0:
            return_list.append(lots)
        elif list_search_index != -1:
         # elif to avoid empty purchase lots being added
            return_list[list_search_index]["units_remaining"] += lots["units_remaining"]
            return_list[list_search_index]["position_value"] += lots["position_value"]
            return_list[list_search_index]["total_cost_basis"] += lots["total_cost_basis"]
            return_list[list_search_index]["profit_loss"] += lots["profit_loss"]
    return return_list


def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1


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
