import cv2

def mask_yellow(img):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_range = (10, 60, 130)
    upper_range = (30, 255, 255)

    img_mask = cv2.inRange(img_hsv, lower_range, upper_range)

    return img_mask


# find yellow road location from input frame
def contour_yellow(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Using threshold for line detection
    ret, img_binary = cv2.threshold(img_gray, 127, 255, 0)

    img_mask = mask_yellow(img)

    yellowcnts = cv2.findContours(img_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    if len(yellowcnts) > 0:

        yellow_area = max(yellowcnts, key=cv2.contourArea)
        (xg, yg, wg, hg) = cv2.boundingRect(yellow_area)
        cv2.rectangle(img, (xg, yg), (xg + wg, yg + hg), (0, 0, 255), 2)
        loc = (xg, yg, wg, hg)

    else:
        loc = (0, 0, 0, 0)

    return loc


def yellow_location(frame):
    y_loc = contour_yellow(frame)
    xg, yg, wg, hg = y_loc[0], y_loc[1], y_loc[2], y_loc[3]

    # case1: curved yellow block detected
    if (wg >= 220):
        cw = 1
        cx = xg + int(1 / 2 * wg)
        cy = yg + int(1 / 2 * hg)
        cv2.line(frame, (cx, cy), (cx, cy), (255, 0, 0), 5)

    # case2: straight yellow block detected
    elif (wg >= 100):
        cw = 0
        cx = xg + int(1 / 2 * wg)
        cy = yg + int(1 / 2 * hg)
        cv2.line(frame, (cx, cy), (cx, cy), (255, 0, 0), 5)

    else:
        cw = 0
        cx = 0

    y_point = (cw, cx)

    return y_point

#find location of the yellow block from the input video
def find_location(point):
    cw, cx = point[0], point[1]
    if (cw == 1):
        if (cx < 200):
            location = "left"
        elif (cx > 300):
            location = "right"
        else:
            location = "stop"

    elif (cw == 0 and cx > 0):
        location = "ahead"

    else:
        location = "stop"

    return location
