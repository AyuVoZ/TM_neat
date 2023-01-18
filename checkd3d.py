import d3dshot
import time
import cv2

time.sleep(2)
d = d3dshot.create(capture_output="numpy")
d.display = d.displays[1]
img = d.screenshot()
cv2.imshow("d3dshot", img)
cv2.waitKey(0)