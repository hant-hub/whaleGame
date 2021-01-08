"""logic and behavior for GUI elements"""

from pyglet import *
from res import PlayerAbilities





class GUI:
	"""main interface for GUI"""

	def __init__(self, pos, player, window, sprites, batch, group):
		self.pos = pos
		self.player = player

		self.bottomlevel = graphics.OrderedGroup(0, parent = group)
		self.toplevel = graphics.OrderedGroup(1, parent = group)
		


		#create healthbar
		self.healthdecor = sprite.Sprite(sprites[(1,0)], *(10, window.height - 70), batch = batch, group = self.toplevel)
		self.healthdecor.scale = 0.5
		self.healthbar = shapes.BorderedRectangle(*(50, window.height - 60), *(400, 40), border = 10, color=(255, 0, 0), border_color =(0, 0, 0),  batch=batch, group=self.bottomlevel)

		#create armourbar
		self.armourdecor = sprite.Sprite(sprites[(1,1)], *(10, window.height - 142), batch = batch, group = self.toplevel)
		self.armourdecor.scale = 0.5
		self.armourbar = shapes.BorderedRectangle(*(50, window.height - 130), *(400, 40), border = 10, color=(100,100,100), border_color =(0, 0, 0), batch=batch, group=self.bottomlevel)

		#create Primary Ability indicator
		self.tail = sprite.Sprite(player.abilityIndicatorOne, *(30, window.height - 210), batch = batch, group = self.bottomlevel)
		self.tail.scale = 0.5

		#create Secondary Ability Indicator
		self.laser = sprite.Sprite(player.abilityIndicatorTwo, *(110, window.height - 210), batch = batch, group = self.bottomlevel)
		self.laser.scale = 0.5

		#create Tertiatry Abilty Indicator
		self.third = sprite.Sprite(player.abilityIndicatorThree, *(190, window.height - 210), batch = batch, group = self.bottomlevel)
		self.third.scale = 0.5

	def update(self, dt):
		self.HealthBar()
		self.ArmourBar()
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

