from user.model import Users , Purchase_Lots, Realized_Positions
from flask_restplus import Api, Resource, reqparse, Namespace
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=20000
)


def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)


# User Login
def auth_login(user, password):
    user_object = Users.objects(user_name=user).first()
    if user_object != None:
        if check_encrypted_password(password, user_object.password):
            access_token = create_access_token(
                identity=str(user_object["id"]))
            return {"access_token": access_token}, 200
    return {"error": "Incorrect user name or password"}, 400


# Create User
def create_user(user, password):
    user_object = Users.objects(user_name=user).first()
    if user_object == None:
        new_user = Users(user_name=user, password=password)
        new_user.save()
        return "User has been added"
    else:
        return "User already exists."


# Change User Password
def change_password(user, password, new_password):
    user_object = Users.objects(user_name=user).first()
    if user_object != None:
        if check_encrypted_password(password, user_object.password):
            user_object.update(set__password=new_password)
            user_object.save()
            return "Password has been updated."
    else:
        return "Username or Password are incorrect."
