from ast import NotIn
from logging import exception
import multiprocessing
from telnetlib import NOP
from numpy import False_
import time
from time import time as time_time
from time import sleep
from Master_Utils import *
# from datetime import datetime
from Master_Controller_Utils import *
from pymodbus.other_message import *
from time import time as TIME
  
def Master_Thread():
    sleep(0.1)
    USB_COM=[]
    m_process1=multiprocessing.Process(target=master_process_tcp_ip, args=(Master_Controller_Utils.Master_priority1_File_Read_Semaphore,
                                                                       Master_Controller_Utils.Master_priority2_File_Read_Semaphore,
                                                                       Master_Controller_Utils.Master_priority3_File_Read_Semaphore,
                                                                       Master_Controller_Utils.Master_priority4_File_Write_Semaphore,
                                                                       Master_Controller_Utils.Master_priority1_File_Write_Semaphore,
                                                                       Master_Controller_Utils.Master_priority2_File_Write_Semaphore,
                                                                       Master_Controller_Utils.Master_priority3_File_Write_Semaphore,
                                                                       Master_Controller_Utils.Master_priority4_File_Read_Semaphore,
                                                                       Master_Controller_Utils.Priority_1_backup_Semaphore,
                                                                       Master_Controller_Utils.Priority_2_backup_Semaphore,
                                                                       Master_Controller_Utils.Priority_3_backup_Semaphore,
                                                                       Master_Controller_Utils.Priority_4_backup_Semaphore,
                                                                       Master_Controller_Utils.Master_write2_value_dic1,
                                                                       Master_Controller_Utils.Master_write2_value_dic2,
                                                                       Master_Controller_Utils.Master_write2_value_dic3,
                                                                       Master_Controller_Utils.Master_write2_value_dic4,
                                                                       Master_Controller_Utils.Master_write1_value_dic1,
                                                                       Master_Controller_Utils.Master_write1_value_dic2,
                                                                       Master_Controller_Utils.Master_write1_value_dic3,
                                                                       Master_Controller_Utils.Master_write1_value_dic4,
                                                                       Master_Controller_Utils.Master_write_value_dic1, 
                                                                       Master_Controller_Utils.Master_write_value_dic2, 
                                                                       Master_Controller_Utils.Master_write_value_dic3, 
                                                                       Master_Controller_Utils.Master_write_value_dic4, 
                                                                       Master_Controller_Utils.Master_write_count_dic1, 
                                                                       Master_Controller_Utils.Master_write_count_dic2, 
                                                                       Master_Controller_Utils.Master_write_count_dic3, 
                                                                       Master_Controller_Utils.Master_write_count_dic4, 
                                                                       Master_Controller_Utils.USB1_Status_Flag,
                                                                       Master_Controller_Utils.USB1_COM,
                                                                       Master_Controller_Utils.all_p_num,
                                                                       Master_Controller_Utils.priority4_reg_list,
                                                                       Master_Controller_Utils.Device_Address,
                                                                       Master_Controller_Utils.Controller_to_master_FileName_Priority1,
                                                                       Master_Controller_Utils.Controller_to_master_FileName_Priority2,
                                                                       Master_Controller_Utils.Controller_to_master_FileName_Priority3,
                                                                       Master_Controller_Utils.Controller_to_master_FileName_Priority4,
                                                                       Master_Controller_Utils.Master_to_controller_FileName_Priority1,
                                                                       Master_Controller_Utils.Master_to_controller_FileName_Priority2,
                                                                       Master_Controller_Utils.Master_to_controller_FileName_Priority3,
                                                                       Master_Controller_Utils.Master_to_controller_FileName_Priority4,
                                                                       Master_Controller_Utils.Priority_1_backup,
                                                                       Master_Controller_Utils.Priority_2_backup,
                                                                       Master_Controller_Utils.Priority_3_backup,
                                                                       Master_Controller_Utils.Priority_4_backup,
        ))
    m_process1.start()

    THREAD_list=[]
    while 1:
        if Master_Controller_Utils.master_usb_check_list_flag== True:
            count = len(THREAD_list)
            backup_list = []
            latest_backup_list = []
            for proc in THREAD_list:
                backup_list.append(proc)
            pts= prtlst.comports()
            USB_COM.clear()
            for pt in pts:
                if 'USB' in pt[1]: #check 'USB' string in device description
                    USB_COM.append(pt[0])
            print("connected usb's=",USB_COM,"master_usb_check_list",Master_Controller_Utils.master_usb_check_list)
            for i in Master_Controller_Utils.master_usb_check_list:
                if i in USB_COM:
                    THREAD_list.append(Process(target=master_usb_detection_process_rtu, args=(Master_Controller_Utils.Master_priority1_File_Read_Semaphore,
                                                                                Master_Controller_Utils.Master_priority2_File_Read_Semaphore,
                                                                                Master_Controller_Utils.Master_priority3_File_Read_Semaphore,
                                                                                Master_Controller_Utils.Master_priority4_File_Write_Semaphore,
                                                                                Master_Controller_Utils.Master_priority1_File_Write_Semaphore,
                                                                                Master_Controller_Utils.Master_priority2_File_Write_Semaphore,
                                                                                Master_Controller_Utils.Master_priority3_File_Write_Semaphore,
                                                                                Master_Controller_Utils.Master_priority4_File_Read_Semaphore,
                                                                                Master_Controller_Utils.Priority_1_backup_Semaphore,
                                                                                Master_Controller_Utils.Priority_2_backup_Semaphore,
                                                                                Master_Controller_Utils.Priority_3_backup_Semaphore,
                                                                                Master_Controller_Utils.Priority_4_backup_Semaphore,
                                                                                Master_Controller_Utils.Master_write2_value_dic1,
                                                                                Master_Controller_Utils.Master_write2_value_dic2,
                                                                                Master_Controller_Utils.Master_write2_value_dic3,
                                                                                Master_Controller_Utils.Master_write2_value_dic4,
                                                                                Master_Controller_Utils.Master_write1_value_dic1,
                                                                                Master_Controller_Utils.Master_write1_value_dic2,
                                                                                Master_Controller_Utils.Master_write1_value_dic3,
                                                                                Master_Controller_Utils.Master_write1_value_dic4,
                                                                                Master_Controller_Utils.Master_write_value_dic1, 
                                                                                Master_Controller_Utils.Master_write_value_dic2, 
                                                                                Master_Controller_Utils.Master_write_value_dic3, 
                                                                                Master_Controller_Utils.Master_write_value_dic4, 
                                                                                Master_Controller_Utils.Master_write_count_dic1, 
                                                                                Master_Controller_Utils.Master_write_count_dic2, 
                                                                                Master_Controller_Utils.Master_write_count_dic3, 
                                                                                Master_Controller_Utils.Master_write_count_dic4, 
                                                                                Master_Controller_Utils.USB1_Status_Flag,
                                                                                Master_Controller_Utils.USB1_COM,
                                                                                Master_Controller_Utils.all_p_num,
                                                                                Master_Controller_Utils.priority4_reg_list,
                                                                                Master_Controller_Utils.Device_Address,
                                                                                Master_Controller_Utils.Controller_to_master_FileName_Priority1,
                                                                                Master_Controller_Utils.Controller_to_master_FileName_Priority2,
                                                                                Master_Controller_Utils.Controller_to_master_FileName_Priority3,
                                                                                Master_Controller_Utils.Controller_to_master_FileName_Priority4,
                                                                                Master_Controller_Utils.Master_to_controller_FileName_Priority1,
                                                                                Master_Controller_Utils.Master_to_controller_FileName_Priority2,
                                                                                Master_Controller_Utils.Master_to_controller_FileName_Priority3,
                                                                                Master_Controller_Utils.Master_to_controller_FileName_Priority4,
                                                                                Master_Controller_Utils.Priority_1_backup,
                                                                                Master_Controller_Utils.Priority_2_backup,
                                                                                Master_Controller_Utils.Priority_3_backup,
                                                                                Master_Controller_Utils.Priority_4_backup,
                                                                                Master_Controller_Utils.master_usb_check_flag,
                                                                                Master_Controller_Utils.master_usb,
                                                                                i,
                                                                                Master_Controller_Utils.MASTER_USB_LIST,
                                                                                Master_Controller_Utils.Master_search_count,
                    )))
            
            for thread in THREAD_list:
                if(not thread in backup_list):
                    latest_backup_list.append(thread)
                if(count==0):
                    thread.start()
                else:
                    count-=1
            while(THREAD_list != [] or latest_backup_list != []):
                if(latest_backup_list==[]):
                    break
                if(Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == True):
                    break
                else:
                    flag = False
                    # flag1 = False
                    counter = 0
                    while(flag==False):   
                        
                        counter=0
                        for proc in THREAD_list:
                            counter+=1
                            if(proc.is_alive() == False):
                                THREAD_list.remove(proc)
                                if(proc in latest_backup_list):
                                    latest_backup_list.remove(proc)
                                flag = False
                                # flag1 = True
                                # print("hi")
                                break
                            else:
                                pass
                                flag=True
                        if(counter==0):
                            flag=True

            Master_Controller_Utils.master_usb_check_list_flag = False
        for proc in THREAD_list:
            if(proc.is_alive() == False):
                THREAD_list.remove(proc)
                break
            else:
                pass
            
if __name__ == "__main__":
    Master_Thread()   