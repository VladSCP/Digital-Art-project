"""
third official prototype of the project
new features: 
- colours are no longer randomly generated, now there are patterns
the previous way to store colours is still here, but is now called "free draw"
- function that generates random colours has been updated to include every colour possible
- a new combobox to select colour patterns
- the shapes now have outlines and the size of them and the colour can be changed in the settings
- increased the dots limit from 7 to 12
- no longer removes dots when shape changes
- every shape on every tessellation mode now stores its own dots
- the fill tool now has an option for right mouse button
- function that add dots has been updated: now insert a dot beetween the dots that have 
the biggest distance between them, if two such distances are equal, it will insert it
on the one that is closest to the starting corner of the edge

Also, the menu has been redesigned again
and the cursors as well
"""

from tkinter import *
from tkinter import colorchooser,filedialog,messagebox,Spinbox
from tkinter import ttk
from tkinter.ttk import Scale
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon as Make_Polygon
import random
import numpy as np
import math

def SIN(x): return np.around(np.sin(math.radians(x)), decimals=6) # accurate sinus(x) function
def COS(x): return np.around(np.cos(math.radians(x)), decimals=6) # accurate cosinus(x) function
def _dist_between(A,B): return np.around(math.sqrt( (A[0]-B[0])*(A[0]-B[0]) + (A[1]-B[1])*(A[1]-B[1]) ), decimals=2)

def _rotate(x,y,  Ox,Oy,  angl): # this function rotates the point (x,y) around (Ox,Oy) by <angl> degrees
    if angl not in [0,360]: return [((x-Ox)*COS(angl)-(y-Oy)*SIN(angl))+Ox, ((x-Ox)*SIN(angl)+(y-Oy)*COS(angl))+Oy]
    else: return [x,y]
def _scale_dot(x,y,  Ox,Oy,  sf): # this function scales the point (x,y) relative to (Ox,Oy) by scale factor <sf>
    if sf not in [0.00,1.00]: return [((x-Ox)*sf)+Ox, ((y-Oy)*sf)+Oy]
    else: return [x,y]
def _polygon_is_simple(P): # this function checks the given shape is a valid (simple) polygon
    the_polygon = []
    for i in range(0,len(P),+2):
        the_polygon.append( (P[i], P[i+1]) )
    Polygon_test = Make_Polygon(the_polygon)
    return Polygon_test.is_valid                    
    


##### global variables ###########

root = Tk()
root.title("Cheesellation")
root.geometry("1280x800")
root.resizable(0,0)

w = 1260
h = 650

mouse_x = 0
mouse_y = 0

offset = [w/2,h/2]
size = 150
zoom = 100
dot_size = 4.5
outline_size = 0

curr_tool = "move"                      # the current tool
shape_orientation = 'still squares'     # the current shape orientation
main_shape = "square"                   # the current shape, there are 5 shapes: [triangle,square,diamond,H_hexagon,V_hexagon]
curr_colour_pattern = "snowflakes"      # the current colour pattern used to pick the colours for the shapes
selected_colour_L = "#e6e6e6"           # the current colour picked for the left click
selected_colour_R = "#737373"           # the current colour picked for the right click
outline_colour = "#FFFFFF"              # the current colour of the outlines

dots_visible = True
tiles_visible = False
tiles_ids = []                          # stores the ids of the tiles
tiles_colours = {}                      # stores the colours of the tiles (it mostly depends on tiles_id)
tiles_proprieties = {}                  # stores the proprieties of the tiles ( offset position, row and column values )
                                        #     note: this does not include the main shape due to some glitches
dots_data = {}                          # stores the id of the dots for each Tessellation mode
dots_order = []                         # the order of the dots from the main shape around (0,0) offset, 
                                        #     to make it easy for a tile to be drawn by simply changing its offset
aux_triangle = []                       # the order of the dots from the auxiliary triangle around (0,0) offset
                                        #     same as dot_order, but applies only to triangles, for other shapes is empty

canvas = Canvas(root, width=w, heigh=h, bg="white") # the main canvas
canvas.place(x=10, y=10)

tool_canvas = Canvas(root, width=1260, heigh=48, bg='black') # the canvas for buttons
tool_canvas.place(x=10, y=665)

polygon_pieces = []                     # a list containing the ids of the dots on each editable edge of the main polygon
pieces_limits = []                      # a list containing the limits where the dots of the main polygon can be moved
corners = []                            # a list containing the main corners of the main polygon
Polygon = canvas.create_polygon([0,0,0,0],fill=selected_colour_L,width=outline_size, outline=outline_colour) # initilisation of the main polygon
canvas.tag_bind(Polygon,'<Button-1>', lambda f: colour_polygon(Polygon, "left"))
canvas.tag_bind(Polygon,'<Button-3>', lambda f: colour_polygon(Polygon, "right"))




