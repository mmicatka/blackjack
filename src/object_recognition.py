# @file object_recognition
# @date Fri Apr 6 2018 16:04:21
# @author Matthew Chan
# @brief Script to handle object recognition logic in order to identify playing cards.

# Project dependencies
import numpy as np
import cv2
import pickle
import blackjack_util as bu

# Declare constants
# CONTOUR_THRESHOLD = 10000
AREA_LOWER_BOUND = 900000
AREA_UPPER_BOUND = 2000000

# Read input image (in gray-scale)
img = cv2.imread('./img/test/test_2.jpg')

# Down-scale image
# img_r = rescale(img, 0.25)
img_r = img.copy()

# Apply pre-processing to the image
preprocess_img = bu.preprocess(img_r)

# Identify contours in the image
image, contours, hierarchy = cv2.findContours(preprocess_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key = cv2.contourArea, reverse = True)

print(f'Largest contour is {cv2.contourArea(contours[0])}')

# Remove contours for objects other than playing cards
contours = bu.filter_contours(contours, AREA_LOWER_BOUND, AREA_UPPER_BOUND)
num_cards = len(contours)
print(f'Identified {num_cards} cards in the image')

# Draw contours onto the image
contour_img = img_r.copy()
cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 5)

# Create window showing the resized image
# cv2.imshow('Object Contour Detection', bu.rescale(contour_img, 0.2))
# cv2.imshow('Object Contour Detection', contour_img)

# From the contour and corner data, locate the 4 corners of each playing card
edges = []

v_transform = np.array([ [0,0],[450,0],[450,450],[0,450] ], np.float32)

reference = []
answers = []
a = open('s_ref.txt', 'rb')
b = open('s_answers.txt', 'rb')
imgs = pickle.load(a)
answers = pickle.load(b)

def gray(img):
    return cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)

norm_type = cv2.NORM_L1

def preprocess(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),2 )
    thresh = cv2.adaptiveThreshold(blur,255,1,1,11,1)
    blur_thresh = cv2.GaussianBlur(thresh,(5,5),5)
    return blur_thresh

for n in np.arange(0, num_cards):
    contours[n] = contours[n].reshape(len(contours[n]), 2).astype(np.float32)
    corners = bu.arrange_vertices(bu.find_corners(contours[n]))
    print(f'Card {n} corners: {corners}')
    # Generate 3x3 perspective transform matrix
    m = cv2.getPerspectiveTransform(corners, v_transform)
    # Warp perspective
    output = cv2.warpPerspective(img_r.copy(), m, (450, 450))
    # min_diff = cv2.norm(gray(imgs[0]), gray(output), norm_type)
    # min_img = imgs[0]
    min_diff = 0
    min_img = 0
    for i, card in enumerate(imgs):
        diff = cv2.absdiff(preprocess(card), preprocess(output))
        diff = cv2.GaussianBlur(diff, (5, 5), 5)
        flag, diff = cv2.threshold(diff, 200, 255, cv2.THRESH_BINARY)
        norm = np.sum(diff)
        # diff = np.subtract(gray(card), gray(output))
        # # diff = np.subtract(card, output)
        # norm = np.sum(abs(diff))
        # print(norm)
        # diff = cv2.norm(gray(card), gray(output), norm_type)
        print(f'{i}: Diff against {answers[i]} is {norm}')
        if i == 0:
            min_diff = norm 
            min_img = 0
        elif norm < min_diff:
            min_diff = norm 
            min_img = i
    # print(f'Difference between {answers[0]} is {cv2.norm(imgs[0], output, norm_type)}')
    # print(f'Difference between {answers[1]} is {cv2.norm(imgs[1], output, norm_type)}')
    # print(f'Difference between {answers[2]} is {cv2.norm(imgs[2], output, norm_type)}')
    # print(f'Difference between {answers[3]} is {cv2.norm(imgs[3], output, norm_type)}')
    # Show the output image
    # reference.append(output)
    print(f'Card {n} is {answers[min_img]} and diff is {min_diff}')
    cv2.imshow(f'Card {n}', output)
    cv2.imshow(f'Match {n}', imgs[min_img])
    # cv2.imshow(f'Solution', imgs[5])
    # cv2.imshow('AH', imgs[0])
    # cv2.imshow('2H', imgs[1])
    # cv2.waitKey(30)
    # answers.append(input('Card is:'))

# print(answers)
# with open('answers.txt', 'wb') as f:
#     pickle.dump(answers, f)
# with open('ref.txt', 'wb') as f:
#     data = pickle.dump(reference, f)

# Destroy window after key-press
cv2.waitKey(0)
cv2.destroyAllWindows()
