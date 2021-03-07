from vector import Vector, fromAngle, dist
from math import pi, radians, inf
import random
import tkinter as tk

class Boundary:
    def __init__(self, x1, y1, x2, y2):
        self.a = Vector(x1, y1)
        self.b = Vector(x2, y2)

    def show(self):
        global stroke, fill
        canvas.create_line(self.a.x, self.a.y, self.b.x, self.b.y, 
                        fill = stroke)


class Ray:
    def __init__(self, pos, angle):
        self.pos = pos
        self.dir = fromAngle(angle)

    def show(self):
        global stroke, fill
        canvas.create_line(self.pos.x, self.pos.y, self.pos.x + self.dir.x * 10, self.pos.y + self.dir.y * 10
                        , fill = fill)

    def lookAt(self, x, y):
        self.dir.x = x - self.pos.x
        self.dir.y = y - self.pos.y
        self.dir.normalize()

    def cast(self, wall):
        x1 = wall.a.x
        y1 = wall.a.y
        x2 = wall.b.x
        y2 = wall.b.y

        x3 = self.pos.x
        y3 = self.pos.y
        x4 = self.pos.x + self.dir.x
        y4 = self.pos.y + self.dir.y

        deno = ((x1 - x2)*(y3 - y4)) - ((y1 - y2)*(x3 - x4))
        if deno == 0:
            return

        t = (((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / deno
        u = -(((x1 - x2) * (y1 - y3)) - ((y1 - y2) * (x1 - x3))) / deno
        
        if t > 0 and t < 1 and u > 0:
            a = x1 + t * (x2 - x1)
            b = y1 + t * (y2 - y1)
            pt = Vector(a, b)
            return pt
        else:
            return


class Particle:
    def __init__(self):
        self.pos = Vector(width/2, height/2)
        self.rays = []
        self.fov = 45
        self.heading = 0
        for i in range(-self.fov // 2, self.fov // 2, 1):
            self.rays.append(Ray(self.pos, radians(i + self.heading)))

    def rotate(self, angle):
        self.heading = self.heading + angle
        for i in range(0, self.fov, 1):
            self.rays[i].dir = fromAngle(radians(i + self.heading))


    def update(self, x, y):
        self.pos.set(x, y)

    def show(self):
        global stroke, fill
        r = 2
        canvas.create_oval(self.pos.x - r, self.pos.y - r, self.pos.x + r, self.pos.y + r, 
                            fill = fill, outline = stroke)

    def look(self, walls):
        scene = []
        global fill
        for ray in self.rays:
            closest = None
            record = inf
            for wall in walls:
                pt = ray.cast(wall)
                if pt: 
                    d = dist(self.pos, pt)
                    if (d < record):
                        record = d
                        closest = pt
            scene.append(record)
            if closest:
                canvas.create_line(self.pos.x, self.pos.y, closest.x, closest.y, fill = fill)
        return scene


def toHexColor(clr):
    helper = hex(clr).split('x')[-1]
    return "#{}{}{}".format(helper, helper, helper)

def mapped(n, x, y, a, b):
    return a + (n - x) * (b - a) / (y - x)


width = 400
height = 400
sceneW = 400
sceneH = 400
bg_color = "#000"
stroke = "#fff"
fill = "#a00"

win = tk.Tk()
win.geometry("800x400")
win.resizable(0, 0)
win.title("Ray Casting")

canvas = tk.Canvas(win, width = width*2, height = height, bg = bg_color)
walls = []

# Boundaries
walls.append(Boundary(0, 0, width, 0))
walls.append(Boundary(0, 0, 0, height))
walls.append(Boundary(0, height, width, height))
walls.append(Boundary(width, 0, width, height))

# Box
walls.append(Boundary(100, 100, 150, 100))
walls.append(Boundary(100, 100, 100, 150))
walls.append(Boundary(150, 100, 150, 150))
walls.append(Boundary(100, 150, 150, 150))

# Random walls
for i in range(4):
    x1 = random.randint(0, width)
    x2 = random.randint(0, width)
    y1 = random.randint(0, height)
    y2 = random.randint(0, height)
    walls.append(Boundary(x1, y1, x2, y2))

particle = Particle()
xShift = sceneW
yShift = 0


def keyPressed(event):
    if event.char == "a":
        particle.rotate(-1)
    elif event.char == "d":
        particle.rotate(1)
    canvas.delete("all")
    for wall in walls:
        wall.show()
    scene = particle.look(walls)
    w = sceneW / len(scene)
    for i in range(len(scene)):
        c = "#fff"
        clr = 0  
        if scene[i] > sceneW:
            scene[i] = sceneW
        if scene[i] == inf:
            c = "#000"
        else:
            sq = scene[i]**2
            wSq = sceneW**2
            clr = round(mapped(sq, 0, wSq, 255, 0))
        if clr < 0:
            c = "#000"
        c = toHexColor(clr)
        stripH = mapped(scene[i], 0, sceneW, sceneH, sceneH / 2)
        canvas.create_rectangle(i * w + xShift, sceneH - stripH + yShift, (i + 1) * w + xShift, stripH + yShift, fill = c, width = 0)


def motion(event):
    global mouseX, mouseY
    mouseX, mouseY = event.x, event.y
    if mouseX > width - 1:
        mouseX = width - 1
    elif mouseX < 1:
        mouseX = 1
    elif mouseY < 1:
        mouseY = 1
    elif mouseY > height - 1:
        mouseY = height - 1 
    canvas.delete("all")
    particle.update(mouseX, mouseY)
    particle.show()
    for wall in walls:
        wall.show()
    scene = particle.look(walls)
    w = sceneW / len(scene)
    for i in range(len(scene)):
        c = "#fff"
        clr = 0
        if scene[i] == inf:
            c = "#000"
        else:
            clr = 255 - round((scene[i] / sceneW) * 255)
        if clr < 0:
            c = "#000"
        c = toHexColor(clr)
        stripH = mapped(scene[i], 0, sceneW, sceneH, sceneH // 2)
        canvas.create_rectangle(i * w + xShift, sceneH - stripH + yShift, (i + 1) * w + xShift, stripH + yShift, fill = c, width = 0)


canvas.pack()
win.bind("<Key>", keyPressed)
win.bind("<Motion>", motion)
win.mainloop()