import time
from Scribbler2 import *

# Connect to the scribbler
# Set timeout to 0 to read instantly, non-blocking

fname = "log-%d.txt" % time.time()

s = Scribbler2('/dev/tty.Fluke2-07DE-Fluke2',fname)

# Set timeout to zero
print 'Connected!'
s.setIRPower(140)
s.setForwardness(1)
# Create a list of commands
# Command is a list [cmd, leftMotor, rightMotor, time]
# Setting motors to 200 will drive 
# forward with the fluke facing forward

## Take picture
pic_fname = "pic-%d.jpg" % time.time()
picture = s.takePicture('jpeg');
s.savePicture(picture, pic_fname)


# Run the robot again
s.runCommands();


## Take picture
pic_fname = "pic-%d.jpg" % time.time()
picture = s.takePicture('jpeg');
s.savePicture(picture, pic_fname)


## Close (Do not remove this line)
s.close();
