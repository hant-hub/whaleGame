"""Holds all projectile types and behavior.

This includes both enemy and player projectiles as well as interfaces for
instantiating projectiles with functions
"""



from pyglet import *
import math, time
from res.util import visibleEntity
from res.arena import Planet


class EnemyProjectile(visibleEntity):
	pass


class Harpoon(EnemyProjectile):
	"""Basic projectile for Enemies"""

	def __init__(self, pos, size, speed, vel, side, camera, batch, group):
		super().__init__(pos,size, shapes.Rectangle(*pos, *size, color=(255, 255, 255), batch=batch, group=group))
		dx, dy = vel

		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)
		self.sprite.rotation = math.degrees( -math.atan2(dy, dx)  )


		
		
		

		self.speed = speed
		self.vel = vel
			
		self.speed = speed
		self.damage = 15

		self.camera = camera
		self.side = None


		#death flag
		self.alive = True

		self.updatevisual(sprite = self.sprite)


		clock.schedule_once(self.kill, 3)




	def update(self, dt):
		"""Update method Projctile, fundamentallythe same for all Projectiles"""

		x, y = self.pos
		dx, dy = self.vel


		x += dx * self.speed
		y += dy * self.speed

		self.updatevisual(sprite = self.sprite)
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)


		self.pos = (x,y)
		self.vel = (dx,dy)


	def hit(self,obj, dt):
		"""handles behavior when colliding with other objects. Currently does nothing"""
		if type(obj) == Planet:
			clock.unschedule(self.kill)
			self.kill(0)

		else:
			pass


	def kill(self, dt):
		"""Deletes projectile after it reaches the end of its 'life' """
		self.alive = False




class ProgrammableProjectile(EnemyProjectile):

	def __init__(self, pos, size, speed, equation, rotation, offset, side, camera, batch, group):
		super().__init__(pos,size, shapes.Rectangle(*pos, *size, color=(255, 255, 255), batch=batch, group=group))

		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)
		self.sprite.rotation = math.degrees( -math.atan2(0,1)  )


		
		
		self.start = time.perf_counter() - offset

		self.speed = speed
		#this equation describes the velocity curve ie: is a function that outputs velocity (should be a derivative)
		self.equation = equation
		self.rotation = math.radians(rotation)

		self.speed = speed
		self.damage = 15

		self.camera = camera
		self.side = None


		#death flag
		self.alive = True

		self.updatevisual(sprite = self.sprite)


		clock.schedule_once(self.kill, 10)



	def update(self, dt):
		"""Update method Projctile, fundamentallythe same for all Projectiles"""

		x, y = self.pos
		dx, dy = self.equation(time.perf_counter() - self.start)


		#rotate dx, dy by rotation
		dx, dy = dx*math.cos(self.rotation) - dy*math.sin(self.rotation), dy*math.cos(self.rotation) + dx*math.sin(self.rotation)
		 

		x += dx * self.speed * dt
		y += dy * self.speed * dt

		self.updatevisual(sprite = self.sprite, rotation = math.degrees( -math.atan2(0,1)  ))
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)


		self.pos = (x,y)



	def hit(self,obj, dt):
		"""handles behavior when colliding with other objects. Currently does nothing"""
		if type(obj) == Planet:
			clock.unschedule(self.kill)
			self.kill(0)

		else:
			pass


	def kill(self, dt):
		"""Deletes projectile after it reaches the end of its 'life' """
		self.alive = False





class Bomb(EnemyProjectile):

	def __init__(self, pos, size, speed, fragNum, objects, vel, side, camera, batch, group):
		super().__init__(pos,size, shapes.Rectangle(*pos, *size, color=(255, 255, 255), batch=batch, group=group))
		dx, dy = vel

		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)


		self.fragNum = fragNum
		self.objects = objects
		
		self.batch = batch
		self.group = group
		self.speed = speed
		self.vel = vel
			
		self.speed = speed
		self.damage = 15

		self.camera = camera
		self.side = None


		#death flag
		self.alive = True

		self.updatevisual(sprite = self.sprite)


		clock.schedule_once(self.kill, 2)

	def update(self, dt):
		"""Update method Projctile, fundamentallythe same for all Projectiles"""

		x, y = self.pos
		dx, dy = self.vel


		x += dx * self.speed
		y += dy * self.speed

		self.updatevisual(sprite = self.sprite)
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)


		self.pos = (x,y)
		self.vel = (dx,dy)


	def hit(self,obj, dt):
		"""handles behavior when colliding with other objects. Currently does nothing"""
		if type(obj) == Planet:
			clock.unschedule(self.kill)
			self.kill(0)

		else:
			pass


	def kill(self, dt):
		"""Deletes projectile after it reaches the end of its 'life' """
		partition = 360/self.fragNum
		x, y = self.pos
		for x in range(self.fragNum):
			angle = partition*x
			angle = math.radians(angle)
			
			self.objects.add(Harpoon(pos = self.pos, size = (30,10), speed = 15, vel = (math.cos(angle),math.sin(angle)), side = type(self), camera = self.camera, batch = self.batch, group = self.group))
			
		self.alive = False




class Laser(EnemyProjectile):

	def __init__(self, pos, width, target, camera, batch, group):
		super().__init__(pos, (10_000,width), shapes.Rectangle(*pos, *(10_000,width), color=(255, 0, 0), batch=batch, group=group))
		
		tx, ty = target
		x, y = pos
		dx, dy = (tx-x), (ty-y)

		self.sprite.anchor_x = 0
		self.sprite.anchor_y = self.sprite.height/2
		self.sprite.rotation = math.degrees( -math.atan2(dy, dx)  )

		
		self.batch = batch
		self.group = group
			
		self.damage = 15

		self.camera = camera

		#death flag
		self.alive = True

		self.updatevisual(sprite = self.sprite)
		clock.schedule_once(self.kill, 2.5)

	def update(self, dt):	
		self.updatevisual(sprite = self.sprite)
		self.sprite.anchor_x = 0
		self.sprite.anchor_y = self.sprite.height/2

	def hit(self, obj, dt):
		pass

	def kill(self, dt):
		self.alive = False

		





def ProgrammableProjectileFire(me, other, equation, rotation, output, offset = 0):
	output.add(ProgrammableProjectile(pos = me.pos, size = (30,30), speed = 15, equation = equation, rotation = rotation, offset = offset, side = type(me), camera = me.camera, batch = me.batch, group = me.group))


def ShootBomb(me, other, fragNum, output):
	tx, ty = other
	x, y = me.pos

	tx -= x
	ty -= y
	
	tx /= math.dist(other, me.pos)
	ty /= math.dist(other, me.pos)
	
	output.add(Bomb(pos = me.pos, size = (100,100), speed = 13, fragNum = fragNum, objects = output, vel = (tx,ty), side = type(me), camera = me.camera, batch = me.batch, group = me.group))



def ShootHarpoon(me, other, output):
	"""method for launching harpoon projectile"""
	tx, ty = other
	x, y = me.pos


	tx -= x
	ty -= y

	tx /= math.dist(other, me.pos)
	ty /= math.dist(other, me.pos)


	output.add(Harpoon(pos = me.pos, size = (30,10), speed = 15, vel = (tx,ty), side = type(me), camera = me.camera, batch = me.batch, group = me.group))