######### methods ###########

# updates/initilises the limits where the dots can be moved
def _update_limits():
    global pieces_limits
    _init_corners()
    _reset_limit_list()
    
    corners_order = []
    if   main_shape == 'triangle':                corners_order = [[0,2,1]]
    elif main_shape in ['square','diamond']:      corners_order = [[0,3,2,1],[2,3,0,1]]
    elif main_shape in ['H_hexagon','V_hexagon']: corners_order = [[0,5,4,3,2,1],[2,1,0,5,4,3],[5,0,1,2,3,4]]
    
    piece_id = 0
    for l in corners_order:
        for j in l: pieces_limits[piece_id].append((corners[j][0], corners[j][1]))
        A = [ corners[l[0]][0], corners[l[0]][1] ]
        B = [ corners[l[len(l)-1]][0], corners[l[len(l)-1]][1] ]
        for i in l[1:len(l)-1]:
            C = _rotate(corners[i][0],corners[i][1],  int((A[0]+B[0])/2),int((A[1]+B[1])/2),  180)
            pieces_limits[piece_id].append((C[0],C[1]))
        piece_id += 1

# initilises the main corners (that are not drawn by the dots)
def _init_corners():
    global corners
    corners.clear()
    angles_order = []
    
    if   main_shape == 'triangle':  angles_order = [270, 30, 150]
    elif main_shape == 'square':    angles_order = [225, 315, 45, 135]
    elif main_shape == 'diamond':   angles_order = [270, 0, 90, 180]
    elif main_shape == 'H_hexagon': angles_order = [0, 60, 120, 180, 240, 300, 360]
    elif main_shape == 'V_hexagon': angles_order = [30, 90, 150, 210, 270, 330, 390]
    
    for j in angles_order:
        corn = _rotate(size,0, 0,0, j)
        corners.append([corn[0]+offset[0],corn[1]+offset[1]])

# initilises the dots_data dictinory
def _init_dots_data():
    global dots_data
    dots_data.update( {'triangles' : [[]]} )
    dots_data.update( {'still squares' : [[],[]]} )
    dots_data.update( {'rotated squares' : [[],[]]} )
    dots_data.update( {'still diamonds' : [[],[]]} )
    dots_data.update( {'rotated diamonds' : [[],[]]} )
    dots_data.update( {'still hexagons H' : [[],[],[]]} )
    dots_data.update( {'rotated hexagons H' : [[],[],[]]} )
    dots_data.update( {'still hexagons V' : [[],[],[]]} )
    dots_data.update( {'rotated hexagons V' : [[],[],[]]} )

# main function for dots clicking
def _circle_pressed(circle, piece_id):
    if curr_tool == "move": 
        _move(circle, piece_id)

# selects the tool and also changes the cursor if applicable
def _select_tool(new_tool):
    global curr_tool
    curr_tool = new_tool
    root.config(cursor=("@{}.cur").format(new_tool))

# check if the moved dot is in its limits
def _check_dot_limit(X, piece_id):
    dot = Point(X[0],X[1])
    pol = Make_Polygon(pieces_limits[piece_id])
    return pol.contains(dot)

# moves the clicked dot to the mouse, if its new position is valid
def _move(circle, piece_id):
    curr_pos = canvas.coords(circle)
    new_pos = [mouse_x - curr_pos[0] - dot_size, mouse_y - curr_pos[1] - dot_size]
    if not _check_dot_limit([mouse_x,mouse_y], piece_id): new_pos = [0,0]
    if new_pos != [0,0]:
        canvas.move(circle, new_pos[0], new_pos[1])
        _update_polygon()
        if not _polygon_is_simple(dots_order):
            canvas.move(circle, -new_pos[0], -new_pos[1])
            _update_polygon()
        if main_shape == "triangle":
            if not _polygon_is_simple(aux_triangle):
                canvas.move(circle, -new_pos[0], -new_pos[1])
                _update_polygon() 

# erase the last dot inserted in each polygon piece
def _erase_circle():
    global dots_data, polygon_pieces
    if dots_visible:
        dot_count = len(polygon_pieces[0])
        if dot_count > 0:
            for j in range(len(polygon_pieces)):
                canvas.delete(polygon_pieces[j][-1])
                del polygon_pieces[j][-1]
            dots_data.update( {shape_orientation : polygon_pieces} )
            _update_polygon()
        else:
            messagebox.showinfo('Error',"There are no dots to erase")
    else:
        messagebox.showinfo('Note',"Can't erase dots while they are hidden")

