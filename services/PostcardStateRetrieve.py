from flask_restful import Resource

from services.PostcardState import PostcardState


class PostcardStateRetrieve(Resource):
    def get(self):
        return {'postcards': [PostcardState().current]}
