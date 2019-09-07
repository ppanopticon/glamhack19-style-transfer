import os

from flask_restful import Resource
from flask import send_file


class PostcardAudio(Resource):
    def get(self, postcard_id):
        return send_file(os.path.join('./postcards/audio', postcard_id + '.mp3'))
