import cv2
import d3dshot
import time
import pytesseract
import re

start_time = time.time()
time.sleep(2)

d = d3dshot.create(capture_output="numpy")
d.display = d.displays[0]

def analyse(img):
    text = pytesseract.image_to_string(img, lang = 'eng', config='--psm 8 -c tessedit_char_whitelist=0123456789.')
    text = re.sub(r'[^\d.]', "", text)
    if text.replace('.','',1).isnumeric():
        # print(text)
        return(float(text))
    else:
        print(f"Not a number : {text}")
        return(0)

while True:
    time.sleep(0.1)
    #get image
    img = d.screenshot()
    speed = img[1005:1035, 1700:1780]
    dist = img[1005:1035, 1780:1880]

    print(f"Generated at time {time.time()- start_time}")
    print(f"Speed : {analyse(speed)}")
    print(f"Dist : {analyse(dist)}")
