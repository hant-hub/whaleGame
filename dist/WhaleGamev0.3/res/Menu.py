from pyglet import *



class MenuButton:

	def __init__(self, pos, size, sprite, func):

		self.pos = pos
		self.size = size
		self.sprite = sprite
		self.activated = False
		self.func = func



	def clicked(self, point):
		px, py = point
		x, y = self.pos
		width, height = self.size


		if (px > x) and (px < (x + width)):
			if (py > y) and (py < (y + height)):

				self.activated = True


		


def StartGame(screen, **kwargs):
	clock.unschedule(kwargs['TitleUpdate'])
	screen.pop_handlers()

	screen.on_draw = kwargs['Gamedraw']
	kwargs['handler'].gamePlayHandler(kwargs['handler'].player, kwargs['handler'].camera)
	clock.schedule_interval(kwargs['GameUpdate'], 1/240)
	kwargs['handler'].titleMenu = False
	kwargs['handler'].pauseMenu = False



def quitGame(screen, **kwargs):
	screen.close()


def quitTitle(screen, **kwargs):
	clock.unschedule(kwargs['TitleUpdate'])
	screen.pop_handlers()

	kwargs['handler'].gamePlayHandler(kwargs['handler'].player, kwargs['handler'].camera)
	clock.schedule_interval(kwargs['GameUpdate'], 1/240)
	kwargs['handler'].titleMenu = True
	kwargs['handler'].pauseMenu = False



def createTitleMenu(screen, objectlist, batch, **kwargs):
	objectlist.add(MenuButton(pos = (screen.width/2 - 100, screen.height/2 + 50), size = (200,100), sprite = (shapes.Rectangle(*(screen.width/2- 100, screen.height/2 + 50), *(200,100), color = (255,255,255), batch = batch)), func = StartGame))
	objectlist.add(MenuButton(pos = (screen.width/2 - 100, screen.height/2 - 150), size = (200,100), sprite = (shapes.Rectangle(*(screen.width/2 - 100, screen.height/2 - 150), *(200,100), color = (255,255,255), batch = batch)), func = quitGame))


def createPauseMenu(screen, objectlist, batch, **kwargs):
	objectlist.add(MenuButton(pos = (screen.width/2 - 100, screen.height/2 + 150), size = (200,100), sprite = (shapes.Rectangle(*(screen.width/2- 100, screen.height/2+150), *(200,100), color = (255,255,255), batch = batch)), func = StartGame))
	objectlist.add(MenuButton(pos = (screen.width/2 - 100, screen.height/2-50), size = (200,100), sprite = (shapes.Rectangle(*(screen.width/2- 100, screen.height/2-50), *(200,100), color = (255,255,255), batch = batch)), func = quitTitle))
	objectlist.add(MenuButton(pos = (screen.width/2 - 100, screen.height/2 - 250), size = (200,100), sprite = (shapes.Rectangle(*(screen.width/2 - 100, screen.height/2 - 250), *(200,100), color = (255,255,255), batch = batch)), func = quitGame))



def TitleMenu(screen, **kwargs):
	clock.unschedule(kwargs['GameUpdate'])

	for button in kwargs["objectlist"]:
		button.sprite.delete()
		del button.sprite

	kwargs["objectlist"].clear()
	createTitleMenu(screen = screen, objectlist = kwargs["objectlist"], batch = kwargs['batch'])


	kwargs['handler'].EndHandling()
	kwargs['handler'].MenuHandler()
	screen.on_draw = kwargs['TitleDraw']
	clock.schedule_interval(kwargs['titleUpdate'], 1/240)




def PauseMenu(screen, **kwargs):
	clock.unschedule(kwargs['GameUpdate'])
	for button in kwargs["objectlist"]:
		button.sprite.delete()
		del button.sprite

	kwargs["objectlist"].clear()

	createPauseMenu(screen = screen, objectlist = kwargs["objectlist"], batch = kwargs['batch'])

	kwargs['handler'].EndHandling()
	kwargs['handler'].MenuHandler()
	screen.on_draw = kwargs['TitleDraw']
	clock.schedule_interval(kwargs['titleUpdate'], 1/240)