import cv2
import numpy as np

def rectify(h):
    # Ensure that the points are ordered correctly
    h = h.reshape((4, 2))
    hnew = np.zeros((4, 2), dtype=np.float32)

    add = h.sum(axis=1)
    hnew[0] = h[np.argmin(add)]
    hnew[2] = h[np.argmax(add)]

    diff = np.diff(h, axis=1)
    hnew[1] = h[np.argmin(diff)]
    hnew[3] = h[np.argmax(diff)]

    return hnew

def scan_document(image):
    # Resize image if necessary to a fixed size (e.g., (1500, 880))
    image = cv2.resize(image, (800, 800))

    # Preprocess image (convert to grayscale, blur, and find edges)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)

    # Find contours and sort by contour area
    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    target = None
    for c in contours:
        p = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * p, True)

        if len(approx) == 4:
            target = approx
            break

    if target is None:
        # Handle case where no document contour is found
        return None

    # Perform perspective transformation
    approx = rectify(target)
    pts2 = np.float32([[0, 0], [800, 0], [800, 800], [0, 800]])

    M = cv2.getPerspectiveTransform(approx, pts2)

    # Get the dimensions of the input image for accurate transformation
    h, w = image.shape[:2]

    # Apply perspective transformation
    dst = cv2.warpPerspective(image, M, (w, h))

    # Crop to the region of interest defined by pts2
    cropped = dst[0:800, 0:800]

    return cropped
