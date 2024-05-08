from ast import Pass
import imp
import multiprocessing
from signal import signal
from sqlite3 import connect

from numpy import append
import Master_Controller_Utils
import serial.tools.list_ports as prtlst
import time
from pymodbus.payload import BinaryPayloadBuilder, Endian, BinaryPayloadDecoder

from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
# from twisted.internet.task import LoopingCall
from pymodbus.server.sync import StartTcpServer

# from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.server.asynchronous import StartSerialServer, StopServer
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer
from pymodbus.datastore import ModbusSequentialDataBlock,ModbusSparseDataBlock
import json
import threading
import sys
from threading import Thread
from signal import SIGKILL
from pymodbus.pdu import ModbusRequest, ModbusResponse
from pymodbus.device import ModbusControlBlock, DeviceInformationFactory
from pymodbus.constants import ModbusStatus 
from pymodbus.compat import byte2int, int2byte
# from pymodbus.pdu.ModbusRequest
from pymodbus.register_read_message import ReadRegistersRequestBase, ReadRegistersResponseBase,ReadHoldingRegistersResponse
import struct
from pymodbus.pdu import ModbusRequest
from pymodbus.pdu import ModbusResponse
from pymodbus.pdu import ModbusExceptions as merror
from pymodbus.compat import int2byte, byte2int
from pymodbus.bit_read_message import ReadBitsRequestBase,ReadBitsResponseBase,ReadCoilsResponse
from pymodbus.register_write_message import WriteMultipleRegistersResponse
from pymodbus.bit_write_message import WriteMultipleCoilsResponse
from pymodbus.utilities import pack_bitstring, unpack_bitstring



from multiprocessing import Process
import os
import time
import serial
from time import sleep
from time import time as TIME

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
    crc=hex(((crc&0xff00)>>8)|((crc & 0x00ff)<<8))
    return crc

class ReadCoilsRequest(ReadBitsRequestBase):
    '''
    This function code is used to read from 1 to 2000(0x7d0) contiguous status
    of coils in a remote device. The Request PDU specifies the starting
    address, ie the address of the first coil specified, and the number of
    coils. In the PDU Coils are addressed starting at zero. Therefore coils
    numbered 1-16 are addressed as 0-15.
    '''
    function_code = 1

    def __init__(self, address=None, count=None, **kwargs):
        ''' Initializes a new instance

        :param address: The address to start reading from
        :param count: The number of bits to read
        '''
        ReadBitsRequestBase.__init__(self, address, count, **kwargs)

    def execute(self, context):
        ''' Run a read coils request against a datastore

        Before running the request, we make sure that the request is in
        the max valid range (0x001-0x7d0). Next we make sure that the
        request is valid against the current datastore.

        :param context: The datastore to request from
        :returns: The initializes response message, exception message otherwise
        '''
        # print("ReadCoilsRequest Slave ID =",self.unit_id)
        if(Master_Controller_Utils.is_tcp_ip == False):
            pass
        # Master_Controller_Utils.Device_Address.value = self.unit_id
        if not (1 <= self.count <= 0x7d0):
            return self.doException(merror.IllegalValue)
        if not context.validate(self.function_code, self.address, self.count):
            return self.doException(merror.IllegalAddress)
        values = context.getValues(self.function_code, self.address, self.count)
        return ReadCoilsResponse(values)

class ReadHoldingRegistersRequest(ReadRegistersRequestBase):
    '''
    This function code is used to read the contents of a contiguous block
    of holding registers in a remote device. The Request PDU specifies the
    starting register address and the number of registers. In the PDU
    Registers are addressed starting at zero. Therefore registers numbered
    1-16 are addressed as 0-15.
    '''
    function_code = 3

    def __init__(self, address=None, count=None, **kwargs):
        ''' Initializes a new instance of the request

        :param address: The starting address to read from
        :param count: The number of registers to read from address
        '''
        ReadRegistersRequestBase.__init__(self, address, count, **kwargs)

    def execute(self, context):
        ''' Run a read holding request against a datastore

        :param context: The datastore to request from
        :returns: An initialized response, exception message otherwise
        '''
        # print("ReadHoldingRegistersRequest Slave ID =",self.unit_id)
        if(Master_Controller_Utils.is_tcp_ip == False):
            pass
        # Master_Controller_Utils.Device_Address.value = self.unit_id
        if not (1 <= self.count <= 0x7d):
            return self.doException(merror.IllegalValue)
        if not context.validate(self.function_code, self.address, self.count):
            return self.doException(merror.IllegalAddress)
        values = context.getValues(self.function_code, self.address, self.count)
        return ReadHoldingRegistersResponse(values)

class WriteMultipleRegistersRequest(ModbusRequest):
    '''
    This function code is used to write a block of contiguous registers (1
    to approx. 120 registers) in a remote device.

    The requested written values are specified in the request data field.
    Data is packed as two bytes per register.
    '''
    function_code = 16
    _rtu_byte_count_pos = 6
    _pdu_length = 5  #func + adress1 + adress2 + outputQuant1 + outputQuant2

    def __init__(self, address=None, values=None, **kwargs):
        ''' Initializes a new instance

        :param address: The address to start writing to
        :param values: The values to write
        '''
        ModbusRequest.__init__(self, **kwargs)
        self.address = address
        if values is None:
            values = []
        elif not hasattr(values, '__iter__'):
            values = [values]
        self.values = values
        self.count = len(self.values)
        self.byte_count = self.count * 2

    def encode(self):
        ''' Encode a write single register packet packet request

        :returns: The encoded packet
        '''
        packet = struct.pack('>HHB', self.address, self.count, self.byte_count)
        if self.skip_encode:
            return packet + b''.join(self.values)
        
        for value in self.values:
            packet += struct.pack('>H', value)

        return packet

    def decode(self, data):
        ''' Decode a write single register packet packet request

        :param data: The request to decode
        '''
        self.address, self.count, \
        self.byte_count = struct.unpack('>HHB', data[:5])
        self.values = []  # reset
        for idx in range(5, (self.count * 2) + 5, 2):
            self.values.append(struct.unpack('>H', data[idx:idx + 2])[0])

    def execute(self, context):
        ''' Run a write single register request against a datastore

        :param context: The datastore to request from
        :returns: An initialized response, exception message otherwise
        '''
        # print("WriteMultipleRegistersRequest Slave ID =",self.unit_id)
        if(Master_Controller_Utils.is_tcp_ip == False):
            pass
        # Master_Controller_Utils.Device_Address.value = self.unit_id
        if not (1 <= self.count <= 0x07b):
            return self.doException(merror.IllegalValue)
        if (self.byte_count != self.count * 2):
            return self.doException(merror.IllegalValue)
        if not context.validate(self.function_code, self.address, self.count):
            return self.doException(merror.IllegalAddress)

        context.setValues(self.function_code, self.address, self.values)
        return WriteMultipleRegistersResponse(self.address, self.count)

    def get_response_pdu_size(self):
        """
        Func_code (1 byte) + Starting Address (2 byte) + Quantity of Reggisters  (2 Bytes)
        :return:
        """
        return 1 + 2 + 2

    def __str__(self):
        ''' Returns a string representation of the instance

        :returns: A string representation of the instance
        '''
        params = (self.address, self.count)
        return "WriteMultipleRegisterRequest %d => %d" % params

