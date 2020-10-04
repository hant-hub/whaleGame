from pyglet import *
from res import whalestuff, util, handlers, gui, enemies



def main():
	"""Main functions, entry point of the application"""


	#initialize graphics
	screen = window.Window(vsync = True, fullscreen=True)
	batch = graphics.Batch()
	background = shapes.Rectangle(x=0, y=0, width=screen.width, height=screen.height, color = (255,0,255), batch=batch)

	#init objectlist
	objects = []


	#create input handler
	handler = handlers.Handler(window = screen)


	#init player
	player = whalestuff.Player(pos = (screen.width, screen.height), size = (150, 75), speed = 1, handler = handler, batch = batch)
	camera = util.Camera(pos = (0,0), zoom = 0, player = player, window = screen)
	objects.append(player)
	objects.append(camera)

	#init GUI
	Gui = gui.GUI(pos = (0,0), player = player, window = screen, batch = batch)
	objects.append(Gui)

	#link objects
	player.camera = camera
	handler.gamePlayHandler(player = player)


	#create test enemy
	for x in range(100):
		objects.append(enemies.FishingBoat(pos = (screen.width/2, screen.height/2 - 100*x), size = (50,25), speed = 1, player = player, objects = objects, handler = handler, camera = camera, batch = batch))


	@screen.event
	def on_draw():
		"""Where draw call is made"""

		screen.clear()
		batch.draw()

	for obj in objects:
		obj.alive = True


	def update(dt):
		"""Updates all objects every frame"""
		
		cx, cy = camera.pos

		background.x = cx
		background.y = cy


		if len([obj for obj in objects if isinstance(obj, enemies.Enemy) ]) > 60:
			sacrifice = objects.pop()
			sacrifice.delete()
			del sacrifice


		for corpse in [obj for obj in objects if not obj.alive]:
			objects.remove(corpse)
			corpse.delete()
			del corpse

		for obj in objects:
			obj.update(dt)

		for obj in [obj for obj in objects if isinstance(obj, util.visibleEntity)]:
			for obj2 in [obj for obj in objects if isinstance(obj, util.visibleEntity)]:
				if util.collision.detectCollision(recA = obj.sprite, recB = obj2.sprite) and (obj != obj2):
					obj.hit(obj2)
					obj2.hit(obj)




		



	clock.schedule_interval(update,1/120)
	app.run()

if __name__ == "__main__":
	main()