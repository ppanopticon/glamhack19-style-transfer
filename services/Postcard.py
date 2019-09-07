import os

from flask_restful import Resource
from flask import send_file

class Postcard(Resource):
    def get(self, postcard_id):
        return send_file(os.path.join('./postcards/', postcard_id))
