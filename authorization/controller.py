from user.model import *
from flask_restplus import Api, Resource, reqparse, Namespace
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)


# User Login
def auth_login(user, password):
    user_finder = Users.objects(user_name=user).first()
    if user_finder != None:
        if user_finder.password == password:
            access_token = create_access_token(
                identity=str(user_finder["id"]))
            return {"access_token": access_token}, 200
    return {"error": "shit happened"}, 400


# Create User
def create_user(user, password):
    user_finder = Users.objects(user_name=user).first()
    if user_finder == None:
        new_user = Users(user_name=user, password=password)
        new_user.save()
        return "User has been added"
    else:
        return "User already exists."


# Change User Password
def change_password(user, password, new_password):
    user_finder = Users.objects(user_name=user).first()
    if user_finder != None:
        if user_finder.password == password:
            user_finder.update(set__password=new_password)
            user_finder.save()
            return "Password has been updated."
    else:
        return "Username/Password does not exist"
