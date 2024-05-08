import requests
import json
import Master_Controller_Utils 
import datetime
from datetime import *
from time import sleep
import os, re, os.path
import glob
from read_write_database.login import headers, user_login


def config_get(API):
    r = requests.get(API, headers=headers)
    error_code = r.status_code
    error_status = r.text
    if(error_code == 401 or error_status == '{"detail":"Authentication credentials were not provided."}'):
        user_login()
        r = requests.get(API, headers=headers)
    return r

def config_post(API,data):
    r = requests.post(API, data=data, headers=headers)
    error_code = r.status_code
    error_status = r.text
    if(error_code == 401 or error_status == '{"detail":"Authentication credentials were not provided."}'):
        user_login()
        r = requests.post(API,data=data, headers=headers)
    return r

def config_patch(API,data):
    r = requests.patch(API, data=data, headers=headers)
    error_code = r.status_code
    error_status = r.text
    if(error_code == 401 or error_status == '{"detail":"Authentication credentials were not provided."}'):
        user_login()
        r = requests.patch(API,data=data, headers=headers)
    #print(r.status_code)
    # print(r.content)
    return r

def Time_defer_check(Stored_JSON_Time,Database_Time):
    try:
        Stored_JSON_Time=Stored_JSON_Time.replace('T',' ')
    except:
        pass
    try:
        Stored_JSON_Time=Stored_JSON_Time.replace('Z',' ')
    except:
        pass
    try:
        Stored_JSON_Time=Stored_JSON_Time.replace('+05:30','')
    except:
        pass
    x=Stored_JSON_Time.split()
    b=str(x[0])
    c=str(x[1])
    c_list=c.replace(':', ' ').replace('.', ' ').split()
    b_list=b.replace('-', ' ').split()
    b_list_old=b_list+c_list
#     print(b_list_old)

    try:
        Database_Time=Database_Time.replace('T',' ')
    except:
        pass
    try:
        Database_Time=Database_Time.replace('Z',' ')
    except:
        pass
    try:
        Database_Time=Database_Time.replace('+05:30','')
    except:
        pass
    x=Database_Time.split()
    b=str(x[0])
    c=str(x[1])
    c_list=c.replace(':', ' ').replace('.', ' ').split()
    Micro_sec_2=c_list[3]
    b_list=b.replace('-', ' ').split()
    b_list_new=b_list+c_list
#     print(b_list_new)
    B_list_old = []
    for i in b_list_old:
        B_list_old.append(int(i))
    B_list_new = []
    for i in b_list_new:
        B_list_new.append(int(i))
#     B_list_old=[eval(i) for i in b_list_old]
#     B_list_new =[eval(i) for i in b_list_new]
#     print(B_list_old)
#     print(B_list_new)
    for old,new in zip(B_list_old,B_list_new):
        if old == new :
            pass 
        else :
            if old < new:
                # print(B_list_old)
                # print(B_list_new)
                return 1
            elif old > new:
                return 1
    return 0       

