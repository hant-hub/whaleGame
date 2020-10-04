"""logic and behavior for GUI elements"""

from pyglet import *





class GUI:
	"""main interface for GUI"""

	def __init__(self, pos, player, window, batch):
		self.pos = pos
		self.player = player

		#create healthbar
		self.healthbar = Healthbar(pos = (30, window.height - 60), size = (400, 40), player = player, batch = batch)

		#create airmeter
		self.airmeter = AirMeter(pos = (window.width-500, window.height - 60), size = (400,40), player = player, batch = batch)

	def update(self, dt):
		self.healthbar.update(dt)
		self.airmeter.update(dt)




class Healthbar:
	"""convienience function for displaying health data. Might refactor later"""
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



class AirMeter:
	"""convienience class for displaying air (remaining dive time). Might refactor into just a function later"""

	def __init__(self, pos, size, player, batch):
		self.pos = pos
		self.player = player

		self.size = size
		self.maxsize = size
		self.rec = shapes.Rectangle(*pos, *size, color=(0, 0, 255), batch=batch)




	def update(self, dt):

		airpart = self.player.air/100

		maxwidth, maxheight = self.maxsize



		width = maxwidth * airpart

		self.rec.width = width









