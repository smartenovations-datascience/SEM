from ast import Pass
from ctypes import c_bool, c_char_p, c_int, c_uint8
from curses.ascii import isblank
from operator import truediv
import serial
import time
from pymodbus.client.sync import ModbusSerialClient
import json
from threading import Thread
import enum
import serial.tools.list_ports as prtlst
from datetime import datetime
from read_write_database.config_to_db import *
from Controller_Utils import Read_Controller_data
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.server.asynchronous import StopServer
from multiprocessing import Process,Manager,Value,Array,Semaphore


######################################################
# Importing GPIO Packages 
######################################################
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep # Import the sleep function from the time module
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering

import gpio
import configparser

import os
import sys


def import_CONNECT_TO_MASTER(USB=[]):
    from Master_Utils import CONNECT_TO_MASTER
    # return
    CONNECT_TO_MASTER(USB)

def master_process_init():
    global JSON
    class JSON(enum.Enum):
        CONTROLLER_TO_MASTER_PRIORITY_1 = 1
        CONTROLLER_TO_MASTER_PRIORITY_2 = 2
        CONTROLLER_TO_MASTER_PRIORITY_3 = 3
        CONTROLLER_TO_MASTER_PRIORITY_4 = 4
        MASTER_TO_CONTROLLER_PRIORITY_1 = 5
        MASTER_TO_CONTROLLER_PRIORITY_2 = 6
        MASTER_TO_CONTROLLER_PRIORITY_3 = 7
        MASTER_TO_CONTROLLER_PRIORITY_4 = 8
        Read_Configuration = 9
        Write_Configuration =10
        CONFIGURATION_BACKUP =11
        PRIORITY_1 =12
        PRIORITY_2 =13
        PRIORITY_3 =14
        PRIORITY_4 =15
    global Dir
    Dir =  os.path.abspath(os.path.dirname(sys.argv[0]))

    global WebServer_JSON_Dir
    # WebServer_JSON_Dir= Dir.replace("/MainCode/Present_version","/Webserver/sem_django/sem/JSON_Files")

    global this_process_master_usb_detected
    this_process_master_usb_detected = False

    global Controller_to_master_FileName_Priority1
    global Controller_to_master_FileName_Priority2
    global Controller_to_master_FileName_Priority3
    global Controller_to_master_FileName_Priority4
    global Master_to_controller_FileName_Priority1
    global Master_to_controller_FileName_Priority2
    global Master_to_controller_FileName_Priority3
    global Master_to_controller_FileName_Priority4
    # global Read_Configuration_file
    # global Write_Configuration_file
    # global Configuration_backup
    global Priority_1_backup
    global Priority_2_backup
    global Priority_3_backup
    global Priority_4_backup
    Controller_to_master_FileName_Priority1 = ""
    Controller_to_master_FileName_Priority2 = ""
    Controller_to_master_FileName_Priority3 = ""
    Controller_to_master_FileName_Priority4 = ""
    Master_to_controller_FileName_Priority1 = ""
    Master_to_controller_FileName_Priority2 = ""
    Master_to_controller_FileName_Priority3 = ""
    Master_to_controller_FileName_Priority4 = ""
    # Read_Configuration_file  = ""
    # Write_Configuration_file = ""
    # Configuration_backup = ""
    Priority_1_backup = ""
    Priority_2_backup = ""
    Priority_3_backup = ""
    Priority_4_backup = ""

    global Master_priority1_File_Read_Semaphore
    global Master_priority2_File_Read_Semaphore
    global Master_priority3_File_Read_Semaphore
    global Master_priority4_File_Write_Semaphore
    global Master_priority1_File_Write_Semaphore
    global Master_priority2_File_Write_Semaphore
    global Master_priority3_File_Write_Semaphore
    global Master_priority4_File_Read_Semaphore
    
    global Read_Configuration_Semaphore
    global Write_Configuration_Semaphore
   
    global Configuration_backup_Semaphore

    global Priority_1_backup_Semaphore
    global Priority_2_backup_Semaphore
    global Priority_3_backup_Semaphore
    global Priority_4_backup_Semaphore

    global new_list
    new_list=[]
    global int_extra_par_dict
    int_extra_par_dict = {}
    global bool_extra_par_dict
    bool_extra_par_dict = {}
    # config_count=0
    global Extra_par_flag
    Extra_par_flag = False

    global block_hr
    block_hr = 0
    global block_cr
    block_cr = 0
    global slaves
    slaves = {}
    global modbus_TCPIP_enable
    global modbus_RTU_enable
    modbus_TCPIP_enable=True
    modbus_RTU_enable=True
    global bool_parameter_dictionary
    global int_parameter_dictionary
    bool_parameter_dictionary={}
    int_parameter_dictionary={}
    
    global Master_write_value_dic1
    global Master_write_value_dic2
    global Master_write_value_dic3
    global Master_write_value_dic4
    global Master_write_count_dic1
    global Master_write_count_dic2
    global Master_write_count_dic3
    global Master_write_count_dic4
    Master_write_value_dic1 = {}
    Master_write_value_dic2 = {}
    Master_write_value_dic3 = {}
    Master_write_value_dic4 = {}
    Master_write_count_dic1 = {}
    Master_write_count_dic2 = {}
    Master_write_count_dic3 = {}
    Master_write_count_dic4 = {}
    global Master_write1_value_dic1
    global Master_write1_value_dic2
    global Master_write1_value_dic3
    global Master_write1_value_dic4

    Master_write1_value_dic1 = {}
    Master_write1_value_dic2 = {}
    Master_write1_value_dic3 = {}
    Master_write1_value_dic4 = {}

    global Master_write2_value_dic1
    global Master_write2_value_dic2
    global Master_write2_value_dic3
    global Master_write2_value_dic4

    Master_write2_value_dic1 = {}
    Master_write2_value_dic2 = {}
    Master_write2_value_dic3 = {}
    Master_write2_value_dic4 = {}
    global USB1_Status_Flag #
    USB1_Status_Flag.value = False
    global USB1_COM #
    USB1_COM.value=''
    global all_p_num
    global priority4_reg_list
    all_p_num=[]
    priority4_reg_list=[]
    global Master_written_JSON_Priority1_Flag
    Master_written_JSON_Priority1_Flag = False

    global Master_written_JSON_Priority2_Flag
    Master_written_JSON_Priority2_Flag = False

    global Master_written_JSON_Priority3_Flag
    Master_written_JSON_Priority3_Flag = False

    global Master_written_JSON_Priority4_Flag
    Master_written_JSON_Priority4_Flag = False

    global Process_exit_flag
    Process_exit_flag = False
    global Device_Address
    global master_usb

    global master_usb_check_flag 

    global USB_found
    USB_found = False

    global USB_port
    USB_port = ""
    global MASTER_USB_LIST
    MASTER_USB_LIST=[]
    global is_tcp_ip
    is_tcp_ip = False
    
    


