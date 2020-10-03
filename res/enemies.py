from pyglet import *
import math
from res.util import visibleEntity, getClosestPointCircle
from random import randint, random
from res.Projectiles import ShootHarpoon, Harpoon



class Enemy(visibleEntity):

	def __init__(self, pos, size, speed, player, objects, handler, camera, batch):
		super().__init__(pos,size, shapes.Rectangle(*pos, *size, color=(255, 255, 255), batch=batch))
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


		clock.schedule_interval(self.fire, (1.5 + random()), self.objects)

		#death flag
		self.alive = True



	def update(self, dt):


		#anti-overlap
		self.avoid_other()



		#pathfinding
		x, y = self.pos
		dx, dy = self.vel
		target = self.player.pos

		x,y, dx,dy = Enemy.AgresiveMovement(pos = (x,y), vel = (dx,dy), speed = self.speed, turnspeed = self.turnspeed, target = target, dt = dt)
		



		self.updatevisual(sprite = self.sprite)

		self.pos = (x,y)
		self.vel = (dx,dy)



	def AgresiveMovement(pos, vel, speed, turnspeed, target, dt, radius = 300,):



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



	def fire(self, dt, objects):
		if math.dist(self.pos, self.player.pos) < 400:
			ShootHarpoon(me = self, other = self.player, output = self.objects)


	def avoid_other(self):
		forcex = 0
		forcey = 0
		sx, sy = self.pos
		

		for obj in [obj for obj in self.objects if type(obj) == Enemy]:

			if math.dist(self.pos, obj.pos) < 100:
				
				bx, by = obj.pos


				forcex += sx - bx
				forcey += sy - by
		
		dx, dy = self.vel


		dx += forcex * 0.1
		dy += forcey * 0.1

		self.vel = (dx,dy)


	def hit(self, obj):

		if type(obj) == Enemy:
			pass

		elif type(obj) not in [Enemy, Harpoon]:
			clock.unschedule(self.fire)
			self.alive = False









