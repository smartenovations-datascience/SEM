from threading import Thread
import Master

from time import sleep
from time import time as TIME
from Master_Utils import *
import Controller
import Master_Controller_Utils
import schedule
import psycopg2
from read_write_database.write_data import Controller_10sec, Controller_5min, Controller_4hour
from read_write_database.config_to_db import * 
import gpio
import configparser
from distutils.command.config import config
import os,sys
import subprocess
#################################################################################
#                                                                               #
#      Firmware Version and Updated Software Release Date                       #
#                                                                               #
#################################################################################
SEM_FW_VERSION =  "latest"
SEM_RELEASE_DATE = "28.03.2023"
#################################################################################

def Get_SEM_FW_Version():
    return SEM_FW_VERSION
def Get_SEM_FW_ReleaseDate():
    return SEM_RELEASE_DATE
def db_thread():
    sleep(0.1)
    while(Master_Controller_Utils.Controller_one_time_read == False):
        time.sleep(1)
    Dir_path = os.getcwd()
    Dir_path_1= Dir_path.replace("/MainCode/Present_version",'')
    os.chdir(Dir_path_1+"/Webserver/sem_django")
    subprocess.call(["sudo","docker-compose","up","-d"]),
    os.chdir(Dir_path)
    from pkg_resources import working_set
    WebServerUP_b = False
    try:
        from tqdm import tqdm
        # colour  : str, optional
        # Bar colour (e.g. 'green', '#00ff00')., nolock=False, end='\n'

        for i in tqdm( range(120),desc="Server is getting Up…",ascii=False, ncols=75,colour='yellow'):
            if(WebServerUP_b == False):
                WebServerUP_b = Master_Controller_Utils.Configuration_DB_Init()
                if(WebServerUP_b == True):
                    pass
                else:
                    time.sleep(1)
            else:
                pass
    except:
        # from pkg_resources import working_set
        while(True):
            WebServerUP_b = Master_Controller_Utils.Configuration_DB_Init()
            if(WebServerUP_b == True):
                break
            else:
                time.sleep(1)
    while( Master_Controller_Utils.Database_setup == False):
        Master_Controller_Utils.Configuration_DB_Init()
        time.sleep(1)
    
    schedule.every(10).seconds.do(Controller_10sec)
    schedule.every(20).seconds.do(Controller_5min)
    schedule.every(30).seconds.do(Controller_4hour)
    print("webserver database up")
    
    while(1):
        schedule.run_pending()  
        sleep(1)


def GPIO_handle():
    Config_present = configparser.ConfigParser()
    Config_present.read("GPIO_conf.ini")
    PIN = Config_present.getint('GPIO', 'TOGGLE')
    pin=0
    for pin in gpio.DIO:
        if pin.value == PIN:
            break
    
    while(1):
        gpio.SET_PIN(Pin_num=pin)
        sleep(1)
        gpio.CLEAR_PIN(Pin_num=pin)
        sleep(1)



def main():
    print("################################################################################")
    print("#                          Firmware Info                                       #")
    print("#                      SEM Firmware Version = ", Get_SEM_FW_Version(),"                         #")
    print("#                         Date = ", Get_SEM_FW_ReleaseDate(),"                                  #")
    print("################################################################################")
   
    #logging enable when not commented 
    # import logging
    # logging.basicConfig()
    # log = logging.getLogger()
    # log.setLevel(logging.DEBUG)
    
    my_thread_list=[]
    
    Master_Controller_Utils.init() 


    Usb_check_Thread= Thread(target= Master_Controller_Utils.master_controller_usb_handle)
    MasterThread = Thread(target=Master.Master_Thread)
    # GPIOThread = Thread(target=GPIO_handle)

    WebserverThread = Thread(target=Master_Controller_Utils.Configuration_DB)
    # my_thread_list.append(WebserverThread)
    DBthread = Thread(target=db_thread) #created thread to load to database
    # my_thread_list.append(DBthread)

    ControllerThread = Thread(target=Controller.Controller_Thread)
    # my_thread_list.append(ControllerThread)
    (":::::::::::::::::::::::::::::::::::::::::::::SEM STARTED RUNNING:::::::::::::::::::::::::::::::::::::::::::::::::::::")
    Usb_check_Thread.start()    #usb_handling start
    
    ############################################################
    # while(Master_Controller_Utils.all_set == False):
    #     pass
    
   
    MasterThread.start()
    print("-------------------------------------------------master_thread_started")
    ControllerThread.start()
    print("-------------------------------------------------ControllerThread_started")
    # DBthread.start()
    print("-------------------------------------------------dbThread_started")
    # WebserverThread.start()
    print("-------------------------------------------------WebserverThread_started")

    # GPIOThread.start()
    
    for i in range(0,5):
        if(i==0):
            MasterThread.join() 
            print("master_thread_joined")
        elif(i==1):
            ControllerThread.join()
            print("ControllerThread_started") 
        elif(i==2): 
            pass  
            # DBthread.join()
            print("DBthread_started")    
        elif(i==3):
            # WebserverThread.join()
            print("WebserverThread_started") 
        elif(i==4):
            # GPIOThread.join()
            print("")


        
    flag = True
    while(flag == True):
        flag = True
        sleep(5) 

if __name__ == "__main__":
    from datetime import datetime
    from turtle import up
    from crontab import CronTab
    import sys
    import subprocess
    import os
    import time
    gpio.GPIO_Init()
    Dir_path =  os.path.abspath(os.path.dirname(sys.argv[0]))
    os.chdir(Dir_path)
    main()