def init (): 
    global stop_master_usb
    stop_master_usb = False
    
    global Print_Enable
    Print_Enable=False
    
    global single_slave
    single_slave=True
    # single_slave=False
    
    global run_once_flag
    run_once_flag = False

    global master_detected
    master_detected=False
    
    global all_set
    all_set = False

    global new_dict
    new_dict={}

    global thread_count
    thread_count = 0

    global list_dict_threads
    list_dict_threads=[]

    global new_connected_usb_list
    new_connected_usb_list=[]

    global Thread_Running_USB_list
    Thread_Running_USB_list=[]


    global start_all_threads
    start_all_threads=False

    global thread_list
    thread_list=[]

    global thread_bool_list
    thread_bool_list=[]

    global block
    block = False

    global block_2
    block_2 = False
    global end_controller_thread_check_b
    end_controller_thread_check_b= False


    global MASTER_USB_LIST
    MASTER_USB_LIST=Manager().list(range(0))

    global master_usb_check_list
    master_usb_check_list = []

    global master_usb_check_list_flag
    master_usb_check_list_flag = False

    global new_list
    new_list=[]
    global new_write_list
    new_write_list=[]
    global int_extra_par_dict
    int_extra_par_dict = {}
    global bool_extra_par_dict
    bool_extra_par_dict = {}
    global USB_found
    USB_found = False

    global Extra_par_flag
    Extra_par_flag = False

    global block_hr
    block_hr = 0
    global block_cr
    block_cr = 0
    global slaves
    slaves = {}
    global modbus_TCPIP_enable
    global modbus_RTU_enable
    modbus_TCPIP_enable=True
    modbus_RTU_enable=True
    global bool_parameter_dictionary
    global int_parameter_dictionary
    bool_parameter_dictionary={}
    int_parameter_dictionary={}


    global Master_write2_value_dic1
    global Master_write2_value_dic2
    global Master_write2_value_dic3
    global Master_write2_value_dic4

    
    Master_write2_value_dic1 = Manager().dict()
    Master_write2_value_dic2 = Manager().dict()
    Master_write2_value_dic3 = Manager().dict()
    Master_write2_value_dic4 = Manager().dict()



    global Master_write1_value_dic1
    global Master_write1_value_dic2
    global Master_write1_value_dic3
    global Master_write1_value_dic4

    Master_write1_value_dic1 = Manager().dict()
    Master_write1_value_dic2 = Manager().dict()
    Master_write1_value_dic3 = Manager().dict()
    Master_write1_value_dic4 = Manager().dict()

    global write_list 
    write_list = []


    global Master_write_value_dic1
    global Master_write_value_dic2
    global Master_write_value_dic3
    global Master_write_value_dic4
    global Master_write_count_dic1
    global Master_write_count_dic2
    global Master_write_count_dic3
    global Master_write_count_dic4
    Master_write_value_dic1 = Manager().dict()
    Master_write_value_dic2 = Manager().dict()
    Master_write_value_dic3 = Manager().dict()
    Master_write_value_dic4 = Manager().dict()
    Master_write_count_dic1 = Manager().dict()
    Master_write_count_dic2 = Manager().dict()
    Master_write_count_dic3 = Manager().dict()
    Master_write_count_dic4 = Manager().dict()

    global Write_dict_priority1
    global Write_dict_priority2
    global Write_dict_priority3
    global Write_dict_priority4

    Write_dict_priority1 = []
    Write_dict_priority2 = []
    Write_dict_priority3 = []
    Write_dict_priority4 = []    

    global priority1_reg_list
    global priority2_reg_list
    global priority3_reg_list
    global priority4_reg_list
    priority1_reg_list=[]
    priority2_reg_list=[]
    priority3_reg_list=[]
    priority4_reg_list=[]


    global Written_dict_priority1
    global Written_dict_priority2
    global Written_dict_priority3
    global Written_dict_priority4

    Written_dict_priority1 = False
    Written_dict_priority2 = False
    Written_dict_priority3 = False
    Written_dict_priority4 = False 
    

    global Config_Table_update_time
    Config_Table_update_time =''

    global first_time_write_to_controller
    first_time_write_to_controller = True




    global Controller_one_time_read
    Controller_one_time_read=False
    global Database_setup
    Database_setup=False

    global USB0
    USB0 =''
    global USB0_Status_Flag #
    USB0_Status_Flag=False
    global USB0_COM #
    USB0_COM=''
    global USB1_Status_Flag #
    USB1_Status_Flag = Manager().Value(c_bool,False)
    global USB1
    USB1=''
    global USB1_COM #
    USB1_COM=Manager().Value(c_char_p,'')
     
    global USB_MASTER_CHECK
    USB_MASTER_CHECK=True

    global USB_CONTROLLER_CHECK
    USB_CONTROLLER_CHECK=True

    global Server_dict
    global Server_read_flag
    Server_read_flag=False
    Server_dict={}
    
    reading = False

    global res_list
    res_list=[]
    global res_flag
    res_flag=False

    global master_usb_check_flag #
    master_usb_check_flag = Manager().list(range(0))
    global Master_search_count
    Master_search_count = -1


    ##################################################################
    #
    #json file read and write enable falgs
    #
    ##################################################################
    global JSON
    class JSON(enum.Enum):
        CONTROLLER_TO_MASTER_PRIORITY_1 = 1
        CONTROLLER_TO_MASTER_PRIORITY_2 = 2
        CONTROLLER_TO_MASTER_PRIORITY_3 = 3
        CONTROLLER_TO_MASTER_PRIORITY_4 = 4
        MASTER_TO_CONTROLLER_PRIORITY_1 = 5
        MASTER_TO_CONTROLLER_PRIORITY_2 = 6
        MASTER_TO_CONTROLLER_PRIORITY_3 = 7
        MASTER_TO_CONTROLLER_PRIORITY_4 = 8
        Read_Configuration = 9
        Write_Configuration =10
        CONFIGURATION_BACKUP =11
        PRIORITY_1 =12
        PRIORITY_2 =13
        PRIORITY_3 =14
        PRIORITY_4 =15


    global Master_Req_Timeout
    Master_Req_Timeout = 75
    global Dir
    Dir =  os.path.abspath(os.path.dirname(sys.argv[0]))

    global WebServer_JSON_Dir
    # WebServer_JSON_Dir= Dir.replace("/MainCode/Present_version","/Webserver/sem_django/sem/JSON_Files")

    global Controller_to_master_FileName_Priority1
    global Controller_to_master_FileName_Priority3
    global Controller_to_master_FileName_Priority2
    global Controller_to_master_FileName_Priority4
    global Master_to_controller_FileName_Priority1
    global Master_to_controller_FileName_Priority2
    global Master_to_controller_FileName_Priority3
    global Master_to_controller_FileName_Priority4
    global Read_Configuration_file
    global Write_Configuration_file
    global Configuration_backup
    global Priority_1_backup
    global Priority_2_backup
    global Priority_3_backup
    global Priority_4_backup
    global Check_Sec_Api
    global Check_Min_Api
    global Check_Hour_Api
    global Check_Conf_Api

    global Varient_XR75_Flg
    global Varient_Corelink_Flg
    Varient_XR75_Flg= True
    Varient_Corelink_Flg = False
    global Varient_ir33_Flg
    Varient_IR33_Flg=False
    global Varient_RTN_400_Flg
    Varient_RTN_400_Flg=False

    Dir_1 =  os.getcwd()
    Config_present = configparser.ConfigParser()
    Config_present.read("Controller_select.ini")
    Controller_varient= Config_present.get('CONTROLLER', 'varient')
    try:
        json_file_name = Config_present.get( Controller_varient, 'json_file_name')
        print("SEM is enabled for",Controller_varient)
    except :
        print("ini json_file_name error")
    try:
        back_up_json_file_name      =Config_present.get( Controller_varient, 'back_up_json_file_name')
    except :
        print("ini back_up_json_file_name error")
    try:
        Webserver_Sec_API           =Config_present.get( Controller_varient, 'Webserver_Sec_API')
    except :
        print("ini Webserver_Sec_API error")
    try:
        Webserver_Min_API           =Config_present.get( Controller_varient, 'Webserver_Min_API')
    except :
        print("ini Webserver_Min_API error")  
    try:
        Webserver_Hour_API          =Config_present.get( Controller_varient, 'Webserver_Hour_API')
    except :
        print("ini Webserver_Hour_API error")  
    try:
        Webserver_Configuration_API =Config_present.get( Controller_varient, 'Webserver_Configuration_API')
    except :
        print("ini Webserver_Configuration_API error")
    try:
        Webserver_json_file         =Config_present.get( Controller_varient, 'Webserver_json_file')
    except :
        print("ini Webserver_json_file error")

    WebServer_JSON_Dir= Dir.replace("/MainCode/Present_version",Webserver_json_file)
    Controller_to_master_FileName_Priority1 = Dir+'/JSON_Files/'+json_file_name+'/Reading_Priority_1.json'
    Controller_to_master_FileName_Priority2 = Dir+'/JSON_Files/'+json_file_name+'/Reading_Priority_2.json'
    Controller_to_master_FileName_Priority3 = Dir+'/JSON_Files/'+json_file_name+'/Reading_Priority_3.json'
    Controller_to_master_FileName_Priority4 = Dir+'/JSON_Files/'+json_file_name+'/Reading_Priority_4.json'

    Master_to_controller_FileName_Priority1 = Dir+'/JSON_Files/'+json_file_name+'/Writing_Priority_1.json'
    Master_to_controller_FileName_Priority2 = Dir+'/JSON_Files/'+json_file_name+'/Writing_Priority_2.json'
    Master_to_controller_FileName_Priority3 = Dir+'/JSON_Files/'+json_file_name+'/Writing_Priority_3.json'
    Master_to_controller_FileName_Priority4 = Dir+'/JSON_Files/'+json_file_name+'/Writing_Priority_4.json'

    Read_Configuration_file = Dir+'/JSON_Files/'+json_file_name+'/Read_Configuration.json'
    Write_Configuration_file = Dir+'/JSON_Files/'+json_file_name+'/Write_Configuration.json'

    Configuration_backup = Dir+'/JSON_Files/'+back_up_json_file_name+'/Configuration.json'
    Priority_1_backup = Dir+'/JSON_Files/'+back_up_json_file_name+'/Priority_1.json'
    Priority_2_backup = Dir+'/JSON_Files/'+back_up_json_file_name+'/Priority_2.json'
    Priority_3_backup = Dir+'/JSON_Files/'+back_up_json_file_name+'/Priority_3.json'
    Priority_4_backup = Dir+'/JSON_Files/'+back_up_json_file_name+'/Priority_4.json'

    Check_Sec_Api= Webserver_Sec_API
    Check_Min_Api= Webserver_Min_API
    Check_Hour_Api= Webserver_Hour_API
    Check_Conf_Api= Webserver_Configuration_API
   
    global ref_dictionary
    ref_dictionary=[]

    global Read_from_controller_Flag
    Read_from_controller_Flag=True

    global Write_to_controller_Flag
    Write_to_controller_Flag=True

    global Controller_extra_parameter_Flag
    Controller_extra_parameter_Flag=True


    global req_list
    req_list=[]
    global req_flag
    req_flag=False

    global client

    ################################################################## 
    # USB handeling global values
    ################################################################## 
    global Break_thread
    Break_thread=False

    global THREAD_list
    THREAD_list=[]

    global master_usb
    master_usb=Manager().Value(c_char_p,'')

    global Handshaking_list
    Handshaking_list=[]

    global Controller_usb
    Controller_usb=''

    global COMs
    COMs = []

    global Slave_ID
    Slave_ID=0

    #####################################
    #To change the priority timing      #
    #####################################
    global Priority_1
    Priority_1=10000

    global Priority_2
    Priority_2=15000

    global Priority_3
    Priority_3=15000

    global Priority_4
    Priority_4=10000
    ######################################

    global Timout_Flag
    Timout_Flag=False

    global Timeout_res_list
    Timeout_res_list=[]
    global Timeout_res_flag
    Timeout_res_flag=False
    
    global Timeout_req_list
    Timeout_req_list=[]
    global Timeout_req_flag
    Timeout_req_flag=False

    global Master_written_JSON_Flag
    Master_written_JSON_Flag =False

    global Master_written_JSON_Priority1_Flag
    Master_written_JSON_Priority1_Flag = False

    global Master_written_JSON_Priority2_Flag
    Master_written_JSON_Priority2_Flag = False

    global Master_written_JSON_Priority3_Flag
    Master_written_JSON_Priority3_Flag = False

    global Master_written_JSON_Priority4_Flag
    Master_written_JSON_Priority4_Flag = False

    global Master_written_conform_JSON_Priority1_Flag
    Master_written_conform_JSON_Priority1_Flag = True

    global Master_written_conform_JSON_Priority2_Flag
    Master_written_conform_JSON_Priority2_Flag = True

    global Master_written_conform_JSON_Priority3_Flag
    Master_written_conform_JSON_Priority3_Flag = True

    global Master_written_conform_JSON_Priority4_Flag
    Master_written_conform_JSON_Priority4_Flag = True

    global Configuration_from_server_written_flag
    Configuration_from_server_written_flag = True


    global Master_priority1_File_Read_Semaphore
    Master_priority1_File_Read_Semaphore = Semaphore(1)
    global Master_priority2_File_Read_Semaphore
    Master_priority2_File_Read_Semaphore = Semaphore(1)
    global Master_priority3_File_Read_Semaphore
    Master_priority3_File_Read_Semaphore = Semaphore(1)
    global Master_priority4_File_Write_Semaphore
    Master_priority4_File_Write_Semaphore = Semaphore(1)
    global Master_priority1_File_Write_Semaphore
    Master_priority1_File_Write_Semaphore = Semaphore(1)
    global Master_priority2_File_Write_Semaphore
    Master_priority2_File_Write_Semaphore = Semaphore(1)
    global Master_priority3_File_Write_Semaphore
    Master_priority3_File_Write_Semaphore = Semaphore(1)
    global Master_priority4_File_Read_Semaphore
    Master_priority4_File_Read_Semaphore = Semaphore(1)
    
    global Read_Configuration_Semaphore
    Read_Configuration_Semaphore = Semaphore(1)
    global Write_Configuration_Semaphore
    Write_Configuration_Semaphore = Semaphore(1)

   
    global Configuration_backup_Semaphore
    Configuration_backup_Semaphore = Semaphore(1)
    global Priority_1_backup_Semaphore
    Priority_1_backup_Semaphore = Semaphore(1)
    global Priority_2_backup_Semaphore
    Priority_2_backup_Semaphore = Semaphore(1)
    global Priority_3_backup_Semaphore
    Priority_3_backup_Semaphore = Semaphore(1)
    global Priority_4_backup_Semaphore
    Priority_4_backup_Semaphore = Semaphore(1)



    global e2_requested_flag
    e2_requested_flag=False

    bool_address_list = []
    bool_address_sorted_list = []
    bool_dict_list = []
    bool_sorted_dict_list = []

    integer_address_list = []
    integer_address_sorted_list = []
    integer_dict_list = []
    integer_sorted_dict_list = []

   
    data_dictionary_priority_ctm = JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_4) 
    try:
        for parameters_ctm in data_dictionary_priority_ctm["parameter"]:
            if(parameters_ctm["reg_name"] != "created_on" and parameters_ctm["reg_name"] != "modified_on"):
                if(parameters_ctm["type"]== "bool"):
                    bool_address_list.append(parameters_ctm["reg_num"])
                    bool_dict_list.append(parameters_ctm)
                elif(parameters_ctm["type"]== "integer"):
                    integer_address_list.append(parameters_ctm["reg_num"])
                    integer_dict_list.append(parameters_ctm)
        bool_address_sorted_list = bool_address_list.sort()
        integer_address_sorted_list = integer_address_list.sort()

        # sorting the list of dictionary according to list
        bool_sorted_dict_list = (sorted(bool_dict_list , key=lambda i:i['reg_num']))
        integer_sorted_dict_list = (sorted(integer_dict_list , key=lambda i:i['reg_num']))
    except:
        data_dictionary_priority_backup = JSON_File_Read(JSON.PRIORITY_4) 
        JSON_File_Write(JSON.CONTROLLER_TO_MASTER_PRIORITY_4, data_dictionary_priority_backup)
        JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_4, data_dictionary_priority_backup)

    JSON_File_Write(JSON.CONTROLLER_TO_MASTER_PRIORITY_4, data_dictionary_priority_ctm)
    data_dictionary_priority_ctm = JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_1) 
    data_dictionary_priority_mtc = JSON_File_Read(JSON.MASTER_TO_CONTROLLER_PRIORITY_1) 
    data_dictionary_priority_backup = JSON_File_Read(JSON.PRIORITY_1) 
    JSON_ctm_Flag = False
    JSON_mts_Flag = False
    try:
        for parameters_ctm in data_dictionary_priority_ctm["parameter"]:
            if(parameters_ctm["reg_name"] != "created_on" and parameters_ctm["reg_name"] != "modified_on"):
                if(parameters_ctm["reg_name"]):
                    if(parameters_ctm["reg_num"]):
                        if(parameters_ctm["type"]):
                            pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
    except:
        JSON_ctm_Flag = True
    try:
        for parameters_mtc in data_dictionary_priority_mtc["parameter"]:
            if(parameters_mtc["reg_name"] != "created_on" and parameters_mtc["reg_name"] != "modified_on"):
                if(parameters_mtc["reg_name"]):
                    if(parameters_mtc["reg_num"]):
                        if(parameters_mtc["type"]):
                            pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
    except:
        JSON_mts_Flag = True
    if(JSON_ctm_Flag == True and JSON_mts_Flag == True):
        JSON_File_Write(JSON.CONTROLLER_TO_MASTER_PRIORITY_1, data_dictionary_priority_backup)
        JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_1, data_dictionary_priority_backup)
    elif(JSON_ctm_Flag == True and JSON_mts_Flag == False):
        JSON_File_Write(JSON.CONTROLLER_TO_MASTER_PRIORITY_1, data_dictionary_priority_mtc)
    elif(JSON_mts_Flag == True and JSON_ctm_Flag == False):
        JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_1, data_dictionary_priority_ctm)

    data_dictionary_priority_ctm = JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_2) 
    data_dictionary_priority_mtc = JSON_File_Read(JSON.MASTER_TO_CONTROLLER_PRIORITY_2) 
    data_dictionary_priority_backup = JSON_File_Read(JSON.PRIORITY_2) 
    JSON_ctm_Flag = False
    JSON_mts_Flag = False
    try:
        for parameters_ctm in data_dictionary_priority_ctm["parameter"]:
            if(parameters_ctm["reg_name"] != "created_on" and parameters_ctm["reg_name"] != "modified_on"):
                if(parameters_ctm["reg_name"]):
                    if(parameters_ctm["reg_num"]):
                        if(parameters_ctm["type"]):
                            pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
    except:
        JSON_ctm_Flag = True
    try:
        for parameters_mtc in data_dictionary_priority_mtc["parameter"]:
            if(parameters_mtc["reg_name"] != "created_on" and parameters_mtc["reg_name"] != "modified_on"):
                if(parameters_mtc["reg_name"]):
                    if(parameters_mtc["reg_num"]):
                        if(parameters_mtc["type"]):
                            pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
    except:
        JSON_mts_Flag = True
    if(JSON_ctm_Flag == True and JSON_mts_Flag == True):
        JSON_File_Write(JSON.CONTROLLER_TO_MASTER_PRIORITY_2, data_dictionary_priority_backup)
        JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_2, data_dictionary_priority_backup)
    elif(JSON_ctm_Flag == True and JSON_mts_Flag == False):
        JSON_File_Write(JSON.CONTROLLER_TO_MASTER_PRIORITY_2, data_dictionary_priority_mtc)
    elif(JSON_mts_Flag == True and JSON_ctm_Flag == False):
        JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_2, data_dictionary_priority_ctm)

    data_dictionary_priority_ctm = JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_3) 
    data_dictionary_priority_mtc = JSON_File_Read(JSON.MASTER_TO_CONTROLLER_PRIORITY_3) 
    data_dictionary_priority_backup = JSON_File_Read(JSON.PRIORITY_3) 
    JSON_ctm_Flag = False
    JSON_mts_Flag = False
    try:
        for parameters_ctm in data_dictionary_priority_ctm["parameter"]:
            if(parameters_ctm["reg_name"] != "created_on" and parameters_ctm["reg_name"] != "modified_on"):
                if(parameters_ctm["reg_name"]):
                    if(parameters_ctm["reg_num"]):
                        if(parameters_ctm["type"]):
                            pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
    except:
        JSON_ctm_Flag = True
    try:
        for parameters_mtc in data_dictionary_priority_mtc["parameter"]:
            if(parameters_mtc["reg_name"] != "created_on" and parameters_mtc["reg_name"] != "modified_on"):
                if(parameters_mtc["reg_name"]):
                    if(parameters_mtc["reg_num"]):
                        if(parameters_mtc["type"]):
                            pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
    except:
        JSON_mts_Flag = True
    if(JSON_ctm_Flag == True and JSON_mts_Flag == True):
        JSON_File_Write(JSON.CONTROLLER_TO_MASTER_PRIORITY_3, data_dictionary_priority_backup)
        JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_3, data_dictionary_priority_backup)
    elif(JSON_ctm_Flag == True and JSON_mts_Flag == False):
        JSON_File_Write(JSON.CONTROLLER_TO_MASTER_PRIORITY_3, data_dictionary_priority_mtc)
    elif(JSON_mts_Flag == True and JSON_ctm_Flag == False):
        JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_3, data_dictionary_priority_ctm)


    data_dictionary_priority_ctm = JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_4) 
    data_dictionary_priority_mtc = JSON_File_Read(JSON.MASTER_TO_CONTROLLER_PRIORITY_4) 
    data_dictionary_priority_backup = JSON_File_Read(JSON.PRIORITY_4) 
    JSON_ctm_Flag = False
    JSON_mts_Flag = False
    try:
        for parameters_ctm in data_dictionary_priority_ctm["parameter"]:
            if(parameters_ctm["reg_name"] != "created_on" and parameters_ctm["reg_name"] != "modified_on"):
                if(parameters_ctm["reg_name"]):
                    if(parameters_ctm["reg_num"]):
                        if(parameters_ctm["type"]):
                            pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
    except:
        JSON_ctm_Flag = True
    try:
        for parameters_mtc in data_dictionary_priority_mtc["parameter"]:
            if(parameters_mtc["reg_name"] != "created_on" and parameters_mtc["reg_name"] != "modified_on"):
                if(parameters_mtc["reg_name"]):
                    if(parameters_mtc["reg_num"]):
                        if(parameters_mtc["type"]):
                            pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
    except:
        JSON_mts_Flag = True
    if(JSON_ctm_Flag == True and JSON_mts_Flag == True):
        JSON_File_Write(JSON.CONTROLLER_TO_MASTER_PRIORITY_4, data_dictionary_priority_backup)
        JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_4, data_dictionary_priority_backup)
    elif(JSON_ctm_Flag == True and JSON_mts_Flag == False):
        JSON_File_Write(JSON.CONTROLLER_TO_MASTER_PRIORITY_4, data_dictionary_priority_mtc)
    elif(JSON_mts_Flag == True and JSON_ctm_Flag == False):
        JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_4, data_dictionary_priority_ctm)

    data_dictionary_priority_ctm = JSON_File_Read(JSON.Read_Configuration) 
    data_dictionary_priority_mtc = JSON_File_Read(JSON.Write_Configuration) 
    data_dictionary_priority_backup = JSON_File_Read(JSON.CONFIGURATION_BACKUP) 
    JSON_ctm_Flag = False
    JSON_mts_Flag = False
    try:
        for parameters_ctm in data_dictionary_priority_ctm["parameter"]:
            if(parameters_ctm["reg_name"] != "created_on" and parameters_ctm["reg_name"] != "modified_on"):
                if(parameters_ctm["reg_name"]):
                    if(parameters_ctm["reg_num"]):
                        if(parameters_ctm["type"]):
                            pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
    except:
        JSON_ctm_Flag = True
    try:
        for parameters_mtc in data_dictionary_priority_mtc["parameter"]:
            if(parameters_mtc["reg_name"] != "created_on" and parameters_mtc["reg_name"] != "modified_on"):
                if(parameters_mtc["reg_name"]):
                    if(parameters_mtc["reg_num"]):
                        if(parameters_mtc["type"]):
                            pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
    except:
        JSON_mts_Flag = True
    if(JSON_ctm_Flag == True and JSON_mts_Flag == True):
        JSON_File_Write(JSON.Read_Configuration, data_dictionary_priority_backup)
        JSON_File_Write(JSON.Write_Configuration, data_dictionary_priority_backup)
    elif(JSON_ctm_Flag == True and JSON_mts_Flag == False):
        JSON_File_Write(JSON.Read_Configuration, data_dictionary_priority_mtc)
    elif(JSON_mts_Flag == True and JSON_ctm_Flag == False):
        JSON_File_Write(JSON.Write_Configuration, data_dictionary_priority_ctm)

    global Device_Address
    Device_Address = Manager().Value(c_uint8,0)
    global all_p_num
    global Protity1_parameter_count
    all_p_num=Manager().list(range(0))
    global REF_DICT_PRIORITY_1

    global REF_DICT_PRIORITY_2

    global REF_DICT_PRIORITY_3

    global REF_DICT_PRIORITY_4
    data_dictionary_Master_To_Controller_Priority_1 = JSON_File_Read(JSON.MASTER_TO_CONTROLLER_PRIORITY_1) 
    REF_DICT_PRIORITY_1=data_dictionary_Master_To_Controller_Priority_1
    data_dictionary_Master_To_Controller_Priority_2 = JSON_File_Read(JSON.MASTER_TO_CONTROLLER_PRIORITY_2) 
    REF_DICT_PRIORITY_2=data_dictionary_Master_To_Controller_Priority_2
    data_dictionary_Master_To_Controller_Priority_3 = JSON_File_Read(JSON.MASTER_TO_CONTROLLER_PRIORITY_3) 
    REF_DICT_PRIORITY_3=data_dictionary_Master_To_Controller_Priority_3
    data_dictionary_Master_To_Controller_Priority_4 = JSON_File_Read(JSON.MASTER_TO_CONTROLLER_PRIORITY_4) 
    REF_DICT_PRIORITY_4=data_dictionary_Master_To_Controller_Priority_4
    Protity1_parameter_count = 0
    for parameters_10sec in data_dictionary_Master_To_Controller_Priority_1["parameter"]:
        if(parameters_10sec["reg_name"] != "created_on" and parameters_10sec["reg_name"] != "modified_on"):
            all_p_num.append( parameters_10sec["reg_num"] )
            priority1_reg_list.append(parameters_10sec["reg_num"])
    for parameters_5min in data_dictionary_Master_To_Controller_Priority_2["parameter"]:
        if(parameters_5min["reg_name"] != "created_on" and parameters_5min["reg_name"] != "modified_on"):
            all_p_num.append( parameters_5min["reg_num"] )
            priority2_reg_list.append(parameters_5min["reg_num"])
    for parameters_4hours in data_dictionary_Master_To_Controller_Priority_3["parameter"]:
        if(parameters_4hours["reg_name"] != "created_on" and parameters_4hours["reg_name"] != "modified_on"):
            all_p_num.append( parameters_4hours["reg_num"] )
            priority3_reg_list.append(parameters_4hours["reg_num"])
    for parameters_list_dont_have in data_dictionary_Master_To_Controller_Priority_4["parameter"]:
        if(parameters_list_dont_have["reg_name"] != "created_on" and parameters_list_dont_have["reg_name"] != "modified_on"):
            all_p_num.append( parameters_list_dont_have["reg_num"] )
            priority4_reg_list.append(parameters_list_dont_have["reg_num"])
            Protity1_parameter_count+=1
    global first_configuration_dict
    first_configuration_dict={}

    global PREVIOUS_CONFIGURATION_DICTIONARY
    PREVIOUS_CONFIGURATION_DICTIONARY={}
    global read_list_dic_priority1
    global read_list_dic_priority2
    global read_list_dic_priority3
    global read_list_dic_priority4

    read_list_dic_priority1, sorted_dictionary_data=Json_file_sorting(JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_1))
    JSON_File_Write(JSON.CONTROLLER_TO_MASTER_PRIORITY_1, sorted_dictionary_data)
    JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_1, sorted_dictionary_data)
    JSON_File_Write(JSON.PRIORITY_1, sorted_dictionary_data)

    read_list_dic_priority2, sorted_dictionary_data=Json_file_sorting(JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_2))
    JSON_File_Write(JSON.CONTROLLER_TO_MASTER_PRIORITY_2, sorted_dictionary_data)
    JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_2, sorted_dictionary_data)
    JSON_File_Write(JSON.PRIORITY_2, sorted_dictionary_data)

    read_list_dic_priority3, sorted_dictionary_data=Json_file_sorting(JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_3))
    JSON_File_Write(JSON.CONTROLLER_TO_MASTER_PRIORITY_3, sorted_dictionary_data)
    JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_3, sorted_dictionary_data)
    JSON_File_Write(JSON.PRIORITY_3, sorted_dictionary_data)

    read_list_dic_priority4, sorted_dictionary_data=Json_file_sorting(JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_4))
    JSON_File_Write(JSON.CONTROLLER_TO_MASTER_PRIORITY_4, sorted_dictionary_data)
    JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_4, sorted_dictionary_data)
    JSON_File_Write(JSON.PRIORITY_4, sorted_dictionary_data)
    global number_of_extra_parmeter
    number_of_extra_parmeter = len(sorted_dictionary_data["parameter"])

    Data={"time": "2022-06-16T07:05:12.458771Z"}
    with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','w') as file:
        json.dump(Data,file,indent=5)
        file.close()
    with open(Master_Controller_Utils.Dir+'/read_write_database/time_update_back_up.json','w') as file:
        json.dump(Data,file,indent=5)
        file.close()

