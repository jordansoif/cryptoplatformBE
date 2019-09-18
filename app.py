from mongoengine import *
from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from accountInfo import api as account_info_api
from authorization import api as auth_api
from binanceAPI import api as binance_api
from trade import api as trade_api
from user import api as user_api

# Init App
app = Flask(__name__)

config = {
    'ORIGINS': [
        'http://localhost:1234',  # React
        'http://127.0.0.1:1234',  # React
    ],
}

api = Api()
api.init_app(app)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)
api.add_namespace(auth_api, path="/auth")
api.add_namespace(binance_api, path="/binance")
api.add_namespace(account_info_api, path="/info")
api.add_namespace(trade_api, path="/trade")
api.add_namespace(user_api, path="/user")
CORS(app, resources={
     r'/*': {'origins': config['ORIGINS']}}, supports_credentials=True)

connect('cryptoplatform')


if __name__ == '__main__':
    app.run(debug=True)
