"""Contains all Enemy types and Enemy logic"""



from pyglet import *
import math
from res.util import visibleEntity, getClosestPointCircle, Hitbox
from random import randint, random
from res.Projectiles import ShootHarpoon, EnemyProjectile, ProgrammableProjectileFire, ShootBomb, Laser, PlayerProjectile
from res.arena import Planet
from res import BossAI



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


	def SniperMovement(self, pos, vel, speed, turnspeed, target, dt, rangeSize, radius = 1500):

		tdist = math.dist(pos, target)
		lradius = radius - rangeSize
		uradius = radius + rangeSize

		print(target, radius, pos)

		tx, ty = getClosestPointCircle(center = target, radius = radius, point = pos)

		x, y = pos
		dx, dy = vel

		if(tdist > uradius) or (tdist < lradius):
			tdx = (tx - x)
			tdy = (ty - y)

			dx += (tdx - dx) * turnspeed
			dy += (tdy - dy) * turnspeed

		else:
			dx /= 2
			dy /= 2

			if dx < 3:
				dx = 0

			if dy < 3:
				dy = 0

		x += dx * dt * speed
		y += dy * dt * speed


		return (x,y, dx,dy)


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



	def avoid_wall(self):
		x, y = self.pos
		mx, my = self.mapsize
		dx, dy = self.vel


		if x <= 0:
			dx += 10

		elif x >= mx:
			dx -= 10

		if y <= 0:
			dy += 10

		elif y >= my:
			dy -= 10

		self.vel = (dx,dy)

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

		self.stun = False


		clock.schedule_once(self.setupFire, (random() * 2))

		#death flag
		self.alive = True

	def EndStun(self, dt):
		self.stun = False

	def StartStun(self):
		self.stun = True

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

		if not self.stun:
			x,y, dx,dy = Enemy.AgresiveMovement(pos = (x,y), vel = (dx,dy), speed = self.speed, turnspeed = self.turnspeed, target = target, dt = dt)
		else:
			x += dx * dt * self.speed * 10
			y += dy * dt * self.speed * 10
		

		self.updatevisual(sprite = self.sprite)
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)

		self.pos = (x,y)
		self.vel = (dx,dy)



	def fire(self, dt, objects):
		"""calls projectile method to launch attack"""
		if math.dist(self.pos, self.player.pos) < 400:
			ShootHarpoon(me = self, other = self.player.pos, output = self.objects)


	


	def hit(self, obj, dt):
		"""handles collision behavior"""

		if type(obj) == Enemy:
			pass

		elif (type(obj) == Planet):

			dx, dy = obj.find_repulsion_vector(self)

			self.vel = ((self.vel[0] + (dx*1.05)), (self.vel[1] + (dy*1.05)))


		elif (isinstance(obj, Hitbox)):
			obj.enemyEffect(self)

		elif isinstance(obj, PlayerProjectile):
			clock.unschedule(self.fire)
			clock.unschedule(self.setupFire)
			self.alive = False

		elif ( not isinstance(obj, (EnemyProjectile, Enemy) )) and ( not obj.dive):
			clock.unschedule(self.fire)
			clock.unschedule(self.setupFire)
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
		self.stun = False


		clock.schedule_once(self.setupFire, (random() * 2))

		#death flag
		self.alive = True

	def EndStun(self, dt):
		self.stun = False

	def StartStun(self):
		self.stun = True

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
			for x in range(6):
				ProgrammableProjectileFire(me = self, other = self.player, equation = Galley.spiral, rotation = x*(360/6), output = self.objects)





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

		if not self.stun:
			x,y, dx,dy = Enemy.DommingMovement(pos = (x,y), vel = (dx,dy), speed = self.speed, turnspeed = self.turnspeed, target = target, dt = dt, radius = 1000)

		else:
			x += dx * dt * self.speed * 10
			y += dy * dt * self.speed * 10

		

		self.updatevisual(sprite = self.sprite)	
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)

		self.pos = (x,y)
		self.vel = (dx,dy)




	def hitflip(self, dt):
		self.hitcool = False


	def hit(self, obj, dt):
		if self.hitcool:
			return

		elif (isinstance(obj, Hitbox)):
			obj.enemyEffect(self)

		elif (isinstance(obj, PlayerProjectile)):
			self.health -= obj.damage
			self.hitcool = True
			clock.schedule_once(self.hitflip, 1.5)

		elif (type(obj) == type(self.player)) and (obj.ram):
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
		self.stun = False


		clock.schedule_once(self.setupFire, (random() * 2))
		clock.schedule_once(self.setupFire, (random() * 2) + 1)

		#death flag
		self.alive = True

	def EndStun(self, dt):
		self.stun = False

	def StartStun(self):
		self.stun = True


	def update(self, dt):
		"""Updates pos and velocity of enemy"""

		if self.health <= 0:
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

		if not self.stun:
			x,y, dx,dy = Enemy.DommingMovement(pos = (x,y), vel = (dx,dy), speed = self.speed, turnspeed = self.turnspeed, target = target, dt = dt, radius = 1300)
		else:
			x += dx * dt * self.speed * 10
			y += dy * dt * self.speed * 10
		

		self.updatevisual(sprite = self.sprite)
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)

		self.pos = (x,y)
		self.vel = (dx,dy)


	def hitflip(self, dt):
		self.hitcool = False


	def fire(self, dt):
		dist = math.dist(self.pos, self.player.pos)

		if dist < 1600:
			ShootBomb(me = self, other = self.player.pos, fragNum = 8, output = self.objects)

	def setupFire(self, dt):
		clock.schedule_interval(self.fire, 5)





	def hit(self, obj, dt):
		if self.hitcool:
			return

		elif (isinstance(obj, Hitbox)):
			obj.enemyEffect(self)


		elif (isinstance(obj, PlayerProjectile)):
			self.health -= obj.damage
			self.hitcool = True
			clock.schedule_once(self.hitflip, 1.5)




		elif (type(obj) == type(self.player)) and (obj.ram):
			self.health -= 1
			self.hitcool = True
			clock.schedule_once(self.hitflip, 1.5)







