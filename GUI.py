import sys
import PySimpleGUI as sg
import cv2
import cvzone
import math
import time
import threading
import serial
from ultralytics import YOLO


#ser = None  # Initialize the serial port as None
ser = serial.Serial('COM13', 9600, timeout=1)

camera_index = 0
stop_thread = False

# Create the main window


def create_display_thread():
    global display_thread
    display_thread = threading.Thread(target=classifier)
    display_thread.daemon = True  # Set as a daemon thread
    display_thread.start()

def init_serial_port():
    global ser
    if ser is None or not ser.is_open:
        ser = serial.Serial('COM13', 9600, timeout=1)

def send_command(command):
    init_serial_port()  # Open the serial port
    ser.write(command.encode())
    ser.close()  # Close the serial port when done

def jammer_initial_state():
    send_command('q')

def jammer_stop():
    send_command('0')

def jammer_on():
    send_command('1')

def run_jammer_initial_state():
    threading.Thread(target=jammer_initial_state).start()

def run_jammer_off():
    threading.Thread(target=jammer_stop).start()

def run_jammer():
    threading.Thread(target=jammer_on).start()

def send_command(command):
    ser.write(command.encode())
    time.sleep(1)

def display_image(image_path):
    image = cv2.imread(image_path)
    cv2.imshow('2.jpg', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def classifier():

    #run_jammer_off()

    global stop_thread
    drone_detected_time = None

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Camera index {camera_index} is not in range. Please switch to a proper camera.")
        return
    print("cam is starting......")
    cap.set(3, 480)
    cap.set(4, 720)
    model = YOLO("yolo-Weights/best_demo.pt")
    classNames = ['Bird', 'Drone']
    prev_frame_time = 0
    print("wait......")
    while not stop_thread:
        new_frame_time = time.time()
        success, img = cap.read()

        if not success or img is None:
            continue

        results = model(img, stream=True)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1
                cvzone.cornerRect(img, (x1, y1, w, h))

                # Confidence
                conf = math.ceil((box.conf[0] * 100)) / 100

                # Class Name
                cls = int(box.cls[0])

                cvzone.putTextRect(img, f'{classNames[cls]} {conf}', (max(0, x1), max(35, y1)), scale=1,
                                   thickness=1)

                if classNames[cls] == "Drone":
                    print("Drone Detected")
                    drone_detected_time = time.time()
                    run_jammer()

        if drone_detected_time and time.time() - drone_detected_time > 10:
            print("Turning off the jammer after 10 seconds")
            run_jammer_off()
            drone_detected_time = None

        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time

        if not stop_thread:
            window['-CLASSIFIER-'].update(data=cv2.imencode('.png', img)[1].tobytes())

    cap.release()
    cv2.destroyAllWindows()

def clear_output():
    window['-CLI-'].update('')

def stop_classifier():
    global stop_thread
    stop_thread = True
    if display_thread and display_thread.is_alive():
        display_thread.join()



layout = [
    [sg.Text('Previously Entered : ', key='pp', justification='center'), sg.Text('None', key='ppn')],
    [sg.Text('Camera Index:',text_color='Black'), sg.InputText(default_text=str(camera_index), key='-CAMERA-INDEX-'), sg.Button('Set')],
    [sg.Button('RUN', key='Button1', expand_x=True,button_color='RED')],
    [sg.Button('STOP', key='Button2', expand_x=True)],
    [sg.Button('RUN-JAMMER ONLY', key='Button3', expand_x=True)],
    [sg.Button('STOP-JAMMER', key='Button4', expand_x=True)],
    #[sg.Button('JAMMER INITIAL STATE', key='Button5', expand_x=True)],
    [sg.Text('To Special Permission run: "sudo run jammer-Boost"', expand_x=True)],
    [sg.Input(key='input',size=(51, 5)), sg.Button('ENTER', key='Button6',expand_x=True)],
    [sg.Text('CLI Output:', expand_x=True)],
    [sg.Output(key='-CLI-', size=(50, 5)), sg.Button('Clear All', key='Button7',size=(10, 5), expand_x=True)],  # Add a button to clear the CLI output
    [sg.Image(filename='', key='-CLASSIFIER-')]
]

window = sg.Window('Jammer', layout)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == 'Set':
        try:
            camera_index = int(values['-CAMERA-INDEX-'])
            print(f"Camera index set to {camera_index}")
        except ValueError:
            print("Please enter a valid camera index (an integer).")

    if event == 'Button1':
        print("RUN")
        create_display_thread()


    if event == 'Button2':
        print("STOP")
        stop_classifier()
        sys.exit(0)


    if event == 'Button3':
        print("RUN-JAMMER-ONLY")
        run_jammer()

    if event == 'Button4':
        print("STOP-JAMMER")
        run_jammer_initial_state()

#    if event == 'Button5':
 #       print("JAMMER-INITIAL-STATE")
  #      run_jammer_initial_state()

    if event == 'Button6':
        window['ppn'].update(values['input'])
        print(values['input'])

    if event == 'Button7':
        # Handle the "Clear All" button
        clear_output()

    if event == 'Set':
        try:
            camera_index = int(values['-CAMERA-INDEX-'])
            print(f"Camera index set to {camera_index}")
        except ValueError:
            print("Please enter a valid camera index (an integer).")

window.close()
