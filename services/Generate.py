import os
import threading
import uuid

import cv2
import numpy as np

from flask_restful import Resource
from flask import request

from model import Model


class Generate(Resource):
    def post(self, postcard_id):

        # Load images
        try:
            data = np.fromstring(request.data, np.uint8)
            style = cv2.imread(os.path.join('postcards', 'images', postcard_id + '.jpg'), cv2.IMREAD_COLOR)
            image = cv2.imdecode(data, cv2.IMREAD_COLOR)

            if style is not None and image is not None:
                # Generate filename and read file.
                filename = str(uuid.uuid4()) + '.jpg'

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

    def __init__(self, input, style, output):
        super(StyleTransferThread, self).__init__()
        self.input = input
        self.style = style
        self.output = output

    # Run method (executed in parallel)
    def run(self):

        #Instantiate model for style transfer
        model = Model(self.input, self.style)

        # Create mask for blue screen replacement.
        lower_blue = np.array([0, 0, 100])
        upper_blue = np.array([120, 100, 255])
        mask = cv2.resize(self.input, (model.width, model.height))
        mask = cv2.inRange(mask, lower_blue, upper_blue)

        # Generate style transfered image and mask it based on blue screen.
        masked_image = model.run(10)
        masked_image[mask != 0] = [0, 0, 0]

        # Mask background image.
        background_image = cv2.resize(self.style, (model.width, model.height))
        background_image = cv2.cvtColor(background_image, cv2.COLOR_BGR2RGB)
        background_image[mask == 0] = [0, 0, 0]

        # Export combined image.
        cv2.imwrite(os.path.join('./snapshots/', self.output), background_image + masked_image)
