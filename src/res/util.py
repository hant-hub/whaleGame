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

	def __init__(self, pos, zoom, player, window):
		self.pos = pos
		self.zoom = zoom
		self.player = player
		self.window = window

	def update(self, dt):
		px, py = self.player.pos

		tx, ty = -(px - self.window.width/2),-(py - self.window.height/2)
		x, y = self.pos

		tx -= x
		ty -= y

		x += tx * dt
		y += ty * dt

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

		sprite.x = x + cx
		sprite.y = y + cy

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


			vx = vx*math.cos(rotation) - vy*math.sin(rotation)
			vy = vy*math.cos(rotation) + vx*math.sin(rotation)

			vx += x
			vy += y

			newVerticies.append((vx,vy))


		return newVerticies



	def calculateAxis(verticies):
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


		return (axis1, axis2)


	def ScalerProjection(axis, point):
		"""projects a point onto an axis and returns a scalar based on where it landed on the axis


		First the point is projected onto the axis using simple matrix multiplication. Then the
		dot product of our new projected point is taken with the axis we projected onto. Finally we
		return the scalar result of our dot product
		"""

		ax, ay = axis
		px, py = point

		numerator = (px * ax) + (py * ay)
		denominator = (ax*ax) + (ay*ay)

		projectionx = (numerator/denominator) * ax
		projectiony = (numerator/denominator) * ay


		output = (projectionx * ax) + (projectiony * ay)

		return output


	def ComputeCollision(recA, recB):
		"""compute fine grain collision with two rectangles


		This is an implementation of the seperating axis approach to
		2d collision detection. This function is only for fine grain collision detection
		as it is rather expensive in computing resources.
		"""
		
		
		axes = set()

		#rec A
		verticiesA = collision.calculateVerticies(recA)
		axis1, axis2 = collision.calculateAxis(verticiesA)
		axes.add(axis1)
		axes.add(axis2)

		#rec B
		verticiesB = collision.calculateVerticies(recB)
		axis1b, axis2b = collision.calculateAxis(verticiesB)
		axes.add(axis1b)
		axes.add(axis2b)


		for axis in axes:
			projectionA = set()
			projectionB = set()

			for point in verticiesA:
				projection = collision.ScalerProjection(axis, point)
				projectionA.add(projection)

			for point in verticiesB:
				projection = collision.ScalerProjection(axis, point)
				projectionB.add(projection)

	


			if not (max(projectionA) >= min(projectionB) and max(projectionB) >= min(projectionA)):
				return False

		
		return True


	def detectCollision(recA, recB):
		"""General function for collision detection between two rectangles


		This includes the coarse grain collision detection and will use the fine grain
		collision detection when nessecary.

		This is the only collision function that should be used outside of this class.
		"""

		widthA, heightA = (recA.width, recA.height)
		widthB, heightB = (recB.width, recB.height)

		radiusA = math.hypot(widthA, heightA)
		radiusB = math.hypot(widthB, heightB)

		ax, ay = recA.position
		bx, by = recB.position


		dist = math.dist([ax,ay], [bx,by])

		if dist < (radiusA + radiusB):
			return collision.ComputeCollision(recA, recB)
		
		else:
			return False












class spatialHash:

	def __init__(self, cell_size):
		self.cell_size = cell_size
		self.contents = {}


	def hash(self, point):
		x, y = point

		return int(x/self.cell_size), int(y/self.cell_size)

	def insert_object_for_point(self, point, object):
		self.contents.setdefault( self._hash(point), [] ).append( object )

	def insert_object_for_box(self, box, obj):
		# hash the minimum and maximum points
		a = tuple(map(max, izip(*box))) 
		b = tuple(map(min, izip(*box))) 
		# iterate over the rectangular region
		for i in range(a[0], b[0]+1):
			for j in range(a[1], b[1]+1):
				# append to each intersecting cell
				self.contents.setdefault( (i, j), [] ).append( obj )


	def insert_rect(obj):
		verticies = collision.calculateVerticies(obj.sprite)
		self.insert_object_for_box(verticies, obj)

