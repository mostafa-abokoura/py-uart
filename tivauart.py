# usbtiva

import datetime
import threading
import serial.tools.list_ports

DEVICE = "Stellaris Virtual Serial Port"
NO_COM = "COM"
BAUD_RATE = 115200

TIMER0_TIME = 0.1
TIMER1_TIME = 0.01

def decode(msg):
    lst, msg = list(msg), ''
    for i in lst:
        msg += ('%02x' % i).upper() + ' '
    return msg

    
class communication:
    def __init__(self):
        self.serEstablished, self.isConnected, self.com = False, False, NO_COM
        self.msgs, self.ser, self.store = [], None, True

        self.InitTimers()

    def t0_KeepAlive(self):
        self.KeepAlive()
        
        if self.isConnected and not self.serEstablished:
            try:
                self.ser = serial.Serial(self.com, BAUD_RATE, timeout=1)
                self.serEstablished = True
                threading.Timer(TIMER1_TIME, self.t1_StoreData).start()
                print("COM Status: Connected")
            except:
                print("COM Status: Serial Error (device not responding)")
        elif not self.isConnected and self.serEstablished:
            self.serEstablished = False
            self.ser.close()
            print("COM Status: Disconnected")
            
        threading.Timer(TIMER0_TIME, self.t0_KeepAlive).start()

    def t1_StoreData(self):
        if self.isConnected:
            char = b''
            try:
                char = self.ser.read()
            except:
                self.isConnected = False
            if len(char) > 0:
                time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                count, msg = ord(char.decode('utf8')), b''
                while count:
                    try:
                        msg += self.ser.read()
                    except:
                        print('Serial Status: Error recieving')
                        break
                    count -= 1
                print('Received at %s:' % time, decode(msg))
                if self.store:
                    self.msgs.append((time, msg))
                
            threading.Timer(TIMER1_TIME, self.t1_StoreData).start()
        else:
            pass

    def Dequeue(self):
        if len(self.msgs):
            return self.msgs.pop(0)
        else:
            return None

    def InitTimers(self):
        threading.Timer(TIMER0_TIME, self.t0_KeepAlive).start()

    def KeepAlive(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if (port.description[:len(DEVICE)] == DEVICE):
                self.isConnected, self.com = True, port.device
                return
        self.isConnected, self.com = False, NO_COM

    def setStore(self, flag):
        self.store = flag


if __name__ == "__main__":
    communication()