class WriteMultipleCoilsRequest(ModbusRequest):
    '''
    "This function code is used to force each coil in a sequence of coils to
    either ON or OFF in a remote device. The Request PDU specifies the coil
    references to be forced. Coils are addressed starting at zero. Therefore
    coil numbered 1 is addressed as 0.

    The requested ON/OFF states are specified by contents of the request
    data field. A logical '1' in a bit position of the field requests the
    corresponding output to be ON. A logical '0' requests it to be OFF."
    '''
    function_code = 15
    _rtu_byte_count_pos = 6
    
    def __init__(self, address=None, values=None, **kwargs):
        ''' Initializes a new instance

        :param address: The starting request address
        :param values: The values to write
        '''
        ModbusRequest.__init__(self, **kwargs)
        self.address = address
        if not values: values = []
        elif not hasattr(values, '__iter__'): values = [values]
        self.values  = values
        self.byte_count = (len(self.values) + 7) // 8

    def encode(self):
        ''' Encodes write coils request

        :returns: The byte encoded message
        '''
        count   = len(self.values)
        self.byte_count = (count + 7) // 8
        packet  = struct.pack('>HHB', self.address, count, self.byte_count)
        packet += pack_bitstring(self.values)
        return packet

    def decode(self, data):
        ''' Decodes a write coils request

        :param data: The packet data to decode
        '''
        self.address, count, self.byte_count = struct.unpack('>HHB', data[0:5])
        values = unpack_bitstring(data[5:])
        self.values = values[:count]

    def execute(self, context):
        ''' Run a write coils request against a datastore

        :param context: The datastore to request from
        :returns: The populated response or exception message
        '''
        # print("WriteMultipleCoilsRequest Slave ID =",self.unit_id)
        if(Master_Controller_Utils.is_tcp_ip == False):
            pass
        # Master_Controller_Utils.Device_Address.value = self.unit_id
        count = len(self.values)
        if not (1 <= count <= 0x07b0):
            return self.doException(merror.IllegalValue)
        if (self.byte_count != (count + 7) // 8):
            return self.doException(merror.IllegalValue)
        if not context.validate(self.function_code, self.address, count):
            return self.doException(merror.IllegalAddress)

        context.setValues(self.function_code, self.address, self.values)
        return WriteMultipleCoilsResponse(self.address, count)

    def __str__(self):
        ''' Returns a string representation of the instance

        :returns: A string representation of the instance
        '''
        params = (self.address, len(self.values))
        return "WriteNCoilRequest (%d) => %d " % params

    def get_response_pdu_size(self):
        """
        Func_code (1 byte) + Output Address (2 byte) + Quantity of Outputs  (2 Bytes)
        :return:
        """
        return 1 + 2 + 2


def CONNECT_TO_MASTER(USB_COM = []):
    # print("passed usb", USB_COM)
    Master_Controller_Utils.master_usb.value=''
    USB_COM = []
    if(USB_COM == []):
        pts= prtlst.comports()
        for pt in pts:
            if 'USB' in pt[1]: #check 'USB' string in device description
                USB_COM.append(pt[0])
    Master_Controller_Utils.master_usb_check_list=[]
    current_usb_list=[]
    for i in Master_Controller_Utils.MASTER_USB_LIST:
        current_usb_list.append(i)
    for usb in USB_COM:
        if((Master_Controller_Utils.USB0_COM != usb) or (Master_Controller_Utils.USB0_Status_Flag == False)):
            if(not usb in Master_Controller_Utils.MASTER_USB_LIST):
                Master_Controller_Utils.master_usb_check_list.append(usb)
    
    if(Master_Controller_Utils.master_usb_check_list != []):
        Master_Controller_Utils.Master_search_count=len(Master_Controller_Utils.master_usb_check_flag)
        Master_Controller_Utils.master_usb_check_flag.append(False)
        Master_Controller_Utils.master_usb_check_list_flag=True
        while  Master_Controller_Utils.master_usb_check_list_flag==True and Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False:
            pass
        for usb in Master_Controller_Utils.MASTER_USB_LIST:
            if not usb in current_usb_list:
                print("Master USB is=",usb)
                Master_Controller_Utils.master_detected=True
        if(Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False):
            Master_Controller_Utils.master_usb_check_flag.pop()
        if (len(Master_Controller_Utils.MASTER_USB_LIST) == 0):
            Master_Controller_Utils.Master_search_count = -1
            Master_Controller_Utils.USB_MASTER_CHECK = False
            print("Master is not connected")
            return False

def master_usb_detection_process_rtu(Master_priority1_File_Read_Semaphore,
                    Master_priority2_File_Read_Semaphore,
                    Master_priority3_File_Read_Semaphore,
                    Master_priority4_File_Write_Semaphore,
                    Master_priority1_File_Write_Semaphore,
                    Master_priority2_File_Write_Semaphore,
                    Master_priority3_File_Write_Semaphore,
                    Master_priority4_File_Read_Semaphore,
                    Priority_1_backup_Semaphore,
                    Priority_2_backup_Semaphore,
                    Priority_3_backup_Semaphore,
                    Priority_4_backup_Semaphore,
                    Master_write2_value_dic1,
                    Master_write2_value_dic2,
                    Master_write2_value_dic3,
                    Master_write2_value_dic4,
                    Master_write1_value_dic1,
                    Master_write1_value_dic2,
                    Master_write1_value_dic3,
                    Master_write1_value_dic4,
                    Master_write_value_dic1, 
                    Master_write_value_dic2, 
                    Master_write_value_dic3, 
                    Master_write_value_dic4, 
                    Master_write_count_dic1, 
                    Master_write_count_dic2, 
                    Master_write_count_dic3, 
                    Master_write_count_dic4,
                    USB1_Status_Flag,
                    USB1_COM,
                    all_p_num,
                    priority4_reg_list,
                    Device_Address,
                    Controller_to_master_FileName_Priority1,
                    Controller_to_master_FileName_Priority2,
                    Controller_to_master_FileName_Priority3,
                    Controller_to_master_FileName_Priority4,
                    Master_to_controller_FileName_Priority1,
                    Master_to_controller_FileName_Priority2,
                    Master_to_controller_FileName_Priority3,
                    Master_to_controller_FileName_Priority4,
                    Priority_1_backup,
                    Priority_2_backup,
                    Priority_3_backup,
                    Priority_4_backup,
                    master_usb_check_flag,
                    master_usb,
                    rtu_usb,
                    MASTER_USB_LIST,
                    Master_search_count
                    ):
    Master_Controller_Utils.master_process_init()
    Master_Controller_Utils.is_tcp_ip = False
    Master_Controller_Utils.Master_priority1_File_Read_Semaphore = Master_priority1_File_Read_Semaphore
    Master_Controller_Utils.Master_priority2_File_Read_Semaphore = Master_priority2_File_Read_Semaphore
    Master_Controller_Utils.Master_priority3_File_Read_Semaphore = Master_priority3_File_Read_Semaphore
    Master_Controller_Utils.Master_priority4_File_Write_Semaphore = Master_priority4_File_Write_Semaphore
    Master_Controller_Utils.Master_priority1_File_Write_Semaphore = Master_priority1_File_Write_Semaphore
    Master_Controller_Utils.Master_priority2_File_Write_Semaphore = Master_priority2_File_Write_Semaphore
    Master_Controller_Utils.Master_priority3_File_Write_Semaphore = Master_priority3_File_Write_Semaphore
    Master_Controller_Utils.Master_priority4_File_Read_Semaphore = Master_priority4_File_Read_Semaphore
    Master_Controller_Utils.Priority_1_backup_Semaphore = Priority_1_backup_Semaphore
    Master_Controller_Utils.Priority_2_backup_Semaphore = Priority_2_backup_Semaphore
    Master_Controller_Utils.Priority_3_backup_Semaphore = Priority_3_backup_Semaphore
    Master_Controller_Utils.Priority_4_backup_Semaphore = Priority_4_backup_Semaphore
    Master_Controller_Utils.Master_write2_value_dic1  = Master_write2_value_dic1
    Master_Controller_Utils.Master_write2_value_dic2  = Master_write2_value_dic2
    Master_Controller_Utils.Master_write2_value_dic3  = Master_write2_value_dic3
    Master_Controller_Utils.Master_write2_value_dic4  = Master_write2_value_dic4
    Master_Controller_Utils.Master_write1_value_dic1  = Master_write1_value_dic1
    Master_Controller_Utils.Master_write1_value_dic2  = Master_write1_value_dic2
    Master_Controller_Utils.Master_write1_value_dic3  = Master_write1_value_dic3
    Master_Controller_Utils.Master_write1_value_dic4  = Master_write1_value_dic4
    Master_Controller_Utils.Master_write_value_dic1   = Master_write_value_dic1 
    Master_Controller_Utils.Master_write_value_dic2   = Master_write_value_dic2 
    Master_Controller_Utils.Master_write_value_dic3   = Master_write_value_dic3 
    Master_Controller_Utils.Master_write_value_dic4   = Master_write_value_dic4 
    Master_Controller_Utils.Master_write_count_dic1   = Master_write_count_dic1 
    Master_Controller_Utils.Master_write_count_dic2   = Master_write_count_dic2 
    Master_Controller_Utils.Master_write_count_dic3   = Master_write_count_dic3 
    Master_Controller_Utils.Master_write_count_dic4   = Master_write_count_dic4 
    Master_Controller_Utils.all_p_num = all_p_num
    Master_Controller_Utils.priority4_reg_list = priority4_reg_list 
    Master_Controller_Utils.Device_Address = Device_Address 
    Master_Controller_Utils.Controller_to_master_FileName_Priority1 =Controller_to_master_FileName_Priority1
    Master_Controller_Utils.Controller_to_master_FileName_Priority2 =Controller_to_master_FileName_Priority2
    Master_Controller_Utils.Controller_to_master_FileName_Priority3 =Controller_to_master_FileName_Priority3
    Master_Controller_Utils.Controller_to_master_FileName_Priority4 =Controller_to_master_FileName_Priority4
    Master_Controller_Utils.Master_to_controller_FileName_Priority1 =Master_to_controller_FileName_Priority1
    Master_Controller_Utils.Master_to_controller_FileName_Priority2 =Master_to_controller_FileName_Priority2
    Master_Controller_Utils.Master_to_controller_FileName_Priority3 =Master_to_controller_FileName_Priority3
    Master_Controller_Utils.Master_to_controller_FileName_Priority4 =Master_to_controller_FileName_Priority4
    Master_Controller_Utils.Priority_1_backup=Priority_1_backup
    Master_Controller_Utils.Priority_2_backup=Priority_2_backup
    Master_Controller_Utils.Priority_3_backup=Priority_3_backup
    Master_Controller_Utils.Priority_4_backup=Priority_4_backup
    Master_Controller_Utils.master_usb_check_flag = master_usb_check_flag
    Master_Controller_Utils.master_usb = master_usb
    Master_Controller_Utils.USB_port = rtu_usb
    Master_Controller_Utils.MASTER_USB_LIST = MASTER_USB_LIST
    Master_Controller_Utils.Master_search_count = Master_search_count
    Modbus_CONTEXT_USB_creator()
    master_context_thread_process_2 = Thread(target=Master_context_Thread, args =[rtu_usb,])
    RTU_server_Thread = Thread(target=RTU_USB_THREAD, args =[rtu_usb,])                    #tcpip thread create

    master_context_thread_process_2.start()
    RTU_server_Thread.start()
    

    master_context_thread_process_2.join()
    RTU_server_Thread.join()
   
    while 1:
        pass


def TCPIP_THREAD():
    if(Master_Controller_Utils.modbus_TCPIP_enable == True):
        pass
        while 1:

            # if(Master_Controller_Utils.single_slave== True):
            #     context = ModbusServerContext(slaves=Master_Controller_Utils.slaves, single=False) 
            # if(Master_Controller_Utils.single_slave== False):
            #     context = ModbusServerContext(slaves=Master_Controller_Utils.slaves, single=True)
            context = ModbusServerContext(slaves=Master_Controller_Utils.slaves, single=True)


            # context = ModbusServerContext(slaves=Master_Controller_Utils.slaves, single=True) # all slaves
            # context = ModbusServerContext(slaves=Master_Controller_Utils.slaves, single=False) # single save
            # context = ModbusServerContext(slaves=Master_Controller_Utils.slaves.values(), single=True)
            # print(context)
            # ----------------------------------------------------------------------- # 
            # initialize the server information
            # ----------------------------------------------------------------------- # 
            identity = ModbusDeviceIdentification()
            identity.VendorName = 'pymodbus'
            identity.ProductCode = 'PM'
            identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
            identity.ProductName = 'pymodbus Server'
            identity.ModelName = 'pymodbus Server'
            identity.MajorMinorRevision = '2.3.0'
            # ----------------------------------------------------------------------- # 
            # run the server you want
            # ----------------------------------------------------------------------- # 
            print("StartTcpServer")
            StartTcpServer(
                context=context,
                identity=identity,
                address=("0.0.0.0", 5020),
                custom_functions=[ReadHoldingRegistersRequest,ReadCoilsRequest,WriteMultipleRegistersRequest,WriteMultipleCoilsRequest]
                # address=("localhost", 5020)
            )
            pass
            print("TCP server stopped")

# def stop(port):
#     while(1):
#         try:
#             USB_COM = []
#             pts= prtlst.comports()
#             for pt in pts:
#                 if 'USB' in pt[1]: #check 'USB' string in device description
#                     USB_COM.append(pt[0])
#             # print("Present USB =",USB_COM)
#             if((not port in USB_COM)):
#                 pass
#                 # print('Process will be down.')
#                 StopServer()  # Stop server.
#                 break
#         except:
#             pass
            
def stop_usb_check(port):
    global USB0_COM
    timout_counter = 0
    start_time = int(round(time.time()*1000))
    end_time = int(round(time.time()*1000))
    while(1):

        try:
            USB_COM = []
            pts= prtlst.comports()
            for pt in pts:
                if 'USB' in pt[1]: #check 'USB' string in device description
                    USB_COM.append(pt[0])
            # print("Present USB =",USB_COM)
            end_time = int(round(time.time()*1000))
            if(((not port in USB_COM) or ((Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == True)  and (Master_Controller_Utils.USB_found == False)) or (False and ((Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False) and (Master_Controller_Utils.USB_found == False))))or(not Master_Controller_Utils.USB0_COM in USB_COM)):
            # if(((not port in USB_COM) or ((Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == True)  and (Master_Controller_Utils.USB_found == False)) or (((end_time-start_time) > 30000) and ((Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False) and (Master_Controller_Utils.USB_found == False))))or(not Master_Controller_Utils.USB0_COM in USB_COM)):
            # if(((not port in USB_COM) or ((Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == True)  and (Master_Controller_Utils.USB_found == False)) or (((Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False) and (Master_Controller_Utils.USB_found == False))))or(not Master_Controller_Utils.USB0_COM in USB_COM)):
                # StopServer()  # Stop server.
                Master_Controller_Utils.stop_master_usb = True
                break
        except:
            pass
 
def RTU_USB_THREAD(USB):
    # if(Master_Controller_Utils.modbus_RTU_enable == True):
    while Master_Controller_Utils.Process_exit_flag == False:

        # client_extra = ModbusSerialClient(method='rtu', port=USB, baudrate=9600, timeout=0.1, parity='N', stopbits=1, bytesize=8)
        if(Master_Controller_Utils.single_slave== True):
            context = ModbusServerContext(slaves=Master_Controller_Utils.slaves, single=False) #single slave
        elif(Master_Controller_Utils.single_slave== False):
            context = ModbusServerContext(slaves=Master_Controller_Utils.slaves, single=True)  #all slaves
        # print(context) 
        # ----------------------------------------------------------------------- # 
        # initialize the server information
        # ----------------------------------------------------------------------- # 
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'pymodbus'
        identity.ProductCode = 'PM'
        identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
        identity.ProductName = 'pymodbus Server'
        identity.ModelName = 'pymodbus Server'
        identity.MajorMinorRevision = '2.3.0'

        # ----------------------------------------------------------------------- # 
        # run the server you want
        # ----------------------------------------------------------------------- # 
        # time = 5  # 5 seconds delay
        # loop = LoopingCall(f=updating_writer, a=(context,))
        # loop.start(time, now=False) # initially delay by time
        # ----------------------------------------------------------------------- # 
        # p=Process(target = RTU_PROCESS, args=(context,identity,Master_Controller_Utils.USB1_COM.value, ))
        # p.start()
        # p.join()

        from twisted.internet import reactor
        stop_thread = Thread(target=stop_usb_check, args=(USB,))
        # usb_thread = Thread(target=Master_usb, args=(Master_Controller_Utils.USB1_COM.value,))
        stop_thread.start()
        # usb_thread.start()
        #########################################################################################################################
        # print("USB detection StartSerialServer", USB)
        # # print('Start an async server.')
        # try:
        #     StartSerialServer(
        #         context=context,
        #         framer=ModbusRtuFramer,
        #         identity=identity,
        #         port=USB,
        #         # timeout=0.0001,
        #         timeout=0.075,
        #         baudrate=9600,
        #         #baudrate=38400,
        #         parity='N',
        #         bytesize=8,
        #         stopbits=1,
        #         custom_functions=[ReadHoldingRegistersRequest,ReadCoilsRequest,WriteMultipleRegistersRequest,WriteMultipleCoilsRequest],
        #         defer_reactor_run=False,
        #         ignore_missing_slaves=False)
        # except Exception as e:
        #     print("Printing error-",e)
        ##########################################################################################################################
        #usb detection tag 1
        ##########################################################################################################################

        # ##########################################################################################################################
        ser = serial.Serial(port=USB, baudrate=9600)
        while True:
            count=0
            Rem_byte_len=0
            ser.flushInput()
            while (True):
                if ser.in_waiting > 0:
                    # # sleep(0.010)
                    # arr =[]
                    # while(ser.in_waiting!=0):
                    #     arr.append(list(ser.read(ser.in_waiting)))
                    #     sleep(0.02)
                    
                    # print(arr)
                    

                    # sleep(0.010)
                    arr =[]
                    count = 0
                    while(ser.in_waiting!=0):
                        arr += (ser.read(ser.in_waiting))
                        sleep(0.02)
                        count+=1
                    if(count >= 2):
                        # print("repeated",count)
                        pass
                    else:
                        pass
                    data=list(arr) 
                    # data=ModbusRtuFramer.get_payload(arr)
                    # print(data) 
                    time_start= int(round(TIME()*1000))
                    if(data[0]== Master_Controller_Utils.Device_Address.value):       
                        if(data[1]== 1 or data[1]== 2 or data[1]== 3 or data[1]== 4 or data[1]== 5 or data[1]== 6):
                            Data_rec_len=len(data)
                            Rem_byte_len=8-Data_rec_len
                            if(Data_rec_len>=4):
                                Reg_add=((data[2]<<8)|(data[3]))
                            if(Data_rec_len>=6):
                                Reg_rd_count=((data[4]<<8)|(data[5]))
                            try:
                                Rec_crc=hex((data[6]<<8)|(data[7]))
                                crc_data=data
                                crc_data.pop()
                                crc_data.pop()
                                crc_1=crc_modbus(crc_data)
                                if(Rec_crc == crc_1):
                                    # print(data)
                                    if(data[1]== 1):
                                        # print(Master_Controller_Utils.block_hr.getValuesInternal(address=Reg_add, count=Reg_rd_count))
                                        # print(Master_Controller_Utils.block_cr.getValuesInternal(Reg_add, 1))
                                        coil_values=Master_Controller_Utils.block_cr.getValuesExternal(address=Reg_add, count=Reg_rd_count)
                                        # print(coil_values)
                                        builder_binary = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big, repack=False)
                                        builder_binary.add_bits(coil_values)
                                        payload = builder_binary.to_registers()
                                        # print(payload)
                                        payload_list=[]
                                        for i in payload:
                                            payload_list.append(((i & 0XFF00)>>8))
                                            if((i & 0X00FF) != 0):
                                                payload_list.append((i & 0X00FF ))
                                        # print(payload_list)
                                        send_buffer=[data[0],data[1],len(payload_list)]
                                        send_buffer=send_buffer+payload_list
                                        if(Master_Controller_Utils.Print_Enable == True):
                                            print(send_buffer)
                                        # send(ser,send_buffer)
                                        crc_1=crc_modbus_non_hex(send_buffer)
                                        send_buffer.append(((crc_1) & 0xFF00)>>8)
                                        send_buffer.append((crc_1) & 0x00FF)
                                        ser.write(send_buffer)

                                        pass
                                    elif(data[1]== 3):
                                        int_value = Master_Controller_Utils.block_hr.getValuesExternal(address=Reg_add, count=Reg_rd_count )
                                        # print(int_value)

                                        send_buffer=[data[0],data[1],(Reg_rd_count*2)]
                                        int_value_list=[]
                                        for value_data in int_value:
                                            int_value_list.append((value_data & 0xFF00)>>8)  
                                            int_value_list.append(value_data & 0x00FF)  

                                        # # Convert 16-bit values to 8-bit values
                                        # int_value_list = [(value & 0xFF, (value >> 8) & 0xFF) for value in int_value]
                                        # # Flatten the list
                                        # int_value_list = [(byte) for pair in int_value_list for byte in pair]
                                        send_buffer=send_buffer+int_value_list
                                        if(Master_Controller_Utils.Print_Enable == True):
                                            print(send_buffer) 
                                        send(ser,send_buffer)
                                        # crc_1=crc_modbus_non_hex(send_buffer)
                                        # # print(crc_1)
                                        # send_buffer.append(((crc_1) & 0xFF00)>>8)
                                        # send_buffer.append((crc_1) & 0x00FF)
                                        # # print(send_buffer)
                                        # # sleep(0.01)
                                        # ser.write(send_buffer)
                                        time_end= int(round(TIME()*1000))
                                        if(Master_Controller_Utils.Print_Enable == True):
                                            print("time take to complete one frame",time_end-time_start)
                                        # int_value_class=CustomDataBlock_int()
                                        # int_value=int_value_class.getValues(address=Reg_add, count=Reg_rd_count )
                                        # print("response of fc=3 ^")
                                        pass
                                    elif(data[1]== 5):
                                        reg_value1 = False
                                        if(Reg_rd_count== 0xFF00):
                                            reg_value1 = True
                                            Master_Controller_Utils.block_cr.setValuesExternal(Reg_add,[reg_value1])
                                        elif(Reg_rd_count == 0x0000):
                                            reg_value1 = False
                                            Master_Controller_Utils.block_cr.setValuesExternal(Reg_add,[reg_value1])

                                        # Master_Controller_Utils.block_cr.setValues(Reg_add,reg_value1)
                                        send(ser,data)
                                        # ser.write(data)
                                    elif(data[1]== 6):
                                        try:
                                            hr_reg_value1=[]
                                            hr_reg_value1.append(Reg_rd_count)
                                            Master_Controller_Utils.block_hr.setValuesExternal(Reg_add,hr_reg_value1)
                                            send(ser,data)
                                        except Exception as e:
                                            print(e)

                                    print("requesting : Slave_address=",data[0] ,"function_code=",data[1],"address=",Reg_add, "count=",Reg_rd_count)
                                else:
                                    pass
                            except Exception as e:
                                print(e)
                                print("response from the other sem")
                                # if(data[1]== 1 or data[1]== 2 or data[1]== 3 or data[1]== 4):
                                #     resp_len=data[2]
                                #     Rec_crc=hex((data[3+resp_len]<<8)|(data[4+resp_len]))
                                #     crc_data=data
                                #     crc_data.pop()
                                #     crc_data.pop()
                                #     crc_1=crc_modbus(crc_data)
                                #     if(Rec_crc == crc_1):
                                #         print(data)
                                #         print("requesting : Slave_address=",data[0] ,"function_code=",data[1],"data_next_bytes=",resp_len, "data=", [crc_data[x] for x in range(len(crc_data)) if ((x > 2) )])
                                        # pass
                                # print(" Exception Requesting to read ",e)
                        
                        elif(data[1] == 15 or data[1] == 16 ):
                            rec_payload=[]
                            Data_rec_len=len(data)
                            Rem_byte_len=8-Data_rec_len
                            if(Data_rec_len>=4):
                                Reg_add=((data[2]<<8)|(data[3]))
                            if(Data_rec_len>=6):
                                Reg_rd_count=((data[4]<<8)|(data[5]))
                            # Rem_byte_len=(data[6])
                            # Data_rec_len=len(data)
                            # print("function_code=",data[1])
                            # if(Data_rec_len>=3):
                            # Reg_add=((data[2]<<8)|(data[3]))
                            # Reg_rd_count=((data[4]<<8)|(data[5]))
                            # if(Data_rec_len>=5):
                            # Num_reg_wrt=((data[4]<<8)|(data[5]))
                            # Num_data_byte=(data[6])
                            Rec_crc=hex((data[8+data[6]-1]<<8)|(data[8+data[6]]))
                            crc_data=data[:-2]
                            crc_1=crc_modbus(crc_data)
                            if(Rec_crc == crc_1):
                                # print("requesting : Slave_address=",data[0] ,"function_code=",data[1],"address=",Reg_add, "count=",Num_reg_wrt )
                                if(data[1] == 16):
                                    count = 7
                                    # rec_payload=[]
                                    for i in range( int((len(data) - 9)/2)):
                                        # fo
                                        rec_payload.append(data[count]<<8 | data[count+1])
                                        count+=2
                                    # rec_payload=data[7:-2]
                                    Master_Controller_Utils.block_hr.setValuesExternal(Reg_add,rec_payload)
                                    send_buffer=data[:6]
                                    send(ser,send_buffer)
                                    # # send_buffer=[data[0],data[1],data[2],data[3],data[4],data[5]]
                                    # crc_1=crc_modbus_non_hex(send_buffer)
                                    # send_buffer.append(((crc_1) & 0xFF00)>>8)
                                    # send_buffer.append((crc_1) & 0x00FF)
                                    # ser.write(send_buffer)
                                # print("requesting : Slave_address=",data[0] ,"function_code=",data[1],"address=",Reg_add, "count=",Num_reg_wrt)
                                elif(data[1] == 15 ):
                                    hex_list=[]
                                    count=0
                                    for i in range(len(data)):
                                        if((i>6) and ( i > (6+data[6]))):
                                            hex_list.append(data[i])
                                            count+=1
                                    val=rev_value_num(hex_list,Reg_rd_count)
                                    Master_Controller_Utils.block_cr.setValuesExternal(Reg_add,val)
                                    send_buffer=data[:6]
                                    send(ser,send_buffer)
                            else:
                                pass
                sleep(0.02)  
                if(Master_Controller_Utils.stop_master_usb == True):
                    break
            if(Master_Controller_Utils.stop_master_usb == True):
                    break
            sleep(0.05)
        #########################################################################################################################
        print('USB detection Server was stopped.',USB)

        Master_Controller_Utils.Process_exit_flag = True 
        try:
            print(Master_Controller_Utils.MASTER_USB_LIST )
            Master_Controller_Utils.MASTER_USB_LIST.remove(USB)
        except Exception as e:
            print("Server was stopped error",e)
        Master_Controller_Utils.USB0_Status_Flag = False
        pid = os.getpid()
        os.kill(pid,SIGKILL)
        print("RTU server stopped")
        Master_Controller_Utils.stop_master_usb = False
        time.sleep(0.5)