# adds a new dot in each piece
def _add_circle():
    if dots_visible:
        dot_count = len(polygon_pieces[0])
        if dot_count < 12:
            corn = [] # ids of the corners where the editable edges start from
            if   main_shape == "triangle":                corn = [0]
            elif main_shape in ["square","diamond"]:      corn = [0,1]
            elif main_shape in ["H_hexagon","V_hexagon"]: corn = [0,2,4]
             
            for j in range(len(polygon_pieces)):
                dots = [corners[corn[j]]]
                for dot in polygon_pieces[j]:
                    dot_coords = canvas.coords(dot)
                    dots += [[dot_coords[0]+dot_size, dot_coords[1]+dot_size]]
                dots += [corners[corn[j]+1]]
              
                max_dist = 0
                index = 0
                for i in range(len(dots)-1):
                    curr_dist = _dist_between(dots[i],dots[i+1])
                    if curr_dist > max_dist:
                        max_dist = curr_dist
                        index = i
                
                _dot((dots[index][0]+dots[index+1][0])/2, (dots[index][1]+dots[index+1][1])/2, index, j)
            _update_polygon()
        else:
            messagebox.showinfo('Error',"You can't have more than 12 dots on each edge")
    else:
        messagebox.showinfo('Note',"Can't add dots while they are hidden")

# erase all dots
def _erase_all_circles():
    if dots_visible:
        dot_count = len(polygon_pieces[0])
        if dot_count > 0:
            for _i in range(dot_count):
                _erase_circle()
        else:
            messagebox.showinfo('Error',"There are no dots to erase")
    else:
        messagebox.showinfo('Note',"Can't erase dots while they are hidden")

# toggles the visibility of the dots
def _toggle_vis_circles():
    global dots_visible
    dots_visible = not dots_visible
    for i in range(len(polygon_pieces)):
        for id in polygon_pieces[i]:
            if dots_visible:    canvas.itemconfigure(id, state='normal')
            else:               canvas.itemconfigure(id, state='hidden') 

# create a new dot
def _dot(X,Y,index,piece_id):
    global dots_data, polygon_pieces
    id = canvas.create_oval(X-dot_size, Y-dot_size, X+dot_size, Y+dot_size, fill="#febfff")
    canvas.tag_bind(id,'<B1-Motion>', lambda f: _circle_pressed(id,piece_id))
    canvas.tag_bind(id,'<Button-1>',  lambda f: _circle_pressed(id,piece_id))
    polygon_pieces[piece_id].insert(index, id)
    dots_data.update( {shape_orientation : polygon_pieces} )

# random hex colour generator
def _random_colour():
    colour = '#'
    hex_decimals = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    for _i in range(6): colour += hex_decimals[random.randint(0,15)]
    return colour

# update dots_data for the current Tessellation mode
def _update_dots_data():
    global dots_data, polygon_pieces
    for i in range(len(polygon_pieces)):
        for id in polygon_pieces[i]:
            canvas.itemconfigure(id, state='hidden')
            
    if main_shape not in ['V_hexagon','H_hexagon']: polygon_pieces = dots_data[shape_orientation]
    elif main_shape == 'V_hexagon': polygon_pieces = dots_data[shape_orientation + ' V']
    elif main_shape == 'H_hexagon': polygon_pieces = dots_data[shape_orientation + ' H']
    
    if dots_visible:
        for i in range(len(polygon_pieces)):
            for id in polygon_pieces[i]:
                canvas.tag_raise(id)
                canvas.itemconfigure(id, state='normal') 