def Json_file_sorting(JSON_Data):
    JSON_Data1={"parameter":[]}
    JSON_Data2={"parameter":[]}
    for parameter in JSON_Data["parameter"]:
        if(parameter["reg_name"] != "created_on" and parameter["reg_name"] != "modified_on"):
            JSON_Data1["parameter"].append(parameter)
        else:
            JSON_Data2["parameter"].append(parameter)
    JSON_Data1["parameter"] = sorted(JSON_Data1["parameter"], key=lambda i: i['reg_num'])
    JSON1_dic = []
    flag = False
    reg = 0
    index = -1
    Key = 0
    value_type = ""
    for parameter in JSON_Data1["parameter"]:
        try:
            if(parameter["Access_type"]):
                pass
        except:
            parameter["Access_type"] = "Read_Write"
        try:
            if(parameter["factor"]):
                pass
        except:
            parameter["factor"] = 1
        try:
            if(parameter["offset"]):
                pass
        except:
            parameter["offset"] = 0

        if(flag == False and (parameter["Access_type"] == "Read_Write" or parameter["Access_type"] == "Read")):
            flag = True
            reg=parameter["reg_num"]
            Key = reg
            JSON1_dic.append({"start_address":parameter["reg_num"],"address_list":[parameter["reg_num"]]})
            index+=1
            value_type = parameter["type"]
        else:
            if(parameter["reg_num"] == reg+1 and value_type == parameter["type"] and (parameter["Access_type"] == "Read_Write" or parameter["Access_type"] == "Read")):
                if(parameter["type"] == "bool" or len(JSON1_dic[index]["address_list"])<5):
                    reg=parameter["reg_num"]
                    JSON1_dic[index]["address_list"].append(parameter["reg_num"])
                elif(parameter["Access_type"] == "Read_Write" or parameter["Access_type"] == "Read"):
                    reg=parameter["reg_num"]
                    Key = reg
                    JSON1_dic.append({"start_address":parameter["reg_num"],"address_list":[parameter["reg_num"]]})
                    index+=1  
                    value_type = parameter["type"]
            elif(parameter["Access_type"] == "Read_Write" or parameter["Access_type"] == "Read"):
                reg=parameter["reg_num"]
                Key = reg
                JSON1_dic.append({"start_address":parameter["reg_num"],"address_list":[parameter["reg_num"]]})
                index+=1  
                value_type = parameter["type"]
            pass
        pass
    for parameter in JSON_Data2["parameter"] :
        JSON_Data1["parameter"].append(parameter)
    return [JSON1_dic,JSON_Data1]

