from pyglet import *
from res import whalestuff, util, handlers, gui


#initialize graphics
screen = window.Window(vsync = True, fullscreen=True)
batch = graphics.Batch()
background = shapes.Rectangle(x=0, y=0, width=screen.width, height=screen.height, color = (255,0,255), batch=batch)

#init objectlist
objects = []


#create input handler
handler = handlers.Handler(window = screen)


#init player
player = whalestuff.Player(pos = (screen.width/2, screen.height/2), size = (100, 50), speed = 1, handler = handler, batch = batch)
camera = util.Camera(pos = (0,0), zoom = 0, player = player, window = screen)
objects.append(player)
objects.append(camera)

#init GUI
Gui = gui.GUI(pos = (0,0), player = player, window = screen, batch = batch)
objects.append(Gui)

#link objects
player.camera = camera
handler.gamePlayHandler(player = player)





@screen.event
def on_draw():
	screen.clear()
	batch.draw()


def update(dt):

	
	cx, cy = camera.pos

	background.x = cx
	background.y = cy

	for obj in objects:
		obj.update(dt)


	if util.collision.detectCollision(recA = player.rec, recB = background):

		player.rec.color = (255,0,0)

	else:

		player.rec.color = (255,255,255)




clock.schedule_interval(update,1/60)
app.run()