class CustomDataBlock_bool(ModbusSparseDataBlock):
    def setValues(self, address, value):
        super(CustomDataBlock_bool, self).setValues(address, value)
        Master_Controller_Utils.USB_found = True
        count = 0
        extra_par_found = False
        for parameter_number in range(address,address+len(value)):
            if not parameter_number in Master_Controller_Utils.all_p_num:
                if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) and parameter_number != 65535 ):
                # if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) ):
                    Master_Controller_Utils.Extra_par_flag = True
                    extra_par_found = True
                    value_bool = "False"
                    Master_Controller_Utils.all_p_num.append(parameter_number)
                    Master_Controller_Utils.priority4_reg_list.append(parameter_number)
                    Master_Controller_Utils.Protity1_parameter_count+=1
                    if(True == value[count]):
                        value_bool = "True"
                    elif(False == value[count]):
                        value_bool = "False"
                    int_dictionary={
                        "reg_num": parameter_number,
                        "reg_name": ("extra_parameter_"+str(Master_Controller_Utils.Protity1_parameter_count)),
                        "type": "bool",
                        "value": value_bool,
                        "Access_type": "Read_Write"
                        }
                    Master_Controller_Utils.new_list.append(int_dictionary)
                    Master_Controller_Utils.new_write_list.append(parameter_number)

            else:
                new_dictinoary={}
                new_dictinoary[parameter_number]=value[count]
                Master_Controller_Utils.bool_parameter_dictionary.update(new_dictinoary)
            count+=1
        print("E2_req.", end='')
        # print("boolian written wrote {} to {}".format(value, address))
        if(extra_par_found == True):
            Master_Controller_Utils.Extra_par_flag = False


    def getValues(self, address, count=1):
        extra_par_found = False
        for parameter_number in range(address,address+count):
            if not parameter_number in Master_Controller_Utils.all_p_num:
                if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) and parameter_number != 65535 ):
                # if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True)):
                    Master_Controller_Utils.Extra_par_flag = True
                    extra_par_found = True
                    Master_Controller_Utils.all_p_num.append(parameter_number)
                    Master_Controller_Utils.priority4_reg_list.append(parameter_number)
                    Master_Controller_Utils.Protity1_parameter_count+=1
                    # Decoder = BinaryPayloadDecoder.fromRegisters([parameter_value],byteorder=Endian.Big, wordorder=Endian.Big)
                    int_dictionary={
                        "reg_num": parameter_number,
                        "reg_name": ("extra_parameter_"+str(Master_Controller_Utils.Protity1_parameter_count)),
                        "type": "bool",
                        "value": "False",
                        "Access_type": "Read_Write"
                        }
                    Master_Controller_Utils.new_list.append(int_dictionary)
        if(extra_par_found == True):
            Master_Controller_Utils.Extra_par_flag = False
        print("E2_req.", end='')
        Master_Controller_Utils.USB_found = True
        return super(CustomDataBlock_bool, self).getValues(address, count)

    def setValuesInternal(self, address, value):
        ModbusSparseDataBlock.setValues(self, address, value)
        
    def getValuesInternal(self, address, count=1):
        return ModbusSparseDataBlock.getValues(self, address, count)

class CustomDataBlock_int(ModbusSparseDataBlock):
    def setValues(self, address, value):
        super(CustomDataBlock_int, self).setValues(address, value)
        Master_Controller_Utils.USB_found = True
        count = 0
        extra_par_found = False
        for parameter_number in range(address,address+len(value)):
            if not parameter_number in Master_Controller_Utils.all_p_num:
                if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) and parameter_number != 65535 ):
                # if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) ):
                    Master_Controller_Utils.Extra_par_flag = True
                    extra_par_found = True
                    Master_Controller_Utils.all_p_num.append(parameter_number)
                    Master_Controller_Utils.priority4_reg_list.append(parameter_number)
                    Master_Controller_Utils.Protity1_parameter_count+=1
                    Decoder = BinaryPayloadDecoder.fromRegisters([value[count]],byteorder=Endian.Big, wordorder=Endian.Big)
                    int_dictionary={
                        "reg_num": parameter_number,
                        "reg_name": ("extra_parameter_"+str(Master_Controller_Utils.Protity1_parameter_count)),
                        "type": "integer",
                        "value": Decoder.decode_16bit_int(),
                        "Access_type": "Read_Write",
                        "factor": 1,
                        "offset": 0
                        }
                    Master_Controller_Utils.new_list.append(int_dictionary)
                    Master_Controller_Utils.new_write_list.append(parameter_number)

            else:
                new_dictinoary={}
                new_dictinoary[parameter_number]=value[count]
                Master_Controller_Utils.int_parameter_dictionary.update(new_dictinoary)
            count+=1
        print("E2_req.", end='')
        # print("integer written wrote {} to {}".format(value, address))
        if(extra_par_found == True):
            Master_Controller_Utils.Extra_par_flag = False

    def getValues(self, address, count=1):
        extra_par_found = False
        for parameter_number in range(address,address+count):
            if not parameter_number in Master_Controller_Utils.all_p_num:
                if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True)  and parameter_number != 65535 ):
                # if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True)   ):
                    Master_Controller_Utils.Extra_par_flag = True
                    extra_par_found = True
                    Master_Controller_Utils.all_p_num.append(parameter_number)
                    Master_Controller_Utils.priority4_reg_list.append(parameter_number)
                    Master_Controller_Utils.Protity1_parameter_count+=1
                    # Decoder = BinaryPayloadDecoder.fromRegisters([parameter_value],byteorder=Endian.Big, wordorder=Endian.Big)
                    int_dictionary={
                        "reg_num": parameter_number,
                        "reg_name": ("extra_parameter_"+str(Master_Controller_Utils.Protity1_parameter_count)),
                        "type": "integer",
                        "value": 0,
                        "Access_type": "Read_Write",
                        "factor": 1,
                        "offset": 0
                        }
                    Master_Controller_Utils.new_list.append(int_dictionary)
        if(extra_par_found == True):
            Master_Controller_Utils.Extra_par_flag = False
        print("E2_req.", end='')
        Master_Controller_Utils.USB_found = True
        return super(CustomDataBlock_int, self).getValues(address, count)
    def setValuesInternal(self, address, value):
        ModbusSparseDataBlock.setValues(self, address, value)
        
    def getValuesInternal(self, address, count=1):
        return ModbusSparseDataBlock.getValues(self, address, count)

