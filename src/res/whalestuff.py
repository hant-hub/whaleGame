"""contains all methods and behavior for the player (whale)"""




from pyglet import *
import math
from res.util import visibleEntity, getClosestPointCircle, collision, Hitbox
from res.enemies import Enemy
from res.Projectiles import EnemyProjectile, PlayerLaser
from res.arena import Planet
from res.PlayerAbilities import *



class Player(visibleEntity):
	"""singleton class for Player.

	The reason its a singleton is because while we only have one player at a time
	it makes packaging of all the methods and data for the player far more convinient to set up.
	And should multiplayer ever become feature we have the option of instantiating more instances of player
	"""
	def __init__(self, pos, size, speed, handler, objects, images, batch, group):
		super().__init__(pos,size, shapes.Rectangle(*pos, *(images["swim"][0].width-10,images["swim"][0].height-10), color=(255, 255, 0), batch=batch, group = group))



		#setup sprite

		self.sprite.anchor_x = 0
		self.sprite.anchor_y = self.sprite.height * 3/4

		self.size = (images["swim"][0].width -10,images["swim"][0].height -10)
		
		

		self.batch = batch
		self.group = group
		self.sprite.visible = False
		self.swim_anims = images["swim"]
		self.visual = sprite.Sprite(self.swim_anims[0], batch = batch, group = self.group)
		self.moving = False




		#setup movment
		self.vel = (0,0)
		self.speed = speed
		self.handler = handler
		self.objects = objects
		self.turnspeed = 0.03


		#setup basic attack
		self.ramcool = True
		self.ram = False
		
		self.damage = True
		self.meleeDamage = 1

		#health
		self.maxhealth = 100
		self.health = 100

		#armour
		self.armour = 30

		#death flag
		self.alive = True

		#projectile mode
		self.moveLock = False
		self.projectile = None


		#abilities
		self.AbilityOne = TailStrike.TailSlap
		self.AbilityTwo = LaserStrike.startLaser
		self.AbilityThree = HomingWeak.Fire

		self.abilityIndicatorOne = TailStrike.sprite
		self.abilityIndicatorTwo = LaserStrike.sprite
		self.abilityIndicatorThree = HomingWeak.sprite

		self.abilityOneCool = True
		self.abilityTwoCool = True
		self.abilityThreeCool = True


	def update(self, dt):
		"""Updates pos and vel of player"""

		if self.health <= 0:
			self.OhFuckOhShitImGonnaDieIWasSoYoungAHHHHHHHHHHH()

		if (math.hypot(*self.vel) > 30) and not self.moving:
			self.visual.delete()
			self.visual = sprite.Sprite(self.swim_anims[1], batch = self.batch, group = self.group)
			self.moving = True

		if (math.hypot(*self.vel) <= 30) and self.moving:
			self.visual.delete()
			self.visual = sprite.Sprite(self.swim_anims[0], batch = self.batch, group = self.group)
			self.moving = False





		#dive logic

		self.speed_limit()
		
		tx,ty = self.handler.target
		zx, zy = self.camera.target
		x, y = self.pos
		dx, dy = self.vel
		cx, cy = self.camera.pos

		
		#preprocess target


		tx = ((tx - (cx + zx))/self.camera.zoom) + zx
		ty = ((ty - (cy + zy))/self.camera.zoom) + zy


		if self.moveLock == True:
			dx += ((tx - x) - dx) * self.turnspeed * self.speed
			dy += ((ty - y) - dy) * self.turnspeed * self.speed

			self.projectile.sprite.rotation = math.degrees(-math.atan2(dy, dx))

		elif self.ram == True:
			x, y, dx, dy = self.Ram.ram(pos = (x, y), vel = (dx, dy), speed = self.speed, dt = dt)

		else:
			x, y, dx, dy = self.basicmovement(pos = self.pos, vel = self.vel, target = (tx,ty), dt = dt)


		

		#apply rotation

		rotation = (math.degrees(math.atan2(dx, dy)) + 90)

		

		if rotation < 90:
			self.visual.scale_y = 1
			flipcorrect = 1

		else:
			self.visual.scale_y = -1
			flipcorrect = -1




		
		self.updatevisual(image = self.sprite, rotation = rotation)
		self.sprite.anchor_x = 0
		self.sprite.anchor_y = self.sprite.height * 3/4


		rotation = math.radians(rotation)

		ax, ay = self.sprite.anchor_position


		if flipcorrect == 1:
			pass
		else:
			ay *= -0.5


		

		ax, ay = ((math.cos(-rotation) * ax) - (ay * math.sin(-rotation))),( (ay * math.cos(-rotation)) + (ax * math.sin(-rotation)))


		self.visual.position = (self.sprite.x - ax, self.sprite.y - ay)
		
		self.visual.rotation = self.sprite.rotation
		self.visual.scale = self.camera.zoom
		


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

		if (isinstance(obj, Enemy)):
			if hasattr(obj, "spiky") and self.damage:
				if obj.spiky:
					self.armour -= obj.damage

					if self.armour < 0:
						self.health += self.armour
						self.armour = 0

					self.damage = False
					clock.schedule_once(self.FlipBool, 0.1, "self.damage", True)

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
			
			self.armour -= obj.damage

			if self.armour < 0:
				self.health += self.armour
				self.armour = 0

			self.damage = False
			clock.schedule_once(self.FlipBool, 2, "self.damage", True)

			print(self.armour, self.health)

		elif (isinstance(obj, Hitbox) and self.damage):
			obj.playerEffect(self)
			self.damage = False
			clock.schedule_once(self.FlipBool, 0.5, "self.damage", True)


	def FlipBool(self, dt, value, output):
		"""supposed to be general purpose boolean toggle function. Might remove in future"""

		if value == "self.ram":
			self.ram = output

		elif value == "self.damage":
			self.damage = output

		elif value == "one":
			self.abilityOneCool = output

		elif value == "two":
			self.abilityTwoCool = output

		elif value == "three":
			self.abilityThreeCool = output



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
			clock.schedule_once(Player.Ram.ramcool, 0.4, parent)

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
			x += dx * speed * dt * 4
			y += dy * speed * dt * 4

			return (x,y, dx, dy)

	



