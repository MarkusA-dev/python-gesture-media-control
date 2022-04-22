#from asyncio.windows_events import NULL
import win32api
import cv2
import mediapipe as mp
import math 

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

NEXT_SONG = 0xB0
PREV_SONG = 0xB1
PAUSE = 0xB3

frameWidth = 800
frameHeight = 800

cap = cv2.VideoCapture(0)
cap.set(3, frameWidth)
cap.set(4, frameHeight)

cap.set(10, 100)

count = 0

def getAngleTest(xstart, ystart, xend, yend):
    xdiff = xend - xstart
    ydiff = yend - ystart
    degrees = math.atan2(ydiff, xdiff)*180/math.pi
    return (360+round(degrees))%360

def testFingerDir(list, counting):
    joints = [list[6], list[8], list[10], list[12], list[14], list[16]]
    #print(counting)

    angle1 = getAngleTest(joints[0][1], joints[0][2], joints[1][1], joints[1][2])
    angle2 = getAngleTest(joints[2][1], joints[2][2], joints[3][1], joints[3][2])
    angle3 = getAngleTest(joints[4][1], joints[4][2], joints[5][1], joints[5][2])

    if counting % 30 == 0:
        if (angle1 in range(150, 200)) and (angle2 in range(150, 200)) and not (angle3 in range(150, 200)):
            win32api.keybd_event(NEXT_SONG, 0)

        elif (angle1 in range(340, 360) or angle1 in range(0, 40)) and (angle2 in range(340, 360) or angle2 in range(0, 40)) and not (angle3 in range(340, 360) or angle3 in range(0, 40)):
            win32api.keybd_event(PREV_SONG, 0)

        elif angle1 in range(230, 300) and angle2 in range(230, 300) and not angle3 in range(230, 300):
            win32api.keybd_event(PAUSE, 0)

with mp_hands.Hands(
    model_complexity = 1,
    min_detection_confidence = 0.75,
    min_tracking_confidence = 0.6,
    max_num_hands = 1
    ) as hands:
        while cap.isOpened():
            success, image = cap.read()
            image.flags.writeable = False
            image =  cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )
            lmList = []
            if results.multi_hand_landmarks:
                myHand = results.multi_hand_landmarks[0]
                for id, lm in enumerate(myHand.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])   
            if len(lmList) == 0:
                count=0
            if len(lmList) != 0:
                count = count + 1
                print(getAngleTest(lmList[6][1], lmList[6][2], lmList[8][1], lmList[8][2]))
                testFingerDir(lmList, count)
            if count == 30:
                count = 0
            cv2.imshow("Result", cv2.flip(image, 1))
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

cap.release()