

import LPC8xx_Bootloader
import time


    
    
#----------------------------------------------------------------------

def bootload(idNum):
    bootLoad812.flushReadBuffer()
    bootLoad812.BMSbootloaderStart(idNum)
    time.sleep(2)
    response = bootLoad812.checkRepsonse()
    
    if(response == '{09RB00000000000016}'):
        print 'Bootoader response correct. Starting...'
        time.sleep(1)
        bootLoad812.checkRepsonse()
        time.sleep(1)
        bootLoad812.sendSyncAndSetup()
        time.sleep(1)
        bootLoad812.sendFirmware('PangeaBMS_LPC812.bin')
        time.sleep(1)
        bootLoad812.sendGoCommand()
    else:
        print 'Failed to receive bootloader response'
 
 
#----------------------------------------------------------------------
def getStatus(idNum):
    bootLoad812.flushReadBuffer()
    bootLoad812.BMSgetStatus(idNum)
    time.sleep(1)
    print bootLoad812.checkRepsonse()

#----------------------------------------------------------------------

def changeAddress(idFrom, idTo):
    bootLoad812.flushReadBuffer()
    bootLoad812.BMSchangeAddress(idFrom, idTo)
    time.sleep(1)
    print bootLoad812.checkRepsonse()


#----------------------------------------------------------------------

if __name__ == '__main__':
    #RAM_ADDR    = 0x10000300q
    #PAGE_SIZE   = 0x40
    #SECTOR_SIZE = 0x400
    #FLASH_SIZE  = 0x4000     
    
    bootLoad812 = LPC8xx_Bootloader.LPC8xx_Bootloader(0x10000300, 0x40, 0x400, 0x4000)
    #bootLoad812.openPort('/dev/tty.usbserial-FTVSIABB', 57600)
    bootLoad812.openPort('/dev/tty.usbserial-FTVSD4UR', 57600)
    
    targetID = 27
    
    changeAddress(99, targetID)
    getStatus(targetID)
    
    #getStatus(99)
    #changeAddress(99, 1)
    
    bootLoad812.closePort()