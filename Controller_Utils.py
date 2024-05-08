from curses.ascii import isblank
from enum import Flag
import re
import time
from time import sleep
from threading import *
from Master_Controller_Utils import *
import Master_Controller_Utils
from pymodbus.payload import BinaryPayloadBuilder, Endian, BinaryPayloadDecoder
from datetime import datetime

def Write_Controller_data(Master_data_dictionary,Controller_data_dictionary,Ref_Master_data_dictionary,JSON_Priority):
    flag=True
    Priority_1_flag= False
    Priority_2_flag= False
    Priority_3_flag= False
    Priority_4_flag= False
    try:
        if(Master_Controller_Utils.USB0_Status_Flag == True):
            for Master_parameters,Controller_parameters in zip(Master_data_dictionary["parameter"],Controller_data_dictionary["parameter"]):
                if(Master_Controller_Utils.USB0_Status_Flag == True ):
                    if(Master_parameters["reg_name"] != "created_on" and Master_parameters["reg_name"] != "modified_on"):
                        if( Master_parameters["reg_num"] == Controller_parameters["reg_num"] and Master_parameters["reg_name"] == Controller_parameters["reg_name"] and Master_parameters["type"] == Controller_parameters["type"]):
                            if(((Master_parameters["reg_num"] in Master_Controller_Utils.Master_write_value_dic1.keys())) or ((Master_parameters["reg_num"] in Master_Controller_Utils.Master_write_value_dic2.keys())) or ((Master_parameters["reg_num"] in Master_Controller_Utils.Master_write_value_dic3.keys())) or ((Master_parameters["reg_num"] in Master_Controller_Utils.Master_write_value_dic4.keys()))):
                                sleep(0.001)
                                try:
                                    if(Controller_parameters["type"] == "bool" or Controller_parameters["type"] == "Bool"):
                                        if(Master_Controller_Utils.client.is_socket_open() == False): 
                                            Master_Controller_Utils.client.connect()
                                        if(Master_Controller_Utils.client.is_socket_open() == True):
                                            address = Master_parameters["reg_num"]
                                            if(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1):
                                                Master_parameters["value"] = Master_Controller_Utils.Master_write_value_dic1[Master_parameters["reg_num"]]
                                            elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2):
                                                Master_parameters["value"] = Master_Controller_Utils.Master_write_value_dic2[Master_parameters["reg_num"]]
                                            elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3):
                                                Master_parameters["value"] = Master_Controller_Utils.Master_write_value_dic3[Master_parameters["reg_num"]]
                                            elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4):
                                                Master_parameters["value"] = Master_Controller_Utils.Master_write_value_dic4[Master_parameters["reg_num"]]
                                            if(Master_parameters["value"] == 'True' or Master_parameters["value"] == 'true'):
                                                value = True
                                            elif(Master_parameters["value"] == 'False' or Master_parameters["value"] == 'false'):
                                                value = False   
                                            try:
                                                Response_status = Master_Controller_Utils.client.write_coil(address,value,unit=Master_Controller_Utils.Device_Address.value)
                                                if(Response_status.isError() == False):
                                                    # print("written value is =",address,"value=",Master_parameters["value"])
                                                    if(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1):
                                                        if(Master_Controller_Utils.Master_write_value_dic1[address] == Master_parameters["value"]):
                                                            Master_Controller_Utils.Master_write_value_dic1.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic1.pop(address)
                                                            # print("poped value is =",address,"value=",Master_parameters["value"])
                                                        if(address not in Master_Controller_Utils.Write_dict_priority1):
                                                            Master_Controller_Utils.Write_dict_priority1.append(address)
                                                            Master_Controller_Utils.Written_dict_priority1 = True
                                                        Priority_1_flag = True
                                                    elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2):
                                                        if(Master_Controller_Utils.Master_write_value_dic2[address] == Master_parameters["value"]):
                                                            Master_Controller_Utils.Master_write_value_dic2.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic2.pop(address)
                                                            # print("poped value is =",address,"value=",Master_parameters["value"])
                                                        if(address not in Master_Controller_Utils.Write_dict_priority2):
                                                            Master_Controller_Utils.Write_dict_priority2.append(address)
                                                            Master_Controller_Utils.Written_dict_priority2 = True
                                                        Priority_2_flag = True
                                                    elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3):
                                                        if(Master_Controller_Utils.Master_write_value_dic3[address] == Master_parameters["value"]):
                                                            Master_Controller_Utils.Master_write_value_dic3.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic3.pop(address)
                                                            # print("poped value is =",address,"value=",Master_parameters["value"])
                                                        if(address not in Master_Controller_Utils.Write_dict_priority3):
                                                            Master_Controller_Utils.Write_dict_priority3.append(address)
                                                            Master_Controller_Utils.Written_dict_priority3 = True
                                                        Priority_3_flag = True
                                                    elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4):
                                                        if(Master_Controller_Utils.Master_write_value_dic4[address] == Master_parameters["value"]):
                                                            Master_Controller_Utils.Master_write_value_dic4.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic4.pop(address)
                                                            # print("poped value is =",address,"value=",Master_parameters["value"])
                                                        if(address not in Master_Controller_Utils.Write_dict_priority4):
                                                            Master_Controller_Utils.Write_dict_priority4.append(address)
                                                            Master_Controller_Utils.Written_dict_priority4 = True
                                                        Priority_4_flag = True
                                                    else:
                                                        pass 
                                                    print("sucessfull writing",address, Master_parameters["value"])
                                                    Master_parameters["value"] == Controller_parameters["value"]  
                                                    pass
                                                elif(Response_status.isError() == True):
                                                    if ((Response_status.function_code & 0x80 ) == 0x80):
                                                        print('write_coil exception code',Response_status.exception_code)
                                                    if(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1):
                                                        Master_Controller_Utils.Master_write_count_dic1[address]+=1
                                                        if(Master_Controller_Utils.Master_write_count_dic1[address] >= 2):
                                                            Master_Controller_Utils.Master_write_value_dic1.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic1.pop(address)
                                                            Master_parameters["value"] == Controller_parameters["value"] 
                                                            Priority_1_flag = True
                                                            if(address not in Master_Controller_Utils.Write_dict_priority1):
                                                                Master_Controller_Utils.Write_dict_priority1.append(address)
                                                                Master_Controller_Utils.Written_dict_priority1 = True 
                                                    elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2):
                                                        Master_Controller_Utils.Master_write_count_dic2[address]+=1
                                                        if(Master_Controller_Utils.Master_write_count_dic2[address] >= 2):
                                                            Master_Controller_Utils.Master_write_value_dic2.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic2.pop(address)
                                                            Master_parameters["value"] == Controller_parameters["value"]
                                                            if(address not in Master_Controller_Utils.Write_dict_priority2):
                                                                Master_Controller_Utils.Write_dict_priority2.append(address)
                                                                Master_Controller_Utils.Written_dict_priority2 = True 
                                                            Priority_2_flag = True
                                                    elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3):
                                                        Master_Controller_Utils.Master_write_count_dic3[address]+=1
                                                        if(Master_Controller_Utils.Master_write_count_dic3[address] >= 2):
                                                            Master_Controller_Utils.Master_write_value_dic3.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic3.pop(address)
                                                            Master_parameters["value"] == Controller_parameters["value"] 
                                                            Priority_3_flag = True
                                                            if(address not in Master_Controller_Utils.Write_dict_priority3):
                                                                Master_Controller_Utils.Write_dict_priority3.append(address)
                                                                Master_Controller_Utils.Written_dict_priority3 = True 
                                                    elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4):
                                                        Master_Controller_Utils.Master_write_count_dic4[address]+=1
                                                        if(Master_Controller_Utils.Master_write_count_dic4[address] >= 2):
                                                            Master_Controller_Utils.Master_write_value_dic4.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic4.pop(address)
                                                            Master_parameters["value"] == Controller_parameters["value"] 
                                                            Priority_4_flag = True
                                                            if(address not in Master_Controller_Utils.Write_dict_priority4):
                                                                Master_Controller_Utils.Write_dict_priority4.append(address)
                                                                Master_Controller_Utils.Written_dict_priority4 = True 
                                                    else:
                                                        pass
                                                    print("Failed writing",address, Master_parameters["value"])
                                                    flag=False
                                            except:
                                                pass
                                                print("Controller is not responding to write")
                                        else:
                                            pass
                                    else:
                                        if(Master_Controller_Utils.client.is_socket_open() == False): 
                                            Master_Controller_Utils.client.connect()
                                        if(Master_Controller_Utils.client.is_socket_open() == True):
                                            address = Master_parameters["reg_num"]
                                            value = Master_parameters["value"]
                                            if(Master_parameters["type"] == "integer"):
                                                builder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                                                builder.reset()
                                                if(Master_parameters["reg_num"] in Master_Controller_Utils.Master_write_value_dic1.keys()):
                                                    builder.add_16bit_int(int((Master_Controller_Utils.Master_write_value_dic1[Master_parameters["reg_num"]]-Master_parameters["offset"]) / Master_parameters["factor"]))
                                                    Master_parameters["value"] = Master_Controller_Utils.Master_write_value_dic1[Master_parameters["reg_num"]]
                                                    payload = builder.to_registers()
                                                elif(Master_parameters["reg_num"] in Master_Controller_Utils.Master_write_value_dic2.keys()):
                                                    builder.add_16bit_int(int((Master_Controller_Utils.Master_write_value_dic2[Master_parameters["reg_num"]]-Master_parameters["offset"]) / Master_parameters["factor"]))
                                                    Master_parameters["value"] = Master_Controller_Utils.Master_write_value_dic2[Master_parameters["reg_num"]]
                                                    payload = builder.to_registers()
                                                elif(Master_parameters["reg_num"] in Master_Controller_Utils.Master_write_value_dic3.keys()):
                                                    builder.add_16bit_int(int((Master_Controller_Utils.Master_write_value_dic3[Master_parameters["reg_num"]]-Master_parameters["offset"]) / Master_parameters["factor"]))
                                                    Master_parameters["value"] = Master_Controller_Utils.Master_write_value_dic3[Master_parameters["reg_num"]]
                                                    payload = builder.to_registers()
                                                elif(Master_parameters["reg_num"] in Master_Controller_Utils.Master_write_value_dic4.keys()):
                                                    builder.add_16bit_int(int((Master_Controller_Utils.Master_write_value_dic4[Master_parameters["reg_num"]]-Master_parameters["offset"]) / Master_parameters["factor"]))
                                                    Master_parameters["value"] = Master_Controller_Utils.Master_write_value_dic4[Master_parameters["reg_num"]]
                                                    payload = builder.to_registers()
                                                else:
                                                    continue
                                            elif(Master_parameters["type"] == "float"):
                                                builder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                                                builder.reset()
                                                if(Master_parameters["reg_num"] in Master_Controller_Utils.Master_write_value_dic1.keys()):
                                                    builder.add_16bit_float(int((Master_Controller_Utils.Master_write_value_dic1[Master_parameters["reg_num"]]-Master_parameters["offset"]) / Master_parameters["factor"]))
                                                    Master_parameters["value"] = Master_Controller_Utils.Master_write_value_dic1[Master_parameters["reg_num"]]
                                                    payload = builder.to_registers()
                                                elif(Master_parameters["reg_num"] in Master_Controller_Utils.Master_write_value_dic2.keys()):
                                                    builder.add_16bit_float(int((Master_Controller_Utils.Master_write_value_dic2[Master_parameters["reg_num"]]-Master_parameters["offset"]) / Master_parameters["factor"]))
                                                    Master_parameters["value"] = Master_Controller_Utils.Master_write_value_dic2[Master_parameters["reg_num"]]
                                                    payload = builder.to_registers()
                                                elif(Master_parameters["reg_num"] in Master_Controller_Utils.Master_write_value_dic3.keys()):
                                                    builder.add_16bit_float(int((Master_Controller_Utils.Master_write_value_dic3[Master_parameters["reg_num"]]-Master_parameters["offset"]) / Master_parameters["factor"]))
                                                    Master_parameters["value"] = Master_Controller_Utils.Master_write_value_dic3[Master_parameters["reg_num"]]
                                                    payload = builder.to_registers()
                                                elif(Master_parameters["reg_num"] in Master_Controller_Utils.Master_write_value_dic4.keys()):
                                                    builder.add_16bit_float(int((Master_Controller_Utils.Master_write_value_dic4[Master_parameters["reg_num"]]-Master_parameters["offset"]) / Master_parameters["factor"]))
                                                    Master_parameters["value"] = Master_Controller_Utils.Master_write_value_dic4[Master_parameters["reg_num"]]
                                                    payload = builder.to_registers()
                                                else:
                                                    continue
                                            try:
                                                Response_status = Master_Controller_Utils.client.write_register(address,payload[0],unit=Master_Controller_Utils.Device_Address.value)
                                                if(Response_status.isError() == False):
                                                    # print("written value is =",address,"value=",Master_parameters["value"],Master_Controller_Utils.Master_write_value_dic4[address])
                                                    if(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1):
                                                        if(Master_Controller_Utils.Master_write_value_dic1[address] == Master_parameters["value"]):
                                                            Master_Controller_Utils.Master_write_value_dic1.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic1.pop(address)
                                                            # print("poped value is =",address,"value=",Master_parameters["value"])
                                                        if(address not in Master_Controller_Utils.Write_dict_priority1):
                                                            Master_Controller_Utils.Write_dict_priority1.append(address)
                                                            Master_Controller_Utils.Written_dict_priority1 = True
                                                        Priority_1_flag = True
                                                    elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2):
                                                        if(Master_Controller_Utils.Master_write_value_dic2[address] == Master_parameters["value"]):
                                                            Master_Controller_Utils.Master_write_value_dic2.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic2.pop(address)
                                                            # print("poped value is =",address,"value=",Master_parameters["value"])
                                                        if(address not in Master_Controller_Utils.Write_dict_priority2):
                                                            Master_Controller_Utils.Write_dict_priority2.append(address)
                                                            Master_Controller_Utils.Written_dict_priority2 = True
                                                        Priority_2_flag = True
                                                    elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3):
                                                        if(Master_Controller_Utils.Master_write_value_dic3[address] == Master_parameters["value"]):
                                                            Master_Controller_Utils.Master_write_value_dic3.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic3.pop(address)
                                                            # print("poped value is =",address,"value=",Master_parameters["value"])
                                                        if(address not in Master_Controller_Utils.Write_dict_priority3):
                                                            Master_Controller_Utils.Write_dict_priority3.append(address)
                                                            Master_Controller_Utils.Written_dict_priority3 = True
                                                        Priority_3_flag = True
                                                    elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4):
                                                        if(Master_Controller_Utils.Master_write_value_dic4[address] == Master_parameters["value"]):
                                                            Master_Controller_Utils.Master_write_value_dic4.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic4.pop(address)
                                                            # print("poped value is =",address,"value=",Master_parameters["value"])
                                                        if(address not in Master_Controller_Utils.Write_dict_priority4):
                                                            Master_Controller_Utils.Write_dict_priority4.append(address)
                                                            Master_Controller_Utils.Written_dict_priority4 = True
                                                        Priority_4_flag = True
                                                    else:
                                                        pass 
                                                    print("Sucessfull writing",address, Master_parameters["value"])
                                                    Master_parameters["value"] == Controller_parameters["value"]
                                                elif(Response_status.isError() == True):
                                                    if ((Response_status.function_code & 0x80 ) == 0x80):
                                                        print('write_register exception code',Response_status.exception_code)
                                                    if(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1):
                                                        Master_Controller_Utils.Master_write_count_dic1[address]+=1
                                                        if(Master_Controller_Utils.Master_write_count_dic1[address] >= 2):
                                                            Master_Controller_Utils.Master_write_value_dic1.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic1.pop(address)
                                                            Master_parameters["value"] == Controller_parameters["value"] 
                                                            Priority_1_flag = True
                                                            if(address not in Master_Controller_Utils.Write_dict_priority1):
                                                                Master_Controller_Utils.Write_dict_priority1.append(address)
                                                                Master_Controller_Utils.Written_dict_priority2 = True 
                                                    elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2):
                                                        Master_Controller_Utils.Master_write_count_dic2[address]+=1
                                                        if(Master_Controller_Utils.Master_write_count_dic2[address] >= 2):
                                                            Master_Controller_Utils.Master_write_value_dic2.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic2.pop(address)
                                                            Master_parameters["value"] == Controller_parameters["value"]
                                                            if(address not in Master_Controller_Utils.Write_dict_priority2):
                                                                Master_Controller_Utils.Write_dict_priority2.append(address)
                                                                Master_Controller_Utils.Written_dict_priority2 = True 
                                                            Priority_2_flag = True
                                                    elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3):
                                                        Master_Controller_Utils.Master_write_count_dic3[address]+=1
                                                        if(Master_Controller_Utils.Master_write_count_dic3[address] >= 2):
                                                            Master_Controller_Utils.Master_write_value_dic3.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic3.pop(address)
                                                            Master_parameters["value"] == Controller_parameters["value"] 
                                                            Priority_3_flag = True
                                                            if(address not in Master_Controller_Utils.Write_dict_priority3):
                                                                Master_Controller_Utils.Write_dict_priority3.append(address)
                                                                Master_Controller_Utils.Written_dict_priority3 = True 
                                                    elif(JSON_Priority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4):
                                                        Master_Controller_Utils.Master_write_count_dic4[address]+=1
                                                        if(Master_Controller_Utils.Master_write_count_dic4[address] >= 2):
                                                            Master_Controller_Utils.Master_write_value_dic4.pop(address)
                                                            Master_Controller_Utils.Master_write_count_dic4.pop(address)
                                                            Master_parameters["value"] == Controller_parameters["value"] 
                                                            Priority_4_flag = True
                                                            if(address not in Master_Controller_Utils.Write_dict_priority4):
                                                                Master_Controller_Utils.Write_dict_priority4.append(address)
                                                                Master_Controller_Utils.Written_dict_priority4 = True 
                                                    else:
                                                        pass
                                                    print("Fail writing",address, Master_parameters["value"])
                                                    flag=False
                                            except:
                                                pass
                                                print("Controller is not responding to write")
                                        else:
                                            pass
                                except:
                                    print("exception is client write code")
        if(Priority_1_flag== True):
            Master_Controller_Utils.REF_DICT_PRIORITY_1= Master_data_dictionary
            Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1, Master_data_dictionary)        
        if(Priority_2_flag== True):
            Master_Controller_Utils.REF_DICT_PRIORITY_2= Master_data_dictionary
            Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2, Master_data_dictionary)        
            Master_Controller_Utils.Master_written_JSON_Priority2_Flag = True
        if(Priority_3_flag== True):
            Master_Controller_Utils.REF_DICT_PRIORITY_3= Master_data_dictionary
            Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3, Master_data_dictionary)        
        if(Priority_4_flag== True):
            Master_Controller_Utils.REF_DICT_PRIORITY_4= Master_data_dictionary
            Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4, Master_data_dictionary)                 
        return flag
    except:
        print("JSON_corrupted")
        return False

