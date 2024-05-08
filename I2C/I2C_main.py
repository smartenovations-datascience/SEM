import smbus

from smbus2 import SMBus
import time



class I2C:
    def __init__(self, i2c_bus=1, addr=0x40):
        # self.bus = smbus.SMBus(i2c_bus)
        self.bus = SMBus(i2c_bus)
        self.addr = addr


    def read(self,Reg_address,Len):
       #pass the register address and length to read the i2c sensor data in 1 byte list format
        data = self.bus.read_i2c_block_data(self.addr, Reg_address, Len)
        return data

    def write(self,Reg_address,data):
      #pass the register address and data of 1 byte list format to write the i2c sensor data 
      #data should be 1 bytes value lists
        self.bus.write_i2c_block_data(self.addr,Reg_address,data)

      
if __name__=='__main__':
   #create a instance of I2C with divice adrress
    Sensor1 = I2C(addr=0x40)
    Sensor2 = I2C(addr=0x41)

    #to read the sensor data with Register address
    Sensor1_data = Sensor1.read(0x10,4)#register address 0x10 with read lenght of 4 bytes 
    print(Sensor1_data)
    time.sleep(2)
    Sensor2_data = Sensor2.read(0x20,2)#register address 0x20 with read lenght of 2 bytes 
    print(Sensor2_data)
    time.sleep(2)
    #to write the sensor data with Register address
    sensor1_write_value=[1,2,3,4]
    Sensor1.write(0x10,sensor1_write_value)#register address 0x10 with write list lenght of 4 bytes 
    time.sleep(2)
    sensor2_write_value=[1,2]
    Sensor2.write(0x20,sensor2_write_value)#register address 0x20 with write list lenght of 2 bytes 
    
