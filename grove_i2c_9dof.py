import time,sys
import RPi.GPIO as GPIO
import smbus
import math

rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)

class icm20600:
    
    ICM20600_ADDR = 0x69

    #register too mach for me
    XG_OFFS_TC_H = 0x04
    XG_OFFS_TC_L = 0x05
    YG_OFFS_TC_H = 0x07
    YG_OFFS_TC_L = 0x08
    ZG_OFFS_TC_H = 0x0A
    ZG_OFFS_TC_L = 0x0B

    SELF_TEST_X_ACCEL = 0x0D
    SELF_TEST_Y_ACCEL = 0x0E
    SELF_TEST_Z_ACCEL = 0x0F

    XG_OFFS_USRH = 0x13
    XG_OFFS_USRL = 0x14
    YG_OFFS_USRH = 0x15
    YG_OFFS_USRL = 0x16
    ZG_OFFS_USRH = 0x17
    ZG_OFFS_USRL = 0x18

    SMPLRT_DIV = 0x19

    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    ACCEL_CONFIG2 = 0x1D
    LP_MODE_CFG = 0x1E

    ACCEL_WOM_X_THR = 0x20
    ACCEL_WOM_Y_THR = 0x21
    ACCEL_WOM_Z_THR = 0x22

    FIFO_EN = 0x23
    
    FSYNC_INT = 0x36
    INT_PIN_CFG = 0x37
    INT_ENABLE = 0x38
    FIFO_WM_INT_STATUS = 0x39
    INT_STATUS = 0x3A

    ACCEL_XOUT_H = 0x3B
    ACCEL_XOUT_L = 0x3C
    ACCEL_YOUT_H = 0x3D
    ACCEL_YOUT_L = 0x3E
    ACCEL_ZOUT_H = 0x3F
    ACCEL_ZOUT_L = 0x40

    TEMP_OUT_H = 0x41
    TEMP_OUT_L = 0x42

    GYRO_XOUT_H = 0x43
    GYRO_XOUT_L = 0x44
    GYRO_YOUT_H = 0x45
    GYRO_YOUT_L = 0x46
    GYRO_ZOUT_H = 0x47
    GYRO_ZOUT_L = 0x48

    SELF_TEST_X_GYRO = 0x50
    SELF_TEST_Y_GYRO = 0x51
    SELF_TEST_Z_GYRO = 0x52

    FIFO_WM_TH1 = 0x60
    FIFO_WM_TH2 = 0x61

    SIGNAL_PATH_RESET = 0x68
    ACCEL_INTEL_CTRL = 0x69
    USER_CTRL = 0x6A

    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C

    I2C_IF = 0x70

    FIFO_COUNTH = 0x72
    FIFO_COUNTL = 0x73
    FIFO_R_W = 0x74
    
    WHO_AM_I = 0x75

    XA_OFFSET_H = 0x77
    XA_OFFSET_L = 0x78
    YA_OFFSET_H = 0x7A
    YA_OFFSET_L = 0x7B
    ZA_OFFSET_H = 0x7D
    ZA_OFFSET_L = 0x7E

    def status(self):
        if self.reg_read(self.WHO_AM_I) != 0x11:
#            print self.reg_read(self.WHO_AM_I)
            return -1
        return 1

    def initialize(self):
        print("initialize")
        self.reg_write(self.CONFIG,0x00)
        self.reg_write(self.FIFO_EN,0x00)
        time.sleep(1)

        #need def power mode setting
        pwr1 = 0x00
        pwr1 = self.reg_read(self.PWR_MGMT_1)&0x8f
        gyr = self.reg_read(self.LP_MODE_CFG)&0x7f
        self.reg_write(self.PWR_MGMT_1,pwr1|0x00)
        self.reg_write(self.PWR_MGMT_2,0x00)
        self.reg_write(self.LP_MODE_CFG,gyr)
        #need gyro scale,output rate,average setting
        #2000DPS bw176 average 1
        #DPS
        gyr_c = self.reg_read(self.GYRO_CONFIG)&0xe7
        self.reg_write(self.GYRO_CONFIG,gyr_c|0x18)
        #rate
        conf = self.reg_read(self.CONFIG)&0xf8
        self.reg_write(self.CONFIG,conf|0x01)
        #averge
        lp_c = self.reg_read(self.LP_MODE_CFG)&0x8f
        self.reg_write(self.LP_MODE_CFG,lp_c|0x00)
        #need accel config setting
        #16G 1k420 average4 acc_scale 16000
        ac_c = self.reg_read(self.ACCEL_CONFIG)&0xE7
