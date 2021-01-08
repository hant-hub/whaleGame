from pyglet import *
from res import whalestuff, util
from random import choice, randint






class HealthPack(util.visibleEntity):

	def __init__(self, health, pos, size, camera, batch, group):
		super().__init__(pos,size, shapes.Rectangle(*pos, *size, color=(0, 255, 0), batch=batch, group = group))
		self.sprite.anchor_x = self.sprite.width/2
		self.sprite.anchor_y = self.sprite.height/2
		self.health = health
		self.alive = True
		self.camera = camera



	def update(self, dt):
		self.updatevisual(image = self.sprite)
		self.sprite.anchor_x = self.sprite.width/2
		self.sprite.anchor_y = self.sprite.height/2


	def hit(self, obj, dt):
		if isinstance(obj, whalestuff.Player):
			self.alive = False
			if (obj.health + self.health) >= obj.maxhealth:
				obj.health = obj.maxhealth

			else:
				obj.health += self.health


		else:
			pass


class SquidPowerup(util.visibleEntity):

	def __init__(self, pos, size, color, camera, batch, group, sprite = None):
		if sprite == None:
			sprite = shapes.Rectangle(*pos, *size, color=color, batch=batch, group = group)
		super().__init__(pos,size, sprite)
		self.sprite.anchor_x = self.sprite.width/2
		self.sprite.anchor_y = self.sprite.height/2
		self.camera = camera
		self.alive = True



	def update(self, dt):
		self.updatevisual(image = self.sprite)
		self.sprite.anchor_x = self.sprite.width/2
		self.sprite.anchor_y = self.sprite.height/2





class Dashbooster(SquidPowerup):

	def __init__(self, pos, size,  camera, batch, group):
		super().__init__(pos, size, (150,150,255), camera, batch, group)



	def resetSpeed(self, dt, obj):
		obj.speed = 1

	def hit(self, obj, dt):
		if isinstance(obj, whalestuff.Player):
			self.alive = False
			obj.speed = 3
			clock.schedule_once(self.resetSpeed, 13.5, obj)


		else:
			pass



class DiveBooster(SquidPowerup):

	def __init__(self, pos, size, camera, batch, group):
		super().__init__(pos, size, (0,0,255),  camera, batch, group)

	def resetDive(self, dt, obj):
		obj.damage = True

	def hit(self, obj, dt):
		if isinstance(obj, whalestuff.Player):
			self.alive = False
			obj.damage = False
			clock.unschedule()
			clock.schedule_once(self.resetDive, 9, obj)


		else:
			pass



class DamageBooster(SquidPowerup):

	def __init__(self, pos, size, camera, batch, group):
		super().__init__(pos, size, (150,0,0), camera, batch, group)

	def resetDamage(self, dt, obj):
		obj.meleeDamage = False

	def hit(self, obj, dt):
		if isinstance(obj, whalestuff.Player):
			self.alive = False
			obj.meleeDamage = 2
			clock.schedule_once(self.resetDamage, 10, obj)


		else:
			pass


class ArmourDrop(SquidPowerup):

	sprites = None

	def __init__(self, pos, size, camera, batch, group):
		super().__init__(pos, size, (100,100,100), camera, batch, group, sprite = sprite.Sprite(choice(ArmourDrop.sprites), batch = batch, group = group))
		self.sprite.rotation = randint(0,359)


	def hit(self, obj, dt):
		if isinstance(obj, whalestuff.Player):
			self.alive = False
			if obj.armour <= 50:
				obj.armour += 5


		else:
			pass