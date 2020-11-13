"""contains all methods and behavior for the player (whale)"""




from pyglet import *
import math
from res.util import visibleEntity, getClosestPointCircle, collision, Hitbox
from res.enemies import Enemy
from res.Projectiles import EnemyProjectile, PlayerLaser
from res.arena import Planet



class Player(visibleEntity):
	"""singleton class for Player.

	The reason its a singleton is because while we only have one player at a time
	it makes packaging of all the methods and data for the player far more convinient to set up.
	And should multiplayer ever become feature we have the option of instantiating more instances of player
	"""
	def __init__(self, pos, size, speed, handler, objects, batch, group):
		super().__init__(pos,size, shapes.Rectangle(*pos, *size, color=(255, 255, 0), batch=batch, group = group))



		#setup sprite


		self.sprite.anchor_x = (self.sprite.width/3) * 2
		self.sprite.anchor_y = (self.sprite.height/2)

		self.batch = batch
		self.group = group


		#setup movment
		self.vel = (0,0)
		self.speed = speed
		self.handler = handler
		self.objects = objects
		self.turnspeed = 0.03

		#diving flag
		self.dive = False
		self.air = 100

		#setup basic attack
		self.ramcool = True
		self.ram = False
		self.tailcool = True
		self.lasercool = True
		self.damage = True

		#health
		self.maxhealth = 100
		self.health = 100

		#death flag
		self.alive = True

		#laser stuff
		self.laserLock = False
		self.laser = None


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


		self.speed_limit()
		
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
		elif self.laserLock == True:
			dx += ((tx - x) - dx) * self.turnspeed * self.speed
			dy += ((ty - y) - dy) * self.turnspeed * self.speed

			self.laser.sprite.rotation = math.degrees(-math.atan2(dy, dx))

		else:
			x, y, dx, dy = self.basicmovement(pos = self.pos, vel = self.vel, target = (tx,ty), dt = dt)


		

		#apply rotation

		rotation = -math.degrees(math.atan2(dy, dx))

		self.updatevisual(sprite = self.sprite, rotation = rotation)
		self.sprite.anchor_x = (self.sprite.width/3) * 2
		self.sprite.anchor_y = (self.sprite.height/2)

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

	def speed_limit(self):
		"""Prevents Enemy from moving too fast"""
		dx, dy = self.vel
		speed = math.hypot(*self.vel)

		if speed > 800:
			dx /= speed
			dy /= speed

			dx *= 800
			dy *= 800

		self.vel = (dx,dy)


	def hit(self, obj, dt):
		"""handles collision behvior.

		In this context, Collision behavior simply means things like taking damage
		when being hit with an enemy projectile, not taking damage from running into enemies, etc.
		"""

		if ((type(obj) == Enemy)):
			pass

		elif (type(obj) == Planet):

			dx, dy = obj.find_repulsion_vector(self)

			self.vel = ((self.vel[0] + (dx*1.05)), (self.vel[1] + (dy*1.05)))

			# ox, oy = obj.direction(self)
			# dx, dy = self.vel
			# x, y = self.pos
			# dist = math.hypot(dx,dy)


			# mag = collision.ScalerProjection(axis = (-oy, ox), point = (dx,dy), sprite = None)
			# pen =  collision.ScalerProjection(axis = (-ox,-oy), point = (dx,dy), sprite = None)

			# # dx /= dist
			# # dy /= dist





			
			


			# dx *+ dist
			# dy *= dist

			# if pen < 0.8*dist:
			# 	x += ox*dist*dt
			# 	y += oy*dist*dt
			# 	self.vel = (-oy * mag, ox * mag)
			# else:
			# 	x -= dx*dt*3
			# 	y -= dy*dt*3
			# 	self.vel = (dx/3,dy/3)

			# self.pos = (x,y)



			


		elif (isinstance(obj, EnemyProjectile)) and self.damage:
			self.health -= obj.damage
			self.damage = False
			clock.schedule_once(self.FlipBool, 2, "self.damage")

		elif (isinstance(obj, Hitbox) and self.damage):
			obj.playerEffect(self)
			self.damage = False
			clock.schedule_once(self.FlipBool, 0.5, "self.damage")


	def FlipBool(self, dt, value):
		"""supposed to be general purpose boolean toggle function. Might remove in future"""
		if value == "self.ram":
			self.ram = not self.ram

		elif value == "self.damage":
			self.damage = not self.damage

		elif value == "self.tailcool":
			self.tailcool = not self.tailcool

		elif value == "self.lasercool":
			self.lasercool = not self.lasercool



	def OhFuckOhShitImGonnaDieIWasSoYoungAHHHHHHHHHHH(self):
		"""Toggles flag to signal to the main program to delete this object"""
		self.handler.EndHandling()
		self.alive = False
	
	def EnemyTailHit(self, enemy):
		px, py = self.pos
		ex, ey = enemy.pos

		ex -= px
		ey -= py

		dist = math.hypot(ex, ey)

		enemy.vel = (ex * 3, ey * 3)

		enemy.StartStun()
		clock.schedule_once(enemy.EndStun, 0.5)


		if hasattr(enemy, "health"):
			enemy.health -= 2
			enemy.hitcool = True
			clock.schedule_once(enemy.hitflip, 1.5)

		else:
			enemy.hit(self, 0)



	def TailSlap(self):
		self.tailcool = False
		self.objects.add(Hitbox(pos = self.pos, size = (500, 550), rotation = (-math.degrees(math.atan2(self.vel[1], self.vel[0]))) - 180, sprite = shapes.Rectangle(*self.pos, width = 500, height = 550, color = (0,255,0), batch = self.batch, group = self.group), camera = self.camera, duration = 0.25, enemyEffect = self.EnemyTailHit, playerEffect = (lambda x: None)))
		clock.schedule_once(self.FlipBool, 3, "self.tailcool")

	def startLaser(self):
		self.lasercool = False
		Player.LaserStrike.Start(self)
		clock.schedule_once(self.FlipBool, 5, "self.lasercool")

		print(self.lasercool)
		print("startLaser")



	class LaserStrike:

		def Start(parent):
			dx, dy = parent.vel

			parent.laserLock = True
			parent.ramcool = False
			parent.laser = PlayerLaser(pos = parent.pos, width = 50, target = (dx,dy), camera = parent.camera, batch = parent.batch, group = parent.group, duration = 1.5)
			parent.laser.sprite.rotation = -math.degrees(math.atan2(dy, dx))
			parent.objects.add(parent.laser)

			clock.schedule_once(Player.LaserStrike.End, 1.5, parent)


		def End(dt, parent):

			parent.laserLock = False
			parent.ramcool = True
			parent.laser = None






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