def First_read_controller():
    data_dictionary_Controller_to_Master_Priority1 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_1)
    JSON_data_dictionary = Read_Controller_data(data_dictionary_Controller_to_Master_Priority1,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1)
    if(JSON_data_dictionary != []):
        Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_1, JSON_data_dictionary)
    data_dictionary_Controller_to_Master_Priority2 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_2)
    JSON_data_dictionary = Read_Controller_data(data_dictionary_Controller_to_Master_Priority2,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2)
    if(JSON_data_dictionary != []):
        Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_2, JSON_data_dictionary) 
    data_dictionary_Controller_to_Master_Priority3 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_3)
    JSON_data_dictionary = Read_Controller_data(data_dictionary_Controller_to_Master_Priority3,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3)
    if(JSON_data_dictionary != []):
            Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_3, JSON_data_dictionary) 
    data_dictionary_Controller_to_Master_Priority4 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_4)
    JSON_data_dictionary = Read_Controller_data(data_dictionary_Controller_to_Master_Priority4,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4)
    if(JSON_data_dictionary != []):
            Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_4, JSON_data_dictionary) 
    pass


def master_controller_usb_handle():
    global USB0_Status_Flag #
    global USB1_Status_Flag #
    global USB1_COM
    global USB0_COM
    global MASTER_USB_LIST
    USB_COM=[]
    USB_CONECTED_LIST=[]
    global thread_list
    global start_all_threads
    global Thread_Running_USB_list
    global thread_bool_list
    global run_once_flag
    global list_dict_threads
    global all_set
    global master_usb_check_list
    while 1:

        USB_CONECTED_LIST=[]
        if(USB0_Status_Flag == False):
            if((len(list_dict_threads) == 0 )):
                print("Trying to connect controller")
                CONNECT_TO_CONTROLLER(USB_COM=[])
                sleep(1)
            else:
                list_dict_threads.clear()
        else:  
            if(USB0_Status_Flag == True):
                pts= prtlst.comports()
                for pt in pts:
                    if 'USB' in pt[1]: #check 'USB' string in device description
                        USB_CONECTED_LIST.append(pt[0])
                if(USB0_COM != ''):
                    if not USB0_COM in USB_CONECTED_LIST:
                        print("Controller removed")
                        list_dict_threads.clear()
                        USB0_Status_Flag = False
                        thread_bool_list = []
                        start_all_threads = False
                        Thread_Running_USB_list = []
                        run_once_flag=False
                        all_set = False
        print("length of MASTER_USB_LIST=",len(MASTER_USB_LIST))
        if((len(MASTER_USB_LIST) >= 0) and (USB0_Status_Flag == True) and (all_set == True)):
            sleep(5)
            print(" Trying (Import)_CONNECT_TO_MASTER")
            import_CONNECT_TO_MASTER(USB_COM)
            sleep(1) 
        else: 
            pts= prtlst.comports()
            for pt in pts:
                if 'USB' in pt[1]: #check 'USB' string in device description
                    USB_CONECTED_LIST.append(pt[0])
            for i in master_usb_check_list:
                if i not in USB_CONECTED_LIST:
                    master_usb_check_list.clear()
        sleep(1)
        

