from pyglet import *
import math




def getClosestPointCircle(center, radius, point):

	ax, ay = center
	bx, by = point
	

	cx = ax + (radius * ( (bx - ax)/math.dist((ax,ay), (bx,by))  ))
	cy = ay + (radius * ( (by - ay)/math.dist((ax,ay), (bx,by))  ))

	return (cx,cy)




class Camera:

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

	def __init__(self, pos, size, sprite):
		self.pos = pos
		self.size = size
		self.camera = None
		self.sprite = sprite




	def updatevisual(self,sprite, rotation = None):

		x, y = self.pos
		cx, cy = self.camera.pos

		sprite.x = x + cx
		sprite.y = y + cy

		if rotation != None:
			sprite.rotation = rotation

	def delete(self):
		self.sprite.delete()
		del self.sprite






class collision:

	def calculateVerticies(sprite):

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
		ur = verticies[0]
		lr = verticies[1]
		ll = verticies[2]
		ul = verticies[3]


		axis1 = tuple(map((lambda i, j: i-j),  ur, ul))
		axis2 = tuple(map((lambda i, j: i-j),  ur, lr))


		return (axis1, axis2)


	def ScalerProjection(axis, point):

		ax, ay = axis
		px, py = point

		numerator = (px * ax) + (py * ay)
		denominator = (ax*ax) + (ay*ay)

		projectionx = (numerator/denominator) * ax
		projectiony = (numerator/denominator) * ay


		output = (projectionx * ax) + (projectiony * ay)

		return output


	def ComputeCollision(recA, recB):
		
		
		axes = []

		#rec A
		verticiesA = collision.calculateVerticies(recA)
		axis1, axis2 = collision.calculateAxis(verticiesA)
		axes.append(axis1)
		axes.append(axis2)

		#rec B
		verticiesB = collision.calculateVerticies(recB)
		axis1b, axis2b = collision.calculateAxis(verticiesB)
		axes.append(axis1b)
		axes.append(axis2b)


		for axis in axes:
			projectionA = []
			projectionB = []

			for point in verticiesA:
				projection = collision.ScalerProjection(axis, point)
				projectionA.append(projection)

			for point in verticiesB:
				projection = collision.ScalerProjection(axis, point)
				projectionB.append(projection)

	


			if not (max(projectionA) >= min(projectionB) and max(projectionB) >= min(projectionA)):
				return False

		
		return True


	def detectCollision(recA, recB):

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










