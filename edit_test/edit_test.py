from tkinter import *
from tkinter import colorchooser,filedialog,messagebox

root = Tk()
root.geometry("800x600")

w = 600
h = 400

mouse_x = 0
mouse_y = 0

curr_tool = "move"
selected_colour = "#e6e6e6"
dots_order = []

canvas = Canvas(root, width=w, heigh=h, bg="white")
canvas.pack(pady=20)

tool_canvas = Canvas(root, width=48, heigh=210, bg='gray')
tool_canvas.place(x=30, y=30)

Polygon = canvas.create_polygon([0,0,0,0],fill=selected_colour)

def _circle_pressed(circle):
    if curr_tool == "move": _move(circle)
    elif curr_tool == "erase": _erase(circle)
    _update_polygon()

def _select_tool(new_tool):
    global curr_tool
    curr_tool = new_tool
    root.config(cursor=("@{}.cur").format(new_tool))
    print(curr_tool)

def _move(circle):
    curr_pos = canvas.coords(circle)
    new_pos = [mouse_x - curr_pos[0] - 5, mouse_y - curr_pos[1] - 5]
    if mouse_x < 0 or mouse_x > w: new_pos[0] = 0
    if mouse_y < 0 or mouse_y > h: new_pos[1] = 0
    canvas.move(circle, new_pos[0], new_pos[1])

def _erase(circle):
    if len(dots_order) > 3:
        dots_order.remove(circle)
        canvas.delete(circle)
    else:
        messagebox.showinfo('Error',"You can't have less than 3 dots")

def _add_circle(event):
    if curr_tool == "pencil":
        if len(dots_order) < 20:
            _dot(mouse_x, mouse_y)
            _update_polygon()
        else:
            messagebox.showinfo('Error',"You can't have more than 20 dots")


def _dot(X,Y):
    id = canvas.create_oval(X-5, Y-5, X+5, Y+5, fill="pink")
    canvas.tag_bind(id,'<B1-Motion>', lambda f: _circle_pressed(id))
    canvas.tag_bind(id,'<Button-1>', lambda f: _circle_pressed(id))
    dots_order.append(id)

def _update_polygon():
    global Polygon
    dots=[]
    for i in dots_order:
        coords = canvas.coords(i)
        dots.append(coords[0]+5)
        dots.append(coords[1]+5)
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
canvas.bind('<Button-1>', _add_circle)


# add buttons
img1 = PhotoImage(file="grab.png")
move_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img1, command = lambda:_select_tool("move"))
move_button.place(x=5,y=5,width=40,height=40)

img2 = PhotoImage(file="pencil.png")
pencil_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img2, command = lambda:_select_tool("pencil"))
pencil_button.place(x=5,y=45,width=40,height=40)

img3 = PhotoImage(file="eraser.png")
erase_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img3, command = lambda:_select_tool("erase"))
erase_button.place(x=5,y=85,width=40,height=40)

img4 = PhotoImage(file="bucket.png")
bucket_button = Button(tool_canvas, bd=2, bg="white", width=3, height=1, image = img4, command = lambda:_select_tool("fill"))
bucket_button.place(x=5,y=125,width=40,height=40)

pallete = Canvas(tool_canvas, bd=5, bg=selected_colour, width=25, height=25)
pallete.bind('<Button-1>', colour_picker)
pallete.place(x=5,y=165)

# create the polygon
_dot(200,100)
_dot(300,300)
_dot(100,300)
_update_polygon()


canvas.tag_bind(Polygon,'<Button-1>',colour_polygon)
root.config(cursor="@move.cur")
root.mainloop()