def Read_Controller_data(JSON_data_dictionary, Prority):
    count = 0
    k =''
    Read_list =[]
    list_index = 0
    list_read = True
    if(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1):
        Read_list = Master_Controller_Utils.read_list_dic_priority1
    elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2):
        Read_list = Master_Controller_Utils.read_list_dic_priority2
    elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3):
        Read_list = Master_Controller_Utils.read_list_dic_priority3
    elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4):
        Read_list = Master_Controller_Utils.read_list_dic_priority4
    Data_arr = []
    Read_one_by_one = False
    try:
        if(Master_Controller_Utils.USB0_Status_Flag == True):
            for parameters in JSON_data_dictionary["parameter"]:
                if(Master_Controller_Utils.USB0_Status_Flag == True):
                    sleep(0.001) 
                    #######################################
                    # Communicate_with_Controller()
                    Check_and_write_Controller_data()
                    #######################################
                    if(parameters["reg_name"] != "created_on" and parameters["reg_name"] != "modified_on" and (parameters["Access_type"] == "Read_Write" or parameters["Access_type"] == "Read")):
                        k= parameters["reg_name"]
                        if(parameters["type"] == "bool" or parameters["type"] == "Bool"):
                            try:
                                if(Master_Controller_Utils.client.is_socket_open() == False): 
                                    Master_Controller_Utils.client.connect()
                                if(Master_Controller_Utils.client.is_socket_open() == True):
                                    address = parameters["reg_num"]
                                    # print(Read_list[list_index]["start_address"],Read_list[list_index]["address_list"])
                                    try:
                                        if(list_read == True):
                                            if(Read_list[list_index]["start_address"] == address):
                                                Read_one_by_one = False
                                                # print(Read_list[list_index]["start_address"],Read_list[list_index]["address_list"])
                                                try:
                                                    Data_arr=[]
                                                    Response_status = Master_Controller_Utils.client.read_coils(address,count=len(Read_list[list_index]["address_list"]),unit=Master_Controller_Utils.Device_Address.value)
                                                    if(Response_status.isError() == False):
                                                        if(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1):
                                                            if(address in Master_Controller_Utils.Master_write1_value_dic1.keys()):
                                                                Master_Controller_Utils.write_list.append(address)
                                                        elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2):
                                                            if(address in Master_Controller_Utils.Master_write1_value_dic2.keys()):
                                                                Master_Controller_Utils.write_list.append(address)
                                                        elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3):
                                                            if(address in Master_Controller_Utils.Master_write1_value_dic3.keys()):
                                                                Master_Controller_Utils.write_list.append(address)
                                                        elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4):
                                                            if(address in Master_Controller_Utils.Master_write1_value_dic4.keys()):
                                                                Master_Controller_Utils.write_list.append(address)
                                                        try:
                                                            for i in range(len(Read_list[list_index]["address_list"])):
                                                                if(Response_status.bits[i] == True):
                                                                    # parameters["value"]='True'
                                                                    Data_arr.append('True')
                                                                elif(Response_status.bits[i] == False):
                                                                    # parameters["value"]="False"
                                                                    Data_arr.append("False")
                                                            parameters["value"] = Data_arr[0]
                                                            if(address in Master_Controller_Utils.Write_dict_priority1):
                                                                Master_Controller_Utils.Write_dict_priority1.remove(address)
                                                                if(Master_Controller_Utils.Write_dict_priority1==[]):
                                                                    Master_Controller_Utils.Written_dict_priority1 = False
                                                            elif(address in Master_Controller_Utils.Write_dict_priority2):
                                                                Master_Controller_Utils.Write_dict_priority2.remove(address)
                                                                if(Master_Controller_Utils.Write_dict_priority2==[]):
                                                                    Master_Controller_Utils.Written_dict_priority2 = False
                                                            elif(address in Master_Controller_Utils.Write_dict_priority3):
                                                                Master_Controller_Utils.Write_dict_priority3.remove(address)
                                                                if(Master_Controller_Utils.Write_dict_priority3==[]):
                                                                    Master_Controller_Utils.Written_dict_priority3 = False
                                                            elif(address in Master_Controller_Utils.Write_dict_priority4):
                                                                Master_Controller_Utils.Write_dict_priority4.remove(address)
                                                                if(Master_Controller_Utils.Write_dict_priority4==[]):
                                                                    Master_Controller_Utils.Written_dict_priority4 = False
                                                        except:
                                                            Read_one_by_one = True
                                                            pass
                                                    elif(Response_status.isError() == True):
                                                        if ((Response_status.function_code & 0x80 ) == 0x80):
                                                            if((Response_status.function_code & 0x83 ) == 0x83 or (Response_status.function_code & 0x82 ) == 0x82):
                                                                print('read_coils exception code',Response_status.exception_code,address)
                                                        print('read_coils exception code',address)
                                                        Read_one_by_one = True
                                                        pass
                                                except:
                                                    pass
                                                    Read_one_by_one = True
                                                    print("Controller is not responding to read_coils", Master_Controller_Utils.Device_Address.value,address)

                                                if(len(Read_list[list_index]["address_list"]) == 1):
                                                    list_read = True
                                                    count=0
                                                    list_index+=1

                                                else:
                                                    list_read = False
                                                    count+=1
                                        else:
                                            if(Read_one_by_one == False):
                                                parameters["value"] = Data_arr[count]
                                            count+=1
                                            if(len(Read_list[list_index]["address_list"]) == count):
                                                count=0
                                                list_index+=1
                                                list_read = True
                                    except Exception as e:
                                        print("Read_list[list_index][start_address] =",e,list_index)            
                                    if(Read_one_by_one == True):
                                        try:
                                            Response_status = Master_Controller_Utils.client.read_coils(address,count=1,unit=Master_Controller_Utils.Device_Address.value)
                            
                                            if(Response_status.isError() == False):
                                                if(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1):
                                                    if(address in Master_Controller_Utils.Master_write1_value_dic1.keys()):
                                                        Master_Controller_Utils.write_list.append(address)
                                                elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2):
                                                    if(address in Master_Controller_Utils.Master_write1_value_dic2.keys()):
                                                        Master_Controller_Utils.write_list.append(address)
                                                elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3):
                                                    if(address in Master_Controller_Utils.Master_write1_value_dic3.keys()):
                                                        Master_Controller_Utils.write_list.append(address)
                                                elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4):
                                                    if(address in Master_Controller_Utils.Master_write1_value_dic4.keys()):
                                                        Master_Controller_Utils.write_list.append(address)
                                                try:
                                                    if(Response_status.bits[0] == True):
                                                        parameters["value"]='True'
                                                    elif(Response_status.bits[0] == False):
                                                        parameters["value"]="False"
                                                    if(address in Master_Controller_Utils.Write_dict_priority1):
                                                        Master_Controller_Utils.Write_dict_priority1.remove(address)
                                                        if(Master_Controller_Utils.Write_dict_priority1==[]):
                                                            Master_Controller_Utils.Written_dict_priority1 = False
                                                    elif(address in Master_Controller_Utils.Write_dict_priority2):
                                                        Master_Controller_Utils.Write_dict_priority2.remove(address)
                                                        if(Master_Controller_Utils.Write_dict_priority2==[]):
                                                            Master_Controller_Utils.Written_dict_priority2 = False
                                                    elif(address in Master_Controller_Utils.Write_dict_priority3):
                                                        Master_Controller_Utils.Write_dict_priority3.remove(address)
                                                        if(Master_Controller_Utils.Write_dict_priority3==[]):
                                                            Master_Controller_Utils.Written_dict_priority3 = False
                                                    elif(address in Master_Controller_Utils.Write_dict_priority4):
                                                        Master_Controller_Utils.Write_dict_priority4.remove(address)
                                                        if(Master_Controller_Utils.Write_dict_priority4==[]):
                                                            Master_Controller_Utils.Written_dict_priority4 = False
                                                except:
                                                    pass
                                            elif(Response_status.isError() == True):
                                                if ((Response_status.function_code & 0x80 ) == 0x80):
                                                    if((Response_status.function_code & 0x83 ) == 0x83 or (Response_status.function_code & 0x82 ) == 0x82):
                                                        print('read_coils exception code',Response_status.exception_code,address)
                                                print('read_coils exception code',address)
                                                # Read_one_by_one = True
                                                # pass

                                        except:
                                            pass
                                            print("Controller is not responding to read_coils",Master_Controller_Utils.Device_Address.value,address)
                                else:
                                    print("Controller USB socket closed")
                                    # Master_Controller_Utils.run_once_flag = False
                                    if(Master_Controller_Utils.USB0_Status_Flag == True):
                                        Master_Controller_Utils.USB0_Status_Flag = False
                            except Exception as e:
                                print("bool controller uitils =",k,e,Read_one_by_one,"\n")
                        
                        else:
                            if(Master_Controller_Utils.client.is_socket_open() == False): 
                                Master_Controller_Utils.client.connect()
                            if(Master_Controller_Utils.client.is_socket_open() == True):
                                address = parameters["reg_num"]
                                try:
                                    if(list_read == True):
                                        if(Read_list[list_index]["start_address"] == address):
                                            Read_one_by_one = False
                                            # print(Read_list[list_index]["start_address"],Read_list[list_index]["address_list"])
                                            try:
                                                Data_arr=[]
                                                Response_status = Master_Controller_Utils.client.read_holding_registers(address,count=len(Read_list[list_index]["address_list"]),unit=Master_Controller_Utils.Device_Address.value)
                                                if(Response_status.isError() == False):
                                                    if(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1):
                                                        if(address in Master_Controller_Utils.Master_write1_value_dic1.keys()):
                                                            Master_Controller_Utils.write_list.append(address)
                                                    elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2):
                                                        if(address in Master_Controller_Utils.Master_write1_value_dic2.keys()):
                                                            Master_Controller_Utils.write_list.append(address)
                                                    elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3):
                                                        if(address in Master_Controller_Utils.Master_write1_value_dic3.keys()):
                                                            Master_Controller_Utils.write_list.append(address)
                                                    elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4):
                                                        if(address in Master_Controller_Utils.Master_write1_value_dic4.keys()):
                                                            Master_Controller_Utils.write_list.append(address)

                                                    try:
                                                        if(parameters["type"] == "integer"):
                                                            for i in range(len(Read_list[list_index]["address_list"])):
                                                                Decoder = BinaryPayloadDecoder.fromRegisters([Response_status.registers[i]],byteorder=Endian.Big, wordorder=Endian.Big)
                                                                value = Decoder.decode_16bit_int()
                                                                Data_arr.append(value)
                                                            parameters["value"] = Data_arr[0]
                                                        elif(parameters["type"] == "float"):
                                                            for i in range(len(Read_list[list_index]["address_list"])):
                                                                Decoder = BinaryPayloadDecoder.fromRegisters([Response_status.registers[i]],byteorder=Endian.Big, wordorder=Endian.Big)
                                                                value = Decoder.decode_16bit_float()
                                                                Data_arr.append(value)
                                                            parameters["value"] = Data_arr[0]
                                                        if(address in Master_Controller_Utils.Write_dict_priority1):
                                                            Master_Controller_Utils.Write_dict_priority1.remove(address)
                                                            if(Master_Controller_Utils.Write_dict_priority1==[]):
                                                                Master_Controller_Utils.Written_dict_priority1 = False
                                                        elif(address in Master_Controller_Utils.Write_dict_priority2):
                                                            Master_Controller_Utils.Write_dict_priority2.remove(address)
                                                            if(Master_Controller_Utils.Write_dict_priority2==[]):
                                                                Master_Controller_Utils.Written_dict_priority2 = False
                                                        elif(address in Master_Controller_Utils.Write_dict_priority3):
                                                            Master_Controller_Utils.Write_dict_priority3.remove(address)
                                                            if(Master_Controller_Utils.Write_dict_priority3==[]):
                                                                Master_Controller_Utils.Written_dict_priority3 = False
                                                        elif(address in Master_Controller_Utils.Write_dict_priority4):
                                                            Master_Controller_Utils.Write_dict_priority4.remove(address)
                                                            if(Master_Controller_Utils.Write_dict_priority4==[]):
                                                                Master_Controller_Utils.Written_dict_priority4 = False
                                                    except :
                                                        print("exption for =",parameters["reg_num"])
                                                        Read_one_by_one = True
                                                        pass

                                                elif(Response_status.isError() == True):
                                                    if ((Response_status.function_code & 0x80 ) == 0x80):
                                                        if((Response_status.function_code & 0x83 ) == 0x83 or (Response_status.function_code & 0x82 ) == 0x82):
                                                            print('read_holding_registers exception code',Response_status.exception_code,address)
                                                    print('read_holding_registers exception code',address)
                                                    Read_one_by_one = True
                                                    pass
                                            except:
                                                pass
                                                Read_one_by_one = True
                                                if(Master_Controller_Utils.Print_Enable == True):
                                                    print("Controller is not responding to read_holding_registers",address,Master_Controller_Utils.Device_Address.value )

                                            if(len(Read_list[list_index]["address_list"]) == 1):
                                                list_read = True
                                                count=0
                                                list_index+=1

                                            else:
                                                list_read = False
                                                count+=1
                                    else:
                                            if(Read_one_by_one == False):
                                                parameters["value"] = Data_arr[count]
                                            count+=1
                                            if(len(Read_list[list_index]["address_list"]) == count):
                                                count=0
                                                list_index+=1
                                                list_read = True
                                except Exception as e:
                                    print("Read_list[list_index][start_address] =",e,list_index)
                                if(Read_one_by_one == True):
                                    try:
                                        Response_status = Master_Controller_Utils.client.read_holding_registers(address,count=1,unit=Master_Controller_Utils.Device_Address.value)
                                        # print(Response_status)
                                        if(Response_status.isError() == False):
                                            if(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1):
                                                if(address in Master_Controller_Utils.Master_write1_value_dic1.keys()):
                                                    Master_Controller_Utils.write_list.append(address)
                                            elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2):
                                                if(address in Master_Controller_Utils.Master_write1_value_dic2.keys()):
                                                    Master_Controller_Utils.write_list.append(address)
                                            elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3):
                                                if(address in Master_Controller_Utils.Master_write1_value_dic3.keys()):
                                                    Master_Controller_Utils.write_list.append(address)
                                            elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4):
                                                if(address in Master_Controller_Utils.Master_write1_value_dic4.keys()):
                                                    Master_Controller_Utils.write_list.append(address)

                                            try:
                                                if(parameters["type"] == "integer"):
                                                    Decoder = BinaryPayloadDecoder.fromRegisters(Response_status.registers,byteorder=Endian.Big, wordorder=Endian.Big)
                                                    value = Decoder.decode_16bit_int()
                                                    Decoder.reset()
                                                    parameters["value"]=value
                                                elif(parameters["type"] == "float"):
                                                    Decoder = BinaryPayloadDecoder.fromRegisters(Response_status.registers,byteorder=Endian.Big, wordorder=Endian.Big)
                                                    value = Decoder.decode_16bit_float()
                                                    Decoder.reset()
                                                    parameters["value"]=value
                                                if(address in Master_Controller_Utils.Write_dict_priority1):
                                                    Master_Controller_Utils.Write_dict_priority1.remove(address)
                                                    if(Master_Controller_Utils.Write_dict_priority1==[]):
                                                        Master_Controller_Utils.Written_dict_priority1 = False
                                                elif(address in Master_Controller_Utils.Write_dict_priority2):
                                                    Master_Controller_Utils.Write_dict_priority2.remove(address)
                                                    if(Master_Controller_Utils.Write_dict_priority2==[]):
                                                        Master_Controller_Utils.Written_dict_priority2 = False
                                                elif(address in Master_Controller_Utils.Write_dict_priority3):
                                                    Master_Controller_Utils.Write_dict_priority3.remove(address)
                                                    if(Master_Controller_Utils.Write_dict_priority3==[]):
                                                        Master_Controller_Utils.Written_dict_priority3 = False
                                                elif(address in Master_Controller_Utils.Write_dict_priority4):
                                                    Master_Controller_Utils.Write_dict_priority4.remove(address)
                                                    if(Master_Controller_Utils.Write_dict_priority4==[]):
                                                        Master_Controller_Utils.Written_dict_priority4 = False
                                            except :
                                                print("exption for =",parameters["reg_num"])
                                                pass
                                        elif(Response_status.isError() == True):
                                            if ((Response_status.function_code & 0x80 ) == 0x80):
                                                if((Response_status.function_code & 0x83 ) == 0x83 or (Response_status.function_code & 0x82 ) == 0x82):
                                                    print('read_holding_registers exception code',Response_status.exception_code, address)
                                            print('read_holding_registers exception code', address)
                                    except:
                                        pass
                                        if(Master_Controller_Utils.Print_Enable == True):
                                            print("Controller is not responding to read_holding_registers",address,Master_Controller_Utils.Device_Address.value )
                            else:
                                print("Controller USB socket closed")
                                # Master_Controller_Utils.run_once_flag = False
                                if(Master_Controller_Utils.USB0_Status_Flag == True):
                                    Master_Controller_Utils.USB0_Status_Flag = False
                                # Master_Controller_Utils.USB0_Status_Flag = False
                    elif(parameters["reg_name"] == "created_on" or parameters["reg_name"] == "modified_on"):
                        Time_value = datetime.now()
                        parameters["value"] = "TIMESTAMP"+"'"+str(Time_value.year)+"-"+str(Time_value.month)+"-"+str(Time_value.day)+"T"+str(Time_value.hour)+":"+str(Time_value.minute)+":"+str(Time_value.second)+"."+str(Time_value.microsecond)+"'"
        return JSON_data_dictionary
    except Exception as e:
        print("JSON corrupted read=",k,e,Read_one_by_one,"\n")
        # print("JSON corrupted read=",k,e,"\n",JSON_data_dictionary)
        return JSON_data_dictionary

