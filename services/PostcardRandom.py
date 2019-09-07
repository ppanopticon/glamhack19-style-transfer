import os
import random

from flask_restful import Resource


class PostcardRandom(Resource):
    def get(self):
        file_list = []
        for root, dirs, files in os.walk('postcards/images'):
            for file in files:
                file_list.append(os.path.splitext(file)[0])

        return {'postcards': [random.choice(file_list)]}