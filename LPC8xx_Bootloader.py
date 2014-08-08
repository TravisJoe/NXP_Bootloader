
import serial
import time
import array
import os


class LPC8xx_Bootloader:
    
    serialPort = None
    
    portIsOpen = False
    
    #Listen and check response from MCU during ISP commands
    ISPisListing = False
    
    #Delay between sent packets in secons if not listening for response
    noResponseDelay = 0.01
    
    addressRam = 0
    sizePage = 0
    sizeSector = 0
    sizeFlash = 0
    
#===================================================================== Init    
    def __init__(self, addressRAM, sizePage, sizeSector, sizeFlash):
        
        #Pass paramters to class variables
        self.addressRam = addressRAM
        self.sizePage = sizePage
        self.sizeSector = sizeSector
        self.sizeFlash = sizeFlash
    
#===================================================================== Open serial port
    def openPort(self, portName, portSpeed):
        if(self.portIsOpen == False):
            try:
                self.serialPort = serial.Serial(portName, portSpeed, timeout=0.01)
                self.serialPort.open()
                self.portIsOpen = True
            except:
                print 'failed to open serial port '

#===================================================================== Close serial port          
    def closePort(self):
        if(self.portIsOpen == True):
            try:
                self.serialPort.close()
                self.portIsOpen = False
                return True
            except:
                print 'failed ot close serial port'
                return False
            
#=====================================================================  Send ISP command to MCU
    def sendISPcommand(self, ID):
        
        print 'Sending ISP start command'
        
        try:
            #self.serialPort.write('command')
            #build packet
            return True
        except:
            print 'ISP start command failed to send'
            return False

#===================================================================== Send Syncronize and setup messages
    def sendSyncAndSetup(self):
        
        print 'Syncing'
        
        try:
            
            self.serialPort.write('?')
            if(self.ISPisListing == True):
                #Deal with response
                pass
            else:
                #Just wait 
                time.sleep(self.noResponseDelay)
                
            self.serialPort.write('Synchronized\r\n')
            if(self.ISPisListing == True):
                #Deal with response
                pass
            else:
                #Just wait 
                time.sleep(self.noResponseDelay)

            self.serialPort.write('12000\r\n')
            if(self.ISPisListing == True):
                #Deal with response
                pass
            else:
                #Just wait 
                time.sleep(self.noResponseDelay)
                
            self.serialPort.write('A 0\r\n')
            if(self.ISPisListing == True):
                #Deal with response
                pass
            else:
                #Just wait 
                time.sleep(self.noResponseDelay)               
                
            self.serialPort.write('J\r\n')
            if(self.ISPisListing == True):
                #Deal with response
                pass
            else:
                #Just wait 
                time.sleep(self.noResponseDelay)  
                
            self.serialPort.write('U 23130\r\n')
            if(self.ISPisListing == True):
                #Deal with response
                pass
            else:
                #Just wait 
                time.sleep(self.noResponseDelay)
                
            self.serialPort.write('P 0 7\r\n')
            if(self.ISPisListing == True):
                #Deal with response
                pass
            else:
                #Just wait 
                time.sleep(self.noResponseDelay)                  
                
            self.serialPort.write('E 0 7\r\n')
            if(self.ISPisListing == True):
                #Deal with response
                pass
            else:
                #Just wait 
                time.sleep(self.noResponseDelay)
                
        except:
            print 'sendSyncAndSetup failed'
                
