from pyglet import *
import math
from res import util, Projectiles, enemies




class TailStrike:

	sprite = None

	def TailSlap(parent,cool):

		def EnemyTailHit(enemy):
			px, py = parent.pos
			ex, ey = enemy.pos

			ex -= px
			ey -= py

			dist = math.hypot(ex, ey)

			enemy.vel = (ex * 3, ey * 3)

			enemy.StartStun()


			if hasattr(enemy, "health"):
				enemy.health -= 2
				enemy.hitcool = True
				clock.schedule_once(enemy.hitflip, 1.5)

			else:
				enemy.hit(parent, 0)


		def ProjectileTailSlap(projectile):
			clock.unschedule(projectile.kill)


			if isinstance(projectile, Projectiles.ProgrammableProjectile):
				rotation = projectile.rotation + math.radians(180)

				vel = (math.cos(rotation), math.sin(rotation))

				parent.objects.add(Projectiles.PlayerHarpoon(pos = projectile.pos, size = projectile.size, speed = 15, vel = vel, side = None, camera = projectile.camera, batch = projectile.batch, group = projectile.group))

				projectile.alive = False



			else:
				vel = (-projectile.vel[0], -projectile.vel[1])


				parent.objects.add(Projectiles.PlayerHarpoon(pos = projectile.pos, size = projectile.size, speed = 15, vel = vel, side = None, camera = projectile.camera, batch = projectile.batch, group = projectile.group))


				projectile.alive = False







		parent.FlipBool(0, cool, False)
		parent.objects.add(util.Hitbox(pos = parent.pos, size = (500, 550), rotation = (-math.degrees(math.atan2(parent.vel[1], parent.vel[0]))) - 180, sprite = shapes.Rectangle(*parent.pos, width = 500, height = 550, color = (0,255,0), batch = parent.batch, group = parent.group), camera = parent.camera, duration = 0.25, enemyEffect = EnemyTailHit, playerEffect = (lambda x: None), projectileEffect = ProjectileTailSlap))
		clock.schedule_once(parent.FlipBool, 3, cool, True)


	





class LaserStrike:
	sprite = None

	def startLaser(parent, cool):
		parent.FlipBool(0, cool, False)
		LaserStrike.Start(parent)
		clock.schedule_once(parent.FlipBool, 5, cool, True)


	def Start(parent):
		dx, dy = parent.vel

		parent.moveLock = True
		parent.ramcool = False
		parent.projectile = Projectiles.PlayerLaser(pos = parent.pos, width = 50, target = (dx,dy), camera = parent.camera, batch = parent.batch, group = parent.group, duration = 1.5)
		parent.projectile.sprite.rotation = -math.degrees(math.atan2(dy, dx))
		parent.objects.add(parent.projectile)

		clock.schedule_once(LaserStrike.End, 1.5, parent = parent)


	def End(dt, parent):

		parent.moveLock = False
		parent.ramcool = True
		parent.projectile = None








class WhaleSong:
	sprite = None

	def Sing(parent, cool):
		



		for obj in parent.objects:
			if isinstance(obj, enemies.EnemyProjectile):
				obj.alive = False

			if isinstance(obj, enemies.Drone):
				obj.StartStun()



		parent.FlipBool(0, cool, False)
		clock.schedule_once(parent.FlipBool, 20, cool, True)




class HomingWeak:
	sprite = None

	def homing(time, args):
		player = args[1]
		parent = args[0]

		dx, dy = parent.vel
		x, y = parent.pos
		tx, ty = player.pos

		tdx, tdy = (tx-x), (ty-y)

		dx += (tdx - dx) * 0.01
		dy += (tdy - dy) * 0.01

		parent.vel = (dx, dy)


		return (dx,dy)

	def getClosestEnemy(parent):
		objects = parent.objects.copy()
		target = next(obj for obj in objects if isinstance(obj, enemies.Enemy))
		while True:
			for obj in [obj for obj in objects if isinstance(obj, enemies.Enemy)]:
				if math.dist(target.pos, parent.pos) > math.dist(obj.pos, parent.pos):
					objects.remove(obj)
					target = obj

				yield obj




	def Fire(parent, cool):
		parent.FlipBool(0, cool, False)
		clock.schedule_once(parent.FlipBool, 4, cool, True)

		things = HomingWeak.getClosestEnemy(parent)

		for x in range(4):
			parent.objects.add(Projectiles.PlayerSmartProjectile(pos = parent.pos, size = (20,20), speed = 2, equation = HomingWeak.homing, rotation = 0 , offset = 0, side = None, camera = parent.camera, batch = parent.batch, group = parent.group, enemy = enemies.Enemy, args = next(things)))

