from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse
from mongoengine.queryset.visitor import Q
from user.model import Users , Purchase_Lots, Realized_Positions


# Get User Purchase Lots for Single Symbol
def get_all_symbol_purchase_lots(user_id, symbol):
    user_only_purchase_lots = Purchase_Lots.objects(
        symbol=symbol, user_owner=user_id).all()
    return [purchase_lot.serializer_purchase_lots()
            for purchase_lot in user_only_purchase_lots]


# Get All Symbols in Holdings
def get_all_symbol_holdings(user_id):
    purchase_lots = Purchase_Lots.objects(user_owner=user_id).all()
    return [purchase_lot.serializer_purchase_lots()
            for purchase_lot in purchase_lots]


# Purchase Security
def purchase_crypto(user_id, symbol, purchase_price, units_purchased):
    # Create new purchase lots
    new_purchase_lot = Purchase_Lots(user_owner=user_id,
                                     symbol=symbol,
                                     units_purchased=units_purchased,
                                     cost_per_unit=purchase_price)
    new_purchase_lot.save()
    # Bitcoin adjustment
    user = Users.objects(id=user_id).first()
    new_bitcoin = user["bitcoin"]-(purchase_price*units_purchased)
    user.update(set__bitcoin=new_bitcoin)
    user.save()
    return "Crypto successfully purchased."


# Sell Security
def sell_crypto(user_id, symbol, share_price, trade_value_calc, total_shares_being_sold, sale_lots):
    # Adjust puchase lots and create new realized positions
    for lots in sale_lots:  # loop over sale_lots to find matching purchase lots and update them
        lot_object = Purchase_Lots.objects(
            _id=ObjectId(lots["saleLotInfo"]["id"]))
        new_units_purchased = (
            lot_object[0]['units_purchased'] - lots["value"])
        lot_object.update(units_purchased=new_units_purchased)
        new_realized_position = Realized_Positions(
            user_owner=user_id,
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
        new_realized_position.save()
    # Delete function for now empty purchase lots
    # Needs updating, Do not delete data, add an indicator for if lot is now empty
    user_only_purchase_lots.filter(units_purchased=0).delete()
    # User bitcoin adjustment
    user = Users.objects(id=user_id)
    new_bitcoin = user["bitcoin"] + trade_value_calc
    user.update(set__bitcoin=new_bitcoin)
    user.save()
    return "Action completed"
