"""logic and behavior for GUI elements"""

from pyglet import *





class GUI:
	"""main interface for GUI"""

	def __init__(self, pos, player, window, batch, group):
		self.pos = pos
		self.player = player


		#create healthbar
		self.healthbar = shapes.Rectangle(*(30, window.height - 60), *(400, 40), color=(255, 0, 0), batch=batch, group=group)

		#create airmeter
		self.airmeter = shapes.Rectangle(*(window.width-500, window.height - 60), *(400,40), color=(0, 0, 255), batch=batch, group=group)

		#create tailindicator
		self.tail = shapes.Rectangle(*(30, window.height - 130), *(25,50), color = (0,0,255), batch = batch, group = group)

	def update(self, dt):
		self.HealthBar()
		self.AirMeter()
		self.tailindicator()


	def HealthBar(self):


		#Grab values
		maxhealth = self.player.maxhealth
		currenthealth = self.player.health

		#grab size data
		width, height = (400,40)

		#calculate %
		healthpart = currenthealth/maxhealth


		#apply % to size
		if healthpart < 0:
			healthpart = 0
		width = width*healthpart

		#change visual
		self.healthbar.width = width


	def AirMeter(self):
		airpart = self.player.air/100

		maxwidth, maxheight = (400,40)



		width = maxwidth * airpart

		self.airmeter.width = width

	def tailindicator(self):
		tail = self.player.tailcool

		if tail:
			self.tail.opacity = 255

		else:
			self.tail.opacity = 0





