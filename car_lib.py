import serial
import time
import struct
import logging

class Urkab():

    def __init__(self):
        self.arduino = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.1)
        self.ultrasonicDist = 0

        rep = ' '  # serial connection validation
        while rep != b'':
            rep = self.arduino.readline()
        logging.debug("Validating connection...")

        time.sleep(2)

        self.arduino.write(b'A22')
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


    def AttAcquit(self, intresp=False):
        rep = b''
        while rep == b'':
            rep = self.arduino.readline()
        logging.debug(f"Acquitted response is: {rep}")
        if not intresp:
            decoded = rep.decode()
        else:
            decoded = int(rep[0])
        logging.info(f"Decoded word is: {decoded}, needs to be converted to int: {intresp}")
        return decoded


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

    def carDeactivateEmergencyStop(self):
        self.arduino.write(b'I0')
        self.AttAcquit()

    def carResetEmergencyStop(self):
        self.arduino.write(b'I1')
        self.AttAcquit()

    def getUltrasonicDist(self):
        self.arduino.write(b's')
        resp = self.AttAcquit(intresp=True)
        self.ultrasonicDist = int(resp)
        return self.ultrasonicDist

    def moveUltrasonic(self, angle):
        self.envoiCmdi(b'G', angle, 0, 0, 0)

    def carDisconnect(self):
        self.arduino.write(b'a')  # deconnection de la carte
        self.arduino.close()  # fermeture de la liaison série
        logging.info("Arduino disconnected")

    def avoid_obstacles(self):
        if self.ultrasonicDist < 15:
            self.carStop()

    def __del__(self):
        self.carDisconnect()