#        print(ac_c)
        self.reg_write(self.ACCEL_CONFIG,0x18|ac_c)
        ac_c2 = self.reg_read(self.ACCEL_CONFIG2)&0xf0
        self.reg_write(self.ACCEL_CONFIG2,0x07|ac_c2)
        ac_c2 = self.reg_read(self.ACCEL_CONFIG2)&0xcf
        self.reg_write(self.ACCEL_CONFIG2,ac_c2)

    def s8(self,value):
        return -(value&0b10000000)|(value&0b01111111)

        
    def reg_write(self,addr,data):
        bus.write_byte_data(self.ICM20600_ADDR,addr,data)

    def reg_read(self,addr):
#        print(addr)
        return bus.read_byte_data(self.ICM20600_ADDR,addr)

    def getAccel(self):
        raw_accel=[0.0,0.0,0.0]
        raw_accel[0] = self.s8(self.reg_read(self.ACCEL_XOUT_H))*16/0xff*2
        raw_accel[1] = self.s8(self.reg_read(self.ACCEL_YOUT_H))*16/0xff*2
        raw_accel[2] = self.s8(self.reg_read(self.ACCEL_ZOUT_H))*16/0xff*2
        return raw_accel

    def getGyro(self):
        raw_gyro = [0,0,0]
        raw_gyro[0] = self.s8(self.reg_read(self.GYRO_XOUT_H))/0xff*2*2000
        raw_gyro[1] = self.s8(self.reg_read(self.GYRO_YOUT_H)+1)/0xff*2*2000
        raw_gyro[2] = self.s8(self.reg_read(self.GYRO_ZOUT_H))/0xff*2*2000
        return raw_gyro

class ak09918:
    AK09918_ADDR = 0x0C
    WIA1 = 0x00
    WIA2 = 0x01
    RAV1 = 0x02
    RSV2 = 0x03
    ST1 = 0x10
    HXL = 0x11
    HXH = 0x12
    HYL = 0x13
    HYH = 0x14
    HZL = 0x15
    HZH = 0x16
    TMPS = 0x17
    ST2 = 0x18
    CNTL1 = 0x30
    CNTL2 = 0x31
    CNTL3 = 0x32
    TS1 = 0x33
    TS2 = 0x34

    def initialize(self):
        self.reg_write(self.CNTL3,0x01)
        self.reg_read(self.ST1)
        self.reg_write(self.CNTL2,0x08)

        self.reg_read(self.ST1)
        self.reg_read(self.CNTL2)
        
    def reg_write(self,addr,data):
        bus.write_byte_data(self.AK09918_ADDR,addr,data)

    def reg_read(self,addr):
#        print(addr)
        return bus.read_byte_data(self.AK09918_ADDR,addr)

    def getMagAxis(self):
        self.reg_write(self.CNTL3,0x01)
        self.reg_write(self.CNTL2,0x08)
        while 1:
            if self.reg_read(self.ST1):
                break
            
        mag_axis = [0,0,0]
        mag_axis[0] = self.reg_read(self.HXL)

        mag_axis[1] = self.reg_read(self.HYL)
        mag_axis[2] = self.reg_read(self.HZL)
        return mag_axis
        

def getAccel():
    return icm20600().getAccel()

def getGyro():
    return icm20600().getGyro()

def getMagAxis():
    return ak09918().getMagAxis()

def initialize():
    icm20600().initialize()
    ak09918().initialize()
    return




def streamTest():
    icm20600().status()
    icm20600().initialize()
    ak09918().initialize()
    while 1:
        print(getAccel())
        print(getGyro())
        print(ak09918().getMagAxis())
        time.sleep(1)
    
if __name__ == "__main__":
    icm20600().initialize()
    icm20600().initialize()
    ak09918.initialize()
