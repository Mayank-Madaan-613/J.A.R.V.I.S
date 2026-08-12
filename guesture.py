import cv2
import mediapipe as mp
import pyautogui
import math
import time 
# Screen size
screen_w, screen_h = pyautogui.size()


# Webcam
cap = cv2.VideoCapture(0)

# MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

clicked = False
pinch_time=None
mute_time=None
mute=False
mouse_mode=False
mode_time=None

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)

    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:

        for hand in results.multi_hand_landmarks:

            # Draw landmarks
            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

            landmarks = hand.landmark

            # middle finger tip
            middle_tip = landmarks[12]
            middle_ip=landmarks[10]

            mx = int(middle_tip.x * w)
            my = int(middle_tip.y * h)
            # index tip
            index_tip = landmarks[8]
            index_ip=landmarks[6]

            ix = int(index_tip.x * w)
            iy = int(index_tip.y * h)
            i_ip_x=int(index_ip.x * w)
            i_ip_y=int(index_ip.y * h)


            thumb_tip=landmarks[4]
            thumb_ip=landmarks[3]
            tx=int(thumb_tip.x *w)
            ty=int(thumb_tip.y *h)
            #thumb is up or down

            thumb_up=(thumb_tip.y<thumb_ip.y)
            wrist=landmarks[0]
            wx=int(wrist.x * w)
            wy=int(wrist.y * h)

            ring_ip=landmarks[14]
            ring_tip=landmarks[16]
            ring_below=landmarks[13]
            r_b_x=int(ring_below.x*w)
            r_b_y=int(ring_below.y*h)
            rx=int(ring_tip.x*w)
            ry=int(ring_tip.y*h)
            r_ip_y=int(ring_ip.y*h)
            r_ip_x=int(ring_ip.x*w)
            distance_ring_tip_wrist=math.hypot(rx-wx,ry-wy)
            distance_ring_ip_wrist=math.hypot(r_ip_x-wx,r_ip_y-wy)
            ring_folded=(distance_ring_tip_wrist<distance_ring_ip_wrist)


            pinky_ip=landmarks[18]
            pinky_tip=landmarks[20]
            px=int(pinky_tip.x*w)
            py=int(pinky_tip.y*h)
            p_ip_y=int(pinky_ip.y*h)
            p_ip_x=int(pinky_ip.x*w)
            distance_pinky_tip_wrist=math.hypot(px-wx,py-wy)
            distance_pinky_ip_wrist=math.hypot(p_ip_x-wx,p_ip_y-wy)
            pinky_folded=(distance_pinky_tip_wrist<distance_pinky_ip_wrist)




            distance_index_tip_wrist=math.hypot(ix-wx,iy-wy)
            distance_index_ip_wrist=math.hypot(i_ip_x-wx,i_ip_y-wy)
            index_folded=(distance_index_tip_wrist<distance_index_ip_wrist)



            distance = math.hypot(mx - ix, my - iy)
            cv2.line(frame, (ix, iy), (wx,wy), (0, 0, 0), 2)
            cv2.line(frame, (px, py), (wx,wy), (0, 0, 0), 2)
            cv2.line(frame, (mx, my), (ix, iy), (0, 255, 0), 2)
            cv2.putText(frame, f"Dist: {int(distance)}",(50,100),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)

            distance_thumb_tip_pinky_tip=math.hypot(tx-px,ty-py)
            distance_thumb_tip_index_tip=math.hypot(tx-ix,ty-iy)
            cv2.putText(frame, f"click:{distance_thumb_tip_index_tip}",(50,150),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
            distance_thumb_tip_bel_ring=math.hypot(tx-r_b_x,ty-r_b_y)
            if distance_thumb_tip_bel_ring<25:
                if mode_time is None:
                    mode_time=time.time()
                if time.time()-mode_time>2:
                    mouse_mode=not(mouse_mode)
                    mode_time=None
            if mouse_mode:
                pyautogui.moveTo(thumb_tip.x*screen_w,thumb_tip.y*screen_h)
                if int(distance_thumb_tip_index_tip)<25:
                    pyautogui.doubleClick()

            cv2.putText(frame, f"mode:{mouse_mode}",(50,200),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),3)
            # Click when pinched
            if distance < 27:
                if pinch_time is None:
                    pinch_time=time.time()
                
                if not clicked and time.time()-pinch_time >0.7:
                    pyautogui.hotkey('alt','f4')
                    clicked = True
            else:
                clicked = False
                pinch_time=None
            if thumb_up and index_folded and pinky_folded and ring_folded:
                clicked=True
                pyautogui.press("volumeup")
                cv2.putText(frame, f"thumb: up",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
            elif not(thumb_up) and index_folded and pinky_folded and ring_folded:
                clicked=True
                pyautogui.press("volumedown")
                cv2.putText(frame, f"thumb: down",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
            else:
                cv2.putText(frame, f"thumb: NONE",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
            if distance_thumb_tip_pinky_tip<20:
                if mute_time is None:
                    mute_time=time.time()
                if not mute and time.time()-mute_time>0.5:
                    pyautogui.press("volumemute")
                    mute=True
            else:
                mute=False
                mute_time=None


    cv2.imshow("jarvis trials", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break
    
cap.release()
cv2.destroyAllWindows()