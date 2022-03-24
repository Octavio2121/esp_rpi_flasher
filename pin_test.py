#! /usr/bin/env python
import argparse
import configparser
import glob
import os
import os.path
import RPi.GPIO as GPIO
import serial
import subprocess
import sys
import threading
from time import sleep

PYTHON=sys.executable

configFilePath = ("/boot/code/config.ini")
config = configparser.ConfigParser()
config.read(configFilePath)
bootloaderPath = config.get('ENCRYPT', 'bootloaderPath')
partitionsPath = config.get('ENCRYPT', 'partitionsPath')
otaDataPath = config.get('ENCRYPT', 'otaDataPath')


flashButton = int(config.get('DEFAULT', 'flashButton'))
reFlashButton = int(config.get('DEFAULT', 'reFlashButton'))
rebootButton = int(config.get('DEFAULT', 'rebootButton'))


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(flashButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(reFlashButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(rebootButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
flashFlag = False
reFlashFlag = False
rebootFlag = False

def _reflash_callback(channel):  
    print("Reflash button is pressed")
    global reFlashFlag
    reFlashFlag = True # enable reflash

def _reboot_callback(channel):  
    print("Reboot button is pressed")
    global rebootFlag
    rebootFlag = True # enable reboot
    
def _flash_callback(channel):  
    print("Flash button is pressed")
    global flashFlag
    flashFlag = True # enable flash
    
def _reboot():
    print("reboot")
    global rebootFlag
    rebootFlag = False
    
def _reflash():
    print("reflash")
    global reFlashFlag
    reFlashFlag = False
    
def _flash():
	print("flash")
	global flashFlag
	flashFlag = False
	
# add event detect buttons
GPIO.add_event_detect(reFlashButton, GPIO.FALLING, callback=_reflash_callback, bouncetime=2000)  
GPIO.add_event_detect(flashButton, GPIO.FALLING, callback=_flash_callback, bouncetime=2000)  
GPIO.add_event_detect(rebootButton, GPIO.FALLING, callback=_reboot_callback, bouncetime=2000)  


try:
    while True:
        if flashFlag == True:
            _flash()
        if reFlashFlag == True:
            _reflash()
        if rebootFlag == True:
            _reboot()
except KeyboardInterrupt:  
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
GPIO.cleanup()           # clean up GPIO on normal exit  
