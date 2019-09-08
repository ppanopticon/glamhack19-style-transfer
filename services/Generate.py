import os
import threading
import uuid

import cv2
import numpy as np

from flask_restful import Resource
from flask import request

from model import Model

from InstagramAPI import InstagramAPI

from postcards import INSTAGRAM_USER, INSTAGRAM_PASSWORD
from services.Generator import Generator


class Generate(Resource):
    def put(self, postcard_id):
        return self.post(postcard_id)

    def post(self, postcard_id):

        # Load images
        try:
            data = np.fromstring(request.data, np.uint8)
            style = cv2.imread(os.path.join('postcards', 'images', postcard_id + '.jpg'), cv2.IMREAD_COLOR)
            image = cv2.imdecode(data, cv2.IMREAD_COLOR)
            cv2.imwrite('received.jpg', image)

            if style is not None and image is not None:
                # Generate filename and read file.
                image = image[0:min(image.shape[0], style.shape[0]), 0:min(image.shape[1], style.shape[1])]
                filename = str(uuid.uuid4())

                # Invoke model (new thread) and generate stuff (new thread).
                Generator().enqueue(image, style, filename)

                return {'status': 1, 'id': filename}
            else:
                return {'status': 0}
        except Exception:
            return {'status': 0}