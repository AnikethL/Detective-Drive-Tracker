import cv2

# Read image
image = cv2.imread('car.jpg')

# Window from plain imshow() command
cv2.imshow('Window from plain imshow()', image)

# Custom window
cv2.namedWindow('custom window', cv2.WINDOW_KEEPRATIO)
cv2.imshow('custom window', image)
cv2.resizeWindow('custom window', 200, 200)

cv2.waitKey(0)
cv2.destroyAllWindows()