class Whaler(Enemy):

	def __init__(self, pos, speed, player, objects, mapsize, handler, camera, batch, group, laserGroup = None):
		super().__init__(pos,(300,200), shapes.Rectangle(*pos, *(300,200), color=(0, 255, 255), batch=batch, group=group))
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)


		self.batch = batch
		self.group = group
		if laserGroup == None:
			self.laserGroup = group
		else:
			self.laserGroup = laserGroup


		self.vel = (0,0)
		
		self.speed = speed
		self.handler = handler
		self.damage = 5
		self.health = 6
		self.turnspeed = 0.02

		self.camera = camera

		self.player = player

		self.objects = objects
		self.mapsize = mapsize

		self.hitcool = False
		self.sniperlock = False
		self.aim = False
		self.sight = None
		self.stun = False
		self.aimpoint = (0,0)


		#clock.schedule_once(self.setupFire, (random() * 2))

		#death flag
		self.alive = True

	def EndStun(self, dt):
		self.stun = False

	def StartStun(self):
		self.stun = True
		self.resetFire(0)

	def laserSight(self):
		self.aimpoint = self.player.pos

	def lockAimPoint(self, dt):
		self.aim = False

	def Aiming(self, dt):
		self.sniperlock = True
		self.aim = True
		self.aimpoint = self.player.sprite.position

		x, y = self.sprite.position
		tx, ty = self.player.sprite.position

		self.sight = shapes.Line(x = tx, y = ty, x2 = x, y2 = y, width=1, color=(255, 0, 0), batch=self.batch, group=self.group)


		clock.schedule_once(self.fire, 4)
		clock.schedule_once(self.lockAimPoint, 3.5)

	def fire(self, dt):
		self.aim = False
		self.sight.delete()
		self.sight = None
		self.objects.add(Laser(pos = self.pos, width = 100, target = self.aimpoint, camera = self.camera, batch = self.batch, group = self.laserGroup))
		clock.schedule_once(self.resetFire, 4)

	def resetFire(self,dt):
		self.aim = False
		self.sniperlock = False

		if self.sight != None:
			self.sight.delete()





	def update(self,dt):


		if self.health <= 0:
			clock.unschedule(self.lockAimPoint)
			clock.unschedule(self.Aiming)
			clock.unschedule(self.fire)
			clock.unschedule(self.resetFire)

			if self.sight != None:
				self.sight.delete()

			self.alive = False



		self.avoid_other()
		self.avoid_wall()
		self.speed_limit()

		x, y = self.pos
		dx, dy = self.vel
		target = self.player.pos

		self.updatevisual(sprite = self.sprite)
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)


		#pathfinding
		if not self.stun:

			if not self.sniperlock:
				x,y, dx,dy = self.SniperMovement(pos = self.pos, vel = self.vel, speed = self.speed, turnspeed = self.turnspeed, target = self.player.pos, dt = dt, rangeSize = 500, radius = 1500)

			if ((dx == 0) and (dy == 0)) and (not self.sniperlock):
				self.Aiming(0)

			#laser Management
			if self.aim:
				self.laserSight()

			if self.sight != None:

				self.sight.x = self.sprite.position[0]
				self.sight.y = self.sprite.position[1]

				self.sight.x2 = ((self.aimpoint[0]-self.camera.target[0]) * self.camera.zoom) + self.camera.pos[0] + (self.camera.target[0]) 
				self.sight.y2 = ((self.aimpoint[1]-self.camera.target[1]) * self.camera.zoom) + self.camera.pos[1] + (self.camera.target[1])

		else:
			x += dx * dt * self.speed * 10
			y += dy * dt * self.speed * 10



		self.pos = (x,y)
		self.vel = (dx,dy)


	def hitflip(self, dt):
		self.hitcool = False


	def hit(self, obj, dt):
		if self.hitcool:
			return

		elif (isinstance(obj, Hitbox)):
			obj.enemyEffect(self)


		elif (isinstance(obj, PlayerProjectile)):
			self.health -= obj.damage
			self.hitcool = True
			clock.schedule_once(self.hitflip, 1.5)


		elif (type(obj) == type(self.player)) and (obj.ram):
			self.health -= 1
			self.hitcool = True
			clock.schedule_once(self.hitflip, 1.5)





