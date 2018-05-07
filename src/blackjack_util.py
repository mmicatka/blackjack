# @file blackjack_util
# @date Sun Apr 15 08:38:37 2018
# @author Matthew Chan
# @brief Utility functions to be used by other scripts

# Project dependencies
import numpy as np
import cv2
import pickle
import datetime

''' Arrange edges by top-left, top-right, bottom-right, bottom-left
    @param vertices An array of vertices (size 4) that represent the corners of a playing card
    @return A numpy array containing the sorted vertices
'''
def arrange_vertices(vertices):
    sort_x = sorted(vertices, key=lambda x : x[0])
    l_vertices = sorted(sort_x[:2], key=lambda x : x[1])
    r_vertices = sorted(sort_x[2:], key=lambda x : x[1])
    # print(f'TL {l_vertices[0]} TR {r_vertices[0]} BR {r_vertices[1]} BL {l_vertices[1]}')
    return np.array([l_vertices[0], r_vertices[0], r_vertices[1], l_vertices[1]], np.float32)

''' Calculate the distance between two xy-coordinates
    @param a The first xy-coordinate
    @param b The second xy-coordinate
    @return The distance between both coordinates
'''
def dist(a, b):
    return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

''' Filter contours based on area
    @param contours An array containing all of the contours
    @param lower_bound Lower bound on the areas to filter out
    @param upper_bound Upper bound on the areas to filter out
    @return The filtered array of contours
'''
def filter_contours(contours, lower_bound, upper_bound):
    return list(filter(lambda x : cv2.contourArea(x) > lower_bound and cv2.contourArea(x) < upper_bound, contours))

''' Identify the four corners of a rectangle, given a set of points on the edge of the rectangle
    @param contour Set of points on the edge of the playing card
    @return A list containing the xy-coordinates of the playing card's four corners
'''
def find_corners(contour):
    d = []
    # Calculate distance between all points on the edge
    print(f'{datetime.datetime.now()} Calculating distances...')
    # Find min and max y
    print(contour[0])
    s = sorted(contour, key=lambda x : x[1])
    min_y = s[0][1]
    max_y = s[-1][1]
    top = list(filter(lambda x : abs(x[1] - min_y) < 10, contour))
    bot = list(filter(lambda x : abs(x[1] - max_y) < 10, contour))
    for coord in top:
        for n in bot:
            d.append([coord, n, dist(coord, n)])
    print(f'{datetime.datetime.now()} Calculating distances...')
    # Sort by longest distance to find two corners
    d = sorted(d, key=lambda x : x[2], reverse=True)
    # Sort two corners by y-value (works for vertical cards)
    pts = sorted(d[0][0:2], key=lambda x : x[1], reverse=True)
    a = pts[0]
    b = pts[1]
    # Determine rotation direction based on x-values
    if (a[0] < b[0]):
        theta = -70
    else:
        theta = 70
    # Calculate midpoint
    midpoint = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
    print(f'Midpoint is {midpoint} | Rotation is {theta}')
    # Rotate both corners around the midpoint
    c = rotate(theta, a[0], a[1], midpoint[0], midpoint[1])
    d = rotate(theta, b[0], b[1], midpoint[0], midpoint[1])
    return [a, b, c, d]

''' Blur image (to remove artifacts) and set color thresholds on the image (for better edge detection)
    @param image The image to apply pre-processing to
    @return The image after pre-processing has been applied
'''
def preprocess(image):
    output = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
    output = cv2.GaussianBlur(output, (1, 1), 1000)
    retval, output = cv2.threshold(output, 120, 255, cv2.THRESH_BINARY)
    return output

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
    # print(f'Resizing image width and height from ({width}, {height}) to ({width_r}, {height_r})')
    return cv2.resize(image.copy(), (width_r, height_r))
    
''' Rotate a point on the xy-plane around a given point
    @param theta Degrees of rotation (positive value will rotate counter-clockwise)
    @param x X-coordinate of the point to rotate
    @param y Y-coordinate of the point to rotate
    @param origin_x X-coordinate of the point to rotate around
    @param origin_y Y-coordinate of the point to rotate around
    @return The xy-coordinate for the rotated point
'''
def rotate(theta, x, y, origin_x, origin_y):
    x1 = x - origin_x
    y1 = y - origin_y
    t = np.radians(theta)
    cos = np.cos(t)
    sin = np.sin(t)
    return [x1 * cos - y1 * sin + origin_x, x1 * sin + y1 * cos + origin_y]

''' Check whether the set of four coordinates form valid corners of a playing card
    @param corners An array containing four xy-coordinates
    @param error_threshold The amount by which the length of each side can differ from the length of it's parallel side
    @return A boolean value denoting whether or not the corners are valid
'''
def valid_corners(corners, error_threshold):
    v = arrange_vertices(corners)
    # print(f'Comparing sides of length {dist(v[0], v[1])} and {dist(v[2], v[3])}')
    # print(f'Comparing sides of length {dist(v[0], v[3])} and {dist(v[1], v[2])}')
    if abs(dist(v[0], v[1]) - dist(v[2], v[3])) < error_threshold and abs(dist(v[0], v[3]) - dist(v[1], v[2])) < error_threshold :
        return True
    return False
