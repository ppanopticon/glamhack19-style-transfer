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
        model = Model(self.input, self.style)
        img = model.run(10)
        cv2.imwrite(os.path.join('./snapshots/', self.output), img)
