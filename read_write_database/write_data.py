import schedule
import psycopg2
import json
import time
import Master_Controller_Utils 
import requests
from read_write_database.login import headers, user_login


def post_data(API,data):
    r = requests.post(API, data=data, headers=headers)
    error_code = r.status_code
    error_status = r.text

    if(error_code == 401 or error_status == '{"detail":"Authentication credentials were not provided."}'):
        user_login()
        r = requests.post(API,data=data, headers=headers)

    return r

def Controller_10sec():

    
    data = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_1)
    json_data=[]
    for i in data:
        json_data.append(data[i])
    
    #print(json_data)
    length=len(data[i])
    parameter_name = []
    parameter_value = []
    for i in range(length):
        parameters = (json_data[0][i]['reg_name'])
        values = (json_data[0][i]['value'])
        parameter_name.append(parameters)
        parameter_value.append(values)

    converted_data = {}
    for key in parameter_name:
        for value in parameter_value:
            converted_data[key] = value
            parameter_value.remove(value)
            break
    # print(converted_data)

    response_API = post_data(Master_Controller_Utils.Check_Sec_Api,converted_data)
    # print(response_API.status_code)
    # print(response_API.content)




def Controller_5min():
    
    data = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_2)
    
    json_data=[]
    for i in data:
        json_data.append(data[i])

    length=len(data[i])
    parameter_name = []
    parameter_value = []
    for i in range(length):
        parameters = (json_data[0][i]['reg_name'])
        values = (json_data[0][i]['value'])
        parameter_name.append(parameters)
        parameter_value.append(values)

    converted_data = {}
    for key in parameter_name:
        for value in parameter_value:
            converted_data[key] = value
            parameter_value.remove(value)
            break


    response_API = post_data(Master_Controller_Utils.Check_Min_Api, converted_data)
 
    # print(response_API.status_code)
    # print(response_API.content)


   
def Controller_4hour():
   
    data = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_3)
    
    json_data=[]
    for i in data:
        json_data.append(data[i])

    length=len(data[i])
    parameter_name = []
    parameter_value = []
    for i in range(length):
        parameters = (json_data[0][i]['reg_name'])
        values = (json_data[0][i]['value'])
        parameter_name.append(parameters)
        parameter_value.append(values)

    converted_data = {}
    for key in parameter_name:
        for value in parameter_value:
            converted_data[key] = value
            parameter_value.remove(value)
            break

    #print(converted_data)
    
    response_API = post_data(Master_Controller_Utils.Check_Hour_Api,converted_data)

    # print(response_API.status_code)
    # print(response_API.content)

   
   
