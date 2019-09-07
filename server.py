from flask import Flask
from flask_restful import Api

from services.PostcardAudio import PostcardAudio
from services.PostcardImageInfo import PostcardImageInfo
from services.PostcardRandom import PostcardRandom
from services.Generate import Generate
from services.History import History
from services.PostcardList import PostcardList
from services.PostcardImage import PostcardImage
from services.Snapshot import Snapshot

app = Flask(__name__)
api = Api(app)

api.add_resource(PostcardList, '/postcard/list') # Route_1: Postcard list
api.add_resource(PostcardRandom, '/postcard/random') # Route_2: Random postcard
api.add_resource(PostcardImageInfo, '/postcard/image/info/<postcard_id>') # Route_3: Access postcard image
api.add_resource(PostcardImage, '/postcard/image/<postcard_id>') # Route_4: Access postcard image
api.add_resource(PostcardAudio, '/postcard/audio/<postcard_id>') # Route_5: Access postcard ambient audio

api.add_resource(History, '/history/list') # Route_5: History list
api.add_resource(Snapshot, '/history/image/<snapshot_id>') # Route_6: Access snapshot

api.add_resource(Generate, '/generate/<postcard_id>') # Route_7: Generate a new photo

if __name__ == '__main__':
     app.run(port='5002', host='0.0.0.0')