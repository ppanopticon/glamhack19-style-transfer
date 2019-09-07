import os

from flask_restful import Resource
from flask import send_file

from postcards import POSTCARDS


class PostcardAudio(Resource):
    def get(self, postcard_id):
        return send_file(os.path.join('postcards', 'audio', POSTCARDS[postcard_id]['audio']))
