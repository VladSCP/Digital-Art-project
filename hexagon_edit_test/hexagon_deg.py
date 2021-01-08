"""
A simple test for hexagon editing making it ready for tiling
has 4 orientation: horizontal or vertical and rotated or no rotated
"""

from tkinter import *
from tkinter import colorchooser,filedialog,messagebox
import random
import numpy as np
import math

def SIN(x): return np.around(np.sin(math.radians(x)), decimals=2)
def COS(x): return np.around(np.cos(math.radians(x)), decimals=2)
def _rotate(x,y, angl): return [x*COS(angl)-y*SIN(angl), x*SIN(angl)+y*COS(angl)]


root = Tk()
root.geometry("800x600")

w = 600
h = 400

mouse_x = 0
mouse_y = 0

offset = [300,200]
size = 100
dot_size = 4

curr_tool = "move"
shape_orientation = 'horizontal 0'
selected_colour = "#e6e6e6"

dots_visible = True
dots_order = []

canvas = Canvas(root, width=w, heigh=h, bg="white")
canvas.pack(pady=20)

tool_canvas = Canvas(root, width=48, heigh=250, bg='gray')
tool_canvas.place(x=30, y=30)

polygon_pieces = [[],[],[]]
corners = []
Polygon = canvas.create_polygon([0,0,0,0],fill=selected_colour)

def _init_corners():
    global corners
    corners.clear()
    angles = []
    if shape_orientation in ['horizontal 0','horizontal 60']: angles = [0,60,120,180,240,300,360]
    elif shape_orientation in ['vertical 0','vertical 60']: angles = [30,90,150,210,270,330,390]
    for j in angles:
        corn = _rotate(size,0 , j)
        corners.append([corn[0]+offset[0], corn[1]+offset[1]])

def _circle_pressed(circle, pieace_id):
    if curr_tool == "move": 
        _move(circle, pieace_id)
        _update_polygon()

def _select_tool(new_tool):
    global curr_tool
    curr_tool = new_tool
    root.config(cursor=("@{}.cur").format(new_tool))
    print(curr_tool)

def _move(circle, pieace_id):
    curr_pos = canvas.coords(circle)
    new_pos = [mouse_x - curr_pos[0] - dot_size, mouse_y - curr_pos[1] - dot_size]
    # limits
    #if pieace_id == 0:
    #    if mouse_x < corners[0][0] or mouse_x > corners[1][0]: new_pos[0] = 0
    #    if mouse_y < corners[0][1]-size*2 or mouse_y > corners[0][1]+size*2: new_pos[1] = 0
    #elif pieace_id == 1:
    #    if mouse_x < corners[1][0]-size*2 or mouse_x > corners[1][0]+size*2: new_pos[0] = 0
    #    if mouse_y < corners[1][1] or mouse_y > corners[2][1]: new_pos[1] = 0
    canvas.move(circle, new_pos[0], new_pos[1])

def _erase_circle():
    dot_count = len(polygon_pieces[0])
    if dot_count > 0:
        for j in [0,1,2]:
            canvas.delete(polygon_pieces[j][-1])
            del polygon_pieces[j][-1] 
        _update_polygon()
    else:
        messagebox.showinfo('Error',"There are no dots to erase")

def _add_circle():
    dot_count = len(polygon_pieces[0])
    if dot_count < 7:
        corn = [0,2,4]
        for j in [0,1,2]:
            A = []; B = corners[corn[j]+1]
            if dot_count == 0: 
                A = corners[corn[j]]
            else: 
                A = canvas.coords(polygon_pieces[j][-1])
                A[0] += dot_size; A[1] += dot_size
            _dot(int((A[0]+B[0])/2), int((A[1]+B[1])/2), j)
        _update_polygon()
    else:
        messagebox.showinfo('Error',"You can't have more than 7 dots on each edge")

def _toggle_vis_circles():
    global dots_visible
    dots_visible = not dots_visible
    for i in range(len(polygon_pieces)):
        for j in range(len(polygon_pieces[0])):
            if dots_visible:    canvas.itemconfigure(polygon_pieces[i][j], state='normal')
            else:               canvas.itemconfigure(polygon_pieces[i][j], state='hidden') 

