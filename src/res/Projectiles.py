"""Holds all projectile types and behavior.

This includes both enemy and player projectiles as well as interfaces for
instantiating projectiles with functions
"""



from pyglet import *
import math
from res.util import visibleEntity



class Harpoon(visibleEntity):
	"""Basic projectile for Enemies"""

	def __init__(self, pos, size, speed, vel, side, camera, batch):
		super().__init__(pos,size, shapes.Rectangle(*pos, *size, color=(255, 255, 255), batch=batch))
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


		self.pos = (x,y)
		self.vel = (dx,dy)


	def hit(self,obj):
		"""handles behavior when colliding with other objects. Currently does nothing"""
		pass


	def kill(self, dt):
		"""Deletes projectile after it reaches the end of its 'life' """
		self.alive = False




def ShootHarpoon(me, other, output):
	"""method for launching harpoon projectile"""
	tx, ty = other.pos
	x, y = me.pos

	tx -= x
	ty -= y

	tx /= math.dist(other.pos, me.pos)
	ty /= math.dist(other.pos, me.pos)

	output.add(Harpoon(pos = me.pos, size = (30,10), speed = 15, vel = (tx,ty), side = type(me), camera = me.camera, batch = me.batch))