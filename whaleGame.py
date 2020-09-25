from pyglet import *


screen = window.Window(vsync = True)
batch = graphics.Batch()
objects = []


@screen.event
def on_draw():
	screen.clear()
	#batch.draw()


#def update(dt):
#	for obj in objects:
#		obj.update(dt)


#clock.schedule_interval(update,1/60)
app.run()