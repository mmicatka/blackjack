# @file build_references.py
# @date Fri Apr 6 2018 16:04:21
# @author Matthew Chan
# @brief Generate reference images for all playing cards

# Project dependencies
import numpy as np
import cv2
import pickle
import blackjack_util as bu
import os

def build_ref(img_file, answers, reference):
    # Declare constants
    AREA_LOWER_BOUND = 400000
    AREA_UPPER_BOUND = 630000

    # Read input image (in gray-scale)
    img = cv2.imread(f'./img/ref/{img_file}') 
    # Down-scale image 
    # img_r = rescale(img, 0.25)
    img_r = img.copy()

    # Apply pre-processing to the image
    preprocess_img = bu.preprocess(img_r)

    # Identify contours in the image
    image, contours, hierarchy = cv2.findContours(preprocess_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

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

    v_transform = np.array([ [0,0],[450,0],[450,450],[0,450] ], np.float32)

    for n in np.arange(0, num_cards):
        contours[n] = contours[n].reshape(len(contours[n]), 2).astype(np.float32)
        corners = bu.arrange_vertices(bu.find_corners(contours[n]))
        # print(f'Card {n} corners: {corners}')
        # Generate 3x3 perspective transform matrix
        m = cv2.getPerspectiveTransform(corners, v_transform)
        # Warp perspective
        output = cv2.warpPerspective(img_r.copy(), m, (450, 450))
        reference.append(output)
        # Show the output image
        cv2.imshow(f'Card {n}', output)
        cv2.waitKey(30)
        answers.append(input(f'Card {n} is: '))

    # print(answers)

    # Destroy window after key-press
    # cv2.waitKey(0)
    cv2.destroyAllWindows()

answers = []
references = []

for f in os.listdir('./img/ref'):
    if f.endswith('.jpg'):
        build_ref(f, answers, references)

with open('s_answers.txt', 'wb') as f:
    pickle.dump(answers, f)
with open('s_ref.txt', 'wb') as f: 
    pickle.dump(references, f)
