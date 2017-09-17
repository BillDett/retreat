import pi3d
from random import random, randint
from numpy import arccos, cos, sin, radians, pi

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

# Randomly 'downgrade' pins from GOOD->BAD->DESTROY
def downgradePins(pins, percentage):
	global num_online_stations
	global num_offline_stations
	global num_stopping_stations
	for p in pins:
		if random() <= percentage:		# We're going to degrade this Pin
			if p['status'] == GOOD:
				p['status'] = BAD
				p['line'].set_material(pinBadColor)
				num_online_stations -= 1
				num_stopping_stations += 1
			elif p['status'] == BAD:
				p['status'] = DESTROY
				p['line'].set_material(pinDestroyColor)
				num_stopping_stations -= 1
				num_offline_stations += 1

def coll_rate_string():
	return 'Collection Rate: ' + str(collection_rate) + '%'

# Set up the environment
DISPLAY = pi3d.Display.create()
DISPLAY.set_background(0.0,0.0,0.0,1) # Black
CAM = pi3d.Camera(eye=(0.0, 0.0, -7.0))
CAM2D = pi3d.Camera(is_3d=False)
lights = pi3d.Light(lightamb = (0.8, 0.8, 0.9))
shader = pi3d.Shader('uv_light')
flatshader = pi3d.Shader("uv_flat")
fontfile = '/home/pi/pi3d_demos-master/fonts/NotoSans-Regular.ttf'
font = pi3d.Font(fontfile, (221,0,170,255))
font.blend = True

xmargin = DISPLAY.width * 0.05
ymargin = DISPLAY.height * 0.05
topleftx = DISPLAY.width/-2 + xmargin	# Top left corner starting X coordinate for stuff
toplefty = DISPLAY.height/2 - ymargin	# Top left corner starting Y coordinate for stuff

backplaneZ = 0

# Mining "Stats"
num_stations = 75
num_online_stations = num_stations
num_stopping_stations = 0
num_offline_stations = 0
collection_rate = 100

# Planet
earthimg = pi3d.Texture('planet.jpg')
ball = pi3d.Sphere(sides=24, slices=24)

# Imperial Logo
isdlogo = pi3d.Texture('imperialseal-100px.png')
logo = pi3d.ImageSprite(isdlogo, shader)
logo.position(4.5, 2.0, backplaneZ)

# Title
mytext="Unobtanium Mining Command Console"
title = pi3d.FixedString(fontfile, mytext, font_size=48, camera=CAM2D, shader=flatshader, f_type='SMOOTH', justify='L')
tx = topleftx + title.sprite.width/2
ty = toplefty - title.sprite.height/2
title.sprite.position(tx, ty, backplaneZ)

# Collection Rate
# TODO: Why is it not showing as white?
# TODO: Sizing not correct- missing the '%'- smaller font?
ymargin = DISPLAY.height * 0.25
#collrate = pi3d.String(font=font, string="Collection Rate: 100%", x=topleftx, y=toplefty-ymargin )
collrate = pi3d.String(font=font, string=coll_rate_string(), x=-1.75, y=1.0, z=-3 )
collrate.set_material((1.0, 1.0, 1.0))
collrate.set_shader(shader)


# Station Status
# TODO: List out indicator of number of online, offline and stopping stations (green, amber, red)


# Lower Left Greeblie
# TODO: "Sample Rate" - bogus scrolling bar chart (lift code from Processing sketch)


# Lower Right Greeblie
# TODO: "AMR STAT" - bogus list of floating point numbers scrolling infinitely



# "Pins" around the globe showing the Unobtanium mining operations
# Each Pin is a tuple of a pi3d.Lines and a status
pinGoodColor = (129/255, 220/255, 247/255)		# Light Blue
pinBadColor = (252/255, 106/255, 28/255)		# Dark Orange
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
rot = -0.05
#rot = -0.5

# listen for keystrokes
mykeys = pi3d.Keyboard()

# TODO: Need to call downgradePins() via GPIO switches (see logic in notes)
while DISPLAY.loop_running():
	# store keystrokes
	k = mykeys.read()
	if k == 27: # ESC
		mykeys.close()
		DISPLAY.destroy()
		break
	elif k == 100:	# 'd'
		downgradePins(pins, 0.20)
	logo.draw()
	title.draw()
	collrate.draw()
	collection_rate *= (1-rot)
	collrate.quick_change(coll_rate_string())
	ball.draw(shader, [earthimg])
	ball.rotateIncY(rot)
	for pin in pins:
		pin['line'].draw()
		pin['line'].rotateIncY(rot)