def Configuration_DB():
    sleep(0.1)
    while(1):
        if(Master_Controller_Utils.Database_setup==True):
            try:
                r = config_get(Master_Controller_Utils.Check_Conf_Api)
                # print(r.status_code)
                    #print(r)
                try:
                    get_data = r.text
                    # print(get_data)
                    if get_data == "[]":
                        Master_Controller_Utils.First_Configuration()
                        data = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.Read_Configuration)
                        response_API = config_post(Master_Controller_Utils.Check_Conf_Api,data[0])
                        # print(response_API.status_code)
                        # print(response_API)
                        # print(response_API.content)
                        response_API_get= config_get(Master_Controller_Utils.Check_Conf_Api)
                        json_response=response_API_get.json()
                        # print(json_response)
                        # print(json_response[0]['modified_on'])
                        modified_time=json_response[0]['modified_on']
                        Master_Controller_Utils.Config_Table_update_time=modified_time
                        # print(modified_time)
                        try:
                            Data=json.loads(open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json').read())
                            # print("from file",Data["time"])
                            Data["time"]=str(modified_time)
                        except :
                            with open(Master_Controller_Utils.Dir+'/read_write_database/time_update_back_up.json','r') as file:
                                    Data=file.read()
                                    file.close()
                            with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','w') as file:
                                    json.dump(Data,file,indent=5)
                                    file.close()
                        Data["time"]=str(modified_time)
                        with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','w') as file:
                            json.dump(Data,file,indent=5)
                            file.close()
                        Master_Controller_Utils.first_time_write_to_controller = False
                    else:
                        r = config_get(Master_Controller_Utils.Check_Conf_Api)
                        # get_data = r.text
                        get_data=r.json()
                        
                        id=get_data[0]['id']
                        url_path=Master_Controller_Utils.Check_Conf_Api + str(id) + "/"
                        get_url_path= Master_Controller_Utils.Check_Conf_Api
                        # print(id)

                        if(Master_Controller_Utils.first_time_write_to_controller == True):
                            Master_Controller_Utils.first_time_write_to_controller = False
                            Master_Controller_Utils.First_Configuration()
                            Data_Read = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.Read_Configuration)

                            response_API = config_patch(url_path,Data_Read[0])
                            response_API_get= config_get(get_url_path)
                            json_response=response_API_get.json()
                            # print(json_response['modified_on'])
                            modified_time=json_response[0]['modified_on']
                            Master_Controller_Utils.Config_Table_update_time=modified_time


                            try:
                                Data=json.loads(open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json').read())
                                # print("from file",Data["time"])
                                Data["time"]=str(modified_time)
                            except :
                                with open(Master_Controller_Utils.Dir+'/read_write_database/time_update_back_up.json','r') as file:
                                    Data=file.read()
                                    file.close()
                                with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','w') as file:
                                    json.dump(Data,file,indent=5)
                                    file.close()
                            Data["time"]=str(modified_time)
                            with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','w') as file:
                                json.dump(Data,file,indent=5)
                                file.close()

                        else:   
                            with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','r') as file:
                                JSON_Data_string=file.read()
                                JSON_Data_time=json.loads(JSON_Data_string)
                                # print(JSON_Data_time['time'])
                                file.close()
                            
                            r_response = config_get(get_url_path)
                            
                            json_response=r_response.json()
                            modified_time=json_response[0]['modified_on']
                            status=Time_defer_check( Stored_JSON_Time=JSON_Data_time['time'] ,Database_Time=modified_time)
                            
                            if(status == 0):
                                if( Master_Controller_Utils.Copy_controller_config() == True ):
                                    CONFIGURATION_DICTIONARY = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.Read_Configuration)
                                    # mypath = "/home/hussmann/Desktop/SEM/Webserver/sem_django/sem/JSON_Files"
                                    mypath = Master_Controller_Utils.WebServer_JSON_Dir
                                    # list_ = glob.glob(r"/home/hussmann/Desktop/SEM/Webserver/sem_django/sem/JSON_Files/*.json")
                                    list_ = glob.glob(r""+Master_Controller_Utils.WebServer_JSON_Dir+"/*.json")
                                    if(list_ == []): 
                                        count = 0
                                        for root, dirs, files in os.walk(mypath):
                                            for file in files:
                                                os.remove(os.path.join(root, file))
                                                count+=1
                                        if(count>0):
                                            print("deleted_0 files = ",count)
                                        r_response = config_get(get_url_path)
                                        json_response=r_response.json()
                                        modified_time=json_response[0]['modified_on']
                                        status=Time_defer_check( Stored_JSON_Time=JSON_Data_time['time'] ,Database_Time=modified_time)
                                    else:
                                        status = 1
                                        print("skip to status 1")
                                    if(status == 0):
                                        # mypath = "/home/hussmann/Desktop/SEM/Webserver/sem_django/sem/JSON_Files"
                                        # # mypath = Master_Controller_Utils.WebServer_JSON_Dir
                                        # for root, dirs, files in os.walk(mypath):
                                        #         for file in files:
                                        #                 os.remove(os.path.join(root, file))
                                        r = config_patch(url_path,CONFIGURATION_DICTIONARY[0])

                                        # list_ = glob.glob(r"/home/hussmann/Desktop/SEM/Webserver/sem_django/sem/JSON_Files/*.json")
                                        list_ = glob.glob(r""+Master_Controller_Utils.WebServer_JSON_Dir+"/*.json")
                                        if(list_ != []): 
                                            with open(list_[0],'r') as file:
                                                JSON_Data_string=file.read()
                                                JSON_Data_from_server=json.loads(JSON_Data_string)
                                                file.close()
                                            for KEYS,VALUES in JSON_Data_from_server[0].items():
                                                if KEYS == "modified_on":
                                                    print("modified time from the server=",VALUES)
                                            #print("web server rewriting")  
                                            # print(modified_time)
                                            #print(list_)  
                                            count = 0   
                                            for root, dirs, files in os.walk(mypath):
                                                for file in files:
                                                        os.remove(os.path.join(root, file))
                                                        count+=1
                                            if(count>0):
                                                print("deleted_1 files = ",count)
                                            #to get time and write in the file 
                                            r_response = config_get(get_url_path)
                                            json_response=r_response.json()
                                            modified_time=json_response[0]['modified_on']
                                            # print(modified_time)
                                            JSON_Data_time['time']=modified_time
                                            with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','w') as file:
                                                    json.dump(JSON_Data_time,file,indent=5)
                                                    file.close()
                                            # print(modified_time)   
                                            CONFIGURATION_DICTIONARY = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.Write_Configuration)
                                            for key_1,value_1 in JSON_Data_from_server[0].items():
                                                if key_1 in CONFIGURATION_DICTIONARY[0].keys():
                                                    CONFIGURATION_DICTIONARY[0][key_1] = value_1
                                            #print("me writing=",JSON_Data_from_server[0]["min_set_point"])
                                            r = config_patch(url_path,CONFIGURATION_DICTIONARY[0])                                               

                                        else:
                                            #to get time and write in the file 
                                            r_response = config_get(get_url_path)
                                            json_response=r_response.json()
                                            modified_time=json_response[0]['modified_on']
                                            # print(modified_time)
                                            JSON_Data_time['time']=modified_time
                                            with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','w') as file:
                                                json.dump(JSON_Data_time,file,indent=5)
                                                file.close()
                                else:
                                    pass

                            while(status == 1):
                                # list_ = glob.glob(r"/home/hussmann/Desktop/SEM/Webserver/sem_django/sem/JSON_Files/*.json")
                                list_ = glob.glob(r""+Master_Controller_Utils.WebServer_JSON_Dir+"/*.json")
                                json_response = []
                                if(list_ != []): 
                                    with open(list_[0],'r') as file:
                                        JSON_Data_string=file.read()
                                        json_response=json.loads(JSON_Data_string)
                                        file.close()
                                mypath = Master_Controller_Utils.WebServer_JSON_Dir
                                # mypath = "/home/hussmann/Desktop/SEM/Webserver/sem_django/sem/JSON_Files"
                                count=0
                                for root, dirs, files in os.walk(mypath):
                                    for file in files:
                                        os.remove(os.path.join(root, file))
                                        count+=1
                                if(count>0):
                                    print("deleted files = ",count)
                                    # json_response=JSON_Data_from_server
                                # else:

                                get_response = config_get(get_url_path)
                                json_response=get_response.json()
                                #print("expected new data")

                                # r_response = config_get (get_url_path)
                                # json_response=r_response.json()
                                modified_time=json_response[0]['modified_on']

                                data=Master_Controller_Utils.data_written_from_Configuration(json_response[0]) 
                                #print(data)
                                CONFIGURATION_DICTIONARY = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.Read_Configuration)
                                r_response = config_get(get_url_path)
                                json_response=r_response.json()
                                modified_time1=json_response[0]['modified_on']
                                if(modified_time == modified_time1):
                                    print("Expected patch")
                                    # r = config_patch(url_path, data = CONFIGURATION_DICTIONARY[0])
                                    # #to get time and write in the file 
                                    # r_response = config_get (get_url_path)
                                    # json_response=r_response.json()
                                    # modified_time=json_response[0]['modified_on']
                                    # # print(modified_time)
                                    # JSON_Data_time['time']=modified_time
                                    # with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','w') as file:
                                    #     json.dump(JSON_Data_time,file,indent=5)
                                    #     file.close()
                                    # r = config_patch(url_path, data = CONFIGURATION_DICTIONARY[0])

                                    # list_ = glob.glob(r"/home/hussmann/Desktop/SEM/Webserver/sem_django/sem/JSON_Files/*.json")
                                    list_ = glob.glob(r""+Master_Controller_Utils.WebServer_JSON_Dir+"/*.json")
                                    if(list_ != []): 
                                        with open(list_[0],'r') as file:
                                            JSON_Data_string=file.read()
                                            JSON_Data_from_server=json.loads(JSON_Data_string)
                                            file.close()
                                        for KEYS,VALUES in JSON_Data_from_server[0].items():
                                            if KEYS == "modified_on":
                                                print("modified time from the server=",VALUES)
                                        # print("web server rewriting")  
                                        # print(modified_time)
                                        #print(list_)  
                                        count = 0   
                                        for root, dirs, files in os.walk(mypath):
                                            for file in files:
                                                    os.remove(os.path.join(root, file))
                                                    count+=1
                                        if(count>0):
                                            print("deleted_3 files = ",count)
                                        #to get time and write in the file 
                                        r_response = config_get(get_url_path)
                                        json_response=r_response.json()
                                        modified_time=json_response[0]['modified_on']
                                        # print(modified_time)
                                        JSON_Data_time['time']=modified_time
                                        with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','w') as file:
                                                json.dump(JSON_Data_time,file,indent=5)
                                                file.close()
                                        #print(modified_time)   
                                        CONFIGURATION_DICTIONARY = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.Write_Configuration)
                                        for key_1,value_1 in JSON_Data_from_server[0].items():
                                            if key_1 in CONFIGURATION_DICTIONARY[0].keys():
                                                CONFIGURATION_DICTIONARY[0][key_1] = value_1
                                        r = config_patch(url_path, CONFIGURATION_DICTIONARY[0]) 
                                    else:
                                        r = config_patch(url_path, data = CONFIGURATION_DICTIONARY[0])
                                        #to get time and write in the file 
                                        r_response = config_get(get_url_path)
                                        json_response=r_response.json()
                                        modified_time=json_response[0]['modified_on']
                                        # print(modified_time)
                                        JSON_Data_time['time']=modified_time
                                        with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','w') as file:
                                            json.dump(JSON_Data_time,file,indent=5)
                                            file.close()
                                        status = 0

                        Master_Controller_Utils.Database_setup=True

                    # return True
                except Exception as e:
                    print(e)
                    # return False
            except Exception as e:
                    # return False
                    pass
            sleep(0.01)
        else:
            sleep(1)


