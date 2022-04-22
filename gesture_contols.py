import win32api
import cv2
import mediapipe as mp
import math 

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

#Creating variables that store the keys i need
NEXT_SONG = 0xB0
PREV_SONG = 0xB1
PAUSE = 0xB3

frameWidth = 800
frameHeight = 800

cap = cv2.VideoCapture(0)
cap.set(3, frameWidth)
cap.set(4, frameHeight)
cap.set(10, 125)

count = 0

#Some math to calculate the angle of the two points, this is used to calculate the angle between two joints
def getAngle(xstart, ystart, xend, yend):
    xdiff = xend - xstart
    ydiff = yend - ystart
    degrees = math.atan2(ydiff, xdiff)*180/math.pi
    return (360+round(degrees))%360

#Function for testing finger direction, takes in a list of joints
def Finger_dir(list, counting):

    #Making an array of all needed fingers to make thing easier, mainly a leftover that I will probably remove later
    joints = [list[6], list[8], list[10], list[12], list[14], list[16]]
    angle1 = getAngle(joints[0][1], joints[0][2], joints[1][1], joints[1][2])
    angle2 = getAngle(joints[2][1], joints[2][2], joints[3][1], joints[3][2])
    angle3 = getAngle(joints[4][1], joints[4][2], joints[5][1], joints[5][2])

    #Triggering a test every 30 loops of the main function with a hand detected
    if counting % 30 == 0:
        if (angle1 in range(150, 200)) and (angle2 in range(150, 200)) and not (angle3 in range(150, 200)):
            win32api.keybd_event(NEXT_SONG, 0)

        #Test if index and middle finger are pointing to the left while also testing if the ringfinger is down
        elif (angle1 in range(340, 360) or angle1 in range(0, 40)) and (angle2 in range(340, 360) or angle2 in range(0, 40)) and not (angle3 in range(340, 360) or angle3 in range(0, 40)):
            win32api.keybd_event(PREV_SONG, 0)

        #Test if index and middle finger are pointing to the upwards while also testing if the ringfinger is down
        elif angle1 in range(230, 300) and angle2 in range(230, 300) and not angle3 in range(230, 300):
            win32api.keybd_event(PAUSE, 0)

#Setting up the mediapipe hand model with some variables, only one that's really important to explain here is that the max_num_hands is 1 because having two hands on the screen caused some issues
with mp_hands.Hands(
    model_complexity = 1,
    min_detection_confidence = 0.8,
    min_tracking_confidence = 0.6,
    max_num_hands = 1
    ) as hands:

        #sets up loop that runs while capture is open 
        while cap.isOpened():
            #if successful read the image from the webcam
            success, image = cap.read()
            image.flags.writeable = False
            #convert color mode, this improved the detection ability
            image =  cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            #If a hand is recognized on the screen run a for loop
            if results.multi_hand_landmarks:
                #For loop that goes through all the landmarks of the hand and draws the lines and landmarks, this can be commented out since i'm not drawing anything to the screen
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )

            #Creating a list that will store the joint information ID, x position, y position
            lmList = []
            if results.multi_hand_landmarks:
                myHand = results.multi_hand_landmarks[0]
                for id, lm in enumerate(myHand.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
            
            #set the count to zero if no hand is detected
            if len(lmList) == 0:
                count=0

            #If a hand is detected add to count every loop, prints the angle of the index finger and calls the Finger_dir function that tests for conditions
            if len(lmList) != 0:
                count = count + 1
                print(f"I see a hand with the index finger at {getAngle(lmList[6][1], lmList[6][2], lmList[8][1], lmList[8][2])} angle")
                Finger_dir(lmList, count)

            #Set count to 0 whenever it is 30, to prevent too large of a number
            if count == 30:
                count = 0

            #Line for showing the window where the image is shown. Commented out as I mainly used this while testing
            #cv2.imshow("Result", cv2.flip(image, 1))

            #Waits for the q key to be pressed to break the loop
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

cap.release()