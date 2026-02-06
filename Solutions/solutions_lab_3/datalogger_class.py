import digitalio
import board
import busio
import sdcardio
import storage
import os
import time
from sensors import *

class datalogger:
    def __init__(self,spi,cs):
        sdcard = sdcardio.SDCard(spi, cs)
        self.vfs = storage.VfsFat(sdcard)
        storage.mount(self.vfs, "/sd")
        print("successful mount")
        #set up sd and file
    def create_file(self,filename):
        self.file=open("/sd/"+filename,"w")
    def write_data(self,data):
        if self.isSpace():
            try:
                self.file.write(data)
            except:
                print("Could not write") #you could also consider putting errors or LED flashes here
        #if there is space
        #write data in the chosen format
    def isSpace(self):
        stats = self.vfs.statvfs("/sd")
        total_space=stats[2]*stats[1]
        free_space = stats[3] * stats[1]
        used_space = total_space-free_space
        if used_space/(1024**3)<14: #space exists
            return 1
        return 0
        #check how much space there is
    def close(self):
        self.file.close()
        #close and save the file

#main control
if __name__ == "__main__": #you can ignore this, but this line just means if you are running the local file then run this code
    #setup spi
    spi = busio.SPI(clock=board.GP2,MOSI=board.GP3,MISO=board.GP4) 
    cs = board.GP16
    data=datalogger(spi,cs)

    #set up record button
    led = digitalio.DigitalInOut(board.GP17)
    button = digitalio.DigitalInOut(board.GP15)
    
    #set up directions of pins
    led.direction = digitalio.Direction.OUTPUT
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    
    #variables needed
    filename="mydata" #the filename
    toggle=False #toggle to keep track of the button press
    recordings=0 #the variable to keep track of how many recordsings have been made

    l = light(board.GP27) # collect light
    h = humidity(board.GP10)

    while True: #use your LED toggle code from yesterdays lab
        led.value=toggle
        if button.value==0: #when you toggle the button on, it should start recording
            toggle=not toggle
            if toggle: #have the filename change everytime you start a new recording
                f=filename+str(recordings)+".csv" #create a unique name for file
                data.create_file(f) 
                data.write_data("time,light,humidity,temperature\n") #make keys
            else: #when you toggle the button off, it should stop
                try:
                    data.close() #close and save the file
                    recordings+=1 #increase the number of files so we do not overwrite
                    print("file saves...")
                except: #if there is an error closing the file
                    pass
            time.sleep(0.5)
        led.value=toggle #try adding an LED to show if it is recording or not
        if toggle: #if recording gather all the sensors
            t1=time.monotonic()
            light_reading=l.readPin() #read analogue sensor
            humid=h.getHumidity() #read humidity sensor
            temp=h.getTemp() #read temperature
            data.write_data(str(time.monotonic()-t1)+","+str(light_reading)+","+str(humid)+","+str(temp)+"\n") #write in csv format
            print(str(time.monotonic()-t1)+","+str(light_reading)+","+str(humid)+","+str(temp)) #show user
            
        time.sleep(0.1)