# update the current main polygon 
# note: (the other pieces of the tesselation will be copy of it, 
# but with different position and roation (if applicable))
def _update_polygon():
    global Polygon, dots_order, aux_triangle
    dots = []
    new_dot = []
    dot_count = len(polygon_pieces[0])
    dots_order.clear()
    aux_triangle.clear()
    
    _init_corners()
    
    if main_shape == "triangle":
        for j in [0,120,240]:
            new_dot = _rotate( corners[0][0],corners[0][1],  offset[0],offset[1],  j)
            dots.append(new_dot[0]); dots.append(new_dot[1])
            for i in range(dot_count):
                coords = canvas.coords(polygon_pieces[0][i])
                new_dot = _rotate( coords[0]+dot_size,coords[1]+dot_size,  offset[0],offset[1],  j)
                dots.append(new_dot[0])
                dots.append(new_dot[1])
        
    elif main_shape in ["square","diamond"]:
        # editable edges
        for j in range(len(polygon_pieces)):
            dots.append(corners[j][0]); dots.append(corners[j][1]) # corner
            for i in range(dot_count):
                coords = canvas.coords(polygon_pieces[j][i])
                dots.append(coords[0]+dot_size)
                dots.append(coords[1]+dot_size)
        # the other 2 edges
        # still orientation
        if shape_orientation in ['still squares','still diamonds']:
            for j in [0,1]:
                dots.append(corners[j+2][0]); dots.append(corners[j+2][1]) #corner
                curr_edge_middle = [ (corners[j][0]+corners[j+1][0])/2, (corners[j][1]+corners[j+1][1])/2 ]
                for i in range(dot_count-1,-1,-1):
                    coords = canvas.coords(polygon_pieces[j][i])
                    new_pos = _rotate(coords[0]+dot_size,coords[1]+dot_size,  curr_edge_middle[0],curr_edge_middle[1],  180)
                    new_pos = _rotate(new_pos[0],new_pos[1],  offset[0],offset[1],  180)
                    dots.append(new_pos[0])
                    dots.append(new_pos[1])
        # rotated orientation
        elif shape_orientation in ['rotated squares','rotated diamonds']:
            cen = [2,0]          # id of the corner to rotate around it
            rot_deg = [270, 90]  # the degree of the rotation angle
            piece_set = [1,0]    # the id of the edge to rotate
            for j in range(len(polygon_pieces)):
                dots.append(corners[j+2][0]); dots.append(corners[j+2][1]) #corner
                for i in range(dot_count-1,-1,-1):
                    coords = canvas.coords(polygon_pieces[piece_set[j]][i])
                    new_pos = _rotate(coords[0]+dot_size,coords[1]+dot_size,  corners[cen[j]][0],corners[cen[j]][1],   rot_deg[j])
                    dots.append(new_pos[0])
                    dots.append(new_pos[1])
        
    elif main_shape in ["H_hexagon","V_hexagon"]:
        corn = -1        # the current corner of the hexagon
        mirror = [2,0,1] # the opposite edge of the current editable edge
        for j in range(len(polygon_pieces)):
            corn += 1
            dots.append(corners[corn][0]) # corner
            dots.append(corners[corn][1])
            for i in range(dot_count):
                coords = canvas.coords(polygon_pieces[j][i])
                dots.append(coords[0]+dot_size)
                dots.append(coords[1]+dot_size)
            corn += 1
            dots.append(corners[corn][0]) # corner
            dots.append(corners[corn][1])
                
            # still orientation
            if shape_orientation == 'still hexagons': 
                curr_edge_mid = [(corners[corn][0]+corners[corn+1][0])/2, (corners[corn][1]+corners[corn+1][1])/2]
                for i in range(dot_count-1,-1,-1):
                    coords = canvas.coords(polygon_pieces[mirror[j]][i])
                    new_dot = _rotate( coords[0]+dot_size,coords[1]+dot_size,  offset[0],offset[1],  180)
                    new_dot = _rotate( new_dot[0],new_dot[1],  curr_edge_mid[0],curr_edge_mid[1],  180)
                    dots.append(new_dot[0])
                    dots.append(new_dot[1])
            # rotated orientation
            elif shape_orientation == 'rotated hexagons': 
                for i in range(dot_count-1,-1,-1):
                    coords = canvas.coords(polygon_pieces[j][i])
                    new_dot = _rotate( coords[0]+dot_size,coords[1]+dot_size,  corners[corn][0],corners[corn][1],  240)
                    dots.append(new_dot[0])
                    dots.append(new_dot[1])
    
    # save the current shape dots positions relative to (0,0) offset
    for d in range(0,len(dots),+2):
        dots_order.append(dots[d]  -offset[0])
        dots_order.append(dots[d+1]-offset[1])
    canvas.coords(Polygon, dots)
    
    # update outline and fill colour
    shape_outline_colour = ''
    if outline_size == 0: shape_outline_colour = tiles_colours[ _get_colour_id(0,0,Polygon,0) ]
    else: shape_outline_colour = outline_colour
            
    canvas.itemconfig(Polygon, width=outline_size, outline=shape_outline_colour)
    canvas.itemconfig(Polygon, fill=tiles_colours[ _get_colour_id(0,0,Polygon,0) ])
    
    # build auxiliary triangle and save it
    if main_shape == "triangle":
        shift = (_dist_between(corners[0],corners[1]))/2
        for j in [0,240,120]:
            for dot in range(dot_count+1):
                if j == 0:
                    aux_triangle.append(dots_order[dot*2]-shift)
                    aux_triangle.append(dots_order[(dot*2)+1])
                else:
                    new_dot = _rotate(aux_triangle[dot*2],aux_triangle[(dot*2)+1],  0,-(SIN(30)*size),  j)
                    aux_triangle.append(new_dot[0])
                    aux_triangle.append(new_dot[1])
    
    # update tessellation
    _update_Tessellation()

