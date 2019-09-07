from flask import Flask
from flask_restful import Api

from services.Postcard import Postcard
from services.Postcards import Postcards

app = Flask(__name__)
api = Api(app)

api.add_resource(Postcards, '/postcards') # Route_1: Postcard list
api.add_resource(Postcard, '/postcard/<postcard_id>') # Route_2: Postcard

if __name__ == '__main__':
     app.run(port='5002')