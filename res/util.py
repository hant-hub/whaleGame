from pyglet import *




class Camera:

	def __init__(self, pos, zoom, player, window):
		self.pos = pos
		self.zoom = zoom
		self.player = player
		self.window = window

	def update(self, dt):
		px, py = self.player.pos

		tx, ty = -(px - self.window.width/2),-(py - self.window.height/2)
		x, y = self.pos

		tx -= x
		ty -= y

		x += tx * dt
		y += ty * dt

		self.pos = (x,y)



class visibleEntity:

	def __init__(self, pos, size):
		self.pos = pos
		self.size = size
		self.camera = None


	def updatevisual(self,sprite, rotation = None):

		x, y = self.pos
		cx, cy = self.camera.pos

		sprite.x = x + cx
		sprite.y = y + cy

		if rotation != None:
			sprite.rotation = rotation



