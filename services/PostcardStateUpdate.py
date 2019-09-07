from flask_restful import Resource

from postcards import POSTCARDS
from services.PostcardState import PostcardState

class PostcardStateUpdate(Resource):
    def get(self, postcard_id):
        if (postcard_id in POSTCARDS):
            PostcardState().current = postcard_id
            return {'status': 1}
        else:
            return {'status': 0}