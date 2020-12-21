"""Contains all Enemy types and Enemy logic"""



from pyglet import *
import math
from random import randint
from res.util import visibleEntity, getClosestPointCircle, Hitbox
from random import randint, random
from res.Projectiles import ShootHarpoon, EnemyProjectile, ProgrammableProjectileFire, ShootBomb, Laser, PlayerProjectile, PlayerLaser, PlayerHarpoon, Bomb, Harpoon, ProgrammableProjectile
from res.arena import Planet
from res import BossAI, collectibles






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
			ShootHarpoon(me = self.pos, other = self.player.pos, output = self.objects)


	def delete(self):
		self.objects.add(collectibles.ArmourDrop(pos = self.pos, size = (40,40), camera = self.camera, batch = self.batch, group = self.group))
		self.sprite.delete()
		del self.sprite

		clock.unschedule(self.fire)
		clock.unschedule(self.setupFire)


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

		elif (type(obj) == type(self.player)) and (obj.ram):
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

	def spiral(time, args):

		dx = 10*math.cos(time*2)
		dy = 10*math.sin(time*2)

		dx *= time**2.5
		dy *= time**2.5

		return (dx,dy)

	def fire(self, dt):
		dist = math.dist(self.pos, self.player.pos)

		if dist < 1400:
			for x in range(4):
				ProgrammableProjectileFire(me = self, other = self.player, equation = Galley.spiral, rotation = x*(360/4), output = self.objects)





	def update(self, dt):
		"""Updates pos and velocity of enemy"""

		if self.health <= 0:
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


	def delete(self):
		self.alive = False
		self.objects.add(collectibles.ArmourDrop(pos = self.pos, size = (40,40), camera = self.camera, batch = self.batch, group = self.group))
		self.sprite.delete()
		del self.sprite

		clock.unschedule(self.fire)

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
			self.health -= obj.meleeDamage
			self.hitcool = True
			clock.schedule_once(self.hitflip, 1.5)

		else:
			pass





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


	def delete(self):
		self.objects.add(collectibles.ArmourDrop(pos = self.pos, size = (40,40), camera = self.camera, batch = self.batch, group = self.group))
		self.sprite.delete()
		del self.sprite

		clock.unschedule(self.fire)
		clock.unschedule(self.fire)


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
			self.health -= obj.meleeDamage
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
				self.sight = None

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

			if self.sight:

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
			self.health -= obj.meleeDamage
			self.hitcool = True
			clock.schedule_once(self.hitflip, 1.5)


	def delete(self):
		self.objects.add(collectibles.ArmourDrop(pos = self.pos, size = (40,40), camera = self.camera, batch = self.batch, group = self.group))
		self.sprite.delete()
		del self.sprite

		clock.unschedule(self.lockAimPoint)
		clock.unschedule(self.Aiming)
		clock.unschedule(self.fire)
		clock.unschedule(self.resetFire)

		if self.sight != None:
			self.sight.delete()



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
			if history[-1] == "idle":
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




	def SmartShot(_, dt, body):
		def sineShot(time, args):
			dx = 30
			dy = math.sin(time*4) * 25

			return dx, dy

		
		ProgrammableProjectileFire(me = body, other = body.player.pos, equation = sineShot, rotation = math.degrees(math.atan2(body.player.pos[1] - body.pos[1], body.player.pos[0] - body.pos[0])), output = body.objects)
		ProgrammableProjectileFire(me = body, other = body.player.pos, equation = sineShot, rotation = math.degrees(math.atan2(body.player.pos[1] - body.pos[1], body.player.pos[0] - body.pos[0])), output = body.objects, offset = math.pi/4)

	def machinegunShot(_, dt, body):
		ShootHarpoon(me = body.pos, other = body.player.pos, output = body.objects)



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
			self.health -= obj.meleeDamage
			self.speed = 3
			self.hitcool = True
			clock.schedule_once(self.hitflip, 1.5)
			clock.schedule_once(self.resetspeed, 1)


	def hitflip(self, dt):
		self.hitcool = False



	def delete(self):
		self.objects.add(collectibles.ArmourDrop(pos = self.pos, size = (40,40), camera = self.camera, batch = self.batch, group = self.group))

		self.sprite.delete()
		del self.sprite

		try:
			self.healthbar.delete()
			del self.healthbar

		except:
			pass

		try:
			self.brain.kill()
			del self.brain

		except:
			pass
			











