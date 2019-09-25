from mongoengine import *
import datetime
from bson.objectid import ObjectId
from binance.client import Client
from keys import *

client = Client(API_KEY_BINANCE, API_SECRET_BINANCE)

# Page needs refactoring, purchase_lots will be made independant  (possibly realized positions as well)
# Holdings will be removed


class Purchase_Lots(EmbeddedDocument):
    _id = ObjectIdField(required=True)
    purchase_date_time = DateTimeField(default=datetime.datetime.now())
    units_purchased = FloatField(default=0.00)
    cost_per_unit = FloatField(default=0.00)

    def serializer_purchase_lots(self):
        return{
            "id": str(self._id),
            "purchase_date_time": self.purchase_date_time.isoformat(),
            "units_purchased": self.units_purchased,
            "cost_per_unit": self.cost_per_unit
        }


class Holdings(EmbeddedDocument):
    symbol = StringField(default="")
    units_held = FloatField(default=0.00)
    average_cost_per_unit = FloatField(default=0.00)
    purchase_lots = EmbeddedDocumentListField('Purchase_Lots', default=list)

    def serializer_test(self):
        return{
            "symbol": self.symbol,
            "units_held": self.units_held,
            "average_cost_per_unit": self.average_cost_per_unit,
            "purchase_lots": [lots.serializer_purchase_lots() for lots in self.purchase_lots]
        }

    def serializer_symbol_only(self):
        return{"symbol": self.symbol}

    def serializer_holdings(self):
        current_price = float(client.get_symbol_ticker(
            symbol=self.symbol)['price'])
        return{
            "symbol": self.symbol,
            "units_held": self.units_held,
            "average_cost_per_unit": self.average_cost_per_unit,
            "current_price": current_price,
            "position_value": self.units_held * current_price,
            "total_cost_basis": self.units_held * self.average_cost_per_unit,
            "profit_or_loss": (current_price - self.average_cost_per_unit) * self.units_held
        }


class Realized_Positions(EmbeddedDocument):
    symbol = StringField(default="")
    purchase_date_time = DateTimeField(default=datetime.datetime.now())
    sale_date_time = DateTimeField(default=datetime.datetime.now())
    purchase_price = FloatField(default=0.00)
    sale_price = FloatField(default=0.00)
    units_sold = FloatField(default=0.00)
    profit_loss = FloatField(default=0.00)
    profit_loss_percent = FloatField(default=0.00)

    def serializer_realized_gain_loss_display(self):
        return{
            "symbol": self.symbol,
            "purchase_date_time": self.purchase_date_time.isoformat(),
            "sale_date_time": self.sale_date_time.isoformat(),
            "purchase_price": self.purchase_price,
            "sale_price": self.sale_price,
            "units_sold": self.units_sold,
            "profit_loss": self.profit_loss,
            "profit_loss_percent": self.profit_loss_percent
        }


class Users(Document):
    user_name = StringField(max_length=20)
    password = StringField()
    bitcoin = FloatField(default=0.00)
    holdings = EmbeddedDocumentListField("Holdings", default=list)
    realized_positions = EmbeddedDocumentListField(
        "Realized_Positions", default=list)

    def serializer_authentication(self):
        return{
            "id": str(self.id),
            "user_name": self.user_name,
            "password": self.password,
            "bitcoin": self.bitcoin,
            "holdings": [holding.serializer_test() for holding in self.holdings],
            "realized_postions": [lot.serializer_realized_gain_loss_display() for lot in self.realized_positions]
        }
