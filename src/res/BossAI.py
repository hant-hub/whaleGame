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



if __name__ == "__main__":
	test = AiBrain(None)


	def idle(dt, body):
		sleep(1)

	def attack(dt, body):
		sleep(1)

	def defend(dt, body):
		sleep(1)

	def decision(body, history):
		if history[-1] != "idle":
			return "idle"

		elif history[-2] == "attack":
			return "defend"

		else:
			return "attack"

	test.decision = decision
	test.addState(idle, "idle")
	test.addState(attack, "attack")
	test.addState(defend, "defend")

	test.state = "idle"
	test.switch()
	print('hello')
	test.states[test.history[-1]](None)
	sleep(2.5)
	test.switch()
	test.states[test.history[-1]](None)










