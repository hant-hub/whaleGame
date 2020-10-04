"""contains input handlers"""


from pyglet import *
import math



class Handler:
	"""general class for managing input"""

	def __init__(self, window):
		self.window = window	

		#init rotation for gameplay
		self.target = (0,0)	
		self.player = None


	def gamePlayHandler(self, player):
		"""Handler for direct gameplay.


		Defines and pushes the handlers for gameplay onto the hander stack
		"""
		self.player=player


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


		self.window.push_handlers(on_mouse_drag = on_mouse_motion, on_mouse_motion = on_mouse_motion, on_mouse_press=on_mouse_press, on_mouse_release = on_mouse_release)




	def EndHandling(self):
		"""Pops handlers off stack.


		Should be used when changing handlers.
		ie: when going from gameplay to a menu
		"""
		self.window.pop_handlers()