import time
from time import sleep 
# import time
from time import time as TIME
from turtle import clear
from Master_Utils import *
import serial.tools.list_ports as prtlst
from Controller_Utils import *

#######################################################
#  comparing two json files and write the new value   #
#   to xr75 and and read all the xr75 parameters      #
#                                                     #
#######################################################
def Controller_Thread():
    time_end= int(round(TIME()*1000))
    time_start= int(round(TIME()*1000))
    priority_4_count=0
    while 1:
        try:
            if(Master_Controller_Utils.USB0_Status_Flag == True):
                print("full read JSON time = ",time_end-time_start)
                time_start= int(round(TIME()*1000))
                ################################################################    
                #   Reading all the parameters with their priority
                ################################################################
                ################################################################
                # Priority 1 Controller handling
                ################################################################
                if(Master_Controller_Utils.Written_dict_priority1==False):
                    Master_Controller_Utils.Write_dict_priority1 = []
                if(Master_Controller_Utils.Written_dict_priority2==False):
                    Master_Controller_Utils.Write_dict_priority2 = []
                if(Master_Controller_Utils.Written_dict_priority3==False):
                    Master_Controller_Utils.Write_dict_priority3 = []
                if(Master_Controller_Utils.Written_dict_priority4==False):
                    Master_Controller_Utils.Write_dict_priority4 = []
                sleep(0.1)
                Check_and_write_Controller_data()
                try:
                    if Master_Controller_Utils.Read_from_controller_Flag ==  True:
                        data_dictionary_Controller_to_Master_Priority1 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_1)
                        Master_Controller_Utils.write_list = []
                        JSON_data_dictionary = Read_Controller_data(data_dictionary_Controller_to_Master_Priority1,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1)
                        if(JSON_data_dictionary != []):
                            Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_1, JSON_data_dictionary)
                            for address in Master_Controller_Utils.write_list:
                                if(address in Master_Controller_Utils.Master_write1_value_dic1.keys()):
                                    Master_Controller_Utils.Master_write1_value_dic1.pop(address)
                                if(address in Master_Controller_Utils.Master_write2_value_dic1.keys()):
                                    Master_Controller_Utils.Master_write2_value_dic1.pop(address)

                            if(len(Master_Controller_Utils.Master_write_value_dic1) == 0):
                                Master_Controller_Utils.REF_DICT_PRIORITY_1=JSON_data_dictionary
                                Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1, JSON_data_dictionary, json_flag_set = False)
                        ReRead_controller()   
                except:
                    print("JSON_corrupted")
                    pass
                else:
                    pass
                ################################################################
                # Priority 2 Controller handling
                ###############################################################
                if(Master_Controller_Utils.Written_dict_priority1==False):
                    Master_Controller_Utils.Write_dict_priority1 = []
                if(Master_Controller_Utils.Written_dict_priority2==False):
                    Master_Controller_Utils.Write_dict_priority2 = []
                if(Master_Controller_Utils.Written_dict_priority3==False):
                    Master_Controller_Utils.Write_dict_priority3 = []
                if(Master_Controller_Utils.Written_dict_priority4==False):
                    Master_Controller_Utils.Write_dict_priority4 = []
                sleep(0.1)
                Check_and_write_Controller_data()
                try:
                    if Master_Controller_Utils.Read_from_controller_Flag == True:
                        data_dictionary_Controller_to_Master_Priority2 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_2)
                        Master_Controller_Utils.write_list = []
                        JSON_data_dictionary = Read_Controller_data(data_dictionary_Controller_to_Master_Priority2,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2)
                        if(JSON_data_dictionary != []):
                            Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_2, JSON_data_dictionary) 
                            for address in Master_Controller_Utils.write_list:
                                if(address in Master_Controller_Utils.Master_write1_value_dic2.keys()):
                                    Master_Controller_Utils.Master_write1_value_dic2.pop(address)
                                if(address in Master_Controller_Utils.Master_write2_value_dic1.keys()):
                                    Master_Controller_Utils.Master_write2_value_dic1.pop(address)
                            
                            if(len(Master_Controller_Utils.Master_write_value_dic2) == 0):
                                Master_Controller_Utils.REF_DICT_PRIORITY_2=JSON_data_dictionary
                                Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2, JSON_data_dictionary, json_flag_set = False)  
                        ReRead_controller()    
                except:
                    print("JSON_corrupted")

                ################################################################
                # Priority 3 Controller handling
                ################################################################
                if(Master_Controller_Utils.Written_dict_priority1==False):
                    Master_Controller_Utils.Write_dict_priority1 = []
                if(Master_Controller_Utils.Written_dict_priority2==False):
                    Master_Controller_Utils.Write_dict_priority2 = []
                if(Master_Controller_Utils.Written_dict_priority3==False):
                    Master_Controller_Utils.Write_dict_priority3 = []
                if(Master_Controller_Utils.Written_dict_priority4==False):
                    Master_Controller_Utils.Write_dict_priority4 = []
                sleep(0.1)
                Check_and_write_Controller_data()
                try:
                    if Master_Controller_Utils.Read_from_controller_Flag == True:
                        data_dictionary_Controller_to_Master_Priority3 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_3)
                        Master_Controller_Utils.write_list = []
                        JSON_data_dictionary = Read_Controller_data(data_dictionary_Controller_to_Master_Priority3,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3)
                        if(JSON_data_dictionary != []):
                            Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_3, JSON_data_dictionary)   
                            for address in Master_Controller_Utils.write_list:
                                if(address in Master_Controller_Utils.Master_write1_value_dic3.keys()):
                                    Master_Controller_Utils.Master_write1_value_dic3.pop(address)
                                if(address in Master_Controller_Utils.Master_write2_value_dic1.keys()):
                                    Master_Controller_Utils.Master_write2_value_dic1.pop(address)
                            
                            if(len(Master_Controller_Utils.Master_write_value_dic3) == 0):
                                Master_Controller_Utils.REF_DICT_PRIORITY_3=JSON_data_dictionary
                                Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3, JSON_data_dictionary, json_flag_set = False) 
                                
                        ReRead_controller()

                except:
                    print("JSON_corrupted")

                ################################################################
                # Priority 4 Controller handling(non present parameters)
                ##################################################################
                if(Master_Controller_Utils.Written_dict_priority1==False):
                    Master_Controller_Utils.Write_dict_priority1 = []
                if(Master_Controller_Utils.Written_dict_priority2==False):
                    Master_Controller_Utils.Write_dict_priority2 = []
                if(Master_Controller_Utils.Written_dict_priority3==False):
                    Master_Controller_Utils.Write_dict_priority3 = []
                if(Master_Controller_Utils.Written_dict_priority4==False):
                    Master_Controller_Utils.Write_dict_priority4 = []
                
                Check_and_write_Controller_data()
                priority_4_count+=1
                if (priority_4_count >= 1):
                    priority_4_count=0
                    try:
                        if (Master_Controller_Utils.Read_from_controller_Flag == True and Master_Controller_Utils.Controller_extra_parameter_Flag == True):
                            data_dictionary_Controller_to_Master_Priority4 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_4)
                            Master_Controller_Utils.write_list = []
                            JSON_data_dictionary = Read_Controller_data(data_dictionary_Controller_to_Master_Priority4,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4)
                            try:
                                if(Master_Controller_Utils.number_of_extra_parmeter != len(JSON_data_dictionary["parameter"])):
                                    Master_Controller_Utils.read_list_dic_priority4, JSON_data_dictionary=Master_Controller_Utils.Json_file_sorting(Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_4))
                                    Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_4, JSON_data_dictionary)
                                    Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4, JSON_data_dictionary)
                                    Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.PRIORITY_4, JSON_data_dictionary)
                                    Master_Controller_Utils.number_of_extra_parmeter = len(JSON_data_dictionary["parameter"])
                            except Exception as e:
                                print("error sorting for the new parameter",e)
                            if(JSON_data_dictionary != []):
                                Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_4, JSON_data_dictionary)
                                for address in Master_Controller_Utils.write_list:
                                    if(address in Master_Controller_Utils.Master_write1_value_dic4.keys()):
                                        Master_Controller_Utils.Master_write1_value_dic4.pop(address)
                                    if(address in Master_Controller_Utils.Master_write2_value_dic1.keys()):
                                        Master_Controller_Utils.Master_write2_value_dic1.pop(address)
                                
                                if(len(Master_Controller_Utils.Master_write_value_dic4) == 0):
                                    Master_Controller_Utils.REF_DICT_PRIORITY_4=JSON_data_dictionary
                                    Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4, JSON_data_dictionary, json_flag_set = False) 
                                    
                            ReRead_controller()
                    except:
                        print("JSON_corrupted")
                Master_Controller_Utils.Controller_one_time_read=True
                time_end= int(round(TIME()*1000))
            else:
                sleep(0.1)
        except Exception as  a:
            print("-----------------------------------------read_controller",a)    
if __name__ == "__main__":
    Master_Controller_Utils.init()
    Controller_Thread()