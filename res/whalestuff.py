from pyglet import *
import math
from res.util import visibleEntity
from res.enemies import Enemy
from res.Projectiles import Harpoon



class Player(visibleEntity):

	def __init__(self, pos, size, speed, handler, batch):
		super().__init__(pos,size, shapes.Rectangle(*pos, *size, color=(255, 255, 255), batch=batch))



		#setup sprite


		self.sprite.anchor_x = (self.sprite.width/3) * 2
		self.sprite.anchor_y = (self.sprite.height/2)


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

		#death flag
		self.alive = True



	def update(self, dt):


		if self.health <= 0:
			self.OhFuckOhShitImGonnaDieIWasSoYoungAHHHHHHHHHHH()

		
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

		self.updatevisual(sprite = self.sprite, rotation = -rotation)

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


	def hit(self, obj):

		if ((type(obj) == Enemy)):
			pass

		elif (type(obj) == Harpoon) and self.damage:
			self.health -= obj.damage
			self.damage = False
			clock.schedule_once(self.FlipBool, 2, "self.damage")


	def FlipBool(self, dt, value):
		if value == "self.ram":
			self.ram = not self.ram

		elif value == "self.damage":
			self.damage = not self.damage



	def OhFuckOhShitImGonnaDieIWasSoYoungAHHHHHHHHHHH(self):
		self.alive = False
		




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

			tx -= x
			ty -= y
			#initilize velocity
			
			mag = math.hypot(tx,ty)
			if mag > 700:
				tx /= mag
				ty /= mag

				tx *= 700
				ty *= 700


			parent.vel = ( tx, ty )

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





