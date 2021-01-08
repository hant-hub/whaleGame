from pyglet import *
from res import whalestuff, util, handlers, gui, enemies, arena, Projectiles, Menu, collectibles, PlayerAbilities
from itertools import combinations
import concurrent.futures
import math





def main():
	"""Main functions, entry point of the application"""







	#initialize graphics
	screen = window.Window(vsync = True, fullscreen=True)

	

	#setup Titlescreen graphics
	titleBatch = graphics.Batch()


	#setup Gameplay Graphics
	batch = graphics.Batch()
	backgrounds = graphics.OrderedGroup(0)
	backgroundd = graphics.OrderedGroup(1)
	foregroundl = graphics.OrderedGroup(2)
	foreground = graphics.OrderedGroup(3)
	ui = graphics.OrderedGroup(4)





	#import art

	#game



	resources = ["Background/StarrySky.png",
				"Planets/planets.png",
				"GUI/Gui.png",
				"Menu/StartButton.png",
				"Menu/ExitButton.png",
				"Menu/MenuButton.png",
				"Menu/Resume.png",
				"Projectiles/Harpoon.png",
				"Menu/QuitGame.png",
				"Player/Whale Boi.png",
				"Menu/PausePanel.png",
				"Collectibles/Armor Drop.png",
				"GUI/Ability Indicators.png"

	]


	images = {}

	def load(path):
		images[path] = image.load("res/images/" + path)



	with concurrent.futures.ThreadPoolExecutor() as executor:

		results = [executor.submit(load, path) for path in resources]

		for f in concurrent.futures.as_completed(results):
			f.result()




	
	background = image.ImageGrid(images["Background/StarrySky.png"], rows = 4, columns = 6)
	background = [*background[18:23], *background[12:17], *background[6:11], *background[0:5]]

	Background_image = image.Animation.from_image_sequence(background, duration=1/8)
	Background = sprite.Sprite(Background_image, batch = batch, group = backgrounds)
	Background.scale = 1.001

	Planet_images = image.ImageGrid(images["Planets/planets.png"], 3, 3)

	Gui_images = image.ImageGrid(images["GUI/Gui.png"], 2, 3)
	Specials = image.ImageGrid(images["GUI/Ability Indicators.png"], rows = 2, columns = 2)


	PlayerAbilities.TailStrike.sprite = Specials[(1,1)]
	PlayerAbilities.LaserStrike.sprite = Specials[(0,0)]
	PlayerAbilities.WhaleSong.sprite = Specials[(0,1)]
	PlayerAbilities.HomingWeak.sprite = Specials[(1,0)]


	button_images = {}
	button_images["start"] = image.ImageGrid(images["Menu/StartButton.png"], rows = 2,  columns = 7)
	button_images["start"] = [*button_images["start"][7:12], *button_images["start"][0:5]]
	button_images["start"] = (button_images["start"][0],image.Animation.from_image_sequence(button_images["start"], duration=1/12))

	button_images["exit"] = image.ImageGrid(images["Menu/ExitButton.png"], rows = 2,  columns = 7)
	button_images["exit"] = [*button_images["exit"][7:12], *button_images["exit"][0:5]]
	button_images["exit"] = (button_images["exit"][0], image.Animation.from_image_sequence(button_images["exit"], duration=1/12))

	button_images["menu"] = image.ImageGrid(images["Menu/MenuButton.png"], rows = 2,  columns = 6) 
	button_images["menu"] = [*button_images["menu"][6:11], *button_images["menu"][0:5]]
	button_images["menu"] = (button_images["menu"][0], image.Animation.from_image_sequence(button_images["menu"], duration=1/12))

	button_images["resume"] = image.ImageGrid(images["Menu/Resume.png"], rows = 2,  columns = 6) 
	button_images["resume"] = [*button_images["resume"][6:11], *button_images["resume"][0:5]]
	button_images["resume"] = (button_images["resume"][0], image.Animation.from_image_sequence(button_images["resume"], duration=1/12))

	button_images["quit"] = image.ImageGrid(images["Menu/QuitGame.png"], rows = 2,  columns = 7) 
	button_images["quit"] = [*button_images["quit"][7:13], *button_images["quit"][0:5]]
	button_images["quit"] = (button_images["quit"][0], image.Animation.from_image_sequence(button_images["quit"], duration=1/12))

	button_images["pausepanel"] = images["Menu/PausePanel.png"]


	player_images = {}
	player_images["swim"] = image.ImageGrid(images["Player/Whale Boi.png"], rows = 2,  columns = 7) 
	player_images["swim"] = [*player_images["swim"][7:13], *player_images["swim"][0:5]]
	player_images["swim"] = (player_images["swim"][0], image.Animation.from_image_sequence(player_images["swim"], duration=1/12))


	collectibles_images = {}
	collectibles_images["amourpickups"] = image.ImageGrid(images["Collectibles/Armor Drop.png"], rows = 2,  columns = 2)
	collectibles_images["amourpickups"] = [collectibles_images["amourpickups"][0], *collectibles_images["amourpickups"][2:3]]

	
	collectibles.ArmourDrop.sprites = collectibles_images["amourpickups"]




	FishingBoatHarpoon = images["Projectiles/Harpoon.png"]
	enemies.FishingBoat.HarpoonSprite = FishingBoatHarpoon





	#title
	#background = shapes.Rectangle(x=0,y=0, width = screen.width, height = screen.height, color = (0,0,0), batch = titleBatch)

	#init objectset
	objects = set()

	#init Title objectset
	titleObjects = set()


	#create input handler
	handler = handlers.Handler(window = screen)

	#init player
	player = whalestuff.Player(pos = (100,100), size = (150, 75), speed = 1, handler = handler, objects = objects, images = player_images, batch = batch, group = foreground)
	camera = util.Camera(pos = (0,0), zoom = 0.5, player = player, handler=handler, window = screen)
	objects.add(player)
	objects.add(camera)




	#generate Map
	mapsize = (screen.width*3, screen.height*3)
	objects.update(arena.Map(k = 30,r = 1000,bounds = mapsize, size = 900, camera = camera, images = Planet_images, batch = batch, group = backgroundd).circles)


	#init GUI
	Gui = gui.GUI(pos = (0,0), player = player, window = screen, sprites = Gui_images, batch = batch, group = ui)
	objects.add(Gui)

	#link objects
	player.camera = camera
	handler.menu = titleObjects
	player.updatevisual(image = player.sprite)
	handler.gamePlayHandler(player = player, camera=camera)


	#create test enemy
	for x in range(5):
		objects.add(enemies.FishingBoat(pos = (screen.width/2, screen.height/2 - 100*x), speed = 1, player = player, objects = objects, handler = handler, camera = camera, batch = batch, group = foreground))

	#objects.add(enemies.Frigate(pos = (0,0), speed = 1, player = player, objects = objects, handler = handler, camera = camera, batch = batch, group = foreground))
	#objects.add(enemies.Galley(pos = (screen.width/2+400, screen.height/2 - 100), speed = 1, player = player, objects = objects, handler = handler, camera = camera, batch = batch, group = foreground))
	#objects.add(enemies.Galleon(pos = (700,700), speed = 0, player = player, objects = objects, mapsize = mapsize, screen = screen, handler = handler, camera = camera, batch = batch, group = foreground, ui = ui))
	#objects.add(enemies.Whaler(pos = (0,0), speed = 1, player = player, objects = objects, mapsize = mapsize, handler = handler, camera = camera, batch = batch, group = foreground, laserGroup = foregroundl))
	#objects.add(collectibles.HealthPack(health = 1000, pos = (500,500), size = (50,50), camera = camera, batch = batch, group = foreground))
	objects.add(collectibles.ArmourDrop(pos = (500,500), size = (75,75), camera = camera, batch=batch, group=foreground))
	# for x in range(40):
	# 	objects.add(enemies.Drone(pos = (0,0), speed = 1, player = player, mapsize = mapsize, objects = objects, handler = handler, camera = camera, batch = batch, group = foreground))
	#objects.add(enemies.Flock(player = player, mapsize = mapsize, objects = objects, handler = handler, camera = camera, batch = batch, group = foreground))
	

	def setup():
		#init objectset
		for obj in range(len(objects)):
			thing = objects.pop()
			if hasattr(thing, "delete"):
				thing.delete()
			del thing

		for obj in range(len(objects)):
			thing = objects.pop()
			if hasattr(thing, "delete"):
				thing.delete()
			del thing

		# objects.clear()


		#init player
		player.__init__(pos = (100,100), size = (150, 75), speed = 1, handler = handler, objects = objects, images = player_images, batch = batch, group = foreground)
		camera.__init__(pos = (0,0), zoom = 0.5, player = player, handler=handler, window = screen)
		objects.add(player)
		objects.add(camera)



		#generate Map
		mapsize = (screen.width*3, screen.height*3)
		objects.update(arena.Map(k = 30,r = 1000,bounds = mapsize, size = 900, camera = camera, images = Planet_images, batch = batch, group = backgroundd).circles)


		#init GUI
		Gui.__init__(pos = (0,0), player = player, window = screen, sprites = Gui_images, batch = batch, group = ui)
		objects.add(Gui)

		#link objects
		player.camera = camera
		handler.menu = titleObjects
		handler.gamePlayHandler(player = player, camera=camera)


		#create test enemy
		for x in range(5):
			objects.add(enemies.FishingBoat(pos = (screen.width/2, screen.height/2 - 100*x), speed = 1, player = player, objects = objects, handler = handler, camera = camera, batch = batch, group = foreground))

		objects.add(enemies.Frigate(pos = (0,0), speed = 1, player = player, objects = objects, handler = handler, camera = camera, batch = batch, group = foreground))
		objects.add(enemies.Galley(pos = (screen.width/2+400, screen.height/2 - 100), speed = 1, player = player, objects = objects, handler = handler, camera = camera, batch = batch, group = foreground))
		objects.add(enemies.Galleon(pos = (700,700), speed = 0, player = player, objects = objects, mapsize = mapsize, screen = screen, handler = handler, camera = camera, batch = batch, group = foreground, ui = ui))
		objects.add(enemies.Whaler(pos = (0,0), speed = 1, player = player, objects = objects, mapsize = mapsize, handler = handler, camera = camera, batch = batch, group = foreground, laserGroup = foregroundl))
		objects.add(collectibles.HealthPack(health = 10, pos = (500,500), size = (50,50), camera = camera, batch = batch, group = foreground))

		for obj in objects:
			obj.alive = True


	for obj in objects:
		obj.alive = True



	def GameDraw():
		"""Where draw call is made"""
		screen.clear()
		batch.draw()

	def TitleDraw():
		titleBatch.draw()




	#@util.timeit
	def GameUpdate(dt):
		"""Updates all objects every frame"""
		
		#cx, cy = camera.pos
		#tx, ty = camera.target

		#background.x = ((0-tx) * camera.zoom) + tx + cx
		#background.y = ((0-ty) * camera.zoom) + ty + cy

		#background.width = screen.width * camera.zoom
		#background.height = screen.height * camera.zoom

		#background.width = screen.width * camera.zoom
		#background.height = screen.height * camera.zoom



		if len([obj for obj in objects if isinstance(obj, enemies.Enemy) ]) > 40:
			sacrifice = objects.pop()
			if isinstance(sacrifice, enemies.Enemy):
				sacrifice.delete()
				del sacrifice
			else:
				objects.add(sacrifice)

		
		if handler.titleMenu == True:
			Menu.TitleMenu(screen = screen, handler = handler, TitleDraw = TitleDraw, titleUpdate = titleUpdate, GameUpdate = GameUpdate, objectlist = titleObjects, batch = titleBatch, sprites = button_images)
			setup()

		if handler.pauseMenu == True:
			Menu.PauseMenu(screen = screen, handler = handler, TitleDraw = TitleDraw, titleUpdate = titleUpdate, GameUpdate = GameUpdate, objectlist = titleObjects, batch = titleBatch, sprites = button_images)


		for corpse in [obj for obj in objects if not obj.alive]:
			objects.remove(corpse)
			corpse.delete()
			del corpse
		
		for obj in objects:
			obj.update(dt)



		for obj, obj2 in combinations([obj for obj in objects if isinstance(obj, (util.visibleEntity))], r=2):
			if util.collision.detectCollision(recA = obj.sprite, recB = obj2.sprite) and (obj != obj2) and (type(obj) != type(obj2)):
				if not (isinstance(obj, (enemies.Enemy, Projectiles.EnemyProjectile)) and isinstance(obj2, (enemies.Enemy, Projectiles.EnemyProjectile))):
					obj.hit(obj2, dt)
					obj2.hit(obj, dt)




		
	def titleUpdate(dt):

		for obj in [obj for obj in titleObjects if isinstance(obj, Menu.MenuButton)]:
			if obj.activated:
				obj.func(screen = screen, TitleDraw = TitleDraw, TitleUpdate = titleUpdate, Gamedraw = GameDraw, GameUpdate = GameUpdate, handler = handler)
				obj.activated = False






	Menu.TitleMenu(screen = screen, handler = handler, TitleDraw = TitleDraw, titleUpdate = titleUpdate, GameUpdate = GameUpdate, objectlist = titleObjects, batch = titleBatch, sprites = button_images)





		



	
	app.run()


if __name__ == "__main__":
	main()
