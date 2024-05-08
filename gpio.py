import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep # Import the sleep function from the time module
import configparser
from distutils.command.config import config
import os,sys
import subprocess
from shutil import copytree, ignore_patterns
import enum

global GPO_List
global GPI_List
GPO_List = []
GPI_List = []
global DIO
def SET_PIN(Pin_num):
    global GPI_List
    if Pin_num.value in GPO_List:
        GPIO.output(Pin_num.value,GPIO.HIGH)
        return True
    else:
        return False

def CLEAR_PIN(Pin_num):
    global GPI_List
    if Pin_num.value in GPO_List:
        GPIO.output(Pin_num.value,GPIO.LOW) 
        return True
    else:
        return False
    

def GET_PIN_STATE(Pin_num):
    global GPI_List
    if Pin_num.value in GPI_List:
        if GPIO.input(Pin_num.value) == 1:
            return DIO.high
        else:
            return DIO.low
    else:
        return DIO.Invalid_pin_number


def GPIO_Init():
    global GPO_List
    global GPI_List
    GPO_List = []
    GPI_List = []
    global DIO
    class DIO(enum.Enum):
        high = True 
        low = False
        Invalid_pin_number= "Invalid_pin_number"
        BOARD_PIN_7 = 7
        BOARD_PIN_11 = 11
        BOARD_PIN_13 = 13
        BOARD_PIN_15 = 15
        BOARD_PIN_29 = 29
        BOARD_PIN_31 = 31
        BOARD_PIN_33 = 33
        BOARD_PIN_35 = 35
        BOARD_PIN_37 = 37
        BOARD_PIN_40 = 40
        BOARD_PIN_38 = 38
        BOARD_PIN_36 = 36
        BOARD_PIN_32 = 32
        BOARD_PIN_16 = 16
        BOARD_PIN_18 = 18
        BOARD_PIN_22 = 22

    Dir_path =  os.path.abspath(os.path.dirname(sys.argv[0]))
    # print(Dir_path)
    os.chdir(Dir_path)
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BOARD)
    Config_present = configparser.ConfigParser()
    try:
        Config_present.read("GPIO_conf.ini")
        if(True == Config_present.getboolean('GPIO', 'USE_INI_FOR_SETUP')):
            update_version = Config_present.get('GPIO', 'GPO')
            update_version = update_version.replace('[','')
            update_version = update_version.replace(']','')
            update_version = update_version.replace(' ','')
            New_value = update_version.split(',')
            if '' in New_value:
                New_value.remove('')
            integer_list = []
            # print(len(New_value))
            i=0
            count=0
            if New_value != ['']:
                [integer_list.append(int(x)) for x in New_value]
                GPO_List = integer_list
                while (count < (len(New_value))):
                    try:
                        for i in GPO_List:
                            count+=1
                            GPIO.setup(i, GPIO.OUT, initial=GPIO.LOW) 
                    except:
                        integer_list.remove(i)

            update_version = Config_present.get('GPIO', 'GPI')
            update_version = update_version.replace('[','')
            update_version = update_version.replace(']','')
            update_version = update_version.replace(' ','')
            update_version = update_version.replace('','')
            New_value = update_version.split(',')
            if '' in New_value:
                New_value.remove('')
            integer_list = []
            i=0
            count=0
            if New_value != ['']:
                [integer_list.append(int(x)) for x in New_value]
                GPI_List = integer_list
                while (count < (len(New_value))):
                    try:
                        for i in GPI_List:
                            count+=1
                            GPIO.setup(i, GPIO.IN) 
                    except:
                        integer_list.remove(i)
    except:
        print("GPIO not initialised")

        


if __name__ == "__main__":
    GPIO_Init()
    while(1):
        SET_PIN(Pin_num=DIO.BOARD_PIN_16)
        # LED(35,'on')
        sleep(1)
        CLEAR_PIN(Pin_num=DIO.BOARD_PIN_16)
        sleep(0.2)




