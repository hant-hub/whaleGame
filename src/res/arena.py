import numpy as np
from pyglet import *
import math
from random import choice, random





class Planet:

	def __init__(self, pos, radius, camera, image, batch, group):
		self.pos = pos
		self.radius = radius
		self.camera = camera
		
		self.sprite = sprite.Sprite(image, *pos, batch = batch, group = group)

		self.sprite.scale = radius
		self.dist = 1



	def update(self, dt):
		"""updates the sprite to match the camera position"""
		x, y = self.pos


		cx, cy = self.camera.pos
		tx, ty = self.camera.target

		self.sprite.x = ((x-tx) * self.camera.zoom) + (cx * self.dist)+ (tx)
		self.sprite.y = ((y-ty) * self.camera.zoom) + (cy * self.dist)+ (ty)


		self.sprite.scale = self.camera.zoom * self.radius


	def hit(self, obj, dt):
		pass

	def delete(self):
		self.sprite.delete()


	def direction(self,obj):
		#relative to obj1

		x1,y1 = self.pos
		x2,y2 = obj.pos

		x2 -= x1
		y2 -= y1

		#divide rise and run by the total distance to get dir on unit circle. ie: unit length step towards obj2

		dist = math.dist(self.pos, obj.pos)

		x2 /= dist
		y2 /= dist


		return (x2,y2)


	def find_repulsion_vector(self, planet):
		
		#calculate magnitude of gravitational force
		M = 50
		m = 500

		dist = math.dist(self.pos,planet.pos) - (self.radius+50)

		r =  dist*dist

		magnitude = (M*m)/math.sqrt(r*(r+0.15))

		vector = self.direction(planet)

		vector_force = (magnitude*vector[0]*10, magnitude*vector[1]*10)

		return vector_force











class Map:


	def __init__(self,k,r, size, bounds, camera, images, batch, group):
		self.k = k
		self.r=r
		self.width, self.height = bounds
		self.batch = batch
		self.group = group
		self.images = images

		self.centers = self.Poission(k,r)
		self.circles = set()
		self.size = size
		self.camera = camera

		self.make_circles()



	def make_circles(self):
		for point in self.centers:
			radius = np.random.uniform(self.size/10, self.size-500)
			self.circles.add(Planet(pos = point, radius = radius/256, camera = self.camera, image = choice(self.images), batch = self.batch, group = self.group))




	def get_cell_coords(self, pt):
	    """Get the coordinates of the cell that pt = (x,y) falls in."""

	    return int(pt[0] // self.a), int(pt[1] // self.a)

	def get_neighbours(self, coords):
	    """Return the indexes of points in cells neighbouring cell at coords.

	    For the cell at coords = (x,y), return the indexes of points in the cells
	    with neighbouring coordinates illustrated below: ie those cells that could 
	    contain points closer than r.

	                                     ooo
	                                    ooooo
	                                    ooXoo
	                                    ooooo
	                                     ooo

	    """

	    dxdy = [(-1,-2),(0,-2),(1,-2),(-2,-1),(-1,-1),(0,-1),(1,-1),(2,-1),
	            (-2,0),(-1,0),(1,0),(2,0),(-2,1),(-1,1),(0,1),(1,1),(2,1),
	            (-1,2),(0,2),(1,2),(0,0)]
	    neighbours = []
	    for dx, dy in dxdy:
	        neighbour_coords = coords[0] + dx, coords[1] + dy
	        if not (0 <= neighbour_coords[0] < self.nx and
	                0 <= neighbour_coords[1] < self.ny):
	            # We're off the grid: no neighbours here.
	            continue
	        neighbour_cell = self.cells[neighbour_coords]
	        if neighbour_cell is not None:
	            # This cell is occupied: store this index of the contained point.
	            neighbours.append(neighbour_cell)
	    return neighbours




	def point_valid(self, pt, samples):
	    """Is pt a valid point to emit as a sample?

	    It must be no closer than r from any other point: check the cells in its
	    immediate neighbourhood.

	    """

	    cell_coords = self.get_cell_coords(pt)
	    for idx in self.get_neighbours(cell_coords):
	        nearby_pt = samples[idx]
	        # Squared distance between or candidate point, pt, and this nearby_pt.
	        distance2 = (nearby_pt[0]-pt[0])**2 + (nearby_pt[1]-pt[1])**2
	        if distance2 < (self.r)**2:
	            # The points are too close, so pt is not a candidate.
	            return False
	    # All points tested: if we're here, pt is valid
	    return True


	def get_point(self, k, refpt, samples):
	    """Try to find a candidate point relative to refpt to emit in the sample.

	    We draw up to k points from the annulus of inner radius r, outer radius 2r
	    around the reference point, refpt. If none of them are suitable (because
	    they're too close to existing points in the sample), return False.
	    Otherwise, return the pt.

	    """
	    i = 0
	    while i < k:
	        rho, theta = np.random.uniform(self.r, 2*self.r), np.random.uniform(0, 2*np.pi)
	        pt = refpt[0] + rho*np.cos(theta), refpt[1] + rho*np.sin(theta)
	        if not (0 <= pt[0] < self.width and 0 <= pt[1] < self.height):
	            # This point falls outside the domain, so try again.
	            continue
	        if self.point_valid(pt, samples):
	            return pt
	        i += 1
	    # We failed to find a suitable point in the vicinity of refpt.
	    return False



	def Poission(self, k, r):

		# Cell side length
		self.a = self.r/np.sqrt(2)
		# Number of cells in the x- and y-directions of the grid
		self.nx, self.ny = int(self.width / self.a) + 1, int(self.height / self.a) + 1

		# A list of coordinates in the grid of cells
		coords_list = [(ix, iy) for ix in range(self.nx) for iy in range(self.ny)]
		# Initilalize the dictionary of cells: each key is a cell's coordinates, the
		# corresponding value is the index of that cell's point's coordinates in the
		# samples list (or None if the cell is empty).
		self.cells = {coords: None for coords in coords_list}

		# Pick a random point to start with.
		pt = (np.random.uniform(0, self.width), np.random.uniform(0, self.height))
		samples = [pt]
		# Our first sample is indexed at 0 in the samples list...
		self.cells[self.get_cell_coords(pt)] = 0
		# ... and it is active, in the sense that we're going to look for more points
		# in its neighbourhood.
		active = [0]

		nsamples = 1
		# As long as there are points in the active list, keep trying to find samples.


		while active:
		    # choose a random "reference" point from the active list.
		    idx = np.random.choice(active)
		    refpt = samples[idx]
		    # Try to pick a new point relative to the reference point.
		    pt = self.get_point(self.k, refpt, samples)
		    if pt:
		        # Point pt is valid: add it to the samples list and mark it as active
		        samples.append(pt)
		        nsamples += 1
		        active.append(len(samples)-1)
		        self.cells[self.get_cell_coords(pt)] = len(samples) - 1
		    else:
		        # We had to give up looking for valid points near refpt, so remove it
		        # from the list of "active" points.
		        active.remove(idx)

		return samples






