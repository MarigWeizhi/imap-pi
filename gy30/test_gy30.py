import time
import smbus
#print(smbus.version)
bus = smbus.SMBus(1)
addr = 0x23

while(1):
    data = bus.read_i2c_block_data(addr, 0x11)
    light= str((data[1] + (256 * data[0])) / 1.2)
    print("Luminosity " + str((data[1] + (256 * data[0])) / 1.2) + "lx")
    tmp_output = open('/home/pi/Desktop/tmp_data.txt', mode='w')
    tmp_output.write(light)
    tmp_output.writelines('\n')
    time.sleep(1)