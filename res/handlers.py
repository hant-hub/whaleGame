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


		def on_mouse_motion(x,y,dx,dy):
			self.target = (x,y)

		def on_mouse_press(x,y, button, modifiers):
			if button == window.mouse.LEFT:
				self.target = (x,y)
				self.player.Ram.ramStart(player)


		self.window.push_handlers(on_mouse_motion = on_mouse_motion, on_mouse_press=on_mouse_press)




	def endGamePlay(self):
		self.window.pop_handlers()