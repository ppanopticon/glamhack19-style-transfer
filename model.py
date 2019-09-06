import numpy as np
import cv2

from keras import backend
from keras.applications.vgg16 import VGG16
from scipy.optimize import fmin_l_bfgs_b

CHANNELS = 3

IMAGE_SIZE = 500
IMAGE_WIDTH = 500
IMAGE_HEIGHT = 375
CONTENT_WEIGHT = 0.02
STYLE_WEIGHT = 4.5

IMAGENET_MEAN_RGB_VALUES = [123.68, 116.779, 103.939]

TOTAL_VARIATION_WEIGHT = 0.995
TOTAL_VARIATION_LOSS_FACTOR = 1.25
ITERATIONS = 4


class Model:

    def __init__(self, input_image, style_image):
        input_image_array = np.asarray(cv2.resize(input_image, (IMAGE_WIDTH, IMAGE_HEIGHT)), dtype="float32")
        input_image_array = np.expand_dims(input_image_array, axis=0)
        input_image_array[:, :, :, 0] -= IMAGENET_MEAN_RGB_VALUES[2]
        input_image_array[:, :, :, 1] -= IMAGENET_MEAN_RGB_VALUES[1]
        input_image_array[:, :, :, 2] -= IMAGENET_MEAN_RGB_VALUES[0]
        input_image_array = input_image_array[:, :, :, ::-1]

        style_image_array = np.asarray(cv2.resize(style_image, (IMAGE_WIDTH, IMAGE_HEIGHT)), dtype="float32")
        style_image_array = np.expand_dims(style_image_array, axis=0)
        style_image_array[:, :, :, 0] -= IMAGENET_MEAN_RGB_VALUES[2]
        style_image_array[:, :, :, 1] -= IMAGENET_MEAN_RGB_VALUES[1]
        style_image_array[:, :, :, 2] -= IMAGENET_MEAN_RGB_VALUES[0]
        style_image_array = style_image_array[:, :, :, ::-1]

        input_image_var = backend.variable(input_image_array)
        style_image_var = backend.variable(style_image_array)
        self.combination_image = backend.placeholder((1, IMAGE_HEIGHT, IMAGE_SIZE, 3))

        input_tensor = backend.concatenate([input_image_var, style_image_var, self.combination_image], axis=0)

        self.model = VGG16(input_tensor=input_tensor, include_top=False)

    def run(self):
        layers = dict([(layer.name, layer.output) for layer in self.model.layers])

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
            style_loss = self.compute_style_loss(style_features, combination_features)
            loss += (STYLE_WEIGHT / len(style_layers)) * style_loss

        loss += TOTAL_VARIATION_WEIGHT * self.total_variation_loss(self.combination_image)

        outputs = [loss]
        outputs += backend.gradients(loss, self.combination_image)

        x = np.random.uniform(0, 255, (1, IMAGE_HEIGHT, IMAGE_WIDTH, 3)) - 128.
        outputs = [loss]
        outputs += backend.gradients(loss, self.combination_image)

        evaluator = Evaluator(self, outputs)

        for i in range(ITERATIONS):
            x, loss, info = fmin_l_bfgs_b(evaluator.loss, x.flatten(), fprime=evaluator.gradients, maxfun=20)
            print("Iteration %d completed with loss %d" % (i, loss))

        x = x.reshape((IMAGE_HEIGHT, IMAGE_WIDTH, CHANNELS))
        x = x[:, :, ::-1]
        x[:, :, 0] += IMAGENET_MEAN_RGB_VALUES[2]
        x[:, :, 1] += IMAGENET_MEAN_RGB_VALUES[1]
        x[:, :, 2] += IMAGENET_MEAN_RGB_VALUES[0]
        x = np.clip(x, 0, 255).astype("uint8")
        return x

    def content_loss(self, content, combination):
        return backend.sum(backend.square(combination - content))

    def gram_matrix(self, x):
        features = backend.batch_flatten(backend.permute_dimensions(x, (2, 0, 1)))
        gram = backend.dot(features, backend.transpose(features))
        return gram

    def compute_style_loss(self, style, combination):
        style = self.gram_matrix(style)
        combination = self.gram_matrix(combination)
        size = IMAGE_HEIGHT * IMAGE_WIDTH
        return backend.sum(backend.square(style - combination)) / (4. * (CHANNELS ** 2) * (size ** 2))

    def total_variation_loss(self, x):
        a = backend.square(x[:, :IMAGE_HEIGHT - 1, :IMAGE_WIDTH - 1, :] - x[:, 1:, :IMAGE_WIDTH - 1, :])
        b = backend.square(x[:, :IMAGE_HEIGHT - 1, :IMAGE_WIDTH - 1, :] - x[:, :IMAGE_HEIGHT - 1, 1:, :])
        return backend.sum(backend.pow(a + b, TOTAL_VARIATION_LOSS_FACTOR))

    def evaluate_loss_and_gradients(self, x, outputs):
        x = x.reshape((1, IMAGE_HEIGHT, IMAGE_WIDTH, CHANNELS))
        outs = backend.function([self.combination_image], outputs)([x])
        loss = outs[0]
        gradients = outs[1].flatten().astype("float64")
        return loss, gradients

class Evaluator:

    def __init__(self, model, outputs):
        self.model = model
        self.outputs = outputs

    def loss(self, x):
        loss, gradients = self.model.evaluate_loss_and_gradients(x, self.outputs)
        self._gradients = gradients
        return loss

    def gradients(self, x):
        return self._gradients