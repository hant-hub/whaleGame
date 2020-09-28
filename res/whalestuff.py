from pyglet import *
import math
from res.util import visibleEntity



class Player(visibleEntity):

	def __init__(self, pos, size, speed, handler, batch):
		super().__init__(pos,size)



		#setup sprite
		self.rec = shapes.Rectangle(*pos, *size, color=(255, 255, 255), batch=batch)

		self.rec.anchor_x = (self.rec.width/3) * 2
		self.rec.anchor_y = (self.rec.height/2)


		#setup movment
		self.vel = (0,0)
		self.speed = speed
		self.handler = handler
		self.turnspeed = 0.1

		#setup basic attack
		self.ram = False
		self.damage = True

		#health
		self.maxhealth = 100
		self.health = 100



	def update(self, dt):

		
		tx,ty = self.handler.target
		x, y = self.pos
		dx, dy = self.vel
		cx, cy = self.camera.pos

		#preprocess target

		tx -= cx
		ty -= cy



		if self.ram == True:
			x, y, dx, dy = self.Ram.ram(pos = (x, y), vel = (dx, dy), speed = self.speed, dt = dt)

		else:
			x, y, dx, dy = self.basicmovement(pos = self.pos, vel = self.vel, target = (tx,ty), dt = dt)


		

		#apply rotation

		rotation = math.degrees(math.atan2(dy, dx))

		self.updatevisual(sprite = self.rec, rotation = -rotation)

		self.pos = (x,y)
		self.vel = (dx,dy)
		


	def basicmovement(self, pos, vel, target, dt):


		tx, ty = target
		x, y = pos
		dx, dy = vel

		#create target velocity
		tdx = (tx - x)
		tdy = (ty - y)



		#update velocity

		dx += (tdx - dx) * self.turnspeed * self.speed
		dy += (tdy - dy) * self.turnspeed * self.speed




		#update position

		x += dx * dt
		y += dy * dt

		return (x,y,dx,dy)


	def hit(obj):

		pass



	class Ram:

		def ramStart(parent):

			#set flags
			parent.ram = True
			parent.damage = False

			#grab relevant information
			x, y = parent.pos
			tx,ty = parent.handler.target
			cx, cy = parent.camera.pos

			#preprocess target
			tx -= cx
			ty -= cy

			#initilize velocity
			#dist = math.dist([x,y],[tx,ty])

			parent.vel = ( (tx - x), (ty - y) )

			#set end
			clock.schedule_once(Player.Ram.ramEnd, 0.3, parent)

		def ramEnd(dt, parent):
			#reset data
			parent.ram = False
			parent.damage = True
			


		def ram(pos, vel, speed, dt):
			#unpack data
			x, y = pos
			dx, dy = vel

	
	
			#apply movement
			x += dx * speed * dt * 3
			y += dy * speed * dt * 3

			return (x,y, dx, dy)





