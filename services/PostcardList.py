import os

from flask_restful import Resource


class PostcardList(Resource):
    def get(self):
        file_list = []
        for root, dirs, files in os.walk('postcards/images'):
            for file in files:
                file_list.append(os.path.splitext(file)[0])

        return {'postcards': file_list}
