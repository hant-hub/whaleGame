"""logic and behavior for GUI elements"""

from pyglet import *





class GUI:
	"""main interface for GUI"""

	def __init__(self, pos, player, window, batch, group):
		self.pos = pos
		self.player = player


		#create healthbar
		self.healthbar = shapes.Rectangle(*(30, window.height - 60), *(400, 40), color=(255, 0, 0), batch=batch, group=group)

		#create armourbar
		self.armourbar = shapes.Rectangle(*(30, window.height - 110), *(400, 40), color=(100,100,100), batch=batch, group=group)


		#create airmeter
		self.airmeter = shapes.Rectangle(*(window.width-500, window.height - 60), *(400,40), color=(0, 0, 255), batch=batch, group=group)

		#create Primary Ability indicator
		self.tail = shapes.Rectangle(*(30, window.height - 180), *(25,50), color = (255,0,0), batch = batch, group = group)

		#create Secondary Ability Indicator
		self.laser = shapes.Rectangle(*(70, window.height - 180), *(25,50), color = (255,0,0), batch = batch, group = group)

		#create Tertiatry Abilty Indicator
		self.third = shapes.Rectangle(*(110, window.height - 180), *(25,50), color = (255,0,0), batch = batch, group = group)

	def update(self, dt):
		self.HealthBar()
		self.ArmourBar()
		self.AirMeter()
		self.Firstindicator()
		self.SecondIndicator()
		self.ThirdIndicator()


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

	def ArmourBar(self):
		maxhealth = 30
		currenthealth = self.player.armour

		#grab size data
		width, height = (400,40)

		#calculate %
		healthpart = currenthealth/maxhealth


		#apply % to size
		if healthpart < 0:
			healthpart = 0
		width = width*healthpart

		#change visual
		self.armourbar.width = width



	def AirMeter(self):
		airpart = self.player.air/100

		maxwidth, maxheight = (400,40)



		width = maxwidth * airpart

		self.airmeter.width = width

	def Firstindicator(self):
		tail = self.player.abilityOneCool

		if tail:
			self.tail.opacity = 255

		else:
			self.tail.opacity = 0


	def SecondIndicator(self):
		laser = self.player.abilityTwoCool

		if laser:
			self.laser.opacity = 255

		else:
			self.laser.opacity = 0


	def ThirdIndicator(self):
		laser = self.player.abilityThreeCool

		if laser:
			self.third.opacity = 255

		else:
			self.third.opacity = 0

