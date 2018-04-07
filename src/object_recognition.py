# @file object_recognition
# @date Fri Apr  6 16:04:21 2018
# @author Matthew Chan
# @brief Script to handle object recognition logic in order to identify playing cards.

# Project dependencies
import numpy as np
import cv2

''' Arrange edges by top-left, top-right, bottom-right, bottom-left
    @param vertices An array of vertices (size 4) that represent the corners of a playing card
    @return A numpy array containing the sorted vertices
'''
def arrange_vertices(vertices):
    sort_x = sorted(vertices.tolist(), key = lambda x : x[0])
    l_vertices = sorted(sort_x[:2], key = lambda x : x[1])
    r_vertices = sorted(sort_x[2:], key = lambda x : x[1])
    return np.array([l_vertices[0], r_vertices[0], r_vertices[1], l_vertices[1]], np.float32)

''' Run Harris edge detection on the provided image
    @param image The image (expected to be in color) to run edge detection on
    @return A tuple containing an array of detected edge coordinates and the output image
'''
def corner_detection(image):
    # Apply gray-scale to image
    gray = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    # Generate Harris edge detection
    dst = cv2.cornerHarris(gray, 5, 3, 0.04)
    dst = cv2.dilate(dst, None)
    # Change detected edge pixel colors to red
    output_img = image.copy()
    output_img[dst > 0.03 * dst.max()] = [0, 0, 255]
    return (dst, output_img)

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
    return cv2.resize(image.copy(), (width_r, height_r))

''' Blur image (to remove artifacts) and set color thresholds on the image (for better edge detection)
    @param image The image to apply pre-processing to
    @return The image after pre-processing has been applied
'''
def preprocess(image):
    output = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
    output = cv2.GaussianBlur(output, (1, 1), 1000)
    retval, output = cv2.threshold(output, 120, 255, cv2.THRESH_BINARY)
    return output 


CONTOUR_THRESHOLD = 10000

# Read input image (in gray-scale)
img = cv2.imread('/Users/mchan/Desktop/cards.jpg')

# Down-scale image
img_r = rescale(img, 0.2)

# Identify corners in the image
corners, corner_img = corner_detection(img_r)
cv2.imshow('Harris Corner Detection', corner_img)

# # Keep gray-scaled version of down-scaled image
# img_gray = cv2.cvtColor(img_r.copy(), cv2.COLOR_BGR2GRAY)

# # Keep a clean copy of the down-scaled image
# imCopy = img_gray
# t_img = img_r.copy()

# Apply pre-processing to the image
preprocess_img = preprocess(img_r)

# Identify contours in the image
image, contours, hierarchy = cv2.findContours(preprocess_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key = cv2.contourArea, reverse = True)

# @TODO: Fix logic to find contours approximately the size of a playing card -- not just the contours with the largest area
# Identify contours that indicate the edges of a playing card
for i, e in enumerate(contours):
    if (cv2.contourArea(contours[i]) - cv2.contourArea(contours[i + 1]) >= CONTOUR_THRESHOLD):
        num_cards = i + 1
        break;

# Remove contours for objects other than playing cards
print(f'Identified {num_cards} cards in the image')
contours = contours[:num_cards]

# Draw contours onto the image
contour_img = img_r.copy()
cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 5)

# Create window showing the resized image
cv2.imshow('Object Contour Detection', contour_img)

# Destroy window after key-press
cv2.waitKey(0)
cv2.destroyAllWindows()

# Find intersections between contours and edges (within margin of error)

# Pick a random intersection and remove all other intersections (within margin of error)
# Repeat for all playing cards until each card has 4 points identified
# If more than 4 points are identified, exit with error






# # @TODO: Find more efficient algorithm / method to parse out vertices
# edges = contours.copy()

# for i, e in enumerate(edges):
#     edges[i] = e.reshape((len(e), 2)).astype(np.float32)
#     min_x = 0
#     max_x = 0
#     min_y = 0
#     max_y = 0
#     for idx, coord in enumerate(edges[i]):
#         # print(f"i is {i}, idx is {idx}, max_x is {max_x}")
#         if (edges[i][idx][0] > edges[i][max_x][0]):
#             max_x = idx
#         if (edges[i][idx][0] < edges[i][min_x][0]):
#             min_x = idx
#         if (edges[i][idx][1] > edges[i][max_y][1]):
#             max_y = idx
#         if (edges[i][idx][1] < edges[i][min_y][1]):
#             min_y = idx
#     edges[i] = edges[i][[min_x, max_x, min_y, max_y], :]

# v_transform = np.array([ [0,0],[450,0],[450,450],[0,450] ], np.float32)

# for n in np.arange(0, num_cards):
#     # Sort vertices
#     v = arrange_vertices(edges[n])
#     print(f'Card {n}\'s vertices: {v}')
#     # Generate 3x3 perspective transform matrix
#     m = cv2.getPerspectiveTransform(v, v_transform)
#     # Warp perspective
#     output = cv2.warpPerspective(img_r.copy(), m, (450, 450))
#     # Show the output image
#     cv2.imshow(f'Card {n}', output)
