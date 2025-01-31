import cv2
import numpy as np

lowerOrange = np.array([0, 150, 150])
upperOrange = np.array([15, 255, 255])

lowerGreen = np.array([85, 50, 40])  
upperGreen = np.array([125, 255, 100])  

lowerGrey = np.array([100, 10, 50])
upperGrey = np.array([150, 50, 100])

webcam_video = cv2.VideoCapture(0)




while True:
    success, video = webcam_video.read()

    img = cv2.cvtColor(video, cv2.COLOR_BGR2HSV)

    maskOrange = cv2.inRange(img, lowerOrange, upperOrange)
    maskGreen = cv2.inRange(img, lowerGreen, upperGreen)
    maskGrey = cv2.inRange(img, lowerGrey, upperGrey)

    contoursOrange, _ = cv2.findContours(maskOrange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contoursGreen, _ = cv2.findContours(maskGreen, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contoursGrey, _ = cv2.findContours(maskGrey, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Get the width and height of the frame
    height, width = video.shape[:2]


    cells_y = 100
    cells_x = 100
    grid_width = width // 2
    grid_height = height // 2

    for x in range (0,width, cells_x):
        cv2.line(video, (x,0), (x,height), (0,0,0), 1)
    for y in range (0,width, cells_x):
        cv2.line(video, (0,y), (width,y), (0,0,0), 1)

    for contour in contoursOrange:
        if cv2.contourArea(contour) > 500:
            x, y, w, h = cv2.boundingRect(contour)
           
            # Adjust the coordinates to center (0, 0) in the center of the image
            adjusted_x = x - width // 2
            adjusted_y = y - height // 2
            
            cv2.putText(video, "Orange", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            cv2.putText(video, f"x: {adjusted_x} y: {adjusted_y}", (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    for contour in contoursGreen:
        if cv2.contourArea(contour) > 500:
            x, y, w, h = cv2.boundingRect(contour)
         
            # Adjust the coordinates to center (0, 0) in the center of the image
            adjusted_x = x - width // 2
            adjusted_y = y - height // 2

            cv2.putText(video, "Green", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 128, 0), 2)
            cv2.putText(video, f"x: {adjusted_x} y: {adjusted_y}", (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 128, 0), 2)

    for contour in contoursGrey:
        if cv2.contourArea(contour) > 500:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Adjust the coordinates to center (0, 0) in the center of the image
            adjusted_x = x - width // 2
            adjusted_y = y - height // 2

            cv2.putText(video, "Grey", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (169, 169, 169), 2)
            cv2.putText(video, f"x: {adjusted_x} y: {adjusted_y}", (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (169, 169, 169), 2)

    cv2.imshow("Color Labels", video)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

webcam_video.release()
cv2.destroyAllWindows()