def Read_Controller_written_data(Reading_Address,JSON_data_dictionary,Prority):
    count = 0
    k =''
    try:
        if(Master_Controller_Utils.USB0_Status_Flag == True):
            for parameters in JSON_data_dictionary["parameter"]:
                if(Master_Controller_Utils.USB0_Status_Flag == True):
                    sleep(0.001) 
                    #######################################
                    # Communicate_with_Controller()
                    Check_and_write_Controller_data()
                    #######################################
                    if(((parameters["reg_name"] != "created_on") and (parameters["reg_name"] != "modified_on")) and (parameters["reg_num"] in Reading_Address)):
                        k= parameters["reg_name"]
                        if(parameters["type"] == "bool" or parameters["type"] == "Bool"):

                            if(Master_Controller_Utils.client.is_socket_open() == False): 
                                Master_Controller_Utils.client.connect()
                            if(Master_Controller_Utils.client.is_socket_open() == True):
                                address = parameters["reg_num"]
                                try:  
                                    Response_status = Master_Controller_Utils.client.read_coils(address,count=1,unit=Master_Controller_Utils.Device_Address.value)
                    
                                    if(Response_status.isError() == False):
                                        if(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1):
                                            if(address in Master_Controller_Utils.Master_write1_value_dic1.keys()):
                                                Master_Controller_Utils.write_list.append(address)
                                        elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2):
                                            if(address in Master_Controller_Utils.Master_write1_value_dic2.keys()):
                                                Master_Controller_Utils.write_list.append(address)
                                        elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3):
                                            if(address in Master_Controller_Utils.Master_write1_value_dic3.keys()):
                                                Master_Controller_Utils.write_list.append(address)
                                        elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4):
                                            if(address in Master_Controller_Utils.Master_write1_value_dic4.keys()):
                                                Master_Controller_Utils.write_list.append(address)
                                        
                                        try:
                                            if(Response_status.bits[0] == True):
                                                parameters["value"]='True'
                                            elif(Response_status.bits[0] == False):
                                                parameters["value"]="False"
                                            if(address in Master_Controller_Utils.Write_dict_priority1):
                                                Master_Controller_Utils.Write_dict_priority1.remove(address)
                                                if(Master_Controller_Utils.Write_dict_priority1==[]):
                                                    Master_Controller_Utils.Written_dict_priority1 = False
                                            elif(address in Master_Controller_Utils.Write_dict_priority2):
                                                Master_Controller_Utils.Write_dict_priority2.remove(address)
                                                if(Master_Controller_Utils.Write_dict_priority2==[]):
                                                    Master_Controller_Utils.Written_dict_priority2 = False
                                            elif(address in Master_Controller_Utils.Write_dict_priority3):
                                                Master_Controller_Utils.Write_dict_priority3.remove(address)
                                                if(Master_Controller_Utils.Write_dict_priority3==[]):
                                                    Master_Controller_Utils.Written_dict_priority3 = False
                                            elif(address in Master_Controller_Utils.Write_dict_priority4):
                                                Master_Controller_Utils.Write_dict_priority4.remove(address)
                                                if(Master_Controller_Utils.Write_dict_priority4==[]):
                                                    Master_Controller_Utils.Written_dict_priority4 = False
                                        except:
                                            pass
                                        # print("no respose for ", address , value, Response_status)
                                    elif(Response_status.isError() == True):
                                        flag=False
                                except:
                                    pass
                                    print("Controller is not responding to read_coils", Master_Controller_Utils.Device_Address.value,address)
                            else:
                                pass
                        else:
                            if(Master_Controller_Utils.client.is_socket_open() == False): 
                                Master_Controller_Utils.client.connect()
                            if(Master_Controller_Utils.client.is_socket_open() == True):
                                address = parameters["reg_num"]
                                # print(address)
                                try:
                                    Response_status = Master_Controller_Utils.client.read_holding_registers(address,count=1,unit=Master_Controller_Utils.Device_Address.value)
                                    if(Response_status.isError() == False):
                                        if(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1):
                                            if(address in Master_Controller_Utils.Master_write1_value_dic1.keys()):
                                                Master_Controller_Utils.write_list.append(address)
                                        elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2):
                                            if(address in Master_Controller_Utils.Master_write1_value_dic2.keys()):
                                                Master_Controller_Utils.write_list.append(address)
                                        elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3):
                                            if(address in Master_Controller_Utils.Master_write1_value_dic3.keys()):
                                                Master_Controller_Utils.write_list.append(address)
                                        elif(Prority == Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4):
                                            if(address in Master_Controller_Utils.Master_write1_value_dic4.keys()):
                                                Master_Controller_Utils.write_list.append(address)
                                        
                                        if(parameters["type"] == "integer"):
                                            try:
                                                Decoder = BinaryPayloadDecoder.fromRegisters(Response_status.registers,byteorder=Endian.Big, wordorder=Endian.Big)
                                                value = Decoder.decode_16bit_int()
                                                parameters["value"]=((value*parameters["factor"]) + parameters["offset"])
                                                if(address in Master_Controller_Utils.Write_dict_priority1):
                                                    Master_Controller_Utils.Write_dict_priority1.remove(address)
                                                    if(Master_Controller_Utils.Write_dict_priority1==[]):
                                                        Master_Controller_Utils.Written_dict_priority1 = False
                                                elif(address in Master_Controller_Utils.Write_dict_priority2):
                                                    Master_Controller_Utils.Write_dict_priority2.remove(address)
                                                    if(Master_Controller_Utils.Write_dict_priority2==[]):
                                                        Master_Controller_Utils.Written_dict_priority2 = False
                                                elif(address in Master_Controller_Utils.Write_dict_priority3):
                                                    Master_Controller_Utils.Write_dict_priority3.remove(address)
                                                    if(Master_Controller_Utils.Write_dict_priority3==[]):
                                                        Master_Controller_Utils.Written_dict_priority3 = False
                                                elif(address in Master_Controller_Utils.Write_dict_priority4):
                                                    Master_Controller_Utils.Write_dict_priority4.remove(address)
                                                    if(Master_Controller_Utils.Write_dict_priority4==[]):
                                                        Master_Controller_Utils.Written_dict_priority4 = False
                                            except :
                                                print("exption for =",parameters["reg_num"])
                                                pass
                                        elif(parameters["type"] == "float"):
                                            try:
                                                # value=( (data_rec[4]<<8) | data_rec[3])
                                                Decoder = BinaryPayloadDecoder.fromRegisters(Response_status.registers,byteorder=Endian.Big, wordorder=Endian.Big)
                                                # Decoder.reset()
                                                value = Decoder.decode_16bit_float()
                                                parameters["value"]=((value*parameters["factor"]) + parameters["offset"])
                                                if(address in Master_Controller_Utils.Write_dict_priority1):
                                                    Master_Controller_Utils.Write_dict_priority1.remove(address)
                                                    if(Master_Controller_Utils.Write_dict_priority1==[]):
                                                        Master_Controller_Utils.Written_dict_priority1 = False
                                                elif(address in Master_Controller_Utils.Write_dict_priority2):
                                                    Master_Controller_Utils.Write_dict_priority2.remove(address)
                                                    if(Master_Controller_Utils.Write_dict_priority2==[]):
                                                        Master_Controller_Utils.Written_dict_priority2 = False
                                                elif(address in Master_Controller_Utils.Write_dict_priority3):
                                                    Master_Controller_Utils.Write_dict_priority3.remove(address)
                                                    if(Master_Controller_Utils.Write_dict_priority3==[]):
                                                        Master_Controller_Utils.Written_dict_priority3 = False
                                                elif(address in Master_Controller_Utils.Write_dict_priority4):
                                                    Master_Controller_Utils.Write_dict_priority4.remove(address)
                                                    if(Master_Controller_Utils.Write_dict_priority4==[]):
                                                        Master_Controller_Utils.Written_dict_priority4 = False
                                            except :
                                                print("exption for =",parameters["reg_num"])
                                                pass
                                    elif(Response_status.isError() == True):
                                        flag=False
                                except:
                                    pass
                                    if(Master_Controller_Utils.Print_Enable == True):
                                        print("Controller is not responding to read_holding_registers", Master_Controller_Utils.Device_Address.value,address)
                            else:
                                pass
                    elif(parameters["reg_name"] == "created_on" or parameters["reg_name"] == "modified_on"):
                        Time_value = datetime.now()
                        parameters["value"] = "TIMESTAMP"+"'"+str(Time_value.year)+"-"+str(Time_value.month)+"-"+str(Time_value.day)+"T"+str(Time_value.hour)+":"+str(Time_value.minute)+":"+str(Time_value.second)+"."+str(Time_value.microsecond)+"'"
        return JSON_data_dictionary
    except Exception as e:
        print("JSON corrupted=",k,e)
        return JSON_data_dictionary

