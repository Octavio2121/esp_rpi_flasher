#! /usr/bin/env python

#To change number of tries of ESP32 when botting. Inside esptool.py change value:     DEFAULT_CONNECT_ATTEMPTS = 7          # default number of times to try connection

#sudo nano /etc/udev/rules.d/serial-ports.rules
#sudo udevadm control --reload-rules

import colorful as cf
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
import datetime
import time

#==========================
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
#==========================
from usb.core import find as finddev


PYTHON=sys.executable

configFilePath = ("/boot/code/config.ini")
config = configparser.ConfigParser()
config.read(configFilePath)

projectPath = config.get('DEFAULT', 'projectPath')
bootloaderPath = config.get('DEFAULT', 'bootloaderPath')
partitionsPath = config.get('DEFAULT', 'partitionsPath')
otaDataPath = config.get('DEFAULT', 'otaDataPath')
appDataPath = config.get('DEFAULT', 'appDataPath')


flashButton = int(config.get('DEFAULT', 'flashButton'))
rebootButton = int(config.get('DEFAULT', 'rebootButton'))
shutdownButton = int(config.get('DEFAULT', 'shutdownButton'))
flashingLED = int(config.get('DEFAULT', 'flashingLED'))
readyLED = int(config.get('DEFAULT', 'readyLED'))

pinInputX = int(config.get('DEFAULT', 'pinInputX'))
pinInputY = int(config.get('DEFAULT', 'pinInputY'))
pinInputZ = int(config.get('DEFAULT', 'pinInputZ'))

ProgLEDinProgress = int(config.get('DEFAULT', 'ProgLEDinProgress'))
ProgLEDcorrect = int(config.get('DEFAULT', 'ProgLEDcorrect'))
ProgLEDfail = int(config.get('DEFAULT', 'ProgLEDfail'))
TestLEDinProgress = int(config.get('DEFAULT', 'TestLEDinProgress'))
TestLEDcorrect = int(config.get('DEFAULT', 'TestLEDcorrect'))
TestLEDfail = int(config.get('DEFAULT', 'TestLEDfail'))
VccTestLEDinProgress = int(config.get('DEFAULT', 'VccTestLEDinProgress'))
VccTestLEDcorrect = int(config.get('DEFAULT', 'VccTestLEDcorrect'))
VccTestLEDfail = int(config.get('DEFAULT', 'VccTestLEDfail'))

pinOutA = int(config.get('DEFAULT', 'pinOutA'))
pinOutB = int(config.get('DEFAULT', 'pinOutB'))
pinOutC = int(config.get('DEFAULT', 'pinOutC'))
pinOutD = int(config.get('DEFAULT', 'pinOutD'))



GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(flashButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
#GPIO.setup(reFlashButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(rebootButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(shutdownButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(flashingLED, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(readyLED, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(pinInputX, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinInputY, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinInputZ, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#OutPuts
GPIO.setup(ProgLEDinProgress,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(ProgLEDcorrect,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(ProgLEDfail,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(TestLEDinProgress,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(TestLEDcorrect,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(TestLEDfail,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(VccTestLEDinProgress,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(VccTestLEDcorrect,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(VccTestLEDfail,GPIO.OUT, initial=GPIO.LOW)

GPIO.setup(pinOutA,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(pinOutB,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(pinOutC,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(pinOutD,GPIO.OUT, initial=GPIO.LOW)


flashFlag = False
rebootFlag = False
shutdownFlag = False
reFlashLEDflag = False
Flag_ErrorPort = False

#==========================
# Create a slack client

try:
    client = WebClient(token = "xoxb-1540856706564-2620312294756-DuPGLLmqBopOw85YRP5QciJW") 
except(OSError, serial.SerialException):
    pass
#==========================
def current_milli_time():
    return round(time.time()*1000)


def _get_args(type, esptool_path, port, baud):
    if type == "burn_secure_key":
        result = [ PYTHON, esptool_path ]
        result += [ "--port", port ]
        result += [ "--do-not-confirm" ]
        result += [ "--before", "default_reset" ]
        result += [ "burn_key" ]
        #result += [ "secure_boot", secureBootloaderKeyPath ]
        return result
    elif type == "burn_flash_encryption_key":
        result = [ PYTHON, esptool_path ]
        result += [ "--port", port ]
        result += [ "--do-not-confirm" ]
        result += [ "--before", "default_reset" ]
        result += [ "burn_key" ]
        #result += [ "flash_encryption", flashEcryptionKeyPath ]
        return result
    elif type == "burn_efuse_cnt":
        result = [ PYTHON, esptool_path ]
        result += [ "--port", port ]
        result += [ "--do-not-confirm" ]
        result += [ "--before", "default_reset" ]
        result += [ "burn_efuse" ]
        result += [ "FLASH_CRYPT_CNT", "1" ]
        return result
    elif type == "burn_efuse_config":
        result = [ PYTHON, esptool_path ]
        result += [ "--port", port ]
        result += [ "--do-not-confirm" ]
        result += [ "--before", "default_reset" ]
        result += [ "burn_efuse" ]
        result += [ "FLASH_CRYPT_CONFIG", "0xf" ]
        return result
    elif type == "flash":
        result = [ PYTHON, esptool_path ]
        result += [ "--chip", "esp32" ]
        result += [ "--port", port ]
        result += [ "--baud", str(baud) ]
        result += [ "--before", "default_reset" ]
        result += [ "--after", "hard_reset" ]
        result += ["--connect-attempts", str(3)]
        result += [ "write_flash", "-z" ]
        result += [ "--flash_mode", "dio" ]
        result += [ "--flash_freq", "40m" ]
        result += [ "--flash_size", "4MB" ]
        result += [ "0x10000", appDataPath ]
        result += [ "0x8000", partitionsPath ]
        result += [ "0xe000", bootloaderPath ]
        result += [ "0x1000", otaDataPath ]
        #print("Successful: %s" % result)
        return result
    elif type == "erase_flash":
        result = [ PYTHON, esptool_path ]
        result += [ "--port", port ]
        result += [ "erase_flash" ]
        return result
    else:
        return 0

def _run_tool(tool_name, args5):          
    try:
        programmedFlag = -1 
        testedFlag = -1
        portsSplit = args5[5].split("/")
        nameOfFile = "log_"+ portsSplit[2] + ".txt"
        f = open(nameOfFile, "a")
        e = open("error.txt", "a")
        f.write("\n\n")
        f.flush()
        f.write("----------------------------------------------------------------------------")
        f.write("\n")
        data2 = " "
        ct = datetime.datetime.now()
        #==========================
        data2 = data2 + ("Date: %s \n" % ct)
        #==========================
        f.write(str(ct))
        f.write("\n\n")
        f.flush()
        a = subprocess.check_call(args5, env=os.environ, cwd=projectPath, stdout = f, stderr= e)
        
        serialPill = serial.Serial("/dev/Port_Pill", baudrate=115200) #Modificar el puerto serie de ser necesario
        comando = "progCorrect\n"
        comandoBytes = comando.encode()
        serialPill.write(comandoBytes)
        time.sleep(0.1)
        serialPill.close()
        
        s = serial.Serial(args5[5],115200)
        data = []
        data = s.readline()
        dataString = data.decode("utf-8")
        
        beginFlag = "%%%" in dataString 
        endFlag = "@@@@@" in dataString 
        cycleFlag = beginFlag * endFlag 
        
        GPIO.output(TestLEDinProgress,True)
        timeInit = current_milli_time()
        timeActual = current_milli_time()
        timeLapse  = timeActual - timeInit
        while(not cycleFlag):
            #print(cf.yellow("Warning: Inside loop")) 	#Move to log 
            s.write(b'1') #ser.write(b'hello')
            data = s.readline()
            dataString = data.decode("utf-8")
            cycleFlag = ("%%%%%" in dataString) * ("@@@@@" in dataString )
            timeActual = current_milli_time()
            timeLapse  = timeActual - timeInit
            if(timeLapse > 3000):
               errors = 1
               break
        if (cycleFlag):
            dataSplit = dataString.split(",")
            errors = 0
            for x in range(len(dataSplit)-2):
                value = dataSplit[x+1]
                data2 = data2 + ("%s," % value)
                if (value[len(value)-1] == "0"):
                    errors = errors + 1            
        if (errors ==  0):
            print(cf.green("Result:     %s   ....  %s    " % (portsSplit[2],dataString)))
            print(cf.green("Successful: %s" % portsSplit[2]))
            GPIO.output(TestLEDinProgress,False)
            GPIO.output(ProgLEDinProgress,False)
            GPIO.output(ProgLEDcorrect,True)
            GPIO.output(TestLEDcorrect,True)
            GPIO.output(pinOutA,True);
            
            
            serialPill = serial.Serial("/dev/Port_Pill", baudrate=115200) #Modificar el puerto serie de ser necesario
            comando = "testCorrect\n"
            comandoBytes = comando.encode()
            serialPill.write(comandoBytes)
            time.sleep(0.1)
            serialPill.close()
            
            
            try:
                data2 = data2 + "\n Successful: %s" % (portsSplit[2])
                #response = client.chat_postMessage(channel='#testbot2', text=data2)
                #assert response["message"]["text"] == data2
                
                
            #==========================
            except SlackApiError as e:
                # You will get a SlackApiError if "ok" is False
                assert e.response["ok"] is False
                assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
                print(f"Got an error: {e.response['error']}")
        else:
            print(cf.red("Error: %s Programmed, but failed test. Please check %s" % (portsSplit[2],nameOfFile)))
            characters = "%@"
            for x in range(len(characters)):
                dataString = dataString.replace(characters[x],"")
            print(cf.red("Result:     %s  %s    " % (portsSplit[2],dataString)))
            
            serialPill = serial.Serial("/dev/Port_Pill", baudrate=115200) #Modificar el puerto serie de ser necesario
            comando = "testFail\n"
            comandoBytes = comando.encode()
            serialPill.write(comandoBytes)
            time.sleep(0.1)
            serialPill.close()
            
            
            try:
                #==========================
                data2 = data2 + "\n Error: %s Programmed, but failed test." % (portsSplit[2])
                #response = client.chat_postMessage(channel='#testbot2', text=data2)
                #assert response["message"]["text"] == data2
                
                
            #==========================
            except SlackApiError as e:
                # You will get a SlackApiError if "ok" is False
                assert e.response["ok"] is False
                assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
                print(f"Got an error: {e.response['error']}")
            
        f.write("\n\n")
        f.write(dataString)
        f.write("----------------------------------------------------------------------------")
        f.flush()
        s.close()
        f.close()
        e.close()


    except subprocess.CalledProcessError as e:
        
        serialPill = serial.Serial("/dev/Port_Pill", baudrate=115200) #Modificar el puerto serie de ser necesario
        comando = "progFail\n"
        comandoBytes = comando.encode()
        serialPill.write(comandoBytes)
        time.sleep(0.1)
        serialPill.close()
        
        
        global Flag_ErrorPort
        if (e.returncode == 2):
            string = "No PCB found"
            GPIO.output(ProgLEDfail,True)
            GPIO.output(ProgLEDinProgress,False)
            
        else:
            string = e.returncode
            if(e.returncode == 1):
                Flag_ErrorPort = True
        print(cf.red("Failed:     %s   ....  %s    " % (portsSplit[2],string)))
        
        try:
            data2 = data2 + "Failed:     %s   ....  %s    " % (portsSplit[2],string)
            #response = client.chat_postMessage(channel='#testbot2', text=data2)
            #assert response["message"]["text"] == data2
                
                
            #==========================
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")
        
    return 0


def _get_ports():
    if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/ttyU*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.U*')
    else:
        raise EnvironmentError('Unsupported platform')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def getFixedPorts():
    ports = ["/dev/Port_1","/dev/Port_2","/dev/Port_3","/dev/Port_4"]
    result = []
    global Flag_ErrorPort
    global l
    for port in ports:
        try:
            s = serial.Serial(port,baudrate = 115200,timeout=5)  #<-
            s.flush()
            s.flushInput()
            s.flushOutput
            s.close()
            result.append(port)
        except(OSError, serial.SerialException):
            pass
    l = len(result)
    if (l != 4):Flag_ErrorPort = True
    return result

def _flash():
    
    # disable flash
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\nGet Fixed Ports ...")
    #os.system('cls' if os.name == 'nt' else 'clear')
    ports = getFixedPorts()
    #print(l)
    if (l != 0):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\nProgramming:     ",end ='')
        GPIO.output(ProgLEDinProgress,True)
        for x in ports:
            print("  %s" % x[5:len(x)], end='')
        print("\n\n")
        threads = []
        for x in ports:
            args5 = _get_args("flash", os.path.join(projectPath,"esptool-master/esptool.py"), x, 2000000)
            flashThread = threading.Thread(target=_run_tool, args=("esptool.py",args5))
        
            threads.append(flashThread)
        #print(threads)
        for x in threads:
            x.start()
        for x in threads:
            x.join()
        #print(cf.white("\n\nDone. !"))           
        global flashFlag
        flashFlag = False # disable flash
        
    else:
        print(cf.red("No programmer detected"))
        serialPill = serial.Serial("/dev/Port_Pill", baudrate=115200) #Modificar el puerto serie de ser necesario
        comando = "progFail\n"
        comandoBytes = comando.encode()
        serialPill.write(comandoBytes)
        time.sleep(0.1)
        serialPill.close()

def _shutdown():
    os.system("sudo shutdown now")

def _reboot():
    os.system("sudo reboot")
    
def _FlashLED():
    global reFlashLEDflag
    #print("Send Files ...")
    reFlashLEDflag = False
    try:
        print("Sending Files ...")
        filepath_1="/home/pi/log_Port_1.txt"
        response = client.files_upload(channels='#testbot2', file=filepath_1)
        assert response["file"]  # the uploaded file
        
        filepath_2="/home/pi/log_Port_2.txt"
        response = client.files_upload(channels='#testbot2', file=filepath_2)
        assert response["file"]  # the uploaded file
        
        filepath_3="/home/pi/log_Port_3.txt"
        response = client.files_upload(channels='#testbot2', file=filepath_3)
        assert response["file"]  # the uploaded file
        
        filepath_4="/home/pi/log_Port_4.txt"
        response = client.files_upload(channels='#testbot2', file=filepath_4)
        assert response["file"]  # the uploaded file
        
        
        print("Finished")
        sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Fix the PCBS and press Program button")
        #==========================
    except(OSError, serial.SerialException):
        print("Sending Files Failed")
        sleep(2)
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Fix the PCBS and press Program button")
        pass
        '''
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")
        '''

def _flash_callback(channel):  
    global flashFlag
    flashFlag = True # enable flash

def _reboot_callback(channel):  
    print("Reboot button is pressed")
    global rebootFlag
    rebootFlag = True # enable reboot
    
def _shutdown_callback(channel):  
    print("Shutdown button is pressed")
    global shutdownFlag
    shutdownFlag = True # enable reboot
    
def _FlashLED_callback(channel):  
    #print("Send File button is pressed")
    global reFlashLEDflag
    reFlashLEDflag = True # enable reboot
#Event buttons
GPIO.add_event_detect(flashButton, GPIO.FALLING, callback=_flash_callback, bouncetime=2000)  
GPIO.add_event_detect(rebootButton, GPIO.FALLING, callback=_reboot_callback, bouncetime=2000)
GPIO.add_event_detect(shutdownButton, GPIO.FALLING, callback=_shutdown_callback, bouncetime=2000)  
GPIO.add_event_detect(flashingLED, GPIO.FALLING, callback=_FlashLED_callback, bouncetime=2000)



try:
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Fix the PCBS and press Program button")
    while True:
        try:
            serialPill = serial.Serial("/dev/Port_Pill", baudrate=115200) #Modificar el puerto serie de ser necesario
            encoding = 'utf-8'
            read = serialPill.readline()
            inputMsg = str(read, encoding)
            serialPill.flush()
            serialPill.flushInput()
            serialPill.close() 
        except(OSError, serial.SerialException):
            inputMsg = ""
            pass
         

        #print(read)
        #print(inputMsg)
        '''
        if inputMsg == "flashPCB\r\n":
            print("Se presiono boton flashPCB")
        if inputMsg == "reboot\r\n":
            print("Se presiono boton reboot")
        if inputMsg == "shutDown\r\n":
            print("Se presiono boton shutDown")
        if inputMsg == "sendFiles\r\n":
            print("Se presiono boton sendFiles")
        '''
        #print("Mensaje recibido")
        #print(inputMsg)
        
        if inputMsg == "flashPCB\r\n":
            if Flag_ErrorPort == True:
                #print("Resetting ports ...")
                #os.system('sudo python3.7 /home/pi/reset_usb.py > /home/pi/Reset_info.txt 2>&1')
                Flag_ErrorPort = False
            serialPill.close()    
            _flash()
        if inputMsg == "reboot\r\n":
            serialPill.close()
            _reboot()
        if inputMsg == "shutDown\r\n":
            serialPill.close()
            _shutdown()
        if inputMsg == "sendFiles\r\n":
            serialPill.close()
            _FlashLED()
        if inputMsg == "vccCorrect\r\n":
            #print("Vcc Test Correct")
            print(cf.green("Vcc Test Correct"))
            print(cf.white("\n\nDone. !"))
            
            serialPill = serial.Serial("/dev/Port_Pill", baudrate=115200) #Modificar el puerto serie de ser necesario
            comando = "endTest\n"
            comandoBytes = comando.encode()
            serialPill.write(comandoBytes)
            time.sleep(0.1)
            
            serialPill.close()
        if inputMsg == "vccFail\r\n":
            #print("Vcc Test Failed")
            print(cf.red("Vcc Test Failed"))
            
            
            serialPill = serial.Serial("/dev/Port_Pill", baudrate=115200) #Modificar el puerto serie de ser necesario
            comando = "endTest\n"
            comandoBytes = comando.encode()
            serialPill.write(comandoBytes)
            time.sleep(0.1)
            serialPill.close()
            
            
            
            
            while inputMsg != "Done Vcc Test\r\n":
                try:
                    serialPill = serial.Serial("/dev/Port_Pill", baudrate=115200) #Modificar el puerto serie de ser necesario
                    encoding = 'utf-8'
                    read = serialPill.readline()
                    inputMsg = str(read, encoding)
                    #print(inputMsg)
                    print(cf.red(inputMsg))
                    serialPill.flush()
                    serialPill.flushInput()
                    serialPill.close() 
                except(OSError, serial.SerialException):
                    inputMsg = ""
                    pass
            print(cf.white("\n\nDone Test. !"))
            
            
except KeyboardInterrupt:
    os.system('cls' if os.name == 'nt' else 'clear')
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
GPIO.cleanup()           # clean up GPIO on normal exit




