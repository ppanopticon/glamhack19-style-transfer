import os

from flask_restful import Resource
from flask import send_file

from postcards import POSTCARDS


class PostcardImage(Resource):
    def get(self, postcard_id):
        return send_file(os.path.join('postcards', 'images', POSTCARDS[postcard_id]['image']))
