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
        logging.debug(f"Decoded word is: {decoded}, needs to be converted to int: {intresp}")
        return decoded


    def resetENC(self):
        self.envoiCmdi(b'B', 0, 0, 0, 0)


    def carStop(self):
        self.envoiCmdi(b'C', 0, 0, 0, 0)


    def carStopS(self):
        self.envoiCmdi(b'D', 0, 0, 20, 0);


    def carAdvance(self, v1, v2):
        self.envoiCmdi(b'C', v1, v2, 0, 0)

    def AttAcquit(self, intresp=False):
        rep = b''
        while rep == b'':
            rep = self.arduino.readline()
        logging.debug(f"Acquitted response is: {rep}")

        if rep.startswith(b"OB"):  # Check for obstacle-related messages
            error_message = rep.decode().strip()  # Decode the response and strip whitespace
            logging.error(f"Obstacle detected: {error_message}")
            raise Exception(f"Obstacle detected: {error_message}")

        if not intresp:
            decoded = rep.decode()
        else:
            decoded = int(rep[0])

        logging.debug(f"Decoded word is: {decoded}, needs to be converted to int: {intresp}")
        return decoded

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

    def executeDirection(self, command):
        """Map direction commands to motor actions, checking for obstacles on the opposite side before turning."""
        logging.info(f"Executing direction: {command}")

        # Check for obstacles on the opposite side before executing a turn
        if command == "left":
            if self.checkObstacle(180):  # Check right side (0 degrees) before turning left
                logging.error("Obstacle detected on the right; cannot turn left.")
                return "Error: Obstacle detected on the right"
        elif command == "right":
            if self.checkObstacle(0):  # Check left side (180 degrees) before turning right
                logging.error("Obstacle detected on the left; cannot turn right.")
                return "Error: Obstacle detected on the left"

        # Proceed with command if no obstacle is detected on the opposite side
        if command == "straight":
            self.carAdvance(250, 250)  # Move forward
        elif command == "left":
            self.carTurnLeft(250, 250)  # Turn left
            time.sleep(0.7)
        elif command == "right":
            self.carTurnRight(250, 250)  # Turn right
            time.sleep(0.7)
        elif command == "do_a_flip":
            self.carTurnRight(250, 250)
            time.sleep(1.2)
        else:
            self.carStop()  # Stop if no command

    def checkObstacle(self, angle):
        """Move ultrasonic to the specified angle and check for obstacles within range."""
        self.moveUltrasonic(angle)
        time.sleep(0.1)  # Small delay to allow ultrasonic to position
        distance = self.getUltrasonicDistance()  # Assume this function returns distance reading
        return distance < 110  # Return True if obstacle is within 110 units

    def getUltrasonicDist(self):
        self.arduino.write(b's')
        resp = self.AttAcquit(intresp=True)
        return int(resp)

    def moveUltrasonic(self, angle):
        self.envoiCmdi(b'G', angle, 0, 0, 0)

    def carDisconnect(self):
        self.arduino.write(b'a')  # deconnection de la carte
        self.arduino.close()  # fermeture de la liaison série
        logging.info("Arduino disconnected")

    def __del__(self):
        self.carDisconnect()
