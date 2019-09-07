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

LOWER_BLUE = np.array([0, 0, 100])
UPPER_BLUE = np.array([120, 100, 255])


class Generate(Resource):
    def put(self, postcard_id):
        return self.post(postcard_id)

    def post(self, postcard_id):

        # Load images
        try:
            data = np.fromstring(request.data, np.uint8)
            style = cv2.imread(os.path.join('postcards', 'images', postcard_id + '.jpg'), cv2.IMREAD_COLOR)
            image = cv2.imdecode(data, cv2.IMREAD_COLOR)

            if style is not None and image is not None:
                # Generate filename and read file.
                image = image[0:min(image.shape[0], style.shape[0]), 0:min(image.shape[1], style.shape[1])]
                filename = str(uuid.uuid4())

                # Invoke model (new thread) and generate stuff (new thread).
                thread = StyleTransferThread(image, style, filename)
                thread.start()

                return {'status': 1, 'id': filename}
            else:
                return {'status': 0}
        except Exception:
            return {'status': 0}


#
# Separate Thread for performing the style transfer.
#
class StyleTransferThread(threading.Thread):

    def __init__(self, input, style, output, post=0):
        super(StyleTransferThread, self).__init__()
        self.input = input
        self.style = style
        self.output = output
        self.post = post

    # Run method (executed in parallel)
    def run(self):
        # Instantiate model for style transfer
        model = Model(self.input, self.style)

        # Create mask for blue screen replacement.
        mask = cv2.cvtColor(self.input, cv2.COLOR_BGR2RGB)
        mask = cv2.resize(mask, (model.width, model.height))
        mask = cv2.inRange(mask, LOWER_BLUE, UPPER_BLUE)

        # Generate style transferred image and mask it based on blue screen.
        masked_image = model.run(10)
        masked_image[mask != 0] = [0, 0, 0]

        # Mask background image.
        background_image = cv2.resize(self.style, (model.width, model.height))
        background_image[mask == 0] = [0, 0, 0]

        # Export combined image.
        path = os.path.join('snapshots', self.output + '.jpg')
        cv2.imwrite(path, background_image + masked_image)

        if self.post == 1:
            api = InstagramAPI(INSTAGRAM_USER, INSTAGRAM_PASSWORD)
            api.login()
            api.uploadPhoto(path, "TimeGazer @ GLAM mix'n'hack 2019 #timegazer #glamhack2019")