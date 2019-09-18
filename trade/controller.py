from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse
from user.model import *


# Get User Purchase Lots for Single Symbol
def get_all_symbol_purchase_lots(user_id, symbol):
    user_finder = Users.objects(id=user_id).first()
    holdings_finder = user_finder.holdings.filter(symbol=symbol)
    serialized_holding = [purchase_lot.serializer_test()
                          for purchase_lot in holdings_finder]
    purchase_lot_finder = serialized_holding[0]["purchase_lots"]
    return purchase_lot_finder


# Get All Symbols in Holdings
def get_all_symbol_holdings(user_id):
    user_finder = Users.objects(id=user_id).first()
    holdings_finder = user_finder.holdings
    return [holding.serializer_holdings() for holding in holdings_finder]


# Purchase Security
def purchase_crypto(user_id, symbol, purchase_price, units_purchased):
    user_finder = Users.objects(id=user_id).first()
    symbol_finder = user_finder.holdings.filter(symbol=symbol).first()
    current_bitcoin = user_finder.bitcoin
    if symbol_finder == None:
        add_new_lot_no_holding = Purchase_Lots(
            units_purchased=units_purchased, cost_per_unit=purchase_price)
        new_holding = Holdings(
            symbol=symbol, units_held=units_purchased, average_cost_per_unit=purchase_price,)
        new_holding.purchase_lots.append(add_new_lot_no_holding)
        user_finder.holdings.append(new_holding)
        user_finder.update(set__bitcoin=(
            current_bitcoin-(purchase_price*units_purchased)))
        user_finder.save()
        return "New Holding and New Lot"
    if symbol_finder:
        current_units_held = symbol_finder['units_held']
        current_average_cost_per_unit = symbol_finder['average_cost_per_unit']
        new_units_held = current_units_held + units_purchased
        new_average_cost_per_unit = ((current_units_held/new_units_held)*current_average_cost_per_unit) + (
            (units_purchased/new_units_held)*purchase_price)
        symbol_finder.units_held = new_units_held
        symbol_finder.average_cost_per_unit = new_average_cost_per_unit
        add_new_lot = Purchase_Lots(
            units_purchased=units_purchased, cost_per_unit=purchase_price)
        symbol_finder.purchase_lots.append(add_new_lot)
        user_finder.update(set__bitcoin=(
            current_bitcoin-(purchase_price*units_purchased)))
        user_finder.save()
        return "New Lot Only"
    else:
        return "Security was not purchased."


# Sell Security
def sell_crypto(user_id, symbol, share_price, trade_value_calc, total_shares_being_sold, sale_lots):
    # Find user # THIS WILL CHANGE TO USER ID
    user_finder = Users.objects(id=user_id).first()
    holdings_finder = user_finder.holdings.filter(
        symbol=symbol)  # Find symbol being traded
    # Purchase_lot adjustment
    # Find tax lots for the holding
    purchase_lots_finder = holdings_finder[0]['purchase_lots']
    for lots in sale_lots:  # loop over sale_lots to find matching purchase lots and update them
        lot_finder = purchase_lots_finder.filter(
            _id=ObjectId(lots["saleLotInfo"]["id"]))
        if lot_finder:
            found_lot_units_purchased = lot_finder[0]['units_purchased']
            lot_finder.update(
                units_purchased=found_lot_units_purchased - lots["value"])
    # Delete function for now empty purchase lots
    purchase_lots_finder.filter(units_purchased=0).delete()
    # Holdings adjustment
    holdings_finder.update(units_held=(
        holdings_finder[0]["units_held"]-total_shares_being_sold))
    if purchase_lots_finder.count() == 0:  # delete a holding if it no longer has purchase_lots, this means you longer hold any units in the holding
        holdings_finder.delete()
        # make a formula to adjust the avg_cost_per_unit
    # Realized Positions adjustment
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
