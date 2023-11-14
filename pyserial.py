#pyserial script for manual controlling

import serial
import time
import threading


ser = serial.Serial('COM13', 9600,timeout=1)
time.sleep(2)

def send_command(command):
    ser.write(command.encode())
    time.sleep(1)


def decision():
    return


def on_jammer():
    threading.Thread(target=send_command,args='1').start()
def off_jammer():
    threading.Thread(target=send_command,args='0').start()

while True:

  
    #if decision == '1':
        send_command('0')
    #elif decision == '0':
     #   send_command('0')
    #elif decision == 'q':
     #  break

ser.close()

