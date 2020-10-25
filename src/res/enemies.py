"""Contains all Enemy types and Enemy logic"""



from pyglet import *
import math
from res.util import visibleEntity, getClosestPointCircle
from random import randint, random
from res.Projectiles import ShootHarpoon, EnemyProjectile, ProgrammableProjectileFire, ShootBomb
from res.arena import Planet



class Enemy(visibleEntity):
	"""Acts as an identifier for enemies"""
	

	def AgresiveMovement(pos, vel, speed, turnspeed, target, dt, radius = 300):
		"""Basic movement algorithm
		
		The basic movement for this enemy, The reason its abstracted into a function
		is so it can be modularized and used in other enemies. (thats also why its a static method)
		"""


		tx, ty = getClosestPointCircle(center = target, radius = radius, point = pos)

		x, y = pos
		dx, dy = vel

		#create target velocity
		tdx = (tx - x)
		tdy = (ty - y)



		#update velocity

		dx += (tdx - dx) * turnspeed
		dy += (tdy - dy) * turnspeed



		#update position

		x += dx * dt * speed
		y += dy * dt * speed


		return (x,y, dx,dy)


	def DommingMovement(pos, vel, speed, turnspeed, target, dt, radius = 300):


		tdist = math.dist(pos, target)
		tradius = randint(100,radius)

		tx, ty = getClosestPointCircle(center = target, radius = tradius, point = pos)

		x, y = pos
		dx, dy = vel

		if tdist > radius:
			tdx = (tx - x)
			tdy = (ty - y)

			dx += (tdx - dx) * turnspeed
			dy += (tdy - dy) * turnspeed

		else:
			dx /= 2
			dy /= 2


		if dx < 1:
			dx = 0

		if dy < 1:
			dy = 0



		x += dx * dt * speed
		y += dy * dt * speed

		return (x,y, dx,dy)





class FishingBoat(Enemy):
	"""Simple Enemy
	attack = slower, weaker harpoon
	speed = slow
	health = low
	"""

	def __init__(self, pos, speed, player, objects, handler, camera, batch, group):
		super().__init__(pos,(50,25), shapes.Rectangle(*pos, *(50,25), color=(0, 255, 255), batch=batch, group=group))
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)


		self.batch = batch
		self.group = group


		self.vel = (0,0)
		
		self.speed = speed
		self.handler = handler
		self.damage = 5
		self.turnspeed = 0.02

		self.camera = camera

		self.player = player

		self.objects = objects


		clock.schedule_once(self.setupFire, (random() * 2))

		#death flag
		self.alive = True

	def setupFire(self, dt):
		"""offsets the firing cycle so every enemy isn't in sync with each other"""
		clock.schedule_interval(self.fire, 4, self.objects)



	def update(self, dt):
		"""Updates pos and velocityof enemy"""

		#anti-overlap
		self.avoid_other()
		self.speed_limit()


		#pathfinding
		x, y = self.pos
		dx, dy = self.vel
		target = self.player.pos

		x,y, dx,dy = Enemy.AgresiveMovement(pos = (x,y), vel = (dx,dy), speed = self.speed, turnspeed = self.turnspeed, target = target, dt = dt)

		

		self.updatevisual(sprite = self.sprite)

		self.pos = (x,y)
		self.vel = (dx,dy)



	def speed_limit(self):
		"""Prevents Enemy from moving too fast"""
		dx, dy = self.vel
		speed = math.hypot(*self.vel)

		if speed > 200:
			dx /= speed
			dy /= speed

			dx *= 200
			dy *= 200

		self.vel = (dx,dy)



	



	def fire(self, dt, objects):
		"""calls projectile method to launch attack"""
		if math.dist(self.pos, self.player.pos) < 400:
			ShootHarpoon(me = self, other = self.player.pos, output = self.objects)


	def avoid_other(self):
		"""Prevents enemies from overlapping
		
		Code borrowed from Boid algorithm. It creates a repulsive force between enemies
		so they spread out and aren't clumped together.
		"""
		forcex = 0
		forcey = 0
		sx, sy = self.pos
		

		for obj in [obj for obj in self.objects if isinstance(obj, FishingBoat)]:

			if math.dist(self.pos, obj.pos) < 100:
				
				bx, by = obj.pos


				forcex += sx - bx
				forcey += sy - by
		
		dx, dy = self.vel


		dx += forcex * 0.1
		dy += forcey * 0.1

		self.vel = (dx,dy)


	def hit(self, obj, dt):
		"""handles collision behavior"""

		if type(obj) == Enemy:
			pass

		elif (type(obj) == Planet):

			dx, dy = obj.find_repulsion_vector(self)

			self.vel = ((self.vel[0] + (dx*1.05)), (self.vel[1] + (dy*1.05)))



		elif ( not isinstance(obj, (EnemyProjectile, Enemy) )) and ( not obj.dive):
			clock.unschedule(self.fire)
			self.alive = False

		else:
			pass









