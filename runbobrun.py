from tkinter import *
import random
import time

MAX_TIME_SECS = 60

class Coords:
    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

def within_x(co1, co2):
    if (co1.x1 > co2.x1 and co1.x1 < co2.x2) \
            or (co1.x2 > co2.x1 and co1.x2 < co2.x2) \
            or (co2.x1 > co1.x1 and co2.x1 < co1.x2) \
            or (co2.x2 > co1.x1 and co2.x2 < co1.x2):
        return True
    else:
        return False

def within_y(co1, co2):
    if (co1.y1 > co2.y1 and co1.y1 < co2.y2) \
            or (co1.y2 > co2.y1 and co1.y2 < co2.y2) \
            or (co2.y1 > co1.y1 and co2.y1 < co1.y2) \
            or (co2.y2 > co1.y1 and co2.y2 < co1.y2):
        return True
    else:
        return False

def collided_left(co1, co2):
    if within_y(co1, co2):
        if co1.x1 >= co2.x1 and co1.x1 <= co2.x2:
            return True
    return False

def collided_right(co1, co2):
    if within_y(co1, co2):
        if co1.x2 >= co2.x1 and co1.x2 <= co2.x2:
            return True
    return False

def collided_top(co1, co2):
    if within_x(co1, co2):
        if co1.y1 >= co2.y1 and co1.y1 <= co2.y2:
            return False
    return False

def collided_bottom(y, co1, co2):
    if within_x(co1, co2):
        y_calc = co1.y2 + y
        if y_calc >= co2.y1 and y_calc <= co2.y2:
            return True
    return False

class Sprite:
    def __init__(self, game):
        self.game = game
        self.endgame = False
        self.coordinates = None
    def move(self):
        pass
    def coords(self):
        return self.coordinates

class PlatformSprite(Sprite):
    def __init__(self, game, photo_image1, photo_image2, x, y, width, height):
        Sprite.__init__(self, game)

        self.game = game
        self.last_time = time.time()
        self.current_image = 1
        self.x = x
        self.y = y
        self.photo_image1 = photo_image1
        self.photo_image2 = photo_image2        
        self.image = game.canvas.create_image(x, y,
                image=photo_image1, anchor='nw')
        self.coordinates = Coords(x, y, x + width, y + height)

    def move(self):
        if time.time() - self.last_time > 1:
            self.last_time = time.time()
            self.current_image = 2 if self.current_image == 1 else 1
        image = self.photo_image1 if self.current_image == 1 else self.photo_image2
        self.game.canvas.itemconfig(self.image, image=image)


class StickFigureSprite(Sprite):
    def __init__(self, game):
        Sprite.__init__(self, game)
        self.images_left = [
            PhotoImage(file='icons/figure-L1.gif'),
            PhotoImage(file='icons/figure-L2.gif'),
            PhotoImage(file='icons/figure-L3.gif')
        ]
        self.images_right = [
            PhotoImage(file='icons/figure-L1.gif'),
            PhotoImage(file='icons/figure-L2.gif'),
            PhotoImage(file='icons/figure-L3.gif')
        ]
        self.figure_wet = PhotoImage(file='icons/figure-wet.gif')
        self.image = game.canvas.create_image(200, 470,
                image=self.images_left[0], anchor='nw')
        self.x = -2
        self.y = 0
        self.current_image = 0
        self.current_image_add = 1
        self.jump_count = 0
        self.last_time = time.time()
        self.coordinates = Coords()
        game.canvas.bind_all('<KeyPress-Left>', self.turn_left)
        game.canvas.bind_all('<KeyPress-Right>', self.turn_right)
        game.canvas.bind_all('<space>', self.jump)

    def turn_left(self, evt):
        if self.y == 0:
            self.x = -2

    def turn_right(self, evt):
        if self.y == 0:
            self.x = 2

    def jump(self, evt):
        if self.y == 0:
            self.y = -4
            self.jump_count = 0

    def animate(self):
        if self.x != 0 and self.y == 0:
            if time.time() - self.last_time > 0.1:
                self.last_time = time.time()
                self.current_image += self.current_image_add
                if self.current_image >= 2:
                    self.current_image_add = -1
                if self.current_image <= 0:
                    self.current_image_add = 1
        if self.x < 0:
            if self.y != 0:
                self.game.canvas.itemconfig(self.image, 
                        image=self.images_left[2])
            else:
                self.game.canvas.itemconfig(self.image, 
                        image=self.images_left[self.current_image])
        elif self.x > 0:
            if self.y != 0:
                self.game.canvas.itemconfig(self.image, 
                        image=self.images_right[2])
            else:
                self.game.canvas.itemconfig(self.image, 
                        image=self.images_right[self.current_image])

    def coords(self):
        xy = self.game.canvas.coords(self.image)
        self.coordinates.x1 = xy[0]
        self.coordinates.y1 = xy[1]
        self.coordinates.x2 = xy[0] + 27
        self.coordinates.y2 = xy[1] + 30
        return self.coordinates

    def move(self):
        self.animate()
        if self.y < 0:
            self.jump_count += 1
            if self.jump_count > 20:
                self.y = 4
        if self.y > 0:
            self.jump_count -= 1
        co = self.coords()
        left = True
        right = True
        top = True
        bottom = True
        falling = True
        if self.y > 0 and co.y2 >= self.game.canvas_height:
            self.y = 0
            bottom = False
        elif self.y < 0 and co.y1 <= 0:
            self.y = 0
            top = False
        if self.x > 0 and co.x2 >= self.game.canvas_width:
            self.x = 0
            right = False
        elif self.x < 0 and co.x1 <= 0:
            self.x = 0
            left = False

        for sprite in self.game.sprites:
            if sprite == self:
                continue
            sprite_co = sprite.coords()
            if top and self.y < 0 and collided_top(co, sprite_co):
                self.y = -self.y
                top = False
            if bottom and self.y > 0 and collided_bottom(self.y, 
                    co, sprite_co):
                self.y = sprite_co.y1 - co.y2
                if self.y < 0:
                    self.y = 0
                bottom = False
                top = False
            if bottom and falling and self.y == 0 \
                    and co.y2 < self.game.canvas_height \
                    and collided_bottom(1, co, sprite_co):
                falling = False
            if left and self.x < 0 and collided_left(co, sprite_co):
                self.x = 0
                left = False
                if sprite.endgame:
                    self.game.running = False
            if right and self.x > 0 and collided_right(co, sprite_co):
                self.x = 0
                right = False
                if sprite.endgame:
                    self.game.running = False

        if falling and bottom and self.y == 0 \
                and co.y2 < self.game.canvas_height:
            self.y = 4
        self.game.canvas.move(self.image, self.x, self.y)

