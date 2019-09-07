import os

from flask_restful import Resource


class History(Resource):
    def get(self):
        return {'snapshots': files for subdir, dirs, files in os.walk('snapshots')}