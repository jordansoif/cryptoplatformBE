from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from user.model import Users
from flask_restplus import Api, Resource, reqparse, Namespace
from .controller import *
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=20000
)

api = Namespace("auth")


def encrypt_password(password):
    return pwd_context.encrypt(password)


# User Login
@api.route("/login")
class AuthLogin(Resource):
    def post(self):
        parser = login_page_parser()
        args = parser.parse_args()
        return auth_login(user=args["user_name"],
                          password=args['password'])

# Create User
@api.route('/createuser')
class CreateUser(Resource):
    def post(self):
        parser = login_page_parser()
        args = parser.parse_args()
        return create_user(user=args['user_name'],
                           password=encrypt_password(args['password']))

# Change User Password
@api.route('/changepassword')
class ChangePassword(Resource):
    def put(self):
        parser = login_page_parser()
        args = parser.parse_args()
        return change_password(user=args['user_name'],
                               password=encrypt_password(args['password']),
                               new_password=encrypt_password(args['new_password']))


# PARSERS
def login_page_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("user_name",
                        required=True,
                        help="Create User Arg Parser")
    parser.add_argument("password",
                        required=True,
                        help="Password Arg Parser")
    parser.add_argument("new_password",
                        required=False,
                        help="New Password Arg Parser")
    return parser