def CONNECT_TO_MASTER_CONTROLLER():
    global Device_Address
    global USB0
    global USB0_Status_Flag #
    USB0_Status_Flag=False
    global USB0_COM #
    USB0_COM=''
    global client
    global USB1_Status_Flag #
    USB1_Status_Flag.value=False
    global USB1
    global USB1_COM #
    USB1_COM.value=''


    address=1
    THREAD_list=[]
    COMs=[]
    pts= prtlst.comports()
    for pt in pts:
        if 'USB' in pt[1]: #check 'USB' string in device description
            COMs.append(pt[0])
    if( COMs != []):
        Master_connected = import_CONNECT_TO_MASTER(COMs)
        if(Master_connected == False):
            Device_Address.value = 0
        CONNECT_TO_CONTROLLER(COMs)

def crc_modbus(buf):
    num=len(buf)
    crc = 0xFFFF
    for pos in range (num):
        crc ^=int((buf[pos]))  
        for i in range (8, 0, -1):
            if ((crc & 0x0001) != 0):
                crc >>= 1 
                crc ^= 0xA001
            else:                         
                crc >>= 1
    
    return crc

def JSON_File_Read(JSON_File_info):
    global JSON
    global Controller_to_master_FileName_Priority1
    global Controller_to_master_FileName_Priority2
    global Controller_to_master_FileName_Priority3
    global Controller_to_master_FileName_Priority4
    global Master_to_controller_FileName_Priority1
    global Master_to_controller_FileName_Priority2
    global Master_to_controller_FileName_Priority3
    global Master_to_controller_FileName_Priority4
    global Read_Configuration_file
    global Write_Configuration_file
    global Configuration_backup
    global Priority_1_backup
    global Priority_2_backup
    global Priority_3_backup
    global Priority_4_backup


    if(JSON.CONTROLLER_TO_MASTER_PRIORITY_1 == JSON_File_info):
        Master_priority1_File_Read_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Controller_to_master_FileName_Priority1,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Master_priority1_File_Read_Semaphore.release()
            return JSON_Data
        except Exception as e:
            print(" file read =",e)
            Master_priority1_File_Read_Semaphore.release()
            return []
    elif(JSON.CONTROLLER_TO_MASTER_PRIORITY_2 == JSON_File_info):
        Master_priority2_File_Read_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Controller_to_master_FileName_Priority2,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Master_priority2_File_Read_Semaphore.release()
            return JSON_Data
        except:
            Master_priority2_File_Read_Semaphore.release()
            return []       
    elif(JSON.CONTROLLER_TO_MASTER_PRIORITY_3 == JSON_File_info):
        Master_priority3_File_Read_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Controller_to_master_FileName_Priority3,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Master_priority3_File_Read_Semaphore.release()
            return JSON_Data
        except:
            Master_priority3_File_Read_Semaphore.release()
            return []  
    elif(JSON.CONTROLLER_TO_MASTER_PRIORITY_4== JSON_File_info):
        Master_priority4_File_Read_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Controller_to_master_FileName_Priority4,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Master_priority4_File_Read_Semaphore.release()
            return JSON_Data
        except:
            Master_priority4_File_Read_Semaphore.release()
            return [] 


    elif(JSON.MASTER_TO_CONTROLLER_PRIORITY_1 == JSON_File_info):
        Master_priority1_File_Write_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Master_to_controller_FileName_Priority1,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Master_priority1_File_Write_Semaphore.release()
            return JSON_Data
        except:
            Master_priority1_File_Write_Semaphore.release()
            return [] 
    elif(JSON.MASTER_TO_CONTROLLER_PRIORITY_2 == JSON_File_info):
        Master_priority2_File_Write_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Master_to_controller_FileName_Priority2,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Master_priority2_File_Write_Semaphore.release()
            return JSON_Data
        except:
            Master_priority2_File_Write_Semaphore.release()
            return []      
    elif(JSON.MASTER_TO_CONTROLLER_PRIORITY_3 == JSON_File_info):
        Master_priority3_File_Write_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Master_to_controller_FileName_Priority3,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Master_priority3_File_Write_Semaphore.release()
            return JSON_Data
        except:
            Master_priority3_File_Write_Semaphore.release()
            return []    
    elif(JSON.MASTER_TO_CONTROLLER_PRIORITY_4 == JSON_File_info):
        Master_priority4_File_Write_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Master_to_controller_FileName_Priority4,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Master_priority4_File_Write_Semaphore.release()
            return JSON_Data
        except:
            Master_priority4_File_Write_Semaphore.release()
            return []   
            
    elif(JSON.Read_Configuration == JSON_File_info):
        Read_Configuration_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Read_Configuration_file,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Read_Configuration_Semaphore.release()
            return JSON_Data
        except:
            Read_Configuration_Semaphore.release()
            return []  
    elif(JSON.Write_Configuration == JSON_File_info):
        Write_Configuration_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Write_Configuration_file,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Write_Configuration_Semaphore.release()
            return JSON_Data
        except:
            Write_Configuration_Semaphore.release()
            return [] 
    elif(JSON.CONFIGURATION_BACKUP == JSON_File_info):
        Configuration_backup_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Configuration_backup,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Configuration_backup_Semaphore.release()
            return JSON_Data
        except:
            Configuration_backup_Semaphore.release()
            return [] 
    elif(JSON.PRIORITY_1 == JSON_File_info):
        Priority_1_backup_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Priority_1_backup,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Priority_1_backup_Semaphore.release()
            return JSON_Data
        except:
            Priority_1_backup_Semaphore.release()
            return [] 
    elif(JSON.PRIORITY_2 == JSON_File_info):
        Priority_2_backup_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Priority_2_backup,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Priority_2_backup_Semaphore.release()
            return JSON_Data
        except:
            Priority_2_backup_Semaphore.release()
            return [] 
    elif(JSON.PRIORITY_3 == JSON_File_info):
        Priority_3_backup_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Priority_3_backup,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Priority_3_backup_Semaphore.release()
            return JSON_Data
        except:
            Priority_3_backup_Semaphore.release()
            return []
    elif(JSON.PRIORITY_4 == JSON_File_info):
        Priority_4_backup_Semaphore.acquire()
        try:
            JSON_Data={}
            with open(Priority_4_backup,'r') as file:
                JSON_Data_string=file.read()
                JSON_Data=json.loads(JSON_Data_string)
                file.close()
            Priority_4_backup_Semaphore.release()
            return JSON_Data
        except:
            Priority_4_backup_Semaphore.release()
            return []

