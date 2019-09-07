from flask_restful import Resource

from postcards import POSTCARDS


class PostcardList(Resource):
    def get(self):
        return {'postcards': list(POSTCARDS.keys())}