class CustomDataBlock_USB_bool(ModbusSparseDataBlock):
    def setValues(self, address, value):
        super(CustomDataBlock_USB_bool, self).setValues(address, value)
        if((not Master_Controller_Utils.USB_port in Master_Controller_Utils.MASTER_USB_LIST) and (Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False)):
            # print("new master added")
            Master_Controller_Utils.MASTER_USB_LIST.append(Master_Controller_Utils.USB_port)
        # Master_Controller_Utils.master_usb.value = Master_Controller_Utils.USB_port
        if(Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False):
            Master_Controller_Utils.USB_found = True
        count = 0
        extra_par_found = False
        for parameter_number in range(address,address+len(value)):
            if not parameter_number in Master_Controller_Utils.all_p_num:
                if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) and parameter_number != 65535 ):
                # if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True)  ):
                    Master_Controller_Utils.Extra_par_flag = True
                    extra_par_found = True
                    value_bool = "False"
                    Master_Controller_Utils.all_p_num.append(parameter_number)
                    Master_Controller_Utils.priority4_reg_list.append(parameter_number)
                    Master_Controller_Utils.Protity1_parameter_count+=1
                    if(True == value[count]):
                        value_bool = "True"
                    elif(False == value[count]):
                        value_bool = "False"
                    int_dictionary={
                        "reg_num": parameter_number,
                        "reg_name": ("extra_parameter_"+str(Master_Controller_Utils.Protity1_parameter_count)),
                        "type": "bool",
                        "value": value_bool,
                        "Access_type": "Read_Write",
                        }
                    Master_Controller_Utils.new_list.append(int_dictionary)
                    Master_Controller_Utils.new_write_list.append(parameter_number)

            else:
                new_dictinoary={}
                new_dictinoary[parameter_number]=value[count]
                Master_Controller_Utils.bool_parameter_dictionary.update(new_dictinoary)
            count+=1
        print("E2_req.", end='')
        # print("boolian written wrote {} to {}".format(value, address))
        if(extra_par_found == True):
            Master_Controller_Utils.Extra_par_flag = False


    def getValues(self, address, count=1):
        extra_par_found = False
        for parameter_number in range(address,address+count):
            if not parameter_number in Master_Controller_Utils.all_p_num:
                if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) and parameter_number != 65535 ):
                # if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) ):
                    Master_Controller_Utils.Extra_par_flag = True
                    extra_par_found = True
                    Master_Controller_Utils.all_p_num.append(parameter_number)
                    Master_Controller_Utils.priority4_reg_list.append(parameter_number)
                    Master_Controller_Utils.Protity1_parameter_count+=1
                    # Decoder = BinaryPayloadDecoder.fromRegisters([parameter_value],byteorder=Endian.Big, wordorder=Endian.Big)
                    int_dictionary={
                        "reg_num": parameter_number,
                        "reg_name": ("extra_parameter_"+str(Master_Controller_Utils.Protity1_parameter_count)),
                        "type": "bool",
                        "value": "False",
                        "Access_type": "Read_Write"
                        }
                    Master_Controller_Utils.new_list.append(int_dictionary)
        if(extra_par_found == True):
            Master_Controller_Utils.Extra_par_flag = False
        print("E2_req.", end='')
        if((not Master_Controller_Utils.USB_port in Master_Controller_Utils.MASTER_USB_LIST) and (Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False)):
            # print("new master added")
            Master_Controller_Utils.MASTER_USB_LIST.append(Master_Controller_Utils.USB_port)
        # Master_Controller_Utils.master_usb.value = Master_Controller_Utils.USB_port
        if(Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False):
            Master_Controller_Utils.USB_found = True
        return super(CustomDataBlock_USB_bool, self).getValues(address, count)

    def setValuesInternal(self, address, value):
        ModbusSparseDataBlock.setValues(self, address, value)
        
    def getValuesInternal(self, address, count=1):
        return ModbusSparseDataBlock.getValues(self, address, count)
    
    def setValuesExternal(self, address, value):
        print("setValuesExternal e2: ",address, value)
        ModbusSparseDataBlock.setValues(self, address, value)
        if((not Master_Controller_Utils.USB_port in Master_Controller_Utils.MASTER_USB_LIST) and (Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False)):
            # print("new master added")
            Master_Controller_Utils.MASTER_USB_LIST.append(Master_Controller_Utils.USB_port)
        # Master_Controller_Utils.master_usb.value = Master_Controller_Utils.USB_port
        if(Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False):
            Master_Controller_Utils.USB_found = True
        count = 0
        extra_par_found = False
        for parameter_number in range(address,address+len(value)):
            if not parameter_number in Master_Controller_Utils.all_p_num:
                if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) and parameter_number != 65535 ):
                # if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True)  ):
                    Master_Controller_Utils.Extra_par_flag = True
                    extra_par_found = True
                    value_bool = "False"
                    Master_Controller_Utils.all_p_num.append(parameter_number)
                    Master_Controller_Utils.priority4_reg_list.append(parameter_number)
                    Master_Controller_Utils.Protity1_parameter_count+=1
                    if(True == value[count]):
                        value_bool = "True"
                    elif(False == value[count]):
                        value_bool = "False"
                    int_dictionary={
                        "reg_num": parameter_number,
                        "reg_name": ("extra_parameter_"+str(Master_Controller_Utils.Protity1_parameter_count)),
                        "type": "bool",
                        "value": value_bool,
                        "Access_type": "Read_Write",
                        }
                    Master_Controller_Utils.new_list.append(int_dictionary)
                    Master_Controller_Utils.new_write_list.append(parameter_number)

            else:
                new_dictinoary={}
                new_dictinoary[parameter_number]=value[count]
                Master_Controller_Utils.bool_parameter_dictionary.update(new_dictinoary)
            count+=1
        print("E2_req.", end='')
        # print("boolian written wrote {} to {}".format(value, address))
        if(extra_par_found == True):
            Master_Controller_Utils.Extra_par_flag = False


    def getValuesExternal(self, address, count=1):
        print("getValuesExternal e2: ",address, count)
        extra_par_found = False
        for parameter_number in range(address,address+count):
            if not parameter_number in Master_Controller_Utils.all_p_num:
                if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) and parameter_number != 65535 ):
                # if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) ):
                    Master_Controller_Utils.Extra_par_flag = True
                    extra_par_found = True
                    Master_Controller_Utils.all_p_num.append(parameter_number)
                    Master_Controller_Utils.priority4_reg_list.append(parameter_number)
                    Master_Controller_Utils.Protity1_parameter_count+=1
                    # Decoder = BinaryPayloadDecoder.fromRegisters([parameter_value],byteorder=Endian.Big, wordorder=Endian.Big)
                    int_dictionary={
                        "reg_num": parameter_number,
                        "reg_name": ("extra_parameter_"+str(Master_Controller_Utils.Protity1_parameter_count)),
                        "type": "bool",
                        "value": "False",
                        "Access_type": "Read_Write"
                        }
                    Master_Controller_Utils.new_list.append(int_dictionary)
        if(extra_par_found == True):
            Master_Controller_Utils.Extra_par_flag = False
        print("E2_req.", end='')
        if((not Master_Controller_Utils.USB_port in Master_Controller_Utils.MASTER_USB_LIST) and (Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False)):
            # print("new master added")
            Master_Controller_Utils.MASTER_USB_LIST.append(Master_Controller_Utils.USB_port)
        # Master_Controller_Utils.master_usb.value = Master_Controller_Utils.USB_port
        if(Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False):
            Master_Controller_Utils.USB_found = True
        return ModbusSparseDataBlock.getValues(self, address, count)

class CustomDataBlock_USB_int(ModbusSparseDataBlock):
    def setValues(self, address, value):
        super(CustomDataBlock_USB_int, self).setValues(address, value)
        if((not Master_Controller_Utils.USB_port in Master_Controller_Utils.MASTER_USB_LIST) and (Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False)):
            # print("new master added")
            Master_Controller_Utils.MASTER_USB_LIST.append(Master_Controller_Utils.USB_port)
        # Master_Controller_Utils.master_usb.value = Master_Controller_Utils.USB_port
        if(Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False):
            Master_Controller_Utils.USB_found = True
        count = 0
        extra_par_found = False
        for parameter_number in range(address,address+len(value)):
            if not parameter_number in Master_Controller_Utils.all_p_num:
                if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True )and parameter_number != 65535 ):
                # if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True )):
                    Master_Controller_Utils.Extra_par_flag = True
                    extra_par_found = True
                    Master_Controller_Utils.all_p_num.append(parameter_number)
                    Master_Controller_Utils.priority4_reg_list.append(parameter_number)
                    Master_Controller_Utils.Protity1_parameter_count+=1
                    Decoder = BinaryPayloadDecoder.fromRegisters([value[count]],byteorder=Endian.Big, wordorder=Endian.Big)
                    int_dictionary={
                        "reg_num": parameter_number,
                        "reg_name": ("extra_parameter_"+str(Master_Controller_Utils.Protity1_parameter_count)),
                        "type": "integer",
                        "value": Decoder.decode_16bit_int(),
                        "Access_type": "Read_Write",
                        "factor": 1,
                        "offset": 0
                        }
                    Master_Controller_Utils.new_list.append(int_dictionary)
                    Master_Controller_Utils.new_write_list.append(parameter_number)

            else:
                new_dictinoary={}
                new_dictinoary[parameter_number]=value[count]
                Master_Controller_Utils.int_parameter_dictionary.update(new_dictinoary)
            count+=1
        print("E2_req.", end='')
        # print("integer written wrote {} to {}".format(value, address))
        if(extra_par_found == True):
            Master_Controller_Utils.Extra_par_flag = False

    def getValues(self, address, count=1):
        extra_par_found = False
        # print("started read")
        for parameter_number in range(address,address+count):
            if not parameter_number in Master_Controller_Utils.all_p_num:
                if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) and parameter_number != 65535 ):
                # if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) ):
                    Master_Controller_Utils.Extra_par_flag = True
                    extra_par_found = True
                    Master_Controller_Utils.all_p_num.append(parameter_number)
                    Master_Controller_Utils.priority4_reg_list.append(parameter_number)
                    Master_Controller_Utils.Protity1_parameter_count+=1
                    # Decoder = BinaryPayloadDecoder.fromRegisters([parameter_value],byteorder=Endian.Big, wordorder=Endian.Big)
                    int_dictionary={
                        "reg_num": parameter_number,
                        "reg_name": ("extra_parameter_"+str(Master_Controller_Utils.Protity1_parameter_count)),
                        "type": "integer",
                        "value": 0,
                        "Access_type": "Read_Write",
                        "factor": 1,
                        "offset": 0
                        }
                    Master_Controller_Utils.new_list.append(int_dictionary)
        if(extra_par_found == True):
            Master_Controller_Utils.Extra_par_flag = False
        print("E2_req.", end='')
        if((not Master_Controller_Utils.USB_port in Master_Controller_Utils.MASTER_USB_LIST) and (Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False)):
            # print("new master added")
            Master_Controller_Utils.MASTER_USB_LIST.append(Master_Controller_Utils.USB_port)
        # Master_Controller_Utils.master_usb.value = Master_Controller_Utils.USB_port
        if(Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False):
            Master_Controller_Utils.USB_found = True
        # print("started read 1")
        return super(CustomDataBlock_USB_int, self).getValues(address, count)
    
    def setValuesInternal(self, address, value):
        ModbusSparseDataBlock.setValues(self, address, value)
        
    def getValuesInternal(self, address, count=1):
        return ModbusSparseDataBlock.getValues(self, address, count)

    def setValuesExternal(self, address, value):
        ModbusSparseDataBlock.setValues(self, address, value)
        if((not Master_Controller_Utils.USB_port in Master_Controller_Utils.MASTER_USB_LIST) and (Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False)):
            # print("new master added")
            Master_Controller_Utils.MASTER_USB_LIST.append(Master_Controller_Utils.USB_port)
        # Master_Controller_Utils.master_usb.value = Master_Controller_Utils.USB_port
        if(Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False):
            Master_Controller_Utils.USB_found = True
        count = 0
        extra_par_found = False
        for parameter_number in range(address,address+len(value)):
            if not parameter_number in Master_Controller_Utils.all_p_num:
                if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True )and parameter_number != 65535 ):
                # if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True )):
                    Master_Controller_Utils.Extra_par_flag = True
                    extra_par_found = True
                    Master_Controller_Utils.all_p_num.append(parameter_number)
                    Master_Controller_Utils.priority4_reg_list.append(parameter_number)
                    Master_Controller_Utils.Protity1_parameter_count+=1
                    Decoder = BinaryPayloadDecoder.fromRegisters([value[count]],byteorder=Endian.Big, wordorder=Endian.Big)
                    int_dictionary={
                        "reg_num": parameter_number,
                        "reg_name": ("extra_parameter_"+str(Master_Controller_Utils.Protity1_parameter_count)),
                        "type": "integer",
                        "value": Decoder.decode_16bit_int(),
                        "Access_type": "Read_Write",
                        "factor": 1,
                        "offset": 0
                        }
                    Master_Controller_Utils.new_list.append(int_dictionary)
                    Master_Controller_Utils.new_write_list.append(parameter_number)

            else:
                new_dictinoary={}
                new_dictinoary[parameter_number]=value[count]
                Master_Controller_Utils.int_parameter_dictionary.update(new_dictinoary)
            count+=1
        print("E2_req.", end='')
        # print("integer written wrote {} to {}".format(value, address))
        if(extra_par_found == True):
            Master_Controller_Utils.Extra_par_flag = False

    def getValuesExternal(self, address, count=1):
        extra_par_found = False
        # print("started read")
        for parameter_number in range(address,address+count):
            if not parameter_number in Master_Controller_Utils.all_p_num:
                if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) and parameter_number != 65535 ):
                # if((Master_Controller_Utils.Extra_par_flag == False or extra_par_found == True) ):
                    Master_Controller_Utils.Extra_par_flag = True
                    extra_par_found = True
                    Master_Controller_Utils.all_p_num.append(parameter_number)
                    Master_Controller_Utils.priority4_reg_list.append(parameter_number)
                    Master_Controller_Utils.Protity1_parameter_count+=1
                    # Decoder = BinaryPayloadDecoder.fromRegisters([parameter_value],byteorder=Endian.Big, wordorder=Endian.Big)
                    int_dictionary={
                        "reg_num": parameter_number,
                        "reg_name": ("extra_parameter_"+str(Master_Controller_Utils.Protity1_parameter_count)),
                        "type": "integer",
                        "value": 0,
                        "Access_type": "Read_Write",
                        "factor": 1,
                        "offset": 0
                        }
                    Master_Controller_Utils.new_list.append(int_dictionary)
        if(extra_par_found == True):
            Master_Controller_Utils.Extra_par_flag = False
        print("E2_req.", end='')
        if((not Master_Controller_Utils.USB_port in Master_Controller_Utils.MASTER_USB_LIST) and (Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False)):
            # print("new master added")
            Master_Controller_Utils.MASTER_USB_LIST.append(Master_Controller_Utils.USB_port)
        # Master_Controller_Utils.master_usb.value = Master_Controller_Utils.USB_port
        if(Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] == False):
            Master_Controller_Utils.USB_found = True
        # print("started read 1")
        return ModbusSparseDataBlock.getValues(self, address, count)
    
