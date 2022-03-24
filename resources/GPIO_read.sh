#!/bin/bash

export TERM=${TERM:-dumb}
#assign parameters


action=read
pin=21
#value=0


#sudo udevadm info -a -n /dev/ttyUSB0 > /home/pi/USB0_info.txt 2>&1
#sudo udevadm info -a -n /dev/ttyUSB1 > /home/pi/USB1_info.txt 2>&1
#sudo udevadm info -a -n /dev/ttyUSB2 > /home/pi/USB2_info.txt 2>&1
#sudo udevadm info -a -n /dev/ttyUSB3 > /home/pi/USB3_info.txt 2>&1

#create gpio instance
#echo 21 > /sys/class/gpio/export

  	#assign direction
	#sudo echo in > /sys/class/gpio/gpio21/direction
  	#read gpio value
        #cat /sys/class/gpio/gpio21/value

        #while :
	#do
		#if [ `cat /sys/class/gpio/gpio21/value` -eq '0' ] 
        	#then 
             		
                        lxterminal --command="sudo python3 /home/pi/Desktop/esp_rpi_flasher/test_code.py"
                        #lxterminal --command="python3.7 /home/pi/esp_rpi_flasher/test_code.py"
                        
        	#fi
	#done

#remove gpio instance
#echo 21 > /sys/class/gpio/unexport