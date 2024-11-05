import time

TOO_CLOSE = 5

def get_ultrasonic_distance():
    arduino.write(b's')
    arduino.write(cma.encode('utf-8'))
    time.sleep(0.01)
    rep = arduino.readline()  		# on lit le message de réponse
    while rep==b'':					# On attend d'avoir une vraie réponse
        rep = arduino.readline()  	# on lit le message de réponse   
    return int(rep.decode())

def detect_obs(m = TOO_CLOSE) :
    distance = get_ultrasonic_distance
    return distance<TOO_CLOSE




















"""
this seems to be completely worthless
def AttAcquit():
    rep=b''
    while rep==b'':					# attend l'acquitement du B2
        rep=arduino.readline()
    return rep                      #pas sur de cette ligne...
    #print(rep.decode())

def resetENC():
    envoiCmdi(b'B',0,0,0,0)         #faudra probablement changer les lettres a l'interieur
"""