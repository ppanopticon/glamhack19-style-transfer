import os
import cv2

from flask_restful import Resource

class PostcardImageInfo(Resource):
    def get(self, postcard_id):
        img = cv2.imread(os.path.join('./postcards/images', postcard_id + '.jpg'))
        return {'id' : postcard_id, 'width': img.shape[1], 'height': img.shape[0]}
