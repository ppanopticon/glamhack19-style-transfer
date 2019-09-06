import numpy as np
import requests
import argparse
import cv2

# Hyperparams
from model import Model

def main():
    ap = argparse.ArgumentParser()

    # Add the arguments to the parser
    ap.add_argument("-i", "--input", required=True, help="The input image.")
    ap.add_argument("-s", "--style", required=True, help="The style image.")
    ap.add_argument("-o", "--output", required=True, help="The output image.")
    args = vars(ap.parse_args())

    #Load required images
    input_image = cv2.imread(args['input'])
    style_image = cv2.imread(args['style'])

    model = Model(input_image, style_image)
    output = model.run()

    cv2.imshow("image", output)
    cv2.imwrite(args['output'], output)

if __name__ == "__main__":
    main()