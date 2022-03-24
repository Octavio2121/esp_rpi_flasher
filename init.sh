#!/bin/bash

export TERM=${TERM:-dumb}



#lxterminal --command="sudo python3 /home/pi/esp_rpi_flasher/test_code.py"

lxterminal --command="sudo cp -r /home/pi/Desktop/esp_rpi_flasher/code /boot"

lxterminal --command="sudo cp /home/pi/Desktop/esp_rpi_flasher/resources/serial-ports.rules /etc/udev/rules.d"

lxterminal --command="sudo cp /home/pi/Desktop/esp_rpi_flasher/resources/firmwareBP.bin /home/pi"

lxterminal --command="sudo udevadm control --reload-rules"

lxterminal --command="sudo cp /home/pi/Desktop/esp_rpi_flasher/resources/CommandProgBlackPill.txt /home/pi/Desktop"

lxterminal --command="sudo cp /home/pi/Desktop/esp_rpi_flasher/resources/autostart /etc/xdg/lxsession/LXDE-pi"

lxterminal --command="sudo cp /home/pi/Desktop/esp_rpi_flasher/resources/config.txt /boot"

lxterminal --command="sudo cp /home/pi/Desktop/esp_rpi_flasher/resources/GPIO_read.sh /home/pi"

lxterminal --command="sudo chmod 777 /home/pi/GPIO_read.sh"

lxterminal --command="sudo apt-get install stlink-tools"

lxterminal --command="pip3 install colorful"

lxterminal --command="pip3 install slack_sdk"

lxterminal --command="pip3 install usb"

lxterminal --command="pip3 install pyusb"

lxterminal --command="sudo reboot"





