from pyglet import *





class GUI:

	def __init__(self, pos, player, window, batch):
		self.pos = pos
		self.player = player

		#create healthbar
		self.healthbar = Healthbar(pos = (30, window.height - 60), size = (150, 40), player = player, batch = batch)

	def update(self, dt):
		self.healthbar.update(dt)




class Healthbar:

	def __init__(self, pos, size, player, batch):
		self.pos = pos
		self.player = player

		self.size = size
		self.maxsize = size
		self.rec = shapes.Rectangle(*pos, *size, color=(255, 0, 0), batch=batch)
	
	def update(self, dt):

		#Grab values
		maxhealth = self.player.maxhealth
		currenthealth = self.player.health

		#grab size data
		width, height = self.size
		maxwidth, maxheight = self.maxsize

		#calculate %
		healthpart = currenthealth/maxhealth


		#apply % to size
		width = maxwidth*healthpart

		#change visual
		self.rec.width = width

		#repack values
		self.size = (width, height)











