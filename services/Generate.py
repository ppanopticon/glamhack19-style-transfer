import os
import threading
import uuid

import cv2
from flask_restful import Resource
from flask import request

from model import Model


class Generate(Resource):
    def post(self, postcard_id):
        data = request.files['file']

        # Load images
        try:
            style = cv2.imread(os.path.join('./postcards/', postcard_id))
            image = cv2.imread(data)

            # Generate filename and read file.
            filename = str(uuid.uuid4()) + '.jpg'

            # Invoke model (new thread) and generate stuff (new thread).
            model = Model(image, style)
            x = threading.Thread(target=self.run, args=(filename,model))
            x.start()

            return {'status': 1, 'id': filename}
        except Exception:
            return {'status': 0}


    # Run
    def run(self, output, model):
        img = model.run()
        cv2.imwrite(output, img)