def Check_and_write_Controller_data():
    if(len(Master_Controller_Utils.Master_write_value_dic1) != 0):
        Master_Controller_Utils.Master_written_JSON_Priority1_Flag = False
        data_dictionary_Master_to_Controller_Priority1 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1)
        data_dictionary_Controller_to_Master_Priority1 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_1)
        if (Master_Controller_Utils.Write_to_controller_Flag==True):           
            Master_Controller_Utils.Master_written_conform_JSON_Priority1_Flag = Write_Controller_data(data_dictionary_Master_to_Controller_Priority1,data_dictionary_Controller_to_Master_Priority1,Master_Controller_Utils.REF_DICT_PRIORITY_1,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1)
    if(len(Master_Controller_Utils.Master_write_value_dic2) != 0):
        Master_Controller_Utils.Master_written_JSON_Priority2_Flag = False
        data_dictionary_Master_to_Controller_Priority2 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2)
        data_dictionary_Controller_to_Master_Priority2 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_2)
        if (Master_Controller_Utils.Write_to_controller_Flag==True):           
            Master_Controller_Utils.Master_written_conform_JSON_Priority2_Flag = Write_Controller_data(data_dictionary_Master_to_Controller_Priority2,data_dictionary_Controller_to_Master_Priority2,Master_Controller_Utils.REF_DICT_PRIORITY_2,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2)
    
    if(len(Master_Controller_Utils.Master_write_value_dic3) != 0):
        Master_Controller_Utils.Master_written_JSON_Priority3_Flag = False
        data_dictionary_Master_to_Controller_Priority3 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3)
        data_dictionary_Controller_to_Master_Priority3 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_3)
        if (Master_Controller_Utils.Write_to_controller_Flag==True):           
            Master_Controller_Utils.Master_written_conform_JSON_Priority3_Flag = Write_Controller_data(data_dictionary_Master_to_Controller_Priority3,data_dictionary_Controller_to_Master_Priority3,Master_Controller_Utils.REF_DICT_PRIORITY_3,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3)
    
    if(len(Master_Controller_Utils.Master_write_value_dic4) != 0):
        Master_Controller_Utils.Master_written_JSON_Priority4_Flag = False
        data_dictionary_Master_to_Controller_Priority4 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4)
        data_dictionary_Controller_to_Master_Priority4 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_4)
        if (Master_Controller_Utils.Write_to_controller_Flag==True):           
            Master_Controller_Utils.Master_written_conform_JSON_Priority4_Flag = Write_Controller_data(data_dictionary_Master_to_Controller_Priority4,data_dictionary_Controller_to_Master_Priority4,Master_Controller_Utils.REF_DICT_PRIORITY_4,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4)