class Galleon(Enemy):
	def __init__(self, pos, speed, player, objects, mapsize, screen, handler, camera, batch, group, ui):
		super().__init__(pos,(700,500), shapes.Rectangle(*pos, *(700,500), color=(0, 255, 255), batch=batch, group=group))
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)


		self.batch = batch
		self.group = group
		self.camera = camera
		self.handler = handler
		self.speed = speed
		self.player = player
		self.turnspeed = 0.01
		self.objects = objects
		self.mapsize = mapsize

		self.health = 10
		self.hitcool = False



		self.healthbar = shapes.Rectangle(x = screen.width/2, y = 30, width = screen.width/2, height = 30, color=(255, 0, 0), batch=batch, group=ui)
		self.healthbar.anchor_x = screen.width/4
		self.screen = screen



		self.vel = (0,0)
		
		self.brain = BossAI.AiBrain(self)

		self.brain.history.append("shields")
		self.brain.history.append("idle")
		self.brain.addState(self.Idle, "idle", 1, 1)
		self.brain.addState(self.Bomb, "bomb", 3, 1.5)
		self.brain.addState(self.Shields, "shields", 2, 2)
		self.brain.addState(self.SmartShot, "smartshot", 3, 0.2)
		self.brain.addState(self.machinegunShot, "machinegunshot", 3, 0.1)
		self.brain.decision = Galleon.decision


		self.alive = True

	def StartStun(self):
		pass
	def EndStun(self, *args, **kwargs):
		pass

	def healthBar(self):
		#Grab values
		maxhealth = 10
		currenthealth = self.health

		#grab size data
		width, height = (self.screen.width/2,60)

		#calculate %
		healthpart = currenthealth/maxhealth


		#apply % to size
		if healthpart < 0:
			healthpart = 0
		width = width*healthpart

		#change visual
		self.healthbar.width = width


	def decision(body, history):

		if body.health > 5:
			if history[-1] == "idle" and history[-2] == "machinegunshot":
				return "shields"
			elif history[-1] == "idle" and history[-2] == "shields":
				return "machinegunshot"

			else:
				return "idle"

		else:
			if history[-1] == "smartshot":
				return "bomb"
			elif history[-1] == "bomb":
				return "smartshot"

			else:
				return "smartshot"






	def Idle(_, dt, body):
		body.hitcool = False
		pass

	def Bomb(_, dt, body):

		def fire(dt, body):
			ShootBomb(me = body, other = body.player.pos, fragNum = 4, output = body.objects)


		clock.schedule_once(fire, 0.1, body)
		clock.schedule_once(fire, 0.5, body)


	def Shields(_, dt, body):
		body.hitcool = True

	def SmartShot(_, dt, body):
		def sineShot(time):
			dx = 30
			dy = math.sin(time*4) * 25

			return dx, dy

		
		ProgrammableProjectileFire(me = body, other = body.player.pos, equation = sineShot, rotation = math.degrees(math.atan2(body.player.pos[1] - body.pos[1], body.player.pos[0] - body.pos[0])), output = body.objects)
		ProgrammableProjectileFire(me = body, other = body.player.pos, equation = sineShot, rotation = math.degrees(math.atan2(body.player.pos[1] - body.pos[1], body.player.pos[0] - body.pos[0])), output = body.objects, offset = math.pi/4)

	def machinegunShot(_, dt, body):
		ShootHarpoon(me = body, other = body.player.pos, output = body.objects)



	def update(self, dt):
		self.healthBar()
		self.brain.switch()
		self.avoid_wall()

		x, y = self.pos
		dx, dy = self.vel
		target = self.player.pos

		x,y, dx,dy = Enemy.AgresiveMovement(pos = (x,y), vel = (dx,dy), speed = self.speed, turnspeed = self.turnspeed, target = target, dt = dt, radius = 1300)

		self.pos = (x,y)
		self.vel = (dx,dy)


		self.updatevisual(sprite = self.sprite)
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)

		if self.health <= 0:
			self.alive = False
			self.brain.resetSwitch(None)
			del self.healthbar
			del self.brain


	def resetspeed(self, dt = 0):
		self.speed = 1



	def hit(self, obj, dt):

		if self.hitcool:
			return

		elif (isinstance(obj, Hitbox)):
			obj.enemyEffect(self)



		elif (isinstance(obj, PlayerProjectile)):
			self.health -= obj.damage
			self.hitcool = True
			self.speed = 3
			clock.schedule_once(self.hitflip, 1.5)
			clock.schedule_once(self.resetspeed, 1)

		elif (type(obj) == type(self.player)) and (obj.ram):
			self.health -= 1
			self.speed = 3
			self.hitcool = True
			clock.schedule_once(self.hitflip, 1.5)
			clock.schedule_once(self.resetspeed, 1)


	def hitflip(self, dt):
		self.hitcool = False








