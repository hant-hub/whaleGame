from pyglet import *
import math
from res import util, Projectiles, enemies




class TailStrike:

	def TailSlap(parent,cool):
		def EnemyTailHit(enemy):
			px, py = parent.pos
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
				enemy.hit(parent, 0)





		parent.FlipBool(0, cool)
		parent.objects.add(util.Hitbox(pos = parent.pos, size = (500, 550), rotation = (-math.degrees(math.atan2(parent.vel[1], parent.vel[0]))) - 180, sprite = shapes.Rectangle(*parent.pos, width = 500, height = 550, color = (0,255,0), batch = parent.batch, group = parent.group), camera = parent.camera, duration = 0.25, enemyEffect = EnemyTailHit, playerEffect = (lambda x: None)))
		clock.schedule_once(parent.FlipBool, 3, cool)


	





class LaserStrike:

	def startLaser(parent, cool):
		parent.FlipBool(0, cool)
		LaserStrike.Start(parent)
		clock.schedule_once(parent.FlipBool, 5, cool)


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

	def Sing(parent, cool):
		



		for obj in parent.objects:
			if isinstance(obj, enemies.EnemyProjectile):
				obj.alive = False



		parent.FlipBool(0, cool)
		clock.schedule_once(parent.FlipBool, 20, cool)




class HomingWeak:

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
		parent.FlipBool(0, cool)
		clock.schedule_once(parent.FlipBool, 4, cool)

		things = HomingWeak.getClosestEnemy(parent)

		for x in range(4):
			parent.objects.add(Projectiles.PlayerSmartProjectile(pos = parent.pos, size = (20,20), speed = 1, equation = HomingWeak.homing, rotation = 0 , offset = 0, side = None, camera = parent.camera, batch = parent.batch, group = parent.group, enemy = enemies.Enemy, args = next(things)))

