from pyglet import *
from res import whalestuff, util, handlers, gui, enemies, arena
from itertools import combinations



def main():
	"""Main functions, entry point of the application"""


	#initialize graphics
	screen = window.Window(vsync = True, fullscreen=True)
	batch = graphics.Batch()
	background = graphics.OrderedGroup(0)
	foreground = graphics.OrderedGroup(1)
	ui = graphics.OrderedGroup(2)


	#import art
	resource.path = ['res/images']
	resource.reindex()
	Background_image = resource.image("Background/Temp_Stars.jpeg")
	Background = sprite.Sprite(Background_image, batch = batch, group = background)

	
	#init objectset
	objects = set()
	chunks = {}


	#create input handler
	handler = handlers.Handler(window = screen)


	#init player
	player = whalestuff.Player(pos = (screen.width, screen.height), size = (150, 75), speed = 1, handler = handler, batch = batch, group = foreground)
	camera = util.Camera(pos = (0,0), zoom = 1, player = player, handler=handler, window = screen)
	objects.add(player)
	objects.add(camera)



	#generate Map
	objects.update(arena.Map(k = 30,r = 1000,bounds = (screen.width*3, screen.height*3), size = 900, camera = camera, batch = batch, group = foreground).circles)


	#init GUI
	Gui = gui.GUI(pos = (0,0), player = player, window = screen, batch = batch, group = ui)
	objects.add(Gui)

	#link objects
	player.camera = camera
	handler.gamePlayHandler(player = player, camera=camera)


	#create test enemy
	for x in range(50):
		objects.add(enemies.FishingBoat(pos = (screen.width/2, screen.height/2 - 100*x), size = (50,25), speed = 1, player = player, objects = objects, handler = handler, camera = camera, batch = batch, group = foreground))


	@screen.event
	def on_draw():
		"""Where draw call is made"""
		batch.draw()



	for obj in objects:
		obj.alive = True

	#@util.timeit
	def update(dt):
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

		

		for corpse in [obj for obj in objects if not obj.alive]:
			objects.remove(corpse)
			corpse.delete()
			del corpse
		
		for obj in objects:
			obj.update(dt)



		for obj, obj2 in combinations([obj for obj in objects if isinstance(obj, (util.visibleEntity, arena.Planet))], r=2):
			if util.collision.detectCollision(recA = obj.sprite, recB = obj2.sprite) and (obj != obj2) and (type(obj) != type(obj2)):
				obj.hit(obj2, dt)
				obj2.hit(obj, dt)











		



	clock.schedule_interval(update,1/240)
	app.run()

if __name__ == "__main__":
	main()
