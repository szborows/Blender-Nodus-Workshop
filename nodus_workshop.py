#!BPY
"""
Name: 'Nodus workshop'
Blender: 249
Group: 'Add'
Tooltip: 'Nodus workshop for creating nodus from circle'
"""
__author__ = "Slawomir Zborowski"
__url__ = ["stilz.vot.pl/", "www.blender.org", "www.python.org"]
__bpydoc__ = ""

import bpy
import Blender
from Blender import *
from Blender.Draw import *
from Blender import Window
from Blender.BGL import *
import math
from math import sin, cos, asin, sqrt

class GLOBALES:
	pass

glb = GLOBALES()
glb.NUM_VERTICES = Create(1)
glb.ANGLE = Create(1)
glb.CREATE = Create(1)

circle = []
a = 0

def grad2rad (angle):
	rad = angle * math.pi/180.0
	return rad

def rad2grad (angle):
	grad = angle/math.pi * 180.0
	return grad

def cbrt (x):
	return (abs(x)) ** (1/3.0)  

def make_circle (origin, circle_vertices = [], num_vertices = 32):
	"""
	This function creates a circle in 3D space.
	"""
	a = 0.0
	for i in range( 0, num_vertices ):
		a = a + 2*math.pi/num_vertices
		circle_vertices.append ( 
			[origin[0]+sin(a), 
			 origin[1]+cos(a), 
			 origin[2]] 
		)

def rot_circle (circle_vertices, angles = [], origin = []):
	"""
	This function rotates a circle.
	"""
	for i in range (0, len(circle_vertices)):
		v = circle_vertices[i]
		for j in range (0, 3):
			v[j] -= origin[j]

		# Probably it could be done better (in more pythonic way)
		u = [v[0], v[1]*cos( angles[0] )-v[2]*sin(angles[0]), v[1]*sin(angles[0])+v[2]*cos(angles[0])]
		w = [u[0]*cos(angles[1])+u[2]*sin(angles[1]), u[1], -u[0]*sin(angles[1])+u[2]*cos(angles[1])]
		u = [w[0]*cos(angles[2])-w[1]*sin(angles[2]), w[0]*sin(angles[2])+w[1]*cos(angles[2]), w[2]]

		for j in range( 0, 3 ):
			u[j] += origin[j]
		circle_vertices[i] = u

def angle_between_plane_and_line (n=[], l=[]):
	"""
	This function computes angle between a plane and a line.
	"""
	return asin (abs(n[0]*l[0]+n[1]*l[1]+n[2]*l[2])/(sqrt(n[0]*n[0]+n[1]*n[1]+n[2]*n[2])*sqrt(l[0]*l[0]+l[1]*l[1]+l[2]*l[2])))

def calc_base_transformation (circle_vertices=[]):
	"""
	This function calculates base trfansformation that is to be 
	applied to certain circle.
	"""
	a = circle_vertices[0].co
	b = circle_vertices[len(circle_vertices)/2].co
	c = circle_vertices[len(circle_vertices)/3].co

	ab = [b[0]-a[0], b[1]-a[1], b[2]-a[2]]
	ac = [c[0]-a[0], c[1]-a[1], c[2]-a[2]]
	n = [ab[1]*ac[2]-ac[1]*ab[2], -(ab[0]*ac[2]-ac[0]*ab[2]), ab[0]*ac[1]-ac[0]*ab[1]]

	d = -n[0]*a[0] + -n[1]*a[1] + -n[2]*a[2]

	#print "Equation: %fx + %fy + %fz + %f = 0." % (n[0], n[1], n[2], d)
	#print "Angles X: %f, Y: %f, Z: %f" % (rad2grad(angle_between_plane_and_line(n, [1.0, 0.0, 0.0])), rad2grad(angle_between_plane_and_line(n, [0.0, 1.0, 0.0])), rad2grad(angle_between_plane_and_line(n, [ 0.0, 0.0, 1.0])))

	return [angle_between_plane_and_line(n, [1.0, 0.0, 0.0] ), angle_between_plane_and_line(n, [0.0, 1.0, 0.0]), angle_between_plane_and_line(n, [0.0, 0.0, 1.0])]

