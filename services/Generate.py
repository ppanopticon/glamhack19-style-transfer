import os
import uuid

import cv2
from flask_restful import Resource
from flask import request


class Generate(Resource):
    def post(self, postcard_id):
        data = request.files['file']

        # Load images
        try:
            style = cv2.imread(os.path.join('./postcards/', postcard_id))
            image = cv2.imread(data)

            # Generate filename and read file.
            filename = str(uuid.uuid4()) + '.jpg'

            # TODO: Invoke model (new thread) and generate stuff.
            # x = threading.Thread(target=thread_function, args=(1,))
            # x.start()

            return {'status': 1, 'id': filename}
        except Exception:
            return {'status': 0}