def JSON_File_Write(JSON_File_info, File_data,json_flag_set=True):
    global JSON
    global Controller_to_master_FileName_Priority1
    global Controller_to_master_FileName_Priority2
    global Controller_to_master_FileName_Priority3
    global Controller_to_master_FileName_Priority4
    global Master_to_controller_FileName_Priority1
    global Master_to_controller_FileName_Priority2
    global Master_to_controller_FileName_Priority3
    global Master_to_controller_FileName_Priority4
    global Master_written_JSON_Priority1_Flag
    global Master_written_JSON_Priority2_Flag
    global Master_written_JSON_Priority3_Flag
    global Master_written_JSON_Priority4_Flag
    global Read_Configuration_file
    global Write_Configuration_file
    global Configuration_backup
    global Priority_1_backup
    global Priority_2_backup
    global Priority_3_backup
    global Priority_4_backup

    if(JSON.CONTROLLER_TO_MASTER_PRIORITY_1 == JSON_File_info):
        Master_priority1_File_Read_Semaphore.acquire()
        try:
            
            with open(Controller_to_master_FileName_Priority1,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
            Master_priority1_File_Read_Semaphore.release()
        except:
            Master_priority1_File_Read_Semaphore.release()
            
    elif(JSON.CONTROLLER_TO_MASTER_PRIORITY_2 == JSON_File_info):
        Master_priority2_File_Read_Semaphore.acquire()
        try:
            with open(Controller_to_master_FileName_Priority2,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
            Master_priority2_File_Read_Semaphore.release()  
        except:
            Master_priority2_File_Read_Semaphore.release()
                 
    elif(JSON.CONTROLLER_TO_MASTER_PRIORITY_3 == JSON_File_info):
        Master_priority3_File_Read_Semaphore.acquire()
        try:
            with open(Controller_to_master_FileName_Priority3,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
            Master_priority3_File_Read_Semaphore.release()
        except:
            Master_priority3_File_Read_Semaphore.release()
            
    elif(JSON.CONTROLLER_TO_MASTER_PRIORITY_4== JSON_File_info):
        Master_priority4_File_Read_Semaphore.acquire()
        try:
            with open(Controller_to_master_FileName_Priority4,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
            Master_priority4_File_Read_Semaphore.release()
        except:
            Master_priority4_File_Read_Semaphore.release()
            
    elif(JSON.MASTER_TO_CONTROLLER_PRIORITY_1 == JSON_File_info):
        Master_priority1_File_Write_Semaphore.acquire()
        try:
            with open(Master_to_controller_FileName_Priority1,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
                if(json_flag_set == True):
                    Master_written_JSON_Priority1_Flag = True
            Master_priority1_File_Write_Semaphore.release()
        except:
            Master_priority1_File_Write_Semaphore.release()
            
    elif(JSON.MASTER_TO_CONTROLLER_PRIORITY_2 == JSON_File_info):
        Master_priority2_File_Write_Semaphore.acquire()
        try:
            with open(Master_to_controller_FileName_Priority2,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
                if(json_flag_set == True):
                    Master_written_JSON_Priority2_Flag = True
            Master_priority2_File_Write_Semaphore.release()
        except:
            Master_priority2_File_Write_Semaphore.release()
                  
    elif(JSON.MASTER_TO_CONTROLLER_PRIORITY_3 == JSON_File_info):
        Master_priority3_File_Write_Semaphore.acquire()
        try:
            with open(Master_to_controller_FileName_Priority3,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
                if(json_flag_set == True):
                    Master_written_JSON_Priority3_Flag = True
            Master_priority3_File_Write_Semaphore.release()
        except:
            Master_priority3_File_Write_Semaphore.release()
               
    elif(JSON.MASTER_TO_CONTROLLER_PRIORITY_4 == JSON_File_info):
        Master_priority4_File_Write_Semaphore.acquire()
        try:
            with open(Master_to_controller_FileName_Priority4,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
                if(json_flag_set == True):
                    Master_written_JSON_Priority4_Flag = True
            Master_priority4_File_Write_Semaphore.release()
        except:
            Master_priority4_File_Write_Semaphore.release()
               
    elif(JSON.Read_Configuration == JSON_File_info):
        Read_Configuration_Semaphore.acquire()
        try:
            with open(Read_Configuration_file,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
            Read_Configuration_Semaphore.release()
        except:
            Read_Configuration_Semaphore.release()
                
    elif(JSON.Write_Configuration == JSON_File_info):
        Write_Configuration_Semaphore.acquire()
        try:
            with open(Write_Configuration_file,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
            Write_Configuration_Semaphore.release()
        except:
            Write_Configuration_Semaphore.release()
                
    elif(JSON.CONFIGURATION_BACKUP == JSON_File_info):
        Configuration_backup_Semaphore.acquire()
        try:
            with open(Configuration_backup,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
                Configuration_backup_Semaphore.release()
        except:
            Configuration_backup_Semaphore.release()
                
    elif(JSON.PRIORITY_1 == JSON_File_info):
        Priority_1_backup_Semaphore.acquire()
        try:
            with open(Priority_1_backup,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
            Priority_1_backup_Semaphore.release()
        except:
            Priority_1_backup_Semaphore.release()
                
    elif(JSON.PRIORITY_2 == JSON_File_info):
        Priority_2_backup_Semaphore.acquire()
        try:
            with open(Priority_2_backup,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
            Priority_2_backup_Semaphore.release()
        except:
            Priority_2_backup_Semaphore.release()
                
    elif(JSON.PRIORITY_3 == JSON_File_info):
        Priority_3_backup_Semaphore.acquire()
        try:
            with open(Priority_3_backup,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
            Priority_3_backup_Semaphore.release()
        except:
            Priority_3_backup_Semaphore.release()
                
    elif(JSON.PRIORITY_4 == JSON_File_info):
        Priority_4_backup_Semaphore.acquire()
        try:
            with open(Priority_4_backup,'w') as file:
                json.dump(File_data,file,indent=5)
                file.close()
            Priority_4_backup_Semaphore.release()
        except:
            Priority_4_backup_Semaphore.release()
            

def data_written_from_Configuration( dictionary ):
    dictionary.pop("id")
    dictionary.pop("created_on")
    dictionary.pop("modified_on")
    for dictionary_key,dictionary_value in dictionary.items():
        if(str(dictionary_value) == 'True'):
            dictionary[dictionary_key]= 'true'
        elif(str(dictionary_value) == 'False'):
            dictionary[dictionary_key]='false'
        elif(str(dictionary_value) == "0" or str(dictionary_value) == "1" or str(dictionary_value) == "2" or str(dictionary_value) == "3" or str(dictionary_value) == "4" or str(dictionary_value) == "5" or str(dictionary_value) == "6" or str(dictionary_value) == "7" or str(dictionary_value) == "8" or str(dictionary_value) == "9" or str(dictionary_value) == "10"):
            dictionary[dictionary_key]=int(dictionary_value)
    JSON_File_Write(JSON.Write_Configuration , [dictionary]) 
    global ref_dictionary
    first_configuration_dict={}
    json_writing_dictionary={}
    priority1_written_flag =False
    priority2_written_flag =False
    priority3_written_flag =False
    data_dictionary_Controller_To_Master_Priority_1 = JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_1) 
    data_dictionary_Controller_To_Master_Priority_2 = JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_2) 
    data_dictionary_Controller_To_Master_Priority_3 = JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_3) 
    CONFIGURATION_DICTIONARY = JSON_File_Read(JSON.Write_Configuration)
    PREVIOUS_CONFIGURATION_DICTIONARY =CONFIGURATION_DICTIONARY[0] 
    first_configuration_dict=CONFIGURATION_DICTIONARY[0] 

    Write_Flag = False
    for parameter_name,parameter_value in PREVIOUS_CONFIGURATION_DICTIONARY.items():
        found = False
        if(found == False):
            for parameters_10sec in data_dictionary_Controller_To_Master_Priority_1["parameter"]:
                if(parameter_name != "created_on" and parameter_name != "modified_on"  and parameters_10sec['reg_name'] == parameter_name ):
                    if(parameters_10sec['reg_name'] in Master_Controller_Utils.Master_write2_value_dic1.values()):
                        first_configuration_dict[parameter_name] = Master_Controller_Utils.Master_write_value_dic1[parameters_10sec["reg_num"]]
                        if(first_configuration_dict[parameter_name] == 'True' or first_configuration_dict[parameter_name] == 'true'):
                            first_configuration_dict[parameter_name] = 'true'
                            found = True
                            break
                        elif(first_configuration_dict[parameter_name] == 'False' or first_configuration_dict[parameter_name] == 'false'):
                            first_configuration_dict[parameter_name] = 'false'
                            found = True
                            break
                    elif((parameters_10sec["value"] == 'True' or parameters_10sec["value"] == 'true') and (parameter_value == 'False' or parameter_value == 'false')):
                        first_configuration_dict[parameter_name] = 'false'
                        new_dictinoary={}
                        new_dictinoary[parameters_10sec['reg_num']]='False'
                        json_writing_dictionary.update(new_dictinoary)
                        priority1_written_flag =True
                        print("webserver is writing=",parameter_name, new_dictinoary )
                        Write_Flag =True
                        found = True
                        break

                    elif((parameters_10sec["value"] == 'False' or  parameters_10sec["value"] == 'false') and (parameter_value == 'True' or parameter_value == 'true')):
                        first_configuration_dict[parameter_name] = 'true'
                        new_dictinoary={}
                        new_dictinoary[parameters_10sec['reg_num']]='True'
                        json_writing_dictionary.update(new_dictinoary)
                        priority1_written_flag =True
                        print("webserver is writing=",parameter_name, new_dictinoary )
                        Write_Flag =True
                        found = True
                        break

                    elif(parameters_10sec["value"] != parameter_value and parameters_10sec["type"] != "bool"):
                        first_configuration_dict[parameter_name] = parameter_value
                        new_dictinoary={}
                        new_dictinoary[parameters_10sec['reg_num']]=parameter_value
                        json_writing_dictionary.update(new_dictinoary)
                        priority1_written_flag =True
                        print("webserver is writing=",parameter_name, new_dictinoary )
                        Write_Flag =True
                        found = True
                        break

        if(found == False):
            for parameters_5min in data_dictionary_Controller_To_Master_Priority_2["parameter"]:
                if(parameter_name != "created_on" and parameter_name != "modified_on"  and parameters_5min['reg_name'] == parameter_name  ):
                    if(parameters_5min['reg_name'] in Master_Controller_Utils.Master_write2_value_dic1.values()):
                        first_configuration_dict[parameter_name] = Master_Controller_Utils.Master_write_value_dic2[parameters_5min["reg_num"]]
                        if(first_configuration_dict[parameter_name] == 'True' or first_configuration_dict[parameter_name] == 'true'):
                            first_configuration_dict[parameter_name] = 'true'
                            found = True
                            break
                        elif(first_configuration_dict[parameter_name] == 'False' or first_configuration_dict[parameter_name] == 'false'):
                            first_configuration_dict[parameter_name] = 'false'
                            found = True
                            break
                    elif((parameters_5min["value"] == 'True' or parameters_5min["value"] == 'true') and (parameter_value == 'False' or parameter_value == 'false')):
                        first_configuration_dict[parameter_name] = 'false'
                        new_dictinoary={}
                        new_dictinoary[parameters_5min['reg_num']]='False'
                        json_writing_dictionary.update(new_dictinoary)
                        priority2_written_flag =True
                        print("webserver is writing=",parameter_name, new_dictinoary )
                        Write_Flag =True
                        found = True
                        break

                    elif((parameters_5min["value"] == 'False' or  parameters_5min["value"] == 'false') and (parameter_value == 'True' or parameter_value == 'true')):
                        first_configuration_dict[parameter_name] = 'true'
                        new_dictinoary={}
                        new_dictinoary[parameters_5min['reg_num']]='True'
                        json_writing_dictionary.update(new_dictinoary)
                        priority2_written_flag =True
                        print("webserver is writing=",parameter_name, new_dictinoary )
                        Write_Flag =True
                        found = True
                        break

                    elif(parameters_5min["value"] != parameter_value and parameters_5min["type"] != "bool"):
                        first_configuration_dict[parameter_name] = parameter_value
                        new_dictinoary={}
                        new_dictinoary[parameters_5min['reg_num']]=parameter_value
                        json_writing_dictionary.update(new_dictinoary)
                        priority2_written_flag =True
                        print("webserver is writing=",parameter_name, new_dictinoary )
                        Write_Flag =True
                        found = True
                        break

        if(found == False):
            for parameters_4hours in data_dictionary_Controller_To_Master_Priority_3["parameter"]:
                if(parameter_name != "created_on" and parameter_name != "modified_on"  and parameters_4hours['reg_name'] == parameter_name  ):
                    if(parameters_4hours['reg_name'] in Master_Controller_Utils.Master_write2_value_dic1.values()):
                        first_configuration_dict[parameter_name] = Master_Controller_Utils.Master_write_value_dic2[parameters_4hours["reg_num"]]
                        if(first_configuration_dict[parameter_name] == 'True' or first_configuration_dict[parameter_name] == 'true'):
                            first_configuration_dict[parameter_name] = 'true'
                            found = True
                            break
                        elif(first_configuration_dict[parameter_name] == 'False' or first_configuration_dict[parameter_name] == 'false'):
                            first_configuration_dict[parameter_name] = 'false'
                            found = True
                            break
                    elif((parameters_4hours["value"] == 'True' or parameters_4hours["value"] == 'true') and (parameter_value == 'False' or parameter_value == 'false')):
                        first_configuration_dict[parameter_name] = 'false'
                        new_dictinoary={}
                        new_dictinoary[parameters_4hours['reg_num']]='False'
                        json_writing_dictionary.update(new_dictinoary)
                        priority3_written_flag =True
                        print("webserver is writing=",parameter_name, new_dictinoary )
                        Write_Flag =True
                        found = True
                        break

                    elif((parameters_4hours["value"] == 'False' or  parameters_4hours["value"] == 'false') and (parameter_value == 'True' or parameter_value == 'true')):
                        first_configuration_dict[parameter_name] = 'true'
                        new_dictinoary={}
                        new_dictinoary[parameters_4hours['reg_num']]='True'
                        json_writing_dictionary.update(new_dictinoary)
                        priority3_written_flag =True
                        print("webserver is writing=",parameter_name, new_dictinoary )
                        Write_Flag =True
                        found = True
                        break

                    elif(parameters_4hours["value"] != parameter_value and parameters_4hours["type"] != "bool"):
                        first_configuration_dict[parameter_name] = parameter_value
                        new_dictinoary={}
                        new_dictinoary[parameters_4hours['reg_num']]=parameter_value
                        json_writing_dictionary.update(new_dictinoary)
                        priority3_written_flag =True
                        print("webserver is writing=",parameter_name, new_dictinoary )
                        Write_Flag =True
                        found = True
                        break

    if( priority1_written_flag == True ):
        data_dictionary_Master_To_Controller_Priority_1 = JSON_File_Read(JSON.MASTER_TO_CONTROLLER_PRIORITY_1) 
        for parameter in data_dictionary_Master_To_Controller_Priority_1["parameter"]:
            if(parameter["reg_name"] != "created_on" and parameter["reg_name"] != "modified_on"):
                if parameter["reg_num"] in json_writing_dictionary.keys():
                    parameter["value"]=json_writing_dictionary[parameter["reg_num"]]
                    new_dictinoary={}
                    new_dictinoary[parameter['reg_num']]=parameter['value']
                    Master_Controller_Utils.Master_write_value_dic1.update(new_dictinoary)
                    Master_Controller_Utils.Master_write1_value_dic1.update(new_dictinoary)
                    new_dictinoary[parameter['reg_num']]=0
                    Master_Controller_Utils.Master_write_count_dic1.update(new_dictinoary)
        JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_1 , data_dictionary_Master_To_Controller_Priority_1)  
    if( priority2_written_flag == True ):
        data_dictionary_Master_To_Controller_Priority_2 = JSON_File_Read(JSON.MASTER_TO_CONTROLLER_PRIORITY_2) 
        for parameter in data_dictionary_Master_To_Controller_Priority_2["parameter"]:
            if(parameter["reg_name"] != "created_on" and parameter["reg_name"] != "modified_on"):
                if parameter["reg_num"] in json_writing_dictionary.keys():
                    parameter["value"]=json_writing_dictionary[parameter["reg_num"]]
                    new_dictinoary={}
                    new_dictinoary[parameter['reg_num']]=parameter['value']
                    Master_Controller_Utils.Master_write_value_dic2.update(new_dictinoary)
                    Master_Controller_Utils.Master_write1_value_dic2.update(new_dictinoary)
                    new_dictinoary[parameter['reg_num']]=0
                    Master_Controller_Utils.Master_write_count_dic2.update(new_dictinoary)
        JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_2 , data_dictionary_Master_To_Controller_Priority_2)  
    if( priority3_written_flag == True ):
        data_dictionary_Master_To_Controller_Priority_3 = JSON_File_Read(JSON.MASTER_TO_CONTROLLER_PRIORITY_3) 
        for parameter in data_dictionary_Master_To_Controller_Priority_3["parameter"]:
            if(parameter["reg_name"] != "created_on" and parameter["reg_name"] != "modified_on"):
                if parameter["reg_num"] in json_writing_dictionary.keys():
                    parameter["value"]=json_writing_dictionary[parameter["reg_num"]]
                    new_dictinoary={}
                    new_dictinoary[parameter['reg_num']]=parameter['value']
                    Master_Controller_Utils.Master_write_value_dic3.update(new_dictinoary)
                    Master_Controller_Utils.Master_write1_value_dic3.update(new_dictinoary)
                    new_dictinoary[parameter['reg_num']]=0
                    Master_Controller_Utils.Master_write_count_dic3.update(new_dictinoary)
        JSON_File_Write(JSON.MASTER_TO_CONTROLLER_PRIORITY_3 , data_dictionary_Master_To_Controller_Priority_3) 
    try:
        first_configuration_dict.pop("created_by_name")
    except:
        pass
    try:
        first_configuration_dict.pop("created_by")
    except:
        pass
    JSON_File_Write(JSON.Read_Configuration , [first_configuration_dict])  


def Copy_controller_config():
    global ref_dictionary
    first_configuration_dict={}
    data_dictionary_Controller_To_Master_Priority_1 = JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_1) 
    data_dictionary_Controller_To_Master_Priority_2 = JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_2) 
    data_dictionary_Controller_To_Master_Priority_3 = JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_3) 
    CONFIGURATION_DICTIONARY = JSON_File_Read(JSON.Read_Configuration)
    JSON_File_Write(JSON.Write_Configuration, CONFIGURATION_DICTIONARY) 
    PREVIOUS_CONFIGURATION_DICTIONARY =CONFIGURATION_DICTIONARY[0] 
    first_configuration_dict=CONFIGURATION_DICTIONARY[0] 
    Write_Flag = False
    for parameter_name,parameter_value in PREVIOUS_CONFIGURATION_DICTIONARY.items():
        found = False
        if(found == False):
            for parameters_10sec in data_dictionary_Controller_To_Master_Priority_1["parameter"]:
                if(parameter_name != "created_on" and parameter_name != "modified_on"  and parameters_10sec['reg_name'] == parameter_name  ):
                    if((parameters_10sec["value"] == 'True' or parameters_10sec["value"] == 'true') and (parameter_value == 'False' and parameter_value == 'false')):
                        first_configuration_dict[parameter_name] = 'true'
                        Write_Flag =True
                        found = True
                        break
                    elif((parameters_10sec["value"] == 'False' or  parameters_10sec["value"] == 'false') and (parameter_value == 'True' and parameter_value == 'true')):
                        first_configuration_dict[parameter_name] = 'false'
                        Write_Flag =True
                        found = True
                        break
                    elif(parameters_10sec["value"] != parameter_value):
                        first_configuration_dict[parameter_name] = parameters_10sec["value"]
                        Write_Flag =True
                        found = True
                        break
        if(found == False):
            for parameters_5min in data_dictionary_Controller_To_Master_Priority_2["parameter"]:
                # print(parameters_5min["reg_name"])
                if(parameter_name != "created_on" and parameter_name != "modified_on"  and parameters_5min["reg_name"] == parameter_name  ):
                    if((parameters_5min["value"] == 'True' or parameters_5min["value"] == 'true') and (parameter_value == 'False' and parameter_value == 'false')):
                        first_configuration_dict[parameter_name] = 'true'
                        Write_Flag =True
                        found = True
                        break
                    elif((parameters_5min["value"] == 'False'  or parameters_5min["value"] == 'false') and (parameter_value == 'True' and parameter_value == 'true')):
                        first_configuration_dict[parameter_name] = 'false'
                        Write_Flag =True
                        found = True
                        break
                    elif(parameters_5min["value"] != parameter_value):
                        first_configuration_dict[parameter_name] = parameters_5min["value"]
                        Write_Flag =True
                        found = True
                        break

        if(found == False):
            for parameters_4hours in data_dictionary_Controller_To_Master_Priority_3["parameter"]:
                if(parameter_name != "created_on" and parameter_name != "modified_on"  and parameters_4hours["reg_name"] == parameter_name  ):
                    
                    if((parameters_4hours["value"] == 'True' or parameters_4hours["value"] == 'true') and (parameter_value == 'False' and parameter_value == 'false')):
                        first_configuration_dict[parameter_name] = 'true'
                        Write_Flag =True
                        found = True
                        break
                    elif((parameters_4hours["value"] == 'False' or parameters_4hours["value"] == 'false') and (parameter_value == 'True' and parameter_value == 'true')):
                        first_configuration_dict[parameter_name] = 'false'
                        Write_Flag =True
                        found = True
                        break
                    elif(parameters_5min["value"] != parameter_value):
                        first_configuration_dict[parameter_name] = parameters_4hours["value"] 
                        Write_Flag =True
                        found = True
                        break
    first_configuration_dict_1=[first_configuration_dict]
    try:
        first_configuration_dict_1.pop("created_by_name")
    except:
        pass
    try:
        first_configuration_dict_1.pop("created_by_id")
    except:
        pass
    if(Write_Flag == True):
        JSON_File_Write(JSON.Read_Configuration , first_configuration_dict_1)        
    return Write_Flag
   
    
def First_Configuration():
    global ref_dictionary
    first_configuration_dict={}
    data_dictionary_Controller_To_Master_Priority_1 = JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_1) 
    data_dictionary_Controller_To_Master_Priority_2 = JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_2) 
    data_dictionary_Controller_To_Master_Priority_3 = JSON_File_Read(JSON.CONTROLLER_TO_MASTER_PRIORITY_3) 
    CONFIGURATION_DICTIONARY = JSON_File_Read(JSON.Read_Configuration)
    for parameter_name,parameter_value in CONFIGURATION_DICTIONARY[0].items():
        for parameters_10sec in data_dictionary_Controller_To_Master_Priority_1["parameter"]:
            if(parameter_name != "created_on" and parameter_name != "modified_on"  and parameters_10sec['reg_name'] == parameter_name  ):
                if(parameters_10sec["value"] == 'True'):
                    first_configuration_dict[parameter_name] = 'true'
                elif(parameters_10sec["value"] == 'False'):
                    first_configuration_dict[parameter_name] = 'false'
                else:
                    first_configuration_dict[parameter_name] = parameters_10sec["value"]
            if(parameter_name == "created_on" or parameter_name == "modified_on" ):
                Time_value = datetime.now()
                time_value_variable = "TIMESTAMP"+"'"+str(Time_value.year)+"-"+str(Time_value.month)+"-"+str(Time_value.day)+"T"+str(Time_value.hour)+":"+str(Time_value.minute)+":"+str(Time_value.second)+"."+str(Time_value.microsecond)+"'"
                first_configuration_dict[parameter_name] = time_value_variable

        for parameters_5min in data_dictionary_Controller_To_Master_Priority_2["parameter"]:
            if(parameter_name != "created_on" and parameter_name != "modified_on"  and parameters_5min["reg_name"] == parameter_name  ):
                if(parameters_5min["value"] == 'True'):
                    first_configuration_dict[parameter_name] = 'true'
                elif(parameters_5min["value"] == 'False'):
                    first_configuration_dict[parameter_name] = 'false'
                else:
                    first_configuration_dict[parameter_name]= parameters_5min["value"]
            elif(parameter_name == "created_on" or parameter_name == "modified_on" ):
                Time_value = datetime.now()
                time_value_variable = "TIMESTAMP"+"'"+str(Time_value.year)+"-"+str(Time_value.month)+"-"+str(Time_value.day)+"T"+str(Time_value.hour)+":"+str(Time_value.minute)+":"+str(Time_value.second)+"."+str(Time_value.microsecond)+"'"
                parameter_value=time_value_variable
                first_configuration_dict[parameter_name]= parameter_value

            
        for parameters_4hours in data_dictionary_Controller_To_Master_Priority_3["parameter"]:
            if(parameter_name != "created_on" and parameter_name != "modified_on"  and parameters_4hours["reg_name"] == parameter_name  ):
                
                if(parameters_4hours["value"] == 'True'):
                    first_configuration_dict[parameter_name] = 'true'
                elif(parameters_4hours["value"] == 'False'):
                    first_configuration_dict[parameter_name] = 'false'
                else:
                    first_configuration_dict[parameter_name] = parameters_4hours["value"] 
            elif(parameter_name == "created_on" or parameter_name == "modified_on" ):
                Time_value = datetime.now()
                time_value_variable = "TIMESTAMP"+"'"+str(Time_value.year)+"-"+str(Time_value.month)+"-"+str(Time_value.day)+"T"+str(Time_value.hour)+":"+str(Time_value.minute)+":"+str(Time_value.second)+"."+str(Time_value.microsecond)+"'"
                parameter_value=time_value_variable
                first_configuration_dict[parameter_name] = parameter_value
    first_configuration_dict_1=[first_configuration_dict]
    try:
        first_configuration_dict_1.pop("created_by_name")
    except:
        pass
    try:
        first_configuration_dict_1.pop("created_by_id")
    except:
        pass
    JSON_File_Write(JSON.Read_Configuration , first_configuration_dict_1)        
    Configuration_from_server_written_flag = True

def CONNECT_TO_CONTROLLER(USB_COM = [],Conform = False):
    global Device_Address
    global USB0
    global USB0_Status_Flag #
    global USB0_COM #
    global client
    global USB1_Status_Flag #
    global USB1
    global USB1_COM #
    global master_usb
    global USB_CONTROLLER_CHECK
    controller_usb_found=False
    address=1
    global MASTER_USB_LIST
    global thread_list
    global new_dict
    global thread_count
    global list_dict_threads
    global thread_bool_list
    abc_list=[]
    new_dict_copy={}
    thread_list_5 = []
    thread_bool_list = []
    try:
        if(USB_COM == []):
            pts= prtlst.comports()
            for pt in pts:
                if 'USB' in pt[1]: #check 'USB' string in device description
                    USB_COM.append(pt[0])
        for USB in USB_COM:
            thread_bool_list.append(True)
            print("creating thread with usb=",USB)
            thread_list_5.append(Thread(target= controller_usb, args=(USB, (len(thread_bool_list)-1), Conform )).start())

        while(1):
            sleep(2)
            print("thread_bool_list",thread_bool_list)
            if( not True in thread_bool_list):
                # sleep(1)
                thread_bool_list.clear()
                break
            pass

    except Exception as e:
        print("USB Removed",USB,e)

def controller_usb(USB_F,index=0, Conform =False):
    global Device_Address
    global USB0
    global USB0_Status_Flag #
    global USB0_COM #
    global client
    global USB1_Status_Flag #
    global USB1
    global USB1_COM #
    global master_usb
    global USB_CONTROLLER_CHECK
    controller_usb_found=False
    address=1
    global MASTER_USB_LIST
    global thread_list
    global start_all_threads
    global thread_bool_list
    global Thread_Running_USB_list
    global list_dict_threads
    Extra_USB_COM=[]
    global all_set
    ret_flag=False

    if(controller_usb_found == True):
        thread_bool_list[index] = False
        return
    if ((not USB_F in MASTER_USB_LIST) and (Conform == False)):
        local_client = ModbusSerialClient(method='rtu', port=USB_F, baudrate=9600, timeout=0.1, parity='N', stopbits=1, bytesize=8)
        if local_client.connect()== True:
            if(Device_Address.value != 0):
                Response_status = local_client.read_holding_registers(address,count=1,unit=Device_Address.value)
                if(Response_status.isError() == False):
                    sleep(0.5)
                    if(read_65535_reg(USB_F,Device_Address.value,local_client) == True):
                        print("Controller USb is re=",USB_F)
                        ###################
                        try:
                            sleep(0.5)
                            local_client.close()
                            sleep(0.5)
                            client = ModbusSerialClient(method='rtu', port=USB_F, baudrate=9600, timeout=0.2, parity='N', stopbits=1, bytesize=8)
                            if client.connect()== True:
                              
                                Response_status = client.read_holding_registers(address,count=1,unit=Device_Address.value)
                                if(Response_status.isError() == False):
                                   
                                    sleep(0.5)
                                    
                                    if(read_65535_reg(USB_F,Device_Address.value,client) == True):
                                        print("conforming Controller USb is  re=",USB_F)
                                       
                                        start_all_threads = True
                                        USB0_COM=USB_F
                                        sleep(1)
                                        USB0_Status_Flag=True
                                        controller_usb_found=True
                                        client.timeout=0.08
                                       
                                        all_set=True
                                        thread_bool_list[index] = False
                                        return 
                                else:
                                    client.close()
                                    
                                    pts= prtlst.comports()
                                    for pt in pts:
                                        if 'USB' in pt[1]: #check 'USB' string in device description
                                            Extra_USB_COM.append(pt[0])
                                    for Usb in Extra_USB_COM:
                                        client = ModbusSerialClient(method='rtu', port=Usb, baudrate=9600, timeout=0.1, parity='N', stopbits=1, bytesize=8)
                                        Response_status = client.read_holding_registers(address,count=1,unit=Device_Address.value)
                                        if(Response_status.isError() == False):
                                            if(read_65535_reg(Usb,Device_Address.value,client) == True):
                                                print("conforming Controller USb is =",Usb)
                                                list_dict_threads.clear()
                                                USB0_COM=Usb
                                                USB0_Status_Flag=True
                                                controller_usb_found=True
                                                start_all_threads = True
                                                client.timeout=0.08
                                                
                                                all_set=True
                                                thread_bool_list[index] = False
                                                return 
                                        else:
                                            
                                            pass
                                    Device_Address.value = 0
                                    thread_list.clear()
                                    USB0_Status_Flag = False
                                    thread_bool_list=[]
                                    start_all_threads = False
                                    Thread_Running_USB_list =[]
                                    pass    
                           
                            pass
                        except Exception as e:
                            print("Exception occured--",e)
                        return 
                else:
                    local_client.close()
                    Device_Address.value = 0
                    thread_list.clear()
                    USB0_Status_Flag = False
                    thread_bool_list=[]
                    start_all_threads = False
                    Thread_Running_USB_list =[]
                    pass
            else:
                try:
                    for i in range(1,248):
                        sleep(0.1)
                        if(USB0_Status_Flag == False):
                            Response_status = local_client.read_holding_registers(address,count=1,unit=i)
                            if( ( Response_status.isError() == False) and (start_all_threads == False)):
                                
                                local_client.timeout=3
                                
                                ret_flag=read_65535_reg(USB_F,i,local_client)
                                if( ret_flag == True ):
                                    start_all_threads = True
                                    print("Controller USb is 121345 =",USB_F,index,"slave id=",i)
                                    
                                    try:
                                        local_client.close()
                                        sleep(0.5)
                                        client = ModbusSerialClient(method='rtu', port=USB_F, baudrate=9600, timeout=0.2, parity='N', stopbits=1, bytesize=8)
                                        if client.connect()== True:
                                            
                                            Response_status = client.read_holding_registers(address,count=1,unit=i)
                                            if(Response_status.isError() == False):
                                                
                                                sleep(0.5)
                                                
                                                if(read_65535_reg(USB_F,i,client) == True):
                                                    print("conforming Controller USb is  =",USB_F)
                                                    Device_Address.value=i
                                                    start_all_threads = True
                                                    USB0_COM=USB_F
                                                    sleep(1)
                                                    USB0_Status_Flag=True
                                                    controller_usb_found=True
                                                    client.timeout=0.08
                                                    
                                                    all_set=True
                                                    thread_bool_list[index] = False
                                                    return 
                                            else:
                                                client.close()
                                                
                                                pts= prtlst.comports()
                                                for pt in pts:
                                                    if 'USB' in pt[1]: #check 'USB' string in device description
                                                        Extra_USB_COM.append(pt[0])
                                                for Usb in Extra_USB_COM:
                                                    client = ModbusSerialClient(method='rtu', port=Usb, baudrate=9600, timeout=0.1, parity='N', stopbits=1, bytesize=8)
                                                    Response_status = client.read_holding_registers(address,count=1,unit=Device_Address.value)
                                                    if(Response_status.isError() == False):
                                                        if(read_65535_reg(Usb,Device_Address.value,client) == True):
                                                            print("conforming Controller USb is =",Usb)
                                                            list_dict_threads.clear()
                                                            USB0_COM=Usb
                                                            USB0_Status_Flag=True
                                                            controller_usb_found=True
                                                            start_all_threads = True
                                                            client.timeout=0.08
                                                            
                                                            all_set=True
                                                            thread_bool_list[index] = False
                                                            return 
                                                    else:
                                                        
                                                        pass
                                                Device_Address.value = 0
                                                thread_list.clear()
                                                USB0_Status_Flag = False
                                                thread_bool_list=[]
                                                start_all_threads = False
                                                Thread_Running_USB_list =[]
                                                pass    
                                        pass
                                    except Exception as e:
                                        print("Exception occured")
                                    Device_Address.value = i
                                    thread_bool_list[index] = False
                                    break 
                                else:
                                    print("one of the sem has slave address=",i)
                                    local_client.timeout=0.1
                                    start_all_threads = False
                                    thread_bool_list[index] = False
                                    local_client.close()
                                    return
                                    pass
                            elif(start_all_threads == True):
                                break
                            else :
                                print("Trying to connect ", USB_F , i)
                                pass
                        else:
                            local_client.close()
                            thread_bool_list[index] = False
                            break
                    thread_bool_list[index] = False
                except Exception as e:
                    print(" Controller usb removed ", e)
                    thread_bool_list[index] = False
            if(controller_usb_found == False):
                try:
                    for inde_x in range(len(list_dict_threads)):
                        if(list_dict_threads[inde_x]["thread_usb"] ==  USB_F ):
                            del list_dict_threads[inde_x]
                    pass
                except Exception as e:
                    pass
            sleep(0.01)
    else:
        pass
def read_65535_reg(Usb,slave_id,client_local):
    address=65535
    client_local.timeout = 0.1
    Response_status = client_local.read_coils(address,count=1,unit=slave_id)
    if(Response_status.isError() == False):                         
        return False
    else:
        return True
