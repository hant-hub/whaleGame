"""misc math functions and classes that are reused often"""


from pyglet import *
import math, time



def timeit(function):


	def wrapper(*args, **kwargs):
		start = time.perf_counter()

		stuff = function(*args, **kwargs)

		end = time.perf_counter()
		print(end-start)

		return stuff


	return wrapper


def getClosestPointCircle(center, radius, point):
	"""computes the closest point on a circle to the given point


	If we have a circle with center = center and radius = radius.
	we return the point on the circumference of our circle with the 
	closest Euclidean distance to our eccentric point
	"""

	ax, ay = center
	bx, by = point
	

	cx = ax + (radius * ( (bx - ax)/math.dist((ax,ay), (bx,by))  ))
	cy = ay + (radius * ( (by - ay)/math.dist((ax,ay), (bx,by))  ))

	return (cx,cy)




class Camera:
	"""holds all camera logic"""

	def __init__(self, pos, zoom, player, handler, window):
		self.pos = pos
		self.zoom = zoom
		self.player = player
		self.target = (0,0)
		self.handler = handler
		self.window = window

	def update(self, dt):
		px, py = self.player.pos
		cx, cy = self.handler.target


		self.target = (px, py)

		tx, ty = -(px - self.window.width/2),-(py - self.window.height/2)

		dist = math.dist(self.pos, (tx,ty))

	

		x, y = self.pos

		tx -= x
		ty -= y

		x += tx * dt * (2/self.zoom)
		y += ty * dt * (2/self.zoom)

		self.pos = (x,y)



class visibleEntity:
	"""class for all objects that need to be rendered in the game world.

	This is only for objects that are affected by the camera. This does not include GUI and menu elements that
	should be directly rendered onto the screen
	"""

	def __init__(self, pos, size, sprite):
		self.pos = pos
		self.size = size
		self.camera = None
		self.sprite = sprite




	def updatevisual(self,sprite, rotation = None):
		"""updates the sprite to match the camera position"""

		x, y = self.pos
		cx, cy = self.camera.pos
		tx, ty = self.camera.target
		width, height = self.size

		sprite.x = ((x-tx) * self.camera.zoom) + cx + (tx)
		sprite.y = ((y-ty) * self.camera.zoom) + cy + (ty)


		sprite.width = width * self.camera.zoom
		sprite.height = height * self.camera.zoom

		sprite.anchor_x *= self.camera.zoom
		sprite.anchor_y *= self.camera.zoom


		if rotation != None:
			sprite.rotation = rotation

	def delete(self):
		"""deconstructor for the sprite to make sure it is no longer rendered after the death of its parent"""
		self.sprite.delete()
		del self.sprite






class collision:
	"""static class for collision functions"""




	def calculateVerticies(sprite):
		"""converts sprite/rec object into world space vertecies


		Takes in a rectangular object and pulls the position in space as well as the relavent
		dimensions and rotation. Then using that data it computes the world space (x,y) coordinates
		of each vertex. This function then returns a list of the vertecies sorted clockwise around the
		rectangle's center
		"""



		#grab relavent data
		rotation = math.radians(sprite.rotation)
		x, y = sprite.position
		anchorx, anchory = (sprite.anchor_x, sprite.anchor_y)
		width, height = (sprite.width, sprite.height)


		#get vertex coordinates in terms of the anchorpoint

		v1 = ((width-anchorx),  (height-anchory))

		v2 = ((width - anchorx), (0-anchory))

		v3 = (-anchorx, -anchory)

		v4 = (-anchorx, (height-anchory))


		verticies = [v1, v2, v3, v4]
		newVerticies = []

		for v in verticies:

			vx, vy = v


			vx, vy = vx*math.cos(rotation) - vy*math.sin(rotation), vy*math.cos(rotation) + vx*math.sin(rotation)


			vx += x
			vy += y

			newVerticies.append((vx,vy))


		return newVerticies



	def calculateAxisCircle(center, verticies):



		point = min(verticies, key=lambda x: math.dist(x,center))


		return point

	def calculateAxis(verticies, sprite, verticies2):
		"""Calculates two vectors to be used as projection axes

		Takes two surface normals of a set of verticies that are
		perpendicular. (this only works for rectangles) These are then returned in a tuple
		"""


		ur = verticies[0]
		lr = verticies[1]
		ll = verticies[2]
		ul = verticies[3]


		axis1 = tuple(map((lambda i, j: i-j),  ur, ul))
		axis2 = tuple(map((lambda i, j: i-j),  ur, lr))


		return {axis1, axis2}




	def ScalerProjection(axis, point, sprite):
		"""projects a point onto an axis and returns a scalar based on where it landed on the axis


		First the point is projected onto the axis using simple matrix multiplication. Then the
		dot product of our new projected point is taken with the axis we projected onto. Finally we
		return the scalar result of our dot product
		"""

		ax, ay = axis
		px, py = point

		#dist = math.hypot(*axis)

		#ax /= dist
		#ay /= dist

		output = (px * ax) + (py * ay)
		

		return output


	def ComputeCircleCollision(circle, rec, returnType = bool):
		point = collision.calculateAxisCircle(center = circle.position, verticies = collision.calculateVerticies(rec))

		if math.dist(point, circle.position) < (circle.radius+100):
			if returnType == bool:
				return True
			else:
				return point

		return False




	def ComputeCollision(recA, recB):
		"""compute fine grain collision with two rectangles


		This is an implementation of the seperating axis approach to
		2d collision detection. This function is only for fine grain collision detection
		as it is rather expensive in computing resources.
		"""
		if isinstance(recA, shapes.Circle) and isinstance(recB, shapes.Circle):
			return False
		elif isinstance(recA, shapes.Circle):
			return collision.ComputeCircleCollision(circle = recA, rec = recB, returnType = bool)
		elif isinstance(recB, shapes.Circle):
			return collision.ComputeCircleCollision(circle = recB, rec = recA, returnType = bool)
		
		
		axes = set()

		#rec A
		verticiesA = collision.calculateVerticies(recA)
		verticiesB = collision.calculateVerticies(recB)


		axisA = collision.calculateAxis(verticiesA, recA, verticiesB)
		axisB = collision.calculateAxis(verticiesB, recB, verticiesA)
		axes |= axisA
		axes |= axisB

		#rec B
		


		for axis in axes:
			projectionA = set()
			projectionB = set()

			for point in verticiesA:
				projection = collision.ScalerProjection(axis, point, recA)
				projectionA.add(projection)

			for point in verticiesB:
				projection = collision.ScalerProjection(axis, point, recB)
				projectionB.add(projection)

	


			if not (max(projectionA) >= min(projectionB) and max(projectionB) >= min(projectionA)):
				return False

		
		return True


	def calculateRadius(sprite):
		if isinstance(sprite, shapes.Circle):
			return sprite.radius

		else:
			return (math.hypot(sprite.width, sprite.height))



	def detectCollision(recA, recB):
		"""General function for collision detection between two rectangles


		This includes the coarse grain collision detection and will use the fine grain
		collision detection when nessecary.

		This is the only collision function that should be used outside of this class.
		"""




		radiusA = collision.calculateRadius(recA)
		radiusB = collision.calculateRadius(recB)

		ax, ay = recA.position
		bx, by = recB.position


		dist = math.dist([ax,ay], [bx,by])

		if dist < (radiusA + radiusB):
			return collision.ComputeCollision(recA, recB)
		
		else:
			return False









