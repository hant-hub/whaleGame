from pyglet import *
from res import whalestuff, util


#initialize graphics
screen = window.Window(vsync = True, fullscreen=True)
batch = graphics.Batch()
background = shapes.Rectangle(x=0, y=0, width=screen.width, height=screen.height, color = (255,0,255), batch=batch)

#init objectlist
objects = []


#init mouse
mouse = [0,0]

#init player
player = whalestuff.Player(pos = (screen.width/2, screen.height/2), size = (100, 50), speed = 1, mouse = mouse, batch = batch)
camera = util.Camera(pos = (0,0), zoom = 0, player = player, window = screen)
objects.append(player)
objects.append(camera)

player.camera = camera





@screen.event
def on_mouse_motion(x,y,dx,dy):

	mouse[0] += dx
	mouse[1] += dy

#screen.push_handlers(on_mouse_motion)


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


clock.schedule_interval(update,1/60)
app.run()