#===================================================================== Send Firmware
    def sendFirmware(self, firmwareName):
        
        print 'Sending firmware'
        continueFirmwareUpdate = True
        
        firmwareSize = os.stat(firmwareName).st_size
        
        #create array with type byte
        firmwareAsArray = array.array('B')
        
        #Load file and put data into array
        try:
            loadFile = file(firmwareName, 'rb')
        except:
            print 'Firmware failed to load'
            continueFirmwareUpdate = False
        
        try:
            firmwareAsArray.fromfile(loadFile, firmwareSize)
        except:
            print 'failed to load file into array'
            continueFirmwareUpdate = False
            
        loadFile.close()
        
        if(continueFirmwareUpdate == True):
            #Fills the remaining page of data with 0xff. 
            firmwareAsArray.fromstring( chr(0xff)*(self.sizePage - (firmwareAsArray.buffer_info()[1]%self.sizePage)) )
            
            #Calcuate checksums
            csum = 0;
            for i in range(7):
                    csum = csum + \
                    (firmwareAsArray[(i*4)]      ) + \
                    (firmwareAsArray[(i*4)+1]<<8 ) + \
                    (firmwareAsArray[(i*4)+2]<<16) + \
                    (firmwareAsArray[(i*4)+3]<<24); \
            
            csum = -csum
            firmwareAsArray[28] = csum     & 0xff
            firmwareAsArray[29] = csum>>8  & 0xff
            firmwareAsArray[30] = csum>>16 & 0xff
            firmwareAsArray[31] = csum>>24 & 0xff
            
            address = 0
            
            while firmwareAsArray.buffer_info()[1]:
                
                # Write
                self.serialPort.write( "W %d %d\r\n"%(self.addressRam, self.sizePage) )
                if(self.ISPisListing == True):
                    #Deal with response
                    pass
                else:
                    #Just wait 
                    time.sleep(self.noResponseDelay)
        
                #Write bulk of data
                for i in range(self.sizePage):
                        self.serialPort.write( chr(firmwareAsArray.pop(0)) )
                        time.sleep(self.noResponseDelay)
    
                #print('P %x %x\r\n'%( address/self.sizeSector, address/self.sizeSector ))
                #print('C %x %x 0xff\r\n'%( address, self.addressRam ))
        
                ## Program page
                self.serialPort.write('P %d %d\r\n'%( address/self.sizeSector, address/self.sizeSector ))
                if(self.ISPisListing == True):
                    #Deal with response
                    pass
                else:
                    #Just wait 
                    time.sleep(self.noResponseDelay)
        
                self.serialPort.write( 'C %d %d %d\r\n'%(address, self.addressRam, self.sizePage) )
                if(self.ISPisListing == True):
                    #Deal with response
                    pass
                else:
                    #Just wait 
                    time.sleep(self.noResponseDelay)
        
                print '.',
                address = address + self.sizePage
                if (address%self.sizeSector) == 0:
                        print ''
        else:
            print 'Did not continue to upload new firmware'
    
    
#===================================================================== Send Go Command  
    def sendGoCommand(self):
        
        print 'Sending GO command'
        
        self.serialPort.write('G 0 T\r\n')
        if(self.ISPisListing == True):
            #Deal with response
            pass
        else:
            #Just wait 
            time.sleep(self.noResponseDelay)   
            
    #----------------------------------------------------------------------        
    def BMSgetStatus(self,ID):
        
        
        buildPacket = ''
        buildPacket = buildPacket + str(ID).zfill(2) # convert int value to ASCII for ID number
        buildPacket = buildPacket + 'S' # Direction = Send
        buildPacket = buildPacket + 'S' # Command = Status
        buildPacket = buildPacket + '000000000000'
        
        
        buildPacket = buildPacket + self._BMSCRC(buildPacket)
        
        buildPacket = '{' + buildPacket + "}"
        
        self.serialPort.write(buildPacket)
        
    #----------------------------------------------------------------------
    def BMSbootloaderStart(self,ID):
        buildPacket = ''
        buildPacket = buildPacket + str(ID).zfill(2) # convert int value to ASCII for ID number
        buildPacket = buildPacket + 'S' # Direction = Send
        buildPacket = buildPacket + 'B' # Command = bootloader
        buildPacket = buildPacket + '000000000000' # Packet fill
        
        
        buildPacket = buildPacket + self._BMSCRC(buildPacket)
        
        buildPacket = '{' + buildPacket + "}"
        
        self.serialPort.write(buildPacket)
        
    #----------------------------------------------------------------------
    def BMSchangeAddress(self, intoID, fromID):
        buildPacket = ''
        buildPacket = buildPacket + str(intoID).zfill(2) # convert int value to ASCII for ID number
        buildPacket = buildPacket + 'S' # Direction = Send
        buildPacket = buildPacket + 'A' # Command = bootloader
        buildPacket = buildPacket + str(fromID).zfill(2) # Command = bootloader
        buildPacket = buildPacket + '0000000000' # Packet fill
        
        
        buildPacket = buildPacket + self._BMSCRC(buildPacket)
        
        buildPacket = '{' + buildPacket + "}"
        
        self.serialPort.write(buildPacket)        
        
    #----------------------------------------------------------------------
    def _BMSCRC(self, packet):
        
        # Base value of CRC
        crc_int = 0;
        
        # Iterate through packet and calculate CRC
        for char in packet:
            # Bitshift CRC value to the left 1 and then exclusive or with the next character. 
            crc_int = (crc_int << 1) ^ ord(char) #value comes from ascii character value
            if crc_int > 511:
                crc_int = crc_int - 512
        
        return str(crc_int).zfill(3)
    
    def checkRepsonse(self):
        returnPacket = self.serialPort.read(24)
        print returnPacket
        returnPacket = returnPacket[returnPacket.find("{"):returnPacket.find('}')+1]
        return returnPacket
    
    def flushReadBuffer(self):

        count = 1
        
        while(count > 0):
            count = self.serialPort.inWaiting()
            if(count < 0):
                count = 0
            self.serialPort.read(count)
            time.sleep(.01)
        
        
        