class Kraken(Enemy):

	def __init__(self, pos, speed, player, objects, mapsize, screen, handler, camera, batch, group, lasergroup, ui):
		super().__init__((mapsize[0]/2, (mapsize[1]/2)-screen.height),(screen.width*2, 600), shapes.Rectangle(*(mapsize[0]/2, mapsize[1]/2), *(screen.width*2,600), color=(0, 255, 255), batch=batch, group=group))
		self.sprite.anchor_x = self.sprite.width/2
		self.sprite.anchor_y = self.sprite.height/2

		#self.pos = pos
		#self.size = (screen.width, 600)
		#self.sprite = shapes.Rectangle(*pos, *(screen.width,600), color=(0, 255, 255), batch=batch, group=group)
		self.speed = speed
		self.player = player
		self.objects = objects
		self.mapsize = mapsize
		self.screen = screen
		self.handler = handler
		self.camera = camera
		self.batch = batch
		self.group = group
		self.ui = ui
		self.lasergroup = lasergroup

		self.alive = True

		self.chase = False
		self.spiky = False
		self.damage = 2


		self.health = 15
		self.vulnerable = False
		self.hitcool = False

		self.healthbar = shapes.Rectangle(x = screen.width/2, y = 50, width = screen.width-100, height = 30, color=(255, 0, 0), batch=batch, group=ui)
		self.healthbar.anchor_x = screen.width/2
		self.healthbar.x = screen.width/2


		self.CameraSetup()

		self.brain = BossAI.AiBrain(self)
		self.brain.history.append("idle")
		self.brain.history.append("idle")
		self.brain.addState(behavior = self.idle, stateName = "idle", stateLength = 3, interval = 3)
		self.brain.addState(behavior = self.SineBeam, stateName = "sinebeam", stateLength = 3, interval = 0.1)
		self.brain.addState(behavior = self.InkShot, stateName = "inkshot", stateLength = 5, interval = 2)
		self.brain.addState(behavior = self.TentacleSlap, stateName = "tentacleslap", stateLength = 6, interval = 3)

		self.brain.addState(behavior = self.SineBeam, stateName = "sinebeamChase", stateLength = 3, interval = 0.2)
		self.brain.addState(behavior = self.InkShot, stateName = "inkshotChase", stateLength = 5, interval = 1)
		self.brain.addState(behavior = self.TentacleSlap, stateName = "tentacleslapChase", stateLength = 6, interval = 1.5)

		self.brain.decision = Kraken.decision

	def decision(body, history):

		if body.chase:
			attack = randint(0,2)

			if attack == 0:
				return "sinebeamChase"
			elif attack == 1:
				return "inkshotChase"
			elif attack == 2:
				return "tentacleslapChase"

		else:
			if (history[-2] != "idle") or (body.vulnerable):
				return "idle"

			else:
				attack = randint(0,2)

				if attack == 0:
					return "sinebeam"
				elif attack == 1:
					return "inkshot"
				elif attack == 2:
					return "tentacleslap"










	def idle(self, dt, *args):
		pass
		
	def SineBeam(self, dt, *args):
		def sineShot(time, args):
			dx = ((args+10)/10) + 30
			dy = (math.sin(time*8) * 60)

			return dx, dy

		
		ProgrammableProjectileFire(me = self, other = self.player.pos, equation = sineShot, rotation = math.degrees(math.atan2(self.player.pos[1] - self.pos[1], self.player.pos[0] - self.pos[0])), output = self.objects, duration = 5, args = self.speed/self.camera.zoom)
		ProgrammableProjectileFire(me = self, other = self.player.pos, equation = sineShot, rotation = math.degrees(math.atan2(self.player.pos[1] - self.pos[1], self.player.pos[0] - self.pos[0])), output = self.objects, offset = math.pi/8, duration = 5, args = self.speed/self.camera.zoom)




	def InkShot(self, dt, *args):

		tx, ty = self.player.pos
		x, y = self.pos

		ty += self.speed/self.camera.zoom*3

		tx -= x
		ty -= y


		tx /= math.dist(self.player.pos, self.pos)
		ty /= math.dist(self.player.pos, self.pos)


	
		self.objects.add(Bomb(pos = self.pos, size = (100,100), speed = 13, fragNum = 6, objects = self.objects, vel = (tx,ty), side = type(self), camera = self.camera, batch = self.batch, group = self.group))


	def TentacleSlap(self, dt, *args):
		pos = self.player.sprite.position
		telegraph = shapes.Rectangle(x = (pos[0]), y = 0, width = 150, height = self.screen.height*3, color=(255, 0, 0), batch=self.batch, group=self.lasergroup)
		telegraph.anchor_x = telegraph.width/2
		telegraph.opacity = 100

		def createLaser(dt, body, pos, telegraph):
			telegraph.delete()
			telegraph = None
			thing = Laser(pos = (pos[0],body.pos[1]), width = 300, target = pos, camera = body.camera, batch = body.batch, group = body.lasergroup, duration = 1.5)
			thing.sprite.rotation = -90
			body.objects.add(thing)


		clock.schedule_once(createLaser, 1, body = self, pos = self.player.pos, telegraph = telegraph)


	def CameraSetup(self):
		mx, my = self.mapsize
		self.player.pos = (mx/2, my/2)

		self.camera.pos = (-(mx/4 - self.screen.width/2),-(my/4 - self.screen.height/2))

		self.camera.locked = True
		self.camera.targetZoom = 0.5

	def CameraTearDown(self):
		mx,my = self.player.pos
		self.camera.target = self.player.pos
		self.camera.pos = (-(mx - self.screen.width/2),-(my - self.screen.height/2))
		self.camera.locked = False
		self.camera.targetZoom = 0.5

	def healthBar(self):
		#Grab values
		maxhealth = 20
		currenthealth = self.health

		#grab size data
		width, height = (self.screen.width-100,60)

		#calculate %
		healthpart = currenthealth/maxhealth


		#apply % to size
		if healthpart < 0:
			healthpart = 0
		width = width*healthpart

		#change visual
		self.healthbar.width = width
		self.healthbar.anchor_x = width/2

	def update(self, dt):

		
		if self.health <= 0 and (not self.chase):
			self.chase = True
			self.spiky = True
			clock.schedule_once(self.kill, 120)



		if self.chase:
			x, y = self.pos
			y += ((self.speed+self.camera.target[1])/self.camera.zoom - self.camera.target[1]) * dt
			self.pos = (x,y)

			cx, cy = self.camera.pos
			cy -= self.speed*dt
			self.camera.pos = (cx,cy)

			if self.speed < 350:
				self.speed += 0.3

			if self.pos[1] > self.mapsize[1]*3:
				x, y = self.pos
				px, py = self.player.pos
				cx, cy = self.camera.pos

				y -= ((self.mapsize[1]*3)+self.camera.target[1])/self.camera.zoom - self.camera.target[1]
				py -= ((self.mapsize[1]*3)+self.camera.target[1])/self.camera.zoom - self.camera.target[1]
				cy += self.mapsize[1]*3


				self.pos = (x,y)
				self.player.pos = (px,py)
				self.camera.pos = (cx,cy)


			elif self.pos[1] < (self.mapsize[1]*3) - 350:
				self.brain.switch()

		else:
			self.brain.switch()
		self.healthBar()
		self.updatevisual(sprite = self.sprite)
		self.sprite.anchor_x = self.sprite.width/2
		self.sprite.anchor_y = self.sprite.height/2

		

	def hitflip(self, dt):
		self.hitcool = False

	def vulflip(self, dt):
		self.vulnerable = False


	def hit(self, obj, dt):


		if self.vulnerable:
			if self.hitcool:
				return

			if (isinstance(obj, Hitbox)):
				self.health -= 2


			elif (isinstance(obj, PlayerProjectile)):
				self.health -= obj.damage
				self.hitcool = True
				clock.schedule_once(self.hitflip, 0.5)


			elif (type(obj) == type(self.player)) and (obj.ram):
				self.health -= obj.meleeDamage
				self.hitcool = True
				clock.schedule_once(self.hitflip, 0.5)



		elif isinstance(obj, PlayerProjectile) and (not self.hitcool):
			if isinstance(obj, PlayerLaser):
				self.health -= 0.5
				self.hitcool = True
				clock.schedule_once(self.hitflip, 1.5)

			elif isinstance(obj, PlayerHarpoon):
				self.vulnerable = True
				self.health -= 1
				obj.alive = False
				clock.schedule_once(self.vulflip, 5)



	def kill(self, dt):
		self.CameraTearDown()
		self.alive = False

		clock.unschedule(self.InkShot)

		


	def delete(self):
		self.objects.add(collectibles.ArmourDrop(pos = self.pos, size = (40,40), camera = self.camera, batch = self.batch, group = self.group))

		self.sprite.delete()
		del self.sprite

		try:
			self.healthbar.delete()
			del self.healthbar

		except:
			pass

		try:
			self.brain.kill()
			del self.brain

		except:
			pass












