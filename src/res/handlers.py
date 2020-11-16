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

			if button == window.mouse.RIGHT:
				self.player.damage = False
				self.player.dive = True
				self.player.sprite.opacity = 128

				clock.unschedule(player.FlipBool)



		def on_mouse_release(x,y, button, modifiers):

			if button == window.mouse.RIGHT:
				self.player.dive = False
				self.player.damage = True
				self.player.sprite.opacity = 255


		def on_key_press(symbol, modifiers):

			if (symbol == window.key.T) and self.player.tailcool:
				self.player.TailSlap()

			elif (symbol == window.key.F) and self.player.lasercool:
				print(self.player.lasercool)
				self.player.startLaser()

			elif (symbol == window.key.TAB):
				self.titleMenu = True

			else:
				pass



		self.window.push_handlers(on_mouse_drag = on_mouse_motion, on_mouse_motion = on_mouse_motion, on_mouse_press=on_mouse_press, on_mouse_release = on_mouse_release, on_mouse_scroll = on_mouse_scroll, on_key_press = on_key_press)



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