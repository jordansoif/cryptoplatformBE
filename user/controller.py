from .model import Users


def get_user(user_id):
    user = Users.objects(id=user_id).first()
    if not user:
        return {"error": "something went wrong"}, 400
    else:
        return user.serializer_authentication(), 200
