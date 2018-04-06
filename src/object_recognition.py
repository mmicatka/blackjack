# @file object_recognition
# @date Fri Apr  6 16:04:21 2018
# @author Matthew Chan
# @brief Script to handle object recognition logic in order to identify playing cards.

# Project dependencies
import numpy as np
import cv2

# Read in input image (as gray-scale)
img = cv2.imread('/Users/mchan/Desktop/cards.jpg', cv2.IMREAD_GRAYSCALE)

# Blur (to remove artifacts) and set color thresholds (for better edge detection) on image
def preprocess(image):
    image = cv2.GaussianBlur(image, (1, 1), 1000)
    retval, image = cv2.threshold(image, 120, 255, cv2.THRESH_BINARY)
    return image

# Pre-process image
img = preprocess(img)

# Scale down image
height = img.shape[0]
width = img.shape[1]
print(f"Image width and height (respectively) is ({width}, {height})")
height_r = int(height / 4)
width_r = int(width / 4)
print(f"Resizing image to width and height of ({width_r}, {height_r})")
img_r = cv2.resize(img, (width_r, height_r))

# Create window showing the resized image
cv2.imshow('object_recognition.py', img_r)

# Destroy window after key-press
cv2.waitKey(0)
cv2.destroyAllWindows()
