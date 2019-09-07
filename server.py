from flask import Flask
from flask_restful import Api

from services.History import History
from services.Postcard import Postcard
from services.Postcards import Postcards
from services.Snapshot import Snapshot

app = Flask(__name__)
api = Api(app)

api.add_resource(Postcards, '/postcards') # Route_1: Postcard list
api.add_resource(Postcard, '/postcard/<postcard_id>') # Route_2: Access postcard
api.add_resource(History, '/history') # Route_3: History
api.add_resource(Snapshot, '/snapshot/<postcard_id>') # Route_3: Access snapshot

if __name__ == '__main__':
     app.run(port='5002', host='0.0.0.0')