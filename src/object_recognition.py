# @file object_recognition
# @date Fri Apr 6 2018 16:04:21
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
    sort_x = sorted(vertices, key = lambda x : x[0])
    l_vertices = sorted(sort_x[:2], key = lambda x : x[1])
    r_vertices = sorted(sort_x[2:], key = lambda x : x[1])
    # print(f'TL {l_vertices[0]} TR {r_vertices[0]} BR {r_vertices[1]} BL {l_vertices[1]}')
    return np.array([l_vertices[0], r_vertices[0], r_vertices[1], l_vertices[1]], np.float32)

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
    print(f'Resizing image width and height from ({width}, {height}) to ({width_r}, {height_r})')
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

''' Calculate the distance between two xy-coordinates
    @param a The first xy-coordinate
    @param b The second xy-coordinate
    @return The distance between both coordinates
'''
def dist(a, b):
    return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

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

''' Identify the four corners of a rectangle, given a set of points on the edge of the rectangle
    @param contour A set of points on the edge of the playing card
    @param error_threshold The amount by which the length of each side can differ from the length of it's parallel side
    @param search_tolerance The amount by which x-coordinates can differ on the right and left sides of the playing card
    @return A list containing the xy-coordinates of the playing card's four corners
'''
def find_corners(contour, error_threshold, search_tolerance):
    # Get a list of x and y coordinates
    x_coords = list(map(lambda x : x[0], contour))
    y_coords = list(map(lambda x : x[1], contour))
    
    # Find indices of min and max values for both lists
    min_x = np.argmin(x_coords)
    max_x = np.argmax(x_coords)
    min_y = np.argmin(y_coords)
    max_y = np.argmax(y_coords)

    corners = [contour[min_x], contour[max_x], contour[min_y], contour[max_y]]

    # Check if the corners are valid, if they are--return
    if valid_corners(corners, error_threshold):
        return corners

    # Find the left and right sides of the card
    l_search_space = list(filter(lambda x : abs(x[0] - min(x_coords)) < search_tolerance, contour))
    r_search_space = list(filter(lambda x : abs(x[0] - max(x_coords)) < search_tolerance, contour))
    
    l_y_coords = list(map(lambda x : x[1], l_search_space))
    r_y_coords = list(map(lambda x : x[1], r_search_space))

    # Return the min and max y values for both sides
    return [l_search_space[np.argmin(l_y_coords)], r_search_space[np.argmin(r_y_coords)], l_search_space[np.argmax(l_y_coords)], r_search_space[np.argmax(r_y_coords)]]

def test(contour):
    d = []
    # Calculate distance between all points on the edge
    for idx, coord in enumerate(contour):
        for n in [x for x in np.arange(0, len(contour)) if x != idx]:
            d.append([coord, contour[n], dist(coord, contour[n])])
    # Sort by longest distance to find two corners
    d = sorted(d, key = lambda x : x[2], reverse = True)
    # Sort two corners by y-value (works for vertical cards)
    pts = sorted(d[0][0:2], key = lambda x : x[1], reverse = True)
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
    
def rotate(theta, x, y, origin_x, origin_y):
    x1 = x - origin_x
    y1 = y - origin_y
    t = np.radians(theta)
    cos = np.cos(t)
    sin = np.sin(t)
    return [x1 * cos - y1 * sin + origin_x, x1 * sin + y1 * cos + origin_y]

# Declare constants
# CONTOUR_THRESHOLD = 10000
AREA_LOWER_BOUND = 5000
AREA_UPPER_BOUND = 12000

# Read input image (in gray-scale)
img = cv2.imread('/Users/mchan/Desktop/train.png')

# Down-scale image
img_r = rescale(img, 0.25)
# img_r = img.copy()

# Apply pre-processing to the image
preprocess_img = preprocess(img_r)

# Identify contours in the image
image, contours, hierarchy = cv2.findContours(preprocess_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key = cv2.contourArea, reverse = True)

print(f'Largest contour is {cv2.contourArea(contours[0])}')
# @TODO: Fix logic to find contours approximately the size of a playing card -- not just the contours with the largest area
# Identify contours that indicate the edges of a playing card
for i, e in enumerate(contours):
    # if (cv2.contourArea(contours[i]) - cv2.contourArea(contours[i + 1]) >= CONTOUR_THRESHOLD):
    if (cv2.contourArea(e) > AREA_LOWER_BOUND and cv2.contourArea(e) < AREA_UPPER_BOUND):
        num_cards = i + 1

# Remove contours for objects other than playing cards
print(f'Identified {num_cards} cards in the image')
contours = contours[:num_cards]

# Draw contours onto the image
contour_img = img_r.copy()
cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 5)

# Create window showing the resized image
# cv2.imshow('Object Contour Detection', rescale(contour_img, 0.2))
cv2.imshow('Object Contour Detection', contour_img)

# From the contour and corner data, locate the 4 corners of each playing card
edges = []

v_transform = np.array([ [0,0],[450,0],[450,450],[0,450] ], np.float32)

for n in np.arange(0, num_cards):
    contours[n] = contours[n].reshape(len(contours[n]), 2).astype(np.float32)
    corners = arrange_vertices(test(contours[n]))
    # corners = arrange_vertices(find_corners(contours[n], 5, 15))
    # corners = np.asarray(corners, dtype = np.float32)
    print(f'Card {n} corners: {corners}')
    # Generate 3x3 perspective transform matrix
    m = cv2.getPerspectiveTransform(corners, v_transform)
    # Warp perspective
    output = cv2.warpPerspective(img_r.copy(), m, (450, 450))
    # Show the output image
    cv2.imshow(f'Card {n}', output)

# Destroy window after key-press
cv2.waitKey(0)
cv2.destroyAllWindows()