class Galley(Enemy):

	def __init__(self, pos, speed, player, objects, handler, camera, batch, group):
		super().__init__(pos,(300,200), shapes.Rectangle(*pos, *(300,200), color=(0, 255, 255), batch=batch, group=group))
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)


		self.batch = batch
		self.group = group


		self.vel = (0,0)
		
		self.speed = speed
		self.handler = handler
		self.damage = 5
		self.health = 2
		self.turnspeed = 0.02

		self.camera = camera

		self.player = player

		self.objects = objects

		self.hitcool = False


		clock.schedule_once(self.setupFire, (random() * 2))

		#death flag
		self.alive = True



	def setupFire(self, dt):
		clock.schedule_interval(self.fire, 5)

	def spiral(time):

		dx = 10*math.cos(time*2)
		dy = 10*math.sin(time*2)

		dx *= time**2.5
		dy *= time**2.5

		return (dx,dy)

	def fire(self, dt):
		dist = math.dist(self.pos, self.player.pos)

		if dist < 1400:
			for x in range(8):
				ProgrammableProjectileFire(me = self, other = self.player, equation = Galley.spiral, rotation = x*(360/8), output = self.objects)





	def update(self, dt):
		"""Updates pos and velocity of enemy"""

		if self.health == 0:
			self.alive = False
			clock.unschedule(self.fire)



		#anti-overlap
		self.speed_limit()
		self.avoid_other()


		#pathfinding
		x, y = self.pos
		dx, dy = self.vel
		target = self.player.pos

		x,y, dx,dy = Enemy.DommingMovement(pos = (x,y), vel = (dx,dy), speed = self.speed, turnspeed = self.turnspeed, target = target, dt = dt, radius = 1000)

		

		self.updatevisual(sprite = self.sprite)

		self.pos = (x,y)
		self.vel = (dx,dy)


	def speed_limit(self):
		"""Prevents Enemy from moving too fast"""
		dx, dy = self.vel
		speed = math.hypot(*self.vel)

		if speed > 100:
			dx /= speed
			dy /= speed

			dx *= 100
			dy *= 100

		self.vel = (dx,dy)

	def avoid_other(self):
		"""Prevents enemies from overlapping
		
		Code borrowed from Boid algorithm. It creates a repulsive force between enemies
		so they spread out and aren't clumped together.
		"""
		forcex = 0
		forcey = 0
		sx, sy = self.pos
		

		for obj in [obj for obj in self.objects if isinstance(obj, Galley)]:

			if math.dist(self.pos, obj.pos) < 100:
				
				bx, by = obj.pos


				forcex += sx - bx
				forcey += sy - by
		
		dx, dy = self.vel


		dx += forcex * 0.5
		dy += forcey * 0.5

		self.vel = (dx,dy)

	def hitflip(self, dt):
		self.hitcool = False


	def hit(self, obj, dt):
		if self.hitcool:
			return

		if (type(obj) == type(self.player)) and (obj.ram):
			self.health -= 1
			self.hitcool = True
			clock.schedule_once(self.hitflip, 1.5)





class Frigate(Enemy):

	def __init__(self, pos, speed, player, objects, handler, camera, batch, group):
		super().__init__(pos,(600,400), shapes.Rectangle(*pos, *(600,400), color=(0, 255, 255), batch=batch, group=group))
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)


		self.batch = batch
		self.group = group


		self.vel = (0,0)
		
		self.speed = speed
		self.handler = handler
		self.damage = 5
		self.health = 4
		self.turnspeed = 0.02

		self.camera = camera

		self.player = player

		self.objects = objects

		self.hitcool = False


		clock.schedule_once(self.setupFire, (random() * 2))
		clock.schedule_once(self.setupFire, (random() * 2) + 1)

		#death flag
		self.alive = True


	def update(self, dt):
		"""Updates pos and velocity of enemy"""

		if self.health == 0:
			self.alive = False
			clock.unschedule(self.fire)
			clock.unschedule(self.fire)



		#anti-overlap
		self.speed_limit()
		self.avoid_other()


		#pathfinding
		x, y = self.pos
		dx, dy = self.vel
		target = self.player.pos

		x,y, dx,dy = Enemy.DommingMovement(pos = (x,y), vel = (dx,dy), speed = self.speed, turnspeed = self.turnspeed, target = target, dt = dt, radius = 1300)

		

		self.updatevisual(sprite = self.sprite)

		self.pos = (x,y)
		self.vel = (dx,dy)


	def hitflip(self, dt):
		self.hitcool = False


	def fire(self, dt):
		dist = math.dist(self.pos, self.player.pos)

		if dist < 1600:
			ShootBomb(me = self, other = self.player.pos, fragNum = 4, output = self.objects)

	def setupFire(self, dt):
		clock.schedule_interval(self.fire, 5)





	def hit(self, obj, dt):
		if self.hitcool:
			return

		if (type(obj) == type(self.player)) and (obj.ram):
			self.health -= 1
			self.hitcool = True
			clock.schedule_once(self.hitflip, 1.5)


	def speed_limit(self):
		"""Prevents Enemy from moving too fast"""
		dx, dy = self.vel
		speed = math.hypot(*self.vel)

		if speed > 100:
			dx /= speed
			dy /= speed

			dx *= 100
			dy *= 100

		self.vel = (dx,dy)

	def avoid_other(self):
		"""Prevents enemies from overlapping
		
		Code borrowed from Boid algorithm. It creates a repulsive force between enemies
		so they spread out and aren't clumped together.
		"""
		forcex = 0
		forcey = 0
		sx, sy = self.pos
		

		for obj in [obj for obj in self.objects if isinstance(obj, Galley)]:

			if math.dist(self.pos, obj.pos) < 100:
				
				bx, by = obj.pos


				forcex += sx - bx
				forcey += sy - by
		
		dx, dy = self.vel


		dx += forcex * 0.5
		dy += forcey * 0.5

		self.vel = (dx,dy)
