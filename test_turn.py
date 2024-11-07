from car_lib import *
import logging
from time import sleep

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
# Initialize the Urkab
logging.debug("Initializing Urkab...")
urkab = Urkab()
urkab.carDeactivateEmergencyStop()


logging.debug("Are the encoders working? Trying reset...")
urkab.resetEncoders()
logging.debug("Encoders reset.")

sleep(1)

logging.debug("Getting the current encoder values...")
encoders = urkab.getEncoders()
logging.debug(f"Encoder values: {encoders}")

# Turn right
logging.debug("Turning right...")
urkab.executeDirection("right")
sleep(2)

# Turn left
logging.debug("Turning left...")
urkab.executeDirection("left")
sleep(2)

# Do a 180 turn
logging.debug("Doing a 180 turn...")
urkab.executeDirection("do_a_flip")

logging.debug("Done!")