# update the tiles
def _update_Tessellation():
    if len(tiles_ids) == 0: _make_Tessellation()
    
    rotated_tiles = {}
    angles = [0]
    if shape_orientation in ['rotated squares','rotated diamonds','rotated hexagons']: # for rotated tiles
        if   main_shape in ['square','diamond']: angles += [90,180,270]
        elif main_shape in ['H_hexagon','V_hexagon']: angles += [120,240]
    for a in angles: # save the rotated tiles, even the one that is not rotated
        tile = []
        for d in range(0,len(dots_order),+2):
            new_dot = _rotate(dots_order[d],dots_order[d+1],  0,0,  a)
            tile.append(new_dot[0])
            tile.append(new_dot[1])
        rotated_tiles.update( {a:tile} )
    
    for id in tiles_ids:
        if tiles_visible:
            tile_offset = [tiles_proprieties[id][0],tiles_proprieties[id][1]]
            dots = []
            
            i = tiles_proprieties[id][2]
            j = tiles_proprieties[id][3]
            tile_rot = 0
            if main_shape == "triangle" and tiles_proprieties[id][3]%2 == 1:
                tile_rot = 180
                for d in range(0,len(aux_triangle),+2):
                    dots.append(aux_triangle[d]  +tile_offset[0])
                    dots.append(aux_triangle[d+1]+tile_offset[1])
            else:
                
                # rotated orientations
                if main_shape == "square" and shape_orientation == "rotated squares":
                    if   i%2 == 0 and j%2 == 1: tile_rot = 90
                    elif i%2 == 1 and j%2 == 0: tile_rot = 270
                    elif i%2 == 1 and j%2 == 1: tile_rot = 180
                if main_shape == "diamond" and shape_orientation == "rotated diamonds":
                    if   ((i%4 == 0 and j%2 == 1) or (i%4 == 2 and j%2 == 0)): tile_rot = 180
                    elif ((i%4 == 1 and j%2 == 0) or (i%4 == 3 and j%2 == 1)): tile_rot = 270
                    elif ((i%4 == 1 and j%2 == 1) or (i%4 == 3 and j%2 == 0)): tile_rot = 90
                if main_shape == "H_hexagon" and shape_orientation == "rotated hexagons":
                    if   i%3 == 1: tile_rot = 120
                    elif i%3 == 2: tile_rot = 240
                if main_shape == "V_hexagon" and shape_orientation == "rotated hexagons":
                    if   ((i%2 == 0 and j%3 == 2) or (i%2 == 1 and j%3 == 1)): tile_rot = 120
                    elif ((i%2 == 0 and j%3 == 1) or (i%2 == 1 and j%3 == 0)): tile_rot = 240  
                
                for d in range(0,len(dots_order),+2):
                    dots.append(rotated_tiles[tile_rot][d]  +tile_offset[0])
                    dots.append(rotated_tiles[tile_rot][d+1]+tile_offset[1])
            
            tiles_proprieties[id][4] = tile_rot
            tile_outline_colour = ''
            if outline_size == 0: tile_outline_colour = tiles_colours[ _get_colour_id(i,j,id,tile_rot) ]
            else: tile_outline_colour = outline_colour
            
            canvas.itemconfig(id, width=outline_size, outline=tile_outline_colour)
            canvas.itemconfig(id, fill=tiles_colours[ _get_colour_id(i,j,id,tile_rot) ])
            canvas.itemconfigure(id, state='normal')
            canvas.coords(id, dots)
        else:
            canvas.itemconfigure(id, state='hidden')

# generate/reset tessellation tiles
def _make_Tessellation():
    tiles_proprieties.clear()
    
    shift = [0,0,0] # [<line shift>, <column shift>, <where line shift starts>(does not apply to squares) ]
    n = 0 # number of rows
    m = 0 # number of columns
    if   main_shape == 'triangle':  
        n = 5; m = 20
        shift = [size*COS(30)*1,  size*SIN(90)+size*SIN(30),   size*COS(30)*1]
    elif main_shape == 'square':
        n = 6; m = 10
        shift = [size*COS(45)*2,  size*SIN(45)*2,   0]
    elif main_shape == 'diamond':
        n = 8; m = 7
        shift = [size*COS(0)*2,   size*SIN(90)*1,   size*COS(0)]
    elif main_shape == 'H_hexagon': 
        n = 9; m = 6
        shift = [size*COS(0)*3,   size*SIN(60)*1,   size*COS(0)*1.5]
    elif main_shape == 'V_hexagon': 
        n = 6; m = 8
        shift = [size*COS(30)*2,  size*SIN(90)*1.5, size*COS(30)]
    
    list_empty = False # if tiles id is empty
    if len(tiles_ids) == 0:
        list_empty = True

    index = 0
    for row in range(0,n): # generate the tiles
        for column in range(0,m):
            if not (row == 0 and column == 0):
                for i in [-1,1]:
                    if list_empty:
                        tiles_ids.append(canvas.create_polygon([0,0,0,0]))
                    if tiles_colours.get(index) == None:
                        tiles_colours.update( {index:_random_colour()} )
                    
                    tile_props = [offset[0]+shift[0]*column*i -((row%2)*shift[2]),offset[1]+shift[1]*row, row,column*i, 0]
                    tiles_proprieties.update( {tiles_ids[index] : tile_props} )
                    index += 1
                    
                if row != 0:
                    for i in [-1,1]:
                        if list_empty:
                            tiles_ids.append(canvas.create_polygon([0,0,0,0]))
                        if tiles_colours.get(index) == None:
                            tiles_colours.update( {index:_random_colour()} )
                    
                        tile_props = [offset[0]+shift[0]*column*i -((row%2)*shift[2]),offset[1]-shift[1]*row, -row,column*i, 0]
                        tiles_proprieties.update( {tiles_ids[index] : tile_props} )
                        index += 1
    
    if list_empty:
        for id in tiles_ids:
            _tile_tag_bind(id)
    
    # bring all dots to the top
    for i in range(len(polygon_pieces)):
        for dot_id in polygon_pieces[i]:
            canvas.tag_raise(dot_id)

