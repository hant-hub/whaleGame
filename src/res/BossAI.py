import math
from time import sleep







class AiBrain:


	def __init__(self, body):
		self.body = body
		self.history = [None]
		self.states = {}
		self.decision = None



	def makestate(self, func, stateName):

		def behavior(*args, **kwargs):
			self.history.append(stateName)
			output = func(*args, **kwargs)
			self.switch()

			return output
		return behavior



	def addState(self,behavior, stateName):

		behavior = self.makestate(behavior, stateName)

		self.states[stateName] = behavior
	


	def switch(self):
		stateName = self.decision(self.body, self.history)
		print(stateName)
		self.states[stateName](self.body)






if __name__ == "__main__":
	test = AiBrain(None)


	def idle(body):
		sleep(1)

	def attack(body):
		sleep(1)

	def defend(body):
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