class ManOWar(Enemy):
	def __init__(self, pos, speed, player, objects, mapsize, screen, handler, camera, batch, group, lasergroup, ui):
		super().__init__((mapsize[0]/2, (mapsize[1]/2)-screen.height),(1800, 1500), shapes.Rectangle(*(mapsize[0]/2, mapsize[1]/2), *(1800, 1500), color=(0, 255, 255), batch=batch, group=group))
		self.maxsize = (1800, 1500)
		self.sprite.anchor_x = self.sprite.width/2
		self.sprite.anchor_y = self.sprite.height/2

		self.pos = pos
		self.vel = (0,0)
		self.turnspeed = 0.01
		#self.size = (screen.width, 600)
		#self.sprite = shapes.Rectangle(*pos, *(screen.width,600), color=(0, 255, 255), batch=batch, group=group)
		self.speed = speed
		self.player = player
		self.objects = objects
		self.mapsize = mapsize
		self.screen = screen
		self.handler = handler
		self.camera = camera
		self.batch = batch
		self.group = group
		self.ui = ui
		self.lasergroup = lasergroup

		self.alive = True
		self.spiky = False

		self.damage = 2

		self.health = 10
		self.hitcool = False

		self.healthbar = shapes.Rectangle(x = screen.width/2, y = 50, width = screen.width-100, height = 30, color=(255, 0, 0), batch=batch, group=ui)
		self.healthbar.anchor_x = screen.width/2
		self.healthbar.x = screen.width/2

		self.camera.targetZoom = 0.25
		self.camera.player = self

		self.brain = BossAI.AiBrain(self)
		self.brain.addState(behavior = self.steamRoll, stateName = "steamroll", stateLength = 10, interval = 11)
		self.brain.addState(behavior = self.MegaBomb, stateName = "megabomb", stateLength = 4, interval = 2)
		self.brain.addState(behavior = self.Turrets, stateName = "turrets", stateLength = 5, interval = 0.2)
		self.brain.addState(behavior = self.deathWheel, stateName = "deathwheel", stateLength = 6, interval = 2)
		self.brain.addState(behavior = self.MidShot, stateName = "midshot", stateLength = 3, interval = 1)
		self.brain.addState(behavior = self.weakShot, stateName = "weakShot", stateLength = 15, interval = 5)
		self.brain.addState(behavior = self.idle, stateName = "idle", stateLength = 60, interval = 60)

		self.brain.decision = ManOWar.decision

	def StartStun(self):
		pass
	def EndStun(self, *args, **kwargs):
		pass

	def decision(body, history):
		scale = body.health/62.5 + 0.2
		


		if scale > 0.6:
			choice = randint(0, 3)

			if choice == 0:
				return "steamroll"
			elif choice == 1:
				return "megabomb"
			elif choice == 2:
				return "turrets"
			else:
				return "deathwheel"

		elif scale > 0.4:
			return "midshot"
		elif scale > 0.3:
			return "weakShot"

		else:
			return "idle"

	def idle(Self, dt, *args):
		pass

	def steamRoll(self, dt, *args):
		self.spiky = True

		def flipSpike(dt, obj):
			obj.spiky = False

		clock.schedule_once(flipSpike, 10, self)


	def MegaBomb(self, dt, *args):

		num = 8

		partition = (math.pi*2)/num

		for x in range(num):
			self.objects.add(Bomb(pos = self.pos, size = (100,100), speed = 13, fragNum = 6, objects = self.objects, vel = (math.cos(x*partition),math.sin(x*partition)), side = type(self), camera = self.camera, batch = self.batch, group = self.group))


	def Turrets(self, dt, *args):
		mx, my = self.pos
		x, y = self.pos
		sx, sy = self.size
		px, py = self.player.pos

		sx /= 2
		sy /= 2

		sx -= 20
		sy -= 20

		x = mx + sx
		y = my + sy
		tx = (px-x)/math.dist(self.player.pos,(x,y))
		ty = (py-y)/math.dist(self.player.pos,(x,y))

		self.objects.add(Harpoon(pos = (x,y), size = (30,10), speed = 30, vel = (tx,ty), side = type(self), camera = self.camera, batch = self.batch, group = self.group))

		x = mx + sx
		y = my - sy
		tx = (px-x)/math.dist(self.player.pos, (x,y))
		ty = (py-y)/math.dist(self.player.pos, (x,y))

		self.objects.add(Harpoon(pos = (x,y), size = (30,10), speed = 30, vel = (tx,ty), side = type(self), camera = self.camera, batch = self.batch, group = self.group))

		x = mx - sx
		y = my + sy
		tx = (px-x)/math.dist(self.player.pos, (x,y))
		ty = (py-y)/math.dist(self.player.pos, (x,y))

		self.objects.add(Harpoon(pos = (x,y), size = (30,10), speed = 30, vel = (tx,ty), side = type(self), camera = self.camera, batch = self.batch, group = self.group))

		x = mx - sx
		y = my - sy
		tx = (px-x)/math.dist(self.player.pos, (x,y))
		ty = (py-y)/math.dist(self.player.pos, (x,y))

		self.objects.add(Harpoon(pos = (x,y), size = (30,10), speed = 30, vel = (tx,ty), side = type(self), camera = self.camera, batch = self.batch, group = self.group))


	def deathWheel(self, dt, *args):

		def Cycloid(time, args):

			r = 80

			dx = math.cos(time*4)*r
			dy = math.sin(time*4)*r

			dx += 50

			return dx, dy


		x, y = self.pos
		px, py = self.player.pos

		dx = px - x
		dy = py - y

		rotation = math.atan2(dy, dx)


		n = 8
		partition = math.pi/(2*n)
		for i in range(n):
			x = self.pos[0] + 320*math.sin(i*((2*math.pi)/n))
			y = self.pos[1] - 320*math.cos(i*((2*math.pi)/n))

			x -= self.pos[0]
			y -= self.pos[1]

			x, y = x*math.cos(rotation) - y*math.sin(rotation), y*math.cos(rotation) + x*math.sin(rotation)

			x +=  self.pos[0]
			y +=  self.pos[1]

			self.objects.add(ProgrammableProjectile(pos = (x,y), size = (30,30), speed = 15, equation = Cycloid, rotation = math.degrees(rotation), offset = i*partition, side = type(self), camera = self.camera, batch = self.batch, group = self.group, duration = 5, args = None))


	def weakShot(self, dt, *args):
		tx, ty = self.player.pos
		x, y = self.pos

		tx -= x
		ty -= y

		tx /=math.dist(self.player.pos,self.pos)
		ty /=math.dist(self.player.pos,self.pos)

		self.objects.add(Harpoon(pos = self.pos, size = (60,20), speed = 15, vel = (tx,ty), side = type(self), camera = self.camera, batch = self.batch, group = self.group))

	def MidShot(self, dt, *args):
		tx, ty = self.player.pos
		x, y = self.pos

		tx -= x
		ty -= y

		tx /= math.dist(self.player.pos,self.pos)
		ty /= math.dist(self.player.pos,self.pos)

		self.objects.add(Harpoon(pos = self.pos, size = (120,40), speed = 30, vel = (tx, ty), side = type(self), camera = self.camera, batch = self.batch, group = self.group))


	def healthBar(self):
		#Grab values
		maxhealth = 50
		currenthealth = self.health

		#grab size data
		width, height = (self.screen.width-100,60)

		#calculate %
		healthpart = currenthealth/maxhealth


		#apply % to size
		if healthpart < 0:
			healthpart = 0
		width = width*healthpart

		#change visual
		self.healthbar.width = width
		self.healthbar.anchor_x = width/2

	def BigMove(self, dt):
		x,y = self.pos
		px, py = self.player.pos
		dx,dy = self.vel

		tdx, tdy = px - x, py - y
	

		dx += (tdx - dx) * self.turnspeed
		dy += (tdy - dy) * self.turnspeed

		speed = math.hypot(dx,dy)

		dx /= speed
		dy /= speed

		x += dx * dt * self.speed
		y += dy * dt * self.speed


		self.pos = (x,y)
		self.vel = (dx,dy)

	def LittleMove(self, dt):
		x,y = self.pos
		px, py = self.player.pos
		dx,dy = self.vel

		tdx, tdy = x - px, y - py
	

		dx += (tdx - dx) * self.turnspeed
		dy += (tdy - dy) * self.turnspeed

		speed = math.hypot(dx,dy)

		dx /= speed
		dy /= speed

		x += dx * dt * self.speed
		y += dy * dt * self.speed


		self.pos = (x,y)
		self.vel = (dx,dy)


	def update(self, dt):

		if self.health <= 0:
			self.alive = False

		self.speed = 8 * (50 - self.health) + 100
		scale = self.health/62.5 + 0.2
		self.size = (self.maxsize[0] * scale, self.maxsize[1] * scale)


		if scale > 0.3:
			self.BigMove(dt)

		else:
			self.LittleMove(dt)


		self.healthBar()
		self.brain.switch()
		self.updatevisual(sprite = self.sprite)
		self.sprite.anchor_x = self.sprite.width/2
		self.sprite.anchor_y = self.sprite.height/2


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
			self.speed = 3
			clock.schedule_once(self.hitflip, 1.5)

		elif (type(obj) == type(self.player)) and (obj.ram):
			self.health -= obj.meleeDamage
			self.speed = 3
			self.hitcool = True
			clock.schedule_once(self.hitflip, 1.5)

		if (self.health/62.5 + 0.2) < 0.55:
			self.camera.targetZoom = 0.5

	def delete(self):
		self.camera.player = self.player
		self.camera.targetZoom = 0.5

		self.objects.add(collectibles.ArmourDrop(pos = self.pos, size = (40,40), camera = self.camera, batch = self.batch, group = self.group))
		self.sprite.delete()
		del self.sprite

		try:
			self.healthbar.delete()
			del self.healthbar

		except:
			pass



