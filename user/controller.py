from .model import Users


def get_user(user_id):
    user_finder = Users.objects(id=user_id).first()
    if not user_finder:
        return {"error": "something went wrong"}, 400
    else:
        return user_finder.serializer_authentication(), 200
