import os

from flask_restful import Resource
from flask import send_file


class Snapshot(Resource):
    def get(self, snapshot_id):
        return send_file(os.path.join('./snapshots/', snapshot_id))
