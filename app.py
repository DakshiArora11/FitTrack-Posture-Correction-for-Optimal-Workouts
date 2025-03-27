import cv2
import mediapipe as mp
import numpy as np
import speech_recognition as sr
import pyttsx3
import threading
from flask import Flask, render_template, request, session, url_for, redirect

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def play_audio_feedback(feedback, prev):
    engine = pyttsx3.init()
    if feedback != prev:
        engine.say(feedback)
        engine.runAndWait()

    
def audio_feedback_thread(feedback, prev):
    thread = threading.Thread(target=play_audio_feedback, args=(feedback, prev,))
    thread.start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods = ['post'])
def submit():
    session['full'] = False
    selected_exercise = request.form.get('exercise')
    
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    def findAngle(joint1, joint2, joint3):
        joint1 = np.array(joint1)
        joint2 = np.array(joint2)
        joint3 = np.array(joint3)
        
        radians = np.arctan2(joint3[1] - joint2[1], joint3[0] - joint2[0]) - np.arctan2(joint1[1] - joint2[1], joint1[0] - joint2[0])

        angle = np.abs(radians*180.0/np.pi)

        return angle


    def plank():
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
        knee = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]

        angle = findAngle(shoulder, hip, knee)

        angle = angle.round(3)

        cv2.putText(
            background,
            str(angle),
            tuple(np.multiply(hip, resolution).astype(int)),
            cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 2, 
        )
        
        feedback = ""

        if angle < 170 or angle > 190:
            feedback = "back not straight"
            cv2.putText(
                        background,
                        feedback,
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.75,
                        (0,0,255),
                        2,
                        cv2.LINE_AA
                    )
        else:
            feedback = "Good form"
            cv2.putText(
                        background,
                        feedback,
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.75,
                        (0,200,0),
                        2,
                        cv2.LINE_AA
                    )
        
        return feedback


    def barbellBicepCurl():

        leftHip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
        leftShoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
        leftElbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y]
        leftWrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]

        rightHip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y]
        rightShoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y]
        rightElbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y]
        rightWrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y]

        leftElbowAngle = findAngle(leftShoulder, leftElbow, leftWrist)
        rightElbowAngle =  findAngle(rightShoulder, rightElbow, rightWrist)

        leftShoulderAngle = findAngle(leftHip, leftShoulder, leftElbow)
        rightShoulderAngle = findAngle(rightHip, rightShoulder, rightElbow)


        leftElbowAngle = leftElbowAngle.round(3)
        rightElbowAngle = rightElbowAngle.round(3)
        leftShoulderAngle = leftShoulderAngle.round(3)
        rightShoulderAngle = rightShoulderAngle.round(3)

        if (leftElbowAngle > 180.0):
            leftElbowAngle = 360.0 - leftElbowAngle

        if (rightElbowAngle > 180.0):
            rightElbowAngle = 360.0 - rightElbowAngle

        elbowAngle = (leftElbowAngle + rightElbowAngle) / 2.0
        shoulderAngle = (leftShoulderAngle + rightShoulderAngle) / 2.0

        cv2.putText(
            background,
            str(leftElbowAngle),
            tuple(np.multiply(leftElbow, resolution).astype(int)),
            cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,0), 2, 
        )

        cv2.putText(
            background,
            str(rightElbowAngle),
            tuple(np.multiply(rightElbow, resolution).astype(int)),
            cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,0), 2, 
        )



        
        cv2.putText(
            background,
            str(leftShoulderAngle),
            tuple(np.multiply(leftShoulder, resolution).astype(int)),
            cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,0), 2, 
        )

        cv2.putText(
            background,
            str(rightShoulderAngle),
            tuple(np.multiply(rightShoulder, resolution).astype(int)),
            cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,0), 2, 
        )

        feedback = ""

        if (shoulderAngle > 20):
            feedback = "Upper arm moving"
            cv2.putText(
                        background,
                        feedback,
                        (350, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.75,
                        (0,0,255),
                        2,
                        cv2.LINE_AA
                    )
            return feedback

        
        if ( (elbowAngle < 50) & (elbowAngle > 10) & (not session['full']) ):
            feedback = "Push more..."
            cv2.putText(
                        background,
                        feedback,
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.75,
                        (0,200,200),
                        2,
                        cv2.LINE_AA
                    )
        elif (elbowAngle < 10):
            feedback = "Peak Contraction achieved"
            cv2.putText(
                        background,
                        feedback,
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.75,
                        (0,200,0),
                        2,
                        cv2.LINE_AA
                    )
            session['full'] = True
        elif (elbowAngle > 150):
            session['full'] = False

        return feedback


        
    def getStartCommand():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio = recognizer.listen(source)

            try:
                text = recognizer.recognize_google(audio)
                if (text.lower() == "start"):
                    return True           
            except sr.RequestError as e:
                print("Error fetching results; {0}".format(e))

        return False


    def getStopCommand():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio = recognizer.listen(source)

            try:
                text = recognizer.recognize_google(audio)
                if (text.lower() == "stop"):
                    return False           
            except sr.RequestError as e:
                print("Error fetching results; {0}".format(e))


        return True

        tracking = False

    cap = cv2.VideoCapture(0)

    cv2.namedWindow('feed')

    window_x, window_y, window_width, window_height = cv2.getWindowImageRect('feed')
    resolution = (window_width, window_height)

    global prev
    prev = ""
    curr = ""

    with mp_pose.Pose(min_detection_confidence = .5, min_tracking_confidence = .5) as pose:
        while (cap.isOpened()):
            ret, frame = cap.read()

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            background = np.zeros((480, 640, 3), dtype=np.uint8)
            background.fill(255)

            try:
                landmarks = results.pose_landmarks.landmark

                cv2.rectangle(background, (0,0), (window_width,60), (255,255,255), -1)

                
                if (selected_exercise == "plank"):
                    curr = plank()
                elif (selected_exercise == "bicep_curl"):
                    curr = barbellBicepCurl()
                else:
                    return redirect(url_for('home'))

                if curr:
                    audio_feedback_thread(curr, prev)
                    prev = curr
                
            except:
                pass
            
            mp_drawing.draw_landmarks(background, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow('feed', background)

            key = cv2.waitKey(1)
            if key == 27 or cv2.getWindowProperty('feed', cv2.WND_PROP_VISIBLE) < 1:
                break

    cap.release()
    cv2.destroyAllWindows()

    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)