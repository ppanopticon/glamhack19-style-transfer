import numpy as np
import cv2

from keras import backend, Sequential
from keras.applications.vgg16 import VGG16
from keras.layers import MaxPooling2D, AveragePooling2D
from scipy.optimize import fmin_l_bfgs_b


CONTENT_WEIGHT = 0.05
STYLE_WEIGHT = 4.5
IMAGE_SIZE = 500

IMAGENET_MEAN_RGB_VALUES = [123.68, 116.779, 103.939]

TOTAL_VARIATION_WEIGHT = 0.995
TOTAL_VARIATION_LOSS_FACTOR = 1.25
ITERATIONS = 10


class Model:

    def __init__(self, input_image, style_image):

        # Calculates the new size of the input image (respecting the maximum).
        self.height, self.width, self.channels = input_image.shape
        if self.height > self.width:
            if self.height > IMAGE_SIZE:
                self.width = int(self.width * (IMAGE_SIZE/self.height))
                self.height = IMAGE_SIZE
        else:
            if self.width > IMAGE_SIZE:
                self.height = int(self.height * (IMAGE_SIZE/self.width))
                self.width = IMAGE_SIZE

        input_image_array = np.asarray(cv2.resize(input_image, (self.width, self.height)), dtype="float32")
        input_image_array = np.expand_dims(input_image_array, axis=0)
        input_image_array[:, :, :, 0] -= IMAGENET_MEAN_RGB_VALUES[2]
        input_image_array[:, :, :, 1] -= IMAGENET_MEAN_RGB_VALUES[1]
        input_image_array[:, :, :, 2] -= IMAGENET_MEAN_RGB_VALUES[0]
        input_image_array = input_image_array[:, :, :, ::-1]

        style_image_array = np.asarray(cv2.resize(style_image, (self.width, self.height)), dtype="float32")
        style_image_array = np.expand_dims(style_image_array, axis=0)
        style_image_array[:, :, :, 0] -= IMAGENET_MEAN_RGB_VALUES[2]
        style_image_array[:, :, :, 1] -= IMAGENET_MEAN_RGB_VALUES[1]
        style_image_array[:, :, :, 2] -= IMAGENET_MEAN_RGB_VALUES[0]
        style_image_array = style_image_array[:, :, :, ::-1]

        input_image_var = backend.variable(input_image_array)
        style_image_var = backend.variable(style_image_array)
        self.combination_image = backend.placeholder((1, self.height, self.width, 3))

        input_tensor = backend.concatenate([input_image_var, style_image_var, self.combination_image], axis=0)

        # Create and adjust VGG16 model
        self.model  = VGG16(input_tensor=input_tensor, weights='imagenet', include_top=False)

        layers = dict([(layer.name, layer.get_output_at(0)) for layer in self.model.layers])

        content_layer = 'block2_conv2'
        layer_features = layers[content_layer]
        content_image_features = layer_features[0, :, :, :]
        combination_features = layer_features[2, :, :, :]

        loss = backend.variable(0.)
        loss += CONTENT_WEIGHT * self.content_loss(content_image_features, combination_features)

        style_layers = ["block1_conv2", "block2_conv2", "block3_conv3", "block4_conv3", "block5_conv3"]
        for layer_name in style_layers:
            layer_features = layers[layer_name]
            style_features = layer_features[1, :, :, :]
            combination_features = layer_features[2, :, :, :]
            style_loss = self.style_loss(style_features, combination_features)
            loss += (STYLE_WEIGHT / len(style_layers)) * style_loss

        loss += TOTAL_VARIATION_WEIGHT * self.total_variation_loss(self.combination_image)

        self.outputs = [loss]
        self.outputs += backend.gradients(loss, self.combination_image)

    def content_loss(self, content, combination):
        return backend.sum(backend.square(combination - content))

    def style_loss(self, style, combination):
        style = self.gram_matrix(style)
        combination = self.gram_matrix(combination)
        size = self.height * self.width
        return backend.sum(backend.square(style - combination)) / (4. * (self.channels ** 2) * (size ** 2))

    def gram_matrix(self, x):
        features = backend.batch_flatten(backend.permute_dimensions(x, (2, 0, 1)))
        gram = backend.dot(features, backend.transpose(features))
        return gram

    def total_variation_loss(self, x):
        a = backend.square(x[:, :self.height - 1, :self.width - 1, :] - x[:, 1:, :self.width - 1, :])
        b = backend.square(x[:, :self.height - 1, :self.width - 1, :] - x[:, :self.height - 1, 1:, :])
        return backend.mean(backend.pow(a + b, TOTAL_VARIATION_LOSS_FACTOR))

    def evaluate_loss_and_gradients(self, x):
        x = x.reshape((1, self.height, self.width, self.channels))
        outs = backend.function(inputs=[self.combination_image], outputs=self.outputs)([x])
        return outs[0], outs[1].flatten().astype("float64")

    def run(self, iterations=ITERATIONS):
        x = np.random.uniform(0, 255, (1, self.height, self.width, 3)) - 128.
        evaluator = Evaluator(self)

        for i in range(iterations):
            x, loss, info = fmin_l_bfgs_b(evaluator.loss, x.flatten(), fprime=evaluator.gradients, maxfun=25)
            print("Iteration %d completed with loss %d" % (i, loss))

        x = x.reshape((self.height, self.width, self.channels))
        x = x[:, :, ::-1]
        x[:, :, 0] += IMAGENET_MEAN_RGB_VALUES[2]
        x[:, :, 1] += IMAGENET_MEAN_RGB_VALUES[1]
        x[:, :, 2] += IMAGENET_MEAN_RGB_VALUES[0]
        return np.clip(x, 0, 255).astype("uint8")

class Evaluator:

    def __init__(self, model):
        self.model = model

    def loss(self, x):
        loss, gradients = self.model.evaluate_loss_and_gradients(x)
        self._gradients = gradients
        return loss

    def gradients(self, x):
        return self._gradients