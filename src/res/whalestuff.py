"""contains all methods and behavior for the player (whale)"""




from pyglet import *
import math
from res.util import visibleEntity
from res.enemies import Enemy
from res.Projectiles import Harpoon



class Player(visibleEntity):
	"""singleton class for Player.

	The reason its a singleton is because while we only have one player at a time
	it makes packaging of all the methods and data for the player far more convinient to set up.
	And should multiplayer ever become feature we have the option of instantiating more instances of player
	"""
	def __init__(self, pos, size, speed, handler, batch):
		super().__init__(pos,size, shapes.Rectangle(*pos, *size, color=(255, 255, 0), batch=batch))



		#setup sprite


		self.sprite.anchor_x = (self.sprite.width/3) * 2
		self.sprite.anchor_y = (self.sprite.height/2)


		#setup movment
		self.vel = (0,0)
		self.speed = speed
		self.handler = handler
		self.turnspeed = 0.1

		#diving flag
		self.dive = False
		self.air = 100

		#setup basic attack
		self.ramcool = True
		self.ram = False
		self.damage = True

		#health
		self.maxhealth = 100
		self.health = 100

		#death flag
		self.alive = True



	def update(self, dt):
		"""Updates pos and vel of player"""

		if self.health <= 0:
			self.OhFuckOhShitImGonnaDieIWasSoYoungAHHHHHHHHHHH()


		#dive logic

		if self.dive:
			self.air -= 0.5

		elif self.air < 100:
			self.air += 0.2



		if self.air <= 0:
			self.dive = False
			self.damage = True
			self.sprite.opacity = 255



		
		tx,ty = self.handler.target
		zx, zy = self.camera.target
		x, y = self.pos
		dx, dy = self.vel
		cx, cy = self.camera.pos

		
		#preprocess target


		tx = ((tx - (cx + zx))/self.camera.zoom) + zx
		ty = ((ty - (cy + zy))/self.camera.zoom) + zy



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
		"""basic movement for player.

		The reason this is abstracted out is so we can switch out the basic movement with
		conditional movement such as dashes or any other conditional movment options.
		"""

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
		"""handles collision behvior.

		In this context, Collision behavior simply means things like taking damage
		when being hit with an enemy projectile, not taking damage from running into enemies, etc.
		"""

		if ((type(obj) == Enemy)):
			pass

		elif (type(obj) == Harpoon) and self.damage:
			self.health -= obj.damage
			self.damage = False
			clock.schedule_once(self.FlipBool, 2, "self.damage")


	def FlipBool(self, dt, value):
		"""supposed to be general purpose boolean toggle function. Might remove in future"""
		if value == "self.ram":
			self.ram = not self.ram

		elif value == "self.damage":
			self.damage = not self.damage



	def OhFuckOhShitImGonnaDieIWasSoYoungAHHHHHHHHHHH(self):
		"""Toggles flag to signal to the main program to delete this object"""
		self.handler.EndHandling()
		self.alive = False
		




	class Ram:
		"""holds all logic for the Ram attack

		This is a medium range dash and the main method of attacking
		"""

		def ramStart(parent):
			""" setup to begin 'ramming' """

			#set flags
			parent.ram = True
			parent.ramcool = False
			parent.damage = False

			#grab relevant information
			x, y = parent.pos
			tx,ty = parent.handler.target
			cx, cy = parent.camera.pos
			zx, zy = parent.camera.target

			#preprocess target
			tx = ((tx - (cx + zx))/parent.camera.zoom) + zx
			ty = ((ty - (cy + zy))/parent.camera.zoom) + zy

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
			clock.schedule_once(Player.Ram.ramcool, 0.5, parent)

		def ramEnd(dt, parent):
			"""tears down/resets all flags and value changes for 'ram' """
			#reset data
			parent.ram = False
			parent.damage = True
			

		def ramcool(dt, parent):
			"""scheduling for cooldown period to stop spamming of ram"""
			parent.ramcool = True

		def ram(pos, vel, speed, dt):
			"""conditional movement logic for ramming"""
			#unpack data
			x, y = pos
			dx, dy = vel

	
	
			#apply movement
			x += dx * speed * dt * 3
			y += dy * speed * dt * 3

			return (x,y, dx, dy)





