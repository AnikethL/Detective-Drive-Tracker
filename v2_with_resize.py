import cv2
import dlib
import time
import math

carCascade = cv2.CascadeClassifier('myhaar.xml')

video = cv2.VideoCapture('cars.mp4')
xlow,xhigh,ylow,yhigh= 0,0,0,0

WIDTH, HEIGHT = 1770, 1000
aspectRatio = WIDTH/HEIGHT
# ppm = 8.8 # depends on scale in video
ppm = 45
clr=False



def estimateSpeed(loc1, loc2):
	d_pixels = math.sqrt(math.pow(loc2[0] - loc1[0], 2) + math.pow(loc2[1] - loc1[1], 2))
	# ppm = location2[2] / carWidht
	
	d_meters = d_pixels / ppm
	#print("d_pixels=" + str(d_pixels), "d_meters=" + str(d_meters))
	fps = 24 # depends on fps of video
 
	speed = d_meters * fps * 3.6 # always the same
	return speed

def trackMultipleObjects():
	rectangleColor = (0, 255, 0)
	frameCounter = 0
	currentCarID = 0
	
	carTracker = {}
	carNumbers = {}
	carLocation1 = {}
	carLocation2 = {}
	speed = [None] * 1000


	while True:
		start_time = time.process_time()
		rc, image = video.read()        

        
		if not type(image):
			break
		
		image = cv2.resize(image, (WIDTH, HEIGHT))
		resultImage = image.copy()
		cv2.rectangle(resultImage, (xlow, ylow), (xhigh, yhigh), (255, 255, 255), 2)
            
		frameCounter += 1
		
		carIDtoDelete = []

		for carID in carTracker.keys():
			trackingQuality = carTracker[carID].update(image)
			
			if trackingQuality < 7:
				carIDtoDelete.append(carID)
				
		for carID in carIDtoDelete:
			carTracker.pop(carID, None)
			carLocation1.pop(carID, None)
			carLocation2.pop(carID, None)
		
		if not (frameCounter % 5):
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			cars = carCascade.detectMultiScale(gray, 1.1, 13, 18, (24, 24))
			
			for (_x, _y, _w, _h) in cars:
				x = int(_x)
				y = int(_y)
				w = int(_w)
				h = int(_h)
			
				x_bar = x + 0.5 * w
				y_bar = y + 0.5 * h
				
				matchCarID = None
			
				for carID in carTracker.keys():
					trackedPosition = carTracker[carID].get_position()
					
					t_x = int(trackedPosition.left())
					t_y = int(trackedPosition.top())
					t_w = int(trackedPosition.width())
					t_h = int(trackedPosition.height())
					
					t_x_bar = t_x + 0.5 * t_w
					t_y_bar = t_y + 0.5 * t_h
				
					if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and (x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))):
						matchCarID = carID
				
				if matchCarID is None:	
					doubleBox=False
					for cID in carTracker.keys():
						if abs(y-carLocation1[cID][1]) <= 80:
							doubleBox = True
						
					if not doubleBox:
						tracker = dlib.correlation_tracker()
						tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))

						if xlow <= x <= xhigh and ylow <= y <= yhigh:
							carTracker[currentCarID] = tracker
							carLocation1[currentCarID] = [x, y, w, h]

							currentCarID = currentCarID + 1
		
		#cv2.line(resultImage,(0,480),(1280,480),(255,0,0),5)


		for carID in carTracker.keys():
			trackedPosition = carTracker[carID].get_position()
					
			t_x = int(trackedPosition.left())
			t_y = int(trackedPosition.top())
			t_w = int(trackedPosition.width())
			t_h = int(trackedPosition.height())
			
   
			if xlow <= t_x <= xhigh-t_w and ylow <= t_y <= yhigh-t_h:
				cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), rectangleColor, 4)
				
				# speed estimation
				carLocation2[carID] = [t_x, t_y, t_w, t_h]
		
		end_time = time.time()
		
		if not (end_time == start_time):
			fps = 1.0/(end_time - start_time)
		


		for i in carLocation1.keys():	
			[x1, y1, w1, h1] = carLocation1[i]
			[x2, y2, w2, h2] = carLocation2[i]
	
			carLocation1[i] = [x2, y2, w2, h2]
			
			if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
				if (speed[i] == None or speed[i] == 0) and xlow <= x1 <= xhigh and ylow <= y1 <= yhigh:
					speed[i] = estimateSpeed([x1, y1, w1, h1], [x2, y2, w2, h2])

				#if y1 > 275 and y1 < 285:
				if speed[i] != None and xlow <= x1 <= xhigh and ylow <= y1 <= yhigh:
					cv2.putText(resultImage, str(int(speed[i]*0.621371)) + " mph", (int(x1 + w1/2), int(y1-5)),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        
        
		cv2.namedWindow("result", cv2.WINDOW_KEEPRATIO)
		cv2.imshow("result", resultImage)
		cv2.resizeWindow("result", WIDTH, HEIGHT)

		if cv2.waitKey(33) == 27:
			break
	
	cv2.destroyAllWindows()
 
def shape_selection(event, x, y, flags, param):
    # grab references to the global variables
    global clr, ref_point, xlow, xhigh, ylow, yhigh
    if not clr:
        # if the left mouse button was clicked, record the starting
        # (x, y) coordinates and indicate that cropping is being performed
        if event == cv2.EVENT_LBUTTONDOWN:
            ref_point = [(x, y)]

        # check to see if the left mouse button was released
        elif event == cv2.EVENT_LBUTTONUP:
            # record the ending (x, y) coordinates and indicate that
            # the cropping operation is finished
            ref_point.append((x, y))
            

            # draw a rectangle around the region of interest
            cv2.rectangle(img, ref_point[0], ref_point[1], (255, 255, 255), 2)
            
            p1, p2 = ref_point
            xlow = int(min(p1[0], p2[0])*aspectRatio)
            xhigh = int(max(p1[0], p2[0])*aspectRatio)
            ylow = int(min(p1[1], p2[1])*aspectRatio)
            yhigh = int(max(p1[1], p2[1])*aspectRatio)
			
            clr = True

rc, img = video.read()
cv2.resize(img, (WIDTH, HEIGHT))

cv2.namedWindow("image", cv2.WINDOW_KEEPRATIO)
cv2.imshow("image", img)
cv2.resizeWindow("image", WIDTH, HEIGHT)

clone = img.copy()

cv2.setMouseCallback("image", shape_selection)
while True:
    cv2.imshow("image",img)
    key = cv2.waitKey(1) & 0xFF

    # press 'r' to reset the window
    if key == ord("r"):
        clr=False

    # if the 'c' key is pressed, break from the loop
    elif key == ord("c"):
        cv2.destroyWindow("image")
        break
    
def main():
    # load the image, clone it, and setup the mouse callback function
    

    trackMultipleObjects()

if __name__ == '__main__':
	main()