# erase current tiles
def _erase_Tessellation():
    while len(tiles_ids) > 0:
        canvas.delete(tiles_ids[0])
        del tiles_ids[0]

# scale the canvas
def _scale(value):
    global size, zoom, polygon_pieces
    d_zoom = int(float(value)) - zoom
    polygon_pieces_copy = polygon_pieces.copy()
    zoom = int(float(value))
    
    if d_zoom > 0: size = size * ((d_zoom * 0.01) + 1)
    elif d_zoom < 0: size = size / ((d_zoom * -0.01) + 1)
    
    _make_Tessellation()
    _update_all()
    if len(polygon_pieces) == len(polygon_pieces_copy):
        polygon_pieces = polygon_pieces_copy.copy()
        for i in range(len(polygon_pieces)):
            for circle in polygon_pieces[i]:
                curr_pos = canvas.coords(circle)
                new_pos = _scale_dot(curr_pos[0],curr_pos[1],    offset[0],offset[1],    ((d_zoom * 0.01) + 1))
                new_pos = [new_pos[0] - curr_pos[0], new_pos[1] - curr_pos[1]]
                canvas.move(circle, new_pos[0], new_pos[1])
        _make_Tessellation()
        _update_polygon()

# reset dots limits list
def _reset_limit_list():
    global pieces_limits
    pieces_limits.clear()
    if main_shape == 'triangle': pieces_limits = [[]]
    elif main_shape in ['square','diamond']: pieces_limits = [[],[]]
    elif main_shape in ['H_hexagon','V_hexagon']: pieces_limits = [[],[],[]]

# update all
def _update_all():
    _reset_limit_list()
    _update_dots_data()
    _init_corners()
    _update_limits()
    _update_polygon()
    _update_Tessellation()

# bind click function to tiles
# note: this function was created to fix a tkinter glitch with tag_bind
def _tile_tag_bind(id):
    canvas.tag_bind(id,'<Button-1>', lambda f: colour_polygon(id, "left"))
    canvas.tag_bind(id,'<Button-3>', lambda f: colour_polygon(id, "right"))

# changes the colour of a polygon
def colour_polygon(id, mouse_button):
    if curr_tool == "fill":
 
        new_colour = ""
        if   mouse_button == "left":  new_colour = selected_colour_L
        elif mouse_button == "right": new_colour = selected_colour_R
        
        if id == Polygon:
            colour_id = _get_colour_id(0,0,Polygon,0)
        else:
            colour_id = _get_colour_id(tiles_proprieties[id][2],tiles_proprieties[id][3],id,tiles_proprieties[id][4])
        tiles_colours[colour_id] = new_colour
        
        _update_polygon()
        _update_Tessellation()
        
        # uncomment for debugging
        #if id == Polygon:
        #    print("id",id,"at 0,0")
        #    print("id",id,"has offset at ",offset[0], offset[1])
        #    print("id",Polygon,"has rotation 0")
        #else:
        #    print("id",id,"at {},{}".format(tiles_proprieties[id][2],tiles_proprieties[id][3]))
        #    print("id",id,"has offset at {}, {}".format(tiles_proprieties[id][0],tiles_proprieties[id][1]))
        #    print("id",id,"has rotation {}".format(tiles_proprieties[id][4]))

# colour outline
def colour_outline(event):
    global outline_colour
    new_colour = colorchooser.askcolor()
    outline_colour = new_colour[1]
    _update_polygon()
    _update_Tessellation()
    pallete_outline.configure(background=new_colour[1])

# pick a new colour
def colour_picker(mouse_button):
    global selected_colour_L, selected_colour_R
    new_colour = colorchooser.askcolor()
    
    if mouse_button == "left":
        selected_colour_L = new_colour[1]
        pallete_L.configure(background=new_colour[1])
    elif mouse_button == "right":
        selected_colour_R = new_colour[1]
        pallete_R.configure(background=new_colour[1])

