import cv2
import tkinter as tk
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
import face_recognition_models
import face_recognition
import threading
import requests
import base64
from io import BytesIO
from pyfingerprint.pyfingerprint import PyFingerprint
import fen as fingerprint_enhancer
import os
import queue

## Tries to initialize the sensor
headers = {"Authorization": "Bearer HT-DA847CTUgK9jhg0QbN87Ivo15DTWu"}


# try:

#     f = PyFingerprint('COM3', 57600, 0xFFFFFFFF, 0x00000000)
#     if ( f.verifyPassword() == False ):

#         raise ValueError('The given fingerprint sensor password is wrong!')



# except Exception as e:

#     print('The fingerprint sensor could not be initialized!')
#     print('Exception message: ' + str(e))
#     exit(1)


#Set up GUI

window = tk.Tk()  #Makes main window
window.wm_title("Booth")
window.config(background="#FFFFFF")
frame = ''
mode = 1
bc_url =''
stored_face_encoding = ''
flag = False

aadhaar_number = ''
face_location = ''
fingerprint_location = ''
name = ''

data = {}

finger_score = 0



q = queue.Queue()

#Graphics window

imageFrame = tk.Frame(window)
imageFrame.grid(row=0, column=0, padx=10, pady=2)
qrframe = tk.Frame(window)
qrframe.grid(row=1,column=0, sticky="nsew")
face_reg = tk.Frame(window)

face_reg.grid(row=1,column=0, sticky="nsew")



finger_reg = tk.Frame(window)
finger_reg.grid(row=1,column=0, sticky="nsew")



#Capture video frames

lmain = tk.Label(imageFrame)
lmain.grid(row=0, column=0)

status = tk.Label(imageFrame,font=('Arial',25))
status.grid(row=1,column=0)



cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
qrcode = tk.Label(qrframe,text="QR CODE")
qrcode.pack(expand=1,fill='both')



face = tk.Label(face_reg,text="FACE")

face.pack(expand=1,fill='both')



finger = tk.Label(finger_reg,text="FINGER")

finger.pack(expand=1,fill='both')



qrframe.tkraise()



def sift_keypoints(image_path):

    # Read the fingerprint image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)



    # Initialize SIFT detector
    sift = cv2.SIFT_create()



    # Detect keypoints and compute descriptors
    keypoints, descriptors = sift.detectAndCompute(img, None)



    # Draw keypoints on the image
    img_with_keypoints = cv2.drawKeypoints(img, keypoints, None)

    return img_with_keypoints, keypoints, descriptors



def save_enhanced_image(image_path:str=r'image_enhanced.bmp'):

    global q,f

    while ( f.readImage() == False ):

        pass



    imageDestination = r'image.bmp'

    f.downloadImage(os.path.join(os.getcwd(),imageDestination))

    img = cv2.imread(os.path.join(os.getcwd(),imageDestination), 0)

    out = fingerprint_enhancer.enhance_Fingerprint(img)



    cv2.imwrite(os.path.join(os.getcwd(),image_path),out)

    q.put(True)



def after_saved_clbk():

    global finger_score,aadhaar_number,face_location,fingerprint_location,name

    try:

        message = q.get(block=False)

    except queue.Empty:

        # let's try again later

        window.after(100, after_saved_clbk)

        return



    if message is not None:

        finger_score = compare_finger('image_enhanced.bmp','dbfinger.bmp')
        print(finger_score)

        if finger_score > 8:

            res = requests.request('PATCH',f'http://localhost:8055/items/attendance/{bc_url}',json={"is_present":1},headers=headers).json()
            print(res)

            status.config(text="VERIFIED "+str(name))
            status['bg'] = 'green'
            print("VERIFIED FINGER")
            
            window.after(2000,change_to_mode_1)

        

        else:
            
            status.config(text="NOT VERIFIED")
            status['bg'] = 'red'
            print("NOT VERIFIED FINGER")

            window.after(2000,change_to_mode_1)


def compare_face(frame,dbface_encoding):

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations,num_jitters=5)
    similarity_score = 0
    for face_encoding in face_encodings:

        # Compare the current face encoding with the stored face encoding
        face_distance = face_recognition.face_distance([dbface_encoding], face_encoding)
        similarity_score = 1 - face_distance[0]

    return similarity_score

def change_to_mode_2():

    global mode
    face_reg.tkraise()
    mode = 2


