from mongoengine import *
import datetime
from bson.objectid import ObjectId


class Purchase_Lots(Document):
    user_owner = ReferenceField("Users")
    symbol = StringField()
    purchase_date_time = DateTimeField(default=datetime.datetime.now())
    units_purchased = FloatField(default=0.00)
    cost_per_unit = FloatField(default=0.00)

    def serializer_purchase_lots(self):
        return{
            "id": str(self._id),
            "user_owner": str(self.user_owner),
            "symbol": self.symbol,
            "purchase_date_time": self.purchase_date_time.isoformat(),
            "units_purchased": self.units_purchased,
            "cost_per_unit": self.cost_per_unit
        }


class Realized_Positions(Document):
    user_owner = ReferenceField("Users")
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
            "user_owner": str(self.user_owner),
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

    def serializer_authentication(self):
        return{
            "id": str(self.id),
            "user_name": self.user_name,
            "password": self.password,
            "bitcoin": self.bitcoin
        }
