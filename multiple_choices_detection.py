# import the necessary packages
import argparse
import cv2
import numpy as np

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
args = vars(ap.parse_args())
 
# load the image, convert it to grayscale, and blur it slightly
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# show the original
cv2.imshow("Original", image)

# apply Otsu's thresholding method to binarize the warped piece of paper
thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
#cv2.imshow("thresh", thresh)

# perform connected components analysis on the thresholded images and
# initialize the mask to hold only the components suitable in
_, labels = cv2.connectedComponents(thresh)
mask = np.zeros(thresh.shape, dtype="uint8")

# loop over the unique components
for (i, label) in enumerate(np.unique(labels)):
    # if this is the background label, ignore it
    if label == 0:
        continue
    # otherwise, construct the label mask to display only connected components for
    # the current label
    labelMask = np.zeros(thresh.shape, dtype="uint8")
    labelMask[labels == label] = 255
    numPixels = cv2.countNonZero(labelMask)
    # if the number of pixels in the component is eligible,
    # add it to the mask 
    if numPixels > 250 and numPixels < 500: # edit range of number pixels for component here
        mask = cv2.add(mask, labelMask)
        
#cv2.imshow("Mask", mask)

cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
'''
cv2.drawContours(image, cnts, -1, (0, 0, 255), 2)
cv2.imshow("Contours", image)
'''
questionCnts = []
# loop over the contours
for c in cnts:
	# compute the bounding box of the contour, then use the
	# bounding box to derive the aspect ratio
	(x, y, w, h) = cv2.boundingRect(c)
	ar = w / float(h)
 
	# in order to label the contour as a question, region
	# should be sufficiently wide, sufficiently tall, and
	# have an aspect ratio approximately from 0.5 to 1.5
	if w >= 10 and h >= 10 and ar >= 0.5 and ar <= 1.5: # edit range of ar for component here
		questionCnts.append(c)

clone = image.copy()
cv2.drawContours(clone, questionCnts, -1, (0, 0, 255), 2)
cv2.imshow("All marked bubbles", clone)

cv2.waitKey(0)

# save the image
cv2.imwrite("output.jpg", clone)
