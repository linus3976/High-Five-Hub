import serial
import time
import struct
import logging

class Urkab():

    def __init__(self):
        self.arduino = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.1)

        rep = ' '  # serial connection validation
        while rep != b'':
            rep = self.arduino.readline()
        logging.debug("Validating connection...")

        time.sleep(2)  # on attend 2s pour que la carte soit initialisée

        self.arduino.write(b'A22')  # demande de connection avec acquitement par OK
        rep = self.arduino.readline()
        if rep.split()[0] == b'OK':
            logging.info("Arduino connected")
        else:
            logging.critical("Arduino connection not returning ok")

    def read_i16(self, f):
        return struct.unpack('<h', bytearray(f.read(2)))[0]


    def read_i32(self, f):
        return struct.unpack('<l', bytearray(f.read(4)))[0]


    def write_i16(self, f, value):
        f.write(struct.pack('<h', value))


    def write_i32(self, f, value):
        f.write(struct.pack('<l', value))


    def envoiCmdi(self, cmd, arg1, arg2, arg3, arg4):
        self.arduino.write(cmd)
        self.write_i16(self.arduino, arg1)
        self.write_i16(self.arduino, arg2)
        self.write_i16(self.arduino, arg3)
        self.write_i16(self.arduino, arg4)
        self.AttAcquit()


    def envoiCmdl(self, cmd, arg1, arg2):
        self.arduino.write(cmd)
        self.write_i32(self.arduino, arg1)
        self.write_i32(self.arduino, arg2)
        self.AttAcquit()


    def recupCmdi(self, cmd):
        self.arduino.write(cmd)
        val1 = self.read_i16(self.arduino)
        val2 = self.read_i16(self.arduino)
        val3 = self.read_i16(self.arduino)
        val4 = self.read_i16(self.arduino)
        return val1, val2, val3, val4
        AttAcquit()


    def recupCmdl(self, cmd):
        self.arduino.write(cmd)
        val1 = self.read_i32(self.arduino)
        val2 = self.read_i32(self.arduino)
        return val1, val2
        AttAcquit()


    def AttAcquit(self):
        rep = b''
        while rep == b'':  # attend l'acquitement du B2
            rep = self.arduino.readline()
        print(rep.decode())


    def resetENC(self):
        self.envoiCmdi(b'B', 0, 0, 0, 0)


    def carStop(self):
        self.envoiCmdi(b'C', 0, 0, 0, 0)


    def carStopS(self):
        self.envoiCmdi(b'D', 0, 0, 20, 0);


    def carAdvance(self, v1, v2):
        self.envoiCmdi(b'C', v1, v2, 0, 0)


    def carAdvanceS(self, v1, v2, v3):
        self.envoiCmdi(b'D', v1, v2, v3, 0)


    def carBack(self, v1, v2):
        self.envoiCmdi(b'C', -v1, -v2, 0, 0)


    def carBackS(self, v1, v2, v3):
        self.envoiCmdi(b'D', -v1, -v2, v3, 0)


    def carTurnLeft(self, v1, v2):
        self.envoiCmdi(b'C', v1, -v2, 0, 0)


    def carTurnRight(self, v1, v2):
        self.envoiCmdi(b'C', -v1, v2, 0, 0)

    def carDisconnect(self):
        self.arduino.write(b'a')  # deconnection de la carte
        self.arduino.close()  # fermeture de la liaison série
        logging.info("Fin de programme")