def rev_value_num(hex_list,count):
    val_1=[]
    for hex_value in hex_list:
        # Convert to binary with leading zeros
        binary_value = format(hex_value, '08b')
        # Reverse the binary representation and convert it to a list of Boolean values
        reversed_binary = list(binary_value[::-1])
        for i in range(len(reversed_binary)):
            if(reversed_binary[i] == '1'):
                val_1.append(True)
            elif(reversed_binary[i]== '0'):
                val_1.append(False)
    # print(val_1)
    return(val_1[:count])

def Modbus_CONTEXT_creator():
    # ----------------------------------------------------------------------- # 
    # initialize your data store
    # ----------------------------------------------------------------------- # 
    json_data_1 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_1) 
    json_data_2 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_2) 
    json_data_3 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_3) 
    json_data_4 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_4) 

    bool_parameter_dictionary={}
    int_parameter_dictionary={}
    float_parameter_dictionary={}

    for parameter_10_sec in json_data_1["parameter"]:
        if parameter_10_sec['reg_name'] == 'created_on' or parameter_10_sec['reg_name'] == 'modified_on':
            continue
        if(parameter_10_sec['type'] == 'bool' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=parameter_10_sec['value']
            bool_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'integer' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            int_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'float' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            float_parameter_dictionary.update(new_dictinoary)

    for parameter_10_sec in json_data_2["parameter"]:
        if parameter_10_sec['reg_name'] == 'created_on' or parameter_10_sec['reg_name'] == 'modified_on':
            continue
        if(parameter_10_sec['type'] == 'bool' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=parameter_10_sec['value']
            bool_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'integer' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            int_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'float' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            float_parameter_dictionary.update(new_dictinoary)

    for parameter_10_sec in json_data_3["parameter"]:
        if parameter_10_sec['reg_name'] == 'created_on' or parameter_10_sec['reg_name'] == 'modified_on':
            continue
        if(parameter_10_sec['type'] == 'bool' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=parameter_10_sec['value']
            bool_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'integer' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            int_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'float' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            float_parameter_dictionary.update(new_dictinoary)
    for parameter_10_sec in json_data_4["parameter"]:
        if parameter_10_sec['reg_name'] == 'created_on' or parameter_10_sec['reg_name'] == 'modified_on':
            continue
        if(parameter_10_sec['type'] == 'bool' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=parameter_10_sec['value']
            bool_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'integer' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            int_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'float' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            float_parameter_dictionary.update(new_dictinoary)
    bool_Rigister_value = []
    bool_Rigister_value_list = {}
    bool_Reg_Value = 0
    bool_register_num = 0
    bool_register_count = 0
    bool_flag = False
    int_Rigister_value = []
    int_Rigister_value_list = {}
    int_Reg_Value = 0
    int_register_num = 0
    int_register_count = 0
    int_flag = False


    builder = BinaryPayloadBuilder(
            byteorder=Endian.Big,
            wordorder=Endian.Little
            )
    for i in range(0,0xFFFF):
        bool_flag = False
        int_flag = False
        float_flag = False
        if i in bool_parameter_dictionary.keys():
            bool_flag = True
            if(bool_register_count == 0):
                bool_register_num = i
            bool_register_count+=1
            if(bool_parameter_dictionary[i] == "True"):
                bool_Reg_Value = True
            elif(bool_parameter_dictionary[i] == "False"):
                bool_Reg_Value = False
            else:
                bool_Reg_Value = False
            # print(i, bool_parameter_dictionary[i])
        elif i in int_parameter_dictionary.keys():
            int_flag = True
            if(int_register_count == 0):
                int_register_num = i
            int_register_count+=1
            builder.add_16bit_int(int_parameter_dictionary[i])  # kWh Tot*10for
            parameter = builder.to_registers()
            builder.reset()
            int_Reg_Value = parameter[0]
            # print(i, int_parameter_dictionary[i])
        elif i in float_parameter_dictionary.keys():
            int_flag = True
            if(int_register_count == 0):
                int_register_num = i
            int_register_count+=1
            builder.add_16bit_float(float_parameter_dictionary[i])  # kWh Tot*10for
            parameter = builder.to_registers()
            builder.reset()
            int_Reg_Value = parameter[0]
            # print(i, int_parameter_dictionary[i])
        else:
            int_Rigister_value_list.update({i: [0]})
            bool_Rigister_value_list.update({i: [False]})
        if(bool_flag == False):
            if(bool_register_count>0):
                bool_Rigister_value_list.update({bool_register_num: bool_Rigister_value})
                pass
            bool_register_count = 0
            bool_Rigister_value = []
        elif(bool_flag == True):
            bool_Rigister_value.append(bool_Reg_Value)
        if(int_flag == False):
            if(int_register_count>0):
                int_Rigister_value_list.update({int_register_num: int_Rigister_value})
                pass
            int_register_count = 0
            int_Rigister_value = []
        elif(int_flag == True):
            int_Rigister_value.append(int_Reg_Value)
    Master_Controller_Utils.block_cr = CustomDataBlock_bool(bool_Rigister_value_list)
    Master_Controller_Utils.block_hr = CustomDataBlock_int(int_Rigister_value_list)
    # ####################################################################################################################

    # Rigister_value = []
    # block_cr = ModbusSequentialDataBlock(0, Rigister_value)
    # Rigister_value = []
    # for address in range(0,5):
    #     Rigister_value.append(10)
    # block_hr = ModbusSequentialDataBlock(5, Rigister_value)
    Sample = ModbusSlaveContext(
    co=Master_Controller_Utils.block_cr,
    hr=Master_Controller_Utils.block_hr, zero_mode=True)
    # Master_Controller_Utils.slaves = Sample
     
    # if(Master_Controller_Utils.single_slave== True):
    #     Master_Controller_Utils.slaves.update({Master_Controller_Utils.Device_Address.value:Sample})
    #     print("updating to lave id ",Master_Controller_Utils.Device_Address.value)
    # elif(Master_Controller_Utils.single_slave== False):
    
    Master_Controller_Utils.slaves = Sample


    # try:
    #     StopServer()
    # except:
    #     print("Server_stoped_error")
    # context = ModbusServerContext(slaves=Master_Controller_Utils.slaves, single=True)

def Modbus_CONTEXT_USB_creator():
    # ----------------------------------------------------------------------- # 
    # initialize your data store
    # ----------------------------------------------------------------------- # 
    json_data_1 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_1) 
    json_data_2 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_2) 
    json_data_3 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_3) 
    json_data_4 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_4) 

    bool_parameter_dictionary={}
    int_parameter_dictionary={}
    float_parameter_dictionary={}

    for parameter_10_sec in json_data_1["parameter"]:
        if parameter_10_sec['reg_name'] == 'created_on' or parameter_10_sec['reg_name'] == 'modified_on':
            continue
        if(parameter_10_sec['type'] == 'bool' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=parameter_10_sec['value']
            bool_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'integer' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            int_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'float' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            float_parameter_dictionary.update(new_dictinoary)

    for parameter_10_sec in json_data_2["parameter"]:
        if parameter_10_sec['reg_name'] == 'created_on' or parameter_10_sec['reg_name'] == 'modified_on':
            continue
        if(parameter_10_sec['type'] == 'bool' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=parameter_10_sec['value']
            bool_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'integer' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            int_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'float' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            float_parameter_dictionary.update(new_dictinoary)

    for parameter_10_sec in json_data_3["parameter"]:
        if parameter_10_sec['reg_name'] == 'created_on' or parameter_10_sec['reg_name'] == 'modified_on':
            continue
        if(parameter_10_sec['type'] == 'bool' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=parameter_10_sec['value']
            bool_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'integer' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            int_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'float' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            float_parameter_dictionary.update(new_dictinoary)
    for parameter_10_sec in json_data_4["parameter"]:
        if parameter_10_sec['reg_name'] == 'created_on' or parameter_10_sec['reg_name'] == 'modified_on':
            continue
        if(parameter_10_sec['type'] == 'bool' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=parameter_10_sec['value']
            bool_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'integer' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            int_parameter_dictionary.update(new_dictinoary)
        elif (parameter_10_sec['type'] == 'float' ):
            new_dictinoary={}
            new_dictinoary[parameter_10_sec['reg_num']]=int((parameter_10_sec['value']-parameter_10_sec['offset']) / parameter_10_sec['factor'])
            float_parameter_dictionary.update(new_dictinoary)
    bool_Rigister_value = []
    bool_Rigister_value_list = {}
    bool_Reg_Value = 0
    bool_register_num = 0
    bool_register_count = 0
    bool_flag = False
    int_Rigister_value = []
    int_Rigister_value_list = {}
    int_Reg_Value = 0
    int_register_num = 0
    int_register_count = 0
    int_flag = False


    builder = BinaryPayloadBuilder(
            byteorder=Endian.Big,
            wordorder=Endian.Little
            )
    for i in range(0,0xFFFF):
        bool_flag = False
        int_flag = False
        float_flag = False
        if i in bool_parameter_dictionary.keys():
            bool_flag = True
            if(bool_register_count == 0):
                bool_register_num = i
            bool_register_count+=1
            if(bool_parameter_dictionary[i] == "True"):
                bool_Reg_Value = True
            elif(bool_parameter_dictionary[i] == "False"):
                bool_Reg_Value = False
            else:
                bool_Reg_Value = False
            # print(i, bool_parameter_dictionary[i])
        elif i in int_parameter_dictionary.keys():
            int_flag = True
            if(int_register_count == 0):
                int_register_num = i
            int_register_count+=1
            builder.add_16bit_int(int_parameter_dictionary[i])  # kWh Tot*10for
            parameter = builder.to_registers()
            builder.reset()
            int_Reg_Value = parameter[0]
            # print(i, int_parameter_dictionary[i])
        elif i in float_parameter_dictionary.keys():
            int_flag = True
            if(int_register_count == 0):
                int_register_num = i
            int_register_count+=1
            builder.add_16bit_float(float_parameter_dictionary[i])  # kWh Tot*10for
            parameter = builder.to_registers()
            builder.reset()
            int_Reg_Value = parameter[0]
            # print(i, int_parameter_dictionary[i])
        else:
            int_Rigister_value_list.update({i: [0]})
            bool_Rigister_value_list.update({i: [False]})
        if(bool_flag == False):
            if(bool_register_count>0):
                bool_Rigister_value_list.update({bool_register_num: bool_Rigister_value})
                pass
            bool_register_count = 0
            bool_Rigister_value = []
        elif(bool_flag == True):
            bool_Rigister_value.append(bool_Reg_Value)
        if(int_flag == False):
            if(int_register_count>0):
                int_Rigister_value_list.update({int_register_num: int_Rigister_value})
                pass
            int_register_count = 0
            int_Rigister_value = []
        elif(int_flag == True):
            int_Rigister_value.append(int_Reg_Value)
    bool_Rigister_value_list.update({0xFFFF: [True]})
    Master_Controller_Utils.block_cr = CustomDataBlock_USB_bool(bool_Rigister_value_list)
    Master_Controller_Utils.block_hr = CustomDataBlock_USB_int(int_Rigister_value_list)
    # ####################################################################################################################

    # Rigister_value = []
    # block_cr = ModbusSequentialDataBlock(0, Rigister_value)
    # Rigister_value = []
    # for address in range(0,5):
    #     Rigister_value.append(10)
    # block_hr = ModbusSequentialDataBlock(5, Rigister_value)
    Sample = ModbusSlaveContext(
    co=Master_Controller_Utils.block_cr,
    hr=Master_Controller_Utils.block_hr, zero_mode=True)
    # Master_Controller_Utils.slaves = Sample
    if(Master_Controller_Utils.single_slave== True):
           Master_Controller_Utils.slaves.update({Master_Controller_Utils.Device_Address.value:Sample})
    elif(Master_Controller_Utils.single_slave== False):
        Master_Controller_Utils.slaves = Sample
    # try:
    #     StopServer()
    # except:
    #     print("Server_stoped_error")
    # context = ModbusServerContext(slaves=Master_Controller_Utils.slaves, single=True)

def master_process_tcp_ip(Master_priority1_File_Read_Semaphore,
                    Master_priority2_File_Read_Semaphore,
                    Master_priority3_File_Read_Semaphore,
                    Master_priority4_File_Write_Semaphore,
                    Master_priority1_File_Write_Semaphore,
                    Master_priority2_File_Write_Semaphore,
                    Master_priority3_File_Write_Semaphore,
                    Master_priority4_File_Read_Semaphore,
                    # Read_Configuration_Semaphore,
                    # Write_Configuration_Semaphore,
                    # Configuration_backup_Semaphore,
                    Priority_1_backup_Semaphore,
                    Priority_2_backup_Semaphore,
                    Priority_3_backup_Semaphore,
                    Priority_4_backup_Semaphore,
                    Master_write2_value_dic1,
                    Master_write2_value_dic2,
                    Master_write2_value_dic3,
                    Master_write2_value_dic4,
                    Master_write1_value_dic1,
                    Master_write1_value_dic2,
                    Master_write1_value_dic3,
                    Master_write1_value_dic4,
                    Master_write_value_dic1, 
                    Master_write_value_dic2, 
                    Master_write_value_dic3, 
                    Master_write_value_dic4, 
                    Master_write_count_dic1, 
                    Master_write_count_dic2, 
                    Master_write_count_dic3, 
                    Master_write_count_dic4,
                    USB1_Status_Flag,
                    USB1_COM,
                    all_p_num,
                    priority4_reg_list,
                    Device_Address,
                    Controller_to_master_FileName_Priority1,
                    Controller_to_master_FileName_Priority2,
                    Controller_to_master_FileName_Priority3,
                    Controller_to_master_FileName_Priority4,
                    Master_to_controller_FileName_Priority1,
                    Master_to_controller_FileName_Priority2,
                    Master_to_controller_FileName_Priority3,
                    Master_to_controller_FileName_Priority4,
                    Priority_1_backup,
                    Priority_2_backup,
                    Priority_3_backup,
                    Priority_4_backup,

                    ):
    Master_Controller_Utils.master_process_init()
    Master_Controller_Utils.is_tcp_ip = True
    Master_Controller_Utils.USB1_Status_Flag = USB1_Status_Flag
    Master_Controller_Utils.USB1_COM = USB1_COM
    Master_Controller_Utils.Master_priority1_File_Read_Semaphore = Master_priority1_File_Read_Semaphore
    Master_Controller_Utils.Master_priority2_File_Read_Semaphore = Master_priority2_File_Read_Semaphore
    Master_Controller_Utils.Master_priority3_File_Read_Semaphore = Master_priority3_File_Read_Semaphore
    Master_Controller_Utils.Master_priority4_File_Write_Semaphore = Master_priority4_File_Write_Semaphore
    Master_Controller_Utils.Master_priority1_File_Write_Semaphore = Master_priority1_File_Write_Semaphore
    Master_Controller_Utils.Master_priority2_File_Write_Semaphore = Master_priority2_File_Write_Semaphore
    Master_Controller_Utils.Master_priority3_File_Write_Semaphore = Master_priority3_File_Write_Semaphore
    Master_Controller_Utils.Master_priority4_File_Read_Semaphore = Master_priority4_File_Read_Semaphore
    # Master_Controller_Utils.Read_Configuration_Semaphore = Read_Configuration_Semaphore
    # Master_Controller_Utils.Write_Configuration_Semaphore = Write_Configuration_Semaphore
    # Master_Controller_Utils.Configuration_backup_Semaphore = Configuration_backup_Semaphore
    Master_Controller_Utils.Priority_1_backup_Semaphore = Priority_1_backup_Semaphore
    Master_Controller_Utils.Priority_2_backup_Semaphore = Priority_2_backup_Semaphore
    Master_Controller_Utils.Priority_3_backup_Semaphore = Priority_3_backup_Semaphore
    Master_Controller_Utils.Priority_4_backup_Semaphore = Priority_4_backup_Semaphore
    Master_Controller_Utils.Master_write2_value_dic1  = Master_write2_value_dic1
    Master_Controller_Utils.Master_write2_value_dic2  = Master_write2_value_dic2
    Master_Controller_Utils.Master_write2_value_dic3  = Master_write2_value_dic3
    Master_Controller_Utils.Master_write2_value_dic4  = Master_write2_value_dic4
    Master_Controller_Utils.Master_write1_value_dic1  = Master_write1_value_dic1
    Master_Controller_Utils.Master_write1_value_dic2  = Master_write1_value_dic2
    Master_Controller_Utils.Master_write1_value_dic3  = Master_write1_value_dic3
    Master_Controller_Utils.Master_write1_value_dic4  = Master_write1_value_dic4
    Master_Controller_Utils.Master_write_value_dic1   = Master_write_value_dic1 
    Master_Controller_Utils.Master_write_value_dic2   = Master_write_value_dic2 
    Master_Controller_Utils.Master_write_value_dic3   = Master_write_value_dic3 
    Master_Controller_Utils.Master_write_value_dic4   = Master_write_value_dic4 
    Master_Controller_Utils.Master_write_count_dic1   = Master_write_count_dic1 
    Master_Controller_Utils.Master_write_count_dic2   = Master_write_count_dic2 
    Master_Controller_Utils.Master_write_count_dic3   = Master_write_count_dic3 
    Master_Controller_Utils.Master_write_count_dic4   = Master_write_count_dic4 
    Master_Controller_Utils.all_p_num = all_p_num
    Master_Controller_Utils.priority4_reg_list = priority4_reg_list 
    Master_Controller_Utils.Device_Address = Device_Address 
    Master_Controller_Utils.Controller_to_master_FileName_Priority1 =Controller_to_master_FileName_Priority1
    Master_Controller_Utils.Controller_to_master_FileName_Priority2 =Controller_to_master_FileName_Priority2
    Master_Controller_Utils.Controller_to_master_FileName_Priority3 =Controller_to_master_FileName_Priority3
    Master_Controller_Utils.Controller_to_master_FileName_Priority4 =Controller_to_master_FileName_Priority4
    Master_Controller_Utils.Master_to_controller_FileName_Priority1 =Master_to_controller_FileName_Priority1
    Master_Controller_Utils.Master_to_controller_FileName_Priority2 =Master_to_controller_FileName_Priority2
    Master_Controller_Utils.Master_to_controller_FileName_Priority3 =Master_to_controller_FileName_Priority3
    Master_Controller_Utils.Master_to_controller_FileName_Priority4 =Master_to_controller_FileName_Priority4
    Master_Controller_Utils.Priority_1_backup=Priority_1_backup
    Master_Controller_Utils.Priority_2_backup=Priority_2_backup
    Master_Controller_Utils.Priority_3_backup=Priority_3_backup
    Master_Controller_Utils.Priority_4_backup=Priority_4_backup

    Modbus_CONTEXT_creator()
    master_context_thread_process_2 = Thread(target=Master_context_Thread)
    TCPIP_Thread = Thread(target=TCPIP_THREAD)             #Rtu thread create

    master_context_thread_process_2.start()
    TCPIP_Thread.start()

    master_context_thread_process_2.join()
    TCPIP_Thread.join()
    while 1:

        pass



def Master_context_Thread(USB = ''):
    while (Master_Controller_Utils.Process_exit_flag == False):
        data_dictionary_Controller_To_Master_Priority_1 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_1) 
        Context_Update(data_dictionary_Controller_To_Master_Priority_1)
        data_dictionary_Controller_To_Master_Priority_2 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_2) 
        Context_Update(data_dictionary_Controller_To_Master_Priority_2)
        data_dictionary_Controller_To_Master_Priority_3 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_3) 
        Context_Update(data_dictionary_Controller_To_Master_Priority_3)
        data_dictionary_Controller_To_Master_Priority_4 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_4) 
        Context_Update(data_dictionary_Controller_To_Master_Priority_4)
        # time.sleep(100)
        if(USB != ''):
            if(Master_Controller_Utils.USB_found ==True and Master_Controller_Utils.this_process_master_usb_detected == False):
                if(Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] != True):
                    Master_Controller_Utils.master_usb_check_flag[Master_Controller_Utils.Master_search_count] = True
                else:
                    Master_Controller_Utils.Master_search_count+=1
                    Master_Controller_Utils.master_usb_check_flag.append(True)
                Master_Controller_Utils.this_process_master_usb_detected = True
                pass

