from pyglet import *



class MenuButton:

	def __init__(self, pos, size, image, batch, group, func):

		self.pos = (pos[0] - size[0]/2 ,pos[1] - size[1]/2)
		self.size = size
		self.anims = image
		self.batch = batch
		self.group = group

		self.sprite = sprite.Sprite(image[0], batch = batch, group = group)
		self.sprite.position = self.pos
		self.activated = False
		self.func = func



	def call(self, dt):
		self.activated = True

	def clicked(self, point):
		px, py = point
		x, y = self.pos
		width, height = self.size
		




		if (px > x) and (px < (x + width)):
			if (py > y) and (py < (y + height)):
				self.sprite.delete()
				self.sprite = sprite.Sprite(self.anims[1], batch = self.batch, group = self.group)
				self.sprite.position =self.pos
				clock.schedule_once(self.call, self.anims[1].get_duration())

		


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





def createTitleMenu(screen, sprites, objectlist, batch, **kwargs):
	screen.clear()
	background = graphics.OrderedGroup(0)
	foreground = graphics.OrderedGroup(1)
	objectlist.add(MenuButton(pos = (screen.width/2, screen.height/2 +50), size = (sprites["start"][0].width,sprites["start"][0].height), image = sprites["start"], batch = batch, group = foreground, func = StartGame))
	objectlist.add(MenuButton(pos = (screen.width/2, screen.height/2 - 100), size = (sprites["exit"][0].width,sprites["exit"][0].height), image = sprites["exit"], batch = batch, group = foreground, func = quitGame))



def createPauseMenu(screen, sprites, objectlist, batch, **kwargs):
	background = graphics.OrderedGroup(0)
	foreground = graphics.OrderedGroup(1)
	panel = sprite.Sprite(sprites["pausepanel"], x= 477, y = -280, batch = batch, group = background)
	panel.scale = 0.39

	objectlist.add(panel)
	objectlist.add(MenuButton(pos = (screen.width/2, screen.height/2 + 150), size = ( sprites["resume"][0].width, sprites["resume"][0].height), image = sprites["resume"], batch = batch, group = foreground, func = StartGame))
	objectlist.add(MenuButton(pos = (screen.width/2, screen.height/2), size =( sprites["menu"][0].width, sprites["menu"][0].height), image = sprites["menu"], batch = batch, group = foreground, func = quitTitle))
	objectlist.add(MenuButton(pos = (screen.width/2, screen.height/2 - 150), size = ( sprites["quit"][0].width, sprites["quit"][0].height), image = sprites["quit"], batch = batch, group = foreground, func = quitGame))



def TitleMenu(screen, **kwargs):
	clock.unschedule(kwargs['GameUpdate'])

	for button in kwargs["objectlist"]:
		if isinstance(button, sprite.Sprite):
			button.delete()
		else:
			button.sprite.delete()
			del button.sprite
		del button

	kwargs["objectlist"].clear()
	createTitleMenu(screen = screen, sprites = kwargs["sprites"], objectlist = kwargs["objectlist"], batch = kwargs['batch'])


	kwargs['handler'].EndHandling()
	kwargs['handler'].MenuHandler()
	screen.on_draw = kwargs['TitleDraw']
	clock.schedule_interval(kwargs['titleUpdate'], 1/240)




def PauseMenu(screen, **kwargs):
	clock.unschedule(kwargs['GameUpdate'])
	for button in kwargs["objectlist"]:
		button.sprite.delete()
		del button.sprite
		del button

	kwargs["objectlist"].clear()

	createPauseMenu(screen = screen, sprites = kwargs["sprites"], objectlist = kwargs["objectlist"], batch = kwargs['batch'])

	kwargs['handler'].EndHandling()
	kwargs['handler'].MenuHandler()
	screen.on_draw = kwargs['TitleDraw']
	clock.schedule_interval(kwargs['titleUpdate'], 1/240)