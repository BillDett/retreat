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


DISPLAY = pi3d.Display.create()
DISPLAY.set_background(0.0,0.0,0.0,1) # Black

CAM = pi3d.Camera(eye=(0.0, 0.0, -7.0))

backplaneZ = 0

lights = pi3d.Light(lightamb = (0.8, 0.8, 0.9))

shader = pi3d.Shader('uv_light')
earthimg = pi3d.Texture('planet.jpg')
isdlogo = pi3d.Texture('imperialseal-100px.png')

logo = pi3d.ImageSprite(isdlogo, shader)
ball = pi3d.Sphere(sides=24, slices=24)

# "Pins" around the globe showing the Unobtanium mining operations
pinGoodColor = (129/255, 220/255, 247/255)		# Light Blue
pinBadColor = (252/255, 106/255, 28/255)		# Dark Orange
pinDestroyColor = (252/255, 28/255, 28/255)		# Red
pins = []
num_pins = 45
for p in range(num_pins):
	pin = pi3d.Lines(vertices=[(0.0, 0.0, 0.0), randomPoint(1.25)])
	pin.set_material(pinDestroyColor)
	pins.append(pin)

# Speed of planet rotation
rot = -0.05
#rot = -0.5

# listen for keystrokes
mykeys = pi3d.Keyboard()

while DISPLAY.loop_running():
	# store keystrokes
	k = mykeys.read()
	if k == 27: # ESC
		mykeys.close()
		DISPLAY.destroy()
		break
	logo.position(4.5, 2.0, backplaneZ)
	logo.draw()
	ball.draw(shader, [earthimg])
	ball.rotateIncY(rot)
	for pin in pins:
		pin.draw()
		pin.rotateIncY(rot)
