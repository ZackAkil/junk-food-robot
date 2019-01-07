from SimpleCV import Camera

import sys
from google.cloud import automl_v1beta1
from google.cloud.automl_v1beta1.proto import service_pb2

import cv2
import time

import RPi.GPIO as GPIO
import time

service_account = 'serivce_account.json'

prediction_client = automl_v1beta1.PredictionServiceClient.from_service_account_file(service_account)

servoPIN = 17
led_pin_red = 22
led_pin_green = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

GPIO.setup(led_pin_red, GPIO.OUT)
GPIO.setup(led_pin_green, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO for PWM with 50Hz
p.start(2.5) # Initialization
time.sleep(0.5)
p.ChangeDutyCycle(0)

def red():
    GPIO.output(led_pin_green, GPIO.LOW)
    GPIO.output(led_pin_red, GPIO.HIGH)
    
    
def green():
    GPIO.output(led_pin_red, GPIO.LOW)
    GPIO.output(led_pin_green, GPIO.HIGH)
    
    
def off():
    GPIO.output(led_pin_red, GPIO.LOW)
    GPIO.output(led_pin_green, GPIO.LOW)


def ease(start, end, delay, steps):
    delta = end - start
    increment = delta / steps
    new_pos = start
    for _ in range(steps):
        p.ChangeDutyCycle(new_pos)
        new_pos += increment
        time.sleep(delay)
    p.ChangeDutyCycle(0)
        

def swipe():
    ease(2.5, 12, 0.001, 350)
    ease(12, 2.5, 0.0025, 350)

def get_prediction(content, project_id='zacks-first', model_id='ICN4382440947979519530'):
  
  name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
  payload = {'image': {'image_bytes': content }}
  params = {}
  request = prediction_client.predict(name, payload, params)
  return request  # waits till request is returned


# Initialize the camera
cam = Camera()

# Loop to continuously get images
while True:
    
    time.sleep(1)
    img = cam.getImage()

    pred = get_prediction(cv2.imencode('.jpg', img.scale(320,240).getNumpy())[1].tostring())
    
    if pred.payload:
        curr_pred = pred.payload[0].display_name
        print( curr_pred, pred.payload[0].classification.score, junk_count)
        
        if pred.payload[0].classification.score > 0.6:
            
            if curr_pred == 'junk':
                red()
                swipe()
            elif curr_pred == 'healthy':
                green()
            else:
                off()
                
        
    else:
        print( 'no prediction')
    # Show the image
    img.show()