from pyglet import *
from res import whalestuff, util, handlers, gui, enemies, arena, Projectiles, Menu, collectibles
from itertools import combinations
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
	resource.path = ['res/images']
	resource.reindex()
	Background_image = resource.image("Background/Temp_Stars.jpeg")
	Background = sprite.Sprite(Background_image, batch = batch, group = backgrounds)


	#title
	#background = shapes.Rectangle(x=0,y=0, width = screen.width, height = screen.height, color = (0,0,0), batch = titleBatch)

	#init objectset
	objects = set()

	#init Title objectset
	titleObjects = set()


	#create input handler
	handler = handlers.Handler(window = screen)

	#init player
	player = whalestuff.Player(pos = (100,100), size = (150, 75), speed = 1, handler = handler, objects = objects, batch = batch, group = foreground)
	camera = util.Camera(pos = (0,0), zoom = 0.5, player = player, handler=handler, window = screen)
	objects.add(player)
	objects.add(camera)



	#generate Map
	mapsize = (screen.width*3, screen.height*3)
	objects.update(arena.Map(k = 30,r = 1000,bounds = mapsize, size = 900, camera = camera, batch = batch, group = backgroundd).circles)


	#init GUI
	Gui = gui.GUI(pos = (0,0), player = player, window = screen, batch = batch, group = ui)
	objects.add(Gui)

	#link objects
	player.camera = camera
	handler.menu = titleObjects
	handler.gamePlayHandler(player = player, camera=camera)


	#create test enemy
	# for x in range(5):
	# 	objects.add(enemies.FishingBoat(pos = (screen.width/2, screen.height/2 - 100*x), speed = 1, player = player, objects = objects, handler = handler, camera = camera, batch = batch, group = foreground))

	# objects.add(enemies.Frigate(pos = (0,0), speed = 1, player = player, objects = objects, handler = handler, camera = camera, batch = batch, group = foreground))
	#objects.add(enemies.Galley(pos = (screen.width/2+400, screen.height/2 - 100), speed = 1, player = player, objects = objects, handler = handler, camera = camera, batch = batch, group = foreground))
	#objects.add(enemies.Galleon(pos = (700,700), speed = 0, player = player, objects = objects, mapsize = mapsize, screen = screen, handler = handler, camera = camera, batch = batch, group = foreground, ui = ui))
	#objects.add(enemies.Whaler(pos = (0,0), speed = 1, player = player, objects = objects, mapsize = mapsize, handler = handler, camera = camera, batch = batch, group = foreground, laserGroup = foregroundl))
	# objects.add(collectibles.HealthPack(health = 1000, pos = (500,500), size = (50,50), camera = camera, batch = batch, group = foreground))
	# objects.add(collectibles.DamageBooster(pos = (500,500), size = (75,75), camera = camera, batch=batch, group=foreground))
	objects.add(enemies.Kraken(pos = (0, -450), speed = 10, player = player, objects = objects, mapsize = mapsize, screen = screen, handler = handler, camera = camera, batch = batch, group = foreground, lasergroup = foregroundl, ui = ui))
	

	def setup():
		#init objectset
		for _ in range(len(objects)):
			thing = objects.pop()
			if hasattr(thing, "delete"):
				thing.delete()
			del thing


		#init player
		player.__init__(pos = (100,100), size = (150, 75), speed = 1, handler = handler, objects = objects, batch = batch, group = foreground)
		camera.__init__(pos = (0,0), zoom = 0.5, player = player, handler=handler, window = screen)
		objects.add(player)
		objects.add(camera)



		#generate Map
		mapsize = (screen.width*3, screen.height*3)
		objects.update(arena.Map(k = 30,r = 1000,bounds = mapsize, size = 900, camera = camera, batch = batch, group = backgroundd).circles)


		#init GUI
		Gui.__init__(pos = (0,0), player = player, window = screen, batch = batch, group = ui)
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
		screen.clear()
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
			Menu.TitleMenu(screen = screen, handler = handler, TitleDraw = TitleDraw, titleUpdate = titleUpdate, GameUpdate = GameUpdate, objectlist = titleObjects, batch = titleBatch)
			setup()

		if handler.pauseMenu == True:
			Menu.PauseMenu(screen = screen, handler = handler, TitleDraw = TitleDraw, titleUpdate = titleUpdate, GameUpdate = GameUpdate, objectlist = titleObjects, batch = titleBatch)


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

		for obj in titleObjects:
			if obj.activated:
				obj.func(screen = screen, TitleDraw = TitleDraw, TitleUpdate = titleUpdate, Gamedraw = GameDraw, GameUpdate = GameUpdate, handler = handler)
				obj.activated = False





	Menu.TitleMenu(screen = screen, handler = handler, TitleDraw = TitleDraw, titleUpdate = titleUpdate, GameUpdate = GameUpdate, objectlist = titleObjects, batch = titleBatch)





		



	
	app.run()

if __name__ == "__main__":
	main()