class Drone(Enemy):
	
	def __init__(self, pos, speed, player, mapsize, objects, handler, camera, batch, group):
		super().__init__(pos,(100,100), shapes.Rectangle(*pos, *(100,100), color=(0, 255, 255), batch=batch, group=group))
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)


		self.batch = batch
		self.group = group
		self.mapsize = mapsize


		self.vel = (1,1)
		
		self.speed = speed
		self.handler = handler
		self.damage = 5
		self.turnspeed = 0.02

		self.sight = randint(300,600)
		self.personal_space = randint(200,300)

		self.camera = camera

		self.player = player

		self.objects = objects

		self.stun = False


		#death flag
		self.alive = True

	# def EndStun(self, dt):
	# 	self.stun = False

	# def StartStun(self):
	# 	self.stun = True

	def avoid_other(self):
		forcex = 0
		forcey = 0
		sx, sy = self.pos
		

		for boid in [obj for obj in self.objects if (type(obj) == type(self))]:
	
			if math.dist(self.pos,boid.pos) < self.personal_space:
				
				bx, by = boid.pos


				forcex += sx - bx
				forcey += sy - by
		
		dx, dy = self.vel


		dx += forcex*0.1
		dy += forcey*0.1

		self.vel = (dx,dy)

	def speed_limit(self):
		dx, dy = self.vel
		speed = math.hypot(*self.vel)

		if speed > 1000:
			dx /= speed
			dy /= speed

			dx *= 1000
			dy *= 1000

		self.vel = (dx,dy)

	def seek_center(self):
		mx, my = self.mapsize
		centerx = mx/2
		centery = my/2

		dx, dy = self.vel
		x, y = self.pos


		dx += (centerx - x) * 0.1
		dy += (centery - y) * 0.1

		self.vel = (dx,dy)

	def avoid_center(self):
		centerx = 0
		centery = 0
		num = 0

		for boid in [obj for obj in self.objects if (type(obj) == type(self))]:

			
			x, y = boid.pos

			centerx += x
			centery += y

			num += 1

		if num != 0:
			dx, dy = self.vel
			x, y = self.pos

			centerx = centerx/num
			centery = centery/num



			dx -= (centerx - x) * 0.05
			dy -= (centery - y) * 0.05

			self.vel = (dx,dy)


	def edge_check(self):
		x, y = self.pos
		dx, dy = self.vel
		mx, my = self.mapsize

		if x < 200:
			dx += 10
		if x > mx-200:
			dx -= 10
		if y < 200:
			dy += 10
		if y > my-200:
			dy -= 10

		

		self.pos = (x,y)
		self.vel = (dx,dy)

	def align_vel(self):
		averagex = 0
		averagey = 0
		num = 0

		for boid in [obj for obj in self.objects if (type(obj) == type(self))]:

			if math.dist(self.pos, boid.pos) > self.sight:
				dx, dy = boid.vel

				averagex += dx
				averagey += dy

				num += 1

		if num != 0:
			averagex /= num
			averagey /= num

			dx, dy = self.vel

			dx += (averagex - dx) * 0.03
			dy += (averagey - dy) * 0.03

			self.vel = (dx,dy)


	def random_vel(self):

		dx, dy = self.vel

		dx += random() * 100
		dy += random() * 100


		self.vel = (dx,dy)





	def update(self, dt):
		"""Updates pos and velocityof enemy"""

		#anti-overlap
		self.avoid_other()
		self.speed_limit()
		self.align_vel()
		self.seek_center()
		self.avoid_center()
		self.edge_check()
		self.random_vel()


		#pathfinding
		x, y = self.pos
		dx, dy = self.vel

		# if not self.stun:
		# 	x,y, dx,dy = Enemy.AgresiveMovement(pos = (x,y), vel = (dx,dy), speed = self.speed, turnspeed = self.turnspeed, target = target, dt = dt)
		# else:


		x += dx * dt * self.speed
		y += dy * dt * self.speed
		

		self.updatevisual(sprite = self.sprite, rotation = math.degrees( -math.atan2(*self.vel)  ))
		self.sprite.anchor_x = (self.sprite.width/2)
		self.sprite.anchor_y = (self.sprite.height/2)

		self.pos = (x,y)
		self.vel = (dx,dy)



	def delete(self):
		self.objects.add(collectibles.ArmourDrop(pos = self.pos, size = (40,40), camera = self.camera, batch = self.batch, group = self.group))
		self.sprite.delete()
		del self.sprite


	def hit(self, obj, dt):
		"""handles collision behavior"""

		pass

class Flock:
	pass

class BigWheel(Enemy):
	pass

class Mech(Enemy):
	pass



