from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse, Namespace
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from .controller import get_user

api = Namespace("user")


@api.route("/")
class GetUser(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        return get_user(user_id)