def Configuration_DB_Init():
    try:
        r = config_get(Master_Controller_Utils.Check_Conf_Api)

        try:
            get_data = r.text
            # print(get_data)
            if get_data == "[]":
                Master_Controller_Utils.First_Configuration()
                data = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.Read_Configuration)
                response_API = config_post(Master_Controller_Utils.Check_Conf_Api,data[0])
                # print(response_API.status_code)
                # print(response_API)
                # print(response_API.content)
                response_API_get= config_get(Master_Controller_Utils.Check_Conf_Api)
                json_response=response_API_get.json()
                # print(json_response)
                # print(json_response[0]['modified_on'])
                modified_time=json_response[0]['modified_on']
                Master_Controller_Utils.Config_Table_update_time=modified_time
                # print(modified_time)
                # print(present_TIME11)
                try:
                    Data=json.loads(open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json').read())
                    # print("from file",Data["time"])
                    Data["time"]=str(modified_time)
                except :
                    with open(Master_Controller_Utils.Dir+'/read_write_database/time_update_back_up.json','r') as file:
                            Data=file.read()
                            file.close()
                    with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','w') as file:
                            json.dump(Data,file,indent=5)
                            file.close()
                Data["time"]=str(modified_time)
                with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','w') as file:
                    json.dump(Data,file,indent=5)
                    file.close()
                Master_Controller_Utils.first_time_write_to_controller = False
            else:
                r = config_get(Master_Controller_Utils.Check_Conf_Api)
                # get_data = r.text
                # data_11=json.dumps(get_data)
                get_data=r.json()
                id=get_data[0]['id']
                url_path= Master_Controller_Utils.Check_Conf_Api + str(id) + "/"
                get_url_path= Master_Controller_Utils.Check_Conf_Api
                # print(id)

                if(Master_Controller_Utils.first_time_write_to_controller == True):
                    Master_Controller_Utils.first_time_write_to_controller = False
                    Master_Controller_Utils.First_Configuration()
                    Data_Read = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.Read_Configuration)

                    response_API = config_patch(url_path,Data_Read[0])
                    response_API_get= config_get(get_url_path)
                    json_response=response_API_get.json()
                    # print(json_response['modified_on'])
                    modified_time=json_response[0]['modified_on']
                    Master_Controller_Utils.Config_Table_update_time=modified_time
                    # print(modified_time)
                    # print(present_TIME11)
                    try:
                        Data=json.loads(open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json').read())
                        # print("from file",Data["time"])
                        Data["time"]=str(modified_time)
                    except :
                        with open(Master_Controller_Utils.Dir+'/read_write_database/time_update_back_up.json','r') as file:
                                Data=file.read()
                                file.close()
                        with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','w') as file:
                                json.dump(Data,file,indent=5)
                                file.close()
                    Data["time"]=str(modified_time)
                    with open(Master_Controller_Utils.Dir+'/read_write_database/time_update.json','w') as file:
                        json.dump(Data,file,indent=5)
                        file.close()
            Master_Controller_Utils.Database_setup=True

            return True
        except Exception as e:
            print(e)
            return False
    except Exception as e:
            return False
