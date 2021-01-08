"""contains input handlers"""


from pyglet import *
from res import Menu
import math



class Handler:
	"""general class for managing input"""

	def __init__(self, window):
		self.window = window	

		#init rotation for gameplay
		self.target = (0,0)	
		self.player = None

		#buttonstuff
		self.menu = None
		self.titleMenu = True
		self.pauseMenu = False


	def gamePlayHandler(self, player, camera):
		"""Handler for direct gameplay.


		Defines and pushes the handlers for gameplay onto the hander stack
		"""
		self.player=player
		self.camera=camera

		def on_mouse_scroll(x, y, scroll_x, scroll_y):
			self.camera.zoom += scroll_y/10

			if self.camera.zoom <= 0.1:
				self.camera.zoom = 0.1


		def on_mouse_motion(x,y,dx,dy, buttons = None, modifiers = None):
			self.target = (x,y)

		def on_mouse_press(x,y, button, modifiers):
			if button == window.mouse.LEFT and self.player.ramcool:
				self.target = (x,y)
				self.player.Ram.ramStart(parent = player)



		def on_mouse_release(x,y, button, modifiers):

			if button == window.mouse.RIGHT:
				self.player.dive = False
				self.player.damage = True
				self.player.sprite.opacity = 255


		def on_key_press(symbol, modifiers):

			if (symbol == window.key._1) and self.player.abilityOneCool:
				self.player.AbilityOne(self.player, "one")

			elif (symbol == window.key._2) and self.player.abilityTwoCool:
				self.player.AbilityTwo(self.player, "two")

			elif (symbol == window.key._3) and self.player.abilityThreeCool:
				self.player.AbilityThree(self.player, "three")

			else:
				pass


		def menuStuff(symbol, modifiers):
			if (symbol == window.key.TAB):
				self.pauseMenu = True

			elif (symbol == window.key.L):
				self.camera.locked = not self.camera.locked



		self.window.push_handlers(on_key_press = menuStuff)
		self.window.push_handlers(on_mouse_drag = on_mouse_motion, on_mouse_motion = on_mouse_motion, on_mouse_press=on_mouse_press, on_mouse_release = on_mouse_release, on_key_press = on_key_press, on_mouse_scroll=on_mouse_scroll)



	def MenuHandler(self):

		def on_mouse_press(x,y, button, modifiers):
			if button == window.mouse.LEFT:

				for obj in [obj for obj in self.menu if isinstance(obj, (Menu.MenuButton))]:
					obj.clicked((x,y))



		self.window.push_handlers(on_mouse_press = on_mouse_press)




	def EndHandling(self):
		"""Pops handlers off stack.


		Should be used when changing handlers.
		ie: when going from gameplay to a menu
		"""
		self.window.pop_handlers()