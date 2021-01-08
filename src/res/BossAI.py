import math
from time import sleep
from pyglet import *







class AiBrain:


	def __init__(self, body):
		self.body = body
		self.history = []
		self.states = {}
		self.decision = None
		self.canswitch = True



	def makestate(self, func, stateName):

		def behavior(*args, **kwargs):
			output = func(*args, **kwargs)


			return output
		return behavior

	def resetSwitch(self, dt):
		self.canswitch = True
		clock.unschedule(self.states[self.history[-1]][0])



	def addState(self,behavior, stateName, stateLength, interval):

		behavior = self.makestate(behavior, stateName)

		self.states[stateName] = (behavior,stateLength, interval)
	


	def switch(self):
		if self.canswitch:
			stateName = self.decision(self.body, self.history)
			self.canswitch = False
			self.history.append(stateName)
			clock.schedule_interval(self.states[stateName][0], self.states[stateName][2], self.body)
			clock.schedule_once(self.resetSwitch, self.states[stateName][1])
		else:
			pass


		
		#self.states[stateName](self.body)


	def kill(self):
		for func in self.states.values():
			clock.unschedule(func[0])









