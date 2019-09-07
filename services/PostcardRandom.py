import random

from flask_restful import Resource

from postcards import POSTCARDS


class PostcardRandom(Resource):
    def get(self):
        return {'postcards': [random.choice(list(POSTCARDS.keys()))]}