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
        d = int(resp)
        return d

    def moveUltrasonic(self, angle):
        self.envoiCmdi(b'G', angle, 0, 0, 0)

    def carDisconnect(self):
        self.arduino.write(b'a')  # deconnection de la carte
        self.arduino.close()  # fermeture de la liaison série
        logging.info("Arduino disconnected")

    def avoid_obstacles(self):
        d = self.getUltrasonicDist()
        print(f"Ultrasonic Values: {d}")
        distace_to_stop = 37
        if d < distace_to_stop:
            print(f"Car should stop here, entered the smaller than {distace_to_stop}")
            self.carStop()
            print("Car stopped")

            # Turn until way is clear
            self.carTurnLeft(150, 150)
            while self.getUltrasonicDist() < (distace_to_stop + 7):
                pass

            self.carStop()
            time.sleep(1)
            logging.debug("Car stopped, way should be clear")
            # Turn ultrasonic to right, go until we find and then loose the object
            self.moveUltrasonic(0)
            self.carAdvance(150, 150)
            while self.getUltrasonicDist() > (distace_to_stop + 7):
                pass
            self.carStop()
            time.sleep(1)
            self.carAdvance(150, 150)

            logging.debug("refound object")
            while self.getUltrasonicDist() < (distace_to_stop + 7):
                pass
            self.carStop()
            logging.debug("object lost")

            self.carAdvance(150, 150)
            time.sleep(0.7)
            self.carStop()

            # Turn ultrasonic to 70 (slightly right), turn until object is within field
            self.moveUltrasonic(60)
            self.carTurnRight(200, 200)
            while self.getUltrasonicDist() > (distace_to_stop + 7):
                pass
            logging.debug("refound object on my right, now going to refind the line, wait 1 sec")
            self.carStop()
            # Go until line is found
            self.carAdvance(150, 150)
            time.sleep(0.1)
            self.moveUltrasonic(90)

    def __del__(self):
        self.carDisconnect()
