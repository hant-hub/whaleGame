from pyglet import *
import math



class Handler:

	def __init__(self, window):
		self.window = window	

		#init rotation for gameplay
		self.target = (0,0)	
		self.player = None


	def gamePlayHandler(self, player):
		self.player=player


		def on_mouse_motion(x,y,dx,dy, buttons = None, modifiers = None):
			self.target = (x,y)

		def on_mouse_press(x,y, button, modifiers):
			if button == window.mouse.LEFT:
				self.target = (x,y)
				self.player.Ram.ramStart(parent = player)

			if button == window.mouse.RIGHT:
				self.player.damage = False
				self.player.rec.opacity = 128



		def on_mouse_release(x,y, button, modifiers):

			if button == window.mouse.RIGHT:
				self.player.damage = True
				self.player.rec.opacity = 255


		self.window.push_handlers(on_mouse_drag = on_mouse_motion, on_mouse_motion = on_mouse_motion, on_mouse_press=on_mouse_press, on_mouse_release = on_mouse_release)




	def endGamePlay(self):
		self.window.pop_handlers()