def _change_orientation():
    global shape_orientation, or_button
    if shape_orientation == 'horizontal 0': shape_orientation = 'horizontal 60'
    elif shape_orientation == 'horizontal 60': shape_orientation = 'vertical 0'
    elif shape_orientation == 'vertical 0': shape_orientation = 'vertical 60'
    elif shape_orientation == 'vertical 60': shape_orientation = 'horizontal 0'
    or_label.config(text="orientation:\n{} deg".format(shape_orientation))
    _init_corners()
    _update_polygon()

def _dot(X,Y,piece_id):
    id = canvas.create_oval(X-dot_size, Y-dot_size, X+dot_size, Y+dot_size, fill="pink")
    canvas.tag_bind(id,'<B1-Motion>', lambda f: _circle_pressed(id,piece_id))
    canvas.tag_bind(id,'<Button-1>',  lambda f: _circle_pressed(id,piece_id))
    polygon_pieces[piece_id].append(id)

def _update_polygon():
    global Polygon
    dots=[]
    dot_count = len(polygon_pieces[0])
    
    corn = -1
    mirror = [2,0,1]
    for j in [0,1,2]:
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
            
        # 0 deg
        if shape_orientation in ['horizontal 0','vertical 0']:
            curr_edge_mid = [int((corners[corn][0]+corners[corn+1][0])/2), int((corners[corn][1]+corners[corn+1][1])/2)]
            for i in range(dot_count-1,-1,-1):
                coords = canvas.coords(polygon_pieces[mirror[j]][i])
                new_dot = _rotate( coords[0]-offset[0]+dot_size, coords[1]-offset[1]+dot_size, 180)
                new_dot = _rotate( new_dot[0]+offset[0]-curr_edge_mid[0], new_dot[1]+offset[1]-curr_edge_mid[1], 180)
                dots.append(new_dot[0]+curr_edge_mid[0])
                dots.append(new_dot[1]+curr_edge_mid[1])
        # 60
        elif shape_orientation in ['horizontal 60','vertical 60']:
            for i in range(dot_count-1,-1,-1):
                coords = canvas.coords(polygon_pieces[j][i])
                new_dot = _rotate( coords[0]-corners[corn][0]+dot_size, coords[1]-corners[corn][1]+dot_size, 240)
                dots.append(new_dot[0]+corners[corn][0])
                dots.append(new_dot[1]+corners[corn][1])
       

    canvas.coords(Polygon, dots)


def colour_polygon(event):
    if curr_tool == "fill":
        canvas.itemconfig(Polygon, fill=selected_colour)

def colour_picker(event):
    global selected_colour
    new_colour = colorchooser.askcolor()
    selected_colour = new_colour[1]
    pallete.configure(background=new_colour[1])
    

def motion(event):
    global mouse_x, mouse_y
    mouse_x, mouse_y = event.x, event.y


root.bind('<Motion>', motion)


# add buttons
img1 = PhotoImage(file="grab.png")
move_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img1, command = lambda:_select_tool("move"))
move_button.place(x=5,y=5,width=40,height=40)

img2 = PhotoImage(file="point_add.png")
pencil_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img2, command = _add_circle)
pencil_button.place(x=5,y=45,width=40,height=40)

img3 = PhotoImage(file="point_rem.png")
erase_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img3, command = _erase_circle)
erase_button.place(x=5,y=85,width=40,height=40)

img4 = PhotoImage(file="bucket.png")
bucket_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img4, command = lambda:_select_tool("fill"))
bucket_button.place(x=5,y=165,width=40,height=40)

img5 = PhotoImage(file="or.png")
or_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img5, command = _change_orientation)
or_button.place(x=5,y=125,width=40,height=40)

pallete = Canvas(tool_canvas, bd=5, bg=selected_colour, width=25, height=25)
pallete.bind('<Button-1>', colour_picker)
pallete.place(x=5,y=205)

or_label = Label(root, text="orientation:\n{} deg".format(shape_orientation), relief=RIDGE, bd=0)
or_label.place(x=5,y=300)

dots_visibility_button = Button(root, text="show/hide dots" ,bd=2, bg="white", width=15, height=1, command = _toggle_vis_circles)
dots_visibility_button.place(x=5, y=440)



_init_corners()
_update_polygon()
canvas.tag_bind(Polygon,'<Button-1>',colour_polygon)
root.config(cursor="@move.cur")
root.mainloop()