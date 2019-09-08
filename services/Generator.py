import os
import threading
from queue import Queue

import cv2
import numpy as np
from InstagramAPI import InstagramAPI

from model import Model
from postcards import INSTAGRAM_USER, INSTAGRAM_PASSWORD

LOWER_BLUE = np.array([0, 0, 100])
UPPER_BLUE = np.array([120, 100, 255])

class Generator():
    class __Generator(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.queue = Queue(250)
            self.api = InstagramAPI(INSTAGRAM_USER, INSTAGRAM_PASSWORD)

        def __str__(self):
            return repr(self) + self.current

        def enqueue(self, input, style, output):
            self.queue.put(item={'input': input, 'output': output, 'style': style}, block=True)

        def run(self):
            while (True):
                item = self.queue.get(block=True)

                # Instantiate model for style transfer
                model = Model(item['input'], item['style'])

                # Create mask for blue screen replacement.
                mask = cv2.cvtColor(item['input'], cv2.COLOR_BGR2RGB)
                mask = cv2.resize(mask, (model.width, model.height))
                mask = cv2.inRange(mask, LOWER_BLUE, UPPER_BLUE)

                # Generate style transferred image and mask it based on blue screen.
                masked_image = model.run(3)
                masked_image[mask != 0] = [0, 0, 0]

                # Mask background image.
                background_image = cv2.resize(item['style'], (model.width, model.height))
                background_image[mask == 0] = [0, 0, 0]

                # Export combined image.
                path = os.path.join('snapshots', item['output'] + '.jpg')
                cv2.imwrite(path, background_image + masked_image)

                self.api.login()
                self.api.uploadPhoto(path, "TimeGazer @ GLAM mix'n'hack 2019 #timegazer #glamhack2019")
                self.api.logout()
    instance = None

    def __init__(self):
        if not Generator.instance:
            Generator.instance = Generator.__Generator()

    def __getattr__(self, name):
        return getattr(self.instance, name)


    def start(self):
        self.instance.start()

    def enqueue(self, input, style, output):
        self.instance.enqueue(input, style, output)
