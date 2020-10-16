"""Contains all Enemy types and Enemy logic"""



from pyglet import *
import math
from res.util import visibleEntity, getClosestPointCircle
from random import randint, random
from res.Projectiles import ShootHarpoon, Harpoon
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



class FishingBoat(Enemy):
	"""Simple Enemy
	attack = slower, weaker harpoon
	speed = slow
	health = low
	"""

	def __init__(self, pos, size, speed, player, objects, handler, camera, batch):
		super().__init__(pos,size, shapes.Rectangle(*pos, *size, color=(0, 255, 255), batch=batch))
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)


		self.batch = batch


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
			ShootHarpoon(me = self, other = self.player, output = self.objects)


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


	def hit(self, obj):
		"""handles collision behavior"""

		if type(obj) == Enemy:
			pass

		elif ( not isinstance(obj, (Harpoon, Enemy, Planet) )) and ( not obj.dive):
			clock.unschedule(self.fire)
			self.alive = False

		else:
			pass









