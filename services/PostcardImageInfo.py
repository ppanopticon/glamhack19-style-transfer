import os
import cv2

from flask_restful import Resource

from postcards import POSTCARDS


class PostcardImageInfo(Resource):
    def get(self, postcard_id):
        img = cv2.imread(os.path.join('postcards', 'images', POSTCARDS[postcard_id]['image']))
        return {'id' : postcard_id, 'width': img.shape[1], 'height': img.shape[0], 'category': POSTCARDS[postcard_id]['class']}
