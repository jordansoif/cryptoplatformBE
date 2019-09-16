from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from user.model import Users
from flask_restplus import Api, Resource, reqparse, Namespace

api = Namespace("auth")


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


@api.route("/login")
class AuthLogin(Resource):
    def post(self):
        parser = login_page_parser()
        args = parser.parse_args()
        args_user_name = args["user_name"]
        args_password = args["password"]
        user_finder = Users.objects(user_name=args_user_name).first()
        if user_finder != None:
            if user_finder.password == args_password:
                access_token = create_access_token(
                    identity=str(user_finder["id"]))
                return {"access_token": access_token}, 200
        return {"error": "shit happened"}, 400

# Create User
@api.route('/createuser')
class create_user(Resource):
    def post(self):
        parser = login_page_parser()
        args = parser.parse_args()
        target_user = args['user_name']
        password = args['password']
        user_finder = Users.objects(user_name=target_user).first()
        if user_finder == None:
            user = Users()
            user.user_name = target_user
            user.password = password
            user.save()
            return "User has been added"
        else:
            return "User already exists."

# Change User Password
@api.route('/changepassword')
class change_password(Resource):
    def put(self):
        parser = login_page_parser()
        args = parser.parse_args()
        target_user = args['user_name']
        password = args['password']
        new_password = args['new_password']
        user_finder = Users.objects(user_name=target_user).first()
        if user_finder != None:
            if user_finder.password == password:
                user_finder.update(set__password=new_password)
                user_finder.save()
                return "Password has been updated."
        else:
            return "Username/Password does not exist"