def change_to_mode_1():

    global mode,bc_url,data,stored_face_encoding,flag,aadhaar_number,face_location,fingerprint_location,name,status

    print("changed to mode 1")

    lmain.grid(row=0, column=0)

    frame = ''
    mode = 1
    bc_url =''
    stored_face_encoding = ''
    aadhaar_number = ''
    face_location = ''
    fingerprint_location = ''
    name = ''
    flag = True
    status.config(text='QR CODE :=')
    
    data = {}

    qrframe.tkraise()

def change_to_mode_3():

    global mode,bc_url,data,stored_face_encoding,flag
    mode = 3
    flag = True
    lmain.grid_forget()
    finger_reg.tkraise()

def show_frame():

    global frame,mode,bc_url,data,stored_face_encoding,flag,aadhaar_number,face_location,fingerprint_location,name
    _, frame = cap.read()
    #frame = cv2.flip(frame, 1)

    #frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.35)

    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)



    if mode == 1:

        try:
            decoded_objects = decode(cv2image)
            if decoded_objects:

                bc_url = decoded_objects[0].data.decode("utf-8")
                print("QR CODE := ",bc_url)
                to_search = {
                    "query": {
                        "filter": {
                            "blockchain_link": {
                                "_eq": bc_url
                            }
                        }
                    }
                }
                
                res = requests.request('SEARCH',r'http://localhost:8055/items/biometric_data/',json=to_search,headers=headers).json()

                if len(res['data']) == 1:
                    user = res['data'][0]
                    aadhaar_number = user['aadhaar_number']
                    face_location = user['face']
                    fingerprint_location = user['fingerprint']
                    name = user.get('name','')
                    
                    # Check if is_present == 0
                    to_search = {
                        "query": {
                            "filter": {
                                "aadhaar_no": {
                                    "_eq": aadhaar_number
                                }
                            }
                        }
                    }
                    
                    res = requests.request('SEARCH',r'http://localhost:8055/items/attendance/',json=to_search,headers=headers).json()
                    bc_url = res['data'][0]['roll_no']
                    status.config(text="QR CODE := "+ str(bc_url))
                    
                    
                    if res['data'][0]['is_present']:
                        print("Invalid QR Code")
                        status.config(text="Invalid QR Code")
                        status['bg'] = 'red'
                    else:
                                            
                        face = requests.get(f'http://localhost:8055/assets/{face_location}',headers=headers).content
                        with open('dbface.jpg','wb') as f:
                            f.write(face)
                        
                        finger = requests.get(f'http://localhost:8055/assets/{fingerprint_location}',headers=headers).content
                        with open('dbfinger.bmp','wb') as f:
                            f.write(finger)
                            
                        stored_image = face_recognition.load_image_file("dbface.jpg")
                        stored_face_encoding = face_recognition.face_encodings(stored_image)[0]
                        flag = True
                        window.after(3000,change_to_mode_2)
                    
                else:
                    pass
        except Exception as e:
            print(e)
            print("Invalid QR Code")
            status.config(text="Invalid QR Code")
            status['bg'] = 'red'
            pass


    if mode == 2:
        cv2.imwrite("frame.jpg",frame)
        score = compare_face(frame,stored_face_encoding)
        print(score)
        # score = 0
        
        print("trying face recognition. Got match := ",score)
        if score > 0 and flag:

            status.config(text="VERIFIED "+ str(name))
            status['bg'] = 'green'
            print("VERIFIED")
            
            res = requests.request('PATCH',f'http://localhost:8055/items/attendance/{bc_url}',json={"is_present":1},headers=headers).json()
            
        
            print("NAME := ",str(aadhaar_number))
            flag = False
            window.after(500,change_to_mode_1)

        elif score < 0.4 and flag:
            
            # TODO: Fingerprint verification algorithm
            # TODO: Record fingerprints of every person

            print("FINGERPRINT VERIFICATION NEEDED")
            status.config(text="FINGERPRINT VERIFICATION NEEDED")
            status['bg'] = 'yellow'
            flag = False

            window.after(500,change_to_mode_3)

    if mode == 3:

        if flag:

            print("NOW TRYING FINGERPRINT CHECK")

            window.after(100, after_saved_clbk)

            threading.Thread(target=save_enhanced_image).start()

            flag = False



    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(50, show_frame) 



def compare_finger(scanner_image_path,dbfinger_path):

    _, _, descriptors1 = sift_keypoints(scanner_image_path)
    _, _, descriptors2 = sift_keypoints(dbfinger_path)

    # Match descriptors between the images using FLANN matcher

    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)



    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(descriptors1, descriptors2, k=2)



    # Apply ratio test to find good matches

    good_matches = []

    for m, n in matches:

        if m.distance < 0.7 * n.distance:
            good_matches.append(m)

    return len(good_matches)





show_frame()  #Display 2
window.mainloop()  #Starts GUI

