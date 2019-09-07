import os

from flask_restful import Resource


class Postcards(Resource):
    def get(self):
        return {'postcards': files for subdir, dirs, files in os.walk('postcards')}
