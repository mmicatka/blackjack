# @file object_recognition
# @date Fri Apr  6 16:04:21 2018
# @author Matthew Chan
# @brief Script to handle object recognition logic in order to identify playing cards.

# Project dependencies
import numpy as np
import cv2

''' Rescale image using the provided multiplier
    @param image The image to rescale
    @param multiplier The multiplier used to rescale both the height and width of the image
    @return The resized image
'''
def rescale(image, multiplier):
    height = image.shape[0]
    width = image.shape[1]
    height_r = int(height * multiplier)
    width_r = int(width * multiplier)
    print(f"Resizing image width and height from ({width}, {height}) to ({width_r}, {height_r})")
    return cv2.resize(image, (width_r, height_r))

''' Blur image (to remove artifacts) and set color thresholds on the image (for better edge detection)
    @param image The image to apply pre-processing to
    @return The image after pre-processing has been applied
'''
def preprocess(image):
    image = cv2.GaussianBlur(image, (1, 1), 1000)
    retval, image = cv2.threshold(image, 120, 255, cv2.THRESH_BINARY)
    return image


CONTOUR_THRESHOLD = 10000

# Read input image (in gray-scale)
img = cv2.imread('/Users/mchan/Desktop/cards.jpg', cv2.IMREAD_GRAYSCALE)

# Down-scale image
img_r = rescale(img, 0.2)

# Keep a clean copy of the down-scaled image
imCopy = img_r.copy()

# Apply pre-processing to the image
img_r = preprocess(img_r)

# Identify contours in the image
image, contours, hierarchy = cv2.findContours(img_r, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key = cv2.contourArea, reverse = True)

# Identify contours that indicate the edges of a playing card
for i, e in enumerate(contours):
    if (cv2.contourArea(contours[i]) - cv2.contourArea(contours[i + 1]) >= CONTOUR_THRESHOLD):
        num_cards = i + 1
        break;

# Remove contours for objects other than playing cards
contours = contours[:num_cards]


# @TODO: Find more efficient algorithm / method to parse out vertices
edges = contours.copy()

for i, e in enumerate(edges):
    edges[i] = e.reshape((len(e), 2)).astype(np.float32)
    min_x = 0
    max_x = 0
    min_y = 0
    max_y = 0
    for idx, coord in enumerate(edges[i]):
        # print(f"i is {i}, idx is {idx}, max_x is {max_x}")
        if (edges[i][idx][0] > edges[i][max_x][0]):
            max_x = idx
        if (edges[i][idx][0] < edges[i][min_x][0]):
            min_x = idx
        if (edges[i][idx][1] > edges[i][max_y][1]):
            max_y = idx
        if (edges[i][idx][1] < edges[i][min_y][1]):
            min_y = idx
    edges[i] = edges[i][[min_x, max_x, min_y, max_y], :]
    print(edges[i])

print(f'Identified {num_cards} cards in the image')

# Draw contours onto the image
cv2.drawContours(imCopy, contours, -1, (0, 255, 0), 5)

# @TODO: Affine transform on the card to normalize the image perspectives
# h = np.array([ [0,0],[449,0],[449,449],[0,449] ], np.float32)
# test = np.array([ contours[0].max(0).tolist(), contours[0].max(1).tolist(), contours[0].min(0).tolist(), contours[0].min(1).tolist() ], np.float32)
# cv2.getPerspectiveTransform(contours[0], h)

# Create window showing the resized image
cv2.imshow('object_recognition.py', imCopy)

# Destroy window after key-press
cv2.waitKey(0)
cv2.destroyAllWindows()
