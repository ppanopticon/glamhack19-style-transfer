import os
import uuid

import cv2
import numpy as np

from flask_restful import Resource
from flask import request

from services.Generator import Generator


class Generate(Resource):
    def put(self, postcard_id):
        return self.post(postcard_id)

    def post(self, postcard_id):

        # Load images
        try:
            data = np.fromstring(request.data, np.uint8)
            style = cv2.imread(os.path.join('postcards', 'images', postcard_id + '.jpg'), cv2.IMREAD_COLOR)

            # Cut received image.
            received = cv2.imdecode(data, cv2.IMREAD_COLOR)
            received = received[300:700, 500:900]

            # Adjust size of style image
            height, width, channels = style.shape
            factor_width, factor_height = (1.0,1.0)
            if height > received.shape[0] * 1.75:
                factor_width = (received.shape[0]*2 / height)
                width = int(width * factor_width)
                height = received.shape[0] * 2
            elif width > received.shape[1] * 1.75:
                factor_height = (received.shape[1]*2 / width)
                height = int(height * factor_height)
                width = received.shape[1] * 2

            style = cv2.resize(style, (width, height))

            # Adjust size of received image.
            vertical = max(0,int((style.shape[0] - received.shape[0]) * factor_height / 2))
            horizontal = max(0,int((style.shape[1] - received.shape[1]) * factor_width / 2))
            image = np.zeros(style.shape,dtype=np.uint8)
            image[:,:,0] = 255
            image[horizontal:horizontal+received.shape[0],vertical:vertical+received.shape[1]] = received

            cv2.imwrite('derived.jpg', image)

            if style is not None and image is not None:
                # Generate filename and read file.
                filename = str(uuid.uuid4())

                # Invoke model (new thread) and generate stuff (new thread).
                Generator().enqueue(image, style, filename)

                return {'status': 1, 'id': filename}
            else:
                return {'status': 0}
        except Exception:
            return {'status': 0}