# returns the id of the colour for the tile, depending on the given arguments
#  and the selected colour pattern
def _get_colour_id(x,y,tile_id,tile_rot):
    id = 0
    
    # here is where the colour patterns are being applied
    if curr_colour_pattern == 'rotations':
        id = "rot_{}".format(tile_rot)
        
    elif curr_colour_pattern == 'lines':
        id = "line_{}".format(x)
        
    elif curr_colour_pattern == 'columns':
        if main_shape == "triangle" and x%2 == 1: 
            y -= 1 
        elif main_shape in ["diamond","H_hexagon","V_hexagon"]:
            if x < 0: x *= -1
            y = y + (10000 * (x%2))
        id = "column_{}".format(y)
        
    elif curr_colour_pattern == 'snowflakes':
        id = "snow_{}_{}".format(x%4,y%4)
        
    elif curr_colour_pattern == 'flower':
        #TODO
        d = _dist_between([0,0],[x,y])
        id = "bull_{}".format(round(d))
        
    elif curr_colour_pattern == '2 colours':
        if x < 0: x *= -1
        if y < 0: y *= -1
        if main_shape in ["triangle","square"]:
            if x%2 == 1 and main_shape == "triangle": y+= 1
            id = "c2_{}".format( (x+y)%2 )
        elif main_shape in ["diamond","H_hexagon","V_hexagon"]:
            id = "c2_{}".format( x%2 )
            
    elif curr_colour_pattern == 'one colour':
        id = "mono"
        
    elif curr_colour_pattern == 'free draw':
        id = tile_id
    
    if tiles_colours.get(id) == None: tiles_colours.update( {id:_random_colour()} )
    return id

# set outline size
def _outline_scale():
    global outline_size
    outline_size = int(outline_scale.get())
    _update_polygon()
    _update_Tessellation()

# change main shape
def _set_main_shape(new_shape):
    global main_shape
    main_shape = new_shape
        
    # update tesselation mode
    tess_combobox['state'] = 'readonly'
    if main_shape == "triangle":
        tess_combobox.set('triangles')
        tess_combobox['state'] = 'disabled'
    elif main_shape == "square":
        tess_combobox.set('still squares')
        tess_combobox['values'] = ('still squares','rotated squares')
    elif main_shape == "diamond":
        tess_combobox.set('still diamonds')
        tess_combobox['values'] = ('still diamonds','rotated diamonds')
    elif main_shape in ['H_hexagon','V_hexagon']:
        tess_combobox.set('still hexagons')
        tess_combobox['values'] = ('still hexagons','rotated hexagons')    
    _change_tessellation_mode('')
        
    # update label 
    if   main_shape in ["triangle","square","diamond"]: shape_label.config(text="selected shape: {}".format(main_shape))
    elif main_shape == "H_hexagon": shape_label.config(text="selected shape: horizontal hexagon")
    elif main_shape == "V_hexagon": shape_label.config(text="selected shape: vertical hexagon")
       
    _erase_Tessellation()
    _make_Tessellation()
    _update_all()

# toggle tesselation
def _toggle_Tessellation_preview():
    global tiles_visible
    tiles_visible = not tiles_visible
    _update_Tessellation()

# change tessellation mode
def _change_tessellation_mode(event):
    global shape_orientation
    shape_orientation = tess_combobox.get()
    _update_dots_data()
    _update_polygon()
    _update_Tessellation()

# change colour pattern
def _change_colour_pattern(event):
    global curr_colour_pattern
    curr_colour_pattern = pattern_combobox.get()
    _update_dots_data()
    _update_polygon()
    _update_Tessellation()

# records the mouse position 
# (note: is always active when the mouse is on screen)
def motion(event):
    global mouse_x, mouse_y
    mouse_pos_label.config(text="mouse position: [{}, {}]".format(event.x, event.y))
    mouse_x, mouse_y = event.x, event.y


######## initiate these first ###
# these functions needs to be intialised before others are called

_init_dots_data()


######## background #########

bgimage1 = PhotoImage(file="canvas_bg1.png")
tool_canvas.create_image(1, 1, image=bgimage1, anchor=NW)


######## buttons ############

## tool buttons ##

img1 = PhotoImage(file="grab.png")
move_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img1, command = lambda:_select_tool("move"))
move_button.place(x=10,y=5,width=40,height=40)

img2 = PhotoImage(file="point_add.png")
pencil_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img2, command = _add_circle)
pencil_button.place(x=50,y=5,width=40,height=40)

img3 = PhotoImage(file="point_rem.png")
erase_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img3, command = _erase_circle)
erase_button.place(x=90,y=5,width=40,height=40)

img4 = PhotoImage(file="point_rem_all.png")
erase_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img4, command = _erase_all_circles)
erase_button.place(x=130,y=5,width=40,height=40)

