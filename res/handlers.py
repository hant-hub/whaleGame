from pyglet import *
import math




class Handler:

	def __init__(self, window):
		self.window = window	

		#init rotation for gameplay
		self.target = (0,0)	


	def gamePlayHandler(self):


		def on_mouse_motion(x,y,dx,dy):
			self.target = (x,y)

		self.window.push_handlers(on_mouse_motion = on_mouse_motion)




	def endGamePlay(self):
		self.window.pop_handlers()