def Context_Update(parameter_dictionary): 
    # return
    try:
        for parameter in parameter_dictionary["parameter"]:
            Master_write()
            if((parameter["reg_name"] != "created_on" and parameter["reg_name"] != "modified_on")):
                if(parameter["type"] == 'bool'):
                    reg_value1 = False
                    # arr = context[2].getValues(1, parameter["reg_num"], count = 1)
                    # arr = Master_Controller_Utils.block_cr.getValuesInternal(1, parameter["reg_num"], count = 1)
                    arr = Master_Controller_Utils.block_cr.getValuesInternal(parameter["reg_num"], count = 1)
                    if(parameter["reg_num"] in Master_Controller_Utils.Master_write1_value_dic1.keys()):
                        if("True" == Master_Controller_Utils.Master_write1_value_dic1[parameter["reg_num"]] or 1 == Master_Controller_Utils.Master_write1_value_dic1[parameter["reg_num"]]):
                            reg_value1 = True
                        elif("False" == Master_Controller_Utils.Master_write1_value_dic1[parameter["reg_num"]] or 0 == Master_Controller_Utils.Master_write1_value_dic1[parameter["reg_num"]]):
                            reg_value1 = False
                        else:
                            reg_value1 = False
                        pass
                        Master_Controller_Utils.block_cr.setValuesInternal(parameter["reg_num"], [reg_value1])
                    elif(parameter["reg_num"] in Master_Controller_Utils.Master_write1_value_dic2.keys()):
                        if("True" == Master_Controller_Utils.Master_write1_value_dic2[parameter["reg_num"]] or 1 == Master_Controller_Utils.Master_write1_value_dic2[parameter["reg_num"]]):
                            reg_value1 = True
                        elif("False" == Master_Controller_Utils.Master_write1_value_dic2[parameter["reg_num"]] or 0 == Master_Controller_Utils.Master_write1_value_dic2[parameter["reg_num"]]):
                            reg_value1 = False
                        else:
                            reg_value1 = False
                        pass
                        Master_Controller_Utils.block_cr.setValuesInternal(parameter["reg_num"], [reg_value1])
                    elif(parameter["reg_num"] in Master_Controller_Utils.Master_write1_value_dic3.keys()):
                        if("True" == Master_Controller_Utils.Master_write1_value_dic3[parameter["reg_num"]] or 1 == Master_Controller_Utils.Master_write1_value_dic3[parameter["reg_num"]]):
                            reg_value1 = True
                        elif("False" == Master_Controller_Utils.Master_write1_value_dic3[parameter["reg_num"]] or 0 == Master_Controller_Utils.Master_write1_value_dic3[parameter["reg_num"]]):
                            reg_value1 = False
                        else:
                            reg_value1 = False
                        pass
                        Master_Controller_Utils.block_cr.setValuesInternal(parameter["reg_num"], [reg_value1])
                    elif(parameter["reg_num"] in Master_Controller_Utils.Master_write1_value_dic4.keys()):
                        if("True" == Master_Controller_Utils.Master_write1_value_dic4[parameter["reg_num"]] or 1 == Master_Controller_Utils.Master_write1_value_dic4[parameter["reg_num"]]):
                            reg_value1 = True
                        elif("False" == Master_Controller_Utils.Master_write1_value_dic4[parameter["reg_num"]] or 0 == Master_Controller_Utils.Master_write1_value_dic4[parameter["reg_num"]]):
                            reg_value1 = False
                        else:
                            reg_value1 = False
                        pass
                        Master_Controller_Utils.block_cr.setValuesInternal(parameter["reg_num"], [reg_value1])
                    else:
                        reg_value=''
                        
                        if(arr[0] == True):
                            reg_value = 'True'
                            reg_value1 = False
                        elif(arr[0] == False):
                            reg_value = 'False'
                            reg_value1 = True
                        if(reg_value != parameter["value"]):     
                            Master_Controller_Utils.block_cr.setValuesInternal(parameter["reg_num"], [reg_value1])
                        else:
                            pass
                elif(parameter["type"] == 'integer'):
                    arr = Master_Controller_Utils.block_hr.getValuesInternal(parameter["reg_num"], count = 1)
                    # arr = Master_Controller_Utils.block_hr.getValuesInternal(3, parameter["reg_num"], count = 1)
                    # arr = context[2].getValues(3, parameter["reg_num"], count = 1)
                    reg_value=0
                    builder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                    builder.reset()
                    Decoder = BinaryPayloadDecoder.fromRegisters(arr,byteorder=Endian.Big, wordorder=Endian.Big)
                    # Decoder.reset()
                    reg_value = Decoder.decode_16bit_int()
                    if(parameter["reg_num"] in Master_Controller_Utils.Master_write1_value_dic1.keys()):
                        if(reg_value != int((Master_Controller_Utils.Master_write1_value_dic1[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"])): 
                            builder.add_16bit_int(int((Master_Controller_Utils.Master_write1_value_dic1[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"]))  
                            payload = builder.to_registers()
                            Master_Controller_Utils.block_hr.setValuesInternal(parameter["reg_num"], payload)
                        else:
                            pass
                    elif(parameter["reg_num"] in Master_Controller_Utils.Master_write1_value_dic2.keys()):
                        if(reg_value != int((Master_Controller_Utils.Master_write1_value_dic2[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"])): 
                            builder.add_16bit_int(int((Master_Controller_Utils.Master_write1_value_dic2[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"]))   
                            payload = builder.to_registers()
                            Master_Controller_Utils.block_hr.setValuesInternal(parameter["reg_num"], payload)
                        else:
                            pass
                    elif(parameter["reg_num"] in Master_Controller_Utils.Master_write1_value_dic3.keys()):
                        if(reg_value != int((Master_Controller_Utils.Master_write1_value_dic3[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"])): 
                            builder.add_16bit_int(int((Master_Controller_Utils.Master_write1_value_dic3[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"]))
                            payload = builder.to_registers()
                            Master_Controller_Utils.block_hr.setValuesInternal(parameter["reg_num"], payload)
                        else:
                            pass
                    elif(parameter["reg_num"] in Master_Controller_Utils.Master_write1_value_dic4.keys()):
                        if(reg_value != int((Master_Controller_Utils.Master_write1_value_dic4[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"])): 
                            builder.add_16bit_int(int((Master_Controller_Utils.Master_write1_value_dic4[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"]))
                            payload = builder.to_registers()
                            Master_Controller_Utils.block_hr.setValuesInternal(parameter["reg_num"], payload)
                        else:
                            pass
                    else:
                        if(reg_value != int((parameter["value"]-parameter["offset"]) / parameter["factor"])):  
                            builder.add_16bit_int(int((parameter["value"]-parameter["offset"]) / parameter["factor"]))
                            payload = builder.to_registers()
                            Master_Controller_Utils.block_hr.setValuesInternal(parameter["reg_num"], payload)
                        else:
                            pass
                elif(parameter["type"] == "float"):
                    arr = Master_Controller_Utils.block_hr.getValuesInternal(parameter["reg_num"], count = 1)
                    # arr = Master_Controller_Utils.block_hr.getValuesInternal(3, parameter["reg_num"], count = 1)
                    # arr = context[2].getValues(3, parameter["reg_num"], count = 1)
                    reg_value=0
                    builder = BinaryPayloadBuilder(byteorder=Endian.Big,wordorder=Endian.Big)
                    builder.reset()
                    Decoder = BinaryPayloadDecoder.fromRegisters(arr,byteorder=Endian.Big, wordorder=Endian.Big)
                    Decoder.reset()
                    reg_value = Decoder.decode_16bit_float()
                    if(parameter["reg_num"] in Master_Controller_Utils.Master_write1_value_dic1.keys()):
                        if(reg_value != int((Master_Controller_Utils.Master_write1_value_dic1[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"])): 
                            builder.add_16bit_float(int((Master_Controller_Utils.Master_write1_value_dic1[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"]))
                            payload = builder.to_registers()
                            Master_Controller_Utils.block_hr.setValuesInternal(parameter["reg_num"], payload)
                        else:
                            pass
                    elif(parameter["reg_num"] in Master_Controller_Utils.Master_write1_value_dic2.keys()):
                        if(reg_value != int((Master_Controller_Utils.Master_write1_value_dic2[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"])): 
                            builder.add_16bit_float(int((Master_Controller_Utils.Master_write1_value_dic2[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"]))
                            payload = builder.to_registers()
                            Master_Controller_Utils.block_hr.setValuesInternal(parameter["reg_num"], payload)
                        else:
                            pass
                    elif(parameter["reg_num"] in Master_Controller_Utils.Master_write1_value_dic3.keys()):
                        if(reg_value != int((Master_Controller_Utils.Master_write1_value_dic3[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"])): 
                            builder.add_16bit_float(int((Master_Controller_Utils.Master_write1_value_dic3[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"]))   
                            payload = builder.to_registers()
                            Master_Controller_Utils.block_hr.setValuesInternal(parameter["reg_num"], payload)
                        else:
                            pass
                    elif(parameter["reg_num"] in Master_Controller_Utils.Master_write1_value_dic4.keys()):
                        if(reg_value != int((Master_Controller_Utils.Master_write1_value_dic4[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"])): 
                            builder.add_16bit_float(int((Master_Controller_Utils.Master_write1_value_dic4[parameter["reg_num"]]-parameter["offset"]) / parameter["factor"]))  
                            payload = builder.to_registers()
                            Master_Controller_Utils.block_hr.setValuesInternal(parameter["reg_num"], payload)
                        else:
                            pass
                    else:
                        if(reg_value != int((parameter["value"]-parameter["offset"]) / parameter["factor"])): 
                            builder.add_16bit_float(int((parameter["value"]-parameter["offset"]) / parameter["factor"]))
                            payload = builder.to_registers()   
                            Master_Controller_Utils.block_hr.setValuesInternal(parameter["reg_num"], payload)
                        else:
                            pass
                time.sleep(0.01) 
    except Exception as e:
        print("Contect_Update exception =",e)
       
def Master_write():
    int_dictionary={}
    new_list=[]
    Priority_1_flag = False
    Priority_2_flag = False
    Priority_3_flag = False
    Priority_4_flag = False
    data_dictionary_Master_To_Controller_Priority_1 = {}
    data_dictionary_Master_To_Controller_Priority_2 = {}
    data_dictionary_Master_To_Controller_Priority_3 = {}
    data_dictionary_Master_To_Controller_Priority_4 = {}
    
    if(len(Master_Controller_Utils.int_parameter_dictionary) != 0):
        for parameter_number, parameter_value in Master_Controller_Utils.int_parameter_dictionary.items():
            read_decision = 0
            if parameter_number in Master_Controller_Utils.priority1_reg_list:
                read_decision=1
            elif parameter_number in Master_Controller_Utils.priority2_reg_list:
                read_decision=2
            elif parameter_number in Master_Controller_Utils.priority3_reg_list:
                read_decision=3
            elif parameter_number in Master_Controller_Utils.priority4_reg_list:
                read_decision=4
            else:
                continue
            Found_Flag = False

                
            if(read_decision==1 and Found_Flag == False):
                if (Priority_1_flag == False):
                    data_dictionary_Master_To_Controller_Priority_1 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1) 
                for parameters_10sec in data_dictionary_Master_To_Controller_Priority_1["parameter"]:
                    if((parameters_10sec["reg_name"] != "created_on" and parameters_10sec["reg_name"] != "modified_on") and parameters_10sec["reg_num"] == parameter_number):
                        if ((parameters_10sec["type"] == "integer") or (parameters_10sec["type"] == "float")):
                            Decoder = BinaryPayloadDecoder.fromRegisters([parameter_value],byteorder=Endian.Big, wordorder=Endian.Big)
                            if(parameters_10sec["type"] == "integer"):
                                parameters_10sec["value"] = ((Decoder.decode_16bit_int() * parameters_10sec["factor"]) + parameters_10sec["offset"])
                                # parameters["value"]=((value*parameters["factor"]) + parameters["offset"])
                            elif(parameters_10sec["type"] == "float"):
                                parameters_10sec["value"] = ((Decoder.decode_16bit_float() * parameters_10sec["factor"]) + parameters_10sec["offset"])
                            new_dictinoary={}
                            new_dictinoary[parameters_10sec['reg_num']]=parameters_10sec['value']
                            Master_Controller_Utils.Master_write_value_dic1.update(new_dictinoary)
                            Master_Controller_Utils.Master_write1_value_dic1.update(new_dictinoary)
                            # print("Trying to write = ",new_dictinoary)
                            new_dictinoary[parameters_10sec['reg_num']]=0
                            Master_Controller_Utils.Master_write_count_dic1.update(new_dictinoary)
                            new_dictinoary={}
                            new_dictinoary[parameters_10sec['reg_num']]=parameters_10sec['reg_name']
                            Master_Controller_Utils.Master_write2_value_dic1.update(new_dictinoary)
                            # print(" ",)
                            Priority_1_flag = True
                            Found_Flag = True
                            break
            if(read_decision==2 and Found_Flag == False):
                if (Priority_2_flag == False):
                    data_dictionary_Master_To_Controller_Priority_2 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2) 
                for parameters_5min in data_dictionary_Master_To_Controller_Priority_2["parameter"]:
                    if((parameters_5min["reg_name"] != "created_on" and parameters_5min["reg_name"] != "modified_on") and parameters_5min["reg_num"] == parameter_number):
                        if ((parameters_5min["type"] == "integer") or (parameters_5min["type"] == "float")):
                            Decoder = BinaryPayloadDecoder.fromRegisters([parameter_value],byteorder=Endian.Big, wordorder=Endian.Big)
                            if(parameters_5min["type"] == "integer"):
                                parameters_5min["value"] = ((Decoder.decode_16bit_int() * parameters_5min["factor"]) + parameters_5min["offset"])
                            elif(parameters_5min["type"] == "float"):
                                parameters_5min["value"] = ((Decoder.decode_16bit_float() * parameters_5min["factor"]) + parameters_5min["offset"])
                            new_dictinoary={}
                            new_dictinoary[parameters_5min['reg_num']]=parameters_5min['value']
                            Master_Controller_Utils.Master_write_value_dic2.update(new_dictinoary)
                            Master_Controller_Utils.Master_write1_value_dic2.update(new_dictinoary)
                            # print("Trying to write = ",new_dictinoary)
                            new_dictinoary[parameters_5min['reg_num']]=0
                            Master_Controller_Utils.Master_write_count_dic2.update(new_dictinoary)
                            new_dictinoary={}
                            new_dictinoary[parameters_5min['reg_num']]=parameters_5min['reg_name']
                            Master_Controller_Utils.Master_write2_value_dic1.update(new_dictinoary)
                            Priority_2_flag = True
                            Found_Flag = True
                            break
            if(read_decision==3 and Found_Flag == False):
                if (Priority_3_flag == False):
                    data_dictionary_Master_To_Controller_Priority_3 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3) 
                for parameters_4hours in data_dictionary_Master_To_Controller_Priority_3["parameter"]:
                    if((parameters_4hours["reg_name"] != "created_on" and parameters_4hours["reg_name"] != "modified_on") and parameters_4hours["reg_num"] == parameter_number):
                        if ((parameters_4hours["type"] == "integer") or (parameters_4hours["type"] == "float")):
                            Decoder = BinaryPayloadDecoder.fromRegisters([parameter_value],byteorder=Endian.Big, wordorder=Endian.Big)
                            if(parameters_4hours["type"] == "integer"):
                                parameters_4hours["value"] = ((Decoder.decode_16bit_int() * parameters_4hours["factor"]) + parameters_4hours["offset"])
                            elif(parameters_4hours["type"] == "float"):
                                parameters_4hours["value"] = ((Decoder.decode_16bit_float() * parameters_4hours["factor"]) + parameters_4hours["offset"])
                            new_dictinoary={}
                            new_dictinoary[parameters_4hours['reg_num']]=parameters_4hours['value']
                            Master_Controller_Utils.Master_write_value_dic3.update(new_dictinoary)
                            Master_Controller_Utils.Master_write1_value_dic3.update(new_dictinoary)
                            # print("Trying to write = ",new_dictinoary)
                            new_dictinoary[parameters_4hours['reg_num']]=0
                            Master_Controller_Utils.Master_write_count_dic3.update(new_dictinoary)
                            new_dictinoary={}
                            new_dictinoary[parameters_4hours['reg_num']]=parameters_4hours['reg_name']
                            Master_Controller_Utils.Master_write2_value_dic1.update(new_dictinoary)
                            Priority_3_flag = True
                            Found_Flag = True
                            break
            if(read_decision==4 and Found_Flag == False):
                if (Priority_4_flag == False):
                    data_dictionary_Master_To_Controller_Priority_4 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4) 
                for parameters_extra in data_dictionary_Master_To_Controller_Priority_4["parameter"]:
                    if((parameters_extra["reg_name"] != "created_on" and parameters_extra["reg_name"] != "modified_on") and parameters_extra["reg_num"] == parameter_number):
                        if ((parameters_extra["type"] == "integer") or (parameters_extra["type"] == "float")):
                            Decoder = BinaryPayloadDecoder.fromRegisters([parameter_value],byteorder=Endian.Big, wordorder=Endian.Big)
                            if(parameters_extra["type"] == "integer"):
                                parameters_extra["value"] = ((Decoder.decode_16bit_int() * parameters_extra["factor"]) + parameters_extra["offset"])
                            elif(parameters_extra["type"] == "float"):
                                parameters_extra["value"] = ((Decoder.decode_16bit_float() * parameters_extra["factor"]) + parameters_extra["offset"])
                            new_dictinoary={}
                            new_dictinoary[parameters_extra['reg_num']]=parameters_extra['value']
                            Master_Controller_Utils.Master_write_value_dic4.update(new_dictinoary)
                            Master_Controller_Utils.Master_write1_value_dic4.update(new_dictinoary)
                            # print("Trying to write = ",new_dictinoary)
                            new_dictinoary[parameters_extra['reg_num']]=0
                            Master_Controller_Utils.Master_write_count_dic4.update(new_dictinoary)
                            new_dictinoary={}
                            new_dictinoary[parameters_extra['reg_num']]=parameters_extra['reg_name']
                            Master_Controller_Utils.Master_write2_value_dic1.update(new_dictinoary)
                            Priority_4_flag = True
                            Found_Flag = True
                            break
                        
        Master_Controller_Utils.int_parameter_dictionary.clear()

    if(len(Master_Controller_Utils.bool_parameter_dictionary) != 0):
        Priority_1_flag = False
        Priority_2_flag = False
        Priority_3_flag = False
        Priority_4_flag = False
        data_dictionary_Master_To_Controller_Priority_1 = {}
        data_dictionary_Master_To_Controller_Priority_2 = {}
        data_dictionary_Master_To_Controller_Priority_3 = {}
        data_dictionary_Master_To_Controller_Priority_4 = {}
        for parameter_number, parameter_value in Master_Controller_Utils.bool_parameter_dictionary.items():
            read_decision = 0
            if parameter_number in Master_Controller_Utils.priority1_reg_list:
                read_decision=1
            elif parameter_number in Master_Controller_Utils.priority2_reg_list:
                read_decision=2
            elif parameter_number in Master_Controller_Utils.priority3_reg_list:
                read_decision=3
            elif parameter_number in Master_Controller_Utils.priority4_reg_list:
                read_decision=4
            else:
                continue
            Found_Flag = False

            if(read_decision==1 and Found_Flag == False):
                if (Priority_1_flag == False):
                    data_dictionary_Master_To_Controller_Priority_1 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1) 
                for parameters_10sec in data_dictionary_Master_To_Controller_Priority_1["parameter"]:
                    if((parameters_10sec["reg_name"] != "created_on" and parameters_10sec["reg_name"] != "modified_on") and parameters_10sec["reg_num"] == parameter_number):
                        if(parameters_10sec["type"] == "bool"):    
                            if(True == parameter_value):
                                parameters_10sec["value"] = "True"
                            elif(False == parameter_value):
                                parameters_10sec["value"] = "False"
                            new_dictinoary={}
                            new_dictinoary[parameters_10sec['reg_num']]=parameters_10sec['value']
                            Master_Controller_Utils.Master_write_value_dic1.update(new_dictinoary)
                            Master_Controller_Utils.Master_write1_value_dic1.update(new_dictinoary)
                            # print("Trying to write = ",new_dictinoary)
                            new_dictinoary[parameters_10sec['reg_num']]=0
                            Master_Controller_Utils.Master_write_count_dic1.update(new_dictinoary)
                            new_dictinoary={}
                            new_dictinoary[parameters_10sec['reg_num']]=parameters_10sec['reg_name']
                            Master_Controller_Utils.Master_write2_value_dic1.update(new_dictinoary)
                            Priority_1_flag = True
                            Found_Flag = True
                            break
                
            if(read_decision==2 and Found_Flag == False):
                if (Priority_2_flag == False):
                    data_dictionary_Master_To_Controller_Priority_2 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2) 
                for parameters_5min in data_dictionary_Master_To_Controller_Priority_2["parameter"]:
                    if((parameters_5min["reg_name"] != "created_on" and parameters_5min["reg_name"] != "modified_on") and parameters_5min["reg_num"] == parameter_number):
                        if(parameters_5min["type"] == "bool"):    
                            if(True == parameter_value):
                                parameters_5min["value"] = "True"
                            elif(False == parameter_value):
                                parameters_5min["value"] = "False"
                            new_dictinoary={}
                            new_dictinoary[parameters_5min['reg_num']]=parameters_5min['value']
                            Master_Controller_Utils.Master_write_value_dic2.update(new_dictinoary)
                            Master_Controller_Utils.Master_write1_value_dic2.update(new_dictinoary)
                            # print("Trying to write = ",new_dictinoary)
                            new_dictinoary[parameters_5min['reg_num']]=0
                            Master_Controller_Utils.Master_write_count_dic2.update(new_dictinoary)
                            new_dictinoary={}
                            new_dictinoary[parameters_5min['reg_num']]=parameters_5min['reg_name']
                            Master_Controller_Utils.Master_write2_value_dic1.update(new_dictinoary)
                            Priority_2_flag = True
                            Found_Flag = True
                            break
                
            if(read_decision==3 and Found_Flag == False):
                if (Priority_3_flag == False):
                    data_dictionary_Master_To_Controller_Priority_3 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3) 
                for parameters_4hours in data_dictionary_Master_To_Controller_Priority_3["parameter"]:
                    if((parameters_4hours["reg_name"] != "created_on" and parameters_4hours["reg_name"] != "modified_on") and parameters_4hours["reg_num"] == parameter_number):
                        if(parameters_4hours["type"] == "bool"):    
                            if(True == parameter_value):
                                parameters_4hours["value"] = "True"
                            elif(False == parameter_value):
                                parameters_4hours["value"] = "False"
                            new_dictinoary={}
                            new_dictinoary[parameters_4hours['reg_num']]=parameters_4hours['value']
                            Master_Controller_Utils.Master_write_value_dic3.update(new_dictinoary)
                            Master_Controller_Utils.Master_write1_value_dic3.update(new_dictinoary)
                            # print("Trying to write = ",new_dictinoary)
                            new_dictinoary[parameters_4hours['reg_num']]=0
                            Master_Controller_Utils.Master_write_count_dic3.update(new_dictinoary)
                            new_dictinoary={}
                            new_dictinoary[parameters_4hours['reg_num']]=parameters_4hours['reg_name']
                            Master_Controller_Utils.Master_write2_value_dic1.update(new_dictinoary)
                            Priority_3_flag = True
                            Found_Flag = True
                            break
            
            if(read_decision==4 and Found_Flag == False):
                if (Priority_4_flag == False):
                    data_dictionary_Master_To_Controller_Priority_4 = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4) 
                for parameters_extra in data_dictionary_Master_To_Controller_Priority_4["parameter"]:
                    if((parameters_extra["reg_name"] != "created_on" and parameters_extra["reg_name"] != "modified_on") and parameters_extra["reg_num"] == parameter_number):
                        if(parameters_extra["type"] == "bool"):    
                            if(True == parameter_value):
                                parameters_extra["value"] = "True"
                            elif(False == parameter_value):
                                parameters_extra["value"] = "False"
                            new_dictinoary={}
                            new_dictinoary[parameters_extra['reg_num']]=parameters_extra['value']
                            Master_Controller_Utils.Master_write_value_dic4.update(new_dictinoary)
                            Master_Controller_Utils.Master_write1_value_dic4.update(new_dictinoary)
                            # print("Trying to write = ",new_dictinoary)
                            new_dictinoary[parameters_extra['reg_num']]=0
                            Master_Controller_Utils.Master_write_count_dic4.update(new_dictinoary)
                            new_dictinoary={}
                            new_dictinoary[parameters_extra['reg_num']]=parameters_extra['reg_name']
                            Master_Controller_Utils.Master_write2_value_dic1.update(new_dictinoary)
                            Priority_4_flag = True
                            Found_Flag = True
                            break
                
        Master_Controller_Utils.bool_parameter_dictionary.clear()
    if(Priority_1_flag== True):
        # Master_Controller_Utils.REF_DICT_PRIORITY_1= data_dictionary_Master_To_Controller_Priority_1
        # Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_1, data_dictionary_Master_To_Controller_Priority_1)        
        Master_Controller_Utils.Master_written_JSON_Priority1_Flag = True
    if(Priority_2_flag== True):
        # Master_Controller_Utils.REF_DICT_PRIORITY_2= data_dictionary_Master_To_Controller_Priority_2
        # Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_2, data_dictionary_Master_To_Controller_Priority_2)        
        Master_Controller_Utils.Master_written_JSON_Priority2_Flag = True
    if(Priority_3_flag== True):
        # Master_Controller_Utils.REF_DICT_PRIORITY_3= data_dictionary_Master_To_Controller_Priority_3
        # Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_3, data_dictionary_Master_To_Controller_Priority_3)        
        Master_Controller_Utils.Master_written_JSON_Priority3_Flag = True
    if(Priority_4_flag== True):
        # Master_Controller_Utils.REF_DICT_PRIORITY_4= data_dictionary_Master_To_Controller_Priority_4
        # Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4, data_dictionary_Master_To_Controller_Priority_4)                 
        Master_Controller_Utils.Master_written_JSON_Priority4_Flag = True  


    Extra_found = False
    if Master_Controller_Utils.new_list != []:
        if(Master_Controller_Utils.Extra_par_flag == False):
            Master_Controller_Utils.Extra_par_flag = True
            Extra_found = True
            data_write = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4)
            data_read = Master_Controller_Utils.JSON_File_Read(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_4)
            removing_list = []
            for new_para_info in Master_Controller_Utils.new_list:
                data_write["parameter"].append(new_para_info)
                data_read["parameter"].append(new_para_info)
                removing_list.append(new_para_info)
                print("Extra =",new_para_info)
                if(new_para_info["reg_num"] in Master_Controller_Utils.new_write_list):
                    parameter_value = 0
                    if(new_para_info["type"] == "bool"):  
                         
                        if("True" == new_para_info["value"]):
                            parameter_value = "True"
                        elif("False" == parameter_value):
                            parameter_value = "False"
                        print(parameter_value)
                        new_dictinoary={}
                        new_dictinoary[new_para_info['reg_num']]=parameter_value
                        Master_Controller_Utils.Master_write_value_dic4.update(new_dictinoary)
                        Master_Controller_Utils.Master_write1_value_dic4.update(new_dictinoary)
                        # print("Trying to write = ",new_dictinoary)
                        new_dictinoary[new_para_info['reg_num']]=0
                        Master_Controller_Utils.Master_write_count_dic4.update(new_dictinoary)
                        new_dictinoary={}
                        new_dictinoary[new_para_info['reg_num']]=new_para_info['reg_name']
                        Master_Controller_Utils.Master_write2_value_dic1.update(new_dictinoary)
                        # print("hi_1",Master_Contro  ller_Utils.new_write_list, Master_Controller_Utils.Master_write_value_dic4) 
                    elif ((new_para_info["type"] == "integer") or (new_para_info["type"] == "float")):
                        # print("hi_2",Master_Controller_Utils.new_write_list)
                        Decoder = BinaryPayloadDecoder.fromRegisters([new_para_info["value"]],byteorder=Endian.Big, wordorder=Endian.Big)
                        if(new_para_info["type"] == "integer"):
                            parameter_value = Decoder.decode_16bit_int()
                        elif(new_para_info["type"] == "float"):
                            parameter_value = Decoder.decode_16bit_float()
                        new_dictinoary={}
                        new_dictinoary[new_para_info['reg_num']]=parameter_value
                        Master_Controller_Utils.Master_write_value_dic4.update(new_dictinoary)
                        Master_Controller_Utils.Master_write1_value_dic4.update(new_dictinoary)
                        new_dictinoary[new_para_info['reg_num']]=0
                        Master_Controller_Utils.Master_write_count_dic4.update(new_dictinoary)
                        new_dictinoary={}
                        new_dictinoary[new_para_info['reg_num']]=new_para_info['reg_name']
                        Master_Controller_Utils.Master_write2_value_dic1.update(new_dictinoary)       
            for i in removing_list:
                Master_Controller_Utils.new_list.remove(i)
                if(i["reg_num"] in Master_Controller_Utils.new_write_list):
                    Master_Controller_Utils.new_write_list.remove(i["reg_num"])
            Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.MASTER_TO_CONTROLLER_PRIORITY_4, data_write) 
            Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.CONTROLLER_TO_MASTER_PRIORITY_4, data_read)
            Master_Controller_Utils.JSON_File_Write(Master_Controller_Utils.JSON.PRIORITY_4, data_read)

    if(Extra_found == True):
        Master_Controller_Utils.Extra_par_flag = False

def crc_modbus_non_hex(buf):
    num = len(buf)
    crc = 0xFFFF
    for pos in range(num):
        crc ^= buf[pos]
        for i in range(8, 0, -1):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    crc = ((crc & 0xff00) >> 8) | ((crc & 0x00ff) << 8)
    return crc

def send(ser,send_buffer):
    crc_1=crc_modbus_non_hex(send_buffer)
    send_buffer.append(((crc_1) & 0xFF00)>>8)
    send_buffer.append((crc_1) & 0x00FF)
    ser.write(send_buffer)