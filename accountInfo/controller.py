from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse
from user.model import Users, Purchase_Lots, Realized_Positions

# get all holdings and get all realized need to be fixed


# # Get All Holdings
# def get_all_holdings(user_id):
#     # Create an empty list to be appended to
#     return_list = []
#     # Get a list of all purchase lots for a user by searching purchase lots by their referenceField
#     # user_owner with the user_id received
#     purchase_lots = Purchase_Lots.objects(user_owner=user_id).all()
#     # Formats previous purchase_lots into JSON serializable info that can be manipulated
#     # in the following lines and output to the frontend. removes the unecessary info like
#     # date and user_owner since we already used this information
#     serialized_lots = [lots.serializer_holdings_page()
#                        for lots in purchase_lots]
#     # For loop over the reformatted data to append/update the info that is going to be
#     # output to the frontend via the return_list
#     for lots in serialized_lots:
#         # This querys the return_list to see if an entry has already been created for
#         # a symbol or not. Since multiple purchase lots can be had for a single symbol
#         # and we only want to output 1 object for each symbol, we need to add an entry
#         # if none exists, and update an entry if one does exist
#         list_search_index = find(return_list, "symbol", lots["symbol"])
#         # == -1 means that nothing was found, so we need to append an entry for that
#         # symbol, lots["units_remaining"] != 0 is to make sure we aren't adding
#         # empty (deleted) purchase_lots
#         if list_search_index == -1 and lots["units_remaining"] != 0:
#             return_list.append(lots)
#         # != means that the return_list already has an entry for the symbol in the loop
#         # so we are going to update this entry with additional information from the
#         # lot that is currently in the for loop
#         elif list_search_index != -1:
#          # elif to avoid empty purchase lots being added
#          # The lines below make the update to the current entry for a symbol
#             return_list[list_search_index]["units_remaining"] += lots["units_remaining"]
#             return_list[list_search_index]["position_value"] += lots["position_value"]
#             return_list[list_search_index]["total_cost_basis"] += lots["total_cost_basis"]
#             return_list[list_search_index]["profit_loss"] += lots["profit_loss"]
#     # this returns a JSON serializable list for the front end that includes purchase_lot
#     # information (current holdings) and contains only one entry per symbol so multiple
#     # same symbol entries dont show on the front end when displaying the data
#     return return_list

# Get All Holdings


def get_all_holdings(user_id):
    return_list = []
    purchase_lots = Purchase_Lots.objects(user_owner=user_id).all()
    for lots in purchase_lots:
        serialized_lot = lots.serializer_holdings_page()
        list_search_index = find(
            return_list, "symbol", serialized_lot["symbol"])
        if list_search_index == -1 and serialized_lot["units_remaining"] != 0:
            return_list.append(serialized_lot)
        elif list_search_index != -1:
            return_list[list_search_index]["units_remaining"] += serialized_lot["units_remaining"]
            return_list[list_search_index]["position_value"] += serialized_lot["position_value"]
            return_list[list_search_index]["total_cost_basis"] += serialized_lot["total_cost_basis"]
            return_list[list_search_index]["profit_loss"] += serialized_lot["profit_loss"]
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
