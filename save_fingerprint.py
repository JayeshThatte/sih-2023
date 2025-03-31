from pyfingerprint.pyfingerprint import PyFingerprint
import fen as fingerprint_enhancer
import os
import cv2

try:

    f = PyFingerprint('COM3', 57600, 0xFFFFFFFF, 0x00000000)
    if ( f.verifyPassword() == False ):

        raise ValueError('The given fingerprint sensor password is wrong!')



except Exception as e:

    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)
    

def save_enhanced_image(image_path:str=r'image_enhanced.bmp'):

    global q,f

    while ( f.readImage() == False ):
        pass

    imageDestination = r'image.bmp'

    f.downloadImage(os.path.join(os.getcwd(),imageDestination))
    img = cv2.imread(os.path.join(os.getcwd(),imageDestination), 0)
    out = fingerprint_enhancer.enhance_Fingerprint(img)

    cv2.imwrite(os.path.join(os.getcwd(),image_path),out)
    
save_enhanced_image()