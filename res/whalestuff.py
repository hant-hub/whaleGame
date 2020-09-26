from pyglet import *
import math
from res.util import visibleEntity



class Player(visibleEntity):

	def __init__(self, pos, size, speed, handler, batch):
		super().__init__(pos,size)




		self.rec = shapes.Rectangle(*pos, *size, color=(255, 255, 255), batch=batch)

		self.rec.anchor_x = (self.rec.width/3) * 2
		self.rec.anchor_y = (self.rec.height/2)

		self.vel = (0,0)
		self.speed = speed
		self.handler = handler
		self.turnspeed = 0.05



	def update(self, dt):

		
		tx,ty = self.handler.target
		x, y = self.pos
		dx, dy = self.vel
		cx, cy = self.camera.pos

		dist = math.dist([x,y], [tx, ty])


		#create target velocity
		tdx = (tx - x)
		tdy = (ty - y)



		#update velocity

		dx += (tdx - dx) * self.turnspeed * self.speed
		dy += (tdy - dy) * self.turnspeed * self.speed




		#update position

		x += dx * dt
		y += dy * dt


		

		#apply rotation

		rotation = math.degrees(math.atan2(dy, dx))

		self.updatevisual(self.rec, -rotation)

		self.pos = (x,y)
		self.vel = (dx,dy)
		