img5 = PhotoImage(file="bucket.png")
bucket_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img5, command = lambda:_select_tool("fill"))
bucket_button.place(x=170,y=5,width=40,height=40)


## shape buttons ##

img6 = PhotoImage(file="V_hexagon.png")
bucket_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img6, command = lambda:_set_main_shape("V_hexagon"))
bucket_button.place(x=1200,y=5,width=40,height=40)

img7 = PhotoImage(file="H_hexagon.png")
bucket_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img7, command = lambda:_set_main_shape("H_hexagon"))
bucket_button.place(x=1160,y=5,width=40,height=40)

img8 = PhotoImage(file="diamond.png")
bucket_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img8, command = lambda:_set_main_shape("diamond"))
bucket_button.place(x=1120,y=5,width=40,height=40)

img9 = PhotoImage(file="square.png")
bucket_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img9, command = lambda:_set_main_shape("square"))
bucket_button.place(x=1080,y=5,width=40,height=40)

img10 = PhotoImage(file="triangle.png")
bucket_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img10, command = lambda:_set_main_shape("triangle"))
bucket_button.place(x=1040,y=5,width=40,height=40)


## tessellation settings ##

toggle_tessellation = Checkbutton(tool_canvas, text='Tessellation live preview', bg="#ffe6cc", command = _toggle_Tessellation_preview)
toggle_tessellation.place(x=680,y=3,height=20)

tess_mode_label = Label(tool_canvas, text="Tessellation mode:", bg="#ffe6cc", relief=RIDGE, bd=0)
tess_mode_label.place(x=680, y=23)

tess_combobox = ttk.Combobox(tool_canvas, width = 18, state = 'readonly')
tess_combobox.place(x=820, y=23)
tess_combobox.set('still squares')
tess_combobox.bind("<<ComboboxSelected>>", _change_tessellation_mode)
tess_combobox['values'] = ('still squares','rotated squares')


## colours for fill and outline ##

pallete_L = Canvas(tool_canvas, bg=selected_colour_L, width=35, height=35)
pallete_L.bind('<Button-1>', lambda f: colour_picker("left"))
pallete_L.place(x=280,y=5)
img11 = PhotoImage(file="mouse_L.png")
pallete_L.create_image(2, 2, image=img11, anchor=NW)

pallete_R = Canvas(tool_canvas, bg=selected_colour_R, width=35, height=35)
pallete_R.bind('<Button-1>', lambda f: colour_picker("right"))
pallete_R.place(x=320,y=5)
img12 = PhotoImage(file="mouse_R.png")
pallete_R.create_image(2, 2, image=img12, anchor=NW)

outline_label1 = Label(tool_canvas, text="outline colour:", bg="#ffb375", relief=RIDGE, bd=0)
outline_label1.place(x=370,y=2)

outline_label2 = Label(tool_canvas, text="outline size:", bg="#ffb375", relief=RIDGE, bd=0)
outline_label2.place(x=370,y=23)

outline_scale = Spinbox(tool_canvas, values=[0,1,2,3,4,5,6], width=1, state='readonly', command=_outline_scale)
outline_scale.place(x=460,y=23)

pallete_outline = Canvas(tool_canvas, bg=outline_colour, width=10, height=10)
pallete_outline.bind('<Button-1>', colour_outline)
pallete_outline.place(x=470,y=7)

pattern_label = Label(tool_canvas, text="colour pattern:", bg="#ffb375", relief=RIDGE, bd=0)
pattern_label.place(x=520,y=2)

pattern_combobox = ttk.Combobox(tool_canvas, width = 15, state = 'readonly')
pattern_combobox.place(x=500, y=23)
pattern_combobox.set('snowflakes')
pattern_combobox.bind("<<ComboboxSelected>>", _change_colour_pattern)
pattern_combobox['values'] = ('snowflakes','rotations','one colour','lines','columns','flower','2 colours','free draw')


## others ##

mouse_pos_label = Label(root, text="mouse position: [x,y]", relief=RIDGE, bd=0)
mouse_pos_label.place(x=350,y=750)

shape_label = Label(root, text="selected shape: {}".format(main_shape), relief=RIDGE, bd=0)
shape_label.place(x=350,y=720)

dots_visibility_button = Button(root, text="show/hide dots" ,bd=2, bg="white", width=15, height=1, command = _toggle_vis_circles)
dots_visibility_button.place(x=15, y=720)

zoom_lable = Label(root, text="Zoom:", relief=RIDGE, bd=0)
zoom_lable.place(x=15, y=765)

zoom_scale = Scale(root, orient=HORIZONTAL, from_=10, to=170, length=200, command = _scale)
zoom_scale.set(zoom)
zoom_scale.place(x=70, y=765)


######## initialisation #####

_update_all()
root.bind('<Motion>', motion)
root.config(cursor="@move.cur")
root.mainloop()