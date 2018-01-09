import pi3d
import RPi.GPIO as GPIO
import os
import threading
import subprocess
import signal
import time
import serial
from random import random, randint
from numpy import arccos, cos, sin, radians, pi


def stop_background():
	global background
	os.killpg(os.getpgid(background.pid), signal.SIGTERM)

# Generate a random point around a sphere with given radius
def randomPoint(radius):
	u1 = random()
	u2 = random()
	latitude = arccos(2*u1 - 1) - pi/2
	longitude = 2*pi*u2
	x = cos(latitude) * cos(longitude) * radius
	y = cos(latitude) * sin(longitude) * radius
	z = sin(latitude) * radius
	return (x, y, z)

# Take 25% of the stations offline
def downgradePins(pins):
	global num_stations
	global num_online_stations
	global num_offline_stations
	count = int(num_stations * 0.25)
	num_online_stations -= count
	num_offline_stations += count
	print('Online: ' + str(num_online_stations) + ' offline: ' + str(num_offline_stations))
	for p in pins:
		if count > 0 and p['status'] == GOOD:
			p['status'] = DESTROY
			p['line'].set_material(pinDestroyColor)
			count -= 1


# Handles the listener for callback from Arduino that door should be unlocked
unlock_door = False
class ArduinoListener( threading.Thread ):
	def __init__( self ):
		super(ArduinoListener, self).__init__()
		# Open Serial port to talk to Arduino
		self.ser = serial.Serial('/dev/ttyACM0', 9600)

	def run( self ):
		global unlock_door
		serinput = self.ser.read()
		if serinput.decode("utf-8") == "Y":
			print("Got response from Arduino")
			unlock_door = True
			# Add the handlers for the chamber triggers- make them "live"
			GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			GPIO.setup(button3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			GPIO.setup(button4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			GPIO.add_event_detect(button1, GPIO.FALLING, callback=button_pressed, bouncetime=300)
			GPIO.add_event_detect(button2, GPIO.FALLING, callback=button_pressed, bouncetime=300)
			GPIO.add_event_detect(button3, GPIO.FALLING, callback=button_pressed, bouncetime=300)
			GPIO.add_event_detect(button4, GPIO.FALLING, callback=button_pressed, bouncetime=300)

def coll_rate_string():
	return 'COLLECTION RATE: ' + str(collection_rate) + '%'

def coll_amount_string():
	return 'AMOUNT COLLECTED: ' + "{0:.2f}".format(collection_amount) + ' units'

def current_time_millis():
    return int(round(time.time() * 1000))

def draw_samplerate():
	global sr_index
	global sr_time
	global explosion
	if not explosion:
		# Time to change sr_index?
		now = current_time_millis()
		if (now - sr_time) > 500:
			sr_index += 1
			sr_time = now
			if sr_index > 3:
				sr_index = 1

		if sr_index == 1:
			samplerate1.draw()
		elif sr_index == 2:
			samplerate2.draw()
		else:
			samplerate3.draw()

def button_pressed(channel):
	global button1_pressed
	global button2_pressed
	global button3_pressed
	global button4_pressed
	global explosion
	global collection_rate
	global overloading
	if channel == button1:
		if not button1_pressed:
			print("BUTTON1")
			downgradePins(pins)
			os.system('aplay deploy.wav &')
		button1_pressed = True
	elif channel == button2:
		if not button2_pressed:
			print("BUTTON2")
			downgradePins(pins)
			os.system('aplay deploy.wav &')
		button2_pressed = True
	elif channel == button3:
		if not button3_pressed:
			print("BUTTON3")
			downgradePins(pins)
			os.system('aplay deploy.wav &')
		button3_pressed = True
	elif channel == button4:
		if not button4_pressed:
			print("BUTTON4")
			downgradePins(pins)
			os.system('aplay deploy.wav &')
		button4_pressed = True

	if button1_pressed and button2_pressed and button3_pressed and button4_pressed:
		print("BOOM!")
		time.sleep(1)
		if not explosion:
			overloading = current_time_millis()
			os.system('aplay finale.wav')
			# TODO: FLASH WARNING OVER DISPLAY NEED TO THINK HOW TO DO THAT!!
			stop_background()
			os.system('aplay explosion.wav')
			collection_rate = 0
			explosion = True


# Set up buttons
button1 = 25
button2 = 23
button3 = 21
button4 = 16

# Pin to trigger chamber
chamberPin = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.add_event_detect(button1, GPIO.FALLING, callback=button_pressed, bouncetime=300)
GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.add_event_detect(button2, GPIO.FALLING, callback=button_pressed, bouncetime=300)
GPIO.setup(button3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.add_event_detect(button3, GPIO.FALLING, callback=button_pressed, bouncetime=300)
GPIO.setup(button4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.add_event_detect(button4, GPIO.FALLING, callback=button_pressed, bouncetime=300)

GPIO.setup(chamberPin, GPIO.OUT)

button1_pressed = False
button2_pressed = False
button3_pressed = False
button4_pressed = False

explosion = False		# Has the explosion occured? 
overloading = 0			# We're in overload mode

# Set up the environment
DISPLAY = pi3d.Display.create()
#DISPLAY = pi3d.Display.create(w=800, h=600)	# For debugging
DISPLAY.set_background(0.0,0.0,0.0,1) # Black
CAM = pi3d.Camera(eye=(0.0, 0.0, -7.0))
CAM2D = pi3d.Camera(is_3d=False)
lights = pi3d.Light(lightamb = (0.8, 0.8, 0.9))
shader = pi3d.Shader('uv_light')
flatshader = pi3d.Shader("uv_flat")
fontfile = '/home/pi/pi3d_demos-master/fonts/NotoSans-Regular.ttf'
font = pi3d.Font(fontfile, font_size=32, color=(255,255,255,255))
font.blend = True

xmargin = DISPLAY.width * 0.05
ymargin = DISPLAY.height * 0.05
topleftx = DISPLAY.width/-2 + xmargin	# Top left corner starting X coordinate for stuff
toplefty = DISPLAY.height/2 - ymargin	# Top left corner starting Y coordinate for stuff

backplaneZ = 0

# Mining "Stats"
num_stations = 120
num_online_stations = num_stations
num_stopping_stations = 0
num_offline_stations = 0
collection_rate = 100
collection_amount = 16834

# Planet
earthimg = pi3d.Texture('planet.jpg')
ball = pi3d.Sphere(sides=24, slices=24)

# Imperial Logo
isdlogo = pi3d.Texture('imperialseal-100px.png')
logo = pi3d.ImageSprite(isdlogo, shader)
logo.position(4.0, 2.0, backplaneZ)

# Title
mytext="UNOBTANIUM MINING COMMAND CONSOLE"
title = pi3d.FixedString(fontfile, mytext, font_size=48, camera=CAM2D, shader=flatshader, f_type='SMOOTH', justify='L')
tx = topleftx + title.sprite.width/2
ty = toplefty - title.sprite.height/2
title.sprite.position(tx, ty, backplaneZ)

# Collection Amount
collamt = pi3d.String(font=font, string=coll_amount_string(), x=-1.45, y=1.00, z=-3 )
collamt.set_material((1.0, 1.0, 1.0))
collamt.set_shader(shader)

# Collection Rate
ymargin = DISPLAY.height * 0.25
collrate = pi3d.String(font=font, string=coll_rate_string(), x=-1.75, y=0.75, z=-3 )
collrate.set_material((1.0, 1.0, 1.0))
collrate.set_shader(shader)

# Status Indicator
statusimg = pi3d.Texture('status.png')
status = pi3d.ImageSprite(statusimg, shader)
status.position(-3.0, 0.45, backplaneZ-1)
online = pi3d.String(font=font, string='999', x=-2.70, y=0.65, z=backplaneZ-1 )
online.set_material((1.0, 1.0, 1.0))
online.set_shader(shader)
stopping = pi3d.String(font=font, string='999', x=-2.70, y=0.45, z=backplaneZ-1 )
stopping.set_material((1.0, 1.0, 1.0))
stopping.set_shader(shader)
offline = pi3d.String(font=font, string='999', x=-2.70, y=0.25, z=backplaneZ-1 )
offline.set_material((1.0, 1.0, 1.0))
offline.set_shader(shader)

# "Sample Rate" - bogus scrolling bar chart 
samplerate1img = pi3d.Texture('samplerate.png')
samplerate1 = pi3d.ImageSprite(samplerate1img, shader)
samplerate1.position(-2.6, -0.65, backplaneZ-1.8)
samplerate2img = pi3d.Texture('samplerate2.png')
samplerate2 = pi3d.ImageSprite(samplerate2img, shader)
samplerate2.position(-2.6, -0.65, backplaneZ-1.8)
samplerate3img = pi3d.Texture('samplerate3.png')
samplerate3 = pi3d.ImageSprite(samplerate3img, shader)
samplerate3.position(-2.6, -0.65, backplaneZ-1.8)
sr_index = 1
sr_time = current_time_millis()

# Lower Right Greeblie
# TODO: "AMR STAT" - bogus list of floating point numbers scrolling infinitely


# OVERLOAD warning flasher
overloadimg = pi3d.Texture('overload.png')
overload = pi3d.ImageSprite(overloadimg, shader)
overload.position(0, 0, backplaneZ-6)

# OFFLINE message
offlineimg = pi3d.Texture('offline.png')
we_are_offline = pi3d.ImageSprite(offlineimg, shader)
we_are_offline.position(0, 0, backplaneZ-6)

# "Pins" around the globe showing the Unobtanium mining operations
# Each Pin is a tuple of a pi3d.Lines and a status
pinGoodColor = (129/255, 220/255, 247/255)		# Light Blue
pinDestroyColor = (252/255, 28/255, 28/255)		# Red
GOOD = 0
BAD = 1
DESTROY = 2
pins = []

# Generate initial set of Pins
for p in range(num_stations):
	pin = {'line': pi3d.Lines(vertices=[(0.0, 0.0, 0.0), randomPoint(1.25)]), 'status': GOOD}
	pin['line'].set_material(pinGoodColor)
	pins.append(pin)

# Speed of planet rotation
rot = -0.15
#rot = -0.5

# listen for keystrokes
mykeys = pi3d.Keyboard()

# Start the background machine noise
#os.system('omxplayer --no-osd --no-keys --loop machine.wav &')
background = subprocess.Popen(['omxplayer', '--no-osd', '--no-keys', '--loop', 'machine.wav'],preexec_fn=os.setsid)

# Start listening to the Arduino
al = ArduinoListener()
al.start()
#unlock_door = True 	# TAKE THIS OUT!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Here's where all the action happens
while DISPLAY.loop_running():
	# store keystrokes
	k = mykeys.read()
	if k == 27: # ESC
		mykeys.close()
		stop_background()
		GPIO.output(chamberPin, 0)	# UnTrigger the chamber
		GPIO.cleanup()
		DISPLAY.destroy()
		break
	
	# Did we get a message from Arduino to open the door?
	if unlock_door:
		GPIO.output(chamberPin, 1)	# Trigger the chamber
		unlock_door = False
	
	collection_amount += (-1 * rot)

	# Draw everything
	logo.draw()
	status.draw()
	draw_samplerate()
	title.draw()
	collrate.draw()
	collamt.draw()
	online.draw()
	stopping.draw()
	offline.draw()
	ball.draw(shader, [earthimg])
	if not explosion:
		collrate.quick_change(coll_rate_string())
		collamt.quick_change(coll_amount_string())
		online.quick_change(str(num_online_stations))
		stopping.quick_change(str(num_stopping_stations))
		offline.quick_change(str(num_offline_stations))
		ball.rotateIncY(rot)
	for pin in pins:
		pin['line'].draw()
		if not explosion:
			pin['line'].rotateIncY(rot)

	if not explosion and not overloading == 0:
		now = current_time_millis()
		delta = now - overloading
		if  delta > 1000 and delta < 2000:
			overload.draw()
		if delta > 2000:
			overloading = now

	if explosion:
		GPIO.output(chamberPin, 0)	# UnTrigger the chamber
		we_are_offline.draw()