def ReRead_controller():
    if(Master_Controller_Utils.Written_dict_priority1 == True and Master_Controller_Utils.Write_dict_priority1 != []):
        data_dictionary_Controller_to_Master_Priority1 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_1)
        Master_Controller_Utils.write_list = []
        JSON_data_dictionary = Read_Controller_written_data(Master_Controller_Utils.Write_dict_priority1,data_dictionary_Controller_to_Master_Priority1,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1)
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
                Master_Controller_Utils.Written_dict_priority1 = False
                         
    if(Master_Controller_Utils.Written_dict_priority2 == True and Master_Controller_Utils.Write_dict_priority2 != []):
        data_dictionary_Controller_to_Master_Priority2 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_2)
        Master_Controller_Utils.write_list = []
        JSON_data_dictionary = Read_Controller_written_data(Master_Controller_Utils.Write_dict_priority2,data_dictionary_Controller_to_Master_Priority2,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2)
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
                Master_Controller_Utils.Written_dict_priority2 = False
            
    if(Master_Controller_Utils.Written_dict_priority3 == True and Master_Controller_Utils.Write_dict_priority3 != []):
        data_dictionary_Controller_to_Master_Priority3 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_3)
        Master_Controller_Utils.write_list = []
        JSON_data_dictionary = Read_Controller_written_data(Master_Controller_Utils.Write_dict_priority3,data_dictionary_Controller_to_Master_Priority3,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3)
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
                Master_Controller_Utils.Written_dict_priority3 = False

    if(Master_Controller_Utils.Written_dict_priority4 == True and Master_Controller_Utils.Write_dict_priority4 != []):
        data_dictionary_Controller_to_Master_Priority4 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_4)
        Master_Controller_Utils.write_list = []
        JSON_data_dictionary = Read_Controller_written_data(Master_Controller_Utils.Write_dict_priority4,data_dictionary_Controller_to_Master_Priority4,Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4)
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
                Master_Controller_Utils.Written_dict_priority4 = False


        