def create_pipe():
	"""
	Creates a nodus
	"""

	edit_mode = Window.EditMode()
	if edit_mode: Window.EditMode(0)

	active_scene = bpy.data.scenes.active
	active_obj = active_scene.objects.active
	me = active_obj.getData( mesh = 1 )
	mev = me.verts
	vindex_offset = len(mev)
	selvn = 0
	selv = []
	for i in mev:
		if i.sel:
			selvn += 1
			selv.append(i)

	#print "There was %d selected verts in mesh: \n" % selvn
	#for i in selv:
	#	print '%d, ' % i.index

	curr_vertices = []
	tmp_vertex = []
	num_verts = selvn

	center = [0.0, 0.0, 0.0]
	for v in selv:
		center[0] = center[0] + v.co.x
		center[1] = center[1] + v.co.y
		center[2] = center[2] + v.co.z
	center[0] /= selvn
	center[1] /= selvn
	center[2] /= selvn

	base_transformation = calc_base_transformation( selv )
	faces = []
	vxt = []
	vx = []
	vx = center
	a = base_transformation[0]
	max_angle = base_transformation[0] + grad2rad(90)
	num_segments = 6

	for i in range( 0, num_segments ):
		a = a + max_angle/num_segments
		vx = [center[0], center[1]+1.5*cos(a)-1.5, center[2]+1.5*sin(a)]
		cv = []
		ce = []
		make_circle (vx, cv, num_verts)
		rot_circle (cv, base_transformation, vx)
		rot_circle (cv, [a, 0, 0], vx)
		for x in cv:
			vxt.append (x)
		if i > 0:
			for j in range (0, num_verts-1 ):
				faces.append ([vindex_offset+(i-1)*num_verts+1+j, vindex_offset+(i-1)*num_verts+j, vindex_offset+i*num_verts+j, vindex_offset+i*num_verts+1+j])
			faces.append([vindex_offset+(i-1)*num_verts+num_verts-1, vindex_offset+(i-1)*num_verts, vindex_offset+i*num_verts, vindex_offset+i*num_verts+num_verts-1])
	 
	me.verts.extend( vxt )
	
	# Compute offset
	v1 = vxt[0]
	v2 = []
	min_dist = 99990.0
	min_index = len(mev)-num_verts
	for i in range( vindex_offset-num_verts, vindex_offset ):
		v2 = mev[i].co
		d = sqrt( (v2[0]-v1[0])**2 + (v2[1]-v1[1])**2 + (v2[2]-v1[2])**2 )
		if d < min_dist :
			min_dist = d
			min_index = i

	#print "Min offset: %f with offset %d"%(min_dist, min_index%num_verts)
	offset = min_index % num_verts

	for j in range (0, num_verts-offset-1):
		faces.append ([min_index+j+1, min_index+j, vindex_offset+j, vindex_offset+1+j])
	faces.append ([min_index+num_verts-offset, vindex_offset+num_verts-1, vindex_offset-num_verts+offset-1, vindex_offset-num_verts+offset])

	for j in range (1, offset):
		faces.append ([vindex_offset+num_verts-1-j, vindex_offset+num_verts-j, min_index-j, min_index-j-1])
	faces.append ([vindex_offset-num_verts, vindex_offset-1, vindex_offset+num_verts-offset-1, vindex_offset+num_verts-offset])

	me.faces.extend (faces)

	if edit_mode:
		Window.EditMode(1)
	Blender.Window.RedrawAll()

def clear_window():
	glColor3f (0.853, 0.853, 0.853)
	glClear (GL_COLOR_BUFFER_BIT)

def display_menu():
	clear_window()
	glRasterPos2i (15, 15)
	Text ('Nodus Workshop')
	glRasterPos2i( 15, 28 )
	Text( '__________________________ _ _ _ _ _ _ _ _ _' )
	glb.CREATE = PushButton ('Create', 1, 15, 30, 60, 20, 'Create nodus')

def event( evt, val ):
	if( evt == ESCKEY and not val ):
		Exit()

def b_evt( evt ):
	if evt == 1: create_pipe()
	elif evt == 6: Exit()

def main():
	Register (display_menu, event, b_evt)

if __name__ == "__main__":
	main()
