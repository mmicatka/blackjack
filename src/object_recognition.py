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
    return np.array([l_vertices[0], r_vertices[0], r_vertices[1], l_vertices[1]], np.float32)

''' Run Harris edge detection on the provided image
    @param image The image (expected to be in color) to run edge detection on
    @return A tuple containing an array of detected edge coordinates and the output image
'''
def edge_detection(image):
    # Apply gray-scale to image
    gray = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)

    # Generate Harris edge detection
    dst = cv2.cornerHarris(gray, 5, 3, 0.04)
    dst = cv2.dilate(dst, None)
    ret, dst = cv2.threshold(dst, 0.03 * dst.max(), 255, 0)
    dst = np.uint8(dst)

    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv2.cornerSubPix(gray, np.float32(centroids), (5, 5), (-1, -1), criteria)

    res = np.hstack((centroids, corners))
    res = np.int0(res)

    # Change detected edge pixel colors to red
    output_img = image.copy()

    output_img[res[:,1], res[:,0]] = [0, 0, 255]
    # Flip xy-coordinates (OpenCV uses yx coordinates)
    coords = np.stack((res[:,0], res[:,1]), axis = -1)
    # output_img[res[:,3], res[:,2]] = [0, 255, 0]

    return (coords, output_img)

# @TODO: Allow for error tolerance in the xy-coordinates
# @TODO: Make this more efficient than O(ab), where a is the length of array a and b is the length of array b
''' Return the intersection between two arrays, each containing arrays of size two
    @param a Input array one
    @param b Input array two
    @return An array containing elements which exist in both a and b
'''
def find_2d_intersection(a, b, tolerance_x, tolerance_y):
    intersection = []
    for x in a:
        for y in b:
            if (abs(x[0] - y[0]) < tolerance_x and abs(x[1] - y[1]) < tolerance_y):
                intersection.append(x.tolist())
    return intersection

# @TODO: Find more efficient algorithm / method to parse out vertices (one that isn't O(n^2), preferrably)
''' Remove similar (i.e. differences in x/y planes are within a specific threshold) xy-coordinates from a 2D array 
    @param arr 2D array containing xy-coordinates
    @param tolerance_x Tolerance for differences in the x direction
    @param tolerance_y Tolerance for differences in the y direction
    @return Array with similar xy-coordinates removed
'''
def minify_2d_array(arr, tolerance_x, tolerance_y):
    min_arr = []
    for x in arr:
        is_unique = True
        for y in min_arr:
            if (abs(x[0] - y[0]) < tolerance_x and abs(x[1] - y[1]) < tolerance_y):
                is_unique = False
        if (is_unique or len(min_arr) == 0):
            min_arr.append(x)
            print(f'Intersection found at ({x[0], x[1]})')
    return min_arr

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

# Declare constants
CONTOUR_THRESHOLD = 10000
INTERSECTION_TOLERANCE_X = 3
INTERSECTION_TOLERANCE_Y = 3
MINIFY_THRESHOLD_X = 50
MINIFY_THRESHOLD_Y = 50

# Read input image (in gray-scale)
img = cv2.imread('/Users/mchan/Desktop/cards.jpg')

# Down-scale image
img_r = rescale(img, 0.2)

# Identify corners in the image
corners, corner_img = edge_detection(img_r)
cv2.imshow('Harris Corner Detection', corner_img)

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

# From the contour and corner data, locate the 4 corners of each playing card
edges = []

for idx, contour in enumerate(contours):
    length = len(contour)
    # Identify intersection between the set of contour points and corner points
    intersections = find_2d_intersection(contour.reshape(length, 2), corners, INTERSECTION_TOLERANCE_X, INTERSECTION_TOLERANCE_Y)
    print(f'Card {idx}: Length of intersection array is {len(intersections)}')
    # Remove similar xy-coordinates (so that hopefully only the four corner coordinates remain)
    edges.append(minify_2d_array(intersections, MINIFY_THRESHOLD_X, MINIFY_THRESHOLD_Y))
    print(f'Card {idx}: Length of intersection array is {len(intersections)}')

v_transform = np.array([ [0,0],[450,0],[450,450],[0,450] ], np.float32)

for n in np.arange(0, num_cards):
    # Sort vertices
    v = arrange_vertices(edges[n])
    # v = np.array(edges[n], np.float32)
    print(f'Card {n}\'s vertices: {v}')
    # Generate 3x3 perspective transform matrix
    m = cv2.getPerspectiveTransform(v, v_transform)
    # Warp perspective
    output = cv2.warpPerspective(img_r.copy(), m, (450, 450))
    # Show the output image
    cv2.imshow(f'Card {n}', output)

# Destroy window after key-press
cv2.waitKey(0)
cv2.destroyAllWindows()
