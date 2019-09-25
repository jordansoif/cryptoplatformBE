from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse
from user.model import *


# Get User Purchase Lots for Single Symbol
def get_all_symbol_purchase_lots(user_id, symbol):
    purchase_lot_finder = Purchase_Lots.objects(symbol=symbol).all()
    user_only_purchase_lots = purchase_lot_finder.filter(user_owner=user_id)
    serialized_purchase_lots = [purchase_lot.serializer_purchase_lots()
                                for purchase_lot in user_only_purchase_lots]
    return serialized_purchase_lots


# Get All Symbols in Holdings
def get_all_symbol_holdings(user_id):
    purchase_lot_finder = Purchase_Lots.objects(user_owner=user_id).all()
    user_only_purchase_lots = [purchase_lot.serializer_purchase_lots()
                               for purchase_lot in purchase_lot_finder]
    return user_only_purchase_lots


# Purchase Security
def purchase_crypto(user_id, symbol, purchase_price, units_purchased):
    # Create new purchase lots
    new_purchase_lot = Purchase_Lots(user_owner=user_id,
                                     symbol=symbol,
                                     units_purchased=units_purchased,
                                     cost_per_unit=purchase_price)
    new_purchase_lot.save()
    # Bitcoin adjustment
    user_finder = Users.objects(id=user_id).first()
    user_finder.update(set__bitcoin=(
        user_finder["bitcoin"]-(purchase_price*units_purchased)))
    user_finder.save()
    return "Crypto successfully purchased."


# Sell Security
def sell_crypto(user_id, symbol, share_price, trade_value_calc, total_shares_being_sold, sale_lots):
    # Adjust puchase lots, delete is lot no longer has any holdings
    purchase_lot_finder = Purchase_Lots.objects(symbol=symbol).all()
    user_only_purchase_lots = purchase_lot_finder.filter(user_owner=user_id)
    for lots in sale_lots:  # loop over sale_lots to find matching purchase lots and update them
        lot_finder = user_only_purchase_lots.filter(
            _id=ObjectId(lots["saleLotInfo"]["id"]))
        if lot_finder:
            found_lot_units_purchased = lot_finder[0]['units_purchased']
            lot_finder.update(
                units_purchased=found_lot_units_purchased - lots["value"])
    # Delete function for now empty purchase lots
    user_only_purchase_lots.filter(units_purchased=0).delete()
    # Realized Positions adjustment
    user_finder = Users.objects(id=user_id).first()
    for lots in sale_lots:
        new_realized_position = Realized_Positions(
            symbol=symbol,
            purchase_date_time=lots["saleLotInfo"]["purchase_date_time"],
            sale_date_time=datetime.datetime.now(),
            purchase_price=lots["saleLotInfo"]["cost_per_unit"],
            sale_price=share_price,
            units_sold=lots["value"],
            profit_loss=(
                share_price - lots["saleLotInfo"]["cost_per_unit"])*lots["value"],
            profit_loss_percent=(
                share_price/lots["saleLotInfo"]["cost_per_unit"])/100
        )
        user_finder.realized_positions.append(new_realized_position)
    # Users adjustment
    user_finder.update(bitcoin=user_finder.bitcoin + trade_value_calc)
    user_finder.save()
    return "Action completed"


# # Sell Security
# def sell_crypto(user_id, symbol, share_price, trade_value_calc, total_shares_being_sold, sale_lots):
#     user_finder = Users.objects(id=user_id).first()
#     holdings_finder = user_finder.holdings.filter(
#         symbol=symbol)  # Find symbol being traded
#     # Purchase_lot adjustment
#     # Find tax lots for the holding
#     purchase_lots_finder = holdings_finder[0]['purchase_lots']
#     for lots in sale_lots:  # loop over sale_lots to find matching purchase lots and update them
#         lot_finder = purchase_lots_finder.filter(
#             _id=ObjectId(lots["saleLotInfo"]["id"]))
#         if lot_finder:
#             found_lot_units_purchased = lot_finder[0]['units_purchased']
#             lot_finder.update(
#                 units_purchased=found_lot_units_purchased - lots["value"])
#     # Delete function for now empty purchase lots
#     purchase_lots_finder.filter(units_purchased=0).delete()
#     # Holdings adjustment
#     holdings_finder.update(units_held=(
#         holdings_finder[0]["units_held"]-total_shares_being_sold))
#     if purchase_lots_finder.count() == 0:  # delete a holding if it no longer has purchase_lots, this means you longer hold any units in the holding
#         holdings_finder.delete()
#         # make a formula to adjust the avg_cost_per_unit
#     # Realized Positions adjustment
#     for lots in sale_lots:
#         new_realized_position = Realized_Positions(
#             symbol=symbol,
#             purchase_date_time=lots["saleLotInfo"]["purchase_date_time"],
#             sale_date_time=datetime.datetime.now(),
#             purchase_price=lots["saleLotInfo"]["cost_per_unit"],
#             sale_price=share_price,
#             units_sold=lots["value"],
#             profit_loss=(
#                 share_price - lots["saleLotInfo"]["cost_per_unit"])*lots["value"],
#             profit_loss_percent=(
#                 share_price/lots["saleLotInfo"]["cost_per_unit"])/100
#         )
#         user_finder.realized_positions.append(new_realized_position)
#     # Users adjustment
#     user_finder.update(bitcoin=user_finder.bitcoin + trade_value_calc)
#     user_finder.save()
#     return "Action completed"