class ToiletSprite(Sprite):
    def __init__(self, game, photo_image, image_wet, x, y, width, height):
        Sprite.__init__(self, game)
        self.photo_image = photo_image
        self.image_wet = image_wet
        self.image = game.canvas.create_image(x, y, 
                image=self.photo_image, anchor='nw')
        self.coordinates = Coords(x, y, x + (width / 2), y + height)
        self.endgame = True

class Game:
    def __init__(self):
        self.tk = Tk()
        self.tk.title('Run Bob Run')
        self.tk.resizable(0, 0)
        self.tk.wm_attributes('-topmost', 1)
        self.canvas = Canvas(self.tk, width=500, height=500, 
                             highlightthickness=0)
        self.canvas.pack()
        self.tk.update()
        self.canvas_height = self.canvas.winfo_height()
        self.canvas_width = self.canvas.winfo_width()
        self.bg = PhotoImage(file='icons/background.gif')
        w = self.bg.width()
        h = self.bg.height()
        for x in range(0, 5):
            for y in range(0, 5):
                self.canvas.create_image(x * w, y * h, 
                        image=self.bg, anchor='nw')
        self.sprites = []
        self.running = True
        self.start_time = time.time()
        self.timer_text = self.canvas.create_text(490, 10,
                text=str(MAX_TIME_SECS), font=('Helvetica', 18), fill='white', anchor='ne')

    def mainloop(self):
        while True:
            if self.running == True:
                elapsed = time.time() - self.start_time
                remaining = max(0, MAX_TIME_SECS - int(elapsed))
                self.canvas.itemconfig(self.timer_text, text=str(remaining))
                if elapsed > MAX_TIME_SECS:
                    self.running = False
                    for sprite in self.sprites:
                        if isinstance(sprite, StickFigureSprite):
                            self.canvas.itemconfig(sprite.image,
                                    image=sprite.figure_wet)
                    self.canvas.create_text(250, 250,
                            text='Oh dear, you did not make it!',
                            font=('Helvetica', 18), fill='red')
                    self.tk.update_idletasks()
                    self.tk.update()
                    time.sleep(5)
                    break
                for sprite in self.sprites:
                    sprite.move()
            else:
                for sprite in self.sprites:
                    if isinstance(sprite, ToiletSprite):
                        self.canvas.itemconfig(sprite.image,
                                image=sprite.image_wet)

                self.canvas.create_text(250, 380, text='Well Done!',
                        font=('Helvetica', 30), fill='red')
                self.tk.update_idletasks()
                self.tk.update()
                time.sleep(5)
                break
            self.tk.update_idletasks()
            self.tk.update()
            time.sleep(0.02)

g = Game()

p1 =  PhotoImage(file='icons/platform1.gif')
p2 =  PhotoImage(file='icons/platform2.gif')
p3 =  PhotoImage(file='icons/platform3.gif')

platform10 = PlatformSprite(g, p2, p1, 45, 60, 60, 10)
platform9 = PlatformSprite(g, p2, p1,  100, 120, 60, 10)                           
platform8 = PlatformSprite(g, p3, p2,  200, 160, 10, 10)
platform7 = PlatformSprite(g, p2, p1, 260, 200, 60, 10)
platform6 = PlatformSprite(g, p2, p1, 170, 250, 60, 10)        
platform5 = PlatformSprite(g, p2, p1, 50, 300, 60, 10)   
platform4 = PlatformSprite(g, p1, p1, 175, 350, 100, 10)  
platform3 = PlatformSprite(g, p2, p1, 300, 400, 60, 10)                               
platform2 = PlatformSprite(g, p1, p1, 150, 440, 100, 10)                                                
platform1 = PlatformSprite(g, p2, p1, 0, 480, 100, 10)                                                                       
g.sprites.append(platform1)
g.sprites.append(platform2)
g.sprites.append(platform3)
g.sprites.append(platform4)
g.sprites.append(platform5)
g.sprites.append(platform6)
g.sprites.append(platform7)
g.sprites.append(platform8)
g.sprites.append(platform9)
g.sprites.append(platform10)
toilet = ToiletSprite(g, PhotoImage(file='icons/toilet-empty.gif'), PhotoImage(file='icons/toilet-fill.gif'),45, 30, 40, 35)
g.sprites.append(toilet)
sf = StickFigureSprite(g)
g.sprites.append(sf)
g.mainloop()