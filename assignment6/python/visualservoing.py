import time
import cv2
from Scribbler2 import *
import numpy as np
import math
from matplotlib import pyplot as plt



# returns a contour object and an image with the contour overlaid on it (for debuggint)
# if @debug is True, displays all intermediate images and waits for a key press before returning
def find_black_square(imgPath, debug = False):
    # read grayscale image
    origImg = cv2.imread(imgPath)

    gray = cv2.cvtColor(origImg, cv2.COLOR_BGR2GRAY)

    # apply gaussian filter to reduce noise before we do edge detection
    kernel = np.ones((5,5),np.float32)/25
    filtered = cv2.filter2D(gray,-1,kernel)

    # run Canny edge-detection
    edged = cv2.Canny(filtered, 100, 100)

    # blur the edged image to help merge any lines that don't connect but are very close
    kernel2 = np.ones((2,2),np.float32)/4
    edgedBlurred = cv2.filter2D(edged, -1, kernel2)

    # get contours
    cnts, _ = cv2.findContours(edgedBlurred.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # sort contours from largets to smallest
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)

    # find the largest rectangle in the contours list

    for c in cnts[1:]:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            corners = approx
            break

    # draw the original image overlaid with the contour we think is the target black rect
    cntAnnotatedImg = origImg.copy()
    cv2.drawContours(cntAnnotatedImg, [corners], -1, (0,255,0), 3)

    # sort by ascending x-value
    corners = sorted(corners, key=lambda pt: pt[0][0])

    # extract left and right sides and sort by ascending y value
    leftPts = sorted(corners[0:2], key=lambda pt: pt[0][1])
    # print "leftPts:"
    # print leftPts
    rightPts = sorted(corners[2:4], key=lambda pt: pt[0][1])
    # print "rightPts:"
    # print rightPts

    # rearrange in order of increasing quadrant (pretending origin is at the center of the corners)
    corners = np.ndarray(shape=(4,2), dtype=int, order='C')
    corners[0] = rightPts[0]
    corners[1] = leftPts[0]
    corners[2] = leftPts[1]
    corners[3] = rightPts[1]

    # print "corners ordered:"
    # print corners

    square = np.zeros((4,2), np.float32)
    for a in range(len(corners)):
        square[a,1] = corners[a][1]
        square[a,0] = corners[a][0]

    square = square.reshape(-1,2)

    if debug:
        cv2.imshow('original', origImg)
        cv2.imshow('filtered', filtered)
        cv2.imshow('edged', edged)
        cv2.imshow('edgedBlurred', edgedBlurred)
        cv2.imshow('contours', cntAnnotatedImg)
        
        cv2.waitKey(0)


    # convert from np.array to tuple
    # square = np.array([[pt[0][0], pt[0][1]] for pt in square])

    return square, cntAnnotatedImg


# returns F, R, T given an image of a 4" x 4" black square
# F is a boolean representing found
# R is Z rotation in radians
# T is a 2x1 vector for translation in inches
# X is in the left direction on the square
# Y is in the down direction
# Z is in the direction into the square
# (0, 0, 0) origin (goal) is in the center of the black square
def getRT(corners):
    # defines the corners of the object we are tracking in x, y, z space in inches
    objectpoints = np.array([[1, -1, 0], [-1, -1, 0], [-1, 1, 0], [1, 1, 0]], np.float32)
    # objectpoints = np.array([[12, 8, 2], [12, 8, -2], [12, 4, -2], [12, 4, 2]], np.float32)
    kmat = np.array([[1211.2959, 0, 657.15924], [0, 1206.00512, 403.17667], [0, 0, 1]])
    F, R, T = cv2.solvePnP(objectpoints, corners, kmat, None)
    # print "Rvec"
    # print R
    # print "Tvec"
    # print T
    print "R"
    R = R[1]
    print R #Y rotation

    # print "T"
    # print T
    print "T"
    T = np.append(T[0], T[2])
    print T

    return F, R, T


# demo!
sq1, img1 = find_black_square('../start.jpg')
sq2, img2 = find_black_square('../goal.jpg')
F, R, T = getRT(sq1)
cv2.imshow('Start', img1)

cv2.waitKey()
cv2.imshow('Goal', img2)
F, R, T = getRT(sq2)

# get the sign of a number
def sgn(num):
    return 1 if num >= 0 else -1


# robot drive constants
DriveScale = 0.15
WheelRadius = 0.04
WheelDist = 0.08;


# rotate in place a given number of radians
def drive_rotate(scrib, rad):
    uL = -100*sgn(rad)
    uR = 100*sgn(rad)
    radPerSec = scale*(uL-uR)*WheelRadius/WheelDist
    time = rad / radPerSec

    scrib.runCommands([[uL, uR, time]])


# move forward a given distance (in inches)
def drive_forward(scrib, inches):
    u = 100
    speed = u*DriveScale*WheelRadius
    time = inches / speed

    scrib.runCommands([[u, u, time]])



# move to a new position and orientation as specified by the rotation and translation matrices given
# @param theta - the amount to rotate
def line_up(theta, trans, targetPos):
    # turn in the direction of the new position we should be in
    # TODO:

    # move the right amount to get there
    # TODO:

    # rotate to face the direction we're supposed to
    # TODO:



def main():
    # connect and initialize Scribbler robot
    fname = "log-%d.txt" % time.time()
    s = Scribbler2('/dev/tty.Fluke2-0610-Fluke2',fname)
    print 'Connected!'
    s.setForwardness(1)

    targetPos = np.append(0, -12)

    while True:
        # take a picture
        pic_fname = "pic-%d.jpg" % time.time()
        pic = s.takePicture('jpeg')
        s.savePicture(pic, pic_fname)

        corners, cntAnnotatedImg = find_black_square(pic_fname)
        found, rot, trans = getRT(corners)

        if !found:
            printf("Error: getRT() failed... exiting")
            break

        # see if we're at the target point yet
        if rot < math.pi / 8 and np.linalg.norm(trans - targetPos) < 4:
            print("Made it!")
            break

        line_up(rot, trans, targetPos)


    s.close();

